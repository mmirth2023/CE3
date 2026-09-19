from datetime import datetime, timedelta, timezone

from ce3.state.models import ControlStatus
from ce3.state.transitions import StateTransition
from ce3.state.transition_history import TransitionHistory

from ce3.state.models import (
    ActivityLevel,
    DiplomaticStatus,
    EconomicStatus,
    HumanitarianStatus,
    PoliticalStatus,
)


def make_transition(
    event_id: str,
    occurred_at: datetime,
    *,
    entity: str = "Facility X",
    previous: ControlStatus = ControlStatus.UNKNOWN,
    new: ControlStatus = ControlStatus.CONTROLLED,
    conflict_id: str = "C1",
) -> StateTransition:
    return StateTransition(
        conflict_id=conflict_id,
        entity=entity,
        dimension="territorial",
        occurred_at=occurred_at,
        previous_value=previous,
        new_value=new,
        source_event_id=event_id,
    )


def test_timeline_returns_transitions_chronologically():
    now = datetime.now(timezone.utc)

    later = make_transition(
        "E2",
        now + timedelta(hours=2),
        previous=ControlStatus.CONTROLLED,
        new=ControlStatus.LOST,
    )

    earlier = make_transition(
        "E1",
        now,
        previous=ControlStatus.UNKNOWN,
        new=ControlStatus.CONTROLLED,
    )

    history = TransitionHistory([later, earlier])

    transitions = history.timeline("C1")

    assert [t.source_event_id for t in transitions] == [
        "E1",
        "E2",
    ]


def test_between_returns_inclusive_time_window():
    now = datetime.now(timezone.utc)

    e1 = make_transition("E1", now)
    e2 = make_transition(
        "E2",
        now + timedelta(hours=1),
        previous=ControlStatus.CONTROLLED,
        new=ControlStatus.CONTESTED,
    )
    e3 = make_transition(
        "E3",
        now + timedelta(hours=2),
        previous=ControlStatus.CONTESTED,
        new=ControlStatus.LOST,
    )

    history = TransitionHistory([e1, e2, e3])

    transitions = history.between(
        "C1",
        now + timedelta(minutes=30),
        now + timedelta(hours=1),
    )

    assert [t.source_event_id for t in transitions] == ["E2"]


def test_affecting_entity_filters_correctly():
    now = datetime.now(timezone.utc)

    e1 = make_transition(
        "E1",
        now,
        entity="Facility X",
    )

    e2 = make_transition(
        "E2",
        now + timedelta(hours=1),
        entity="Facility Y",
    )

    history = TransitionHistory([e1, e2])

    transitions = history.affecting_entity(
        "C1",
        "Facility X",
    )

    assert [t.source_event_id for t in transitions] == ["E1"]


def test_latest_returns_latest_transition():
    now = datetime.now(timezone.utc)

    e1 = make_transition("E1", now)

    e2 = make_transition(
        "E2",
        now + timedelta(hours=1),
        previous=ControlStatus.CONTROLLED,
        new=ControlStatus.CONTESTED,
    )

    history = TransitionHistory([e1, e2])

    latest = history.latest("C1")

    assert latest is not None
    assert latest.source_event_id == "E2"
    assert latest.new_value == ControlStatus.CONTESTED


def test_latest_can_be_limited_to_entity():
    now = datetime.now(timezone.utc)

    e1 = make_transition(
        "E1",
        now,
        entity="Facility X",
    )

    e2 = make_transition(
        "E2",
        now + timedelta(hours=1),
        entity="Facility Y",
    )

    e3 = make_transition(
        "E3",
        now + timedelta(hours=2),
        entity="Facility X",
        previous=ControlStatus.CONTROLLED,
        new=ControlStatus.LOST,
    )

    history = TransitionHistory([e1, e2, e3])

    latest = history.latest(
        "C1",
        entity="Facility X",
    )

    assert latest is not None
    assert latest.source_event_id == "E3"


def test_latest_returns_none_when_no_transitions_exist():
    history = TransitionHistory([])

    assert history.latest("C1") is None


