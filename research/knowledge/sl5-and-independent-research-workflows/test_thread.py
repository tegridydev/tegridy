from thread import fixture, Forecast


def test_nested_attribution_and_original_time():
    thread = fixture()
    answer = thread.attribution("m2", 0, 16)
    assert (
        answer["author"] == "author-0"
        and answer["original_timestamp"] == 0
        and answer["corrected_timestamp"] == -1
    )
    for identity in ["m0", "m1", "m2", "m5", "m9"]:
        answer = thread.attribution(identity, 0, 16)
        assert answer["text"] == "The value is 10."


def test_ambiguous_forecasts_do_not_gain_hindsight():
    thread = fixture()
    for identity in ["m3", "m4"]:
        forecast = Forecast(
            identity,
            0,
            len(thread.messages[identity].text),
            5,
            None,
            None,
            "no measurable target",
        )
        assert thread.resolve(forecast, 10, "anything") == "unresolvable"
