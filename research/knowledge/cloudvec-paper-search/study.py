"""Persistent index crash/replay and rebuild correctness; no encoder-quality claim."""
import json
from pathlib import Path
import random
from outbox import Store,PersistentIndex


def run(seed,data_seed,profile,output):
    output=Path(output);rng=random.Random(seed+data_seed);events=[]
    store=Store(output/'metadata.sqlite');index=PersistentIndex(output/'index.sqlite')
    count=20 if profile=='smoke' else 1000
    try:
        for step in range(count):
            identity='document-'+str(rng.randrange(50))
            text=None if step%7==0 else 'version payload '+str(step)
            job=store.write(identity,text)
            crash=step%11==0
            try:store.deliver(job,index,crash_before_ack=crash)
            except RuntimeError:
                index.close();index=PersistentIndex(output/'index.sqlite')
            if step%13==0:store.replay(index)
            events.append(dict(step=step,id=identity,text=text,job=job,injected_crash=crash))
        store.replay(index)
        expected=store.rebuild().records
        if index.records!=expected:raise ValueError('persistent index differs from authoritative state')
        for (job,) in store.db.execute('SELECT job FROM outbox ORDER BY job DESC').fetchall():store.deliver(job,index)
        if index.records!=expected:raise ValueError('stale reverse replay changed final state')
        live=index.eligible()
        for identity,row in live.items():index.attach_vector(identity,row['version'],[1.,-1.],{'model':'explicit-fixture','dimension':2})
        if live and index.search([1.,-1.],{'model':'explicit-fixture','dimension':2})[0]['score']<.999:raise ValueError('signed cosine inconsistency')
        Path(output,'events.json').write_text(json.dumps(events,indent=2)+'\n')
        return dict(scope='Persistent SQLite crash/replay/version/tombstone comparison; supplied fixture vectors only, no semantic relevance measurement.',metrics=dict(writes=count,injected_crashes=sum(e['injected_crash'] for e in events),live_documents=len(live),rebuild_equal=1,reverse_replay_equal=1),seed=seed,data_seed=data_seed)
    finally:index.close();store.close()
