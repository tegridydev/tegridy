import pytest
from governance import PersistentLedger


def test_journal_replay_and_invalid_command_rolls_back(tmp_path):
    path=tmp_path/'ledger.sqlite';store=PersistentLedger(path)
    store.apply('submit',identity='v1',statement='fixture',evidence=['e'])
    store.apply('decide',version='v1',support={'e':True});store.close()
    store=PersistentLedger(path)
    assert store.replay().default=='v1'
    with pytest.raises(ValueError):store.apply('submit',identity='v1',statement='duplicate')
    assert len(store.replay().versions)==1
    store.apply('event',kind='challenged',version='v1',actor='reviewer',reason='check evidence')
    assert store.replay().default is None
    store.close()
