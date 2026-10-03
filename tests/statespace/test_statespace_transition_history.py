from datetime import datetime, timezone

import pytest

from ce3.statespace.models import (
    StateSpaceDimension,
    StateSpacePosition,
)
from ce3.statespace.transition import (
    StateSpaceTransitionType,
)
from ce3.statespace.transition_engine import (
    StateSpaceTransitionEngine,
)
from ce3.statespace.transition_history import (
    StateSpaceTransitionHistory,
)


STATE_TIME_A = datetime(
    2026,
    10,
    3,
    10,
    0,
    0,
    tzinfo=timezone.utc,
)

STATE_TIME_B = datetime(
    2026,
    10,
    3,
    11,
    0,
    0,
    tzinfo=timezone.utc,
)

STATE_TIME_C = datetime(
    2026,
    10,
    3,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)

STATE_TIME_D = datetime(
    2026,
    10,
    3,
    13,
    0,
    0,
    tzinfo=timezone.utc,
)


def make_position(
    position_id: str,
    state_time: datetime,
    *,
    physical: float = 0.5,
    economic: float = 0.5,
    constraints: list[str] | None = None,
    labels: list[str] | None = None,
) -> StateSpacePosition:
    return StateSpacePosition(
        id=position_id,
        state_time=state_time,
        dimensions={
            StateSpaceDimension.PHYSICAL: physical,
            StateSpaceDimension.ECONOMIC: economic,
        },
        labels=list(labels or []),
        active_constraints=list(
            constraints or []
        ),
        confidence=0.9,
        uncertainty=0.1,
    )


def make_transition(
    transition_id: str,
    previous: StateSpacePosition,
    current: StateSpacePosition,
):
    engine = StateSpaceTransitionEngine()

    return engine.assess(
        transition_id=transition_id,
        previous=previous,
        current=current,
    )


def test_history_starts_empty():
    history = StateSpaceTransitionHistory()

    assert history.all() == []
    assert history.latest() is None
    assert history.count() == 0


def test_add_stores_transition():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.7,
    )

    transition = make_transition(
        "TRANSITION-001",
        previous,
        current,
    )

    history = StateSpaceTransitionHistory()

    stored = history.add(
        transition
    )

    assert stored is transition
    assert history.count() == 1


def test_get_returns_transition_by_id():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.7,
    )

    transition = make_transition(
        "TRANSITION-001",
        previous,
        current,
    )

    history = StateSpaceTransitionHistory()
    history.add(transition)

    assert history.get(
        "TRANSITION-001"
    ) is transition


def test_get_unknown_transition_raises():
    history = StateSpaceTransitionHistory()

    with pytest.raises(
        KeyError,
        match="Unknown transition",
    ):
        history.get(
            "TRANSITION-UNKNOWN"
        )


def test_duplicate_transition_id_is_rejected():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.7,
    )

    transition = make_transition(
        "TRANSITION-001",
        previous,
        current,
    )

    history = StateSpaceTransitionHistory()

    history.add(transition)

    with pytest.raises(
        ValueError,
        match="Transition already exists",
    ):
        history.add(transition)


def test_all_returns_chronological_order():
    position_a = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    position_b = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.7,
    )

    position_c = make_position(
        "POSITION-003",
        STATE_TIME_C,
        physical=0.8,
    )

    first = make_transition(
        "TRANSITION-001",
        position_a,
        position_b,
    )

    second = make_transition(
        "TRANSITION-002",
        position_b,
        position_c,
    )

    history = StateSpaceTransitionHistory()

    history.add(second)
    history.add(first)

    assert [
        transition.id
        for transition in history.all()
    ] == [
        "TRANSITION-001",
        "TRANSITION-002",
    ]


def test_between_is_inclusive():
    position_a = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    position_b = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.7,
    )

    position_c = make_position(
        "POSITION-003",
        STATE_TIME_C,
        physical=0.8,
    )

    first = make_transition(
        "TRANSITION-001",
        position_a,
        position_b,
    )

    second = make_transition(
        "TRANSITION-002",
        position_b,
        position_c,
    )

    history = StateSpaceTransitionHistory()

    history.add(first)
    history.add(second)

    results = history.between(
        STATE_TIME_B,
        STATE_TIME_C,
    )

    assert [
        transition.id
        for transition in results
    ] == [
        "TRANSITION-001",
        "TRANSITION-002",
    ]


def test_as_of_returns_transitions_up_to_timestamp():
    position_a = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    position_b = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.7,
    )

    position_c = make_position(
        "POSITION-003",
        STATE_TIME_C,
        physical=0.8,
    )

    first = make_transition(
        "TRANSITION-001",
        position_a,
        position_b,
    )

    second = make_transition(
        "TRANSITION-002",
        position_b,
        position_c,
    )

    history = StateSpaceTransitionHistory()

    history.add(first)
    history.add(second)

    results = history.as_of(
        STATE_TIME_B
    )

    assert [
        transition.id
        for transition in results
    ] == [
        "TRANSITION-001",
    ]


