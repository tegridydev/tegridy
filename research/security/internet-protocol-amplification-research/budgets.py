"""Finite job graphs and byte-accounting invariants; no sockets or protocol traffic."""

from collections import deque
import json


def simulate(graph, root, budget=100, max_depth=10, detect_cycles=True):
    if (
        type(budget) is not int
        or budget < 0
        or type(max_depth) is not int
        or max_depth < 0
    ):
        raise ValueError("nonnegative integer limits required")
    if root not in graph or any(
        child not in graph for children in graph.values() for child in children
    ):
        raise ValueError("graph contains missing nodes")
    queued = deque()
    seen = set()
    ledger = []
    charged = 0
    peak = 0

    def admit(node, parent, depth):
        nonlocal charged, peak
        reason = (
            "depth"
            if depth > max_depth
            else "already-visited"
            if detect_cycles and node in seen
            else "work-budget"
            if charged >= budget
            else None
        )
        identity = len(ledger)
        ledger.append(
            dict(
                job=identity,
                node=node,
                parent=parent,
                depth=depth,
                work_units=0 if reason else 1,
                outcome="rejected" if reason else "queued",
                reason=reason,
            )
        )
        if reason:
            return
        charged += 1
        seen.add(node)
        queued.append(identity)
        peak = max(peak, len(queued))

    admit(root, None, 0)
    while queued:
        identity = queued.popleft()
        job = ledger[identity]
        job["outcome"] = "completed"
        for child in graph[job["node"]]:
            admit(child, identity, job["depth"] + 1)
    return dict(
        charged_work=charged,
        completed=sum(j["outcome"] == "completed" for j in ledger),
        rejected=sum(j["outcome"] == "rejected" for j in ledger),
        peak_queued=peak,
        ledger=ledger,
    )


class UnvalidatedBytes:
    def __init__(self):
        self.received = 0
        self.sent = 0

    def receive(self, count):
        if type(count) is not int or count < 0:
            raise ValueError("nonnegative attributable byte count required")
        self.received += count

    def send(self, count):
        if type(count) is not int or count < 0:
            raise ValueError("nonnegative byte count required")
        if self.sent + count > 3 * self.received:
            return False
        self.sent += count
        return True


if __name__ == "__main__":
    examples = {
        "chain": {"a": ["b"], "b": ["c"], "c": []},
        "cycle": {"a": ["b"], "b": ["a"]},
        "branch": {
            "a": ["b", "c"],
            "b": ["d", "e"],
            "c": ["f", "g"],
            "d": [],
            "e": [],
            "f": [],
            "g": [],
        },
    }
    print(
        json.dumps(
            {name: simulate(graph, "a", budget=5) for name, graph in examples.items()},
            indent=2,
        )
    )
