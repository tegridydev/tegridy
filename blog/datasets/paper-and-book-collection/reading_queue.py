"""Persistent local work/edition queue; acquisition and reading remain separate."""

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


class ReadingQueue:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        PRAGMA foreign_keys=ON;
        CREATE TABLE IF NOT EXISTS works(id TEXT PRIMARY KEY,title TEXT,reason TEXT);
        CREATE TABLE IF NOT EXISTS editions(id TEXT PRIMARY KEY,work TEXT REFERENCES works(id),version TEXT,url TEXT,rights TEXT,path TEXT,sha256 TEXT,UNIQUE(work,version));
        CREATE TABLE IF NOT EXISTS reading(id INTEGER PRIMARY KEY,edition TEXT REFERENCES editions(id),scope TEXT,notes TEXT);
        """)

    def add(self, identity, title, reason):
        if not all(isinstance(v, str) and v.strip() for v in [identity, title, reason]):
            raise ValueError("work ID, title and selection reason required")
        with self.db:
            self.db.execute(
                "INSERT INTO works VALUES(?,?,?)", (identity, title, reason)
            )

    def edition(self, identity, work, version, url, rights, path=None):
        if not all(
            isinstance(v, str) and v.strip()
            for v in [identity, work, version, url, rights]
        ):
            raise ValueError("edition identity and source/rights description required")
        digest = hashlib.sha256(Path(path).read_bytes()).hexdigest() if path else None
        with self.db:
            self.db.execute(
                "INSERT INTO editions VALUES(?,?,?,?,?,?,?)",
                (
                    identity,
                    work,
                    version,
                    url,
                    rights,
                    str(Path(path).resolve()) if path else None,
                    digest,
                ),
            )

    def read(self, edition, scope, notes):
        if not scope.strip():
            raise ValueError("record the actual pages/sections read")
        with self.db:
            self.db.execute(
                "INSERT INTO reading(edition,scope,notes) VALUES(?,?,?)",
                (edition, scope, notes),
            )

    def export(self):
        return {
            table: [dict(row) for row in self.db.execute("SELECT * FROM " + table)]
            for table in ["works", "editions", "reading"]
        }

    def close(self):
        self.db.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("database")
    sub = p.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add")
    [add.add_argument(x) for x in ["id", "title", "reason"]]
    edition = sub.add_parser("edition")
    [edition.add_argument(x) for x in ["id", "work", "version", "url", "rights"]]
    edition.add_argument("--file")
    read = sub.add_parser("read")
    [read.add_argument(x) for x in ["edition", "scope", "notes"]]
    sub.add_parser("export")
    a = p.parse_args()
    q = ReadingQueue(a.database)
    try:
        if a.command == "add":
            q.add(a.id, a.title, a.reason)
        elif a.command == "edition":
            q.edition(a.id, a.work, a.version, a.url, a.rights, a.file)
        elif a.command == "read":
            q.read(a.edition, a.scope, a.notes)
        else:
            print(json.dumps(q.export(), indent=2))
    finally:
        q.close()
