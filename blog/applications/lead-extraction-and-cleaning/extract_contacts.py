"""Local contact candidates with exact spans, explicit review and suppression."""

import argparse
import csv
import hashlib
import re
import sqlite3
from pathlib import Path

EMAIL = re.compile(
    r"(?<![\w.+-])([A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+)(?![\w-])"
)


def key(email):
    return email.casefold()


def safe_cell(text):
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) else text


class Contacts:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY,name TEXT,text TEXT);
        CREATE TABLE IF NOT EXISTS candidates(id TEXT PRIMARY KEY,source TEXT,start INTEGER,end INTEGER,email TEXT,status TEXT DEFAULT 'pending',reviewer TEXT,relation TEXT);
        CREATE TABLE IF NOT EXISTS suppressed(email TEXT PRIMARY KEY,reason TEXT);
        """)

    def ingest(self, name, text):
        source = hashlib.sha256(text.encode()).hexdigest()
        candidates = []
        with self.db:
            self.db.execute(
                "INSERT OR IGNORE INTO sources VALUES(?,?,?)", (source, name, text)
            )
            for match in EMAIL.finditer(text):
                email = match[1]
                if ".." in email.split("@")[0] or email.startswith("."):
                    continue
                identity = hashlib.sha256(
                    f"{source}:{match.start(1)}:{match.end(1)}".encode()
                ).hexdigest()
                self.db.execute(
                    "INSERT OR IGNORE INTO candidates(id,source,start,end,email) VALUES(?,?,?,?,?)",
                    (identity, source, match.start(1), match.end(1), email),
                )
                candidates.append(identity)
        return candidates

    def review(self, identity, status, reviewer, relation=""):
        if status not in {"accepted", "rejected"} or not reviewer.strip():
            raise ValueError("explicit disposition and reviewer required")
        with self.db:
            result = self.db.execute(
                "UPDATE candidates SET status=?,reviewer=?,relation=? WHERE id=?",
                (status, reviewer, relation, identity),
            )
            if not result.rowcount:
                raise KeyError(identity)

    def suppress(self, email, reason):
        if not reason.strip():
            raise ValueError("suppression reason required")
        with self.db:
            self.db.execute(
                "INSERT INTO suppressed VALUES(?,?) ON CONFLICT(email) DO UPDATE SET reason=excluded.reason",
                (key(email), reason),
            )

    def rows(self):
        return [
            dict(row)
            for row in self.db.execute(
                "SELECT c.*,s.name,s.text FROM candidates c JOIN sources s ON s.id=c.source ORDER BY source,start"
            )
        ]

    def export(self, path):
        suppressed = {r[0] for r in self.db.execute("SELECT email FROM suppressed")}
        rows = [
            r
            for r in self.rows()
            if r["status"] == "accepted" and key(r["email"]) not in suppressed
        ]
        with path.open("x", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["email", "relation", "source", "start", "end", "reviewer"])
            for row in rows:
                writer.writerow(
                    [
                        safe_cell(str(row[k]))
                        for k in [
                            "email",
                            "relation",
                            "source",
                            "start",
                            "end",
                            "reviewer",
                        ]
                    ]
                )
        return len(rows)

    def close(self):
        self.db.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("database")
    s = p.add_subparsers(dest="command", required=True)
    ingest = s.add_parser("ingest")
    ingest.add_argument("file", type=Path)
    review = s.add_parser("review")
    review.add_argument("id")
    review.add_argument("status", choices=["accepted", "rejected"])
    review.add_argument("reviewer")
    review.add_argument("--relation", default="")
    suppress = s.add_parser("suppress")
    suppress.add_argument("email")
    suppress.add_argument("reason")
    export = s.add_parser("export")
    export.add_argument("file", type=Path)
    s.add_parser("list")
    a = p.parse_args()
    store = Contacts(a.database)
    try:
        if a.command == "ingest":
            print(store.ingest(a.file.name, a.file.read_text()))
        elif a.command == "review":
            store.review(a.id, a.status, a.reviewer, a.relation)
        elif a.command == "suppress":
            store.suppress(a.email, a.reason)
        elif a.command == "export":
            print(store.export(a.file))
        else:
            import json

            print(json.dumps(store.rows(), indent=2))
    finally:
        store.close()