def test_latest_returns_latest_transition():
    position_a = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    position_b = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.7,
    )

    position_c = make_position(
        "POSITION-003",
        STATE_TIME_C,
        physical=0.8,
    )

    first = make_transition(
        "TRANSITION-001",
        position_a,
        position_b,
    )

    second = make_transition(
        "TRANSITION-002",
        position_b,
        position_c,
    )

    history = StateSpaceTransitionHistory()

    history.add(first)
    history.add(second)

    assert history.latest() is second


def test_by_type_filters_transitions():
    position_a = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    position_b = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.8,
    )

    position_c = make_position(
        "POSITION-003",
        STATE_TIME_C,
        physical=0.6,
    )

    recovery = make_transition(
        "TRANSITION-001",
        position_a,
        position_b,
    )

    deterioration = make_transition(
        "TRANSITION-002",
        position_b,
        position_c,
    )

    history = StateSpaceTransitionHistory()

    history.add(recovery)
    history.add(deterioration)

    results = history.by_type(
        StateSpaceTransitionType.RECOVERY
    )

    assert [
        transition.id
        for transition in results
    ] == [
        "TRANSITION-001",
    ]


def test_affecting_dimension_filters_transitions():
    position_a = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    position_b = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.8,
    )

    position_c = make_position(
        "POSITION-003",
        STATE_TIME_C,
        physical=0.8,
        economic=0.8,
    )

    first = make_transition(
        "TRANSITION-001",
        position_a,
        position_b,
    )

    second = make_transition(
        "TRANSITION-002",
        position_b,
        position_c,
    )

    history = StateSpaceTransitionHistory()

    history.add(first)
    history.add(second)

    physical_results = (
        history.affecting_dimension(
            "physical"
        )
    )

    economic_results = (
        history.affecting_dimension(
            "economic"
        )
    )

    assert [
        transition.id
        for transition in physical_results
    ] == [
        "TRANSITION-001",
    ]

    assert [
        transition.id
        for transition in economic_results
    ] == [
        "TRANSITION-002",
    ]


def test_involving_position_filters_transitions():
    position_a = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    position_b = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.7,
    )

    position_c = make_position(
        "POSITION-003",
        STATE_TIME_C,
        physical=0.8,
    )

    first = make_transition(
        "TRANSITION-001",
        position_a,
        position_b,
    )

    second = make_transition(
        "TRANSITION-002",
        position_b,
        position_c,
    )

    history = StateSpaceTransitionHistory()

    history.add(first)
    history.add(second)

    results = history.involving_position(
        "POSITION-002"
    )

    assert [
        transition.id
        for transition in results
    ] == [
        "TRANSITION-001",
        "TRANSITION-002",
    ]


def test_history_preserves_transition_object():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.8,
    )

    transition = make_transition(
        "TRANSITION-001",
        previous,
        current,
    )

    history = StateSpaceTransitionHistory()
    history.add(transition)

    stored = history.get(
        "TRANSITION-001"
    )

    assert stored.id == transition.id
    assert (
        stored.transition_type
        == transition.transition_type
    )
    assert (
        stored.state_space_diff
        == transition.state_space_diff
    )


def test_history_can_store_structural_transitions():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        constraints=[
            "CONSTRAINT-001",
        ],
    )

    transition = make_transition(
        "TRANSITION-001",
        previous,
        current,
    )

    history = StateSpaceTransitionHistory()
    history.add(transition)

    results = history.by_type(
        StateSpaceTransitionType.STRUCTURAL_SHIFT
    )

    assert len(results) == 1
    assert results[0].id == (
        "TRANSITION-001"
    )


def test_history_supports_multiple_transition_types():
    position_a = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    position_b = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.8,
    )

    position_c = make_position(
        "POSITION-003",
        STATE_TIME_C,
        physical=0.4,
    )

    position_d = make_position(
        "POSITION-004",
        STATE_TIME_D,
        physical=0.4,
        labels=[
            "normalized",
        ],
    )

    recovery = make_transition(
        "TRANSITION-001",
        position_a,
        position_b,
    )

    deterioration = make_transition(
        "TRANSITION-002",
        position_b,
        position_c,
    )

    normalization = make_transition(
        "TRANSITION-003",
        position_c,
        position_d,
    )

    history = StateSpaceTransitionHistory()

    history.add(recovery)
    history.add(deterioration)
    history.add(normalization)

    assert len(
        history.by_type(
            StateSpaceTransitionType.RECOVERY
        )
    ) == 1

    assert len(
        history.by_type(
            StateSpaceTransitionType.DETERIORATION
        )
    ) == 1

    assert len(
        history.by_type(
            StateSpaceTransitionType.NORMALIZATION
        )
    ) == 1