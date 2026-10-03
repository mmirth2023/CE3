from datetime import datetime, timezone

from ce3.propagation import (
    PropagationEngine,
    PropagationStatus,
    PropagationType,
)


def test_engine_builds_propagation_path():
    engine = PropagationEngine()

    path = engine.build(
        propagation_id="PROP-001",
        source_id="facility_A",
        target_id="company_A",
        propagation_type=PropagationType.SUPPLY,
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
        relationship_id="REL-001",
        dependency_id="DEP-001",
        rationale="Direct supply dependency.",
    )

    assert path.id == "PROP-001"
    assert path.source_id == "facility_A"
    assert path.target_id == "company_A"
    assert path.propagation_type == PropagationType.SUPPLY
    assert path.status == PropagationStatus.UNKNOWN
    assert path.strength == 0.8
    assert path.confidence == 0.9
    assert path.relationship_id == "REL-001"
    assert path.dependency_id == "DEP-001"


def test_engine_build_observed():
    engine = PropagationEngine()

    path = engine.build_observed(
        propagation_id="PROP-002",
        source_id="facility_A",
        target_id="port_B",
        propagation_type=PropagationType.INFRASTRUCTURE,
        identified_at=datetime.now(timezone.utc),
        strength=0.7,
        confidence=0.8,
        source_event_ids=["EV-001"],
        source_observation_ids=["OBS-001"],
    )

    assert path.status == PropagationStatus.OBSERVED
    assert path.source_event_ids == ["EV-001"]
    assert path.source_observation_ids == ["OBS-001"]


def test_engine_build_supported():
    engine = PropagationEngine()

    path = engine.build_supported(
        propagation_id="PROP-003",
        source_id="company_A",
        target_id="market_A",
        propagation_type=PropagationType.MARKET,
        identified_at=datetime.now(timezone.utc),
        strength=0.6,
        confidence=0.9,
    )

    assert path.status == PropagationStatus.SUPPORTED


def test_engine_build_structurally_possible():
    engine = PropagationEngine()

    path = engine.build_structurally_possible(
        propagation_id="PROP-004",
        source_id="port_A",
        target_id="commodity_A",
        propagation_type=PropagationType.SUPPLY,
        identified_at=datetime.now(timezone.utc),
        strength=0.5,
        confidence=0.7,
        intermediate_ids=["vessel_A"],
    )

    assert path.status == PropagationStatus.STRUCTURALLY_POSSIBLE
    assert path.intermediate_ids == ["vessel_A"]


def test_engine_build_contradicted():
    engine = PropagationEngine()

    path = engine.build_contradicted(
        propagation_id="PROP-005",
        source_id="entity_A",
        target_id="entity_B",
        propagation_type=PropagationType.INFORMATION,
        identified_at=datetime.now(timezone.utc),
        confidence=0.8,
        rationale="Observed evidence contradicts the proposed path.",
    )

    assert path.status == PropagationStatus.CONTRADICTED
    assert (
        path.rationale
        == "Observed evidence contradicts the proposed path."
    )


def test_engine_preserves_temporal_validity():
    engine = PropagationEngine()

    valid_from = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    valid_to = datetime(
        2026,
        12,
        31,
        tzinfo=timezone.utc,
    )

    path = engine.build(
        propagation_id="PROP-006",
        source_id="entity_A",
        target_id="entity_B",
        propagation_type=PropagationType.DEPENDENCY,
        identified_at=datetime.now(timezone.utc),
        valid_from=valid_from,
        valid_to=valid_to,
    )

    assert path.valid_from == valid_from
    assert path.valid_to == valid_to


def test_engine_preserves_intermediate_nodes():
    engine = PropagationEngine()

    path = engine.build(
        propagation_id="PROP-007",
        source_id="entity_A",
        target_id="entity_D",
        propagation_type=PropagationType.SUPPLY,
        identified_at=datetime.now(timezone.utc),
        intermediate_ids=[
            "entity_B",
            "entity_C",
        ],
    )

    assert path.intermediate_ids == [
        "entity_B",
        "entity_C",
    ]


def test_engine_preserves_metadata():
    engine = PropagationEngine()

    path = engine.build(
        propagation_id="PROP-008",
        source_id="entity_A",
        target_id="entity_B",
        propagation_type=PropagationType.OTHER,
        identified_at=datetime.now(timezone.utc),
        metadata={
            "basis": "structural_dependency",
            "version": 1,
        },
    )

    assert path.metadata == {
        "basis": "structural_dependency",
        "version": 1,
    }