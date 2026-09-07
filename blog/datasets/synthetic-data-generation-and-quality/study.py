"""Generation, deliberate rejection and connected-world split accounting."""
from pathlib import Path
import json
from generate import generate,verify


def run(seed,data_seed,profile,output):
    records=generate(20 if profile=='smoke' else 10000,seed+data_seed);states={};parents={};rejected=[]
    for index,row in enumerate(records):
        if not verify(row)['valid']:raise ValueError('generated invalid row')
        states.setdefault(tuple(row['state']),set()).add(row['split']);parents.setdefault(row['parent_id'],set()).add(row['split'])
        if index%100==0:
            bad=dict(row,answer=row['answer']+1);verdict=verify(bad)
            if verdict['valid']:raise ValueError('wrong answer accepted')
            rejected.append(dict(record=bad,verification=verdict))
    if any(len(s)!=1 for s in list(states.values())+list(parents.values())):raise ValueError('connected world crosses split')
    with Path(output,'generated.jsonl').open('w') as stream:
        for row in records:stream.write(json.dumps(row)+'\n')
    Path(output,'rejected.json').write_text(json.dumps(rejected,indent=2)+'\n')
    return dict(scope='Explicit inventory-arithmetic grammar at larger generation scale, deliberate answer corruption and split accounting. Broader rule families and downstream training value are not established.',metrics=dict(rows=len(records),parent_worlds=len(parents),distinct_states=len(states),deliberately_rejected=len(rejected),split_leaks=0),seed=seed,data_seed=data_seed)
