"""Publish validated output to the existing static branch and request its Pages build.

Runs only from the main branch workflow. Never changes Pages configuration.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from urllib.request import Request, urlopen


def git(*args, cwd=None):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()


def validate_settings(settings):
    if settings.get('source') != {'branch': 'static', 'path': '/'}:
        raise RuntimeError('Pages must already publish static at /. No settings were changed.')
    if settings.get('cname') != 'tegridydev.com' or settings.get('https_enforced') is not True:
        raise RuntimeError('Expected tegridydev.com with HTTPS enforced. No settings were changed.')
    if settings.get('build_type', 'legacy') != 'legacy':
        raise RuntimeError('Expected the existing branch based Pages publishing source.')


def validate_output(output):
    if not output.is_dir() or output.is_symlink():
        raise RuntimeError('Missing or unsafe build output')
    for name in ('index.html', 'sitemap.xml', 'robots.txt', '.nojekyll'):
        if not (output / name).is_file():
            raise RuntimeError('Incomplete build: ' + name)
    if (output / 'CNAME').read_text().strip() != 'tegridydev.com':
        raise RuntimeError('The build must preserve the custom domain')
    if any(p.is_symlink() or p.name == '.git' for p in output.rglob('*')):
        raise RuntimeError('Unsafe file in build output')


def api(path, method='GET'):
    request = Request('https://api.github.com' + path, method=method,
                      data=b'{}' if method == 'POST' else None,
                      headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                               'Accept': 'application/vnd.github+json',
                               'X-GitHub-Api-Version': '2026-03-10'})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    repo = os.environ['GITHUB_REPOSITORY']
    sha = os.environ['GITHUB_SHA']
    if repo != 'tegridydev/tegridy' or os.environ['GITHUB_REF'] != 'refs/heads/main':
        raise RuntimeError('Publishing is restricted to tegridydev/tegridy main')
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise RuntimeError('Invalid source commit')
    root = Path(__file__).resolve().parents[1]
    output = root.parent / 'releases/_site'
    validate_output(output)
    endpoint = '/repos/' + repo
    validate_settings(api(endpoint + '/pages'))
    # A newer main commit should publish instead of this queued run.
    if api(endpoint + '/git/ref/heads/main')['object']['sha'] != sha:
        print('A newer main commit exists. Skipping this stale publication.')
        return
    git('fetch', '--no-tags', 'origin', 'static', cwd=root)
    with tempfile.TemporaryDirectory(prefix='tegridy-publish-') as folder:
        checkout = Path(folder) / 'static'
        git('worktree', 'add', '--detach', str(checkout), 'FETCH_HEAD', cwd=root)
        try:
            for item in checkout.iterdir():
                if item.name == '.git':
                    continue
                if item.is_dir() and not item.is_symlink():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            shutil.copytree(output, checkout, dirs_exist_ok=True)
            git('add', '--all', cwd=checkout)
            if git('status', '--porcelain', cwd=checkout):
                git('-c', 'user.name=github-actions[bot]', '-c',
                    'user.email=41898282+github-actions[bot]@users.noreply.github.com',
                    'commit', '-m', 'Build site from main ' + sha, cwd=checkout)
                # Fast forward only. Concurrent manual edits cause a safe failure.
                git('push', 'origin', 'HEAD:refs/heads/static', cwd=checkout)
            published = git('rev-parse', 'HEAD', cwd=checkout)
        finally:
            git('worktree', 'remove', '--force', str(checkout), cwd=root)
    # GITHUB_TOKEN pushes do not trigger branch based Pages builds automatically.
    api(endpoint + '/pages/builds', method='POST')
    wait_for_pages(endpoint, published, sha)


def wait_for_pages(endpoint, published, source, attempts=90):
    """Confirm the exact output commit despite overlapping Pages builds."""
    last_status = 'unknown'
    for _ in range(attempts):
        result = api(endpoint + '/pages/builds/latest')
        if result.get('commit') == published:
            last_status = result.get('status', 'unknown')
            if last_status == 'built':
                print('Pages built static commit ' + published + ' from main ' + source)
                return
        # A cancelled duplicate can leave the legacy endpoint errored while the
        # generated Pages workflow for the same commit is still deploying.
        data = api(endpoint + '/actions/runs?head_sha=' + published + '&per_page=100')
        runs = [run for run in data.get('workflow_runs', [])
                if run.get('head_sha') == published
                and run.get('path') == 'dynamic/pages/pages-build-deployment']
        if any(run.get('status') == 'completed' and run.get('conclusion') == 'success' for run in runs):
            print('Pages deployed static commit ' + published + ' from main ' + source)
            return
        time.sleep(10)
    raise RuntimeError('Pages deployment not confirmed for static commit ' + published
                       + '. Last Pages status: ' + str(last_status)
                       + '. Static is updated; check the matching Pages workflow logs.')



if __name__ == '__main__':
    main()
