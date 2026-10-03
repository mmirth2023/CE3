from datetime import datetime, timezone

from ce3.statespace.models import (
    StateSpaceDimension,
)
from ce3.statespace.sequence import (
    StateSpaceTransitionSequence,
)
from ce3.statespace.transition import (
    StateSpaceTransitionType,
)


START = datetime(
    2026,
    10,
    3,
    10,
    0,
    0,
    tzinfo=timezone.utc,
)

END = datetime(
    2026,
    10,
    3,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


def test_sequence_stores_transition_ids():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
        ],
        transition_types=[
            StateSpaceTransitionType.RECOVERY,
            StateSpaceTransitionType.DIMENSIONAL_SHIFT,
        ],
        transition_count=2,
    )

    assert sequence.transition_ids == [
        "TRANSITION-001",
        "TRANSITION-002",
    ]


def test_sequence_stores_transition_types():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        transition_types=[
            StateSpaceTransitionType.RECOVERY,
            StateSpaceTransitionType.DETERIORATION,
        ],
        transition_count=2,
    )

    assert sequence.transition_types == [
        StateSpaceTransitionType.RECOVERY,
        StateSpaceTransitionType.DETERIORATION,
    ]


def test_transition_type_names_returns_values():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        transition_types=[
            StateSpaceTransitionType.NORMALIZATION,
            StateSpaceTransitionType.STRUCTURAL_SHIFT,
        ],
        transition_count=2,
    )

    assert sequence.transition_type_names == [
        "normalization",
        "structural_shift",
    ]


def test_sequence_stores_changed_dimensions():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        changed_dimensions=[
            StateSpaceDimension.PHYSICAL.value,
            StateSpaceDimension.ECONOMIC.value,
        ],
        transition_count=2,
    )

    assert set(
        sequence.changed_dimensions
    ) == {
        "physical",
        "economic",
    }


def test_sequence_stores_position_boundaries():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        start_position_id="POSITION-001",
        end_position_id="POSITION-003",
        transition_count=2,
    )

    assert sequence.start_position_id == (
        "POSITION-001"
    )

    assert sequence.end_position_id == (
        "POSITION-003"
    )


def test_sequence_stores_transition_count():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        transition_count=3,
    )

    assert sequence.transition_count == 3


def test_sequence_stores_cumulative_magnitude():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        cumulative_magnitude=1.7,
        transition_count=3,
    )

    assert sequence.cumulative_magnitude == 1.7


def test_sequence_stores_average_confidence():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        average_confidence=0.75,
        transition_count=2,
    )

    assert sequence.average_confidence == 0.75


def test_sequence_records_structural_shift():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.STRUCTURAL_SHIFT,
        ],
        transition_count=2,
        has_structural_shift=True,
    )

    assert sequence.has_structural_shift is True


def test_sequence_can_store_rationale():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        rationale=[
            "Physical conditions deteriorated.",
            "A structural constraint was added.",
        ],
    )

    assert sequence.rationale == [
        "Physical conditions deteriorated.",
        "A structural constraint was added.",
    ]


def test_sequence_can_store_metadata():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        metadata={
            "domain": "energy",
            "region": "test",
        },
    )

    assert sequence.metadata == {
        "domain": "energy",
        "region": "test",
    }


def test_empty_sequence_property():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
    )

    assert sequence.is_empty is True


def test_non_empty_sequence_property():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        transition_ids=[
            "TRANSITION-001",
        ],
        transition_types=[
            StateSpaceTransitionType.RECOVERY,
        ],
        transition_count=1,
    )

    assert sequence.is_empty is False


def test_sequence_accepts_none_position_boundaries():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
        start_position_id=None,
        end_position_id=None,
    )

    assert sequence.start_position_id is None
    assert sequence.end_position_id is None


def test_sequence_preserves_time_window():
    sequence = StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=START,
        end_time=END,
    )

    assert sequence.start_time == START
    assert sequence.end_time == END