"""Typed provider streams with deterministic replay and first-terminal precedence."""

import asyncio
import hashlib
import json
from dataclasses import dataclass, field

TERMINAL = {"completed", "failed", "cancelled"}


def cache_key(request):
    return hashlib.sha256(
        json.dumps(
            dict(schema=1, request=request),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()


@dataclass
class Stream:
    text: str = ""
    status: str = "pending"
    next_sequence: int = 0
    seen: dict = field(default_factory=dict)
    ignored: list = field(default_factory=list)

    def apply(self, event):
        sequence = event["sequence"]
        if type(sequence) is not int or sequence < 0:
            raise ValueError("nonnegative integer sequence required")
        if sequence in self.seen:
            if self.seen[sequence] != event:
                raise ValueError("conflicting duplicate event")
            return
        if sequence != self.next_sequence:
            raise ValueError("out-of-order or missing event")
        if event["kind"] not in {"started", "delta", "usage"} | TERMINAL:
            raise ValueError("unknown event kind")
        kind = event["kind"]
        if self.status not in TERMINAL:
            if kind == "started" and self.status != "pending":
                raise ValueError("duplicate start")
            if kind == "delta" and (self.status != "running" or not isinstance(event.get("payload"), str)):
                raise ValueError("delta outside running stream or non-string payload")
        # Reject invalid events before consuming their sequence number.
        self.seen[sequence] = dict(event)
        self.next_sequence += 1
        if self.status in TERMINAL:
            self.ignored.append(event)
            return
        if kind == "started":
            self.status = "running"
        elif kind == "delta":
            self.text += event["payload"]
        elif kind in TERMINAL:
            self.status = kind


async def fake(kind):
    yield "first"
    if kind == "empty":
        yield ""
    if kind == "timeout":
        await asyncio.sleep(1)
    yield " second"


async def run(providers, deadline=0.05, max_attempts=3):
    if deadline <= 0 or len(providers) > max_attempts:
        raise ValueError("dispatch budget or deadline invalid")
    traces = {}
    streams = {}

    async def worker(identity, provider):
        events = []
        stream = Stream()
        traces[identity] = events
        streams[identity] = stream

        def emit(kind, payload=None):
            event = dict(
                attempt=identity, sequence=len(events), kind=kind, payload=payload
            )
            stream.apply(event)
            events.append(event)

        emit("started")
        try:
            async with asyncio.timeout(deadline):
                async for text in provider:
                    emit("delta", text)
            emit("completed")
        except TimeoutError:
            emit("failed", "deadline exceeded")
        except asyncio.CancelledError:
            emit("cancelled")
            raise
        except Exception as error:
            emit("failed", str(error))
        finally:
            await provider.aclose()

    await asyncio.gather(
        *(worker(identity, provider) for identity, provider in providers.items())
    )
    return dict(
        traces=traces,
        streams={k: dict(text=v.text, status=v.status) for k, v in streams.items()},
        aggregate="\n".join(
            f"{k}: {v.text}" for k, v in streams.items() if v.status == "completed"
        ),
        excluded=[k for k, v in streams.items() if v.status != "completed"],
    )


if __name__ == "__main__":
    print(
        json.dumps(
            asyncio.run(
                run({name: fake(name) for name in ["ordinary", "empty", "timeout"]})
            ),
            indent=2,
        )
    )


class Cache:
    """Persistent request-identity cache; expiration is explicit and testable."""
    def __init__(self,path):
        import sqlite3
        self.db=sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS cache(key TEXT PRIMARY KEY,expires REAL,value TEXT)')

    def put(self,request,value,now,ttl):
        import math
        if not math.isfinite(now) or not math.isfinite(ttl) or ttl<=0:raise ValueError('finite time and positive TTL required')
        encoded=json.dumps(value,allow_nan=False)
        with self.db:self.db.execute('INSERT INTO cache VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET expires=excluded.expires,value=excluded.value',(cache_key(request),now+ttl,encoded))

    def get(self,request,now):
        import math
        if not math.isfinite(now):raise ValueError('finite time required')
        row=self.db.execute('SELECT expires,value FROM cache WHERE key=?',(cache_key(request),)).fetchone()
        if row is None:return None
        if row[0]<=now:
            with self.db:self.db.execute('DELETE FROM cache WHERE key=?',(cache_key(request),))
            return None
        return json.loads(row[1])

    def close(self):self.db.close()
