#!/usr/bin/env python3
"""Build the public site. Python 3.11+, one build dependency: Python-Markdown.

Only explicit, non-draft Markdown documents and their local assets are published.
Repository Markdown/HTML is trusted author content, not untrusted user input.
"""
from __future__ import annotations
import argparse
import base64
import fcntl
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import sys
import struct
import tempfile
import tomllib
from urllib.parse import quote, unquote, urlsplit, urlunsplit
import xml.etree.ElementTree as ET
import markdown

from paths import ROOT, infrastructure, releases
from navigation import Navigation
ASSETS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.pdf', '.html', '.txt', '.mp4', '.webm'}
# Browser-only files are explicitly published; server templates are not demos.
DEMO_FILES = {
    'blog/model-interpretability/what-a-model-map-can-show/viewer.js',
    'blog/model-interpretability/what-a-model-map-can-show/fixture.json',
}
SERVER_TEMPLATES = {'blog/agents/botsim-local-community/interface.html'}


def public_asset(path: Path, relative: str) -> bool:
    return (relative not in SERVER_TEMPLATES
            and not re.fullmatch(r'requirements(?:[-.].*)?\.txt', path.name)
            and (path.suffix.lower() in ASSETS or relative in DEMO_FILES))


def read_document(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding='utf-8')
    if not text.startswith('+++\n'):
        return {}, text
    try:
        front, body = text[4:].split('\n+++', 1)
    except ValueError as exc:
        raise ValueError(f'{path}: unclosed +++ metadata') from exc
    return tomllib.loads(front), body.lstrip('\n')


def date_string(value: object) -> str:
    if value is None or value == "":
        return ""
    if re.fullmatch(r'[0-9]{4}', str(value)) and 1 <= int(value) <= 9999:
        return str(value)
    return date.fromisoformat(str(value)).isoformat()


def site_url(value: str) -> str:
    parts = urlsplit(value.rstrip('/'))
    if parts.scheme not in {'https', 'http'} or not parts.netloc or parts.query or parts.fragment or parts.username:
        raise ValueError('Site URL must be an absolute HTTP(S) URL without query or fragment')
    if '..' in unquote(parts.path).split('/'):
        raise ValueError('Invalid site URL path')
    return value.rstrip('/')


def date_label(value: str) -> str:
    if not value:
        return ''
    label = escape(value)
    return '<time datetime="' + escape(value, quote=True) + '">' + label + '</time>'


def image_layout(html: str, root: Path) -> str:
    leading = True
    manifest_path = infrastructure(root) / 'site/images.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    def replace(match):
        nonlocal leading
        tag = match[0]
        src = re.search(r'src="([^"]+)"', tag)
        if not src or not src[1].startswith('/') or src[1].startswith('//'):
            return tag
        path = (root / unquote(src[1]).lstrip('/')).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError('Image outside source')
        raw = path.read_bytes()
        data = raw[:24]
        attrs = ''
        if src[1] in manifest:
            record = manifest[src[1]]
            if hashlib.sha256(raw).hexdigest() != record['source_sha256']:
                raise ValueError('Image derivatives are stale: ' + src[1])
            variants = record['variants']
            for variant in variants:
                asset = (root / variant['path'].lstrip('/')).resolve()
                if not asset.is_relative_to(root.resolve()) or not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest() != variant['sha256']:
                    raise ValueError('Missing or modified image derivative')
            chosen = variants[-1]
            tag = tag.replace('src="' + src[1] + '"', 'src="' + chosen['path'] + '"')
            attrs += ' srcset="' + ', '.join(v['path'] + ' ' + str(v['width']) + 'w' for v in variants) + '" sizes="(max-width: 800px) 95vw, 760px"'
            attrs += f' width="{chosen["width"]}" height="{chosen["height"]}"'
            data = b''
        if data.startswith(b'\x89PNG\r\n\x1a\n') and len(data) == 24:
            width, height = struct.unpack('>II', data[16:24])
            if not re.search(r'\bwidth=', tag):
                attrs += f' width="{width}" height="{height}"'
        if not re.search(r'\bloading=', tag):
            attrs += ' loading="eager" fetchpriority="high"' if leading else ' loading="lazy"'
        leading = False
        attrs += ' decoding="async"' if 'decoding=' not in tag else ''
        return tag.rstrip('>').rstrip('/').rstrip() + attrs + '>'
    return re.sub(r'<img\b[^>]*>', replace, html)


