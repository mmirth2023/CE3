import pytest

from ce3.entities.models import Entity, EntityType
from ce3.entities.store import EntityStore
from ce3.integrity.engine import EntityRelationshipIntegrity
from ce3.relationships.models import (
    Relationship,
    RelationshipType,
)


def make_entity_store() -> EntityStore:
    store = EntityStore()

    store.add(
        Entity(
            id="COMP-001",
            entity_type=EntityType.COMPANY,
            canonical_name="Example Company",
        )
    )

    store.add(
        Entity(
            id="FAC-001",
            entity_type=EntityType.FACILITY,
            canonical_name="Example Facility",
        )
    )

    return store


def make_relationship() -> Relationship:
    return Relationship(
        id="REL-001",
        relationship_type=RelationshipType.OPERATES,
        source_entity_id="COMP-001",
        target_entity_id="FAC-001",
        confidence=0.9,
    )


def test_integrity_accepts_relationship_with_existing_entities():
    entity_store = make_entity_store()

    integrity = EntityRelationshipIntegrity(
        entity_store
    )

    relationship = make_relationship()

    validated = integrity.validate_relationship(
        relationship
    )

    assert validated is relationship


def test_integrity_rejects_unknown_source_entity():
    entity_store = EntityStore()

    entity_store.add(
        Entity(
            id="FAC-001",
            entity_type=EntityType.FACILITY,
            canonical_name="Example Facility",
        )
    )

    integrity = EntityRelationshipIntegrity(
        entity_store
    )

    relationship = make_relationship()

    with pytest.raises(
        ValueError,
        match="unknown source entity",
    ):
        integrity.validate_relationship(
            relationship
        )


def test_integrity_rejects_unknown_target_entity():
    entity_store = EntityStore()

    entity_store.add(
        Entity(
            id="COMP-001",
            entity_type=EntityType.COMPANY,
            canonical_name="Example Company",
        )
    )

    integrity = EntityRelationshipIntegrity(
        entity_store
    )

    relationship = make_relationship()

    with pytest.raises(
        ValueError,
        match="unknown target entity",
    ):
        integrity.validate_relationship(
            relationship
        )


def test_integrity_rejects_unknown_source_and_target():
    entity_store = EntityStore()

    integrity = EntityRelationshipIntegrity(
        entity_store
    )

    relationship = make_relationship()

    with pytest.raises(
        ValueError,
        match="unknown source entity",
    ):
        integrity.validate_relationship(
            relationship
        )


def test_integrity_does_not_modify_relationship():
    entity_store = make_entity_store()

    integrity = EntityRelationshipIntegrity(
        entity_store
    )

    relationship = make_relationship()

    before = relationship.model_dump()

    integrity.validate_relationship(
        relationship
    )

    after = relationship.model_dump()

    assert after == before