from datetime import datetime, timezone

from ce3.statespace.models import (
    StateSpaceDimension,
    StateSpacePosition,
)
from ce3.statespace.transition import (
    StateSpaceTransitionType,
)
from ce3.statespace.transition_engine import (
    StateSpaceTransitionEngine,
)


STATE_TIME_A = datetime(
    2026,
    10,
    3,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)

STATE_TIME_B = datetime(
    2026,
    10,
    3,
    13,
    0,
    0,
    tzinfo=timezone.utc,
)


def make_position(
    position_id: str,
    state_time: datetime,
    *,
    physical: float = 0.5,
    economic: float = 0.5,
    constraints: list[str] | None = None,
    dependencies: list[str] | None = None,
    shocks: list[str] | None = None,
    propagation_paths: list[str] | None = None,
    labels: list[str] | None = None,
    confidence: float = 0.9,
    uncertainty: float = 0.1,
    source_event_ids: list[str] | None = None,
    source_observation_ids: list[str] | None = None,
) -> StateSpacePosition:
    return StateSpacePosition(
        id=position_id,
        state_time=state_time,
        dimensions={
            StateSpaceDimension.PHYSICAL: physical,
            StateSpaceDimension.ECONOMIC: economic,
        },
        labels=list(labels or []),
        active_constraints=list(
            constraints or []
        ),
        active_dependencies=list(
            dependencies or []
        ),
        active_shocks=list(
            shocks or []
        ),
        propagation_path_ids=list(
            propagation_paths or []
        ),
        source_event_ids=list(
            source_event_ids or []
        ),
        source_observation_ids=list(
            source_observation_ids or []
        ),
        confidence=confidence,
        uncertainty=uncertainty,
    )


def assess(
    previous: StateSpacePosition,
    current: StateSpacePosition,
):
    engine = StateSpaceTransitionEngine()

    return engine.assess(
        transition_id="TRANSITION-001",
        previous=previous,
        current=current,
    )


def test_identical_positions_produce_no_transition():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        physical=0.5,
        economic=0.5,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.5,
        economic=0.5,
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.transition_type == (
        StateSpaceTransitionType.NONE
    )

    assert transition.has_transition is False
    assert transition.magnitude == 0.0


def test_decreasing_dimensions_are_classified_as_deterioration():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        physical=0.8,
        economic=0.7,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.5,
        economic=0.4,
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.transition_type == (
        StateSpaceTransitionType.DETERIORATION
    )

    assert transition.has_transition is True


def test_increasing_dimensions_are_classified_as_recovery():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        physical=0.4,
        economic=0.3,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.7,
        economic=0.8,
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.transition_type == (
        StateSpaceTransitionType.RECOVERY
    )


def test_mixed_directional_change_is_dimensional_shift():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        physical=0.8,
        economic=0.3,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.4,
        economic=0.7,
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.transition_type == (
        StateSpaceTransitionType.DIMENSIONAL_SHIFT
    )


def test_added_constraint_is_structural_shift():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        physical=0.5,
        economic=0.5,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.5,
        economic=0.5,
        constraints=[
            "CONSTRAINT-001",
        ],
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.transition_type == (
        StateSpaceTransitionType.STRUCTURAL_SHIFT
    )

    assert transition.has_transition is True


def test_removed_constraint_is_structural_shift():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        constraints=[
            "CONSTRAINT-001",
        ],
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.transition_type == (
        StateSpaceTransitionType.STRUCTURAL_SHIFT
    )


def test_added_dependency_is_structural_shift():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        dependencies=[
            "DEPENDENCY-001",
        ],
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.transition_type == (
        StateSpaceTransitionType.STRUCTURAL_SHIFT
    )


def test_added_shock_is_structural_shift():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        shocks=[
            "SHOCK-001",
        ],
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.transition_type == (
        StateSpaceTransitionType.STRUCTURAL_SHIFT
    )


def test_added_propagation_path_is_structural_shift():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        propagation_paths=[
            "PATH-001",
        ],
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.transition_type == (
        StateSpaceTransitionType.STRUCTURAL_SHIFT
    )


def test_label_only_change_is_normalization():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        labels=[
            "stable",
        ],
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        labels=[
            "normalized",
        ],
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.transition_type == (
        StateSpaceTransitionType.NORMALIZATION
    )


def test_magnitude_is_mean_absolute_dimension_change():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        physical=0.8,
        economic=0.6,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.4,
        economic=0.4,
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.magnitude == 0.3


def test_magnitude_is_bounded_to_one():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        physical=0.0,
        economic=0.0,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=1.0,
        economic=1.0,
    )

    transition = assess(
        previous,
        current,
    )

    assert 0.0 <= transition.magnitude <= 1.0
    assert transition.magnitude == 1.0


def test_confidence_uses_lower_position_confidence():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        physical=0.5,
        confidence=0.8,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.7,
        confidence=0.6,
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.confidence == 0.6


def test_provenance_is_combined_without_duplicates():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        source_event_ids=[
            "EV-001",
            "EV-002",
        ],
        source_observation_ids=[
            "OBS-001",
        ],
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.8,
        source_event_ids=[
            "EV-002",
            "EV-003",
        ],
        source_observation_ids=[
            "OBS-001",
            "OBS-002",
        ],
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.source_event_ids == [
        "EV-001",
        "EV-002",
        "EV-003",
    ]

    assert transition.source_observation_ids == [
        "OBS-001",
        "OBS-002",
    ]


def test_transition_preserves_position_identity():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.8,
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.previous_position_id == (
        "POSITION-001"
    )

    assert transition.current_position_id == (
        "POSITION-002"
    )


def test_transition_preserves_state_times():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.8,
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.previous_state_time == STATE_TIME_A
    assert transition.current_state_time == STATE_TIME_B


def test_transition_uses_current_state_time_by_default():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.8,
    )

    transition = assess(
        previous,
        current,
    )

    assert transition.assessed_at == STATE_TIME_B


def test_transition_accepts_assessment_timestamp():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.8,
    )

    assessed_at = datetime(
        2026,
        10,
        3,
        13,
        5,
        0,
        tzinfo=timezone.utc,
    )

    engine = StateSpaceTransitionEngine()

    transition = engine.assess(
        transition_id="TRANSITION-002",
        previous=previous,
        current=current,
        assessed_at=assessed_at,
    )

    assert transition.assessed_at == assessed_at


def test_metadata_is_preserved():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.8,
    )

    engine = StateSpaceTransitionEngine()

    transition = engine.assess(
        transition_id="TRANSITION-003",
        previous=previous,
        current=current,
        metadata={
            "source": "test",
        },
    )

    assert transition.metadata == {
        "source": "test",
    }


def test_rationale_identifies_changed_dimensions():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
        physical=0.8,
        economic=0.8,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        physical=0.5,
        economic=0.6,
    )

    transition = assess(
        previous,
        current,
    )

    assert any(
        "physical" in item
        for item in transition.rationale
    )

    assert any(
        "economic" in item
        for item in transition.rationale
    )


def test_rationale_identifies_added_constraint():
    previous = make_position(
        "POSITION-001",
        STATE_TIME_A,
    )

    current = make_position(
        "POSITION-002",
        STATE_TIME_B,
        constraints=[
            "CONSTRAINT-001",
        ],
    )

    transition = assess(
        previous,
        current,
    )

    assert any(
        "CONSTRAINT-001" in item
        for item in transition.rationale
    )