def documents(root: Path) -> list[dict]:
    result = []
    seen = set()
    for section in ('blog', 'research'):
        for path in sorted((root / section).rglob('*.md')):
            if path.is_symlink():
                raise ValueError(f'Symlink not allowed: {path}')
            if path.name.lower() == 'readme.md':
                continue
            meta, body = read_document(path)
            # Explicit publication prevents unfinished notes silently becoming pages.
            if meta.get('draft', True) is not False:
                continue
            for key in ('title', 'description'):
                if not meta.get(key):
                    raise ValueError(f'{path}: published article needs {key}')
            rel = path.relative_to(root).as_posix()
            parent = path.parent.relative_to(root / section).as_posix()
            default_slug = path.stem if parent == '.' else parent
            slug = meta.get('slug', default_slug)
            if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9]+(?:[-/][a-z0-9]+)*', slug):
                raise ValueError(f'{path}: slug must use lowercase letters, numbers, hyphens or /')
            route = f'/{section}/{slug}/'
            if route in seen:
                raise ValueError(f'Duplicate article URL: {route}')
            seen.add(route)
            result.append(dict(meta, date=date_string(meta.get('date')), route=route, source=rel,
                               section=section, body=body, updated=date_string(meta.get('updated'))))
    ids = set()
    titles = set()
    descriptions = set()
    for article in result:
        article.setdefault('id', article['section'] + '/' + article['route'].strip('/').split('/')[-1])
        identity = article['id']
        if not isinstance(identity, str) or not re.fullmatch(r'[a-z0-9]+(?:[-/][a-z0-9]+)*', identity) or identity in ids:
            raise ValueError('Invalid or duplicate article ID: ' + str(identity))
        ids.add(identity)
        for key, seen_values in (('title', titles), ('description', descriptions)):
            value = article[key].strip()
            if not value or value.casefold() in seen_values or value.endswith(('…', '...')):
                raise ValueError('Duplicate, empty or truncated ' + key + ': ' + identity)
            seen_values.add(value.casefold())
        if article.get('type', 'article') not in {'article', 'research-note'}:
            raise ValueError('Invalid article type: ' + identity)
        if article.get('status', 'implemented') not in {'proposal', 'implemented', 'pilot'}:
            raise ValueError('Invalid research status: ' + identity)
        if article.get('author', 'tegridydev') != 'tegridydev':
            raise ValueError('Unknown author: ' + identity)
        related = article.get('related', [])
        if not isinstance(related, list) or not all(isinstance(x, str) for x in related) or len(related) != len(set(related)):
            raise ValueError('Invalid related article IDs: ' + identity)
        if article.get('image') and (not article.get('image_alt') or not article['image'].startswith('/') or article['image'].startswith('//')):
            raise ValueError('Article image requires a local root path and image_alt: ' + identity)
        if article.get('image'):
            image = (root / article['image'].lstrip('/')).resolve()
            if not image.is_relative_to(root.resolve()) or not image.is_file():
                raise ValueError('Missing article social image: ' + identity)
    for article in result:
        if set(article.get('related', [])) - (ids - {article['id']}):
            raise ValueError('Missing, draft or self-related article ID: ' + article['id'])
    return sorted(result, key=lambda x: (x['date'], x['route']), reverse=True)


