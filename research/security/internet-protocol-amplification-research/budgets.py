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


def simulate_lifetimes(jobs, capacity=16, deadline=10, work_budget=1000):
    """Discrete simulated time; one work unit per admission, no network traffic.

    A deadline is absolute from admission; additional bytes cannot extend it.
    At a deadline boundary an unfinished request expires before a new admission.
    """
    import heapq
    if any(type(v) is not int or v<1 for v in [capacity,deadline,work_budget]):
        raise ValueError('positive integer limits required')
    rows=list(jobs)
    seen=set()
    for job in rows:
        if not job.get('id') or job['id'] in seen:raise ValueError('unique nonempty job IDs required')
        seen.add(job['id'])
        if type(job['arrival']) is not int or job['arrival']<0 or (job['duration'] is not None and (type(job['duration']) is not int or job['duration']<0)):
            raise ValueError('nonnegative simulated arrival and duration required')
    active=[]; ledger=[]; work=0; peak=0
    for job in sorted(rows,key=lambda j:(j['arrival'],j['id'])):
        while active and active[0][0]<=job['arrival']:
            heapq.heappop(active)
        if work>=work_budget or len(active)>=capacity:
            ledger.append(dict(**job,status='rejected',reason='work-budget' if work>=work_budget else 'capacity',work_units=0))
            continue
        duration=job['duration']; expired=duration is None or duration>=deadline
        end=job['arrival']+(deadline if expired else duration)
        ledger.append(dict(**job,status='expired' if expired else 'completed',finished=end,work_units=1))
        work+=1
        if end>job['arrival']:heapq.heappush(active,(end,job['id']))
        peak=max(peak,len(active))
    return dict(ledger=ledger,offered=len(rows),charged_work=work,peak_active=peak,
                completed=sum(r['status']=='completed' for r in ledger),expired=sum(r['status']=='expired' for r in ledger),
                rejected=sum(r['status']=='rejected' for r in ledger),remaining_after_final_deadline=0)
