from prepare import prepare, load
import pytest

RECIPE = dict(
    id_field="id",
    protected_fields=["id", "label"],
    trim_outer_whitespace=["text"],
    duplicate_key_policy="quarantine-conflicts",
    missing_value_policy="preserve-null",
)


def test_conflicts_and_lineage():
    rows = [
        dict(id="0017", text=" A ", label="X"),
        dict(id="0018", text="a"),
        dict(id="0018", text="b"),
        None,
    ]
    result = prepare(rows, RECIPE)
    assert result["counts"] == dict(accepted=1, quarantined=2, rejected=1, duplicates=0)
    assert result["accepted"][0]["output"] == dict(id="0017", text="A", label="X")
    assert rows[0]["text"] == " A "


def test_group_split_and_protection():
    recipe = dict(RECIPE, group_field="parent")
    rows = [dict(id=str(i), parent="same") for i in range(100)]
    assert len({e["split"] for e in prepare(rows, recipe)["accepted"]}) == 1
    with pytest.raises(ValueError):
        prepare(rows, dict(recipe, trim_outer_whitespace=["id"]))


def test_load_and_duplicate_accounting(tmp_path):
    p = tmp_path / "input.csv"
    p.write_text("id,text\n0017,hi\n0017,hi\n")
    result = prepare(load(p), RECIPE)
    assert result["accepted"][0]["input"]["id"] == "0017"
    assert result["counts"]["duplicates"] == 1
