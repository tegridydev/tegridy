"""Varied synthetic correction histories with source-owner and temporal controls."""
from pathlib import Path
import json
import random
from retrieval import Memory,Item


def run(seed,data_seed,profile,output):
    rng=random.Random(seed+data_seed);rows=[];metrics={}
    families=['drink','timeout','address','timezone','project','editor','meeting','dataset','format','language']
    for index in range(10 if profile=='smoke' else 200):
        fact=families[index%len(families)];owner='owner-'+str(index);items=[]
        for version in range(rng.randrange(2,7)):
            items.append(Item(f'v{version}',owner,fact,f'{fact} value-{rng.randrange(10000)}',f'event-{version}',version*3,version*3+1))
        versions=list(items)
        target=versions[rng.randrange(len(versions))]
        previous=next((v.id for v in reversed(versions) if v.recorded<target.recorded),None)
        for distractor in range(20):items.append(Item(f'd{distractor}',owner,f'noise-{distractor}',f'unrelated note {distractor}',f'noise-event-{distractor}',100+distractor,100+distractor))
        items.append(Item('other','different-owner',fact,f'{fact} same display name','other-event',0,0))
        memory=Memory(items)
        for policy in ['relevant','recent']:
            for query_kind,as_of,known_at,expected in [('current',1000,1000,versions[-1].id),('historical',target.effective,target.recorded,target.id),('known_then',target.effective,target.recorded-1,previous)]:
                result=memory.retrieve(owner,fact,as_of,known_at,budget=3,policy=policy)
                rows.append(dict(history=index,family=fact,policy=policy,kind=query_kind,expected=expected,correct=(expected in result['selected'] if expected is not None else not result['selected']),trace=result))
    for policy in ['relevant','recent']:
        for kind in ['current','historical','known_then']:
            selected=[r for r in rows if r['policy']==policy and r['kind']==kind]
            metrics[policy+'.'+kind+'.recall']=sum(r['correct'] for r in selected)/len(selected)
    if any('other' in r['trace']['selected'] for r in rows):raise ValueError('cross-owner leak')
    Path(output,'retrieval-traces.json').write_text(json.dumps(rows,indent=2)+'\n')
    return dict(scope='Synthetic lexical memory retrieval across ten fact vocabularies, corrections and owner collisions; whitespace-word budget, no model-answering or semantic paraphrase claim.',metrics=metrics,seed=seed,data_seed=data_seed)
