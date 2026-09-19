from datetime import datetime, timedelta, timezone

from ce3.events.history import EventHistory
from ce3.events.models import (
    Event,
    EventSeverity,
    EventType,
)
from ce3.events.store import EventStore
from ce3.state.models import (
    ActivityLevel,
    ControlStatus,
    DiplomaticStatus,
    EconomicStatus,
    PoliticalStatus,
    HumanitarianStatus,
)
from ce3.state.transition_engine import TransitionEngine


def make_event(
    event_id: str,
    event_type: EventType,
    *,
    occurred_at: datetime | None = None,
    severity: EventSeverity = EventSeverity.MEDIUM,
    title: str = "Test event",
    description: str = "Test event description",
    affected_entities: list[str] | None = None,
) -> Event:
    if occurred_at is None:
        occurred_at = datetime.now(timezone.utc)

    return Event(
        id=event_id,
        conflict_id="conflict-1",
        event_type=event_type,
        occurred_at=occurred_at,
        detected_at=occurred_at,
        title=title,
        description=description,
        severity=severity,
        affected_entities=affected_entities or [],
        confidence=0.9,
    )


def make_engine(
    events: list[Event],
) -> TransitionEngine:
    store = EventStore()

    for event in events:
        store.add(event)

    history = EventHistory(store)

    return TransitionEngine(history)


# ---------------------------------------------------------------------------
# Territorial transitions
# ---------------------------------------------------------------------------


def test_first_territorial_event_creates_transition():
    event = make_event(
        "event-1",
        EventType.TERRITORY_CHANGE,
        title="Area controlled",
        description="Area is now controlled",
        affected_entities=["area-1"],
    )

    engine = make_engine([event])

    transitions = engine.derive_territorial_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1

    transition = transitions[0]

    assert transition.dimension == "territorial"
    assert transition.entity == "area-1"
    assert transition.previous_value == ControlStatus.UNKNOWN
    assert transition.new_value == ControlStatus.CONTROLLED
    assert transition.source_event_id == "event-1"