def build(root: Path = ROOT, base_url: str | None = None, preview: bool = False) -> Path:
    """Publish a validated staging tree, retaining the last good output on failure."""
    root = root.resolve()
    with (infrastructure(root) / '.site-build.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('Another site build is running; retry after it finishes') from exc
        return _publish(root, base_url, preview)


def _publish(root: Path, base_url: str | None, preview: bool) -> Path:
    out = infrastructure(root) / '_preview' if preview else releases(root) / '_site'
    backup = out.with_name(out.name + '.previous')
    if out.is_symlink() or backup.is_symlink():
        raise ValueError('Build output must not be a symlink')
    if backup.exists():
        if out.exists():
            shutil.rmtree(backup)
        else:
            backup.rename(out)
    with tempfile.TemporaryDirectory(prefix='.site-build-', dir=out.parent) as staging:
        staged = Path(staging) / 'public'
        _render(root, base_url, staged, preview)
        if out.exists():
            out.rename(backup)
        try:
            staged.rename(out)
        except OSError:
            if backup.exists():
                backup.rename(out)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    print(f'Validated site → {out}')
    return out


def _render(root: Path, base_url: str | None, out: Path, preview: bool) -> None:
    config = tomllib.loads((infrastructure(root) / 'site.toml').read_text())
    base = site_url(base_url or config['url'])
    prefix = urlsplit(base).path.rstrip('/')
    out.mkdir()
    static = infrastructure(root) / 'site/static'
    for p in static.rglob('*'):
        if p.is_symlink():
            raise ValueError(f'Symlink not allowed: {p}')
    shutil.copytree(static, out, dirs_exist_ok=True)
    template = infrastructure(root) / 'site/templates'
    header = (template / 'header.html').read_text()
    footer = (template / 'footer.html').read_text()
    theme = (template / 'theme-init.js').read_text()
    css = '/assets/build/site.502282bc98c5.css'
    articles = documents(root)
    routes = {x['source']: x['route'] for x in articles}
    readmes = {'README.md': '/'}
    for section in ('blog', 'research'):
        for readme in (root / section).rglob('README.md'):
            siblings = [a for a in articles if (root / a['source']).parent == readme.parent]
            readmes[readme.relative_to(root).as_posix()] = siblings[0]['route'] if len(siblings) == 1 else f'/{section}/'
    external = json.loads((infrastructure(root) / 'site/external-articles.json').read_text())
    for item in external:
        if urlsplit(site_url(item['url'])).scheme != 'https':
            raise ValueError('External articles require HTTPS URLs')
        item['date'] = date_string(item['date'])
        item['route'] = item['url']
        item['section'] = 'blog'
    blog = sorted([x for x in articles if x['section'] == 'blog'] + external,
                  key=lambda x: (x['date'], x['route']), reverse=True)
    research = [x for x in articles if x['section'] == 'research']
    navigation = Navigation(blog, research, any(a.get('topic') for a in articles))
    umami_id = config.get('umami_website_id', '')
    if umami_id and not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', umami_id):
        raise ValueError('Umami website ID must be a UUID')
    # Never send preview traffic to the production property. Domain filtering also
    # protects production files opened on localhost or another hosting domain.
    analytics_enabled = bool(umami_id) and not preview and base == site_url(config['url'])
    analytics = (f'<script defer src="https://cloud.umami.is/script.js" data-website-id="{umami_id}" '
                 'data-domains="tegridydev.com,www.tegridydev.com" data-performance="true" '
                 'data-do-not-track="true" data-exclude-search="true" data-exclude-hash="true" '
                 'data-before-send="tegridyAnalyticsFilter"></script>') if analytics_enabled else ''

    def local(route: str) -> str:
        return route if urlsplit(route).scheme else prefix + route

    if analytics_enabled:
        analytics = f'<script defer src="{local("/assets/analytics.js")}"></script>' + analytics

    def absolute(route: str) -> str:
        return route if urlsplit(route).scheme else base + route

    def rebase(html: str) -> str:
        # Root-relative assets must work at both /tegridy/ and the custom domain root.
        html = re.sub(r'\b(href|src)=("|\')(/(?!/).*?)\2',
                      lambda m: f'{m[1]}={m[2]}{prefix}{m[3]}{m[2]}', html)
        return re.sub(r'\bsrcset="([^"]+)"', lambda m: 'srcset="' + ', '.join((prefix + part.strip() if part.strip().startswith('/') and not part.strip().startswith('//') else part.strip()) for part in m[1].split(',')) + '"', html)

    def entries(items: list[dict]) -> str:
        if not items:
            return '<p>No articles published here yet.</p>'
        rows = []
        for x in items:
            label = ' · on Hugging Face' if x in external else ''
            rows.append(f'<li><a class="entry-link" href="{escape(x["route"], quote=True)}">'
                        f'<span class="entry-title">{escape(x["title"])}</span>'
                        f'<span class="entry-description">{escape(x["description"])}</span></a>'
                        f'<p class="article-meta">{date_label(x["date"])}{label}</p></li>')
        return '<ul class="entries">' + ''.join(rows) + '</ul>'

    def write_page(route: str, title: str, description: str, body: str,
                   schema: dict | None = None, contact: bool = False, noindex: bool = False, social: dict | None = None) -> None:
        body = navigation.wrap(route, body)
        writing = route.startswith(('/blog/', '/research/'))
        url = absolute(route)
        schema_text = json.dumps(schema, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c') if schema else ''
        hashes = ["'sha256-" + base64.b64encode(hashlib.sha256(s.encode()).digest()).decode() + "'"
                  for s in (theme, schema_text) if s]
        csp = ("default-src 'none'; base-uri 'none'; object-src 'none'; script-src 'self' " + ' '.join(hashes)
               + (' https://cloud.umami.is' if analytics_enabled else '')
               + "; script-src-attr 'none'; style-src 'self'; style-src-attr 'none'; img-src 'self' https:; "
                 "connect-src 'self'" + (' https://gateway.umami.is' if analytics_enabled else '')
               + "; font-src 'none'; media-src 'self'; frame-src 'none'; worker-src 'none'; form-action 'none'; "
                 "require-trusted-types-for 'script'")
        desc = escape(description, quote=True)
        ttl = escape(title, quote=True)
        social = social or {}
        if not social.get('image'):
            social = {**social, 'image': '/assets/social.png', 'image_alt': 'tegridydev: open source tools, AI and security research'}
        social_meta = ''
        if social and social.get('image'):
            image_url = escape(absolute(social['image']), quote=True)
            image_alt = escape(social['image_alt'], quote=True)
            social_meta = f'<meta property="og:image" content="{image_url}"><meta property="og:image:alt" content="{image_alt}"><meta name="twitter:image" content="{image_url}"><meta name="twitter:image:alt" content="{image_alt}">'
        head = f'''<!doctype html>
<html lang="en" data-theme="mocha" data-theme-choice="system"><head>
<meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="{escape(csp, quote=True)}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{ttl}</title><meta name="description" content="{desc}">
<meta name="author" content="tegridydev"><meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-image-preview:large'}">
<meta name="referrer" content="strict-origin-when-cross-origin"><meta name="color-scheme" content="dark light">
<meta name="theme-color" content="#11111b" id="theme-color"><link rel="canonical" href="{escape(url, quote=True)}">
<link rel="me" href="https://github.com/tegridydev"><link rel="me" href="https://huggingface.co/tegridydev">
<link rel="me" href="https://bsky.app/profile/mechanistics.bsky.social">
<link rel="icon" href="{local('/favicon.svg')}" type="image/svg+xml"><link rel="describedby" href="{local('/llms.txt')}">
<link rel="alternate" type="application/rss+xml" title="tegridydev blog" href="{local('/blog/feed.xml')}">
<link rel="alternate" type="application/rss+xml" title="tegridydev research" href="{local('/research/feed.xml')}">
<meta property="og:type" content="{'article' if schema and schema.get('@type') == 'BlogPosting' else 'website'}">
<meta property="og:site_name" content="tegridydev"><meta property="og:title" content="{ttl}">
<meta property="og:description" content="{desc}"><meta property="og:url" content="{escape(url, quote=True)}">
{social_meta}<meta name="twitter:card" content="{'summary_large_image' if social_meta else 'summary'}"><meta name="twitter:title" content="{ttl}"><meta name="twitter:description" content="{desc}">
{analytics}
<script>{theme}</script><link rel="stylesheet" href="{local(css)}"><link rel="stylesheet" href="{local('/assets/articles.css')}"><link rel="stylesheet" href="{local('/assets/responsive.css')}"><script defer src="{local('/assets/responsive.js')}"></script>
{('<script type="application/ld+json">' + schema_text + '</script>') if schema_text else ''}
</head>'''
        if writing:
            head = head.replace('</head>', '<link rel="stylesheet" href="' + local('/assets/reading.css') + '"><script src="' + local('/assets/reading.js') + '" defer></script></head>')
        tail = footer.replace('{{CONTACT_SCRIPT}}', '<script src="/assets/build/contact.72f5707fe9d1.js" defer></script>' if contact else '')
        tail = tail.replace('{{ANALYTICS}}', '')
        if route != '/':
            tail = tail.replace('href="/#home">top ↑', 'href="#main-content">top ↑')
        nav = header.replace('<body>', '<body class="writing-page">') if writing else header
        active = '/blog/' if route.startswith('/blog/') else '/research/' if route.startswith('/research/') else None
        if active:
            nav = nav.replace(f'href="{active}"', f'href="{active}" aria-current="page"')
        html = head + rebase(nav + body + tail)
        if len(re.findall(r'<h1(?:\s|>)', html)) != 1:
            raise ValueError('Page must contain exactly one H1: ' + route)
        destination = out / (route.strip('/') + '/index.html' if route.endswith('/') and route != '/' else 'index.html' if route == '/' else route.lstrip('/'))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(html, encoding='utf-8')

    desc = 'Open source tools, datasets and practical research by tegridydev across AI security, local LLMs, mechanistic interpretability, OSINT and physical security.'
    home = (template / 'home.html').read_text().replace('{{TOPICS}}', '<p><a href="/topics/">Explore topic reading paths</a></p>' if any(a.get('topic') for a in articles) else '')
    featured_ids = ('blog/what-a-model-map-can-show', 'blog/dataset-discovery-and-preparation', 'research/cloudvec-paper-search')
    featured = [a for identifier in featured_ids for a in articles if a['id'] == identifier]
    home = home.replace('{{WRITING}}', '<h3>Latest writing</h3>' + entries([a for a in blog if a.get('id') not in featured_ids][:5]))
    home = home.replace('{{FEATURED}}', '<h3>Start here</h3>' + entries(featured) if featured else '')
    profile = {'@context': 'https://schema.org', '@type': 'ProfilePage', 'url': absolute('/'),
               'mainEntity': {'@type': 'Person', 'name': 'tegridydev', 'url': absolute('/'),
                              'sameAs': ['https://github.com/tegridydev', 'https://huggingface.co/tegridydev',
                                         'https://bsky.app/profile/mechanistics.bsky.social']}}
    write_page('/', 'tegridydev | Open Source AI and Security Research', desc, home, profile, contact=True)
    for section, items in [('blog', blog), ('research', research)]:
        intro = ('Practical writing about AI tools, datasets, document processing and the things I build.' if section == 'blog' else 'AI and security research notes with methods, controls and measured limits. Proposed study means a plan; local implementation means working code; bounded pilot means a saved experiment with a stated scope.')
        body = f'<main class="container" id="main-content"><div class="document"><h1>{section.title()}</h1><p>{intro}</p><p><a href="/{section}/feed.xml">Subscribe via RSS</a></p>{navigation.index(section, entries)}</div></main>'
        write_page(f'/{section}/', ('AI, Datasets and Developer Tools Blog' if section == 'blog' else 'AI and Security Research Notes') + ' | tegridydev', intro, body)

    by_id = {a['id']: a for a in articles}
    topic_file = infrastructure(root) / 'site/topics.json'
    topics = json.loads(topic_file.read_text()) if topic_file.exists() else []
    topic_routes = []
    topic_ids = set()
    for topic in topics:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', topic['slug']) or topic['slug'] in topic_ids:
            raise ValueError('Invalid or duplicate topic slug')
        topic_ids.add(topic['slug'])
        members = [by_id[x] for x in topic['articles'] if x in by_id]
        if not members:
            continue
        route = '/topics/' + topic['slug'] + '/'
        topic_routes.append(route)
        write_page(route, topic['title'] + ' | tegridydev', topic['description'],
                   '<main class="container" id="main-content"><div class="document"><h1>' + escape(topic['title']) + '</h1><p>' + escape(topic['description']) + '</p>' + ''.join('<h2>' + escape(g['title']) + '</h2><p>' + escape(g['text']) + '</p>' for g in topic.get('guide', [])) + '<h2>Articles in this reading path</h2>' + entries(members) + '<p><a href="/topics/">All reading paths</a></p></div></main>')
    if topic_routes:
        cards = ''.join('<li><a href="/topics/' + t['slug'] + '/">' + escape(t['title']) + '</a>: ' + escape(t['description']) + '</li>' for t in topics if '/topics/' + t['slug'] + '/' in topic_routes)
        write_page('/topics/', 'AI Research and Developer Reading Paths | tegridydev', 'Choose a reading path through document processing, retrieval, AI agents, model evaluation and architecture experiments.', '<main class="container" id="main-content"><div class="document"><h1>Reading paths</h1><p>Choose the problem you are working on. Each path explains where to start and connects practical tools with the experiments behind them.</p><ul>' + cards + '</ul></div></main>')
        topic_routes.append('/topics/')
    asset_owners: dict[str, str] = {}
    for article in articles:
        path = root / article['source']
        # Keep the original H1 as the visible title; add a title only if absent.
        body = article['body']
        if not re.search(r'^# ', body, re.M):
            body = '# ' + article['title'] + '\n\n' + body
        rendered = markdown.markdown(body, extensions=['fenced_code', 'tables', 'toc', 'sane_lists'], output_format='html')

        def article_link(match: re.Match) -> str:
            attr, delim, raw = match[1], match[2], match[3]
            from html import unescape
            parts = urlsplit(unescape(raw))
            if parts.scheme or parts.netloc or not parts.path:
                return match[0]
            source_path = unquote(parts.path)
            resolved = posixpath.normpath(source_path.lstrip('/') if source_path.startswith('/') else str(PurePosixPath(article['source']).parent / source_path))
            if resolved == '..' or resolved.startswith('../'):
                raise ValueError(f'Link outside repository in {article["source"]}: {raw}')
            source = root / resolved
            if not source.is_file() or not source.resolve().is_relative_to(root):
                raise ValueError(f'Missing source link in {article["source"]}: {raw}')
            if resolved in readmes:
                # README section IDs describe setup docs, not the article body.
                if parts.fragment or readmes[resolved] in routes.values():
                    resolved = config['repository'].rstrip('/') + '/blob/main/' + quote(resolved)
                else:
                    resolved = readmes[resolved]
            elif resolved.endswith('.md'):
                if resolved not in routes:
                    raise ValueError(f'Link to unpublished Markdown: {resolved}')
                resolved = routes[resolved]
            elif not public_asset(source, resolved):
                resolved = config['repository'].rstrip('/') + '/blob/main/' + quote(resolved)
            else:
                resolved = '/' + quote(resolved, safe='/@-._~')
            target = urlsplit(resolved)
            rewritten = urlunsplit((target.scheme, target.netloc, target.path, parts.query, parts.fragment))
            return f'{attr}={delim}{escape(rewritten, quote=True)}{delim}'

        rendered = re.sub(r'\b(href|src)=("|\')(.*?)\2', article_link, rendered)
        rendered = image_layout(rendered, root)
        # Only assets alongside this published document are copied. Draft subfolders
        # and unrelated repository files are never recursively published.
        for asset in path.parent.iterdir():
            rel = asset.relative_to(root).as_posix()
            if not public_asset(asset, rel) or asset.name.startswith('.') or not asset.is_file():
                continue
            if asset.is_symlink():
                raise ValueError(f'Symlink not allowed: {asset}')
            rel = asset.relative_to(root).as_posix()
            if rel in asset_owners:
                continue
            asset_owners[rel] = article['source']
            destination = out / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(asset, destination)
        related = article.get('related', [])
        reading = ('<aside aria-label="Related reading"><h2>Related reading</h2>' + entries([by_id[x] for x in related]) + '</aside>') if related else ''
        topic = article.get('topic')
        if topic:
            if topic not in topic_ids:
                raise ValueError('Unknown topic: ' + topic)
            reading += '<p><a href="/topics/' + topic + '/">Explore this reading path</a></p>'
        status = {'proposal': 'Proposed study', 'implemented': 'Local implementation', 'pilot': 'Bounded pilot; see scope and results'}.get(article.get('status'), '')
        meta = '<a rel="author" href="/">' + escape(config['author']) + '</a>' + (' · ' + date_label(article['date']) if article['date'] else '')
        if article['updated']:
            meta += ' · Updated ' + date_label(article['updated'])
        if status:
            meta += ' · ' + status
        body = (f'<main class="container" id="main-content"><article class="article">'
                f'<p><a href="/{article["section"]}/">← {article["section"].title()}</a></p>'
                f'<p class="article-meta">{meta}</p>'
                + rendered + reading + f'<p class="article-nav"><a href="{escape(config["repository"], quote=True)}/blob/main/{quote(article["source"])}">Source on GitHub</a> · '
                + (f'<a href="{escape(config["repository"], quote=True)}/blob/main/{quote(path.with_name("README.md").relative_to(root).as_posix())}">Setup and supporting files</a> · ' if path.with_name('README.md').is_file() else '')
                +
                f'<a href="/{article["section"]}/">More {article["section"]}</a></p></article></main>')
        schema = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': article['title'],
                  'description': article['description'], 'datePublished': article['date'], 'dateModified': article['updated'],
                  'author': {'@type': 'Person', 'name': config['author'], 'url': absolute('/')},
                  'mainEntityOfPage': absolute(article['route'])}
        # Schema.org Date and RSS dates need a full date; do not invent one.
        for key in ('datePublished', 'dateModified'):
            if len(schema[key]) != 10:
                del schema[key]
        schema['image'] = absolute(article.get('image') or '/assets/social.png')
        schema['inLanguage'] = 'en'
        schema['url'] = absolute(article['route'])
        write_page(article['route'], article['title'] + ' | tegridydev', article['description'], body, schema, social=article)

    analytics_text = ('This site uses Umami Cloud to understand page visits, referring websites, approximate location, '
                      'browser and device information, and page performance. The tracker sends page information and '
                      'performance measurements to Umami. Only the campaign labels utm_source, utm_medium and utm_campaign are retained from page query strings. Other query values and fragments are excluded. '
                      'Browser Do Not Track preferences are respected. Clicks on external links, demo links and contact controls are counted using limited category information. No email addresses, form answers or full destination URLs are attached to these events. This integration does not configure session recordings, '
                      'heatmaps or user identities. '
                      '<a href="https://umami.is/privacy">Umami privacy policy</a>.') if analytics_enabled else 'No website analytics tracking script is included in this preview or build.'

    privacy = ('<main class="container" id="main-content"><div class="document"><h1>Privacy</h1>'
               '<p>Last updated 9 September 2026.</p><h2>Website analytics</h2><p>' + analytics_text + '</p><h2>Local preferences and contact</h2>'
               '<p>Your theme choice is stored locally as <code>td-theme</code>. The contact check runs in your browser. '
               'Revealing or copying the address sends no message.</p><h2>Hosting</h2>'
               '<p>GitHub Pages hosts this site and logs visitor IP addresses for security purposes. '
               '<a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub privacy statement</a>. '
               'Cloudflare manages the domain’s DNS. If its proxy is enabled, Cloudflare also receives web requests to deliver and protect the site. '
               '<a href="https://www.cloudflare.com/privacypolicy/">Cloudflare privacy policy</a>.</p>'
               '<h2>Other websites</h2><p>External links lead to independently operated sites with their own policies.</p>'
               '<h2>Questions</h2><p>Use the <a href="/#contact">contact section</a>.</p></div></main>')
    write_page('/privacy/', 'Privacy | tegridydev', 'How this website handles hosting, analytics and local preferences.', privacy)
    write_page('/404.html', 'Page not found | tegridydev', 'This page could not be found.',
               '<main class="container" id="main-content"><div class="document"><h1>Page not found</h1><p>That page may have moved.</p><p><a href="/">Home</a> · <a href="/blog/">Blog</a> · <a href="/research/">Research</a></p></div></main>', noindex=True)
    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    sitemap = ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')
    for route in ['/', '/blog/', '/research/', '/privacy/'] + topic_routes + [a['route'] for a in articles]:
        node = ET.SubElement(sitemap, 'url'); ET.SubElement(node, 'loc').text = absolute(route)
        modified = next((a['updated'] for a in articles if a['route'] == route), '')
        if len(modified) == 10:
            ET.SubElement(node, 'lastmod').text = modified
    ET.ElementTree(sitemap).write(out / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (out / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {absolute("/sitemap.xml")}\n')
    for section, items in [('blog', blog), ('research', research)]:
        rss = ET.Element('rss', version='2.0'); channel = ET.SubElement(rss, 'channel')
        for tag, value in [('title', f'tegridydev {section}'), ('link', absolute(f'/{section}/')), ('description', f'Writing by tegridydev: {section}'), ('language', 'en')]:
            ET.SubElement(channel, tag).text = value
        for article in items:
            item = ET.SubElement(channel, 'item')
            for tag, value in [('title', article['title']), ('link', absolute(article['route'])), ('description', article['description'])]:
                ET.SubElement(item, tag).text = value
            ET.SubElement(item, 'guid', isPermaLink='false').text = 'urn:tegridy:' + article['id'] if article.get('id') else article['url']
            if len(article['date']) == 10:
                ET.SubElement(item, 'pubDate').text = format_datetime(datetime.combine(date.fromisoformat(article['date']), datetime.min.time(), timezone.utc))
        ET.ElementTree(rss).write(out / section / 'feed.xml', encoding='utf-8', xml_declaration=True)
    (out / '.nojekyll').touch()
    domain = config.get('custom_domain', '')
    if domain and not preview and base == site_url(config['url']):
        if not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?', domain) or domain != urlsplit(base).hostname or prefix:
            raise ValueError('custom_domain must match the production URL hostname without a path')
        (out / 'CNAME').write_text(domain + '\n', encoding='utf-8')
    (out / 'llms.txt').write_text('# tegridydev\n\nOpen-source tools, datasets and practical research.\n\n' + '\n'.join(f'- [{label}]({absolute(route)})' for label, route in [('Home','/'),('Blog','/blog/'),('Research','/research/')]) + '\n')
    validate(out, base)
    print(f'Built {len(articles)} local articles and {len(external)} external links')


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.ids = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if tag in {'a', 'link', 'img', 'script', 'source', 'video'}:
            for key in ('href', 'src', 'poster'):
                if a.get(key): self.links.append(a[key])
        if a.get('srcset'):
            # Data URLs may contain commas; those are embedded, not local files.
            if not a['srcset'].lstrip().startswith('data:'):
                self.links.extend(part.strip().split()[0] for part in a['srcset'].split(',') if part.strip())


def validate(out: Path, base: str) -> None:
    """Check local HTML/CSS dependencies and static fragment targets, offline."""
    out = out.resolve()
    prefix = urlsplit(base).path.rstrip('/')
    errors = []
    pages = {}
    for path in out.rglob('*.html'):
        parser = Links()
        parser.feed(path.read_text(encoding='utf-8'))
        pages[path] = parser
        if len(parser.ids) != len(set(parser.ids)):
            errors.append(f'{path.relative_to(out)}: duplicate HTML IDs')
    resources = [(p, parser.links) for p, parser in pages.items()]
    for path in out.rglob('*.css'):
        links = re.findall(r"url\(\s*[\"']?([^\"')\s]+)", path.read_text(encoding='utf-8'))
        resources.append((path, links))
    for path, links in resources:
        for link in links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc:
                continue
            target = unquote(parts.path)
            if not target:
                dest = path
            elif target.startswith('/'):
                if prefix and target != prefix and not target.startswith(prefix + '/'):
                    errors.append(f'{path.relative_to(out)}: missing base path: {target}')
                    continue
                dest = out / target[len(prefix):].lstrip('/')
            else:
                dest = path.parent / target
            dest = dest.resolve()
            if not dest.is_relative_to(out):
                errors.append(f'{path.relative_to(out)}: link outside output {link}')
                continue
            if dest.is_dir():
                dest /= 'index.html'
            if not dest.is_file():
                errors.append(f'{path.relative_to(out)}: broken link {link}')
            elif parts.fragment and dest in pages and unquote(parts.fragment) not in pages[dest].ids:
                errors.append(f'{path.relative_to(out)}: missing fragment {link}')
    if errors:
        raise ValueError('\n'.join(errors))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', action='store_true', help='Build into _preview without production analytics or CNAME')
    parser.add_argument('--base-url', help='Override deployment URL, including /tegridy for project Pages')
    args = parser.parse_args()
    try:
        build(base_url=args.base_url, preview=args.preview)
    except (ValueError, OSError, KeyError, tomllib.TOMLDecodeError) as exc:
        sys.exit(f'Build failed: {exc}')
