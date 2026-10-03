from datetime import datetime, timezone

import pytest

from ce3.statespace.models import (
    StateSpaceDimension,
    StateSpacePosition,
)
from ce3.statespace.sequence import (
    StateSpaceTransitionSequence,
)
from ce3.statespace.sequence_engine import (
    StateSpaceSequenceEngine,
)
from ce3.statespace.transition import (
    StateSpaceTransition,
    StateSpaceTransitionType,
)


TIME_A = datetime(
    2026,
    10,
    3,
    10,
    0,
    0,
    tzinfo=timezone.utc,
)

TIME_B = datetime(
    2026,
    10,
    3,
    11,
    0,
    0,
    tzinfo=timezone.utc,
)

TIME_C = datetime(
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
    state_time: datetime,
    *,
    stability: float = 0.5,
    capacity: float = 0.5,
    confidence: float = 0.9,
) -> StateSpacePosition:
    return StateSpacePosition(
        id=position_id,
        state_time=state_time,
        dimensions={
            StateSpaceDimension.STABILITY: stability,
            StateSpaceDimension.CAPACITY: capacity,
        },
        confidence=confidence,
    )


def make_transition(
    transition_id: str,
    *,
    assessed_at: datetime,
    previous_position_id: str,
    current_position_id: str,
    previous_state_time: datetime,
    current_state_time: datetime,
    transition_type: StateSpaceTransitionType,
    changed_dimensions: list[str],
    magnitude: float,
    confidence: float,
) -> StateSpaceTransition:
    previous = make_position(
        previous_position_id,
        previous_state_time,
    )

    current = make_position(
        current_position_id,
        current_state_time,
    )

    from ce3.statespace.diff import StateSpaceDiff

    state_space_diff = StateSpaceDiff.between(
        previous,
        current,
    )

    return StateSpaceTransition(
        id=transition_id,
        assessed_at=assessed_at,
        previous_position_id=previous_position_id,
        current_position_id=current_position_id,
        previous_state_time=previous_state_time,
        current_state_time=current_state_time,
        transition_type=transition_type,
        changed_dimensions=changed_dimensions,
        magnitude=magnitude,
        confidence=confidence,
        state_space_diff=state_space_diff,
    )


def test_sequence_engine_builds_observed_sequence():
    transition_a = make_transition(
        "TRANSITION-001",
        assessed_at=TIME_B,
        previous_position_id="POSITION-001",
        current_position_id="POSITION-002",
        previous_state_time=TIME_A,
        current_state_time=TIME_B,
        transition_type=StateSpaceTransitionType.DETERIORATION,
        changed_dimensions=["stability"],
        magnitude=0.4,
        confidence=0.9,
    )

    transition_b = make_transition(
        "TRANSITION-002",
        assessed_at=TIME_C,
        previous_position_id="POSITION-002",
        current_position_id="POSITION-003",
        previous_state_time=TIME_B,
        current_state_time=TIME_C,
        transition_type=StateSpaceTransitionType.STRUCTURAL_SHIFT,
        changed_dimensions=["capacity"],
        magnitude=0.6,
        confidence=0.8,
    )

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-001",
        transitions=[
            transition_a,
            transition_b,
        ],
    )

    assert isinstance(
        sequence,
        StateSpaceTransitionSequence,
    )

    assert sequence.id == "SEQUENCE-001"
    assert sequence.transition_ids == [
        "TRANSITION-001",
        "TRANSITION-002",
    ]
    assert sequence.transition_types == [
        StateSpaceTransitionType.DETERIORATION,
        StateSpaceTransitionType.STRUCTURAL_SHIFT,
    ]


