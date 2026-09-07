"""Server-rendered writing navigation, with optional client-side title filtering."""
from collections import defaultdict
from html import escape, unescape
import re
from urllib.parse import urlsplit

LABELS = {
    'agents': 'Agents & assistants', 'applications': 'Applications & utilities',
    'datasets': 'Datasets & documents', 'developer-tools': 'Developer workflows',
    'knowledge': 'Knowledge & memory', 'model-interpretability': 'Model interpretability',
    'mathematics': 'Mathematics', 'security': 'Security',
    'training-and-evaluation': 'Training & evaluation', 'transformers': 'Transformers',
    'elsewhere': 'On Hugging Face', 'general': 'Articles',
}


def grouped(items):
    groups = defaultdict(list)
    for item in items:
        parts = item['route'].strip('/').split('/')
        category = 'elsewhere' if urlsplit(item['route']).scheme else parts[1] if len(parts) > 2 else 'general'
        groups[category].append(item)
    return dict(sorted(groups.items(), key=lambda pair: (pair[0] == 'elsewhere', LABELS.get(pair[0], pair[0]))))


class Navigation:
    def __init__(self, blog, research, show_paths=False):
        self.show_paths = show_paths
        self.catalog = {'blog': grouped(blog), 'research': grouped(research)}

    def index(self, section, entries):
        return ''.join(
            '<section class="catalog-group" id="topic-' + escape(key, quote=True) + '"><h2>'
            + escape(LABELS.get(key, key.replace('-', ' ').title()))
            + f' <span>{len(items)}</span></h2>' + entries(items) + '</section>'
            for key, items in self.catalog[section].items())

    def wrap(self, route, body):
        section = route.strip('/').split('/')[0]
        if section not in self.catalog:
            return body
        index = route == f'/{section}/'
        nav = ('<aside class="reading-sidebar" aria-label="Writing navigation">'
               '<details class="browse-panel" open><summary>Browse ' + section
               + ' <span class="browse-hint">topics &amp; articles</span></summary>'
               '<div class="browse-content"><nav class="writing-tabs" aria-label="Writing sections">')
        for name in self.catalog:
            state = ' aria-current="page"' if name == section and index else ' class="selected"' if name == section else ''
            nav += f'<a href="/{name}/"{state}>{name.title()}</a>'
        nav += '</nav>'
        if self.show_paths:
            nav += '<a class="reading-paths-link" href="/topics/">Explore reading paths ↗</a>'
        nav += ('<div class="search-wrapper">'
                '<div class="navigation-search" hidden><label for="nav-search">Find an article</label>'
                '<input id="nav-search" type="search" placeholder="Filter titles or topics…" autocomplete="off" '
                'aria-controls="topic-list"><p class="search-status" role="status" aria-live="polite"></p></div></div>'
                '<nav id="topic-list" aria-label="' + section.title() + ' topics">')
        for key, items in self.catalog[section].items():
            active = any(item['route'] == route for item in items)
            label = escape(LABELS.get(key, key.replace('-', ' ').title()))
            nav += '<details class="topic-group"' + (' open' if index or active else '') + f'><summary>{label}<span>{len(items)}</span></summary><ul>'
            for item in items:
                current = ' aria-current="page"' if item['route'] == route else ''
                nav += '<li><a href="' + escape(item['route'], quote=True) + '"' + current + '>' + escape(item['title']) + '</a></li>'
            nav += '</ul></details>'
        nav += f'</nav><a class="sidebar-rss" href="/{section}/feed.xml">Subscribe via RSS ↗</a></div></details></aside>'
        if not index:
            # The article's own H2s have stable Markdown-generated IDs. Related-reading
            # headings without IDs are deliberately excluded from the contents list.
            headings = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S)
            if headings:
                toc = '<details class="article-toc" open><summary>On this page</summary><ol>'
                toc += ''.join('<li><a href="#' + escape(anchor, quote=True) + '">' + escape(unescape(re.sub('<[^>]+>', '', title))) + '</a></li>' for anchor, title in headings)
                toc += '</ol></details>'
                body = body.replace('</h1>', '</h1>' + toc, 1)
            for items in self.catalog[section].values():
                for i, item in enumerate(items):
                    if item['route'] != route:
                        continue
                    links = []
                    for offset, label in [(-1, 'Previous in topic'), (1, 'Next in topic')]:
                        if 0 <= i + offset < len(items):
                            other = items[i + offset]
                            links.append('<a href="' + escape(other['route'], quote=True) + '"><span>' + label + '</span><strong>' + escape(other['title']) + '</strong></a>')
                    if links:
                        body = body.replace('</article>', '<nav class="article-pagination" aria-label="More in this topic">' + ''.join(links) + '</nav></article>')
        return body.replace('<main class="container" id="main-content">', '<div class="reading-layout">' + nav + '<main class="reading-main" id="main-content">', 1).replace('</main>', '</main></div>', 1)
