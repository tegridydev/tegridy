"""Local four-person simulation with persistent tasks and explicit provider choice."""

import argparse
import json
import sqlite3
import urllib.request
import uuid
from pathlib import Path
from flask import Flask, request, redirect, render_template_string

PERSONAS = {
    "ada": ("You enjoy building small tools.", ("workshop", "lounge")),
    "ben": ("You check evidence and arithmetic.", ("workshop",)),
    "cy": ("You ask what remains uncertain.", ("workshop", "lounge")),
    "dee": ("You keep track of decisions.", ("lounge",)),
}


class Simulation:
    def __init__(self, path, max_messages=100, max_depth=3):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.max_messages = max_messages
        self.max_depth = max_depth
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY,author TEXT,channel TEXT,text TEXT,parent TEXT,depth INTEGER,ordinal INTEGER UNIQUE);
        CREATE TABLE IF NOT EXISTS tasks(event TEXT,persona TEXT,status TEXT DEFAULT 'queued',attempt TEXT,context TEXT,error TEXT,PRIMARY KEY(event,persona));
        """)

    def _message(self, author, channel, text, parent=None, depth=0):
        if (
            channel not in {"workshop", "lounge"}
            or not text.strip()
            or len(text) > 20000
        ):
            raise ValueError("invalid message")
        count = self.db.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        if count >= self.max_messages:
            raise ValueError("message budget exhausted")
        identity = str(uuid.uuid4())
        self.db.execute(
            "INSERT INTO messages VALUES(?,?,?,?,?,?,?)",
            (identity, author, channel, text, parent, depth, count),
        )
        if depth < self.max_depth:
            for persona, (_, channels) in PERSONAS.items():
                if persona != author and channel in channels:
                    self.db.execute(
                        "INSERT OR IGNORE INTO tasks(event,persona) VALUES(?,?)",
                        (identity, persona),
                    )
        return identity

    def post(self, channel, text):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            return self._message("you", channel, text)

    def cancel(self, event, persona):
        with self.db:
            self.db.execute(
                "UPDATE tasks SET status='cancelled' WHERE event=? AND persona=? AND status IN ('queued','running')",
                (event, persona),
            )

    def recover(self):
        # Explicit startup recovery only; don't call while another worker is live.
        with self.db:
            self.db.execute(
                "UPDATE tasks SET status='queued',attempt=NULL WHERE status='running'"
            )

    def step(self, provider):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            task = self.db.execute(
                "SELECT t.*,m.channel,m.depth,m.ordinal FROM tasks t JOIN messages m ON m.id=t.event WHERE t.status='queued' ORDER BY m.ordinal,t.persona LIMIT 1"
            ).fetchone()
            if task is None:
                return False
            attempt = str(uuid.uuid4())
            channels = PERSONAS[task["persona"]][1]
            context = [
                dict(row)
                for row in self.db.execute("SELECT * FROM messages ORDER BY ordinal")
                if row["channel"] in channels
            ][-20:]
            self.db.execute(
                "UPDATE tasks SET status='running',attempt=?,context=? WHERE event=? AND persona=?",
                (attempt, json.dumps(context), task["event"], task["persona"]),
            )
        try:
            reply = provider(task["persona"], context)
            if not isinstance(reply, str) or not reply.strip():
                raise ValueError("provider returned empty response")
            with self.db:
                self.db.execute("BEGIN IMMEDIATE")
                state = self.db.execute(
                    "SELECT status,attempt FROM tasks WHERE event=? AND persona=?",
                    (task["event"], task["persona"]),
                ).fetchone()
                if state["status"] != "running" or state["attempt"] != attempt:
                    return False
                self._message(
                    task["persona"],
                    task["channel"],
                    reply,
                    task["event"],
                    task["depth"] + 1,
                )
                self.db.execute(
                    "UPDATE tasks SET status='completed' WHERE event=? AND persona=?",
                    (task["event"], task["persona"]),
                )
        except Exception as error:
            with self.db:
                self.db.execute(
                    "UPDATE tasks SET status='failed',error=? WHERE event=? AND persona=? AND status='running' AND attempt=?",
                    (str(error), task["event"], task["persona"], attempt),
                )
        return True

    def close(self):
        self.db.close()


def fake(persona, context):
    return f"{persona}: I can see {len(context)} messages. Latest: {context[-1]['text'][:100]}"


def ollama(model):
    def generate(persona, context):
        payload = dict(
            model=model,
            stream=False,
            messages=[dict(role="system", content=PERSONAS[persona][0])]
            + [
                dict(
                    role="user", content=f"{m['author']} in {m['channel']}: {m['text']}"
                )
                for m in context
            ],
            options=dict(num_predict=128, temperature=0.7),
        )
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read(2_000_000))
        return data["message"]["content"]

    return generate


def create_app(path, provider=fake):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 32 * 1024

    @app.before_request
    def local_browser_only():
        from flask import abort

        if request.host.split(":")[0] not in {"127.0.0.1", "localhost"}:
            abort(403)
        origin = request.headers.get("Origin")
        if origin and origin != request.host_url.rstrip("/"):
            abort(403)

    @app.route("/", methods=["GET", "POST"])
    def index():
        simulation = Simulation(path)
        try:
            if request.method == "POST":
                if request.form.get("action") == "step":
                    simulation.step(provider)
                else:
                    simulation.post(
                        request.form.get("channel", "workshop"),
                        request.form.get("text", ""),
                    )
                return redirect("/")
            messages = [
                dict(r)
                for r in simulation.db.execute(
                    "SELECT * FROM messages ORDER BY ordinal"
                )
            ]
            tasks = [dict(r) for r in simulation.db.execute("SELECT * FROM tasks")]
            return render_template_string(
                (Path(__file__).with_name("interface.html")).read_text(),
                messages=messages,
                tasks=tasks,
            )
        except ValueError:
            app.logger.warning("BotSim rejected a request")
            return "Unable to process this request. Check your input and try again.", 400
        finally:
            simulation.close()

    return app


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--database", default="botsim.sqlite")
    p.add_argument("--ollama-model")
    a = p.parse_args()
    simulation = Simulation(a.database)
    simulation.recover()
    simulation.close()
    create_app(a.database, ollama(a.ollama_model) if a.ollama_model else fake).run(
        host="127.0.0.1", port=5050, threaded=False
    )
