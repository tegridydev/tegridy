"""Finite fictional utility decisions with explicit hard-constraint accounting."""
import json
from pathlib import Path
import random
from perspectives import evaluate


def run(seed,data_seed,profile,output):
    rng=random.Random(seed+data_seed);rows=[];disagreements=0
    for case in range(10 if profile=='smoke' else 200):
        actions=[dict(id=str(i),scores=dict(speed=rng.random(),cost=rng.random(),reliability=rng.random()),facts=dict(spend=rng.randrange(200),delay=rng.randrange(30))) for i in range(5)]
        constraints=dict(spend=rng.randrange(50,150),delay=rng.randrange(10,30))
        views={name:evaluate(actions,weights,constraints) for name,weights in [('speed',dict(speed=.8,cost=.1,reliability=.1)),('cost',dict(speed=.1,cost=.8,reliability=.1)),('reliability',dict(speed=.1,cost=.1,reliability=.8))]}
        for result in views.values():
            for winner in result['winners']:
                action=next(a for a in actions if a['id']==winner)
                if any(action['facts'][k]>limit for k,limit in constraints.items()):raise ValueError('infeasible winner')
        disagreements+=len({tuple(v['winners']) for v in views.values()})>1
        rows.append(dict(id=case,actions=actions,constraints=constraints,perspectives=views))
    Path(output,'decisions.json').write_text(json.dumps(rows,indent=2)+'\n')
    return dict(scope='Varied fictional finite utilities and objective budget ceilings; this measures value-weight sensitivity, not real-world moral judgement or language-model deliberation.',metrics=dict(cases=len(rows),disagreement_rate=disagreements/len(rows),infeasible_winners=0),seed=seed,data_seed=data_seed)
