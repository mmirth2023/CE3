from datetime import datetime, timezone

import pytest

from ce3.statespace.sequence import (
    StateSpaceTransitionSequence,
)
from ce3.statespace.sequence_history import (
    StateSpaceTransitionSequenceHistory,
)
from ce3.statespace.transition import (
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

TIME_D = datetime(
    2026,
    10,
    3,
    13,
    0,
    0,
    tzinfo=timezone.utc,
)


def make_sequence(
    sequence_id: str,
    *,
    start_time: datetime,
    end_time: datetime,
    transition_ids: list[str],
    transition_types: list[StateSpaceTransitionType],
    changed_dimensions: list[str],
    start_position_id: str | None = None,
    end_position_id: str | None = None,
    has_structural_shift: bool = False,
) -> StateSpaceTransitionSequence:
    return StateSpaceTransitionSequence(
        id=sequence_id,
        start_time=start_time,
        end_time=end_time,
        transition_ids=transition_ids,
        transition_types=transition_types,
        changed_dimensions=changed_dimensions,
        start_position_id=start_position_id,
        end_position_id=end_position_id,
        transition_count=len(transition_ids),
        cumulative_magnitude=0.5,
        average_confidence=0.8,
        has_structural_shift=has_structural_shift,
    )


def test_history_adds_and_gets_sequence():
    history = StateSpaceTransitionSequenceHistory()

    sequence = make_sequence(
        "SEQUENCE-001",
        start_time=TIME_A,
        end_time=TIME_B,
        transition_ids=["TRANSITION-001"],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION
        ],
        changed_dimensions=["stability"],
    )

    added = history.add(sequence)

    assert added is sequence
    assert history.get("SEQUENCE-001") is sequence
    assert history.count() == 1


def test_history_rejects_duplicate_sequence_id():
    history = StateSpaceTransitionSequenceHistory()

    sequence = make_sequence(
        "SEQUENCE-001",
        start_time=TIME_A,
        end_time=TIME_B,
        transition_ids=["TRANSITION-001"],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION
        ],
        changed_dimensions=["stability"],
    )

    history.add(sequence)

    with pytest.raises(
        ValueError,
        match="Sequence already exists: SEQUENCE-001",
    ):
        history.add(sequence)


def test_history_get_unknown_sequence_raises_key_error():
    history = StateSpaceTransitionSequenceHistory()

    with pytest.raises(
        KeyError,
        match="Unknown sequence: SEQUENCE-404",
    ):
        history.get("SEQUENCE-404")


def test_history_returns_sequences_in_chronological_order():
    history = StateSpaceTransitionSequenceHistory()

    later = make_sequence(
        "SEQUENCE-002",
        start_time=TIME_C,
        end_time=TIME_D,
        transition_ids=["TRANSITION-002"],
        transition_types=[
            StateSpaceTransitionType.RECOVERY
        ],
        changed_dimensions=["capacity"],
    )

    earlier = make_sequence(
        "SEQUENCE-001",
        start_time=TIME_A,
        end_time=TIME_B,
        transition_ids=["TRANSITION-001"],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION
        ],
        changed_dimensions=["stability"],
    )

    history.add(later)
    history.add(earlier)

    assert [
        sequence.id
        for sequence in history.all()
    ] == [
        "SEQUENCE-001",
        "SEQUENCE-002",
    ]


def test_history_between_returns_overlapping_sequences():
    history = StateSpaceTransitionSequenceHistory()

    sequence_a = make_sequence(
        "SEQUENCE-001",
        start_time=TIME_A,
        end_time=TIME_B,
        transition_ids=["TRANSITION-001"],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION
        ],
        changed_dimensions=["stability"],
    )

    sequence_b = make_sequence(
        "SEQUENCE-002",
        start_time=TIME_B,
        end_time=TIME_C,
        transition_ids=["TRANSITION-002"],
        transition_types=[
            StateSpaceTransitionType.RECOVERY
        ],
        changed_dimensions=["capacity"],
    )

    sequence_c = make_sequence(
        "SEQUENCE-003",
        start_time=TIME_C,
        end_time=TIME_D,
        transition_ids=["TRANSITION-003"],
        transition_types=[
            StateSpaceTransitionType.NORMALIZATION
        ],
        changed_dimensions=["connectivity"],
    )

    history.add(sequence_a)
    history.add(sequence_b)
    history.add(sequence_c)

    result = history.between(
        TIME_B,
        TIME_C,
    )

    assert [
        sequence.id
        for sequence in result
    ] == [
        "SEQUENCE-001",
        "SEQUENCE-002",
        "SEQUENCE-003",
    ]


