from datetime import datetime, timedelta, timezone

from ce3.events.history import EventHistory
from ce3.events.models import (
    Event,
    EventSeverity,
    EventType,
)
from ce3.events.store import EventStore
from ce3.state.engine import StateEngine
from ce3.state.models import (
    ActivityLevel,
    ControlStatus,
    DiplomaticStatus,
    EconomicStatus,
    HumanitarianStatus,
    PoliticalStatus,
)


def make_event(
    event_id: str,
    conflict_id: str,
    event_type: EventType,
    occurred_at: datetime,
    *,
    severity: EventSeverity = EventSeverity.MEDIUM,
    title: str = "Test event",
    description: str = "Test description",
    affected_entities: list[str] | None = None,
    confidence: float = 0.8,
) -> Event:
    return Event(
        id=event_id,
        conflict_id=conflict_id,
        event_type=event_type,
        occurred_at=occurred_at,
        detected_at=occurred_at,
        title=title,
        description=description,
        severity=severity,
        affected_entities=affected_entities or [],
        confidence=confidence,
    )


def make_engine() -> StateEngine:
    store = EventStore()
    history = EventHistory(store)
    return StateEngine(history)


def test_empty_conflict_produces_unknown_state():
    engine = make_engine()

    now = datetime.now(timezone.utc)

    state = engine.derive(
        "C1",
        as_of=now,
    )

    assert state.conflict_id == "C1"
    assert state.territorial == []
    assert state.military.activity_level == ActivityLevel.UNKNOWN
    assert state.diplomatic == DiplomaticStatus.UNKNOWN
    assert state.political == PoliticalStatus.UNKNOWN
    assert state.economic == EconomicStatus.UNKNOWN
    assert state.humanitarian == HumanitarianStatus.UNKNOWN
    assert state.confidence == 0.0
    assert state.uncertainty


def test_military_state_uses_highest_recorded_severity():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "C1",
            EventType.MILITARY_ACTION,
            now,
            severity=EventSeverity.MEDIUM,
        )
    )

    store.add(
        make_event(
            "E2",
            "C1",
            EventType.FACILITY_DAMAGE,
            now + timedelta(hours=1),
            severity=EventSeverity.HIGH,
        )
    )

    history = EventHistory(store)
    engine = StateEngine(history)

    state = engine.derive(
        "C1",
        as_of=now + timedelta(hours=2),
    )

    assert state.military.activity_level == ActivityLevel.HIGH

    assert state.military.source_event_ids == [
        "E1",
        "E2",
    ]


def test_territorial_state_uses_latest_event_for_entity():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "C1",
            EventType.TERRITORY_CHANGE,
            now,
            title="Facility X controlled",
            description="Facility X is controlled.",
            affected_entities=["Facility X"],
            confidence=0.7,
        )
    )

    store.add(
        make_event(
            "E2",
            "C1",
            EventType.TERRITORY_CHANGE,
            now + timedelta(hours=1),
            title="Facility X contested",
            description="Facility X is contested.",
            affected_entities=["Facility X"],
            confidence=0.8,
        )
    )

    history = EventHistory(store)
    engine = StateEngine(history)

    state = engine.derive(
        "C1",
        as_of=now + timedelta(hours=2),
    )

    assert len(state.territorial) == 1

    territorial = state.territorial[0]

    assert territorial.entity == "Facility X"

    assert territorial.status == ControlStatus.CONTESTED

    assert territorial.source_event_ids == ["E2"]


def test_diplomatic_state_reflects_latest_diplomatic_event():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "C1",
            EventType.DIPLOMATIC_ACTION,
            now,
        )
    )

    store.add(
        make_event(
            "E2",
            "C1",
            EventType.NEGOTIATION,
            now + timedelta(hours=1),
        )
    )

    history = EventHistory(store)
    engine = StateEngine(history)

    state = engine.derive(
        "C1",
        as_of=now + timedelta(hours=2),
    )

    assert state.diplomatic == DiplomaticStatus.NEGOTIATION


def test_political_state_becomes_disrupted_for_high_severity_change():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "C1",
            EventType.LEADERSHIP_CHANGE,
            now,
            severity=EventSeverity.HIGH,
        )
    )

    history = EventHistory(store)
    engine = StateEngine(history)

    state = engine.derive(
        "C1",
        as_of=now + timedelta(hours=1),
    )

    assert state.political == PoliticalStatus.DISRUPTED


def test_economic_state_becomes_critical_for_critical_shock():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "C1",
            EventType.ECONOMIC_SHOCK,
            now,
            severity=EventSeverity.CRITICAL,
        )
    )

    history = EventHistory(store)
    engine = StateEngine(history)

    state = engine.derive(
        "C1",
        as_of=now + timedelta(hours=1),
    )

    assert state.economic == EconomicStatus.CRITICAL


def test_humanitarian_state_becomes_severe_for_high_severity_event():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "C1",
            EventType.HUMANITARIAN_EVENT,
            now,
            severity=EventSeverity.HIGH,
        )
    )

    history = EventHistory(store)
    engine = StateEngine(history)

    state = engine.derive(
        "C1",
        as_of=now + timedelta(hours=1),
    )

    assert state.humanitarian == HumanitarianStatus.SEVERE


def test_state_respects_as_of_timestamp():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "C1",
            EventType.MILITARY_ACTION,
            now,
            severity=EventSeverity.LOW,
        )
    )

    store.add(
        make_event(
            "E2",
            "C1",
            EventType.MILITARY_ACTION,
            now + timedelta(hours=2),
            severity=EventSeverity.CRITICAL,
        )
    )

    history = EventHistory(store)
    engine = StateEngine(history)

    state = engine.derive(
        "C1",
        as_of=now + timedelta(hours=1),
    )

    assert state.military.activity_level == ActivityLevel.LOW

    assert state.source_event_ids == ["E1"]


def test_state_confidence_is_derived_from_events():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "C1",
            EventType.MILITARY_ACTION,
            now,
            confidence=0.6,
        )
    )

    store.add(
        make_event(
            "E2",
            "C1",
            EventType.MILITARY_ACTION,
            now + timedelta(hours=1),
            confidence=0.8,
        )
    )

    history = EventHistory(store)
    engine = StateEngine(history)

    state = engine.derive(
        "C1",
        as_of=now + timedelta(hours=2),
    )

    assert state.confidence == 0.7