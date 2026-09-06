import pytest
from governance import Ledger, histories


def test_history_and_missing_evidence_defer():
    ledger = Ledger()
    ledger.submit("v1", "claim", ("missing",))
    decision = ledger.decide("v1", {})
    assert ledger.default is None and ledger.events[-1].kind == "deferred"
    ledger.event("appealed", "v1", "author", "missing source supplied", decision)
    ledger.decide("v1", {"missing": True})
    assert ledger.default == "v1"
    ledger.event("challenged", "v1", "reviewer", "applicability unclear")
    assert ledger.default is None
    with pytest.raises(ValueError):
        ledger.submit("v1", "overwrite")
    assert len(histories()) == 40
