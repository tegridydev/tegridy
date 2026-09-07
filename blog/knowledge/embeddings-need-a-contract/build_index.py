"""Build a document index with the explicitly acquired pinned encoder."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'research'))
from model_assets import encoder


def build(documents):
    if not documents or len({d['id'] for d in documents})!=len(documents) or any(not isinstance(d['text'],str) or not d['text'].strip() for d in documents):raise ValueError('unique document IDs and nonempty text required')
    encode,manifest,entry=encoder()
    vectors=encode([d['text'] for d in documents])
    return dict(manifest=manifest,documents=[dict(d,vector=v) for d,v in zip(documents,vectors)],model=entry)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('documents',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    index=build(json.loads(a.documents.read_text()))
    with a.output.open('x') as stream:json.dump(index,stream,indent=2,allow_nan=False)
