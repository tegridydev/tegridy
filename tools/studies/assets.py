"""Explicit acquisition of public model snapshots; never reads account tokens."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from huggingface_hub import HfApi,snapshot_download

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
MODELS={'encoder':'sentence-transformers/all-MiniLM-L6-v2','causal':'EleutherAI/gpt-neo-125m'}


def fetch(name):
    repo=MODELS[name]
    path=HERE/'assets.json'
    existing=json.loads(path.read_text()) if path.exists() else {'schema':1,'models':{}}
    previous=existing['models'].get(name)
    info=HfApi(token=False).model_info(repo,revision=previous['revision'] if previous else None)
    revision=previous['revision'] if previous else info.sha
    if not re.fullmatch('[0-9a-f]{40}',revision):raise ValueError('model revision is not immutable')
    destination=ROOT/'tools/_models'/name/revision
    snapshot_download(repo_id=repo,revision=revision,token=False,local_dir=destination,
                      allow_patterns=['*.json','*.txt','*.safetensors'],max_workers=2)
    files={str(p.relative_to(destination)):hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.rglob('*') if p.is_file() and not any(part.startswith('.') for part in p.relative_to(destination).parts)}
    if 'model.safetensors' not in files:raise ValueError('expected safe tensor weights missing')
    path=HERE/'assets.json'
    data=json.loads(path.read_text()) if path.exists() else {'schema':1,'models':{}}
    data['models'][name]=dict(repo=repo,revision=revision,directory=str(destination.relative_to(ROOT)),files=files,
                              source='https://huggingface.co/'+repo+'/tree/'+revision,
                              licence=info.card_data.get('license') if info.card_data else None)
    temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n');temporary.replace(path)
    print(name,repo,revision,'files',len(files),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('name',choices=list(MODELS)+['all']);args=parser.parse_args()
    for name in MODELS if args.name=='all' else [args.name]:fetch(name)
