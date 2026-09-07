"""Exact quote attribution and frozen forecast interpretation in local threads."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    id: str
    author: str
    text: str
    timestamp: int
    parent: str | None = None


@dataclass(frozen=True)
class Forecast:
    message: str
    start: int
    end: int
    frozen_at: int
    deadline: int | None
    target: str | None
    ambiguity: str | None


class Thread:
    def __init__(self):
        self.messages = {}
        self.quotes = {}
        self.corrections = []

    def add(self, message):
        if message.id in self.messages or (
            message.parent is not None and message.parent not in self.messages
        ):
            raise ValueError("duplicate or missing parent")
        self.messages[message.id] = message

    def quote(self, container, start, end, target, target_start, target_end):
        a = self.messages[container]
        b = self.messages[target]
        if (
            not 0 <= start < end <= len(a.text)
            or not 0 <= target_start < target_end <= len(b.text)
            or a.text[start:end] != b.text[target_start:target_end]
        ):
            raise ValueError("quote span mismatch")
        if any(
            start < old_end and old_start < end
            for old_start, old_end, *_ in self.quotes.get(container, [])
        ):
            raise ValueError("overlapping quote annotation")
        self.quotes.setdefault(container, []).append(
            (start, end, target, target_start, target_end)
        )

    def attribution(self, identity, start, end, visited=()):
        if identity in visited:
            raise ValueError("quote cycle")
        message = self.messages[identity]
        if not 0 <= start < end <= len(message.text):
            raise ValueError("invalid passage")
        for lo, hi, target, tlo, thi in self.quotes.get(identity, []):
            if lo <= start < end <= hi:
                return self.attribution(
                    target, tlo + start - lo, tlo + end - lo, visited + (identity,)
                )
            if start < hi and lo < end:
                raise ValueError("passage mixes quoted and authored text")
        return dict(
            message=identity,
            author=message.author,
            text=message.text[start:end],
            original_timestamp=message.timestamp,
            corrected_timestamp=next(
                (
                    c["timestamp"]
                    for c in reversed(self.corrections)
                    if c["message"] == identity
                ),
                message.timestamp,
            ),
        )

    def correct_time(self, identity, timestamp, reason):
        if identity not in self.messages or not reason:
            raise ValueError("correction identity and reason required")
        self.corrections.append(
            dict(message=identity, timestamp=timestamp, reason=reason)
        )

    def resolve(self, forecast, outcome_at, value):
        self.attribution(forecast.message, forecast.start, forecast.end)
        if (
            forecast.frozen_at < self.messages[forecast.message].timestamp
            or forecast.frozen_at >= outcome_at
        ):
            raise ValueError(
                "interpretation must be frozen after message and before outcome"
            )
        if forecast.ambiguity or forecast.deadline is None or forecast.target is None:
            return "unresolvable"
        if outcome_at < forecast.deadline:
            return "not-yet-due"
        return "met" if value == forecast.target else "not-met"


def fixture():
    thread = Thread()
    for i in range(10):
        thread.add(
            Message(
                f"m{i}",
                f"author-{i}",
                (
                    "It will improve soon."
                    if i == 3
                    else "Things may change."
                    if i == 4
                    else "The value is 10."
                ),
                i,
                f"m{i - 1}" if i else None,
            )
        )
    thread.quote("m1", 0, 16, "m0", 0, 16)
    thread.quote("m2", 0, 16, "m1", 0, 16)
    thread.correct_time("m0", -1, "clock correction from source metadata")
    return thread


def export_thread(thread):
    from dataclasses import asdict
    return dict(schema=1,messages=[asdict(m) for m in thread.messages.values()],quotes=thread.quotes,corrections=thread.corrections)


def import_thread(data):
    if data.get('schema')!=1:raise ValueError('unknown thread schema')
    thread=Thread()
    for row in data['messages']:thread.add(Message(**row))
    for container,quotes in data['quotes'].items():
        for start,end,target,target_start,target_end in quotes:thread.quote(container,start,end,target,target_start,target_end)
    for row in data['corrections']:thread.correct_time(row['message'],row['timestamp'],row['reason'])
    # Resolve every annotated span now, rejecting quote cycles on import.
    for container,quotes in thread.quotes.items():
        for start,end,*_ in quotes:thread.attribution(container,start,end)
    return thread
