from datetime import datetime, timezone

import pytest

from ce3.relationships.history import RelationshipHistory
from ce3.relationships.models import (
    Relationship,
    RelationshipType,
)


def make_relationship(
    relationship_id: str,
    relationship_type: RelationshipType,
    source_entity_id: str,
    target_entity_id: str,
    valid_from: datetime | None = None,
    valid_to: datetime | None = None,
) -> Relationship:
    return Relationship(
        id=relationship_id,
        relationship_type=relationship_type,
        source_entity_id=source_entity_id,
        target_entity_id=target_entity_id,
        valid_from=valid_from,
        valid_to=valid_to,
        confidence=0.9,
    )


def test_relationship_history_adds_relationship():
    history = RelationshipHistory()

    relationship = make_relationship(
        "REL-001",
        RelationshipType.OWNS,
        "COMP-001",
        "FAC-001",
    )

    stored = history.add(relationship)

    assert stored is relationship
    assert len(history) == 1


def test_relationship_history_rejects_duplicate_ids():
    history = RelationshipHistory()

    relationship = make_relationship(
        "REL-001",
        RelationshipType.OWNS,
        "COMP-001",
        "FAC-001",
    )

    history.add(relationship)

    with pytest.raises(ValueError):
        history.add(relationship)


def test_relationship_history_returns_chronological_order():
    history = RelationshipHistory()

    later = make_relationship(
        "REL-002",
        RelationshipType.OPERATES,
        "COMP-001",
        "FAC-001",
        valid_from=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    earlier = make_relationship(
        "REL-001",
        RelationshipType.OWNS,
        "COMP-001",
        "FAC-001",
        valid_from=datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    history.add(later)
    history.add(earlier)

    assert history.all() == [
        earlier,
        later,
    ]


def test_relationship_history_as_of_returns_valid_relationships():
    history = RelationshipHistory()

    active = make_relationship(
        "REL-001",
        RelationshipType.OWNS,
        "COMP-001",
        "FAC-001",
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
    )

    inactive = make_relationship(
        "REL-002",
        RelationshipType.OPERATES,
        "COMP-001",
        "FAC-002",
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
    )

    history.add(active)
    history.add(inactive)

    result = history.as_of(
        datetime(
            2023,
            1,
            1,
            tzinfo=timezone.utc,
        )
    )

    assert result == [active]


def test_relationship_history_between_returns_overlapping_relationships():
    history = RelationshipHistory()

    overlapping = make_relationship(
        "REL-001",
        RelationshipType.OWNS,
        "COMP-001",
        "FAC-001",
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
    )

    outside = make_relationship(
        "REL-002",
        RelationshipType.OPERATES,
        "COMP-001",
        "FAC-002",
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
    )

    history.add(overlapping)
    history.add(outside)

    result = history.between(
        datetime(
            2023,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    assert result == [overlapping]


def test_relationship_history_between_includes_boundary_overlap():
    history = RelationshipHistory()

    relationship = make_relationship(
        "REL-001",
        RelationshipType.OWNS,
        "COMP-001",
        "FAC-001",
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
    )

    history.add(relationship)

    result = history.between(
        datetime(
            2025,
            12,
            31,
            tzinfo=timezone.utc,
        ),
        datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    assert result == [relationship]


def test_relationship_history_latest_returns_latest_relationship():
    history = RelationshipHistory()

    earlier = make_relationship(
        "REL-001",
        RelationshipType.OWNS,
        "COMP-001",
        "FAC-001",
        valid_from=datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    later = make_relationship(
        "REL-002",
        RelationshipType.OPERATES,
        "COMP-001",
        "FAC-001",
        valid_from=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    history.add(earlier)
    history.add(later)

    assert history.latest() is later


def test_relationship_history_latest_returns_none_when_empty():
    history = RelationshipHistory()

    assert history.latest() is None


def test_relationship_history_finds_relationships_affecting_entity():
    history = RelationshipHistory()

    first = make_relationship(
        "REL-001",
        RelationshipType.OWNS,
        "COMP-001",
        "FAC-001",
    )

    second = make_relationship(
        "REL-002",
        RelationshipType.SUPPLIES,
        "COMP-002",
        "FAC-001",
    )

    third = make_relationship(
        "REL-003",
        RelationshipType.OPERATES,
        "COMP-003",
        "FAC-003",
    )

    history.add(first)
    history.add(second)
    history.add(third)

    result = history.affecting_entity(
        "FAC-001"
    )

    assert result == [
        first,
        second,
    ]


def test_relationship_history_supports_open_ended_relationships():
    history = RelationshipHistory()

    relationship = make_relationship(
        "REL-001",
        RelationshipType.CONTROLS,
        "COMP-001",
        "FAC-001",
        valid_from=datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    history.add(relationship)

    result = history.as_of(
        datetime(
            2035,
            1,
            1,
            tzinfo=timezone.utc,
        )
    )

    assert result == [relationship]


def test_relationship_history_supports_relationships_without_start_date():
    history = RelationshipHistory()

    relationship = make_relationship(
        "REL-001",
        RelationshipType.EXPOSED_TO,
        "COMP-001",
        "FAC-001",
    )

    history.add(relationship)

    result = history.as_of(
        datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        )
    )

    assert result == [relationship]