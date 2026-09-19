from __future__ import annotations

from datetime import datetime

from ce3.events.history import EventHistory
from ce3.events.models import Event, EventSeverity, EventType

from .models import (
    ActivityLevel,
    ConflictState,
    ControlStatus,
    DiplomaticStatus,
    EconomicStatus,
    HumanitarianStatus,
    MilitaryState,
    PoliticalStatus,
    TerritorialState,
)


class StateEngine:
    """
    Deterministic engine for deriving ConflictState from EventHistory.

    The engine does not create evidence and does not alter events.
    """

    def __init__(self, history: EventHistory) -> None:
        self.history = history

    def derive(
        self,
        conflict_id: str,
        *,
        as_of: datetime,
    ) -> ConflictState:
        """
        Derive conflict state from all events occurring at or before
        the supplied timestamp.
        """

        events = self.history.as_of(
            conflict_id,
            as_of,
        )

        if not events:
            return ConflictState(
                conflict_id=conflict_id,
                as_of=as_of,
                confidence=0.0,
                uncertainty=[
                    "No events available for this conflict and timestamp."
                ],
            )

        territorial = self._territorial_state(events)

        military = self._military_state(events)

        diplomatic = self._diplomatic_state(events)

        political = self._political_state(events)

        economic = self._economic_state(events)

        humanitarian = self._humanitarian_state(events)

        source_event_ids = [
            event.id
            for event in events
        ]

        confidence = self._state_confidence(events)

        uncertainty = self._uncertainty(
            events,
            confidence,
        )

        return ConflictState(
            conflict_id=conflict_id,
            as_of=as_of,
            territorial=territorial,
            military=military,
            diplomatic=diplomatic,
            political=political,
            economic=economic,
            humanitarian=humanitarian,
            source_event_ids=source_event_ids,
            confidence=confidence,
            uncertainty=uncertainty,
        )

    def _territorial_state(
        self,
        events: list[Event],
    ) -> list[TerritorialState]:
        """
        Derive territorial state from the latest relevant event
        affecting each entity.

        This first implementation is deliberately conservative.
        Only explicit territory-change events produce a territorial
        conclusion.
        """

        latest: dict[str, Event] = {}

        for event in events:
            if event.event_type != EventType.TERRITORY_CHANGE:
                continue

            for entity in event.affected_entities:
                latest[entity] = event

        result = []

        for entity, event in latest.items():
            status = self._territorial_status(event)

            result.append(
                TerritorialState(
                    entity=entity,
                    status=status,
                    confidence=event.confidence,
                    source_event_ids=[event.id],
                )
            )

        return sorted(
            result,
            key=lambda item: item.entity,
        )

    def _territorial_status(
        self,
        event: Event,
    ) -> ControlStatus:
        """
        Map explicit event descriptions into broad territorial states.

        This is intentionally conservative until a richer territorial
        ontology is introduced.
        """

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

    def _military_state(
        self,
        events: list[Event],
    ) -> MilitaryState:
        relevant = [
            event
            for event in events
            if event.event_type
            in {
                EventType.MILITARY_ACTION,
                EventType.FACILITY_DAMAGE,
            }
        ]

        if not relevant:
            return MilitaryState()

        highest = max(
            relevant,
            key=lambda event: self._severity_rank(
                event.severity
            ),
        )

        activity = {
            EventSeverity.LOW: ActivityLevel.LOW,
            EventSeverity.MEDIUM: ActivityLevel.MEDIUM,
            EventSeverity.HIGH: ActivityLevel.HIGH,
            EventSeverity.CRITICAL: ActivityLevel.CRITICAL,
            EventSeverity.UNKNOWN: ActivityLevel.UNKNOWN,
        }[highest.severity]

        return MilitaryState(
            activity_level=activity,
            source_event_ids=[
                event.id
                for event in relevant
            ],
        )

    def _diplomatic_state(
        self,
        events: list[Event],
    ) -> DiplomaticStatus:
        relevant = [
            event
            for event in events
            if event.event_type
            in {
                EventType.DIPLOMATIC_ACTION,
                EventType.AGREEMENT,
                EventType.NEGOTIATION,
            }
        ]

        if not relevant:
            return DiplomaticStatus.UNKNOWN

        latest = relevant[-1]

        if latest.event_type == EventType.AGREEMENT:
            return DiplomaticStatus.AGREEMENT

        if latest.event_type == EventType.NEGOTIATION:
            return DiplomaticStatus.NEGOTIATION

        return DiplomaticStatus.CONTACT

    def _political_state(
        self,
        events: list[Event],
    ) -> PoliticalStatus:
        relevant = [
            event
            for event in events
            if event.event_type
            in {
                EventType.POLITICAL_CHANGE,
                EventType.LEADERSHIP_CHANGE,
                EventType.POLICY_CHANGE,
            }
        ]

        if not relevant:
            return PoliticalStatus.UNKNOWN

        if any(
            event.severity
            in {
                EventSeverity.HIGH,
                EventSeverity.CRITICAL,
            }
            for event in relevant
        ):
            return PoliticalStatus.DISRUPTED

        return PoliticalStatus.CHANGING

    def _economic_state(
        self,
        events: list[Event],
    ) -> EconomicStatus:
        relevant = [
            event
            for event in events
            if event.event_type
            in {
                EventType.ECONOMIC_SHOCK,
                EventType.SANCTION,
                EventType.TRADE_CHANGE,
            }
        ]

        if not relevant:
            return EconomicStatus.UNKNOWN

        if any(
            event.severity == EventSeverity.CRITICAL
            for event in relevant
        ):
            return EconomicStatus.CRITICAL

        if any(
            event.severity == EventSeverity.HIGH
            for event in relevant
        ):
            return EconomicStatus.DISRUPTED

        return EconomicStatus.PRESSURED

    def _humanitarian_state(
        self,
        events: list[Event],
    ) -> HumanitarianStatus:
        relevant = [
            event
            for event in events
            if event.event_type
            == EventType.HUMANITARIAN_EVENT
        ]

        if not relevant:
            return HumanitarianStatus.UNKNOWN

        if any(
            event.severity == EventSeverity.CRITICAL
            for event in relevant
        ):
            return HumanitarianStatus.CRITICAL

        if any(
            event.severity == EventSeverity.HIGH
            for event in relevant
        ):
            return HumanitarianStatus.SEVERE

        return HumanitarianStatus.STRAINED

    def _state_confidence(
        self,
        events: list[Event],
    ) -> float:
        """
        Conservative aggregate confidence.

        This is a diagnostic aggregate, not a calibrated probability.
        """

        if not events:
            return 0.0

        return sum(
            event.confidence
            for event in events
        ) / len(events)

    def _uncertainty(
        self,
        events: list[Event],
        confidence: float,
    ) -> list[str]:
        uncertainty = []

        if confidence < 0.5:
            uncertainty.append(
                "Derived state has low aggregate event confidence."
            )

        if any(
            event.confidence < 0.5
            for event in events
        ):
            uncertainty.append(
                "One or more contributing events have low confidence."
            )

        return uncertainty

    @staticmethod
    def _severity_rank(
        severity: EventSeverity,
    ) -> int:
        return {
            EventSeverity.UNKNOWN: 0,
            EventSeverity.LOW: 1,
            EventSeverity.MEDIUM: 2,
            EventSeverity.HIGH: 3,
            EventSeverity.CRITICAL: 4,
        }[severity]