def test_caused_by_event_returns_matching_transitions():
    now = datetime.now(timezone.utc)

    e1 = make_transition("E1", now)

    e2 = make_transition(
        "E2",
        now + timedelta(hours=1),
        entity="Facility Y",
    )

    history = TransitionHistory([e1, e2])

    transitions = history.caused_by_event(
        "C1",
        "E2",
    )

    assert len(transitions) == 1
    assert transitions[0].source_event_id == "E2"
    assert transitions[0].entity == "Facility Y"


def test_reconstruct_state_at_returns_state_at_requested_time():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-1",
            dimension="military",
            occurred_at=base,
            previous_value=ActivityLevel.UNKNOWN,
            new_value=ActivityLevel.MEDIUM,
            source_event_id="event-1",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="economic",
            occurred_at=base + timedelta(hours=1),
            previous_value=EconomicStatus.UNKNOWN,
            new_value=EconomicStatus.PRESSURED,
            source_event_id="event-2",
        ),
    ]

    history = TransitionHistory(transitions)

    state = history.reconstruct_state_at(
        "conflict-1",
        base + timedelta(minutes=30),
    )

    assert state.conflict_id == "conflict-1"
    assert state.as_of == base + timedelta(minutes=30)

    assert state.military.activity_level == ActivityLevel.MEDIUM
    assert state.economic == EconomicStatus.UNKNOWN


def test_reconstruct_state_at_applies_all_transitions_up_to_timestamp():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-1",
            dimension="military",
            occurred_at=base,
            previous_value=ActivityLevel.UNKNOWN,
            new_value=ActivityLevel.MEDIUM,
            source_event_id="event-1",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="economic",
            occurred_at=base + timedelta(hours=1),
            previous_value=EconomicStatus.UNKNOWN,
            new_value=EconomicStatus.DISRUPTED,
            source_event_id="event-2",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="humanitarian",
            occurred_at=base + timedelta(hours=2),
            previous_value=HumanitarianStatus.UNKNOWN,
            new_value=HumanitarianStatus.SEVERE,
            source_event_id="event-3",
        ),
    ]

    history = TransitionHistory(transitions)

    state = history.reconstruct_state_at(
        "conflict-1",
        base + timedelta(hours=2),
    )

    assert state.military.activity_level == ActivityLevel.MEDIUM
    assert state.economic == EconomicStatus.DISRUPTED
    assert state.humanitarian == HumanitarianStatus.SEVERE


def test_reconstruct_state_at_ignores_future_transitions():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-1",
            dimension="military",
            occurred_at=base,
            previous_value=ActivityLevel.UNKNOWN,
            new_value=ActivityLevel.MEDIUM,
            source_event_id="event-1",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="economic",
            occurred_at=base + timedelta(hours=2),
            previous_value=EconomicStatus.UNKNOWN,
            new_value=EconomicStatus.CRITICAL,
            source_event_id="event-2",
        ),
    ]

    history = TransitionHistory(transitions)

    state = history.reconstruct_state_at(
        "conflict-1",
        base + timedelta(hours=1),
    )

    assert state.military.activity_level == ActivityLevel.MEDIUM
    assert state.economic == EconomicStatus.UNKNOWN


def test_reconstruct_state_at_returns_unknown_state_when_no_transitions_exist():
    base = datetime.now(timezone.utc)

    history = TransitionHistory([])

    state = history.reconstruct_state_at(
        "conflict-1",
        base,
    )

    assert state.conflict_id == "conflict-1"
    assert state.as_of == base

    assert state.military.activity_level == ActivityLevel.UNKNOWN
    assert state.diplomatic == DiplomaticStatus.UNKNOWN
    assert state.political == PoliticalStatus.UNKNOWN
    assert state.economic == EconomicStatus.UNKNOWN
    assert state.humanitarian == HumanitarianStatus.UNKNOWN
    assert state.territorial == []


