"""Validate a question/evidence ledger without inventing support judgements."""
import argparse
import hashlib
import json
from pathlib import Path


def validate(data, root):
    if data.get('schema') != 1 or not isinstance(data.get('question'),str) or not data['question'].strip():
        raise ValueError('schema 1 and an explicit question required')
    root=Path(root).resolve()
    evidence={}
    for row in data['evidence']:
        if not row['id'] or row['id'] in evidence:raise ValueError('duplicate or empty evidence ID')
        path=(root/row['path']).resolve()
        if not path.is_relative_to(root) or not path.is_file():raise ValueError('evidence path missing or outside ledger folder')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('evidence content changed')
        evidence[row['id']]=row
    claims={}
    for row in data['claims']:
        if not row['id'] or row['id'] in claims or not row['statement'].strip():raise ValueError('claim identity and statement required')
        if row['status'] not in {'proposed','supported','contradicted','inconclusive','withdrawn'}:raise ValueError('unknown claim status')
        if row.get('supersedes') is not None and row['supersedes'] not in claims:raise ValueError('prior claim must precede revision')
        if any(identity not in evidence for identity in row['evidence']):raise ValueError('unknown evidence reference')
        if row['status'] in {'supported','contradicted'} and (not row['evidence'] or not row.get('reviewer') or not row.get('reason')):raise ValueError('attributed evidence judgement required')
        claims[row['id']]=row
    return dict(question=data['question'],claims=len(claims),evidence=len(evidence),
                unresolved=[r['id'] for r in claims.values() if r['status'] in {'proposed','inconclusive'}],
                scope='Reference/hash consistency only; human support judgements are not independently verified.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('ledger',type=Path);a=p.parse_args()
    print(json.dumps(validate(json.loads(a.ledger.read_text()),a.ledger.parent),indent=2))
