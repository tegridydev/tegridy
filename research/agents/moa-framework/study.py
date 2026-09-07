"""100 bounded synthetic stream requests with retained fault and cache traces."""
import asyncio
import json
from pathlib import Path
from orchestrator import run as orchestrate,Cache


async def provider(kind):
    yield 'first'
    if kind=='empty':yield ''
    if kind=='failure':raise RuntimeError('injected provider failure')
    if kind=='timeout':await asyncio.sleep(6)
    yield ' second'


async def experiment(count):
    records=[]
    for index in range(count):
        kind=['ordinary','empty','failure','timeout'][index%4]
        # A short declared timeout-injection deadline keeps CPU validation bounded;
        # ordinary completion cases retain the article's five-second deadline.
        deadline=.01 if kind=='timeout' else 5.
        result=await orchestrate({kind:provider(kind)},deadline=deadline)
        expected='completed' if kind in {'ordinary','empty'} else 'failed'
        if result['streams'][kind]['status']!=expected:raise ValueError('unexpected terminal status')
        if expected=='completed' and result['streams'][kind]['text']!='first second':raise ValueError('lost or changed chunks')
        if expected=='failed' and result['aggregate']:raise ValueError('failed output entered aggregate')
        records.append(dict(request=index,kind=kind,deadline_seconds=deadline,result=result))
    return records


def run(seed,data_seed,profile,output):
    rows=asyncio.run(experiment(8 if profile=='smoke' else 100))
    cache=Cache(Path(output)/'cache.sqlite')
    try:
        for row in rows:
            request=dict(id=row['request'],provider=row['kind'],model='fake-v1',prompt='bounded replay')
            cache.put(request,row,now=100,ttl=10)
            if cache.get(request,109)!=row or cache.get(request,110) is not None:raise ValueError('cache expiration failed')
    finally:cache.close()
    Path(output,'traces.json').write_text(json.dumps(rows,indent=2)+'\n')
    return dict(scope='Deterministic provider fixtures, explicit fault deadlines and persistent cache expiry; no live SDK, token-spend or answer-quality claim. Seed repeats are identical protocol replays, not independent task families.',metrics=dict(requests=len(rows),completed=sum(r['kind'] in {'ordinary','empty'} for r in rows),failed=sum(r['kind'] in {'failure','timeout'} for r in rows)),seed=seed,data_seed=data_seed)
