from datetime import datetime, timedelta, timezone

from ce3.statespace.diff import StateSpaceDiff
from ce3.statespace.models import (
    StateSpaceDimension,
    StateSpacePosition,
)


BASE_TIME = datetime(
    2026,
    10,
    3,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


def make_position(
    position_id: str,
    *,
    stability: float = 0.8,
    capacity: float = 0.7,
    labels: list[str] | None = None,
    constraints: list[str] | None = None,
    dependencies: list[str] | None = None,
    shocks: list[str] | None = None,
    paths: list[str] | None = None,
    events: list[str] | None = None,
    observations: list[str] | None = None,
    confidence: float = 0.9,
    uncertainty: float = 0.1,
    metadata: dict | None = None,
) -> StateSpacePosition:
    return StateSpacePosition(
        id=position_id,
        state_time=BASE_TIME,
        dimensions={
            StateSpaceDimension.STABILITY: stability,
            StateSpaceDimension.CAPACITY: capacity,
        },
        labels=labels or [],
        active_constraints=constraints or [],
        active_dependencies=dependencies or [],
        active_shocks=shocks or [],
        propagation_path_ids=paths or [],
        source_event_ids=events or [],
        source_observation_ids=observations or [],
        confidence=confidence,
        uncertainty=uncertainty,
        metadata=metadata or {},
    )


def test_diff_between_identical_positions_has_no_changes():
    previous = make_position("POSITION-001")
    current = make_position("POSITION-002")

    diff = StateSpaceDiff.between(
        previous,
        current,
    )

    assert diff.previous_position_id == "POSITION-001"
    assert diff.current_position_id == "POSITION-002"
    assert diff.has_changes is False


def test_diff_detects_changed_dimensions():
    previous = make_position(
        "POSITION-001",
        stability=0.8,
        capacity=0.7,
    )

    current = make_position(
        "POSITION-002",
        stability=0.4,
        capacity=0.5,
    )

    diff = StateSpaceDiff.between(
        previous,
        current,
    )

    assert diff.changed_dimensions == {
        StateSpaceDimension.STABILITY: (0.8, 0.4),
        StateSpaceDimension.CAPACITY: (0.7, 0.5),
    }

    assert set(diff.changed_dimension_names) == {
        "stability",
        "capacity",
    }


def test_diff_detects_added_and_removed_labels():
    previous = make_position(
        "POSITION-001",
        labels=["stable", "connected"],
    )

    current = make_position(
        "POSITION-002",
        labels=["strained", "connected"],
    )

    diff = StateSpaceDiff.between(
        previous,
        current,
    )

    assert diff.added_labels == ["strained"]
    assert diff.removed_labels == ["stable"]


def test_diff_detects_constraint_changes():
    previous = make_position(
        "POSITION-001",
        constraints=["C-001", "C-002"],
    )

    current = make_position(
        "POSITION-002",
        constraints=["C-002", "C-003"],
    )

    diff = StateSpaceDiff.between(
        previous,
        current,
    )

    assert diff.added_constraints == ["C-003"]
    assert diff.removed_constraints == ["C-001"]


def test_diff_detects_dependency_changes():
    previous = make_position(
        "POSITION-001",
        dependencies=["D-001"],
    )

    current = make_position(
        "POSITION-002",
        dependencies=["D-001", "D-002"],
    )

    diff = StateSpaceDiff.between(
        previous,
        current,
    )

    assert diff.added_dependencies == ["D-002"]
    assert diff.removed_dependencies == []


def test_diff_detects_shock_changes():
    previous = make_position(
        "POSITION-001",
        shocks=["S-001"],
    )

    current = make_position(
        "POSITION-002",
        shocks=["S-002"],
    )

    diff = StateSpaceDiff.between(
        previous,
        current,
    )

    assert diff.added_shocks == ["S-002"]
    assert diff.removed_shocks == ["S-001"]


def test_diff_detects_propagation_path_changes():
    previous = make_position(
        "POSITION-001",
        paths=["PATH-001"],
    )

    current = make_position(
        "POSITION-002",
        paths=["PATH-001", "PATH-002"],
    )

    diff = StateSpaceDiff.between(
        previous,
        current,
    )

    assert diff.added_propagation_path_ids == [
        "PATH-002",
    ]
    assert diff.removed_propagation_path_ids == []


def test_diff_detects_provenance_changes():
    previous = make_position(
        "POSITION-001",
        events=["EV-001"],
        observations=["OBS-001"],
    )

    current = make_position(
        "POSITION-002",
        events=["EV-001", "EV-002"],
        observations=["OBS-002"],
    )

    diff = StateSpaceDiff.between(
        previous,
        current,
    )

    assert diff.added_source_event_ids == [
        "EV-002",
    ]

    assert diff.removed_source_event_ids == []

    assert diff.added_source_observation_ids == [
        "OBS-002",
    ]

    assert diff.removed_source_observation_ids == [
        "OBS-001",
    ]


def test_diff_detects_confidence_and_uncertainty_changes():
    previous = make_position(
        "POSITION-001",
        confidence=0.8,
        uncertainty=0.2,
    )

    current = make_position(
        "POSITION-002",
        confidence=0.95,
        uncertainty=0.05,
    )

    diff = StateSpaceDiff.between(
        previous,
        current,
    )

    assert diff.confidence_change == (
        0.8,
        0.95,
    )

    assert diff.uncertainty_change == (
        0.2,
        0.05,
    )


def test_diff_detects_metadata_changes():
    previous = make_position(
        "POSITION-001",
        metadata={
            "source": "initial",
            "version": 1,
        },
    )

    current = make_position(
        "POSITION-002",
        metadata={
            "source": "updated",
            "version": 2,
        },
    )

    diff = StateSpaceDiff.between(
        previous,
        current,
    )

    assert diff.metadata_changes == {
        "source": (
            "initial",
            "updated",
        ),
        "version": (
            1,
            2,
        ),
    }


def test_diff_preserves_temporal_context():
    previous = make_position("POSITION-001")
    current = make_position("POSITION-002")

    current.state_time = BASE_TIME + timedelta(
        hours=2
    )

    diff = StateSpaceDiff.between(
        previous,
        current,
    )

    assert diff.previous_state_time == BASE_TIME

    assert diff.current_state_time == (
        BASE_TIME + timedelta(hours=2)
    )


def test_diff_has_changes_when_any_structural_change_exists():
    previous = make_position("POSITION-001")

    current = make_position(
        "POSITION-002",
        labels=["strained"],
    )

    diff = StateSpaceDiff.between(
        previous,
        current,
    )

    assert diff.has_changes is True