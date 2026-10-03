from __future__ import annotations

from datetime import datetime

from .models import Relationship


class RelationshipHistory:
    """
    Provides chronological and temporal access to canonical
    CE³ relationships.

    This layer describes how structural relationships are
    represented through time.

    It does not determine causality, propagation, systemic
    impact, or future outcomes.
    """

    def __init__(
        self,
        relationships: list[Relationship] | None = None,
    ) -> None:
        self._relationships: list[Relationship] = []

        for relationship in relationships or []:
            self.add(relationship)

    def add(
        self,
        relationship: Relationship,
    ) -> Relationship:
        if any(
            existing.id == relationship.id
            for existing in self._relationships
        ):
            raise ValueError(
                f"Relationship already exists: "
                f"{relationship.id}"
            )

        self._relationships.append(
            relationship
        )

        return relationship

    def all(self) -> list[Relationship]:
        return sorted(
            self._relationships,
            key=self._sort_key,
        )

    def between(
        self,
        start: datetime,
        end: datetime,
    ) -> list[Relationship]:
        return [
            relationship
            for relationship in self.all()
            if self._overlaps_period(
                relationship,
                start,
                end,
            )
        ]

    def as_of(
        self,
        timestamp: datetime,
    ) -> list[Relationship]:
        return [
            relationship
            for relationship in self.all()
            if self._valid_at(
                relationship,
                timestamp,
            )
        ]

    def latest(self) -> Relationship | None:
        relationships = self.all()

        if not relationships:
            return None

        return relationships[-1]

    def affecting_entity(
        self,
        entity_id: str,
    ) -> list[Relationship]:
        return [
            relationship
            for relationship in self.all()
            if (
                relationship.source_entity_id
                == entity_id
                or relationship.target_entity_id
                == entity_id
            )
        ]

    def __len__(self) -> int:
        return len(self._relationships)

    @staticmethod
    def _sort_key(
        relationship: Relationship,
    ) -> datetime:
        if relationship.valid_from is not None:
            return relationship.valid_from

        return datetime.min

    @staticmethod
    def _valid_at(
        relationship: Relationship,
        timestamp: datetime,
    ) -> bool:
        starts_before_or_at = (
            relationship.valid_from is None
            or relationship.valid_from <= timestamp
        )

        ends_after_or_at = (
            relationship.valid_to is None
            or timestamp <= relationship.valid_to
        )

        return (
            starts_before_or_at
            and ends_after_or_at
        )

    @staticmethod
    def _overlaps_period(
        relationship: Relationship,
        start: datetime,
        end: datetime,
    ) -> bool:
        relationship_start = (
            relationship.valid_from
            or datetime.min
        )

        relationship_end = (
            relationship.valid_to
            or datetime.max
        )

        return (
            relationship_start <= end
            and relationship_end >= start
        )