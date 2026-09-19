from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from .models import (
    ActivityLevel,
    ControlStatus,
    DiplomaticStatus,
    EconomicStatus,
    HumanitarianStatus,
    PoliticalStatus,
)


class StateTransition(BaseModel):
    """
    Represents a change in conflict state caused by a specific event.

    StateTransition is historical evidence about how derived state
    changed. It does not replace ConflictState.
    """

    conflict_id: str
    entity: str | None = None

    dimension: str

    occurred_at: datetime

    previous_value: (
        ControlStatus
        | ActivityLevel
        | DiplomaticStatus
        | PoliticalStatus
        | EconomicStatus
        | HumanitarianStatus
        | None
    ) = None

    new_value: (
        ControlStatus
        | ActivityLevel
        | DiplomaticStatus
        | PoliticalStatus
        | EconomicStatus
        | HumanitarianStatus
        | None
    ) = None

    source_event_id: str