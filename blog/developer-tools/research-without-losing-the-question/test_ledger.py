import hashlib
import pytest
from ledger import validate


def test_revision_and_changed_evidence(tmp_path):
    evidence=tmp_path/'record.txt';evidence.write_text('measured value: 4')
    data=dict(schema=1,question='What was measured?',evidence=[dict(id='r',path='record.txt',sha256=hashlib.sha256(evidence.read_bytes()).hexdigest())],claims=[dict(id='c1',statement='value is 5',status='proposed',evidence=[]),dict(id='c2',supersedes='c1',statement='value is 4',status='supported',evidence=['r'],reviewer='fixture-reviewer',reason='exact recorded value')])
    assert validate(data,tmp_path)['claims']==2
    evidence.write_text('changed')
    with pytest.raises(ValueError,match='changed'):validate(data,tmp_path)
