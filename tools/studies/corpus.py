"""Explicit pinned WikiText-2 acquisition and document-boundary reconstruction."""
import hashlib
import json
from pathlib import Path
import re
from huggingface_hub import HfApi,snapshot_download
import pyarrow.parquet as pq

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent


def fetch():
    repo='Salesforce/wikitext';manifest=HERE/'corpus.json'
    old=json.loads(manifest.read_text()) if manifest.exists() else None
    info=HfApi(token=False).dataset_info(repo);revision=old['revision'] if old else info.sha
    if not re.fullmatch('[0-9a-f]{40}',revision):raise ValueError('immutable revision required')
    destination=ROOT/'tools/_datasets/wikitext'/revision
    snapshot_download(repo,repo_type='dataset',revision=revision,token=False,local_dir=destination,allow_patterns=['wikitext-2-raw-v1/*.parquet'],max_workers=2)
    files={};documents=[];owners={}
    for split in ['train','validation','test']:
        path=destination/'wikitext-2-raw-v1'/f'{split}-00000-of-00001.parquet'
        files[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
        lines=pq.read_table(path,columns=['text']).column('text').to_pylist();title=None;body=[]
        def finish():
            if title is None or not body:return
            raw=''.join(body).encode();digest=hashlib.sha256(raw).hexdigest()
            previous=owners.get(title)
            if previous and previous!=split:raise ValueError('article title crosses official splits: '+title)
            owners[title]=split
            documents.append(dict(title=title,split=split,sha256=digest,text=raw.decode()))
        for line in lines:
            if re.fullmatch(r'\s*=\s+[^=].*?\s+=\s*',line):
                finish();title=line.strip();body=[line]
            elif title is not None:body.append(line)
        finish()
    processed=destination/'documents.json';processed.write_text(json.dumps(documents,ensure_ascii=False)+'\n')
    files[str(processed.relative_to(ROOT))]=hashlib.sha256(processed.read_bytes()).hexdigest()
    metadata=dict(schema=1,repo=repo,revision=revision,source='https://huggingface.co/datasets/'+repo+'/tree/'+revision,
                  licence=info.card_data.get('license') if info.card_data else None,documents_path=str(processed.relative_to(ROOT)),files=files,
                  split_documents={split:sum(d['split']==split for d in documents) for split in ['train','validation','test']},
                  split_bytes={split:sum(len(d['text'].encode()) for d in documents if d['split']==split) for split in ['train','validation','test']})
    manifest.write_text(json.dumps(metadata,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in metadata.items() if k!='files'},indent=2))


if __name__=='__main__':fetch()