def test_reconstruct_state_at_preserves_multiple_territorial_entities():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-1",
            entity="area-1",
            dimension="territorial",
            occurred_at=base,
            previous_value=ControlStatus.UNKNOWN,
            new_value=ControlStatus.CONTROLLED,
            source_event_id="event-1",
        ),
        StateTransition(
            conflict_id="conflict-1",
            entity="area-2",
            dimension="territorial",
            occurred_at=base + timedelta(hours=1),
            previous_value=ControlStatus.UNKNOWN,
            new_value=ControlStatus.CONTESTED,
            source_event_id="event-2",
        ),
    ]

    history = TransitionHistory(transitions)

    state = history.reconstruct_state_at(
        "conflict-1",
        base + timedelta(hours=1),
    )

    assert len(state.territorial) == 2

    area_1 = next(
        item
        for item in state.territorial
        if item.entity == "area-1"
    )

    area_2 = next(
        item
        for item in state.territorial
        if item.entity == "area-2"
    )

    assert area_1.status == ControlStatus.CONTROLLED
    assert area_2.status == ControlStatus.CONTESTED


def test_reconstruct_state_at_uses_latest_territorial_transition_per_entity():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-1",
            entity="area-1",
            dimension="territorial",
            occurred_at=base,
            previous_value=ControlStatus.UNKNOWN,
            new_value=ControlStatus.CONTROLLED,
            source_event_id="event-1",
        ),
        StateTransition(
            conflict_id="conflict-1",
            entity="area-1",
            dimension="territorial",
            occurred_at=base + timedelta(hours=1),
            previous_value=ControlStatus.CONTROLLED,
            new_value=ControlStatus.CONTESTED,
            source_event_id="event-2",
        ),
    ]

    history = TransitionHistory(transitions)

    state = history.reconstruct_state_at(
        "conflict-1",
        base + timedelta(hours=1),
    )

    assert len(state.territorial) == 1
    assert state.territorial[0].entity == "area-1"
    assert state.territorial[0].status == ControlStatus.CONTESTED


def test_reconstruct_state_at_records_source_event_ids():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-1",
            dimension="military",
            occurred_at=base,
            previous_value=ActivityLevel.UNKNOWN,
            new_value=ActivityLevel.MEDIUM,
            source_event_id="event-1",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="economic",
            occurred_at=base + timedelta(hours=1),
            previous_value=EconomicStatus.UNKNOWN,
            new_value=EconomicStatus.DISRUPTED,
            source_event_id="event-2",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="humanitarian",
            occurred_at=base + timedelta(hours=2),
            previous_value=HumanitarianStatus.UNKNOWN,
            new_value=HumanitarianStatus.SEVERE,
            source_event_id="event-3",
        ),
    ]

    history = TransitionHistory(transitions)

    state = history.reconstruct_state_at(
        "conflict-1",
        base + timedelta(hours=2),
    )

    assert state.source_event_ids == [
        "event-1",
        "event-2",
        "event-3",
    ]


def test_reconstruct_state_at_ignores_transitions_from_other_conflicts():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-2",
            dimension="military",
            occurred_at=base,
            previous_value=ActivityLevel.UNKNOWN,
            new_value=ActivityLevel.CRITICAL,
            source_event_id="event-other",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="economic",
            occurred_at=base + timedelta(hours=1),
            previous_value=EconomicStatus.UNKNOWN,
            new_value=EconomicStatus.PRESSURED,
            source_event_id="event-own",
        ),
    ]

    history = TransitionHistory(transitions)

    state = history.reconstruct_state_at(
        "conflict-1",
        base + timedelta(hours=1),
    )

    assert state.military.activity_level == ActivityLevel.UNKNOWN
    assert state.economic == EconomicStatus.PRESSURED

    assert state.source_event_ids == [
        "event-own",
    ]


