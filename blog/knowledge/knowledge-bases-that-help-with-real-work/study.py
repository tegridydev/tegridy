"""Worked question/evidence/next-check records with explicit insufficient scope."""
import importlib.util
import json
from pathlib import Path


def run(seed,data_seed,profile,output):
    root=Path(__file__).resolve().parents[3]
    spec=importlib.util.spec_from_file_location('cedar_evidence',root/'research/knowledge/graph-memory-with-a-paper-trail/cedar.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    queries=[dict(question='What is the new release 2 timeout?',release='2',deployment='new'),dict(question='What happens during an upgrade?',release='2',deployment='upgraded'),dict(question='What is the timeout?',release=None,deployment=None),dict(question='What is the release 3 timeout?',release='3',deployment='new')]
    rows=[]
    for row in queries:
        result=module.select(release=row['release'],deployment=row['deployment'])
        next_check='Confirm the quoted source applies to this deployment.' if result['status']=='scoped' else 'Ask which release and deployment the reader means.' if result['status']=='needs-scope' else 'Acquire an applicable source before answering.'
        rows.append(dict(**row,evidence=result,next_check=next_check))
    Path(output,'worked-questions.json').write_text(json.dumps(rows,indent=2)+'\n')
    return dict(scope='Explicit Cedar fictional-document walkthrough; supported evidence, ambiguity and missing coverage remain separate. No external knowledge-base performance claim.',metrics=dict(questions=len(rows),scoped=sum(r['evidence']['status']=='scoped' for r in rows),needs_scope=sum(r['evidence']['status']=='needs-scope' for r in rows),unsupported=sum(r['evidence']['status']=='unsupported' for r in rows)),seed=seed,data_seed=data_seed)
