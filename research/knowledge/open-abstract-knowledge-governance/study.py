"""Persistent governance replay across explicit supported/unsupported disputes."""
import json
from pathlib import Path
import random
from governance import PersistentLedger


def run(seed,data_seed,profile,output):
    rng=random.Random(seed+data_seed);cases=[]
    for index in range(8 if profile=='smoke' else 100):
        path=Path(output)/f'ledger-{index}.sqlite'
        store=PersistentLedger(path)
        support=rng.choice([True,False,None]);kind='missing' if support is None else 'supported' if support else 'unsupported'
        store.apply('submit',identity='original',statement=f'Fictional record {index}',evidence=['source-a'])
        store.apply('decide',version='original',support={'source-a':True})
        store.apply('submit',identity='correction',statement=f'Fictional corrected record {index}',evidence=['source-b'],parent='original')
        decision=store.apply('decide',version='correction',support={} if support is None else {'source-b':support})
        store.apply('event',kind='appealed',version='correction',actor='reviewer',reason='explicit replay challenge',appeal_of=decision)
        store.close();store=PersistentLedger(path)
        try:
            store.apply('decide',version='correction',support={} if support is None else {'source-b':support})
            ledger=store.replay();expected='correction' if support else 'original'
            # An accepted correction loses its default on appeal; a failed correction
            # never displaced the original accepted version.
            if ledger.default!=expected:raise ValueError('unexpected default after replay')
            cases.append(dict(id=index,family=kind,default=ledger.default,events=[vars(e) for e in ledger.events]))
        finally:store.close()
    Path(output,'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
    return dict(scope='Synthetic command-journal crash/replay with explicit support labels; no independent-source voting or human-governance advantage claim.',metrics=dict(cases=len(cases),replay_errors=0),seed=seed,data_seed=data_seed)
