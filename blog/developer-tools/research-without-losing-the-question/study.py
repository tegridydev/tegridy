"""Reusable question card and a recorded contradicted-claim revision."""
import hashlib
import json
from pathlib import Path
from ledger import validate


def run(seed,data_seed,profile,output):
    output=Path(output);record=output/'measurement.txt';record.write_text('Fixture observation: five records were accepted and two were rejected.\n')
    data=dict(schema=1,question='Did the fixture accept every record?',evidence=[dict(id='measurement',path=record.name,sha256=hashlib.sha256(record.read_bytes()).hexdigest())],claims=[dict(id='proposal',statement='All seven records will be accepted.',status='proposed',evidence=[]),dict(id='revision',supersedes='proposal',statement='The fixture accepted five records and rejected two.',status='supported',evidence=['measurement'],reviewer='explicit-fixture-check',reason='Matches the saved count fixture.')])
    result=validate(data,output);Path(output,'ledger.json').write_text(json.dumps(data,indent=2)+'\n')
    return dict(scope='Worked question/evidence/revision example with a deliberately authored fixture, not an independently observed external experiment.',metrics=dict(claims=result['claims'],evidence=result['evidence']),seed=seed,data_seed=data_seed)
