from __future__ import annotations

from ce3.entities.store import EntityStore
from ce3.relationships.models import Relationship


class EntityRelationshipIntegrity:
    """
    Validates that relationship endpoints exist in the
    canonical CE³ entity registry.

    This layer establishes structural integrity between
    entities and relationships.

    It does not perform entity resolution, infer missing
    relationships, determine causality, or model propagation.
    """

    def __init__(
        self,
        entity_store: EntityStore,
    ) -> None:
        self.entity_store = entity_store

    def validate_relationship(
        self,
        relationship: Relationship,
    ) -> Relationship:
        self._validate_source(relationship)
        self._validate_target(relationship)

        return relationship

    def _validate_source(
        self,
        relationship: Relationship,
    ) -> None:
        try:
            self.entity_store.get(
                relationship.source_entity_id
            )
        except KeyError as exc:
            raise ValueError(
                "Relationship references unknown "
                f"source entity: "
                f"{relationship.source_entity_id}"
            ) from exc

    def _validate_target(
        self,
        relationship: Relationship,
    ) -> None:
        try:
            self.entity_store.get(
                relationship.target_entity_id
            )
        except KeyError as exc:
            raise ValueError(
                "Relationship references unknown "
                f"target entity: "
                f"{relationship.target_entity_id}"
            ) from exc