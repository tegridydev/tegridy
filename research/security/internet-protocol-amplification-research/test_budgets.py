from budgets import simulate, UnvalidatedBytes


def test_chain_cycle_branch_and_budget():
    assert simulate({"a": ["b"], "b": ["c"], "c": []}, "a")["completed"] == 3
    cycle = {"a": ["b"], "b": ["a"]}
    assert simulate(cycle, "a")["completed"] == 2
    assert simulate(cycle, "a", budget=7, detect_cycles=False)["charged_work"] == 7
    branch = {
        "a": ["b", "c"],
        "b": ["d", "e"],
        "c": ["f", "g"],
        "d": [],
        "e": [],
        "f": [],
        "g": [],
    }
    assert simulate(branch, "a")["completed"] == 7
    result = simulate(branch, "a", budget=3)
    assert (
        result["charged_work"] == result["completed"] == 3 and result["rejected"] == 4
    )
    assert simulate(branch, "a", budget=0)["completed"] == 0


def test_byte_invariant_counts_total_before_write():
    account = UnvalidatedBytes()
    assert not account.send(1)
    account.receive(100)
    assert account.send(299) and not account.send(2) and account.send(1)
    account.receive(1)
    assert account.send(3) and account.sent == 3 * account.received
