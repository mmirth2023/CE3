from datetime import datetime, timezone

from ce3.system.diff import GlobalSystemStateDiff
from ce3.system.models import GlobalSystemState


def make_state(
    state_id: str,
    physical: dict | None = None,
    market: dict | None = None,
    relationships: dict | None = None,
) -> GlobalSystemState:
    return GlobalSystemState(
        id=state_id,
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        physical=physical or {},
        market=market or {},
        relationships=relationships or {},
        confidence=0.9,
    )


def test_global_system_state_diff_detects_no_change():
    state = make_state(
        "STATE-001",
        physical={
            "production": {
                "capacity": 500_000,
            },
        },
    )

    diff = GlobalSystemStateDiff.between(
        state,
        state,
    )

    assert diff.changed is False
    assert diff.changes == []


def test_global_system_state_diff_detects_modified_value():
    previous = make_state(
        "STATE-001",
        physical={
            "production": {
                "capacity": 500_000,
            },
        },
    )

    current = make_state(
        "STATE-002",
        physical={
            "production": {
                "capacity": 350_000,
            },
        },
    )

    diff = GlobalSystemStateDiff.between(
        previous,
        current,
    )

    assert diff.changed is True
    assert any(
        change.path == "physical.production.capacity"
        and change.previous_value == 500_000
        and change.new_value == 350_000
        for change in diff.changes
    )


def test_global_system_state_diff_detects_added_dimension():
    previous = make_state(
        "STATE-001",
    )

    current = make_state(
        "STATE-002",
        market={
            "brent": {
                "price": 91.5,
            },
        },
    )

    diff = GlobalSystemStateDiff.between(
        previous,
        current,
    )

    assert diff.changed is True
    assert any(
        change.path == "market.brent"
        and change.change_type == "added"
        for change in diff.changes
    )


def test_global_system_state_diff_detects_removed_dimension():
    previous = make_state(
        "STATE-001",
        market={
            "brent": {
                "price": 91.5,
            },
        },
    )

    current = make_state(
        "STATE-002",
    )

    diff = GlobalSystemStateDiff.between(
        previous,
        current,
    )

    assert diff.changed is True
    assert any(
        change.path == "market.brent"
        and change.change_type == "removed"
        for change in diff.changes
    )


def test_global_system_state_diff_detects_relationship_changes():
    previous = make_state(
        "STATE-001",
        relationships={
            "REL-001": {
                "type": "owns",
                "source": "COMP-001",
                "target": "FAC-001",
            },
        },
    )

    current = make_state(
        "STATE-002",
        relationships={
            "REL-001": {
                "type": "owns",
                "source": "COMP-001",
                "target": "FAC-002",
            },
        },
    )

    diff = GlobalSystemStateDiff.between(
        previous,
        current,
    )

    assert diff.changed is True
    assert any(
        change.path
        == "relationships.REL-001.target"
        and change.previous_value == "FAC-001"
        and change.new_value == "FAC-002"
        for change in diff.changes
    )


def test_global_system_state_diff_detects_multiple_changes():
    previous = make_state(
        "STATE-001",
        physical={
            "production": {
                "capacity": 500_000,
            },
        },
        market={
            "brent": {
                "price": 82.0,
            },
        },
    )

    current = make_state(
        "STATE-002",
        physical={
            "production": {
                "capacity": 350_000,
            },
        },
        market={
            "brent": {
                "price": 91.5,
            },
        },
    )

    diff = GlobalSystemStateDiff.between(
        previous,
        current,
    )

    assert diff.changed is True
    assert len(diff.changes) >= 2