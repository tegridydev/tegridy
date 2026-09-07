"""Sixty synthetic documents with explicit qualified-by evidence relationships."""
from pathlib import Path
import json
from cedar import retrieve


def run(seed,data_seed,profile,output):
    sources={};edges=[];questions=[]
    for i in range(20):
        sources[f'a{i}']=dict(text=f'Product{i} deployment documentation.',release=str(i))
        sources[f'b{i}']=dict(text=f'The linked default timeout is {10+i} seconds.',release=str(i))
        sources[f'c{i}']=dict(text=f'An upgrade retains the prior configured value {30+i}.',release=str(i))
        edges += [dict(source=f'a{i}',target=f'b{i}',reviewed=True,reason='Synthetic manual points to its default specification.'),dict(source=f'b{i}',target=f'c{i}',reviewed=True,reason='Synthetic default has an upgrade exception.')]
        questions.append(dict(query=f'Product{i}',release=str(i),support=[f'b{i}',f'c{i}']))
    rows=[];metrics={}
    for question in questions:
        for policy,hops in [('lexical',0),('graph',2)]:
            result=retrieve(sources,edges,question['query'],{'release':question['release']},budget=40,initial_limit=1,max_hops=hops)
            recall=len(set(result['selected'])&set(question['support']))/len(question['support'])
            rows.append(dict(question=question,policy=policy,recall=recall,result=result))
        metadata=[k for k,v in sources.items() if v['release']==question['release']]
        rows.append(dict(question=question,policy='metadata-only',recall=len(set(metadata)&set(question['support']))/2,result=dict(selected=metadata)))
    for policy in ['lexical','graph','metadata-only']:
        metrics[policy+'.support_recall']=sum(r['recall'] for r in rows if r['policy']==policy)/len(questions)
    Path(output,'corpus.json').write_text(json.dumps(dict(sources=sources,edges=edges,questions=questions),indent=2)+'\n')
    Path(output,'retrievals.json').write_text(json.dumps(rows,indent=2)+'\n')
    return dict(scope='Sixty purpose-built synthetic documents; graph links make qualifications reachable, while metadata-only is a strong control. This construction does not measure natural-corpus relevance or human annotation cost; seed repeats are deterministic.',metrics=metrics,seed=seed,data_seed=data_seed)
