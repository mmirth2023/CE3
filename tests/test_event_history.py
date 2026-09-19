from datetime import datetime, timedelta, timezone

from ce3.events.history import EventHistory
from ce3.events.models import (
    Event,
    EventSeverity,
    EventType,
)
from ce3.events.store import EventStore


def make_event(
    event_id: str,
    conflict_id: str,
    occurred_at: datetime,
    affected_entities: list[str] | None = None,
) -> Event:
    return Event(
        id=event_id,
        conflict_id=conflict_id,
        event_type=EventType.FACILITY_DAMAGE,
        occurred_at=occurred_at,
        detected_at=occurred_at,
        title=f"Event {event_id}",
        description=f"Description for {event_id}",
        severity=EventSeverity.MEDIUM,
        affected_entities=affected_entities or [],
        confidence=0.8,
    )


def test_timeline_returns_chronological_events():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E2",
            "C1",
            now + timedelta(hours=2),
        )
    )

    store.add(
        make_event(
            "E1",
            "C1",
            now,
        )
    )

    history = EventHistory(store)

    events = history.timeline("C1")

    assert [event.id for event in events] == [
        "E1",
        "E2",
    ]


def test_between_returns_events_inside_time_window():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "C1",
            now,
        )
    )

    store.add(
        make_event(
            "E2",
            "C1",
            now + timedelta(hours=1),
        )
    )

    store.add(
        make_event(
            "E3",
            "C1",
            now + timedelta(hours=2),
        )
    )

    history = EventHistory(store)

    events = history.between(
        "C1",
        now + timedelta(minutes=30),
        now + timedelta(hours=1, minutes=30),
    )

    assert [event.id for event in events] == [
        "E2",
    ]


def test_as_of_reconstructs_historical_event_set():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "C1",
            now,
        )
    )

    store.add(
        make_event(
            "E2",
            "C1",
            now + timedelta(hours=1),
        )
    )

    store.add(
        make_event(
            "E3",
            "C1",
            now + timedelta(hours=2),
        )
    )

    history = EventHistory(store)

    events = history.as_of(
        "C1",
        now + timedelta(hours=1),
    )

    assert [event.id for event in events] == [
        "E1",
        "E2",
    ]


def test_latest_returns_most_recent_event():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "C1",
            now,
        )
    )

    store.add(
        make_event(
            "E2",
            "C1",
            now + timedelta(hours=1),
        )
    )

    history = EventHistory(store)

    latest = history.latest("C1")

    assert latest is not None
    assert latest.id == "E2"


def test_latest_returns_none_for_empty_conflict():
    store = EventStore()

    history = EventHistory(store)

    assert history.latest("EMPTY") is None


def test_events_can_be_filtered_by_affected_entity():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "C1",
            now,
            affected_entities=["Facility X"],
        )
    )

    store.add(
        make_event(
            "E2",
            "C1",
            now + timedelta(hours=1),
            affected_entities=["Facility Y"],
        )
    )

    store.add(
        make_event(
            "E3",
            "C1",
            now + timedelta(hours=2),
            affected_entities=["Facility X"],
        )
    )

    history = EventHistory(store)

    events = history.affecting_entity(
        "C1",
        "Facility X",
    )

    assert [event.id for event in events] == [
        "E1",
        "E3",
    ]