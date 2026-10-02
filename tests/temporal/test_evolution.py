from datetime import datetime, timezone

from ce3.temporal.evolution import StateEvolution
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
            "facility_A": {
                "status": status,
            },
        },
        confidence=0.9,
    )


def test_evolution_builds_diffs_between_consecutive_versions():
    history = StateHistory()

    history.add(
        make_version(
            "STATE-001",
            0,
            "operational",
        )
    )

    history.add(
        make_version(
            "STATE-002",
            5,
            "degraded",
        )
    )

    history.add(
        make_version(
            "STATE-003",
            10,
            "offline",
        )
    )

    evolution = StateEvolution.from_history(history)

    assert evolution.change_count == 2
    assert len(evolution.state_diffs) == 2

    assert evolution.state_diffs[0].from_state_id == "STATE-001"
    assert evolution.state_diffs[0].to_state_id == "STATE-002"

    assert evolution.state_diffs[1].from_state_id == "STATE-002"
    assert evolution.state_diffs[1].to_state_id == "STATE-003"


def test_evolution_preserves_change_details():
    history = StateHistory()

    history.add(
        make_version(
            "STATE-001",
            0,
            "operational",
        )
    )

    history.add(
        make_version(
            "STATE-002",
            5,
            "degraded",
        )
    )

    evolution = StateEvolution.from_history(history)

    diff = evolution.state_diffs[0]

    assert diff.changed is True
    assert len(diff.changes) == 1

    change = diff.changes[0]

    assert change.path == "facility_A.status"
    assert change.previous_value == "operational"
    assert change.new_value == "degraded"


def test_evolution_identifies_no_change():
    history = StateHistory()

    history.add(
        make_version(
            "STATE-001",
            0,
            "operational",
        )
    )

    history.add(
        make_version(
            "STATE-002",
            5,
            "operational",
        )
    )

    evolution = StateEvolution.from_history(history)

    assert evolution.change_count == 1
    assert evolution.changed is False
    assert evolution.state_diffs[0].changed is False


def test_evolution_handles_single_version():
    history = StateHistory()

    history.add(
        make_version(
            "STATE-001",
            0,
            "operational",
        )
    )

    evolution = StateEvolution.from_history(history)

    assert evolution.state_diffs == []
    assert evolution.change_count == 0
    assert evolution.changed is False


def test_evolution_handles_empty_history():
    history = StateHistory()

    evolution = StateEvolution.from_history(history)

    assert evolution.state_diffs == []
    assert evolution.change_count == 0
    assert evolution.changed is False