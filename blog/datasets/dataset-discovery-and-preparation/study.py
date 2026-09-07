"""Measured row-accounting and split-isolation workload with retained input."""
from pathlib import Path
import json
import random
import time
from prepare import prepare


def run(seed,data_seed,profile,output):
    rng=random.Random(seed+data_seed);count=100 if profile=='smoke' else 10000
    rows=[dict(id=f'{i:06d}',group=f'group-{i//4}',text=f' example {rng.randrange(1000)} ',nullable=None) for i in range(count)]
    rows += [dict(rows[i]) for i in range(0,count,10)]
    rows += [dict(rows[i],text='conflicting original') for i in range(0,count,17)]
    rows += [None,{},dict(id=123)]
    recipe=dict(id_field='id',group_field='group',protected_fields=['id'],trim_outer_whitespace=['text'],duplicate_key_policy='quarantine-conflicts',missing_value_policy='preserve-null')
    start=time.perf_counter();result=prepare(rows,recipe,seed);elapsed=time.perf_counter()-start
    indices=[e['source_row'] for key in ['accepted','quarantined','rejected','duplicates'] for e in result[key]]
    if sorted(indices)!=list(range(len(rows))):raise ValueError('missing or duplicated row accounting')
    groups={}
    for row in result['accepted']:groups.setdefault(row['input']['group'],set()).add(row['split'])
    if any(len(v)!=1 for v in groups.values()):raise ValueError('group crossed split')
    Path(output,'input.json').write_text(json.dumps(rows)+'\n');Path(output,'receipt.json').write_text(json.dumps(dict(recipe=recipe,**result),indent=2)+'\n')
    return dict(scope='Synthetic mixed-quality row accounting and grouped splitting; no discovery-provider or downstream-quality claim.',metrics=dict(**result['counts'],input_rows=len(rows),elapsed_seconds=elapsed,split_leaks=0),seed=seed,data_seed=data_seed)
