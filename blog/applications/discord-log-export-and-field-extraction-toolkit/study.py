"""Large saved-JSON export fixture with revisions and overlapping pages."""
from pathlib import Path
import json
from export_logs import collect


def run(seed,data_seed,profile,output):
    count=100 if profile=='smoke' else 10000
    rows=[dict(id=str(i),author_id='fixture-user',channel_id='fixture-channel',timestamp='2026-01-01T00:00:00Z',content=f'saved message {i}') for i in range(count)]
    pages=[]
    for index,start in enumerate(range(0,count,100)):
        messages=rows[max(0,start-2):start+100]
        if index==0:messages=messages+[dict(rows[0],content='edited message',edited_timestamp='2026-01-02T00:00:00Z')]
        pages.append(dict(cursor=None if index==0 else str(index),messages=messages,next_cursor=str(index+1) if start+100<count else None))
    result=collect(pages)
    if result['status']!='complete' or len(result['messages'])!=count:raise ValueError('saved export lost messages')
    Path(output,'pages.json').write_text(json.dumps(pages)+'\n');Path(output,'export.json').write_text(json.dumps(result,indent=2)+'\n')
    return dict(scope='Generated saved-JSON pages with duplicates and an edit; offline reconciliation only, no Discord connection.',metrics=dict(input_unique_messages=count,exported_messages=len(result['messages']),pages=len(pages)),seed=seed,data_seed=data_seed)