def test_sequence_engine_orders_transitions_deterministically():
    transition_a = make_transition(
        "TRANSITION-A",
        assessed_at=TIME_C,
        previous_position_id="POSITION-002",
        current_position_id="POSITION-003",
        previous_state_time=TIME_B,
        current_state_time=TIME_C,
        transition_type=StateSpaceTransitionType.RECOVERY,
        changed_dimensions=["capacity"],
        magnitude=0.3,
        confidence=0.8,
    )

    transition_b = make_transition(
        "TRANSITION-B",
        assessed_at=TIME_B,
        previous_position_id="POSITION-001",
        current_position_id="POSITION-002",
        previous_state_time=TIME_A,
        current_state_time=TIME_B,
        transition_type=StateSpaceTransitionType.DETERIORATION,
        changed_dimensions=["stability"],
        magnitude=0.5,
        confidence=0.9,
    )

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-002",
        transitions=[
            transition_a,
            transition_b,
        ],
    )

    assert sequence.transition_ids == [
        "TRANSITION-B",
        "TRANSITION-A",
    ]

    assert sequence.transition_types == [
        StateSpaceTransitionType.DETERIORATION,
        StateSpaceTransitionType.RECOVERY,
    ]


def test_sequence_engine_uses_transition_id_as_tiebreaker():
    transition_b = make_transition(
        "TRANSITION-B",
        assessed_at=TIME_B,
        previous_position_id="POSITION-001",
        current_position_id="POSITION-002",
        previous_state_time=TIME_A,
        current_state_time=TIME_B,
        transition_type=StateSpaceTransitionType.DETERIORATION,
        changed_dimensions=["stability"],
        magnitude=0.4,
        confidence=0.8,
    )

    transition_a = make_transition(
        "TRANSITION-A",
        assessed_at=TIME_B,
        previous_position_id="POSITION-002",
        current_position_id="POSITION-003",
        previous_state_time=TIME_B,
        current_state_time=TIME_C,
        transition_type=StateSpaceTransitionType.RECOVERY,
        changed_dimensions=["capacity"],
        magnitude=0.3,
        confidence=0.9,
    )

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-003",
        transitions=[
            transition_b,
            transition_a,
        ],
    )

    assert sequence.transition_ids == [
        "TRANSITION-A",
        "TRANSITION-B",
    ]


def test_sequence_captures_time_window():
    transition_a = make_transition(
        "TRANSITION-001",
        assessed_at=TIME_B,
        previous_position_id="POSITION-001",
        current_position_id="POSITION-002",
        previous_state_time=TIME_A,
        current_state_time=TIME_B,
        transition_type=StateSpaceTransitionType.DETERIORATION,
        changed_dimensions=["stability"],
        magnitude=0.4,
        confidence=0.9,
    )

    transition_b = make_transition(
        "TRANSITION-002",
        assessed_at=TIME_C,
        previous_position_id="POSITION-002",
        current_position_id="POSITION-003",
        previous_state_time=TIME_B,
        current_state_time=TIME_C,
        transition_type=StateSpaceTransitionType.RECOVERY,
        changed_dimensions=["capacity"],
        magnitude=0.3,
        confidence=0.8,
    )

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-004",
        transitions=[
            transition_a,
            transition_b,
        ],
    )

    assert sequence.start_time == TIME_B
    assert sequence.end_time == TIME_C


def test_sequence_captures_position_boundaries():
    transition_a = make_transition(
        "TRANSITION-001",
        assessed_at=TIME_B,
        previous_position_id="POSITION-001",
        current_position_id="POSITION-002",
        previous_state_time=TIME_A,
        current_state_time=TIME_B,
        transition_type=StateSpaceTransitionType.DETERIORATION,
        changed_dimensions=["stability"],
        magnitude=0.4,
        confidence=0.9,
    )

    transition_b = make_transition(
        "TRANSITION-002",
        assessed_at=TIME_C,
        previous_position_id="POSITION-002",
        current_position_id="POSITION-003",
        previous_state_time=TIME_B,
        current_state_time=TIME_C,
        transition_type=StateSpaceTransitionType.RECOVERY,
        changed_dimensions=["capacity"],
        magnitude=0.3,
        confidence=0.8,
    )

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-005",
        transitions=[
            transition_a,
            transition_b,
        ],
    )

    assert sequence.start_position_id == "POSITION-001"
    assert sequence.end_position_id == "POSITION-003"


