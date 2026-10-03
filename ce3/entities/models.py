from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    PERSON = "person"
    COMPANY = "company"
    GOVERNMENT = "government"
    FACILITY = "facility"
    VESSEL = "vessel"
    AIRPORT = "airport"
    PORT = "port"
    COMMODITY = "commodity"
    SECURITY = "security"
    CURRENCY = "currency"
    INDEX = "index"
    COUNTRY = "country"
    REGION = "region"
    INFRASTRUCTURE = "infrastructure"


class Entity(BaseModel):
    """
    Canonical identity for an entity represented in the
    CE³ world model.

    An Entity is an identity object, not a state snapshot.
    Its changing properties belong in the temporal state
    system rather than being overwritten here.
    """

    id: str

    entity_type: EntityType

    canonical_name: str

    aliases: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )