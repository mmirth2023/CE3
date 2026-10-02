from datetime import datetime, timezone

from ce3.temporal.state_diff import StateDiff
from ce3.temporal.state_version import StateVersion


STATE_TIME_1 = datetime(
    2026,
    10,
    2,
    15,
    0,
    0,
    tzinfo=timezone.utc,
)

STATE_TIME_2 = datetime(
    2026,
    10,
    2,
    15,
    5,
    0,
    tzinfo=timezone.utc,
)


def make_version(
    version_id: str,
    state: dict,
) -> StateVersion:
    return StateVersion(
        id=version_id,
        state_time=(
            STATE_TIME_1
            if version_id == "STATE-001"
            else STATE_TIME_2
        ),
        state=state,
        confidence=0.9,
    )


def test_identical_states_produce_no_changes():
    state = {
        "facility_A": {
            "status": "operational",
            "capacity": 500000,
        },
    }

    previous = make_version("STATE-001", state)
    current = make_version("STATE-002", state.copy())

    diff = StateDiff.between(previous, current)

    assert diff.from_state_id == "STATE-001"
    assert diff.to_state_id == "STATE-002"
    assert diff.changes == []
    assert diff.changed is False


def test_detects_modified_nested_value():
    previous = make_version(
        "STATE-001",
        {
            "facility_A": {
                "status": "operational",
                "capacity": 500000,
            },
        },
    )

    current = make_version(
        "STATE-002",
        {
            "facility_A": {
                "status": "degraded",
                "capacity": 500000,
            },
        },
    )

    diff = StateDiff.between(previous, current)

    assert diff.changed is True
    assert len(diff.changes) == 1

    change = diff.changes[0]

    assert change.path == "facility_A.status"
    assert change.change_type == "modified"
    assert change.previous_value == "operational"
    assert change.new_value == "degraded"


def test_detects_added_value():
    previous = make_version(
        "STATE-001",
        {
            "facility_A": {
                "status": "operational",
            },
        },
    )

    current = make_version(
        "STATE-002",
        {
            "facility_A": {
                "status": "operational",
                "capacity": 500000,
            },
        },
    )

    diff = StateDiff.between(previous, current)

    assert len(diff.changes) == 1

    change = diff.changes[0]

    assert change.path == "facility_A.capacity"
    assert change.change_type == "added"
    assert change.previous_value is None
    assert change.new_value == 500000


def test_detects_removed_value():
    previous = make_version(
        "STATE-001",
        {
            "facility_A": {
                "status": "operational",
                "capacity": 500000,
            },
        },
    )

    current = make_version(
        "STATE-002",
        {
            "facility_A": {
                "status": "operational",
            },
        },
    )

    diff = StateDiff.between(previous, current)

    assert len(diff.changes) == 1

    change = diff.changes[0]

    assert change.path == "facility_A.capacity"
    assert change.change_type == "removed"
    assert change.previous_value == 500000
    assert change.new_value is None


def test_detects_multiple_changes():
    previous = make_version(
        "STATE-001",
        {
            "facility_A": {
                "status": "operational",
                "capacity": 500000,
            },
            "port_B": {
                "status": "open",
            },
        },
    )

    current = make_version(
        "STATE-002",
        {
            "facility_A": {
                "status": "degraded",
                "capacity": 300000,
            },
            "port_B": {
                "status": "closed",
            },
        },
    )

    diff = StateDiff.between(previous, current)

    assert diff.changed is True
    assert len(diff.changes) == 3

    paths = {
        change.path
        for change in diff.changes
    }

    assert paths == {
        "facility_A.status",
        "facility_A.capacity",
        "port_B.status",
    }


def test_detects_list_modification():
    previous = make_version(
        "STATE-001",
        {
            "affected_entities": [
                "facility_A",
                "port_B",
            ],
        },
    )

    current = make_version(
        "STATE-002",
        {
            "affected_entities": [
                "facility_A",
                "port_B",
                "vessel_C",
            ],
        },
    )

    diff = StateDiff.between(previous, current)

    assert len(diff.changes) == 1

    change = diff.changes[0]

    assert change.path == "affected_entities"
    assert change.change_type == "modified"
    assert change.previous_value == [
        "facility_A",
        "port_B",
    ]
    assert change.new_value == [
        "facility_A",
        "port_B",
        "vessel_C",
    ]