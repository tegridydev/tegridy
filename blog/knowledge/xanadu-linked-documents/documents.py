"""Immutable document versions and exact passage links in SQLite."""

import hashlib
import json
import sqlite3
import uuid


class Documents:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS versions(document TEXT,version INTEGER,text TEXT,hash TEXT,PRIMARY KEY(document,version));
        CREATE TABLE IF NOT EXISTS links(id TEXT PRIMARY KEY,document TEXT,version INTEGER,start INTEGER,end INTEGER,quote TEXT);
        """)

    def update(self, document, text, expected_version=0):
        if not isinstance(document, str) or not document or not isinstance(text, str):
            raise ValueError("document ID and text required")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            current = self.db.execute(
                "SELECT COALESCE(MAX(version),0) FROM versions WHERE document=?",
                (document,),
            ).fetchone()[0]
            if current != expected_version:
                raise ValueError("version conflict; reload before editing")
            version = current + 1
            self.db.execute(
                "INSERT INTO versions VALUES(?,?,?,?)",
                (document, version, text, hashlib.sha256(text.encode()).hexdigest()),
            )
            return version

    def link(self, document, version, start, end):
        row = self.db.execute(
            "SELECT text FROM versions WHERE document=? AND version=?",
            (document, version),
        ).fetchone()
        if row is None:
            raise KeyError("target version missing")
        if (
            type(start) is not int
            or type(end) is not int
            or not 0 <= start < end <= len(row["text"])
        ):
            raise ValueError("invalid Unicode character span")
        identity = str(uuid.uuid4())
        with self.db:
            self.db.execute(
                "INSERT INTO links VALUES(?,?,?,?,?,?)",
                (identity, document, version, start, end, row["text"][start:end]),
            )
        return identity

    def resolve(self, identity):
        link = self.db.execute("SELECT * FROM links WHERE id=?", (identity,)).fetchone()
        if link is None:
            raise KeyError(identity)
        version = self.db.execute(
            "SELECT text,hash FROM versions WHERE document=? AND version=?",
            (link["document"], link["version"]),
        ).fetchone()
        if version is None:
            return dict(status="missing-version", link=dict(link))
        if (
            hashlib.sha256(version["text"].encode()).hexdigest() != version["hash"]
            or version["text"][link["start"] : link["end"]] != link["quote"]
        ):
            return dict(status="integrity-failure", link=dict(link))
        return dict(status="resolved", text=link["quote"], link=dict(link))

    def export(self):
        return dict(
            schema=1,
            versions=[
                dict(r)
                for r in self.db.execute(
                    "SELECT * FROM versions ORDER BY document,version"
                )
            ],
            links=[dict(r) for r in self.db.execute("SELECT * FROM links ORDER BY id")],
        )

    def restore(self, data):
        if data.get("schema") != 1:
            raise ValueError("unsupported schema")
        with self.db:
            for row in data["versions"]:
                if hashlib.sha256(row["text"].encode()).hexdigest() != row["hash"]:
                    raise ValueError("version hash mismatch")
                self.db.execute(
                    "INSERT INTO versions VALUES(:document,:version,:text,:hash)", row
                )
            for row in data["links"]:
                if (
                    not row["id"]
                    or type(row["start"]) is not int
                    or type(row["end"]) is not int
                    or not 0 <= row["start"] < row["end"]
                ):
                    raise ValueError("invalid link")
                self.db.execute(
                    "INSERT INTO links VALUES(:id,:document,:version,:start,:end,:quote)",
                    row,
                )
                if self.resolve(row["id"])["status"] == "integrity-failure":
                    raise ValueError("link quote mismatch")

    def close(self):
        self.db.close()


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("database")
    p.add_argument("--import-file", type=Path)
    a = p.parse_args()
    store = Documents(a.database)
    try:
        if a.import_file:
            store.restore(json.loads(a.import_file.read_text()))
        print(json.dumps(store.export(), indent=2))
    finally:
        store.close()
