from datetime import datetime, timezone

from ce3.statespace.engine import StateSpaceEngine
from ce3.statespace.models import StateSpaceDimension
from ce3.system.models import GlobalSystemState


STATE_TIME = datetime(
    2026,
    10,
    3,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


def make_system_state() -> GlobalSystemState:
    return GlobalSystemState(
        id="SYSTEM-001",
        state_time=STATE_TIME,
        entities={
            "facility_A": {
                "type": "facility",
            },
            "company_A": {
                "type": "company",
            },
        },
        relationships={
            "REL-001": {
                "source": "facility_A",
                "target": "company_A",
            },
        },
        physical={
            "facility_A": {
                "status": "degraded",
            },
        },
        economic={
            "production": "reduced",
        },
        financial={
            "market": "strained",
        },
        political={
            "policy": "restrictive",
        },
        information={
            "uncertainty": "elevated",
        },
        infrastructure={
            "port_B": {
                "status": "operational",
            },
        },
        market={
            "oil": {
                "price": 100,
            },
        },
        constraints={
            "CONSTRAINT-001": {
                "type": "capacity",
            },
        },
        dependencies={
            "DEPENDENCY-001": {
                "type": "supply",
            },
        },
        active_shocks={
            "SHOCK-001": {
                "type": "facility_damage",
            },
        },
        observability={
            "coverage": 0.8,
        },
        adaptations={
            "ADAPTATION-001": {
                "type": "rerouting",
            },
        },
        propagation_paths={
            "PATH-001": {
                "source": "facility_A",
                "target": "company_A",
            },
            "PATH-002": {
                "source": "company_A",
                "target": "port_B",
            },
        },
        source_event_ids=[
            "EV-001",
        ],
        source_observation_ids=[
            "OBS-001",
        ],
        confidence=0.9,
        uncertainty={
            "score": 0.1,
        },
    )


def test_engine_builds_state_space_position():
    engine = StateSpaceEngine()

    position = engine.build(
        position_id="POSITION-001",
        system_state=make_system_state(),
    )

    assert position.id == "POSITION-001"
    assert position.state_time == STATE_TIME


def test_engine_maps_system_state_domains():
    engine = StateSpaceEngine()

    position = engine.build(
        position_id="POSITION-001",
        system_state=make_system_state(),
    )

    assert position.dimensions[
        StateSpaceDimension.PHYSICAL
    ] == 1.0

    assert position.dimensions[
        StateSpaceDimension.ECONOMIC
    ] == 1.0

    assert position.dimensions[
        StateSpaceDimension.FINANCIAL
    ] == 1.0

    assert position.dimensions[
        StateSpaceDimension.POLITICAL
    ] == 1.0

    assert position.dimensions[
        StateSpaceDimension.INFORMATION
    ] == 1.0

    assert position.dimensions[
        StateSpaceDimension.INFRASTRUCTURE
    ] == 1.0


def test_engine_maps_structural_collections():
    engine = StateSpaceEngine()

    position = engine.build(
        position_id="POSITION-001",
        system_state=make_system_state(),
    )

    assert position.dimensions[
        StateSpaceDimension.CONNECTIVITY
    ] == 1.0

    assert position.dimensions[
        StateSpaceDimension.DEPENDENCY
    ] == 1.0

    assert position.dimensions[
        StateSpaceDimension.CONSTRAINT
    ] == 1.0

    assert position.dimensions[
        StateSpaceDimension.ADAPTATION
    ] == 1.0

    assert position.dimensions[
        StateSpaceDimension.RESILIENCE
    ] == 1.0


def test_engine_preserves_constraints_dependencies_and_shocks():
    engine = StateSpaceEngine()

    position = engine.build(
        position_id="POSITION-001",
        system_state=make_system_state(),
    )

    assert position.active_constraints == [
        "CONSTRAINT-001",
    ]

    assert position.active_dependencies == [
        "DEPENDENCY-001",
    ]

    assert position.active_shocks == [
        "SHOCK-001",
    ]


def test_engine_preserves_propagation_paths():
    engine = StateSpaceEngine()

    position = engine.build(
        position_id="POSITION-001",
        system_state=make_system_state(),
    )

    assert position.propagation_path_ids == [
        "PATH-001",
        "PATH-002",
    ]


def test_engine_preserves_provenance():
    engine = StateSpaceEngine()

    position = engine.build(
        position_id="POSITION-001",
        system_state=make_system_state(),
    )

    assert position.source_event_ids == [
        "EV-001",
    ]

    assert position.source_observation_ids == [
        "OBS-001",
    ]


def test_engine_preserves_confidence_and_uncertainty():
    engine = StateSpaceEngine()

    position = engine.build(
        position_id="POSITION-001",
        system_state=make_system_state(),
    )

    assert position.confidence == 0.9
    assert position.uncertainty == 0.1


def test_engine_allows_state_time_override():
    engine = StateSpaceEngine()

    override_time = datetime(
        2026,
        10,
        3,
        14,
        0,
        0,
        tzinfo=timezone.utc,
    )

    position = engine.build(
        position_id="POSITION-001",
        system_state=make_system_state(),
        state_time=override_time,
    )

    assert position.state_time == override_time


def test_engine_preserves_labels_and_metadata():
    engine = StateSpaceEngine()

    position = engine.build(
        position_id="POSITION-001",
        system_state=make_system_state(),
        labels=[
            "strained",
            "high_dependency",
        ],
        metadata={
            "scenario": "observed",
        },
    )

    assert position.labels == [
        "strained",
        "high_dependency",
    ]

    assert position.metadata == {
        "scenario": "observed",
    }


def test_engine_represents_empty_domains_as_zero():
    system_state = GlobalSystemState(
        id="SYSTEM-EMPTY",
        state_time=STATE_TIME,
        confidence=0.0,
    )

    engine = StateSpaceEngine()

    position = engine.build(
        position_id="POSITION-EMPTY",
        system_state=system_state,
    )

    assert position.dimensions[
        StateSpaceDimension.PHYSICAL
    ] == 0.0

    assert position.dimensions[
        StateSpaceDimension.ECONOMIC
    ] == 0.0

    assert position.dimensions[
        StateSpaceDimension.CONNECTIVITY
    ] == 0.0

    assert position.dimensions[
        StateSpaceDimension.DEPENDENCY
    ] == 0.0

    assert position.dimensions[
        StateSpaceDimension.CONSTRAINT
    ] == 0.0

    assert position.dimensions[
        StateSpaceDimension.ADAPTATION
    ] == 0.0

    assert position.uncertainty == 0.0


def test_engine_extracts_explicit_uncertainty_score():
    system_state = make_system_state()

    system_state.uncertainty = {
        "score": 0.65,
    }

    engine = StateSpaceEngine()

    position = engine.build(
        position_id="POSITION-001",
        system_state=system_state,
    )

    assert position.uncertainty == 0.65