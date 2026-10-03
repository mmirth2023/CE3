from datetime import datetime, timezone

import pytest

from ce3.relationships.models import Relationship, RelationshipType
from ce3.relationships.store import RelationshipStore


def make_relationship() -> Relationship:
    return Relationship(
        id="REL-001",
        relationship_type=RelationshipType.OPERATES,
        source_entity_id="COMP-001",
        target_entity_id="FAC-001",
        valid_from=datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        confidence=0.9,
    )


def test_relationship_preserves_canonical_structure():
    relationship = make_relationship()

    assert relationship.id == "REL-001"

    assert relationship.relationship_type == (
        RelationshipType.OPERATES
    )

    assert relationship.source_entity_id == "COMP-001"
    assert relationship.target_entity_id == "FAC-001"

    assert relationship.valid_from == datetime(
        2020,
        1,
        1,
        tzinfo=timezone.utc,
    )

    assert relationship.valid_to is None
    assert relationship.confidence == 0.9


def test_relationship_types_are_explicit():
    assert RelationshipType.OWNS.value == "owns"
    assert RelationshipType.OPERATES.value == "operates"
    assert RelationshipType.LOCATED_AT.value == "located_at"
    assert RelationshipType.PRODUCES.value == "produces"
    assert RelationshipType.EXPORTS.value == "exports"
    assert RelationshipType.IMPORTS.value == "imports"
    assert RelationshipType.CONTROLS.value == "controls"
    assert RelationshipType.DEPENDS_ON.value == "depends_on"
    assert RelationshipType.SUPPLIES.value == "supplies"
    assert RelationshipType.COMPETES_WITH.value == "competes_with"
    assert RelationshipType.EXPOSED_TO.value == "exposed_to"


def test_relationship_supports_temporal_validity():
    relationship = Relationship(
        id="REL-002",
        relationship_type=RelationshipType.OWNS,
        source_entity_id="COMP-001",
        target_entity_id="FAC-001",
        valid_from=datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        valid_to=datetime(
            2025,
            12,
            31,
            tzinfo=timezone.utc,
        ),
        confidence=0.95,
    )

    assert relationship.valid_from is not None
    assert relationship.valid_to is not None

    assert relationship.valid_from < relationship.valid_to


def test_relationship_supports_metadata():
    relationship = Relationship(
        id="REL-003",
        relationship_type=RelationshipType.SUPPLIES,
        source_entity_id="COMP-001",
        target_entity_id="FAC-001",
        confidence=0.8,
        metadata={
            "source": "official_filing",
            "jurisdiction": "Kenya",
        },
    )

    assert relationship.metadata == {
        "source": "official_filing",
        "jurisdiction": "Kenya",
    }


def test_relationship_rejects_invalid_confidence():
    with pytest.raises(ValueError):
        Relationship(
            id="REL-004",
            relationship_type=RelationshipType.CONTROLS,
            source_entity_id="COMP-001",
            target_entity_id="FAC-001",
            confidence=1.1,
        )


def test_relationship_rejects_negative_confidence():
    with pytest.raises(ValueError):
        Relationship(
            id="REL-005",
            relationship_type=RelationshipType.CONTROLS,
            source_entity_id="COMP-001",
            target_entity_id="FAC-001",
            confidence=-0.1,
        )


def test_relationship_store_adds_and_retrieves_relationship():
    store = RelationshipStore()
    relationship = make_relationship()

    stored = store.add(relationship)

    assert stored is relationship
    assert store.get("REL-001") is relationship
    assert len(store) == 1


def test_relationship_store_rejects_duplicate_ids():
    store = RelationshipStore()

    store.add(make_relationship())

    with pytest.raises(ValueError):
        store.add(make_relationship())


def test_relationship_store_lists_all_relationships():
    store = RelationshipStore()

    first = make_relationship()

    second = Relationship(
        id="REL-002",
        relationship_type=RelationshipType.OWNS,
        source_entity_id="COMP-001",
        target_entity_id="FAC-002",
        confidence=0.9,
    )

    store.add(first)
    store.add(second)

    assert store.all() == [
        first,
        second,
    ]


def test_relationship_store_filters_by_type():
    store = RelationshipStore()

    operates = make_relationship()

    owns = Relationship(
        id="REL-002",
        relationship_type=RelationshipType.OWNS,
        source_entity_id="COMP-001",
        target_entity_id="FAC-002",
        confidence=0.9,
    )

    store.add(operates)
    store.add(owns)

    assert store.by_type(
        RelationshipType.OPERATES
    ) == [
        operates
    ]

    assert store.by_type(
        RelationshipType.OWNS
    ) == [
        owns
    ]


