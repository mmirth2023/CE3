from datetime import datetime, timezone

import pytest

from ce3.temporal.state_version import StateVersion


def test_state_version_preserves_state_and_provenance():
    state_time = datetime(
        2026, 10, 2, 15, 0, 17,
        tzinfo=timezone.utc,
    )

    version = StateVersion(
        id="STATE-001",
        state_time=state_time,
        state={
            "facility_x": {
                "status": "degraded",
            },
        },
        source_event_ids=["EV-001"],
        source_observation_ids=[
            "OBS-001",
            "OBS-002",
        ],
        confidence=0.87,
    )

    assert version.id == "STATE-001"
    assert version.state_time == state_time
    assert version.state["facility_x"]["status"] == "degraded"
    assert version.source_event_ids == ["EV-001"]
    assert version.source_observation_ids == [
        "OBS-001",
        "OBS-002",
    ]
    assert version.confidence == 0.87


def test_state_version_defaults_are_safe():
    state_time = datetime(
        2026, 10, 2, 15, 0, 17,
        tzinfo=timezone.utc,
    )

    version = StateVersion(
        id="STATE-002",
        state_time=state_time,
        confidence=0.0,
    )

    assert version.state == {}
    assert version.source_event_ids == []
    assert version.source_observation_ids == []
    assert version.metadata == {}


def test_state_version_rejects_invalid_confidence():
    state_time = datetime(
        2026, 10, 2, 15, 0, 17,
        tzinfo=timezone.utc,
    )

    with pytest.raises(ValueError):
        StateVersion(
            id="STATE-003",
            state_time=state_time,
            confidence=1.5,
        )