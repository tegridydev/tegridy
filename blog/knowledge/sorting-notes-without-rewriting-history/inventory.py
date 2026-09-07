"""Read-only archive inventory and exact-duplicate proposal; never moves source files."""
import argparse
import hashlib
import json
from pathlib import Path
import unicodedata


def inventory(root):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('archive must be a directory')
    files, excluded = [], []
    groups, names = {}, {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            excluded.append(dict(path=str(path.relative_to(root)), reason='symbolic link'))
            continue
        if not path.is_file():
            continue
        before = path.stat()
        hasher = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024*1024), b''):
                hasher.update(chunk)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            raise ValueError('file changed during inventory: '+str(path))
        relative = str(path.relative_to(root))
        row = dict(path=relative, bytes=after.st_size, sha256=hasher.hexdigest())
        files.append(row)
        groups.setdefault(row['sha256'], []).append(relative)
        names.setdefault(unicodedata.normalize('NFC', path.name).casefold(), []).append(row)
    return dict(schema=1, files=files, excluded=excluded,
                exact_duplicates=[dict(sha256=k, paths=v, action='review; retain originals') for k,v in groups.items() if len(v)>1],
                name_conflicts=[dict(name=k, files=v) for k,v in names.items() if len({r['sha256'] for r in v})>1],
                policy='Content hashes establish byte identity only. No automatic deletion, relocation or semantic deduplication.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive',type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.output and a.output.resolve().is_relative_to(a.archive.resolve()):
        p.error('save the report outside the source archive')
    text=json.dumps(inventory(a.archive),indent=2,ensure_ascii=False)+'\n'
    if a.output:
        with a.output.open('x',encoding='utf-8') as stream:stream.write(text)
    else:print(text,end='')


if __name__=='__main__':main()
