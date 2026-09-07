"""Navigation must remain useful without JavaScript and preserve article content."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigation import Navigation


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.nav = Navigation([
            {'route': '/blog/agents/one/', 'title': 'One & two'},
            {'route': '/blog/agents/two/', 'title': '<Second>'},
        ], [], False)

    def test_article_links_current_page_and_contents(self):
        source = '<main class="container" id="main-content"><article><h1>Title</h1><p>Keep this text.</p><h2 id="scope">Scope &amp; limits</h2></article></main>'
        page = self.nav.wrap('/blog/agents/one/', source)
        self.assertIn('href="/blog/agents/one/" aria-current="page"', page)
        self.assertIn('href="#scope">Scope &amp; limits</a>', page)
        self.assertIn('Next in topic', page)
        self.assertIn('<p>Keep this text.</p>', page)
        self.assertNotIn('href="/topics/"', page)
        self.assertIn('&lt;Second&gt;', page)

    def test_non_writing_pages_unchanged(self):
        self.assertEqual(self.nav.wrap('/', '<main>Home</main>'), '<main>Home</main>')

    def test_empty_catalog_has_no_fake_entries(self):
        self.assertEqual(self.nav.index('research', lambda entries: 'unexpected'), '')

    def test_index_renders_every_entry_once(self):
        result = self.nav.index('blog', lambda entries: ','.join(a['route'] for a in entries))
        self.assertEqual(result.count('/blog/agents/one/'), 1)
        self.assertEqual(result.count('/blog/agents/two/'), 1)


if __name__ == '__main__':
    unittest.main()