def test_territorial_control_change_creates_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.TERRITORY_CHANGE,
        occurred_at=base,
        title="Area controlled",
        description="Area is now controlled",
        affected_entities=["area-1"],
    )

    event_2 = make_event(
        "event-2",
        EventType.TERRITORY_CHANGE,
        occurred_at=base + timedelta(hours=1),
        title="Area contested",
        description="Area is now contested",
        affected_entities=["area-1"],
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_territorial_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert transitions[0].previous_value == ControlStatus.UNKNOWN
    assert transitions[0].new_value == ControlStatus.CONTROLLED

    assert transitions[1].previous_value == ControlStatus.CONTROLLED
    assert transitions[1].new_value == ControlStatus.CONTESTED


def test_repeated_territorial_state_does_not_create_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.TERRITORY_CHANGE,
        occurred_at=base,
        title="Area controlled",
        description="Area is now controlled",
        affected_entities=["area-1"],
    )

    event_2 = make_event(
        "event-2",
        EventType.TERRITORY_CHANGE,
        occurred_at=base + timedelta(hours=1),
        title="Area remains controlled",
        description="Area remains controlled",
        affected_entities=["area-1"],
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_territorial_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1
    assert transitions[0].source_event_id == "event-1"


def test_territorial_transitions_are_tracked_per_entity():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.TERRITORY_CHANGE,
        occurred_at=base,
        title="Area A controlled",
        description="Area A is controlled",
        affected_entities=["area-a"],
    )

    event_2 = make_event(
        "event-2",
        EventType.TERRITORY_CHANGE,
        occurred_at=base + timedelta(hours=1),
        title="Area B controlled",
        description="Area B is controlled",
        affected_entities=["area-b"],
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_territorial_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert transitions[0].entity == "area-a"
    assert transitions[1].entity == "area-b"


# ---------------------------------------------------------------------------
# Military transitions
# ---------------------------------------------------------------------------


def test_first_military_event_creates_transition():
    event = make_event(
        "event-1",
        EventType.MILITARY_ACTION,
        severity=EventSeverity.MEDIUM,
    )

    engine = make_engine([event])

    transitions = engine.derive_military_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1

    transition = transitions[0]

    assert transition.dimension == "military"
    assert transition.previous_value == ActivityLevel.UNKNOWN
    assert transition.new_value == ActivityLevel.MEDIUM
    assert transition.source_event_id == "event-1"


def test_military_severity_increase_creates_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.MILITARY_ACTION,
        occurred_at=base,
        severity=EventSeverity.LOW,
    )

    event_2 = make_event(
        "event-2",
        EventType.MILITARY_ACTION,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.HIGH,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_military_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert transitions[0].previous_value == ActivityLevel.UNKNOWN
    assert transitions[0].new_value == ActivityLevel.LOW

    assert transitions[1].previous_value == ActivityLevel.LOW
    assert transitions[1].new_value == ActivityLevel.HIGH


def test_military_lower_severity_does_not_reverse_state():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.MILITARY_ACTION,
        occurred_at=base,
        severity=EventSeverity.HIGH,
    )

    event_2 = make_event(
        "event-2",
        EventType.MILITARY_ACTION,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.LOW,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_military_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1

    assert transitions[0].previous_value == ActivityLevel.UNKNOWN
    assert transitions[0].new_value == ActivityLevel.HIGH


def test_repeated_military_severity_does_not_create_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.MILITARY_ACTION,
        occurred_at=base,
        severity=EventSeverity.MEDIUM,
    )

    event_2 = make_event(
        "event-2",
        EventType.MILITARY_ACTION,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.MEDIUM,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_military_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1
    assert transitions[0].source_event_id == "event-1"


def test_critical_military_event_creates_critical_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.MILITARY_ACTION,
        occurred_at=base,
        severity=EventSeverity.HIGH,
    )

    event_2 = make_event(
        "event-2",
        EventType.FACILITY_DAMAGE,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.CRITICAL,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_military_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert transitions[1].previous_value == ActivityLevel.HIGH
    assert transitions[1].new_value == ActivityLevel.CRITICAL


def test_non_military_events_do_not_create_military_transitions():
    event = make_event(
        "event-1",
        EventType.DIPLOMATIC_ACTION,
        severity=EventSeverity.CRITICAL,
    )

    engine = make_engine([event])

    transitions = engine.derive_military_transitions(
        "conflict-1"
    )

    assert transitions == []


# ---------------------------------------------------------------------------
# Diplomatic transitions
# ---------------------------------------------------------------------------


def test_first_diplomatic_contact_creates_transition():
    event = make_event(
        "event-1",
        EventType.DIPLOMATIC_ACTION,
        title="Officials establish contact",
        description="Officials establish diplomatic contact",
    )

    engine = make_engine([event])

    transitions = engine.derive_diplomatic_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1

    transition = transitions[0]

    assert transition.dimension == "diplomatic"
    assert transition.previous_value == DiplomaticStatus.UNKNOWN
    assert transition.new_value == DiplomaticStatus.CONTACT
    assert transition.source_event_id == "event-1"


def test_negotiation_creates_diplomatic_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.DIPLOMATIC_ACTION,
        occurred_at=base,
    )

    event_2 = make_event(
        "event-2",
        EventType.NEGOTIATION,
        occurred_at=base + timedelta(hours=1),
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_diplomatic_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert transitions[0].new_value == DiplomaticStatus.CONTACT
    assert transitions[1].previous_value == DiplomaticStatus.CONTACT
    assert transitions[1].new_value == DiplomaticStatus.NEGOTIATION


def test_agreement_creates_diplomatic_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.NEGOTIATION,
        occurred_at=base,
    )

    event_2 = make_event(
        "event-2",
        EventType.AGREEMENT,
        occurred_at=base + timedelta(hours=1),
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_diplomatic_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert transitions[0].new_value == DiplomaticStatus.NEGOTIATION
    assert transitions[1].previous_value == DiplomaticStatus.NEGOTIATION
    assert transitions[1].new_value == DiplomaticStatus.AGREEMENT


def test_diplomatic_breakdown_creates_breakdown_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.NEGOTIATION,
        occurred_at=base,
    )

    event_2 = make_event(
        "event-2",
        EventType.DIPLOMATIC_ACTION,
        occurred_at=base + timedelta(hours=1),
        title="Talks break down",
        description="Negotiations broke down",
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_diplomatic_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert transitions[1].previous_value == DiplomaticStatus.NEGOTIATION
    assert transitions[1].new_value == DiplomaticStatus.BREAKDOWN


# ---------------------------------------------------------------------------
# Political transitions
# ---------------------------------------------------------------------------


def test_first_political_event_creates_changing_transition():
    event = make_event(
        "event-1",
        EventType.POLITICAL_CHANGE,
        severity=EventSeverity.MEDIUM,
    )

    engine = make_engine([event])

    transitions = engine.derive_political_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1

    transition = transitions[0]

    assert transition.dimension == "political"
    assert transition.previous_value == PoliticalStatus.UNKNOWN
    assert transition.new_value == PoliticalStatus.CHANGING
    assert transition.source_event_id == "event-1"


def test_high_severity_political_event_creates_disrupted_transition():
    event = make_event(
        "event-1",
        EventType.LEADERSHIP_CHANGE,
        severity=EventSeverity.HIGH,
    )

    engine = make_engine([event])

    transitions = engine.derive_political_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1

    assert transitions[0].previous_value == PoliticalStatus.UNKNOWN
    assert transitions[0].new_value == PoliticalStatus.DISRUPTED


def test_political_state_changes_from_changing_to_disrupted():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.POLITICAL_CHANGE,
        occurred_at=base,
        severity=EventSeverity.MEDIUM,
    )

    event_2 = make_event(
        "event-2",
        EventType.POLICY_CHANGE,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.CRITICAL,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_political_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert transitions[0].new_value == PoliticalStatus.CHANGING
    assert transitions[1].previous_value == PoliticalStatus.CHANGING
    assert transitions[1].new_value == PoliticalStatus.DISRUPTED


def test_repeated_political_state_does_not_create_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.POLITICAL_CHANGE,
        occurred_at=base,
        severity=EventSeverity.MEDIUM,
    )

    event_2 = make_event(
        "event-2",
        EventType.LEADERSHIP_CHANGE,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.LOW,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_political_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1
    assert transitions[0].source_event_id == "event-1"


# ---------------------------------------------------------------------------
# Economic transitions
# ---------------------------------------------------------------------------


def test_first_economic_event_creates_pressured_transition():
    event = make_event(
        "event-1",
        EventType.SANCTION,
        severity=EventSeverity.MEDIUM,
    )

    engine = make_engine([event])

    transitions = engine.derive_economic_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1

    transition = transitions[0]

    assert transition.dimension == "economic"
    assert transition.previous_value == EconomicStatus.UNKNOWN
    assert transition.new_value == EconomicStatus.PRESSURED
    assert transition.source_event_id == "event-1"


def test_high_severity_economic_event_creates_disrupted_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.SANCTION,
        occurred_at=base,
        severity=EventSeverity.MEDIUM,
    )

    event_2 = make_event(
        "event-2",
        EventType.ECONOMIC_SHOCK,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.HIGH,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_economic_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert transitions[0].previous_value == EconomicStatus.UNKNOWN
    assert transitions[0].new_value == EconomicStatus.PRESSURED

    assert transitions[1].previous_value == EconomicStatus.PRESSURED
    assert transitions[1].new_value == EconomicStatus.DISRUPTED


def test_critical_economic_event_creates_critical_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.ECONOMIC_SHOCK,
        occurred_at=base,
        severity=EventSeverity.HIGH,
    )

    event_2 = make_event(
        "event-2",
        EventType.SANCTION,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.CRITICAL,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_economic_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert transitions[0].previous_value == EconomicStatus.UNKNOWN
    assert transitions[0].new_value == EconomicStatus.DISRUPTED

    assert transitions[1].previous_value == EconomicStatus.DISRUPTED
    assert transitions[1].new_value == EconomicStatus.CRITICAL


def test_lower_economic_severity_does_not_reverse_state():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.ECONOMIC_SHOCK,
        occurred_at=base,
        severity=EventSeverity.CRITICAL,
    )

    event_2 = make_event(
        "event-2",
        EventType.TRADE_CHANGE,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.MEDIUM,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_economic_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1

    assert transitions[0].previous_value == EconomicStatus.UNKNOWN
    assert transitions[0].new_value == EconomicStatus.CRITICAL


def test_repeated_economic_state_does_not_create_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.SANCTION,
        occurred_at=base,
        severity=EventSeverity.MEDIUM,
    )

    event_2 = make_event(
        "event-2",
        EventType.SANCTION,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.MEDIUM,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_economic_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1
    assert transitions[0].source_event_id == "event-1"


def test_non_economic_events_do_not_create_economic_transitions():
    event = make_event(
        "event-1",
        EventType.MILITARY_ACTION,
        severity=EventSeverity.CRITICAL,
    )

    engine = make_engine([event])

    transitions = engine.derive_economic_transitions(
        "conflict-1"
    )

    assert transitions == []


def test_first_humanitarian_event_creates_strained_transition():
    event = make_event(
        "event-1",
        EventType.HUMANITARIAN_EVENT,
        severity=EventSeverity.MEDIUM,
    )

    engine = make_engine([event])

    transitions = engine.derive_humanitarian_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1

    transition = transitions[0]

    assert transition.dimension == "humanitarian"
    assert transition.previous_value == HumanitarianStatus.UNKNOWN
    assert transition.new_value == HumanitarianStatus.STRAINED
    assert transition.source_event_id == "event-1"


def test_high_severity_humanitarian_event_creates_severe_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.HUMANITARIAN_EVENT,
        occurred_at=base,
        severity=EventSeverity.MEDIUM,
    )

    event_2 = make_event(
        "event-2",
        EventType.HUMANITARIAN_EVENT,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.HIGH,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_humanitarian_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert transitions[0].previous_value == HumanitarianStatus.UNKNOWN
    assert transitions[0].new_value == HumanitarianStatus.STRAINED

    assert transitions[1].previous_value == HumanitarianStatus.STRAINED
    assert transitions[1].new_value == HumanitarianStatus.SEVERE


def test_critical_humanitarian_event_creates_critical_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.HUMANITARIAN_EVENT,
        occurred_at=base,
        severity=EventSeverity.HIGH,
    )

    event_2 = make_event(
        "event-2",
        EventType.HUMANITARIAN_EVENT,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.CRITICAL,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_humanitarian_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert transitions[0].previous_value == HumanitarianStatus.UNKNOWN
    assert transitions[0].new_value == HumanitarianStatus.SEVERE

    assert transitions[1].previous_value == HumanitarianStatus.SEVERE
    assert transitions[1].new_value == HumanitarianStatus.CRITICAL


def test_lower_humanitarian_severity_does_not_reverse_state():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.HUMANITARIAN_EVENT,
        occurred_at=base,
        severity=EventSeverity.CRITICAL,
    )

    event_2 = make_event(
        "event-2",
        EventType.HUMANITARIAN_EVENT,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.MEDIUM,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_humanitarian_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1

    assert transitions[0].previous_value == HumanitarianStatus.UNKNOWN
    assert transitions[0].new_value == HumanitarianStatus.CRITICAL


def test_repeated_humanitarian_state_does_not_create_transition():
    base = datetime.now(timezone.utc)

    event_1 = make_event(
        "event-1",
        EventType.HUMANITARIAN_EVENT,
        occurred_at=base,
        severity=EventSeverity.MEDIUM,
    )

    event_2 = make_event(
        "event-2",
        EventType.HUMANITARIAN_EVENT,
        occurred_at=base + timedelta(hours=1),
        severity=EventSeverity.MEDIUM,
    )

    engine = make_engine(
        [
            event_1,
            event_2,
        ]
    )

    transitions = engine.derive_humanitarian_transitions(
        "conflict-1"
    )

    assert len(transitions) == 1
    assert transitions[0].source_event_id == "event-1"


def test_non_humanitarian_events_do_not_create_humanitarian_transitions():
    event = make_event(
        "event-1",
        EventType.MILITARY_ACTION,
        severity=EventSeverity.CRITICAL,
    )

    engine = make_engine([event])

    transitions = engine.derive_humanitarian_transitions(
        "conflict-1"
    )

    assert transitions == []

    
def test_derive_all_transitions_combines_all_dimensions():
    base = datetime.now(timezone.utc)

    events = [
        make_event(
            "event-1",
            EventType.MILITARY_ACTION,
            occurred_at=base,
            severity=EventSeverity.MEDIUM,
        ),
        make_event(
            "event-2",
            EventType.ECONOMIC_SHOCK,
            occurred_at=base + timedelta(hours=1),
            severity=EventSeverity.HIGH,
        ),
        make_event(
            "event-3",
            EventType.DIPLOMATIC_ACTION,
            occurred_at=base + timedelta(hours=2),
        ),
        make_event(
            "event-4",
            EventType.HUMANITARIAN_EVENT,
            occurred_at=base + timedelta(hours=3),
            severity=EventSeverity.HIGH,
        ),
        make_event(
            "event-5",
            EventType.POLITICAL_CHANGE,
            occurred_at=base + timedelta(hours=4),
            severity=EventSeverity.MEDIUM,
        ),
        make_event(
            "event-6",
            EventType.TERRITORY_CHANGE,
            occurred_at=base + timedelta(hours=5),
            title="Area controlled",
            description="Area is now controlled",
            affected_entities=["area-1"],
        ),
    ]

    engine = make_engine(events)

    transitions = engine.derive_all_transitions(
        "conflict-1"
    )

    assert len(transitions) == 6

    assert [
        transition.dimension
        for transition in transitions
    ] == [
        "military",
        "economic",
        "diplomatic",
        "humanitarian",
        "political",
        "territorial",
    ]


def test_derive_all_transitions_is_chronological():
    base = datetime.now(timezone.utc)

    events = [
        make_event(
            "event-3",
            EventType.DIPLOMATIC_ACTION,
            occurred_at=base + timedelta(hours=2),
        ),
        make_event(
            "event-1",
            EventType.MILITARY_ACTION,
            occurred_at=base,
            severity=EventSeverity.MEDIUM,
        ),
        make_event(
            "event-2",
            EventType.ECONOMIC_SHOCK,
            occurred_at=base + timedelta(hours=1),
            severity=EventSeverity.HIGH,
        ),
    ]

    engine = make_engine(events)

    transitions = engine.derive_all_transitions(
        "conflict-1"
    )

    assert len(transitions) == 3

    assert [
        transition.source_event_id
        for transition in transitions
    ] == [
        "event-1",
        "event-2",
        "event-3",
    ]

    assert transitions[0].occurred_at <= transitions[1].occurred_at
    assert transitions[1].occurred_at <= transitions[2].occurred_at


def test_derive_all_transitions_ignores_events_without_state_changes():
    base = datetime.now(timezone.utc)

    events = [
        make_event(
            "event-1",
            EventType.MILITARY_ACTION,
            occurred_at=base,
            severity=EventSeverity.MEDIUM,
        ),
        make_event(
            "event-2",
            EventType.MILITARY_ACTION,
            occurred_at=base + timedelta(hours=1),
            severity=EventSeverity.MEDIUM,
        ),
        make_event(
            "event-3",
            EventType.ECONOMIC_SHOCK,
            occurred_at=base + timedelta(hours=2),
            severity=EventSeverity.HIGH,
        ),
        make_event(
            "event-4",
            EventType.ECONOMIC_SHOCK,
            occurred_at=base + timedelta(hours=3),
            severity=EventSeverity.MEDIUM,
        ),
    ]

    engine = make_engine(events)

    transitions = engine.derive_all_transitions(
        "conflict-1"
    )

    assert len(transitions) == 2

    assert [
        transition.source_event_id
        for transition in transitions
    ] == [
        "event-1",
        "event-3",
    ]


def test_derive_all_transitions_returns_empty_for_no_transitions():
    event = make_event(
        "event-1",
        EventType.INFORMATION_EVENT,
    )

    engine = make_engine([event])

    transitions = engine.derive_all_transitions(
        "conflict-1"
    )

    assert transitions == []