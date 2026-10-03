from __future__ import annotations

from datetime import datetime

from .sequence import StateSpaceTransitionSequence
from .transition import StateSpaceTransitionType


class StateSpaceTransitionSequenceHistory:
    """
    Store and query observed state-space transition sequences.

    The history is descriptive. It records sequences that have
    already been constructed from observed transitions. It does not
    forecast future sequences, infer causality, or assign probabilities
    to future states.
    """

    def __init__(self) -> None:
        self._sequences: dict[
            str,
            StateSpaceTransitionSequence,
        ] = {}

    def add(
        self,
        sequence: StateSpaceTransitionSequence,
    ) -> StateSpaceTransitionSequence:
        """
        Add a sequence to history.

        Sequence IDs must be unique.
        """
        if sequence.id in self._sequences:
            raise ValueError(
                f"Sequence already exists: {sequence.id}"
            )

        self._sequences[sequence.id] = sequence

        return sequence

    def get(
        self,
        sequence_id: str,
    ) -> StateSpaceTransitionSequence:
        """
        Retrieve a sequence by ID.
        """
        try:
            return self._sequences[sequence_id]
        except KeyError as exc:
            raise KeyError(
                f"Unknown sequence: {sequence_id}"
            ) from exc

    def all(
        self,
    ) -> list[StateSpaceTransitionSequence]:
        """
        Return all sequences in deterministic chronological order.
        """
        return sorted(
            self._sequences.values(),
            key=lambda sequence: (
                sequence.start_time,
                sequence.end_time,
                sequence.id,
            ),
        )

    def between(
        self,
        start: datetime,
        end: datetime,
    ) -> list[StateSpaceTransitionSequence]:
        """
        Return sequences whose observed time window overlaps
        the requested interval.

        A sequence is included when its end time is on or after
        the interval start and its start time is on or before the
        interval end.
        """
        return [
            sequence
            for sequence in self.all()
            if (
                sequence.end_time >= start
                and sequence.start_time <= end
            )
        ]

    def as_of(
        self,
        timestamp: datetime,
    ) -> list[StateSpaceTransitionSequence]:
        """
        Return sequences that had completed by the given timestamp.
        """
        return [
            sequence
            for sequence in self.all()
            if sequence.end_time <= timestamp
        ]

    def latest(
        self,
    ) -> StateSpaceTransitionSequence | None:
        """
        Return the most recently completed sequence.
        """
        sequences = self.all()

        if not sequences:
            return None

        return max(
            sequences,
            key=lambda sequence: (
                sequence.end_time,
                sequence.id,
            ),
        )

    def by_transition_type(
        self,
        transition_type: StateSpaceTransitionType,
    ) -> list[StateSpaceTransitionSequence]:
        """
        Return sequences containing the specified transition type.
        """
        return [
            sequence
            for sequence in self.all()
            if transition_type in sequence.transition_types
        ]

    def affecting_dimension(
        self,
        dimension: str,
    ) -> list[StateSpaceTransitionSequence]:
        """
        Return sequences that affected the specified dimension.
        """
        return [
            sequence
            for sequence in self.all()
            if dimension in sequence.changed_dimensions
        ]

    def involving_position(
        self,
        position_id: str,
    ) -> list[StateSpaceTransitionSequence]:
        """
        Return sequences beginning or ending at the specified
        state-space position.
        """
        return [
            sequence
            for sequence in self.all()
            if (
                sequence.start_position_id == position_id
                or sequence.end_position_id == position_id
            )
        ]

    def containing_transition(
        self,
        transition_id: str,
    ) -> list[StateSpaceTransitionSequence]:
        """
        Return sequences containing the specified transition.
        """
        return [
            sequence
            for sequence in self.all()
            if transition_id in sequence.transition_ids
        ]

    def structural_sequences(
        self,
    ) -> list[StateSpaceTransitionSequence]:
        """
        Return sequences containing an observed structural shift.
        """
        return [
            sequence
            for sequence in self.all()
            if sequence.has_structural_shift
        ]

    def count(self) -> int:
        """
        Return the number of stored sequences.
        """
        return len(self._sequences)