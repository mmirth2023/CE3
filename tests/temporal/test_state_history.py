from datetime import datetime, timezone

import pytest

from ce3.temporal.state_history import StateHistory
from ce3.temporal.state_version import StateVersion


def make_version(
    version_id: str,
    minute: int,
    status: str,
) -> StateVersion:
    return StateVersion(
        id=version_id,
        state_time=datetime(
            2026,
            10,
            2,
            15,
            minute,
            0,
            tzinfo=timezone.utc,
        ),
        state={
            "system": {
                "status": status,
            },
        },
        confidence=0.8,
    )


def test_state_history_preserves_chronological_order():
    history = StateHistory()

    v3 = make_version("STATE-003", 30, "critical")
    v1 = make_version("STATE-001", 10, "normal")
    v2 = make_version("STATE-002", 20, "degraded")

    history.add(v3)
    history.add(v1)
    history.add(v2)

    assert [version.id for version in history.all()] == [
        "STATE-001",
        "STATE-002",
        "STATE-003",
    ]


def test_state_history_rejects_duplicate_ids():
    history = StateHistory()

    version = make_version("STATE-001", 10, "normal")

    history.add(version)

    with pytest.raises(ValueError):
        history.add(version)


def test_state_history_get_returns_version():
    history = StateHistory()

    version = make_version("STATE-001", 10, "normal")

    history.add(version)

    assert history.get("STATE-001") is version


def test_state_history_between_is_inclusive():
    history = StateHistory()

    v1 = make_version("STATE-001", 10, "normal")
    v2 = make_version("STATE-002", 20, "degraded")
    v3 = make_version("STATE-003", 30, "critical")

    history.add(v1)
    history.add(v2)
    history.add(v3)

    start = datetime(
        2026,
        10,
        2,
        15,
        10,
        0,
        tzinfo=timezone.utc,
    )

    end = datetime(
        2026,
        10,
        2,
        15,
        20,
        0,
        tzinfo=timezone.utc,
    )

    assert [
        version.id
        for version in history.between(start, end)
    ] == [
        "STATE-001",
        "STATE-002",
    ]


def test_state_history_as_of_excludes_future_state():
    history = StateHistory()

    v1 = make_version("STATE-001", 10, "normal")
    v2 = make_version("STATE-002", 20, "degraded")
    v3 = make_version("STATE-003", 30, "critical")

    history.add(v1)
    history.add(v2)
    history.add(v3)

    timestamp = datetime(
        2026,
        10,
        2,
        15,
        20,
        0,
        tzinfo=timezone.utc,
    )

    assert [
        version.id
        for version in history.as_of(timestamp)
    ] == [
        "STATE-001",
        "STATE-002",
    ]


def test_state_history_latest_returns_latest_version():
    history = StateHistory()

    history.add(make_version("STATE-001", 10, "normal"))
    history.add(make_version("STATE-002", 20, "degraded"))
    history.add(make_version("STATE-003", 30, "critical"))

    latest = history.latest()

    assert latest is not None
    assert latest.id == "STATE-003"


def test_state_history_latest_as_of_respects_timestamp():
    history = StateHistory()

    history.add(make_version("STATE-001", 10, "normal"))
    history.add(make_version("STATE-002", 20, "degraded"))
    history.add(make_version("STATE-003", 30, "critical"))

    timestamp = datetime(
        2026,
        10,
        2,
        15,
        20,
        0,
        tzinfo=timezone.utc,
    )

    latest = history.latest(timestamp)

    assert latest is not None
    assert latest.id == "STATE-002"


def test_state_history_empty_queries_are_safe():
    history = StateHistory()

    timestamp = datetime(
        2026,
        10,
        2,
        15,
        20,
        0,
        tzinfo=timezone.utc,
    )

    assert history.all() == []
    assert history.as_of(timestamp) == []
    assert history.between(timestamp, timestamp) == []
    assert history.latest() is None
    assert history.latest(timestamp) is None
    assert len(history) == 0