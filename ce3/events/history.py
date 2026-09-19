from __future__ import annotations

from datetime import datetime

from .models import Event
from .store import EventStore


class EventHistory:
    """
    Chronological event-history interface for CE³.

    EventHistory does not create, modify, or interpret events.
    It provides deterministic temporal queries over the EventStore.
    """

    def __init__(self, store: EventStore) -> None:
        self.store = store

    def timeline(
        self,
        conflict_id: str,
    ) -> list[Event]:
        """
        Return the complete chronological event timeline
        for a conflict.
        """

        return self.store.for_conflict(conflict_id)

    def between(
        self,
        conflict_id: str,
        start: datetime,
        end: datetime,
    ) -> list[Event]:
        """
        Return events occurring within the inclusive time window.
        """

        return [
            event
            for event in self.store.for_conflict(conflict_id)
            if start <= event.occurred_at <= end
        ]

    def as_of(
        self,
        conflict_id: str,
        timestamp: datetime,
    ) -> list[Event]:
        """
        Return all events known to have occurred at or before
        the supplied timestamp.
        """

        return [
            event
            for event in self.store.for_conflict(conflict_id)
            if event.occurred_at <= timestamp
        ]

    def latest(
        self,
        conflict_id: str,
    ) -> Event | None:
        """
        Return the most recent event for a conflict.

        Returns None when the conflict has no recorded events.
        """

        events = self.store.for_conflict(conflict_id)

        if not events:
            return None

        return events[-1]

    def affecting_entity(
        self,
        conflict_id: str,
        entity: str,
    ) -> list[Event]:
        """
        Return events that explicitly identify the supplied
        entity as affected.
        """

        return [
            event
            for event in self.store.for_conflict(conflict_id)
            if entity in event.affected_entities
        ]