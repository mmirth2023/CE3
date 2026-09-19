from __future__ import annotations

from .models import Event


class EventStore:
    """
    In-memory event store for CE³.

    The store is intentionally simple at this stage.
    Persistence can be introduced later without changing
    the Event model or normalization layer.
    """

    def __init__(self) -> None:
        self._events: dict[str, Event] = {}

    def add(self, event: Event) -> None:
        """
        Add an event to the store.

        Event IDs are unique. Attempting to overwrite an existing
        event is treated as an error so event history cannot be
        silently mutated.
        """

        if event.id in self._events:
            raise ValueError(
                f"Event already exists: {event.id}"
            )

        self._events[event.id] = event

    def get(self, event_id: str) -> Event:
        """
        Retrieve an event by ID.
        """

        if event_id not in self._events:
            raise KeyError(
                f"Unknown event_id: {event_id}"
            )

        return self._events[event_id]

    def all(self) -> list[Event]:
        """
        Return all stored events ordered by occurrence time.
        """

        return sorted(
            self._events.values(),
            key=lambda event: event.occurred_at,
        )

    def for_conflict(
        self,
        conflict_id: str,
    ) -> list[Event]:
        """
        Return all events belonging to a conflict,
        ordered chronologically.
        """

        return sorted(
            (
                event
                for event in self._events.values()
                if event.conflict_id == conflict_id
            ),
            key=lambda event: event.occurred_at,
        )

    def __len__(self) -> int:
        return len(self._events)