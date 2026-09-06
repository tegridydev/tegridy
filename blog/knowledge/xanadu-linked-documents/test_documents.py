import json
import pytest
from documents import Documents


def test_immutable_passage_and_roundtrip():
    store = Documents()
    store.update("doc", "a café note")
    identity = store.link("doc", 1, 2, 6)
    store.update("doc", "a replacement", 1)
    assert store.resolve(identity)["text"] == "café"
    with pytest.raises(ValueError):
        store.update("doc", "stale edit", 1)
    clone = Documents()
    clone.restore(json.loads(json.dumps(store.export())))
    assert (
        clone.export() == store.export()
        and clone.resolve(identity)["status"] == "resolved"
    )
    store.close()
    clone.close()


def test_missing_target_and_import_rollback():
    store = Documents()
    store.update("d", "abc")
    identity = store.link("d", 1, 0, 2)
    data = store.export()
    data["versions"] = []
    clone = Documents()
    clone.restore(data)
    assert clone.resolve(identity)["status"] == "missing-version"
    invalid = store.export()
    invalid["links"][0]["quote"] = "wrong"
    empty = Documents()
    with pytest.raises(ValueError):
        empty.restore(invalid)
    assert empty.export()["versions"] == []
    for s in [store, clone, empty]:
        s.close()
