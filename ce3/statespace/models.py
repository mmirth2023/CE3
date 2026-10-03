from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class StateSpaceDimension(str, Enum):
    """
    Canonical dimensions used to describe a system's position
    within its observable state-space.
    """

    STABILITY = "stability"
    CAPACITY = "capacity"
    CONNECTIVITY = "connectivity"
    DEPENDENCY = "dependency"
    CONSTRAINT = "constraint"
    RESILIENCE = "resilience"
    ADAPTATION = "adaptation"
    INFORMATION = "information"
    ECONOMIC = "economic"
    FINANCIAL = "financial"
    POLITICAL = "political"
    PHYSICAL = "physical"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    OTHER = "other"


class StateSpacePosition(BaseModel):
    """
    Canonical representation of a system's position within
    an observable state-space.

    A position describes the system as observed at a point in
    time. It does not predict future states or establish that
    one state will necessarily follow another.
    """

    id: str
    state_time: datetime

    dimensions: dict[
        StateSpaceDimension,
        float,
    ] = Field(
        default_factory=dict,
    )

    labels: list[str] = Field(
        default_factory=list,
    )

    active_constraints: list[str] = Field(
        default_factory=list,
    )

    active_dependencies: list[str] = Field(
        default_factory=list,
    )

    active_shocks: list[str] = Field(
        default_factory=list,
    )

    propagation_path_ids: list[str] = Field(
        default_factory=list,
    )

    source_event_ids: list[str] = Field(
        default_factory=list,
    )

    source_observation_ids: list[str] = Field(
        default_factory=list,
    )

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    uncertainty: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )