"""Acquire explicitly selected HTTPS files with pinned hashes and bounded size."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request
from urllib.parse import urlsplit


class HTTPSOnly(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,fp,code,msg,headers,newurl):
        if urlsplit(newurl).scheme!='https':raise ValueError('redirect left HTTPS')
        return super().redirect_request(request,fp,code,msg,headers,newurl)


def acquire(entry, destination, limit=25_000_000):
    if type(limit) is not int or limit<1:raise ValueError('positive download limit required')
    if urlsplit(entry['url']).scheme!='https' or not entry.get('rights') or len(entry.get('sha256',''))!=64:
        raise ValueError('explicit HTTPS URL, rights description and pinned SHA-256 required')
    expected=entry['sha256'].lower()
    if any(c not in '0123456789abcdef' for c in expected):raise ValueError('invalid SHA-256')
    destination=Path(destination)
    if destination.exists():
        if hashlib.sha256(destination.read_bytes()).hexdigest()==expected:
            return dict(status='already-acquired',sha256=expected,bytes=destination.stat().st_size)
        raise FileExistsError('destination contains different bytes')
    destination.parent.mkdir(parents=True,exist_ok=True)
    temporary=None
    try:
        request=urllib.request.Request(entry['url'],headers={'User-Agent':'tegridy-local-acquisition/1.0'})
        with urllib.request.build_opener(HTTPSOnly()).open(request,timeout=30) as response, tempfile.NamedTemporaryFile(dir=destination.parent,delete=False) as stream:
            temporary=Path(stream.name);count=0;digest=hashlib.sha256()
            while chunk:=response.read(65536):
                count+=len(chunk)
                if count>limit:raise ValueError('download exceeds declared byte limit')
                digest.update(chunk);stream.write(chunk)
            final_url=response.url
        if digest.hexdigest()!=expected:raise ValueError('download hash does not match pinned source')
        # Exclusive copy prevents an existing destination being replaced.
        with destination.open('xb') as target,temporary.open('rb') as source:
            import shutil
            shutil.copyfileobj(source,target)
        return dict(status='acquired',sha256=expected,bytes=count,url=entry['url'],final_url=final_url,rights=entry['rights'],reading_status='unread')
    finally:
        if temporary:temporary.unlink(missing_ok=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('entry',type=Path);p.add_argument('output',type=Path);p.add_argument('--max-bytes',type=int,default=25_000_000);a=p.parse_args()
    print(json.dumps(acquire(json.loads(a.entry.read_text()),a.output,a.max_bytes),indent=2))
