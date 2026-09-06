from export_logs import collect


def message(i):
    return dict(
        id=str(i),
        author_id="u1",
        channel_id="c1",
        timestamp="2025-01-01T00:00:00Z",
        content=f"message {i}",
    )


def test_pagination_edits_duplicates_and_partial():
    rows = [message(i) for i in range(250)]
    pages = [
        dict(cursor=None, messages=rows[:100], next_cursor="p2"),
        dict(cursor="p2", messages=rows[100:200], next_cursor="p3"),
        dict(
            cursor="p3",
            messages=rows[200:]
            + [
                dict(
                    rows[0], content="edited", edited_timestamp="2025-01-02T00:00:00Z"
                ),
                rows[1],
            ],
            next_cursor=None,
        ),
    ]
    result = collect(pages)
    assert result["status"] == "complete" and len(result["messages"]) == 250
    assert (
        result["messages"][0]["current"]["content"] == "edited"
        and len(result["messages"][0]["revisions"]) == 2
    )
    assert collect(pages[:1])["status"] == "partial"
    pages[1]["cursor"] = "wrong"
    assert collect(pages)["status"] == "partial"


def test_conflicting_revision_and_malformed_row():
    a = message(1)
    result = collect(
        [
            dict(
                cursor=None,
                messages=[a, dict(a, content="conflict"), None],
                next_cursor=None,
            )
        ]
    )
    assert result["status"] == "partial" and len(result["errors"]) == 2
    assert result["messages"][0]["current"] == a


def test_malformed_cursor_and_edit_produce_partial_receipts():
    for page in [
        dict(cursor=[], messages=[]),
        dict(messages=[], next_cursor={}),
        dict(messages=[dict(message(1), edited_timestamp=123)]),
    ]:
        result = collect([page])
        assert result['status'] == 'partial' and result['errors']