def test_history_as_of_returns_completed_sequences():
    history = StateSpaceTransitionSequenceHistory()

    sequence_a = make_sequence(
        "SEQUENCE-001",
        start_time=TIME_A,
        end_time=TIME_B,
        transition_ids=["TRANSITION-001"],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION
        ],
        changed_dimensions=["stability"],
    )

    sequence_b = make_sequence(
        "SEQUENCE-002",
        start_time=TIME_B,
        end_time=TIME_C,
        transition_ids=["TRANSITION-002"],
        transition_types=[
            StateSpaceTransitionType.RECOVERY
        ],
        changed_dimensions=["capacity"],
    )

    history.add(sequence_a)
    history.add(sequence_b)

    result = history.as_of(TIME_B)

    assert [
        sequence.id
        for sequence in result
    ] == [
        "SEQUENCE-001",
    ]


def test_history_latest_returns_most_recent_sequence():
    history = StateSpaceTransitionSequenceHistory()

    sequence_a = make_sequence(
        "SEQUENCE-001",
        start_time=TIME_A,
        end_time=TIME_B,
        transition_ids=["TRANSITION-001"],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION
        ],
        changed_dimensions=["stability"],
    )

    sequence_b = make_sequence(
        "SEQUENCE-002",
        start_time=TIME_C,
        end_time=TIME_D,
        transition_ids=["TRANSITION-002"],
        transition_types=[
            StateSpaceTransitionType.RECOVERY
        ],
        changed_dimensions=["capacity"],
    )

    history.add(sequence_a)
    history.add(sequence_b)

    assert history.latest() is sequence_b


def test_history_latest_returns_none_when_empty():
    history = StateSpaceTransitionSequenceHistory()

    assert history.latest() is None


def test_history_filters_by_transition_type():
    history = StateSpaceTransitionSequenceHistory()

    deterioration = make_sequence(
        "SEQUENCE-001",
        start_time=TIME_A,
        end_time=TIME_B,
        transition_ids=["TRANSITION-001"],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION
        ],
        changed_dimensions=["stability"],
    )

    recovery = make_sequence(
        "SEQUENCE-002",
        start_time=TIME_B,
        end_time=TIME_C,
        transition_ids=["TRANSITION-002"],
        transition_types=[
            StateSpaceTransitionType.RECOVERY
        ],
        changed_dimensions=["capacity"],
    )

    mixed = make_sequence(
        "SEQUENCE-003",
        start_time=TIME_C,
        end_time=TIME_D,
        transition_ids=[
            "TRANSITION-003",
            "TRANSITION-004",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.RECOVERY,
        ],
        changed_dimensions=[
            "stability",
            "capacity",
        ],
    )

    history.add(deterioration)
    history.add(recovery)
    history.add(mixed)

    result = history.by_transition_type(
        StateSpaceTransitionType.DETERIORATION
    )

    assert [
        sequence.id
        for sequence in result
    ] == [
        "SEQUENCE-001",
        "SEQUENCE-003",
    ]


