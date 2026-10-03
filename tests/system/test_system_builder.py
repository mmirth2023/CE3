from datetime import datetime, timezone

import pytest

from ce3.system.builder import GlobalSystemStateBuilder


def test_global_system_state_builder_builds_state():
    builder = GlobalSystemStateBuilder()

    state = builder.build(
        state_id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        confidence=0.9,
    )

    assert state.id == "STATE-001"
    assert state.state_time == datetime(
        2025,
        1,
        1,
        tzinfo=timezone.utc,
    )
    assert state.confidence == 0.9


def test_global_system_state_builder_preserves_entities():
    builder = GlobalSystemStateBuilder()

    entities = {
        "COMP-001": {
            "type": "company",
            "name": "Example Energy",
        },
    }

    state = builder.build(
        state_id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        entities=entities,
    )

    assert state.entities == entities


def test_global_system_state_builder_preserves_relationships():
    builder = GlobalSystemStateBuilder()

    relationships = {
        "REL-001": {
            "type": "owns",
            "source": "COMP-001",
            "target": "FAC-001",
        },
    }

    state = builder.build(
        state_id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        relationships=relationships,
    )

    assert state.relationships == relationships


def test_global_system_state_builder_preserves_domain_state():
    builder = GlobalSystemStateBuilder()

    state = builder.build(
        state_id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        physical={
            "production": {
                "status": "reduced",
            },
        },
        economic={
            "inflation": {
                "direction": "higher",
            },
        },
        financial={
            "credit": {
                "conditions": "tightening",
            },
        },
        market={
            "brent": {
                "price": 85.0,
            },
        },
    )

    assert state.physical["production"]["status"] == "reduced"
    assert state.economic["inflation"]["direction"] == "higher"
    assert state.financial["credit"]["conditions"] == "tightening"
    assert state.market["brent"]["price"] == 85.0


def test_global_system_state_builder_preserves_lineage():
    builder = GlobalSystemStateBuilder()

    state = builder.build(
        state_id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        source_event_ids=[
            "EVENT-001",
            "EVENT-002",
        ],
        source_observation_ids=[
            "OBS-001",
            "OBS-002",
        ],
    )

    assert state.source_event_ids == [
        "EVENT-001",
        "EVENT-002",
    ]

    assert state.source_observation_ids == [
        "OBS-001",
        "OBS-002",
    ]


def test_global_system_state_builder_preserves_structural_context():
    builder = GlobalSystemStateBuilder()

    state = builder.build(
        state_id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        constraints={
            "supply": {
                "binding": True,
            },
        },
        dependencies={
            "refinery": {
                "depends_on": "imported_crude",
            },
        },
        active_shocks={
            "SHOCK-001": {
                "type": "facility_damage",
            },
        },
        adaptations={
            "shipping": {
                "rerouting": True,
            },
        },
    )

    assert state.constraints["supply"]["binding"] is True
    assert (
        state.dependencies["refinery"]["depends_on"]
        == "imported_crude"
    )
    assert (
        state.active_shocks["SHOCK-001"]["type"]
        == "facility_damage"
    )
    assert state.adaptations["shipping"]["rerouting"] is True


def test_global_system_state_builder_preserves_uncertainty_and_metadata():
    builder = GlobalSystemStateBuilder()

    state = builder.build(
        state_id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        uncertainty={
            "production": {
                "confidence_range": [
                    400_000,
                    500_000,
                ],
            },
        },
        metadata={
            "scenario": "observed",
        },
    )

    assert state.uncertainty["production"]["confidence_range"] == [
        400_000,
        500_000,
    ]

    assert state.metadata["scenario"] == "observed"


def test_global_system_state_builder_initializes_missing_dimensions():
    builder = GlobalSystemStateBuilder()

    state = builder.build(
        state_id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    assert state.entities == {}
    assert state.relationships == {}
    assert state.physical == {}
    assert state.economic == {}
    assert state.financial == {}
    assert state.political == {}
    assert state.information == {}
    assert state.infrastructure == {}
    assert state.market == {}
    assert state.constraints == {}
    assert state.dependencies == {}
    assert state.active_shocks == {}
    assert state.observability == {}
    assert state.adaptations == {}
    assert state.propagation_paths == {}


def test_global_system_state_builder_rejects_invalid_confidence():
    builder = GlobalSystemStateBuilder()

    with pytest.raises(ValueError):
        builder.build(
            state_id="STATE-001",
            state_time=datetime(
                2025,
                1,
                1,
                tzinfo=timezone.utc,
            ),
            confidence=1.5,
        )