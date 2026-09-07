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


class PersistentIndex:
    """Durable local index contract; optional supplied vectors share one manifest.

    This does not call an encoder or claim semantic relevance. Tombstones and
    versions survive process restart independently of the authoritative store.
    """
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY,version INTEGER NOT NULL,text TEXT);
        CREATE TABLE IF NOT EXISTS vectors(id TEXT PRIMARY KEY,version INTEGER NOT NULL,manifest TEXT NOT NULL,vector TEXT NOT NULL);
        ''')

    @property
    def records(self):
        return {identity:dict(version=version,text=text) for identity,version,text in self.db.execute('SELECT id,version,text FROM records')}

    def upsert(self, identity, version, text):
        if not isinstance(identity,str) or not identity or type(version) is not int or version<1 or (text is not None and not isinstance(text,str)):
            raise ValueError('valid identity, positive version and text/tombstone required')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            old=self.db.execute('SELECT version,text FROM records WHERE id=?',(identity,)).fetchone()
            if old and old[0]==version and old[1]!=text:raise ValueError('same index version has different content')
            if old is None or old[0]<version:
                self.db.execute('INSERT INTO records VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET version=excluded.version,text=excluded.text',(identity,version,text))
                self.db.execute('DELETE FROM vectors WHERE id=?',(identity,))

    def eligible(self):
        return {k:v for k,v in self.records.items() if v['text'] is not None}

    def attach_vector(self, identity, version, vector, manifest):
        import math
        if not isinstance(manifest,dict) or not manifest or not isinstance(vector,(tuple,list)) or not vector or any(type(x) not in (int,float) or not math.isfinite(x) for x in vector):
            raise ValueError('finite vector and explicit representation manifest required')
        if not math.isfinite(math.hypot(*vector)) or not math.hypot(*vector):raise ValueError('finite nonzero vector norm required')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            record=self.db.execute('SELECT version,text FROM records WHERE id=?',(identity,)).fetchone()
            if not record or record[0]!=version or record[1] is None:raise ValueError('vector must match the current live version')
            self.db.execute('INSERT INTO vectors VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET version=excluded.version,manifest=excluded.manifest,vector=excluded.vector',(identity,version,json.dumps(manifest,sort_keys=True,allow_nan=False),json.dumps(vector,allow_nan=False)))

    def search(self, query, manifest, limit=10):
        import math
        if type(limit) is not int or limit<1:raise ValueError('positive limit required')
        if not query or any(type(x) not in (int,float) or not math.isfinite(x) for x in query):raise ValueError('finite query required')
        norm=math.hypot(*query)
        if not norm or not math.isfinite(norm):raise ValueError('finite nonzero query norm required')
        expected=json.dumps(manifest,sort_keys=True,allow_nan=False)
        scores=[]
        for identity,encoded_manifest,encoded in self.db.execute('SELECT v.id,v.manifest,v.vector FROM vectors v JOIN records r ON v.id=r.id AND v.version=r.version WHERE r.text IS NOT NULL'):
            if encoded_manifest!=expected:continue
            vector=json.loads(encoded)
            if len(vector)!=len(query):raise ValueError('vector dimension differs despite matching manifest')
            score=math.fsum((x/norm)*(y/math.hypot(*vector)) for x,y in zip(query,vector))
            scores.append(dict(id=identity,score=max(-1.,min(1.,score))))
        return sorted(scores,key=lambda r:(-r['score'],r['id']))[:limit]

    def close(self):self.db.close()
