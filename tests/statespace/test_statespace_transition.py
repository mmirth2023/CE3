from datetime import datetime, timezone

from ce3.statespace.diff import StateSpaceDiff
from ce3.statespace.models import (
    StateSpaceDimension,
    StateSpacePosition,
)
from ce3.statespace.transition import (
    StateSpaceTransition,
    StateSpaceTransitionType,
)


STATE_TIME_A = datetime(
    2026,
    10,
    3,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)

STATE_TIME_B = datetime(
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
    physical: float,
    economic: float,
) -> StateSpacePosition:
    return StateSpacePosition(
        id=position_id,
        state_time=state_time,
        dimensions={
            StateSpaceDimension.PHYSICAL: physical,
            StateSpaceDimension.ECONOMIC: economic,
        },
        labels=["observed"],
        confidence=0.9,
        uncertainty=0.1,
    )


def make_diff() -> StateSpaceDiff:
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        0.8,
        0.8,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        0.5,
        0.6,
    )

    return StateSpaceDiff.between(
        previous,
        current,
    )


def make_transition(
    transition_type: StateSpaceTransitionType,
) -> StateSpaceTransition:
    diff = make_diff()

    return StateSpaceTransition(
        id="TRANSITION-001",
        assessed_at=STATE_TIME_B,
        previous_position_id="POSITION-001",
        current_position_id="POSITION-002",
        previous_state_time=STATE_TIME_A,
        current_state_time=STATE_TIME_B,
        transition_type=transition_type,
        changed_dimensions=[
            "physical",
            "economic",
        ],
        magnitude=0.5,
        confidence=0.9,
        state_space_diff=diff,
        rationale=[
            "Physical and economic dimensions changed."
        ],
        source_event_ids=[
            "EV-001",
        ],
        source_observation_ids=[
            "OBS-001",
        ],
    )


def test_transition_model_preserves_identity():
    transition = make_transition(
        StateSpaceTransitionType.DETERIORATION
    )

    assert transition.id == "TRANSITION-001"
    assert transition.previous_position_id == (
        "POSITION-001"
    )
    assert transition.current_position_id == (
        "POSITION-002"
    )


def test_transition_model_preserves_times():
    transition = make_transition(
        StateSpaceTransitionType.DETERIORATION
    )

    assert transition.previous_state_time == STATE_TIME_A
    assert transition.current_state_time == STATE_TIME_B
    assert transition.assessed_at == STATE_TIME_B


def test_transition_model_preserves_type():
    transition = make_transition(
        StateSpaceTransitionType.DETERIORATION
    )

    assert transition.transition_type == (
        StateSpaceTransitionType.DETERIORATION
    )


def test_transition_model_preserves_changed_dimensions():
    transition = make_transition(
        StateSpaceTransitionType.DIMENSIONAL_SHIFT
    )

    assert transition.changed_dimensions == [
        "physical",
        "economic",
    ]


def test_transition_model_preserves_magnitude():
    transition = make_transition(
        StateSpaceTransitionType.DETERIORATION
    )

    assert transition.magnitude == 0.5


def test_transition_model_preserves_confidence():
    transition = make_transition(
        StateSpaceTransitionType.DETERIORATION
    )

    assert transition.confidence == 0.9


def test_transition_model_preserves_diff():
    transition = make_transition(
        StateSpaceTransitionType.DETERIORATION
    )

    assert transition.state_space_diff.has_changes is True


def test_transition_model_preserves_rationale():
    transition = make_transition(
        StateSpaceTransitionType.DETERIORATION
    )

    assert transition.rationale == [
        "Physical and economic dimensions changed."
    ]


def test_transition_model_preserves_provenance():
    transition = make_transition(
        StateSpaceTransitionType.DETERIORATION
    )

    assert transition.source_event_ids == [
        "EV-001",
    ]

    assert transition.source_observation_ids == [
        "OBS-001",
    ]


def test_has_transition_is_true_for_real_transition():
    transition = make_transition(
        StateSpaceTransitionType.DETERIORATION
    )

    assert transition.has_transition is True


def test_has_transition_is_false_for_none():
    transition = make_transition(
        StateSpaceTransitionType.NONE
    )

    assert transition.has_transition is False


def test_is_structural_is_true_for_structural_shift():
    transition = make_transition(
        StateSpaceTransitionType.STRUCTURAL_SHIFT
    )

    assert transition.is_structural is True


def test_is_structural_is_false_for_dimensional_shift():
    transition = make_transition(
        StateSpaceTransitionType.DIMENSIONAL_SHIFT
    )

    assert transition.is_structural is False