def test_sequence_counts_transitions():
    transitions = [
        make_transition(
            "TRANSITION-001",
            assessed_at=TIME_A,
            previous_position_id="POSITION-001",
            current_position_id="POSITION-002",
            previous_state_time=TIME_A,
            current_state_time=TIME_B,
            transition_type=StateSpaceTransitionType.DETERIORATION,
            changed_dimensions=["stability"],
            magnitude=0.2,
            confidence=0.9,
        ),
        make_transition(
            "TRANSITION-002",
            assessed_at=TIME_B,
            previous_position_id="POSITION-002",
            current_position_id="POSITION-003",
            previous_state_time=TIME_B,
            current_state_time=TIME_C,
            transition_type=StateSpaceTransitionType.RECOVERY,
            changed_dimensions=["capacity"],
            magnitude=0.3,
            confidence=0.8,
        ),
    ]

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-006",
        transitions=transitions,
    )

    assert sequence.transition_count == 2
    assert sequence.is_empty is False


def test_sequence_calculates_cumulative_magnitude():
    transitions = [
        make_transition(
            "TRANSITION-001",
            assessed_at=TIME_B,
            previous_position_id="POSITION-001",
            current_position_id="POSITION-002",
            previous_state_time=TIME_A,
            current_state_time=TIME_B,
            transition_type=StateSpaceTransitionType.DETERIORATION,
            changed_dimensions=["stability"],
            magnitude=0.25,
            confidence=0.9,
        ),
        make_transition(
            "TRANSITION-002",
            assessed_at=TIME_C,
            previous_position_id="POSITION-002",
            current_position_id="POSITION-003",
            previous_state_time=TIME_B,
            current_state_time=TIME_C,
            transition_type=StateSpaceTransitionType.RECOVERY,
            changed_dimensions=["capacity"],
            magnitude=0.35,
            confidence=0.8,
        ),
    ]

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-007",
        transitions=transitions,
    )

    assert sequence.cumulative_magnitude == pytest.approx(
        0.60
    )


def test_sequence_calculates_average_confidence():
    transitions = [
        make_transition(
            "TRANSITION-001",
            assessed_at=TIME_B,
            previous_position_id="POSITION-001",
            current_position_id="POSITION-002",
            previous_state_time=TIME_A,
            current_state_time=TIME_B,
            transition_type=StateSpaceTransitionType.DETERIORATION,
            changed_dimensions=["stability"],
            magnitude=0.25,
            confidence=0.8,
        ),
        make_transition(
            "TRANSITION-002",
            assessed_at=TIME_C,
            previous_position_id="POSITION-002",
            current_position_id="POSITION-003",
            previous_state_time=TIME_B,
            current_state_time=TIME_C,
            transition_type=StateSpaceTransitionType.RECOVERY,
            changed_dimensions=["capacity"],
            magnitude=0.35,
            confidence=0.6,
        ),
    ]

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-008",
        transitions=transitions,
    )

    assert sequence.average_confidence == pytest.approx(
        0.7
    )


def test_sequence_detects_structural_shift():
    transition = make_transition(
        "TRANSITION-001",
        assessed_at=TIME_B,
        previous_position_id="POSITION-001",
        current_position_id="POSITION-002",
        previous_state_time=TIME_A,
        current_state_time=TIME_B,
        transition_type=StateSpaceTransitionType.STRUCTURAL_SHIFT,
        changed_dimensions=["constraint"],
        magnitude=0.8,
        confidence=0.9,
    )

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-009",
        transitions=[transition],
    )

    assert sequence.has_structural_shift is True


def test_sequence_without_structural_shift_is_false():
    transition = make_transition(
        "TRANSITION-001",
        assessed_at=TIME_B,
        previous_position_id="POSITION-001",
        current_position_id="POSITION-002",
        previous_state_time=TIME_A,
        current_state_time=TIME_B,
        transition_type=StateSpaceTransitionType.DETERIORATION,
        changed_dimensions=["stability"],
        magnitude=0.4,
        confidence=0.9,
    )

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-010",
        transitions=[transition],
    )

    assert sequence.has_structural_shift is False


