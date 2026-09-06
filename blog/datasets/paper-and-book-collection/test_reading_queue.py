import sqlite3
import pytest
from reading_queue import ReadingQueue


def test_versions_reading_scope_and_restart(tmp_path):
    path = tmp_path / "queue.sqlite"
    q = ReadingQueue(path)
    q.add("work", "Same title", "Check a claim")
    q.edition("v1", "work", "1", "https://example.org/v1", "self-authored fixture")
    q.edition("v2", "work", "2", "https://example.org/v2", "self-authored fixture")
    q.read("v1", "pages 2–3", "checked the derivation")
    q.close()
    q = ReadingQueue(path)
    data = q.export()
    assert len(data["editions"]) == 2 and data["reading"][0]["edition"] == "v1"
    with pytest.raises(sqlite3.IntegrityError):
        q.read("missing", "page 1", "")
    with pytest.raises(ValueError):
        q.read("v2", "", "")
    q.close()
