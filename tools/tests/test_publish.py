"""Exercise publication against a local bare remote; never contact GitHub."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import publish
SETTINGS = {'source': {'branch': 'static', 'path': '/'}, 'cname': 'tegridydev.com', 'https_enforced': True, 'build_type': 'legacy'}
class PublishTests(unittest.TestCase):
    def test_settings_cannot_change_hosting(self):
        publish.validate_settings(SETTINGS)
        for change in ({'source': {'branch': 'main', 'path': '/'}}, {'cname': None}, {'https_enforced': False}, {'build_type': 'workflow'}):
            with self.assertRaises(RuntimeError): publish.validate_settings({**SETTINGS, **change})
    def test_real_static_sync_and_build_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); root=base/'main'; remote=base/'remote.git'; root.mkdir()
            def run(*args,cwd=root):
                return subprocess.check_output(['git',*args],cwd=cwd,text=True,stderr=subprocess.DEVNULL).strip()
            run('init','--bare',str(remote),cwd=base); run('init','-b','main')
            run('config','user.name','Test');run('config','user.email','test@example.com')
            (root/'source.txt').write_text('main source');run('add','.');run('commit','-m','Source')
            sha=run('rev-parse','HEAD');run('remote','add','origin',str(remote));run('push','origin','main')
            run('checkout','-b','static');(root/'obsolete.txt').write_text('old output');run('add','.');run('commit','-m','Old site')
            old=run('rev-parse','HEAD');run('push','origin','static');run('checkout','main')
            output=base/'releases/_site';output.mkdir(parents=True)
            for name,text in {'index.html':'new site','sitemap.xml':'<urlset/>','robots.txt':'User-agent: *','.nojekyll':'','CNAME':'tegridydev.com\n'}.items():
                (output/name).write_text(text)
            requests=[]
            def api(path,method='GET'):
                requests.append((path,method))
                if path.endswith('/pages'):return SETTINGS
                if path.endswith('/git/ref/heads/main'):return {'object':{'sha':sha}}
                if path.endswith('/pages/builds/latest'):return {'commit':run('rev-parse','static',cwd=remote),'status':'built'}
                if path.endswith('/pages/builds') and method=='POST':return {'status':'queued'}
                raise AssertionError((path,method))
            env={'GITHUB_REPOSITORY':'tegridydev/tegridy','GITHUB_SHA':sha,'GITHUB_REF':'refs/heads/main'}
            with patch.dict(os.environ,env),patch.object(publish,'__file__',str(root/'tools/publish.py')),patch.object(publish,'api',side_effect=api):
                publish.main();first=run('rev-parse','static',cwd=remote)
                publish.main();self.assertEqual(first,run('rev-parse','static',cwd=remote))
            self.assertEqual(set(run('ls-tree','--name-only','static',cwd=remote).splitlines()),{'index.html','sitemap.xml','robots.txt','.nojekyll','CNAME'})
            self.assertEqual(run('rev-parse','static^',cwd=remote),old);self.assertEqual(run('rev-parse','HEAD'),sha)
            self.assertEqual(sum(method=='POST' for _,method in requests),2)
            self.assertTrue(all(method in ('GET','POST') for _,method in requests))
            (output/'CNAME').write_text('wrong.example')
            with self.assertRaises(RuntimeError):publish.validate_output(output)
            (output/'CNAME').write_text('tegridydev.com');(output/'unsafe').symlink_to(root/'source.txt')
            with self.assertRaises(RuntimeError):publish.validate_output(output)
if __name__=='__main__':unittest.main()
