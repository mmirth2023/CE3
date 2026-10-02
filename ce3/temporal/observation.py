from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .timestamps import TemporalTimestamps


class TemporalObservation(BaseModel):
    """
    An observation represented explicitly within CE³'s temporal core.

    This object does not determine whether an observation is true.
    It preserves what was observed, by whom, what entities were
    involved, and the relevant temporal clocks.
    """

    id: str

    source_id: str

    timestamps: TemporalTimestamps

    content: str

    entities: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)