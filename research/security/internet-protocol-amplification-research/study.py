"""Matched simulated workloads with explicit admission and deadline ledgers."""
import json
from pathlib import Path
import random
from budgets import simulate_lifetimes


def run(seed,data_seed,profile,output):
    rng=random.Random(data_seed+seed); rows=[];metrics={}
    for index in range(10 if profile=='smoke' else 100):
        family=['ordinary','incomplete','burst','slow'][index%4]
        jobs=[dict(id=str(i),arrival=i if family!='burst' else i//20,
                   duration=None if family=='incomplete' and i%3==0 else rng.randrange(15,30) if family=='slow' else rng.randrange(1,6)) for i in range(100)]
        for policy,deadline in [('short',5),('long',20)]:
            result=simulate_lifetimes(jobs,capacity=16,deadline=deadline,work_budget=100)
            if result['completed']+result['expired']+result['rejected']!=len(jobs):raise ValueError('lost job')
            if result['peak_active']>16 or result['charged_work']>100:raise ValueError('budget exceeded')
            rows.append(dict(workload=index,family=family,policy=policy,deadline=deadline,**result))
    for family in ['ordinary','incomplete','burst','slow']:
        for policy in ['short','long']:
            selected=[r for r in rows if r['family']==family and r['policy']==policy]
            for metric in ['completed','expired','rejected','peak_active']:
                metrics[family+'.'+policy+'.'+metric]=sum(r[metric] for r in selected)/len(selected)
    Path(output,'ledgers.json').write_text(json.dumps(rows,indent=2)+'\n')
    return dict(scope='100 synthetic simulated workloads per CPU seed; deadline/capacity trade-off, no sockets or deployed-protocol measurements.',metrics=metrics,seed=seed,data_seed=data_seed)
