from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TemporalTimestamps(BaseModel):
    """
    Canonical temporal metadata for a CE³ observation or event.

    CE³ distinguishes when something happened in the world from
    when information about it became available to the engine and
    when the engine incorporated that information into canonical
    state.
    """

    event_time: datetime | None = None
    published_time: datetime | None = None
    observed_time: datetime
    ingested_time: datetime
    state_time: datetime | None = None

    @property
    def information_latency_seconds(self) -> float | None:
        """
        Time between the world observation and CE³ ingestion.

        Returns None when event_time is unavailable.
        """

        if self.event_time is None:
            return None

        return (
            self.ingested_time - self.event_time
        ).total_seconds()

    @property
    def publication_latency_seconds(self) -> float | None:
        """
        Time between publication and CE³ ingestion.

        Returns None when published_time is unavailable.
        """

        if self.published_time is None:
            return None

        return (
            self.ingested_time - self.published_time
        ).total_seconds()