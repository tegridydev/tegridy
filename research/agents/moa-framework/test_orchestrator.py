import asyncio
import pytest
from orchestrator import Stream, run, fake, cache_key


def test_empty_delta_partial_timeout_and_cache():
    result = asyncio.run(run({n: fake(n) for n in ["ordinary", "empty", "timeout"]}))
    assert (
        result["streams"]["ordinary"]["text"]
        == result["streams"]["empty"]["text"]
        == "first second"
    )
    assert result["streams"]["timeout"] == dict(
        text="first", status="failed"
    ) and result["excluded"] == ["timeout"]
    assert cache_key(dict(prompt="same", system="a")) != cache_key(
        dict(prompt="same", system="b")
    )


def test_duplicate_late_terminal_and_missing_sequence():
    stream = Stream()
    start = dict(sequence=0, kind="started", payload=None)
    stream.apply(start)
    stream.apply(start)
    stream.apply(dict(sequence=1, kind="cancelled", payload=None))
    stream.apply(dict(sequence=2, kind="completed", payload=None))
    assert stream.status == "cancelled" and len(stream.ignored) == 1
    with pytest.raises(ValueError):
        stream.apply(dict(sequence=4, kind="delta", payload="lost"))


def test_invalid_provider_delta_becomes_failed_trace_without_corrupting_sequence():
    async def invalid():
        yield None
    result = asyncio.run(run({'bad': invalid(), 'good': fake('ordinary')}))
    assert result['streams']['bad']['status'] == 'failed'
    assert result['streams']['good']['status'] == 'completed'
    assert [e['sequence'] for e in result['traces']['bad']] == [0, 1]
    stream = Stream()
    with pytest.raises(ValueError):
        stream.apply(dict(sequence=0, kind='delta', payload='invalid'))
    stream.apply(dict(sequence=0, kind='started', payload=None))
    assert stream.status == 'running'
