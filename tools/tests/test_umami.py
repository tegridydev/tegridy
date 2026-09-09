"""Check tracker placement, policy and production isolation without sending events."""
from html.parser import HTMLParser
import unittest
import test_build

WEBSITE_ID = 'af5a218c-d27d-484c-b0a2-8f1a25e82669'
class Tags(HTMLParser):
    def __init__(self):
        super().__init__(); self.head=False; self.scripts=[]; self.policy=''
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='head': self.head=True
        if tag=='script' and attrs.get('src')=='https://cloud.umami.is/script.js': self.scripts.append((self.head,attrs))
        if tag=='meta' and attrs.get('http-equiv')=='Content-Security-Policy': self.policy=attrs['content']
    def handle_endtag(self,tag):
        if tag=='head':self.head=False

class UmamiTests(unittest.TestCase):
    setUp=test_build.PublishingTests.setUp
    tearDown=test_build.PublishingTests.tearDown
    run_build=test_build.PublishingTests.run_build
    def enable(self,value=WEBSITE_ID):
        p=self.root/'tools/site.toml'
        p.write_text(p.read_text().replace('umami_website_id = ""',f'umami_website_id = "{value}"'))
    def test_tracker_and_csp_on_every_generated_page(self):
        self.enable();out=self.run_build()
        for page in out.rglob('*.html'):
            source=page.read_text();parsed=Tags();parsed.feed(source)
            if not parsed.policy: # The standalone offline demo is preserved.
                self.assertFalse(parsed.scripts);continue
            self.assertEqual(len(parsed.scripts),1,page)
            in_head,attrs=parsed.scripts[0];self.assertTrue(in_head)
            self.assertEqual(attrs['data-website-id'],WEBSITE_ID)
            self.assertIn('defer',attrs)
            self.assertEqual(attrs['data-before-send'],'tegridyAnalyticsFilter')
            self.assertLess(source.index('src="/assets/analytics.js"'), source.index('src="https://cloud.umami.is/script.js"'))
            self.assertEqual(attrs['data-domains'],'tegridydev.com,www.tegridydev.com')
            for option in ('performance','do-not-track','exclude-search','exclude-hash'):
                self.assertEqual(attrs['data-'+option],'true')
            directives=dict((p.strip().split(' ',1)+[''])[:2] for p in parsed.policy.split(';') if p.strip())
            self.assertIn('https://cloud.umami.is',directives['script-src'].split())
            self.assertIn('https://gateway.umami.is',directives['connect-src'].split())
            self.assertNotIn('*',directives['connect-src'].split())
            self.assertNotIn("'unsafe-inline'",directives['script-src'])
            self.assertNotIn('cloudflareinsights.com',source)
            self.assertNotIn('googletagmanager.com',source)
        self.assertIn('This site uses Umami Cloud',(out/'privacy/index.html').read_text())
    def test_alternate_build_removes_network_permissions(self):
        self.enable();out=self.run_build('https://tegridydev.github.io/tegridy')
        self.assertNotIn('https://gateway.umami.is',(out/'index.html').read_text())
        self.assertNotIn('https://cloud.umami.is',(out/'index.html').read_text())
    def test_invalid_identifier_fails_before_publication(self):
        self.enable('not-a-uuid')
        with self.assertRaisesRegex(ValueError,'Umami website ID'): self.run_build()
