from __future__ import annotations

from datetime import datetime

from .models import (
    ActivityLevel,
    ConflictState,
    ControlStatus,
    DiplomaticStatus,
    EconomicStatus,
    HumanitarianStatus,
    PoliticalStatus,
)
from .transitions import StateTransition


class TransitionHistory:
    """
    Query interface for historical state transitions.

    TransitionHistory does not create or modify transitions.
    It provides deterministic temporal and entity-based queries.
    """

    def __init__(
        self,
        transitions: list[StateTransition],
    ) -> None:
        self.transitions = sorted(
            transitions,
            key=lambda transition: transition.occurred_at,
        )

    def timeline(
        self,
        conflict_id: str,
    ) -> list[StateTransition]:
        """
        Return all transitions for a conflict chronologically.
        """

        return [
            transition
            for transition in self.transitions
            if transition.conflict_id == conflict_id
        ]

    def between(
        self,
        conflict_id: str,
        start: datetime,
        end: datetime,
    ) -> list[StateTransition]:
        """
        Return transitions occurring within an inclusive time window.
        """

        return [
            transition
            for transition in self.timeline(conflict_id)
            if start <= transition.occurred_at <= end
        ]

    def affecting_entity(
        self,
        conflict_id: str,
        entity: str,
    ) -> list[StateTransition]:
        """
        Return transitions affecting a specific entity.
        """

        return [
            transition
            for transition in self.timeline(conflict_id)
            if transition.entity == entity
        ]

    def latest(
        self,
        conflict_id: str,
        entity: str | None = None,
    ) -> StateTransition | None:
        """
        Return the latest transition for a conflict.

        If entity is supplied, return the latest transition
        affecting that entity.
        """

        transitions = self.timeline(conflict_id)

        if entity is not None:
            transitions = [
                transition
                for transition in transitions
                if transition.entity == entity
            ]

        if not transitions:
            return None

        return transitions[-1]

    def reconstruct_state_at(
        self,
        conflict_id: str,
        as_of: datetime,
    ) -> ConflictState:
        """
        Reconstruct the derived conflict state at a point in time.

        Only transitions belonging to the requested conflict and
        occurring at or before `as_of` are applied.

        This method does not derive new state transitions. It only
        replays existing transitions in chronological order.
        """

        territorial: dict[str, ControlStatus] = {}
        military = ActivityLevel.UNKNOWN
        diplomatic = DiplomaticStatus.UNKNOWN
        political = PoliticalStatus.UNKNOWN
        economic = EconomicStatus.UNKNOWN
        humanitarian = HumanitarianStatus.UNKNOWN

        source_event_ids: list[str] = []

        for transition in self.transitions:
            if transition.conflict_id != conflict_id:
                continue

            if transition.occurred_at > as_of:
                continue

            if transition.new_value is None:
                continue

            if transition.dimension == "territorial":
                if transition.entity is not None:
                    territorial[
                        transition.entity
                    ] = transition.new_value

            elif transition.dimension == "military":
                military = transition.new_value

            elif transition.dimension == "diplomatic":
                diplomatic = transition.new_value

            elif transition.dimension == "political":
                political = transition.new_value

            elif transition.dimension == "economic":
                economic = transition.new_value

            elif transition.dimension == "humanitarian":
                humanitarian = transition.new_value

            if transition.source_event_id not in source_event_ids:
                source_event_ids.append(
                    transition.source_event_id
                )

        territorial_states = [
            {
                "entity": entity,
                "status": status,
                "confidence": 0.0,
                "source_event_ids": [],
            }
            for entity, status in territorial.items()
        ]

        return ConflictState(
            conflict_id=conflict_id,
            as_of=as_of,
            territorial=territorial_states,
            military={
                "activity_level": military,
                "source_event_ids": [],
            },
            diplomatic=diplomatic,
            political=political,
            economic=economic,
            humanitarian=humanitarian,
            source_event_ids=source_event_ids,
            confidence=0.0,
        )

    def caused_by_event(
        self,
        conflict_id: str,
        event_id: str,
    ) -> list[StateTransition]:
        """
        Return transitions caused by a specific event.
        """

        return [
            transition
            for transition in self.timeline(conflict_id)
            if transition.source_event_id == event_id
        ]

    def evolution(
        self,
        conflict_id: str,
    ) -> list[ConflictState]:
        """
        Reconstruct the complete state evolution of a conflict.

        A new ConflictState is produced after each transition
        affecting the requested conflict.

        States are cumulative: each state includes all transitions
        observed up to that point in time.
        """

        transitions = [
            transition
            for transition in self.transitions
            if transition.conflict_id == conflict_id
        ]

        if not transitions:
            return []

        evolution: list[ConflictState] = []

        for transition in transitions:
            state = self.reconstruct_state_at(
                conflict_id,
                transition.occurred_at,
            )

            evolution.append(state)

        return evolution


def test_evolution_handles_multiple_transitions_at_same_timestamp():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-1",
            dimension="military",
            occurred_at=base,
            previous_value=ActivityLevel.UNKNOWN,
            new_value=ActivityLevel.MEDIUM,
            source_event_id="event-military",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="economic",
            occurred_at=base,
            previous_value=EconomicStatus.UNKNOWN,
            new_value=EconomicStatus.DISRUPTED,
            source_event_id="event-economic",
        ),
    ]

    history = TransitionHistory(transitions)

    evolution = history.evolution("conflict-1")

    assert len(evolution) == 2

    assert evolution[0].as_of == base
    assert evolution[1].as_of == base

    assert evolution[-1].military.activity_level == (
        ActivityLevel.MEDIUM
    )

    assert evolution[-1].economic == (
        EconomicStatus.DISRUPTED
    )

    assert evolution[-1].source_event_ids == [
        "event-military",
        "event-economic",
    ]