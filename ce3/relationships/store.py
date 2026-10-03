from __future__ import annotations

from datetime import datetime

from .models import Relationship, RelationshipType


class RelationshipStore:
    """
    In-memory canonical relationship registry.

    Relationships are stored independently from entities.
    Entity IDs referenced by relationships are resolved
    against the entity registry at a higher layer.

    Relationships may also carry temporal validity, allowing
    the store to reconstruct which structural connections
    existed at a given point in time.
    """

    def __init__(self) -> None:
        self._relationships: dict[str, Relationship] = {}

    def add(
        self,
        relationship: Relationship,
    ) -> Relationship:
        if relationship.id in self._relationships:
            raise ValueError(
                f"Relationship already exists: "
                f"{relationship.id}"
            )

        self._relationships[
            relationship.id
        ] = relationship

        return relationship

    def get(
        self,
        relationship_id: str,
    ) -> Relationship:
        try:
            return self._relationships[
                relationship_id
            ]
        except KeyError as exc:
            raise KeyError(
                f"Unknown relationship: "
                f"{relationship_id}"
            ) from exc

    def all(self) -> list[Relationship]:
        return list(
            self._relationships.values()
        )

    def by_type(
        self,
        relationship_type: RelationshipType,
    ) -> list[Relationship]:
        return [
            relationship
            for relationship in self._relationships.values()
            if relationship.relationship_type
            == relationship_type
        ]

    def from_entity(
        self,
        entity_id: str,
    ) -> list[Relationship]:
        return [
            relationship
            for relationship in self._relationships.values()
            if relationship.source_entity_id
            == entity_id
        ]

    def to_entity(
        self,
        entity_id: str,
    ) -> list[Relationship]:
        return [
            relationship
            for relationship in self._relationships.values()
            if relationship.target_entity_id
            == entity_id
        ]

    def between_entities(
        self,
        source_entity_id: str,
        target_entity_id: str,
    ) -> list[Relationship]:
        return [
            relationship
            for relationship in self._relationships.values()
            if (
                relationship.source_entity_id
                == source_entity_id
                and relationship.target_entity_id
                == target_entity_id
            )
        ]

    def valid_at(
        self,
        timestamp: datetime,
    ) -> list[Relationship]:
        """
        Return relationships that were valid at the
        specified point in time.

        A relationship is valid at timestamp T when:

            valid_from <= T

        and:

            valid_to is None
            or
            T <= valid_to

        Relationships without a valid_from timestamp are
        treated as having no known lower temporal boundary.
        """

        return [
            relationship
            for relationship in self._relationships.values()
            if (
                (
                    relationship.valid_from is None
                    or relationship.valid_from <= timestamp
                )
                and
                (
                    relationship.valid_to is None
                    or timestamp <= relationship.valid_to
                )
            )
        ]

    def __len__(self) -> int:
        return len(self._relationships)