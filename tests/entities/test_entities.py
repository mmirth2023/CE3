import pytest

from ce3.entities.models import Entity, EntityType
from ce3.entities.store import EntityStore


def make_facility() -> Entity:
    return Entity(
        id="FAC-001",
        entity_type=EntityType.FACILITY,
        canonical_name="Facility A",
        aliases=[
            "Facility A",
            "FAC A",
        ],
    )


def test_entity_preserves_canonical_identity():
    entity = make_facility()

    assert entity.id == "FAC-001"
    assert entity.entity_type == EntityType.FACILITY
    assert entity.canonical_name == "Facility A"
    assert entity.aliases == [
        "Facility A",
        "FAC A",
    ]


def test_entity_types_are_explicit():
    assert EntityType.COMPANY.value == "company"
    assert EntityType.FACILITY.value == "facility"
    assert EntityType.PORT.value == "port"
    assert EntityType.COMMODITY.value == "commodity"
    assert EntityType.COUNTRY.value == "country"


def test_entity_store_adds_and_retrieves_entity():
    store = EntityStore()
    entity = make_facility()

    stored = store.add(entity)

    assert stored is entity
    assert store.get("FAC-001") is entity
    assert len(store) == 1


def test_entity_store_rejects_duplicate_ids():
    store = EntityStore()

    store.add(make_facility())

    with pytest.raises(ValueError):
        store.add(make_facility())


def test_entity_store_lists_all_entities():
    store = EntityStore()

    facility = make_facility()

    company = Entity(
        id="COMP-001",
        entity_type=EntityType.COMPANY,
        canonical_name="Company A",
    )

    store.add(facility)
    store.add(company)

    assert store.all() == [
        facility,
        company,
    ]


def test_entity_store_filters_by_type():
    store = EntityStore()

    facility = make_facility()

    company = Entity(
        id="COMP-001",
        entity_type=EntityType.COMPANY,
        canonical_name="Company A",
    )

    port = Entity(
        id="PORT-001",
        entity_type=EntityType.PORT,
        canonical_name="Port A",
    )

    store.add(facility)
    store.add(company)
    store.add(port)

    assert store.by_type(EntityType.FACILITY) == [
        facility
    ]

    assert store.by_type(EntityType.PORT) == [
        port
    ]


def test_entity_store_finds_canonical_name():
    store = EntityStore()

    entity = make_facility()

    store.add(entity)

    assert (
        store.by_canonical_name("Facility A")
        is entity
    )


def test_entity_store_returns_none_for_unknown_name():
    store = EntityStore()

    assert (
        store.by_canonical_name("Unknown Facility")
        is None
    )


def test_entity_store_raises_for_unknown_id():
    store = EntityStore()

    with pytest.raises(KeyError):
        store.get("UNKNOWN")