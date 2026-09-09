from app import Simulation, fake, create_app


def test_restart_context_and_cancel(tmp_path):
    path = tmp_path / "sim.sqlite"
    s = Simulation(path)
    event = s.post("workshop", "test")
    s.step(fake)
    s.close()
    s = Simulation(path)
    s.recover()
    assert (
        s.db.execute("SELECT COUNT(*) FROM tasks WHERE status='completed'").fetchone()[
            0
        ]
        == 1
    )
    assert s.db.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 2
    s.cancel(event, "ben")
    s.step(fake)
    assert (
        s.db.execute(
            "SELECT status FROM tasks WHERE event=? AND persona='ben'", (event,)
        ).fetchone()[0]
        == "cancelled"
    )
    assert all(
        row["channel"] == "workshop" for row in s.db.execute("SELECT * FROM messages")
    )
    s.close()


def test_late_result_does_not_commit(tmp_path):
    s = Simulation(tmp_path / "sim.sqlite")
    event = s.post("workshop", "test")

    def cancelled(persona, context):
        s.cancel(event, persona)
        return "too late"

    s.step(cancelled)
    assert s.db.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 1
    s.close()


def test_web_escapes_and_rejects_foreign_origin(tmp_path):
    app = create_app(tmp_path / "web.sqlite")
    client = app.test_client()
    assert (
        client.post(
            "/", data=dict(text="<script>bad()</script>", channel="lounge")
        ).status_code
        == 302
    )
    page = client.get("/").text
    assert "&lt;script&gt;" in page and "<script>bad" not in page
    assert (
        client.post(
            "/", headers={"Origin": "https://example.com"}, data={"text": "no"}
        ).status_code
        == 403
    )


def test_exception_details_are_not_returned(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise ValueError("private/database/path secret")
    monkeypatch.setattr(Simulation, "post", fail)
    client = create_app(tmp_path / "error.sqlite").test_client()
    response = client.post("/", data={"text": "hello"})
    assert response.status_code == 400
    assert "private/database/path" not in response.text
    assert "Check your input" in response.text
