from datetime import datetime, timezone

import pytest

from ce3.propagation import (
    PropagationPath,
    PropagationStatus,
    PropagationType,
)


def test_propagation_path_creation():
    path = PropagationPath(
        id="PROP-001",
        source_id="facility_A",
        target_id="company_A",
        propagation_type=PropagationType.SUPPLY,
        status=PropagationStatus.SUPPORTED,
        identified_at=datetime(
            2026,
            10,
            3,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        strength=0.8,
        confidence=0.9,
    )

    assert path.id == "PROP-001"
    assert path.source_id == "facility_A"
    assert path.target_id == "company_A"
    assert path.propagation_type == PropagationType.SUPPLY
    assert path.status == PropagationStatus.SUPPORTED
    assert path.strength == 0.8
    assert path.confidence == 0.9


def test_propagation_path_preserves_relationship_and_dependency():
    path = PropagationPath(
        id="PROP-002",
        source_id="facility_A",
        target_id="port_B",
        propagation_type=PropagationType.INFRASTRUCTURE,
        identified_at=datetime.now(timezone.utc),
        relationship_id="REL-001",
        dependency_id="DEP-001",
        intermediate_ids=[
            "company_A",
            "vessel_B",
        ],
    )

    assert path.relationship_id == "REL-001"
    assert path.dependency_id == "DEP-001"
    assert path.intermediate_ids == [
        "company_A",
        "vessel_B",
    ]


def test_propagation_path_preserves_provenance():
    path = PropagationPath(
        id="PROP-003",
        source_id="entity_A",
        target_id="entity_B",
        propagation_type=PropagationType.FINANCIAL,
        identified_at=datetime.now(timezone.utc),
        source_event_ids=[
            "EV-001",
            "EV-002",
        ],
        source_observation_ids=[
            "OBS-001",
            "OBS-002",
        ],
    )

    assert path.source_event_ids == [
        "EV-001",
        "EV-002",
    ]

    assert path.source_observation_ids == [
        "OBS-001",
        "OBS-002",
    ]


def test_propagation_path_supports_temporal_validity():
    path = PropagationPath(
        id="PROP-004",
        source_id="entity_A",
        target_id="entity_B",
        propagation_type=PropagationType.DEPENDENCY,
        identified_at=datetime.now(timezone.utc),
        valid_from=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        valid_to=datetime(
            2026,
            12,
            31,
            tzinfo=timezone.utc,
        ),
    )

    assert path.valid_from is not None
    assert path.valid_to is not None
    assert path.valid_from < path.valid_to


def test_propagation_path_rejects_invalid_strength():
    with pytest.raises(ValueError):
        PropagationPath(
            id="PROP-005",
            source_id="entity_A",
            target_id="entity_B",
            propagation_type=PropagationType.MARKET,
            identified_at=datetime.now(timezone.utc),
            strength=1.5,
        )


def test_propagation_path_rejects_invalid_confidence():
    with pytest.raises(ValueError):
        PropagationPath(
            id="PROP-006",
            source_id="entity_A",
            target_id="entity_B",
            propagation_type=PropagationType.MARKET,
            identified_at=datetime.now(timezone.utc),
            confidence=-0.1,
        )


def test_propagation_path_defaults_are_explicit():
    path = PropagationPath(
        id="PROP-007",
        source_id="entity_A",
        target_id="entity_B",
        propagation_type=PropagationType.OTHER,
        identified_at=datetime.now(timezone.utc),
    )

    assert path.status == PropagationStatus.UNKNOWN
    assert path.strength == 0.0
    assert path.confidence == 0.0
    assert path.source_event_ids == []
    assert path.source_observation_ids == []
    assert path.intermediate_ids == []
    assert path.metadata == {}


def test_propagation_type_values_are_stable():
    assert PropagationType.DEPENDENCY.value == "dependency"
    assert PropagationType.SUPPLY.value == "supply"
    assert PropagationType.FINANCIAL.value == "financial"
    assert PropagationType.INFORMATION.value == "information"
    assert PropagationType.MARKET.value == "market"


def test_propagation_status_values_are_stable():
    assert PropagationStatus.OBSERVED.value == "observed"
    assert PropagationStatus.SUPPORTED.value == "supported"
    assert (
        PropagationStatus.STRUCTURALLY_POSSIBLE.value
        == "structurally_possible"
    )
    assert PropagationStatus.CONTRADICTED.value == "contradicted"
    assert PropagationStatus.UNKNOWN.value == "unknown"