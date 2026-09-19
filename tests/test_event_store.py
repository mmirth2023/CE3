from datetime import datetime, timedelta, timezone

import pytest

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
        confidence=0.8,
    )


def test_event_can_be_stored_and_retrieved():
    store = EventStore()

    now = datetime.now(timezone.utc)

    event = make_event(
        "E1",
        "CONFLICT-1",
        now,
    )

    store.add(event)

    assert len(store) == 1

    retrieved = store.get("E1")

    assert retrieved.id == "E1"
    assert retrieved.conflict_id == "CONFLICT-1"


def test_event_ids_cannot_be_overwritten():
    store = EventStore()

    now = datetime.now(timezone.utc)

    event = make_event(
        "E1",
        "CONFLICT-1",
        now,
    )

    store.add(event)

    with pytest.raises(ValueError):
        store.add(event)


def test_events_are_returned_in_chronological_order():
    store = EventStore()

    now = datetime.now(timezone.utc)

    later = make_event(
        "E2",
        "CONFLICT-1",
        now + timedelta(hours=2),
    )

    earlier = make_event(
        "E1",
        "CONFLICT-1",
        now,
    )

    store.add(later)
    store.add(earlier)

    events = store.all()

    assert [event.id for event in events] == [
        "E1",
        "E2",
    ]


def test_events_can_be_filtered_by_conflict():
    store = EventStore()

    now = datetime.now(timezone.utc)

    store.add(
        make_event(
            "E1",
            "CONFLICT-1",
            now,
        )
    )

    store.add(
        make_event(
            "E2",
            "CONFLICT-2",
            now + timedelta(hours=1),
        )
    )

    store.add(
        make_event(
            "E3",
            "CONFLICT-1",
            now + timedelta(hours=2),
        )
    )

    events = store.for_conflict("CONFLICT-1")

    assert [event.id for event in events] == [
        "E1",
        "E3",
    ]


def test_unknown_event_raises_key_error():
    store = EventStore()

    with pytest.raises(KeyError):
        store.get("UNKNOWN")