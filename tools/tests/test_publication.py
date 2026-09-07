"""Regression checks for metadata, discovery and the exported build layout."""
import contextlib
import io
import json
from pathlib import Path
import re
import struct
import sys
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
import test_build

class PublicationTests(unittest.TestCase):
    setUp = test_build.PublishingTests.setUp
    tearDown = test_build.PublishingTests.tearDown
    run_build = test_build.PublishingTests.run_build

    def article(self):
        return self.root/'blog/minecraft-time-with-astra/minecraft-time-with-astra.md'

    def page(self, out):
        return (out/'blog/minecraft-time-with-astra/index.html').read_text()

    def test_unknown_dates_have_no_invented_schema_or_feed_date(self):
        p = self.article()
        p.write_text(p.read_text().replace('date = "2026-09-06"\n', ''))
        out = self.run_build()
        page = self.page(out)
        self.assertIn('Publication date unverified', page)
        self.assertNotIn('datePublished', page)
        self.assertNotIn('dateModified', page)
        item = next(x for x in ET.parse(out/'blog/feed.xml').findall('.//item') if x.findtext('guid', '').startswith('urn:tegridy:'))
        self.assertIsNone(item.find('pubDate'))
        self.assertIsNone(ET.parse(out/'sitemap.xml').find('.//{*}lastmod'))

    def test_stable_feed_ids_across_domains_and_explicit_update(self):
        p = self.article()
        p.write_text(p.read_text().replace('draft = false', 'id = "blog/stable"\nupdated = "2026-09-07"\ndraft = false'))
        out = self.run_build()
        guid = ET.parse(out/'blog/feed.xml').find('.//item/guid')
        self.assertEqual(guid.text, 'urn:tegridy:blog/stable')
        self.assertEqual(guid.attrib, {'isPermaLink':'false'})
        self.assertIn('Updated', self.page(out))
        self.assertEqual(ET.parse(out/'sitemap.xml').findtext('.//{*}lastmod'), '2026-09-07')
        out = self.run_build('https://tegridydev.github.io/tegridy')
        self.assertEqual(ET.parse(out/'blog/feed.xml').findtext('.//item/guid'), guid.text)

    def test_related_drafts_and_duplicate_identity_fail(self):
        p = self.article()
        original = p.read_text()
        p.write_text(original.replace('draft = false', 'related = ["research/missing"]\ndraft = false'))
        with self.assertRaisesRegex(ValueError, 'related article'):
            self.run_build()
        p.write_text(original.replace('draft = false', 'id = "same"\ndraft = false'))
        other = self.root/'research/other.md'
        other.write_text('+++\nid="same"\ntitle="Other"\ndescription="Another"\ndraft=false\n+++\n# Other')
        with self.assertRaisesRegex(ValueError, 'duplicate article ID'):
            self.run_build()

    def test_setup_fragments_target_real_readme(self):
        p = self.article()
        (p.parent/'README.md').write_text('# Setup\n## Run\n')
        p.write_text(p.read_text()+'\n[Module setup](README.md#run)\n')
        page = self.page(self.run_build())
        self.assertIn('/blob/main/blog/minecraft-time-with-astra/README.md#run', page)
        self.assertNotIn('href="/blog/minecraft-time-with-astra/#run"', page)

    def test_single_h1_and_complete_descriptions(self):
        p = self.article()
        original = p.read_text()
        p.write_text(original+'\n# Another heading\n')
        with self.assertRaisesRegex(ValueError, 'exactly one H1'):
            self.run_build()
        p.write_text(original.replace('A test article.', 'A truncated sentence…'))
        with self.assertRaisesRegex(ValueError, 'truncated description'):
            self.run_build()

    def test_analytics_absent_from_preview_and_alternate_host(self):
        p = self.root/'tools/site.toml'
        p.write_text(p.read_text().replace('cloudflare_analytics_token = ""', 'cloudflare_analytics_token = "'+'a'*32+'"'))
        out = self.run_build('https://tegridydev.github.io/tegridy')
        self.assertNotIn('beacon.min.js', self.page(out))
        with contextlib.redirect_stdout(io.StringIO()):
            out = build.build(self.root, 'http://127.0.0.1:8000', preview=True)
        self.assertNotIn('beacon.min.js', self.page(out))
        self.assertEqual(out.parent, self.root/'tools')

    def test_image_dimensions_loading_and_topic_navigation(self):
        p = self.article()
        image = p.parent/'wild-block-one-shot.png'
        image.write_bytes(b'\x89PNG\r\n\x1a\n'+b'\0'*8+struct.pack('>II', 800, 400))
        p.write_text(p.read_text().replace('draft = false', 'id = "blog/fixture"\ntopic = "fixtures"\ndraft = false')+'\n![Second](wild-block-one-shot.png)\n')
        (self.root/'tools/site/topics.json').write_text(json.dumps([{'slug':'fixtures','title':'Fixtures','description':'Useful fixtures.','articles':['blog/fixture']}]))
        out = self.run_build()
        page = self.page(out)
        self.assertEqual(page.count('width="800" height="400"'), 2)
        self.assertEqual(page.count('loading="eager"'), 1)
        self.assertEqual(page.count('loading="lazy"'), 1)
        self.assertTrue((out/'topics/fixtures/index.html').exists())
        self.assertIn('/topics/fixtures/', page)
        self.assertIn('/topics/fixtures/', (out/'sitemap.xml').read_text())

if __name__ == '__main__':
    unittest.main()