def test_sequence_collects_unique_changed_dimensions():
    transitions = [
        make_transition(
            "TRANSITION-001",
            assessed_at=TIME_B,
            previous_position_id="POSITION-001",
            current_position_id="POSITION-002",
            previous_state_time=TIME_A,
            current_state_time=TIME_B,
            transition_type=StateSpaceTransitionType.DETERIORATION,
            changed_dimensions=[
                "stability",
                "capacity",
            ],
            magnitude=0.5,
            confidence=0.9,
        ),
        make_transition(
            "TRANSITION-002",
            assessed_at=TIME_C,
            previous_position_id="POSITION-002",
            current_position_id="POSITION-003",
            previous_state_time=TIME_B,
            current_state_time=TIME_C,
            transition_type=StateSpaceTransitionType.RECOVERY,
            changed_dimensions=[
                "capacity",
                "connectivity",
            ],
            magnitude=0.4,
            confidence=0.8,
        ),
    ]

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-011",
        transitions=transitions,
    )

    assert sequence.changed_dimensions == [
        "capacity",
        "connectivity",
        "stability",
    ]


def test_sequence_preserves_metadata():
    transition = make_transition(
        "TRANSITION-001",
        assessed_at=TIME_B,
        previous_position_id="POSITION-001",
        current_position_id="POSITION-002",
        previous_state_time=TIME_A,
        current_state_time=TIME_B,
        transition_type=StateSpaceTransitionType.DETERIORATION,
        changed_dimensions=["stability"],
        magnitude=0.4,
        confidence=0.9,
    )

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-012",
        transitions=[transition],
        metadata={
            "domain": "energy",
            "region": "global",
        },
    )

    assert sequence.metadata == {
        "domain": "energy",
        "region": "global",
    }


def test_sequence_builds_rationale():
    transition = make_transition(
        "TRANSITION-001",
        assessed_at=TIME_B,
        previous_position_id="POSITION-001",
        current_position_id="POSITION-002",
        previous_state_time=TIME_A,
        current_state_time=TIME_B,
        transition_type=StateSpaceTransitionType.DETERIORATION,
        changed_dimensions=["stability"],
        magnitude=0.4,
        confidence=0.9,
    )

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-013",
        transitions=[transition],
    )

    assert (
        "Observed transition sequence: "
        "deterioration."
        in sequence.rationale
    )

    assert (
        "Affected dimensions: stability."
        in sequence.rationale
    )


def test_sequence_rationale_identifies_structural_shift():
    transition = make_transition(
        "TRANSITION-001",
        assessed_at=TIME_B,
        previous_position_id="POSITION-001",
        current_position_id="POSITION-002",
        previous_state_time=TIME_A,
        current_state_time=TIME_B,
        transition_type=StateSpaceTransitionType.STRUCTURAL_SHIFT,
        changed_dimensions=["constraint"],
        magnitude=0.8,
        confidence=0.9,
    )

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-014",
        transitions=[transition],
    )

    assert (
        "The observed sequence includes a structural shift."
        in sequence.rationale
    )


def test_sequence_rejects_empty_transition_list():
    engine = StateSpaceSequenceEngine()

    with pytest.raises(
        ValueError,
        match="At least one transition is required",
    ):
        engine.build(
            sequence_id="SEQUENCE-015",
            transitions=[],
        )

def test_sequence_preserves_per_transition_dimensions():
    transition_a = make_transition(
        "TRANSITION-001",
        assessed_at=TIME_B,
        previous_position_id="POSITION-001",
        current_position_id="POSITION-002",
        previous_state_time=TIME_A,
        current_state_time=TIME_B,
        transition_type=StateSpaceTransitionType.DETERIORATION,
        changed_dimensions=[
            "stability",
            "capacity",
        ],
        magnitude=0.4,
        confidence=0.9,
    )

    transition_b = make_transition(
        "TRANSITION-002",
        assessed_at=TIME_C,
        previous_position_id="POSITION-002",
        current_position_id="POSITION-003",
        previous_state_time=TIME_B,
        current_state_time=TIME_C,
        transition_type=StateSpaceTransitionType.RECOVERY,
        changed_dimensions=[
            "stability",
        ],
        magnitude=0.3,
        confidence=0.8,
    )

    engine = StateSpaceSequenceEngine()

    sequence = engine.build(
        sequence_id="SEQUENCE-016",
        transitions=[
            transition_a,
            transition_b,
        ],
    )

    assert sequence.transition_dimensions == [
        [
            "stability",
            "capacity",
        ],
        [
            "stability",
        ],
    ]