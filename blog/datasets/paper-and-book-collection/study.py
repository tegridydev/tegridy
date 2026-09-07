"""Selection/acquisition/reading state receipts over declared local fixtures."""
import json
from pathlib import Path
from reading_queue import ReadingQueue


def run(seed,data_seed,profile,output):
    output=Path(output);queue=ReadingQueue(output/'queue.sqlite');count=10 if profile=='smoke' else 100
    try:
        for index in range(count):
            queue.add(str(index),f'Fictional document {index}','fixture workflow coverage')
            local=None
            if index%2==0:
                local=output/f'{index}.txt';local.write_text(f'Locally authored fixture document {index}.\n')
            queue.edition('edition-'+str(index),str(index),'fixture-v1','https://example.invalid/'+str(index),'locally authored synthetic fixture; URL is not an acquisition source',local)
            if index%4==0:queue.read('edition-'+str(index),'first sentence','scripted fixture read marker, not an author reading claim')
        queue.close();queue=ReadingQueue(output/'queue.sqlite');result=queue.export()
        if len(result['works'])!=count or sum(e['sha256'] is not None for e in result['editions'])!=count//2:raise ValueError('queue states lost')
        Path(output,'queue.json').write_text(json.dumps(result,indent=2)+'\n')
        return dict(scope='Local synthetic selection/acquisition/read-state persistence; no automatic rights determination or claim of reading real papers.',metrics=dict(selected=count,acquired=sum(e['sha256'] is not None for e in result['editions']),reading_records=len(result['reading'])),seed=seed,data_seed=data_seed)
    finally:queue.close()
