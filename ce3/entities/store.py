from __future__ import annotations

from .models import Entity


class EntityStore:
    """
    In-memory canonical entity registry.

    The store guarantees unique canonical entity IDs and
    provides deterministic lookup by ID and canonical name.
    """

    def __init__(self) -> None:
        self._entities: dict[str, Entity] = {}

    def add(self, entity: Entity) -> Entity:
        if entity.id in self._entities:
            raise ValueError(
                f"Entity already exists: {entity.id}"
            )

        self._entities[entity.id] = entity

        return entity

    def get(self, entity_id: str) -> Entity:
        try:
            return self._entities[entity_id]
        except KeyError as exc:
            raise KeyError(
                f"Unknown entity: {entity_id}"
            ) from exc

    def all(self) -> list[Entity]:
        return list(self._entities.values())

    def by_type(
        self,
        entity_type,
    ) -> list[Entity]:
        return [
            entity
            for entity in self._entities.values()
            if entity.entity_type == entity_type
        ]

    def by_canonical_name(
        self,
        canonical_name: str,
    ) -> Entity | None:
        for entity in self._entities.values():
            if entity.canonical_name == canonical_name:
                return entity

        return None

    def __len__(self) -> int:
        return len(self._entities)