def test_history_filters_by_dimension():
    history = StateSpaceTransitionSequenceHistory()

    stability = make_sequence(
        "SEQUENCE-001",
        start_time=TIME_A,
        end_time=TIME_B,
        transition_ids=["TRANSITION-001"],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION
        ],
        changed_dimensions=["stability"],
    )

    capacity = make_sequence(
        "SEQUENCE-002",
        start_time=TIME_B,
        end_time=TIME_C,
        transition_ids=["TRANSITION-002"],
        transition_types=[
            StateSpaceTransitionType.RECOVERY
        ],
        changed_dimensions=["capacity"],
    )

    mixed = make_sequence(
        "SEQUENCE-003",
        start_time=TIME_C,
        end_time=TIME_D,
        transition_ids=[
            "TRANSITION-003",
            "TRANSITION-004",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.RECOVERY,
        ],
        changed_dimensions=[
            "stability",
            "capacity",
        ],
    )

    history.add(stability)
    history.add(capacity)
    history.add(mixed)

    result = history.affecting_dimension(
        "stability"
    )

    assert [
        sequence.id
        for sequence in result
    ] == [
        "SEQUENCE-001",
        "SEQUENCE-003",
    ]


def test_history_filters_by_position():
    history = StateSpaceTransitionSequenceHistory()

    sequence_a = make_sequence(
        "SEQUENCE-001",
        start_time=TIME_A,
        end_time=TIME_B,
        transition_ids=["TRANSITION-001"],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION
        ],
        changed_dimensions=["stability"],
        start_position_id="POSITION-001",
        end_position_id="POSITION-002",
    )

    sequence_b = make_sequence(
        "SEQUENCE-002",
        start_time=TIME_B,
        end_time=TIME_C,
        transition_ids=["TRANSITION-002"],
        transition_types=[
            StateSpaceTransitionType.RECOVERY
        ],
        changed_dimensions=["capacity"],
        start_position_id="POSITION-002",
        end_position_id="POSITION-003",
    )

    history.add(sequence_a)
    history.add(sequence_b)

    result = history.involving_position(
        "POSITION-002"
    )

    assert [
        sequence.id
        for sequence in result
    ] == [
        "SEQUENCE-001",
        "SEQUENCE-002",
    ]


def test_history_filters_by_transition_id():
    history = StateSpaceTransitionSequenceHistory()

    sequence_a = make_sequence(
        "SEQUENCE-001",
        start_time=TIME_A,
        end_time=TIME_B,
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.DIMENSIONAL_SHIFT,
        ],
        changed_dimensions=[
            "stability",
            "capacity",
        ],
    )

    sequence_b = make_sequence(
        "SEQUENCE-002",
        start_time=TIME_C,
        end_time=TIME_D,
        transition_ids=[
            "TRANSITION-003",
        ],
        transition_types=[
            StateSpaceTransitionType.RECOVERY
        ],
        changed_dimensions=["capacity"],
    )

    history.add(sequence_a)
    history.add(sequence_b)

    result = history.containing_transition(
        "TRANSITION-002"
    )

    assert [
        sequence.id
        for sequence in result
    ] == [
        "SEQUENCE-001",
    ]


def test_history_returns_structural_sequences():
    history = StateSpaceTransitionSequenceHistory()

    structural = make_sequence(
        "SEQUENCE-001",
        start_time=TIME_A,
        end_time=TIME_B,
        transition_ids=["TRANSITION-001"],
        transition_types=[
            StateSpaceTransitionType.STRUCTURAL_SHIFT
        ],
        changed_dimensions=["constraint"],
        has_structural_shift=True,
    )

    ordinary = make_sequence(
        "SEQUENCE-002",
        start_time=TIME_B,
        end_time=TIME_C,
        transition_ids=["TRANSITION-002"],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION
        ],
        changed_dimensions=["stability"],
    )

    history.add(structural)
    history.add(ordinary)

    result = history.structural_sequences()

    assert [
        sequence.id
        for sequence in result
    ] == [
        "SEQUENCE-001",
    ]


def test_history_count_tracks_sequences():
    history = StateSpaceTransitionSequenceHistory()

    assert history.count() == 0

    sequence = make_sequence(
        "SEQUENCE-001",
        start_time=TIME_A,
        end_time=TIME_B,
        transition_ids=["TRANSITION-001"],
        transition_types=[
            StateSpaceTransitionType.NORMALIZATION
        ],
        changed_dimensions=["connectivity"],
    )

    history.add(sequence)

    assert history.count() == 1