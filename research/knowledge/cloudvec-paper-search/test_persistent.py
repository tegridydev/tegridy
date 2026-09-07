import pytest
from outbox import PersistentIndex,Store


def test_restart_tombstone_and_vector_version(tmp_path):
    path=tmp_path/'index.sqlite';index=PersistentIndex(path)
    index.upsert('a',1,'first');manifest={'model':'fixture','dimension':2}
    index.attach_vector('a',1,[-1.,0.],manifest)
    assert index.search([1.,0.],manifest)[0]['score']==-1
    index.close();index=PersistentIndex(path)
    assert index.records['a']['text']=='first'
    index.upsert('a',2,None);index.upsert('a',1,'first')
    assert not index.eligible() and not index.search([1.,0.],manifest)
    with pytest.raises(ValueError):index.attach_vector('a',1,[1.,0.],manifest)
    index.close()
