import csv
from extract_contacts import Contacts


def test_spans_no_invented_owner_review_and_suppression(tmp_path):
    store = Contacts(tmp_path / "contacts.sqlite")
    text = "Zoë forwards Ada <ada@example.org> and team@example.org."
    ids = store.ingest("note", text)
    assert len(ids) == 2
    for r in store.rows():
        assert text[r["start"] : r["end"]] == r["email"] and r["relation"] is None
    store.review(ids[0], "accepted", "human", "=not a formula")
    store.review(ids[1], "accepted", "human")
    store.suppress("TEAM@example.org", "removed by owner")
    assert store.export(tmp_path / "export.csv") == 1
    with (tmp_path / "export.csv").open() as stream:
        rows = list(csv.reader(stream))
    assert rows[1][1].startswith("'=")
    assert store.ingest("copy", text) == ids
    store.close()
