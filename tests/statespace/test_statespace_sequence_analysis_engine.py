from datetime import datetime, timezone

import pytest

from ce3.statespace.sequence import (
    StateSpaceTransitionSequence,
)
from ce3.statespace.sequence_analysis import (
    StateSpaceSequenceClassification,
)
from ce3.statespace.sequence_analysis_engine import (
    StateSpaceSequenceAnalysisEngine,
)
from ce3.statespace.transition import (
    StateSpaceTransitionType,
)


TIME_A = datetime(
    2026,
    10,
    3,
    10,
    0,
    0,
    tzinfo=timezone.utc,
)

TIME_B = datetime(
    2026,
    10,
    3,
    11,
    0,
    0,
    tzinfo=timezone.utc,
)

TIME_C = datetime(
    2026,
    10,
    3,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)

TIME_D = datetime(
    2026,
    10,
    3,
    13,
    0,
    0,
    tzinfo=timezone.utc,
)


def make_sequence(
    *,
    transition_ids: list[str],
    transition_types: list[
        StateSpaceTransitionType
    ],
    transition_dimensions: list[list[str]],
    start_time: datetime = TIME_B,
    end_time: datetime = TIME_C,
    cumulative_magnitude: float = 1.0,
    average_confidence: float = 0.8,
    has_structural_shift: bool = False,
) -> StateSpaceTransitionSequence:
    return StateSpaceTransitionSequence(
        id="SEQUENCE-001",
        start_time=start_time,
        end_time=end_time,
        transition_ids=transition_ids,
        transition_types=transition_types,
        transition_dimensions=transition_dimensions,
        changed_dimensions=sorted(
            {
                dimension
                for dimensions
                in transition_dimensions
                for dimension
                in dimensions
            }
        ),
        transition_count=len(transition_ids),
        cumulative_magnitude=cumulative_magnitude,
        average_confidence=average_confidence,
        has_structural_shift=has_structural_shift,
    )


def test_analysis_engine_counts_transition_types():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
            "TRANSITION-003",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.RECOVERY,
        ],
        transition_dimensions=[
            ["stability"],
            ["capacity"],
            ["stability"],
        ],
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-001",
        sequence=sequence,
    )

    assert analysis.transition_count == 3
    assert analysis.deterioration_count == 2
    assert analysis.recovery_count == 1
    assert analysis.normalization_count == 0
    assert analysis.dimensional_shift_count == 0
    assert analysis.structural_shift_count == 0
    assert analysis.none_count == 0
    assert analysis.unknown_count == 0


def test_analysis_engine_preserves_changed_dimensions():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.RECOVERY,
        ],
        transition_dimensions=[
            [
                "stability",
                "capacity",
            ],
            [
                "connectivity",
            ],
        ],
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-002",
        sequence=sequence,
    )

    assert analysis.changed_dimensions == [
        "capacity",
        "connectivity",
        "stability",
    ]


def test_analysis_engine_detects_repeated_dimensions():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
            "TRANSITION-003",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.RECOVERY,
            StateSpaceTransitionType.DETERIORATION,
        ],
        transition_dimensions=[
            [
                "stability",
                "capacity",
            ],
            [
                "stability",
            ],
            [
                "capacity",
            ],
        ],
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-003",
        sequence=sequence,
    )

    assert analysis.repeated_dimensions == [
        "capacity",
        "stability",
    ]

    assert analysis.has_repeated_dimensions is True


def test_analysis_engine_identifies_dominant_dimension():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
            "TRANSITION-003",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.RECOVERY,
            StateSpaceTransitionType.DETERIORATION,
        ],
        transition_dimensions=[
            [
                "stability",
                "capacity",
            ],
            [
                "stability",
            ],
            [
                "stability",
            ],
        ],
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-004",
        sequence=sequence,
    )

    assert analysis.dominant_dimension == "stability"


def test_analysis_engine_identifies_dominant_transition_type():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
            "TRANSITION-003",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.RECOVERY,
        ],
        transition_dimensions=[
            ["stability"],
            ["capacity"],
            ["connectivity"],
        ],
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-005",
        sequence=sequence,
    )

    assert (
        analysis.dominant_transition_type
        == "deterioration"
    )


