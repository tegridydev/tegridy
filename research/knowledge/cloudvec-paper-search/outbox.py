"""Transactional metadata/outbox with a monotonic, tombstone-aware index fixture."""

import hashlib
import json
import sqlite3


class Index:
    def __init__(self):
        self.records = {}

    def upsert(self, identity, version, text):
        previous = self.records.get(identity)
        if previous is None or previous["version"] < version:
            self.records[identity] = {"version": version, "text": text}
        elif previous["version"] == version and previous["text"] != text:
            raise ValueError("same index version has different content")

    def eligible(self):
        return {k: v for k, v in self.records.items() if v["text"] is not None}


class Store:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS metadata(id TEXT PRIMARY KEY,version INTEGER NOT NULL,text TEXT);
        CREATE TABLE IF NOT EXISTS outbox(job INTEGER PRIMARY KEY,id TEXT,version INTEGER,text TEXT,hash TEXT,ack INTEGER DEFAULT 0,UNIQUE(id,version));
        """)

    def write(self, identity, text):
        if not isinstance(identity, str) or not identity:
            raise ValueError("nonempty ID required")
        if text is not None and not isinstance(text, str):
            raise ValueError("text or deletion tombstone required")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            previous = self.db.execute(
                "SELECT version FROM metadata WHERE id=?", (identity,)
            ).fetchone()
            version = previous[0] + 1 if previous else 1
            self.db.execute(
                "INSERT INTO metadata VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET version=excluded.version,text=excluded.text",
                (identity, version, text),
            )
            digest = hashlib.sha256(json.dumps(text).encode()).hexdigest()
            cursor = self.db.execute(
                "INSERT INTO outbox(id,version,text,hash) VALUES(?,?,?,?)",
                (identity, version, text, digest),
            )
            return cursor.lastrowid

    def deliver(self, job, index, crash_before_ack=False):
        row = self.db.execute(
            "SELECT id,version,text,hash FROM outbox WHERE job=?", (job,)
        ).fetchone()
        if row is None:
            raise KeyError(job)
        identity, version, text, digest = row
        if hashlib.sha256(json.dumps(text).encode()).hexdigest() != digest:
            raise ValueError("outbox payload changed")
        index.upsert(identity, version, text)
        if crash_before_ack:
            raise RuntimeError("injected crash after index write")
        with self.db:
            self.db.execute("UPDATE outbox SET ack=1 WHERE job=?", (job,))

    def replay(self, index):
        for (job,) in self.db.execute(
            "SELECT job FROM outbox WHERE ack=0 ORDER BY job"
        ).fetchall():
            self.deliver(job, index)

    def rebuild(self):
        index = Index()
        for identity, version, text in self.db.execute(
            "SELECT id,version,text FROM metadata"
        ):
            index.upsert(identity, version, text)
        return index

    def close(self):
        self.db.close()