def test_relationship_store_finds_relationships_from_entity():
    store = RelationshipStore()

    first = make_relationship()

    second = Relationship(
        id="REL-002",
        relationship_type=RelationshipType.OWNS,
        source_entity_id="COMP-001",
        target_entity_id="FAC-002",
        confidence=0.9,
    )

    third = Relationship(
        id="REL-003",
        relationship_type=RelationshipType.SUPPLIES,
        source_entity_id="COMP-002",
        target_entity_id="FAC-001",
        confidence=0.9,
    )

    store.add(first)
    store.add(second)
    store.add(third)

    assert store.from_entity("COMP-001") == [
        first,
        second,
    ]


def test_relationship_store_finds_relationships_to_entity():
    store = RelationshipStore()

    first = make_relationship()

    second = Relationship(
        id="REL-002",
        relationship_type=RelationshipType.SUPPLIES,
        source_entity_id="COMP-002",
        target_entity_id="FAC-001",
        confidence=0.9,
    )

    third = Relationship(
        id="REL-003",
        relationship_type=RelationshipType.OWNS,
        source_entity_id="COMP-001",
        target_entity_id="FAC-002",
        confidence=0.9,
    )

    store.add(first)
    store.add(second)
    store.add(third)

    assert store.to_entity("FAC-001") == [
        first,
        second,
    ]


def test_relationship_store_finds_relationships_between_entities():
    store = RelationshipStore()

    first = make_relationship()

    second = Relationship(
        id="REL-002",
        relationship_type=RelationshipType.OWNS,
        source_entity_id="COMP-001",
        target_entity_id="FAC-001",
        confidence=0.9,
    )

    third = Relationship(
        id="REL-003",
        relationship_type=RelationshipType.SUPPLIES,
        source_entity_id="COMP-002",
        target_entity_id="FAC-001",
        confidence=0.9,
    )

    store.add(first)
    store.add(second)
    store.add(third)

    assert store.between_entities(
        "COMP-001",
        "FAC-001",
    ) == [
        first,
        second,
    ]


def test_relationship_store_raises_for_unknown_id():
    store = RelationshipStore()

    with pytest.raises(KeyError):
        store.get("UNKNOWN")

def test_relationship_store_finds_relationships_valid_at_timestamp():
    store = RelationshipStore()

    active = Relationship(
        id="REL-006",
        relationship_type=RelationshipType.OPERATES,
        source_entity_id="COMP-001",
        target_entity_id="FAC-001",
        valid_from=datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        valid_to=datetime(
            2025,
            12,
            31,
            tzinfo=timezone.utc,
        ),
        confidence=0.9,
    )

    inactive = Relationship(
        id="REL-007",
        relationship_type=RelationshipType.OWNS,
        source_entity_id="COMP-001",
        target_entity_id="FAC-002",
        valid_from=datetime(
            2010,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        valid_to=datetime(
            2015,
            12,
            31,
            tzinfo=timezone.utc,
        ),
        confidence=0.9,
    )

    store.add(active)
    store.add(inactive)

    result = store.valid_at(
        datetime(
            2023,
            1,
            1,
            tzinfo=timezone.utc,
        )
    )

    assert result == [active]


def test_relationship_store_includes_open_ended_relationship():
    store = RelationshipStore()

    relationship = Relationship(
        id="REL-008",
        relationship_type=RelationshipType.CONTROLS,
        source_entity_id="COMP-001",
        target_entity_id="FAC-001",
        valid_from=datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        confidence=0.9,
    )

    store.add(relationship)

    result = store.valid_at(
        datetime(
            2035,
            1,
            1,
            tzinfo=timezone.utc,
        )
    )

    assert result == [relationship]


def test_relationship_store_excludes_relationship_before_valid_from():
    store = RelationshipStore()

    relationship = Relationship(
        id="REL-009",
        relationship_type=RelationshipType.OPERATES,
        source_entity_id="COMP-001",
        target_entity_id="FAC-001",
        valid_from=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        confidence=0.9,
    )

    store.add(relationship)

    result = store.valid_at(
        datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        )
    )

    assert result == []


def test_relationship_store_excludes_relationship_after_valid_to():
    store = RelationshipStore()

    relationship = Relationship(
        id="REL-010",
        relationship_type=RelationshipType.OPERATES,
        source_entity_id="COMP-001",
        target_entity_id="FAC-001",
        valid_from=datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        valid_to=datetime(
            2025,
            12,
            31,
            tzinfo=timezone.utc,
        ),
        confidence=0.9,
    )

    store.add(relationship)

    result = store.valid_at(
        datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        )
    )

    assert result == []


def test_relationship_store_treats_validity_boundaries_as_inclusive():
    store = RelationshipStore()

    relationship = Relationship(
        id="REL-011",
        relationship_type=RelationshipType.OPERATES,
        source_entity_id="COMP-001",
        target_entity_id="FAC-001",
        valid_from=datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        valid_to=datetime(
            2025,
            12,
            31,
            tzinfo=timezone.utc,
        ),
        confidence=0.9,
    )

    store.add(relationship)

    assert store.valid_at(
        datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        )
    ) == [relationship]

    assert store.valid_at(
        datetime(
            2025,
            12,
            31,
            tzinfo=timezone.utc,
        )
    ) == [relationship]