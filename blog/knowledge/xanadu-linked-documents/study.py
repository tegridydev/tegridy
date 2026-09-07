"""Unicode passage preservation across local versions and export/import."""
import json
from pathlib import Path
from documents import Documents


def run(seed,data_seed,profile,output):
    output=Path(output);store=Documents(output/'original.sqlite');links=[]
    count=10 if profile=='smoke' else 1000
    try:
        for i in range(count):
            text=f'αβγ document {i}: original evidence.'
            version=store.update(str(i),text)
            links.append(store.link(str(i),version,0,3))
            store.update(str(i),'A revised statement, preserving the old version.',expected_version=version)
        data=store.export();Path(output,'export.json').write_text(json.dumps(data,indent=2)+'\n')
    finally:store.close()
    restored=Documents(output/'restored.sqlite')
    try:
        restored.restore(data)
        if restored.export()!=data or any(restored.resolve(link)['text']!='αβγ' for link in links):raise ValueError('passage identity lost')
    finally:restored.close()
    return dict(scope='Local immutable Unicode passage storage and transactional round-trip, not a distributed editor or verified upstream repair.',metrics=dict(documents=count,versions=2*count,preserved_links=len(links)),seed=seed,data_seed=data_seed)
