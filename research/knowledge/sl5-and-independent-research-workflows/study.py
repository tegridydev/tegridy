"""Nested quote attribution and export/import with retained source records."""
from pathlib import Path
import json
import random
from thread import Thread,Message,export_thread,import_thread


def run(seed,data_seed,profile,output):
    rng=random.Random(seed+data_seed);records=[]
    for i in range(10 if profile=='smoke' else 100):
        thread=Thread();text=f'Original fictional measurement {rng.randrange(10000)}.'
        thread.add(Message('m0','original-author',text,0))
        start=0;end=len(text);previous='m0'
        for depth in range(rng.randrange(1,8)):
            identity='m'+str(depth+1);prefix='Quoted evidence: '
            thread.add(Message(identity,'quoting-author-'+str(depth),prefix+text,depth+1,previous))
            thread.quote(identity,len(prefix),len(prefix)+len(text),previous,start,end)
            previous=identity;start=len(prefix);end=start+len(text)
        thread.correct_time('m0',-1,'fixture source clock correction')
        data=export_thread(thread);restored=import_thread(data);result=restored.attribution(previous,start,end)
        if result['author']!='original-author' or result['text']!=text or result['corrected_timestamp']!=-1:raise ValueError('nested attribution changed')
        records.append(dict(source=data,result=result))
    Path(output,'threads.json').write_text(json.dumps(records,indent=2)+'\n')
    return dict(scope='Generated nested-quote histories with exact offsets and explicit clock corrections; no semantic retrieval or human annotation-agreement claim.',metrics=dict(threads=len(records),attribution_errors=0),seed=seed,data_seed=data_seed)
