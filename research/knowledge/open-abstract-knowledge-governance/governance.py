"""Immutable claim history, append-only review events and a separate reading pointer."""

from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Version:
    id: str
    statement: str
    parent: str | None
    evidence: tuple


@dataclass(frozen=True)
class Event:
    id: int
    kind: str
    version: str
    actor: str
    reason: str
    appeal_of: int | None = None


class Ledger:
    def __init__(self):
        self.versions = {}
        self.events = []
        self.default = None

    def submit(self, identity, statement, evidence=(), parent=None):
        if identity in self.versions or (
            parent is not None and parent not in self.versions
        ):
            raise ValueError("duplicate version or missing parent")
        self.versions[identity] = Version(identity, statement, parent, tuple(evidence))
        self.event("submitted", identity, "author", "new version")

    def event(self, kind, version, actor, reason, appeal_of=None):
        if version not in self.versions or not actor or not reason:
            raise ValueError("version, actor and reason required")
        if kind not in {
            "submitted",
            "challenged",
            "accepted",
            "rejected",
            "deferred",
            "appealed",
        }:
            raise ValueError("unknown event")
        if kind == "appealed" and (
            appeal_of is None
            or not 0 <= appeal_of < len(self.events)
            or self.events[appeal_of].version != version
            or self.events[appeal_of].kind not in {"accepted", "rejected", "deferred"}
        ):
            raise ValueError("appeal must identify a decision on this version")
        event = Event(len(self.events), kind, version, actor, reason, appeal_of)
        self.events.append(event)
        if kind == "accepted":
            self.default = version
        elif (
            kind in {"challenged", "rejected", "deferred", "appealed"}
            and self.default == version
        ):
            self.default = None
        return event.id

    def decide(self, version, support):
        # support contains independent fixture annotations, not model judgements.
        evidence = self.versions[version].evidence
        if not evidence or any(identity not in support for identity in evidence):
            decision = "deferred"
        elif all(support[identity] is True for identity in set(evidence)):
            decision = "accepted"
        elif any(support[identity] is False for identity in evidence):
            decision = "rejected"
        else:
            decision = "deferred"
        return self.event(
            decision,
            version,
            "equal-permission-reviewer",
            "explicit fixture support annotations",
        )


def histories():
    from dataclasses import asdict

    output = []
    for i in range(40):
        ledger = Ledger()
        ledger.submit("v1", "Fictional timeout is 30.", ("old",))
        ledger.decide("v1", {"old": True})
        ledger.submit("v2", "Corrected timeout is 10.", ("new",), "v1")
        ledger.event("challenged", "v2", "reviewer", "check the source")
        support = {} if i % 4 == 0 else {"new": False} if i % 4 == 1 else {"new": True}
        decision = ledger.decide("v2", support)
        ledger.event("appealed", "v2", "author", "request another review", decision)
        ledger.decide("v2", support)
        output.append(
            dict(
                id=i,
                split="development" if i < 20 else "held-out-fixture",
                default=ledger.default,
                events=[asdict(e) for e in ledger.events],
            )
        )
    return output


if __name__ == "__main__":
    print(json.dumps(histories(), indent=2))