def test_evolution_returns_states_in_chronological_order():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-1",
            dimension="economic",
            occurred_at=base + timedelta(hours=2),
            previous_value=EconomicStatus.PRESSURED,
            new_value=EconomicStatus.DISRUPTED,
            source_event_id="event-2",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="military",
            occurred_at=base,
            previous_value=ActivityLevel.UNKNOWN,
            new_value=ActivityLevel.MEDIUM,
            source_event_id="event-1",
        ),
    ]

    history = TransitionHistory(transitions)

    evolution = history.evolution("conflict-1")

    assert len(evolution) == 2

    assert [
        state.as_of
        for state in evolution
    ] == [
        base,
        base + timedelta(hours=2),
    ]


def test_evolution_applies_transitions_cumulatively():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-1",
            dimension="military",
            occurred_at=base,
            previous_value=ActivityLevel.UNKNOWN,
            new_value=ActivityLevel.MEDIUM,
            source_event_id="event-1",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="economic",
            occurred_at=base + timedelta(hours=1),
            previous_value=EconomicStatus.UNKNOWN,
            new_value=EconomicStatus.PRESSURED,
            source_event_id="event-2",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="humanitarian",
            occurred_at=base + timedelta(hours=2),
            previous_value=HumanitarianStatus.UNKNOWN,
            new_value=HumanitarianStatus.SEVERE,
            source_event_id="event-3",
        ),
    ]

    history = TransitionHistory(transitions)

    evolution = history.evolution("conflict-1")

    assert len(evolution) == 3

    assert evolution[0].military.activity_level == (
        ActivityLevel.MEDIUM
    )
    assert evolution[0].economic == EconomicStatus.UNKNOWN

    assert evolution[1].military.activity_level == (
        ActivityLevel.MEDIUM
    )
    assert evolution[1].economic == (
        EconomicStatus.PRESSURED
    )

    assert evolution[2].military.activity_level == (
        ActivityLevel.MEDIUM
    )
    assert evolution[2].economic == (
        EconomicStatus.PRESSURED
    )
    assert evolution[2].humanitarian == (
        HumanitarianStatus.SEVERE
    )


def test_evolution_preserves_state_provenance():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-1",
            dimension="military",
            occurred_at=base,
            previous_value=ActivityLevel.UNKNOWN,
            new_value=ActivityLevel.MEDIUM,
            source_event_id="event-1",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="economic",
            occurred_at=base + timedelta(hours=1),
            previous_value=EconomicStatus.UNKNOWN,
            new_value=EconomicStatus.DISRUPTED,
            source_event_id="event-2",
        ),
    ]

    history = TransitionHistory(transitions)

    evolution = history.evolution("conflict-1")

    assert evolution[0].source_event_ids == [
        "event-1",
    ]

    assert evolution[1].source_event_ids == [
        "event-1",
        "event-2",
    ]


def test_evolution_ignores_other_conflicts():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-2",
            dimension="military",
            occurred_at=base,
            previous_value=ActivityLevel.UNKNOWN,
            new_value=ActivityLevel.CRITICAL,
            source_event_id="other-event",
        ),
        StateTransition(
            conflict_id="conflict-1",
            dimension="economic",
            occurred_at=base + timedelta(hours=1),
            previous_value=EconomicStatus.UNKNOWN,
            new_value=EconomicStatus.PRESSURED,
            source_event_id="own-event",
        ),
    ]

    history = TransitionHistory(transitions)

    evolution = history.evolution("conflict-1")

    assert len(evolution) == 1

    assert evolution[0].economic == (
        EconomicStatus.PRESSURED
    )

    assert evolution[0].military.activity_level == (
        ActivityLevel.UNKNOWN
    )

    assert evolution[0].source_event_ids == [
        "own-event",
    ]


def test_evolution_returns_empty_for_conflict_without_transitions():
    base = datetime.now(timezone.utc)

    transitions = [
        StateTransition(
            conflict_id="conflict-2",
            dimension="military",
            occurred_at=base,
            previous_value=ActivityLevel.UNKNOWN,
            new_value=ActivityLevel.MEDIUM,
            source_event_id="event-1",
        ),
    ]

    history = TransitionHistory(transitions)

    assert history.evolution("conflict-1") == []

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