def test_analysis_engine_detects_directional_reversal():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.RECOVERY,
        ],
        transition_dimensions=[
            ["stability"],
            ["stability"],
        ],
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-006",
        sequence=sequence,
    )

    assert analysis.reversal_detected is True
    assert analysis.is_reversal is True
    assert (
        analysis.classification
        == StateSpaceSequenceClassification.REVERSAL
    )


def test_analysis_engine_detects_structural_sequence():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.STRUCTURAL_SHIFT,
        ],
        transition_dimensions=[
            ["stability"],
            ["constraint"],
        ],
        has_structural_shift=True,
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-007",
        sequence=sequence,
    )

    assert analysis.structural_shift_detected is True
    assert analysis.is_structural is True
    assert (
        analysis.classification
        == StateSpaceSequenceClassification.STRUCTURAL
    )


def test_analysis_engine_classifies_deteriorating_sequence():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.DETERIORATION,
        ],
        transition_dimensions=[
            ["stability"],
            ["capacity"],
        ],
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-008",
        sequence=sequence,
    )

    assert (
        analysis.classification
        == StateSpaceSequenceClassification.DETERIORATING
    )


def test_analysis_engine_classifies_recovering_sequence():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
        ],
        transition_types=[
            StateSpaceTransitionType.RECOVERY,
            StateSpaceTransitionType.RECOVERY,
        ],
        transition_dimensions=[
            ["stability"],
            ["capacity"],
        ],
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-009",
        sequence=sequence,
    )

    assert (
        analysis.classification
        == StateSpaceSequenceClassification.RECOVERING
    )


def test_analysis_engine_classifies_mixed_sequence():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.RECOVERY,
        ],
        transition_dimensions=[
            ["stability"],
            ["capacity"],
        ],
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-010",
        sequence=sequence,
    )

    assert (
        analysis.classification
        == StateSpaceSequenceClassification.REVERSAL
    )


def test_analysis_engine_calculates_transition_density():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.DETERIORATION,
        ],
        transition_dimensions=[
            ["stability"],
            ["capacity"],
        ],
        start_time=TIME_B,
        end_time=TIME_C,
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-011",
        sequence=sequence,
    )

    assert analysis.transition_density == pytest.approx(
        2.0
    )


def test_analysis_engine_preserves_sequence_metrics():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
        ],
        transition_types=[
            StateSpaceTransitionType.RECOVERY,
        ],
        transition_dimensions=[
            ["stability"],
        ],
        cumulative_magnitude=0.75,
        average_confidence=0.85,
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-012",
        sequence=sequence,
    )

    assert analysis.cumulative_magnitude == 0.75
    assert analysis.average_confidence == 0.85


def test_analysis_engine_builds_rationale():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
            "TRANSITION-002",
        ],
        transition_types=[
            StateSpaceTransitionType.DETERIORATION,
            StateSpaceTransitionType.RECOVERY,
        ],
        transition_dimensions=[
            ["stability"],
            ["stability"],
        ],
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-013",
        sequence=sequence,
    )

    assert (
        "Observed sequence classified as reversal."
        in analysis.rationale
    )

    assert (
        "Observed deterioration transitions: 1."
        in analysis.rationale
    )

    assert (
        "Observed recovery transitions: 1."
        in analysis.rationale
    )

    assert (
        "The observed sequence contains a "
        "directional reversal."
        in analysis.rationale
    )

    assert (
        "Dominant transition type: deterioration."
        in analysis.rationale
    )

    assert (
        "Dominant affected dimension: stability."
        in analysis.rationale
    )


def test_analysis_engine_preserves_metadata():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
        ],
        transition_types=[
            StateSpaceTransitionType.RECOVERY,
        ],
        transition_dimensions=[
            ["stability"],
        ],
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-014",
        sequence=sequence,
        metadata={
            "domain": "energy",
            "region": "global",
        },
    )

    assert analysis.metadata == {
        "domain": "energy",
        "region": "global",
    }


def test_analysis_engine_handles_unknown_transition():
    sequence = make_sequence(
        transition_ids=[
            "TRANSITION-001",
        ],
        transition_types=[
            StateSpaceTransitionType.UNKNOWN,
        ],
        transition_dimensions=[
            ["information"],
        ],
    )

    engine = StateSpaceSequenceAnalysisEngine()

    analysis = engine.analyze(
        analysis_id="ANALYSIS-015",
        sequence=sequence,
    )

    assert analysis.unknown_count == 1
    assert (
        analysis.classification
        == StateSpaceSequenceClassification.COMPLEX
    )