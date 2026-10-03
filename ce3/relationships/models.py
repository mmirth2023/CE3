from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    OWNS = "owns"
    OPERATES = "operates"
    LOCATED_AT = "located_at"
    PRODUCES = "produces"
    EXPORTS = "exports"
    IMPORTS = "imports"
    CONTROLS = "controls"
    DEPENDS_ON = "depends_on"
    SUPPLIES = "supplies"
    COMPETES_WITH = "competes_with"
    EXPOSED_TO = "exposed_to"


class Relationship(BaseModel):
    """
    Canonical relationship between two CE³ entities.

    A relationship represents a structural connection in the
    world model. It is not itself a state snapshot and does
    not determine causality or propagation.
    """

    id: str

    relationship_type: RelationshipType

    source_entity_id: str

    target_entity_id: str

    valid_from: datetime | None = None

    valid_to: datetime | None = None

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )