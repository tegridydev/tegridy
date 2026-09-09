"""Publication-boundary, routing and metadata checks; no network calls."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build

class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        shutil.copytree(build.ROOT/'tools/site', self.root/'tools/site')
        shutil.copy2(build.ROOT/'tools/site.toml', self.root/'tools/site.toml')
        # Small independent fixtures keep tests fast and avoid recursive build copies.
        for section in ('blog', 'research'):
            (self.root/section).mkdir()
        folder = self.root/'blog/minecraft-time-with-astra'
        folder.mkdir()
        (folder/'minecraft-time-with-astra.md').write_text(
            '+++\ntitle = "Fixture"\ndate = "2026-09-06"\ndescription = "A test article."\ndraft = false\n+++\n'
            '# Fixture\n\nroughly **145 minutes**\n\n![Test](/blog/minecraft-time-with-astra/wild-block-one-shot.png)\n')
        (folder/'wild-block-one-shot.png').write_bytes(b'fixture asset')
        (folder/'wildblock.html').write_text('<!doctype html><title>Fixture</title><p>Standalone asset</p>')
        (self.root/'research/hydraform.md').write_text('+++\ntitle = "Draft"\ndraft = true\n+++\n# Draft\n')
        (self.root/'tools/site/external-articles.json').write_text(json.dumps([
            {'title':f'External {i}', 'description':'External article', 'date':'2025-01-01',
             'url':f'https://example.com/article-{i}'} for i in range(4)]))
        config = self.root/'tools/site.toml'
        import re
        config.write_text(re.sub(r'umami_website_id = "[^"]*"', 'umami_website_id = ""', config.read_text()))
    def tearDown(self):
        self.tmp.cleanup()
    def run_build(self, url='https://tegridydev.com'):
        with contextlib.redirect_stdout(io.StringIO()):
            return build.build(self.root, url)
    def test_domain_build_preserves_article_and_excludes_drafts(self):
        out = self.run_build()
        self.assertFalse((out/'research/hydraform').exists())
        page = (out/'blog/minecraft-time-with-astra/index.html').read_text()
        self.assertIn('roughly <strong>145 minutes</strong>', page)
        self.assertIn('https://tegridydev.com/blog/minecraft-time-with-astra/', page)
        for name in ['wildblock.html', 'wild-block-one-shot.png']:
            self.assertEqual((out/'blog/minecraft-time-with-astra'/name).read_bytes(),
                             (self.root/'blog/minecraft-time-with-astra'/name).read_bytes())
        self.assertFalse((out/'scripts').exists())
        self.assertFalse((out/'research/hydraform.md').exists())
        self.assertNotIn('cloud.umami.is/script.js', (out/'index.html').read_text())
        self.assertNotIn('hydraform', (out/'sitemap.xml').read_text())
    def test_project_prefix_and_feeds(self):
        out = self.run_build('https://tegridydev.github.io/tegridy')
        page = (out/'blog/minecraft-time-with-astra/index.html').read_text()
        self.assertIn('src="/tegridy/blog/minecraft-time-with-astra/wild-block-one-shot.png"', page)
        self.assertIn('href="/tegridy/assets/', page)
        self.assertNotIn('/tegridy/tegridy/', page)
        feed = ET.parse(out/'blog/feed.xml')
        self.assertEqual(len(feed.findall('.//item')), 5)
        self.assertEqual(feed.findtext('.//item/link'), 'https://tegridydev.github.io/tegridy/blog/minecraft-time-with-astra/')
        ET.parse(out/'research/feed.xml'); ET.parse(out/'sitemap.xml')
    def test_missing_asset_fails_build(self):
        p = self.root/'blog/minecraft-time-with-astra/minecraft-time-with-astra.md'
        p.write_text(p.read_text()+'\n![Missing](missing.png)\n')
        with self.assertRaisesRegex(ValueError, 'Missing source link|broken link'):
            self.run_build()
    def test_duplicate_slug_fails_build(self):
        p = self.root/'blog/minecraft-time-with-astra/duplicate.md'
        p.write_text((p.parent/'minecraft-time-with-astra.md').read_text())
        with self.assertRaisesRegex(ValueError, 'Duplicate article URL'):
            self.run_build()
    def test_published_article_requires_metadata(self):
        p = self.root/'research/hydraform.md'
        p.write_text('+++\ntitle = "Hydraform"\ndraft = false\n+++\n# Hydraform\n')
        with self.assertRaisesRegex(ValueError, 'needs description'):
            self.run_build()
    def test_analytics_configuration_and_csp(self):
        p = self.root/'tools/site.toml'
        p.write_text(p.read_text().replace('umami_website_id = ""', 'umami_website_id = "'+'af5a218c-d27d-484c-b0a2-8f1a25e82669'+'"'))
        out = self.run_build()
        page = (out/'index.html').read_text()
        self.assertIn('https://gateway.umami.is', page)
        self.assertEqual(page.count('src="https://cloud.umami.is/script.js"'), 1)
        self.assertIn('This site uses Umami Cloud', (out/'privacy/index.html').read_text())
    def test_rebuild_removes_unpublished_output(self):
        out = self.run_build()
        p = self.root/'blog/minecraft-time-with-astra/minecraft-time-with-astra.md'
        p.write_text(p.read_text().replace('draft = false', 'draft = true'))
        self.run_build()
        self.assertFalse((out/'blog/minecraft-time-with-astra').exists())
    def test_build_is_reproducible(self):
        out = self.run_build()
        def hashes():
            return {str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
        before = hashes(); self.run_build(); self.assertEqual(before, hashes())

    def test_year_only_dates_and_readme_routes(self):
        folder = self.root/'blog/minecraft-time-with-astra'
        article = folder/'minecraft-time-with-astra.md'
        article.write_text(article.read_text().replace('2026-09-06', '2026') + '\n[Setup](README.md)\n[Blog](../README.md)\n')
        (folder/'README.md').write_text('# Setup')
        (self.root/'blog/README.md').write_text('# Blog')
        out = self.run_build()
        page = (out/'blog/minecraft-time-with-astra/index.html').read_text()
        self.assertIn('<time datetime="2026">2026</time>', page)
        self.assertNotIn('datePublished', page)
        item = ET.parse(out/'blog/feed.xml').find('.//item')
        self.assertIsNone(item.find('pubDate'))
        self.assertIn('href="https://github.com/tegridydev/tegridy/blob/main/blog/minecraft-time-with-astra/README.md">Setup', page)
        self.assertIn('href="/blog/">Blog', page)

    def test_standalone_dependencies_and_fragments_are_checked(self):
        folder = self.root/'blog/minecraft-time-with-astra'
        demo = folder/'wildblock.html'
        demo.write_text('<script src="missing.js"></script>')
        with self.assertRaisesRegex(ValueError, 'broken link missing.js'):
            self.run_build()
        demo.write_text('<a href="#missing">Missing</a>')
        with self.assertRaisesRegex(ValueError, 'missing fragment'):
            self.run_build()

    def test_failure_preserves_last_successful_output(self):
        out = self.run_build()
        previous = (out/'index.html').read_bytes()
        (self.root/'research/broken.md').write_text('+++\ndraft = false\n+++\n')
        with self.assertRaises(ValueError):
            self.run_build()
        self.assertEqual(previous, (out/'index.html').read_bytes())
        self.assertFalse(list(self.root.glob('.site-build-*')))

    def test_preview_is_separate_and_custom_domain_only_in_production(self):
        config = self.root/'tools/site.toml'
        config.write_text(config.read_text().replace(
            'url = "https://tegridydev.github.io/tegridy"', 'url = "https://tegridydev.com"').replace(
            'custom_domain = ""', 'custom_domain = "tegridydev.com"'))
        out = self.run_build()
        self.assertEqual((out/'CNAME').read_text().strip(), 'tegridydev.com')
        before = (out/'index.html').read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            preview = build.build(self.root, 'http://127.0.0.1:8000', preview=True)
        self.assertEqual(preview.name, '_preview')
        self.assertFalse((preview/'CNAME').exists())
        self.assertEqual((out/'index.html').read_bytes(), before)
        out = self.run_build('https://example.org/project')
        self.assertFalse((out/'CNAME').exists())

    def test_default_production_uses_custom_domain(self):
        with contextlib.redirect_stdout(io.StringIO()):
            out = build.build(self.root)
        page = (out/'index.html').read_text()
        self.assertIn('href="/assets/', page)
        self.assertIn('src="/assets/', page)
        self.assertIn('https://tegridydev.com/', page)
        self.assertTrue((out/'CNAME').exists())

    def test_viewer_dependencies_are_published_but_server_template_is_not(self):
        folder = self.root/'blog/model-interpretability/what-a-model-map-can-show'
        folder.mkdir(parents=True)
        (folder/'viewer.md').write_text('+++\ntitle="Viewer"\ndate="2026"\ndescription="Viewer"\ndraft=false\n+++\n[View](viewer.html)')
        (folder/'viewer.html').write_text('<script src="viewer.js"></script>')
        (folder/'viewer.js').write_text('console.log("viewer")')
        (folder/'fixture.json').write_text('{}')
        (folder/'private.py').write_text('print("source")')
        (folder/'requirements.txt').write_text('pytest')
        (folder/'requirements-model.txt').write_text('torch')
        server = self.root/'blog/agents/botsim-local-community'
        server.mkdir(parents=True)
        (server/'app.md').write_text('+++\ntitle="App"\ndate="2026"\ndescription="Local app"\ndraft=false\n+++\n[Template](interface.html)')
        (server/'interface.html').write_text('{{ server_only_template }}')
        out = self.run_build()
        for name in ('viewer.html', 'viewer.js', 'fixture.json'):
            self.assertTrue((out/folder.relative_to(self.root)/name).is_file())
        self.assertFalse((out/folder.relative_to(self.root)/'private.py').exists())
        self.assertFalse((out/folder.relative_to(self.root)/'requirements.txt').exists())
        self.assertFalse((out/folder.relative_to(self.root)/'requirements-model.txt').exists())
        self.assertFalse((out/server.relative_to(self.root)/'interface.html').exists())

    def test_css_srcset_and_concurrent_build_are_checked(self):
        css = self.root/'tools/site/static/assets/articles.css'
        css.write_text(css.read_text() + '\n.bad { background: url(missing.png) }')
        with self.assertRaisesRegex(ValueError, 'broken link missing.png'):
            self.run_build()
        css.write_text('')
        article = self.root/'blog/minecraft-time-with-astra/minecraft-time-with-astra.md'
        article.write_text(article.read_text() + '\n<img srcset="missing.png 2x" alt="Test">')
        with self.assertRaisesRegex(ValueError, 'broken link missing.png'):
            self.run_build()
        import fcntl
        with (self.root/'tools/.site-build.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(ValueError, 'Another site build'):
                self.run_build()

if __name__ == '__main__':
    unittest.main()
