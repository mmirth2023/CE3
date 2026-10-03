from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PropagationType(str, Enum):
    """
    Type of relationship through which a system change propagates.
    """

    DEPENDENCY = "dependency"
    SUPPLY = "supply"
    DEMAND = "demand"
    OWNERSHIP = "ownership"
    CONTROL = "control"
    INFRASTRUCTURE = "infrastructure"
    FINANCIAL = "financial"
    PHYSICAL = "physical"
    INFORMATION = "information"
    POLICY = "policy"
    MARKET = "market"
    OTHER = "other"


class PropagationStatus(str, Enum):
    """
    Descriptive status of an identified propagation relationship.
    """

    OBSERVED = "observed"
    SUPPORTED = "supported"
    STRUCTURALLY_POSSIBLE = "structurally_possible"
    CONTRADICTED = "contradicted"
    UNKNOWN = "unknown"


class PropagationPath(BaseModel):
    """
    Canonical representation of a potential or observed propagation
    path between system components.

    A propagation path describes how a change may be connected across
    entities, states, relationships, or dependencies.

    It does not by itself establish causality, forecast future outcomes,
    determine economic consequences, or identify a regime transition.
    """

    id: str

    source_id: str

    target_id: str

    propagation_type: PropagationType

    status: PropagationStatus = PropagationStatus.UNKNOWN

    identified_at: datetime

    valid_from: datetime | None = None

    valid_to: datetime | None = None

    strength: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    relationship_id: str | None = None

    dependency_id: str | None = None

    source_event_ids: list[str] = Field(
        default_factory=list
    )

    source_observation_ids: list[str] = Field(
        default_factory=list
    )

    intermediate_ids: list[str] = Field(
        default_factory=list
    )

    rationale: str = ""

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )