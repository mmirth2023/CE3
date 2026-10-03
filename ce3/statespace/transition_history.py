from __future__ import annotations

from datetime import datetime

from .transition import (
    StateSpaceTransition,
    StateSpaceTransitionType,
)


class StateSpaceTransitionHistory:
    """
    Store and query observed state-space transitions over time.

    The history layer preserves assessed transitions. It does not
    reclassify transitions, infer causality, forecast future states,
    or alter the underlying transition assessment.
    """

    def __init__(self) -> None:
        self._transitions: dict[
            str,
            StateSpaceTransition,
        ] = {}

    def add(
        self,
        transition: StateSpaceTransition,
    ) -> StateSpaceTransition:
        """
        Add a transition to history.

        Transition IDs must be unique.
        """
        if transition.id in self._transitions:
            raise ValueError(
                f"Transition already exists: {transition.id}"
            )

        self._transitions[
            transition.id
        ] = transition

        return transition

    def get(
        self,
        transition_id: str,
    ) -> StateSpaceTransition:
        """
        Retrieve a transition by ID.
        """
        try:
            return self._transitions[
                transition_id
            ]
        except KeyError as exc:
            raise KeyError(
                f"Unknown transition: {transition_id}"
            ) from exc

    def all(self) -> list[StateSpaceTransition]:
        """
        Return all transitions in chronological order.
        """
        return sorted(
            self._transitions.values(),
            key=lambda transition: (
                transition.assessed_at,
                transition.id,
            ),
        )

    def between(
        self,
        start: datetime,
        end: datetime,
    ) -> list[StateSpaceTransition]:
        """
        Return transitions assessed within an inclusive time range.
        """
        return [
            transition
            for transition in self.all()
            if start
            <= transition.assessed_at
            <= end
        ]

    def as_of(
        self,
        timestamp: datetime,
    ) -> list[StateSpaceTransition]:
        """
        Return transitions assessed on or before a timestamp.
        """
        return [
            transition
            for transition in self.all()
            if transition.assessed_at
            <= timestamp
        ]

    def latest(
        self,
    ) -> StateSpaceTransition | None:
        """
        Return the latest assessed transition.
        """
        transitions = self.all()

        if not transitions:
            return None

        return transitions[-1]

    def by_type(
        self,
        transition_type: StateSpaceTransitionType,
    ) -> list[StateSpaceTransition]:
        """
        Return transitions of a specific classification.
        """
        return [
            transition
            for transition in self.all()
            if transition.transition_type
            == transition_type
        ]

    def affecting_dimension(
        self,
        dimension: str,
    ) -> list[StateSpaceTransition]:
        """
        Return transitions that changed a specified dimension.
        """
        return [
            transition
            for transition in self.all()
            if dimension
            in transition.changed_dimensions
        ]

    def involving_position(
        self,
        position_id: str,
    ) -> list[StateSpaceTransition]:
        """
        Return transitions involving a specified position.
        """
        return [
            transition
            for transition in self.all()
            if (
                transition.previous_position_id
                == position_id
                or transition.current_position_id
                == position_id
            )
        ]

    def count(self) -> int:
        """
        Return the number of stored transitions.
        """
        return len(self._transitions)