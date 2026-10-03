from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from ce3.statespace.models import (
    StateSpaceDimension,
    StateSpacePosition,
)


STATE_TIME = datetime(
    2026,
    10,
    3,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


def make_position() -> StateSpacePosition:
    return StateSpacePosition(
        id="POSITION-001",
        state_time=STATE_TIME,
        dimensions={
            StateSpaceDimension.STABILITY: 0.7,
            StateSpaceDimension.CAPACITY: 0.5,
            StateSpaceDimension.DEPENDENCY: 0.8,
        },
        labels=[
            "strained",
            "high_dependency",
        ],
        active_constraints=[
            "CONSTRAINT-001",
        ],
        active_dependencies=[
            "DEPENDENCY-001",
        ],
        active_shocks=[
            "SHOCK-001",
        ],
        propagation_path_ids=[
            "PATH-001",
            "PATH-002",
        ],
        source_event_ids=[
            "EV-001",
        ],
        source_observation_ids=[
            "OBS-001",
        ],
        confidence=0.9,
        uncertainty=0.1,
    )


def test_state_space_position_constructs():
    position = make_position()

    assert position.id == "POSITION-001"
    assert position.state_time == STATE_TIME


def test_state_space_dimensions_are_preserved():
    position = make_position()

    assert position.dimensions == {
        StateSpaceDimension.STABILITY: 0.7,
        StateSpaceDimension.CAPACITY: 0.5,
        StateSpaceDimension.DEPENDENCY: 0.8,
    }


def test_state_space_labels_are_preserved():
    position = make_position()

    assert position.labels == [
        "strained",
        "high_dependency",
    ]


def test_state_space_constraints_dependencies_and_shocks_are_preserved():
    position = make_position()

    assert position.active_constraints == [
        "CONSTRAINT-001",
    ]

    assert position.active_dependencies == [
        "DEPENDENCY-001",
    ]

    assert position.active_shocks == [
        "SHOCK-001",
    ]


def test_state_space_propagation_paths_are_preserved():
    position = make_position()

    assert position.propagation_path_ids == [
        "PATH-001",
        "PATH-002",
    ]


def test_state_space_provenance_is_preserved():
    position = make_position()

    assert position.source_event_ids == [
        "EV-001",
    ]

    assert position.source_observation_ids == [
        "OBS-001",
    ]


def test_state_space_confidence_and_uncertainty_are_preserved():
    position = make_position()

    assert position.confidence == 0.9
    assert position.uncertainty == 0.1


@pytest.mark.parametrize(
    "field,value",
    [
        ("confidence", -0.1),
        ("confidence", 1.1),
        ("uncertainty", -0.1),
        ("uncertainty", 1.1),
    ],
)
def test_state_space_rejects_invalid_confidence_values(
    field: str,
    value: float,
):
    data = {
        "id": "POSITION-001",
        "state_time": STATE_TIME,
        field: value,
    }

    with pytest.raises(ValidationError):
        StateSpacePosition(**data)


def test_state_space_allows_empty_position():
    position = StateSpacePosition(
        id="POSITION-EMPTY",
        state_time=STATE_TIME,
    )

    assert position.dimensions == {}
    assert position.labels == []
    assert position.active_constraints == []
    assert position.active_dependencies == []
    assert position.active_shocks == []
    assert position.propagation_path_ids == []