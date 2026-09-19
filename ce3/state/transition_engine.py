from __future__ import annotations

from ce3.events.history import EventHistory
from ce3.events.models import Event, EventSeverity, EventType

from .models import (
    ActivityLevel,
    ControlStatus,
    DiplomaticStatus,
    EconomicStatus,
    HumanitarianStatus,
    PoliticalStatus,
)
from .transitions import StateTransition


class TransitionEngine:
    """
    Derives state transitions from chronological event history.

    The engine does not modify events or ConflictState.
    It identifies points where an event changes the derived state.
    """

    def __init__(self, history: EventHistory) -> None:
        self.history = history

    def derive_territorial_transitions(
        self,
        conflict_id: str,
    ) -> list[StateTransition]:
        """
        Derive territorial state transitions for a conflict.

        Only explicit TERRITORY_CHANGE events are considered.
        """

        events = self.history.timeline(conflict_id)

        transitions: list[StateTransition] = []

        current: dict[str, ControlStatus] = {}

        for event in events:
            if event.event_type != EventType.TERRITORY_CHANGE:
                continue

            for entity in event.affected_entities:
                previous = current.get(
                    entity,
                    ControlStatus.UNKNOWN,
                )

                new = self._territorial_status(event)

                if new == previous:
                    continue

                transitions.append(
                    StateTransition(
                        conflict_id=conflict_id,
                        entity=entity,
                        dimension="territorial",
                        occurred_at=event.occurred_at,
                        previous_value=previous,
                        new_value=new,
                        source_event_id=event.id,
                    )
                )

                current[entity] = new

        return transitions

    def derive_military_transitions(
        self,
        conflict_id: str,
    ) -> list[StateTransition]:
        """
        Derive military activity-level transitions.

        Military state represents the highest-severity military
        activity observed so far in chronological history.
        """

        events = self.history.timeline(conflict_id)

        transitions: list[StateTransition] = []

        current = ActivityLevel.UNKNOWN

        for event in events:
            if event.event_type not in {
                EventType.MILITARY_ACTION,
                EventType.FACILITY_DAMAGE,
            }:
                continue

            new = self._military_activity(event)

            if self._activity_rank(new) <= self._activity_rank(current):
                continue

            transitions.append(
                StateTransition(
                    conflict_id=conflict_id,
                    entity=None,
                    dimension="military",
                    occurred_at=event.occurred_at,
                    previous_value=current,
                    new_value=new,
                    source_event_id=event.id,
                )
            )

            current = new

        return transitions

    def derive_diplomatic_transitions(
        self,
        conflict_id: str,
    ) -> list[StateTransition]:
        """
        Derive diplomatic state transitions.

        Diplomatic states are categorical rather than ordinal.
        Every relevant event is mapped to an explicit diplomatic
        state, and a transition is recorded whenever that state
        differs from the current state.
        """

        events = self.history.timeline(conflict_id)

        transitions: list[StateTransition] = []

        current = DiplomaticStatus.UNKNOWN

        for event in events:
            if event.event_type not in {
                EventType.DIPLOMATIC_ACTION,
                EventType.NEGOTIATION,
                EventType.AGREEMENT,
            }:
                continue

            new = self._diplomatic_status(event)

            if new == current:
                continue

            transitions.append(
                StateTransition(
                    conflict_id=conflict_id,
                    entity=None,
                    dimension="diplomatic",
                    occurred_at=event.occurred_at,
                    previous_value=current,
                    new_value=new,
                    source_event_id=event.id,
                )
            )

            current = new

        return transitions

    def derive_political_transitions(
        self,
        conflict_id: str,
    ) -> list[StateTransition]:
        """
        Derive political state transitions.

        Political states are categorical rather than ordinal.

        Normal political, leadership, or policy changes produce
        CHANGING.

        High or critical political events produce DISRUPTED.

        A transition is recorded only when the derived state
        changes.
        """

        events = self.history.timeline(conflict_id)

        transitions: list[StateTransition] = []

        current = PoliticalStatus.UNKNOWN

        for event in events:
            if event.event_type not in {
                EventType.POLITICAL_CHANGE,
                EventType.LEADERSHIP_CHANGE,
                EventType.POLICY_CHANGE,
            }:
                continue

            new = self._political_status(event)

            if new == current:
                continue

            transitions.append(
                StateTransition(
                    conflict_id=conflict_id,
                    entity=None,
                    dimension="political",
                    occurred_at=event.occurred_at,
                    previous_value=current,
                    new_value=new,
                    source_event_id=event.id,
                )
            )

            current = new

        return transitions

    def derive_economic_transitions(
        self,
        conflict_id: str,
    ) -> list[StateTransition]:
        """
        Derive economic state transitions.

        Economic state represents the highest-severity economic
        condition observed so far.

        The progression is:

            UNKNOWN
                ↓
            PRESSURED
                ↓
            DISRUPTED
                ↓
            CRITICAL

        Lower-severity events do not reverse a previously
        observed higher economic state.

        A transition is recorded only when the derived state
        changes.
        """

        events = self.history.timeline(conflict_id)

        transitions: list[StateTransition] = []

        current = EconomicStatus.UNKNOWN

        for event in events:
            if event.event_type not in {
                EventType.ECONOMIC_SHOCK,
                EventType.SANCTION,
                EventType.TRADE_CHANGE,
            }:
                continue

            new = self._economic_status(event)

            if self._economic_rank(new) <= self._economic_rank(current):
                continue

            transitions.append(
                StateTransition(
                    conflict_id=conflict_id,
                    entity=None,
                    dimension="economic",
                    occurred_at=event.occurred_at,
                    previous_value=current,
                    new_value=new,
                    source_event_id=event.id,
                )
            )

            current = new

        return transitions

    def derive_humanitarian_transitions(
        self,
        conflict_id: str,
    ) -> list[StateTransition]:
        """
        Derive humanitarian state transitions.

        Humanitarian state represents the highest-severity
        humanitarian condition observed so far.

        The progression is:

            UNKNOWN
                ↓
            STRAINED
                ↓
            SEVERE
                ↓
            CRITICAL

        Lower-severity events do not reverse a previously
        observed higher humanitarian state.

        A transition is recorded only when the derived state
        changes.
        """

        events = self.history.timeline(conflict_id)

        transitions: list[StateTransition] = []

        current = HumanitarianStatus.UNKNOWN

        for event in events:
            if event.event_type != EventType.HUMANITARIAN_EVENT:
                continue

            new = self._humanitarian_status(event)

            if (
                self._humanitarian_rank(new)
                <= self._humanitarian_rank(current)
            ):
                continue

            transitions.append(
                StateTransition(
                    conflict_id=conflict_id,
                    entity=None,
                    dimension="humanitarian",
                    occurred_at=event.occurred_at,
                    previous_value=current,
                    new_value=new,
                    source_event_id=event.id,
                )
            )

            current = new

        return transitions

    def derive_all_transitions(
        self,
        conflict_id: str,
    ) -> list[StateTransition]:
        """
        Derive all state transitions for a conflict.

        This combines the six dimension-specific transition
        streams into one chronological history.

        The method does not create new transition logic.
        It delegates to the existing dimension-specific
        methods and sorts their results by occurrence time.
        """

        transitions = [
            *self.derive_territorial_transitions(
                conflict_id
            ),
            *self.derive_military_transitions(
                conflict_id
            ),
            *self.derive_diplomatic_transitions(
                conflict_id
            ),
            *self.derive_political_transitions(
                conflict_id
            ),
            *self.derive_economic_transitions(
                conflict_id
            ),
            *self.derive_humanitarian_transitions(
                conflict_id
            ),
        ]

        return sorted(
            transitions,
            key=lambda transition: transition.occurred_at,
        )

    @staticmethod
    def _territorial_status(
        event: Event,
    ) -> ControlStatus:
        text = (
            f"{event.title} {event.description}"
        ).lower()

        if "lost" in text:
            return ControlStatus.LOST

        if "contested" in text:
            return ControlStatus.CONTESTED

        if "controlled" in text:
            return ControlStatus.CONTROLLED

        return ControlStatus.UNKNOWN

    @staticmethod
    def _military_activity(
        event: Event,
    ) -> ActivityLevel:
        return {
            EventSeverity.UNKNOWN: ActivityLevel.UNKNOWN,
            EventSeverity.LOW: ActivityLevel.LOW,
            EventSeverity.MEDIUM: ActivityLevel.MEDIUM,
            EventSeverity.HIGH: ActivityLevel.HIGH,
            EventSeverity.CRITICAL: ActivityLevel.CRITICAL,
        }[event.severity]

    @staticmethod
    def _activity_rank(
        activity: ActivityLevel,
    ) -> int:
        return {
            ActivityLevel.UNKNOWN: 0,
            ActivityLevel.NONE: 0,
            ActivityLevel.LOW: 1,
            ActivityLevel.MEDIUM: 2,
            ActivityLevel.HIGH: 3,
            ActivityLevel.CRITICAL: 4,
        }[activity]

    @staticmethod
    def _diplomatic_status(
        event: Event,
    ) -> DiplomaticStatus:
        text = (
            f"{event.title} {event.description}"
        ).lower()

        if (
            "breakdown" in text
            or "break down" in text
            or "broke down" in text
            or "collapsed" in text
            or "collapse" in text
        ):
            return DiplomaticStatus.BREAKDOWN

        if event.event_type == EventType.AGREEMENT:
            return DiplomaticStatus.AGREEMENT

        if event.event_type == EventType.NEGOTIATION:
            return DiplomaticStatus.NEGOTIATION

        return DiplomaticStatus.CONTACT

    @staticmethod
    def _political_status(
        event: Event,
    ) -> PoliticalStatus:
        if event.severity in {
            EventSeverity.HIGH,
            EventSeverity.CRITICAL,
        }:
            return PoliticalStatus.DISRUPTED

        return PoliticalStatus.CHANGING

    @staticmethod
    def _economic_status(
        event: Event,
    ) -> EconomicStatus:
        return {
            EventSeverity.UNKNOWN: EconomicStatus.PRESSURED,
            EventSeverity.LOW: EconomicStatus.PRESSURED,
            EventSeverity.MEDIUM: EconomicStatus.PRESSURED,
            EventSeverity.HIGH: EconomicStatus.DISRUPTED,
            EventSeverity.CRITICAL: EconomicStatus.CRITICAL,
        }[event.severity]

    @staticmethod
    def _economic_rank(
        status: EconomicStatus,
    ) -> int:
        return {
            EconomicStatus.UNKNOWN: 0,
            EconomicStatus.STABLE: 0,
            EconomicStatus.PRESSURED: 1,
            EconomicStatus.DISRUPTED: 2,
            EconomicStatus.CRITICAL: 3,
        }[status]

    @staticmethod
    def _humanitarian_status(
        event: Event,
    ) -> HumanitarianStatus:
        return {
            EventSeverity.UNKNOWN: HumanitarianStatus.STRAINED,
            EventSeverity.LOW: HumanitarianStatus.STRAINED,
            EventSeverity.MEDIUM: HumanitarianStatus.STRAINED,
            EventSeverity.HIGH: HumanitarianStatus.SEVERE,
            EventSeverity.CRITICAL: HumanitarianStatus.CRITICAL,
        }[event.severity]

    @staticmethod
    def _humanitarian_rank(
        status: HumanitarianStatus,
    ) -> int:
        return {
            HumanitarianStatus.UNKNOWN: 0,
            HumanitarianStatus.STABLE: 0,
            HumanitarianStatus.STRAINED: 1,
            HumanitarianStatus.SEVERE: 2,
            HumanitarianStatus.CRITICAL: 3,
        }[status]