"""Source revision receipts retain old citations without asserting entailment."""
from pathlib import Path
import json
import random
from evidence import Research


def run(seed,data_seed,profile,output):
    rng=random.Random(seed+data_seed);studies=[];historical=0
    for i in range(10 if profile=='smoke' else 100):
        study=Research(f'What changed in fictional source {i}?');old=[]
        for revision in range(rng.randrange(2,8)):
            text=f'Revision {revision}: fictional timeout {rng.randrange(100)} seconds.'
            version=study.capture('manual',text);passage=study.passage('manual',version,0,len(text))
            study.revise([(f'The source at revision {revision} states the quoted value.',[passage])])
            if old:
                if study.check(old[-1])!='historical-version':raise ValueError('old citation treated as current')
                historical+=1
            old.append(passage)
        studies.append(study.export())
    Path(output,'revision-ledgers.json').write_text(json.dumps(studies,indent=2)+'\n')
    return dict(scope='Synthetic source-version and answer-revision traces; exact citations do not establish entailment or web research quality.',metrics=dict(histories=len(studies),retained_historical_citations=historical),seed=seed,data_seed=data_seed)
