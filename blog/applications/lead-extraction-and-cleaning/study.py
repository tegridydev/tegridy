"""Saved candidate/review/suppression/export workflow using fictional addresses."""
from pathlib import Path
import json
from extract_contacts import Contacts


def run(seed,data_seed,profile,output):
    output=Path(output);count=10 if profile=='smoke' else 1000;store=Contacts(output/'contacts.sqlite')
    try:
        for index in range(count):
            text=f'Fictional contact user{index}@example.invalid, source item {index}.'
            ids=store.ingest(f'fixture-{index}',text)
            if len(ids)!=1:raise ValueError('fixture extraction mismatch')
            store.review(ids[0],'accepted' if index%3 else 'rejected','scripted-fixture-review','explicit fixture label')
            if index%5==0:store.suppress(f'user{index}@example.invalid','fixture suppression')
        store.close();store=Contacts(output/'contacts.sqlite')
        exported=store.export(output/'accepted.csv')
        expected=sum(bool(i%3) and bool(i%5) for i in range(count))
        if exported!=expected:raise ValueError('review or suppression not reflected in export')
        rows=store.rows();Path(output,'candidates.json').write_text(json.dumps(rows,indent=2)+'\n')
        return dict(scope='Fictional example.invalid contact workflow; scripted labels test persistence and suppression, not real-world extraction precision or deliverability.',metrics=dict(candidates=len(rows),exported=exported,expected_exported=expected),seed=seed,data_seed=data_seed)
    finally:store.close()
