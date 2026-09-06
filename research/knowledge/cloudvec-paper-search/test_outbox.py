import pytest
from outbox import Store, Index


def test_crash_out_of_order_delete_and_restart(tmp_path):
    path = tmp_path / "metadata.sqlite"
    store = Store(path)
    index = Index()
    old = store.write("paper", "v1")
    with pytest.raises(RuntimeError):
        store.deliver(old, index, True)
    new = store.write("paper", "v2")
    store.deliver(new, index)
    store.deliver(old, index)
    assert index.eligible()["paper"]["text"] == "v2"
    deletion = store.write("paper", None)
    store.deliver(deletion, index)
    store.deliver(new, index)
    assert index.eligible() == {}
    store.close()
    store = Store(path)
    store.replay(index)
    assert index.records == store.rebuild().records
    assert (
        store.db.execute("SELECT COUNT(*) FROM outbox WHERE ack=0").fetchone()[0] == 0
    )
    store.close()


def test_empty_and_distinct_identity():
    store = Store()
    index = Index()
    store.replay(index)
    assert index.eligible() == {}
    store.write("a", "same title")
    store.write("b", "same title")
    store.replay(index)
    assert set(index.eligible()) == {"a", "b"}
    with pytest.raises(ValueError):
        index.upsert("a", 1, "conflicting")
    store.close()
