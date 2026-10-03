from ce3.statespace.sequence_analysis import (
    StateSpaceSequenceAnalysis,
    StateSpaceSequenceClassification,
)


def test_sequence_analysis_defaults():
    analysis = StateSpaceSequenceAnalysis(
        id="ANALYSIS-001",
        sequence_id="SEQUENCE-001",
        classification=(
            StateSpaceSequenceClassification.UNKNOWN
        ),
    )

    assert analysis.transition_count == 0
    assert analysis.deterioration_count == 0
    assert analysis.recovery_count == 0
    assert analysis.normalization_count == 0
    assert analysis.dimensional_shift_count == 0
    assert analysis.structural_shift_count == 0
    assert analysis.none_count == 0
    assert analysis.unknown_count == 0


def test_sequence_analysis_stores_transition_counts():
    analysis = StateSpaceSequenceAnalysis(
        id="ANALYSIS-002",
        sequence_id="SEQUENCE-002",
        classification=(
            StateSpaceSequenceClassification.DETERIORATING
        ),
        transition_count=4,
        deterioration_count=3,
        recovery_count=1,
    )

    assert analysis.transition_count == 4
    assert analysis.deterioration_count == 3
    assert analysis.recovery_count == 1


def test_sequence_analysis_stores_changed_dimensions():
    analysis = StateSpaceSequenceAnalysis(
        id="ANALYSIS-003",
        sequence_id="SEQUENCE-003",
        classification=(
            StateSpaceSequenceClassification.MIXED
        ),
        changed_dimensions=[
            "capacity",
            "stability",
            "connectivity",
        ],
        repeated_dimensions=[
            "capacity",
        ],
    )

    assert analysis.changed_dimensions == [
        "capacity",
        "stability",
        "connectivity",
    ]

    assert analysis.repeated_dimensions == [
        "capacity",
    ]


def test_sequence_analysis_structural_property():
    analysis = StateSpaceSequenceAnalysis(
        id="ANALYSIS-004",
        sequence_id="SEQUENCE-004",
        classification=(
            StateSpaceSequenceClassification.STRUCTURAL
        ),
        structural_shift_detected=True,
    )

    assert analysis.is_structural is True


def test_sequence_analysis_reversal_property():
    analysis = StateSpaceSequenceAnalysis(
        id="ANALYSIS-005",
        sequence_id="SEQUENCE-005",
        classification=(
            StateSpaceSequenceClassification.REVERSAL
        ),
        reversal_detected=True,
    )

    assert analysis.is_reversal is True


def test_sequence_analysis_repeated_dimensions_property():
    analysis = StateSpaceSequenceAnalysis(
        id="ANALYSIS-006",
        sequence_id="SEQUENCE-006",
        classification=(
            StateSpaceSequenceClassification.COMPLEX
        ),
        repeated_dimensions=[
            "stability",
        ],
    )

    assert analysis.has_repeated_dimensions is True


def test_sequence_analysis_without_repeated_dimensions():
    analysis = StateSpaceSequenceAnalysis(
        id="ANALYSIS-007",
        sequence_id="SEQUENCE-007",
        classification=(
            StateSpaceSequenceClassification.STABLE
        ),
    )

    assert analysis.has_repeated_dimensions is False


def test_sequence_analysis_stores_magnitude_and_confidence():
    analysis = StateSpaceSequenceAnalysis(
        id="ANALYSIS-008",
        sequence_id="SEQUENCE-008",
        classification=(
            StateSpaceSequenceClassification.RECOVERING
        ),
        cumulative_magnitude=1.75,
        average_confidence=0.85,
    )

    assert analysis.cumulative_magnitude == 1.75
    assert analysis.average_confidence == 0.85


def test_sequence_analysis_stores_dominant_features():
    analysis = StateSpaceSequenceAnalysis(
        id="ANALYSIS-009",
        sequence_id="SEQUENCE-009",
        classification=(
            StateSpaceSequenceClassification.DETERIORATING
        ),
        dominant_transition_type="deterioration",
        dominant_dimension="stability",
    )

    assert (
        analysis.dominant_transition_type
        == "deterioration"
    )

    assert (
        analysis.dominant_dimension
        == "stability"
    )


def test_sequence_analysis_stores_transition_density():
    analysis = StateSpaceSequenceAnalysis(
        id="ANALYSIS-010",
        sequence_id="SEQUENCE-010",
        classification=(
            StateSpaceSequenceClassification.COMPLEX
        ),
        transition_density=2.5,
    )

    assert analysis.transition_density == 2.5


def test_sequence_analysis_stores_rationale():
    analysis = StateSpaceSequenceAnalysis(
        id="ANALYSIS-011",
        sequence_id="SEQUENCE-011",
        classification=(
            StateSpaceSequenceClassification.REVERSAL
        ),
        rationale=[
            "Observed deterioration followed by recovery.",
            "The sequence contains a directional reversal.",
        ],
    )

    assert analysis.rationale == [
        "Observed deterioration followed by recovery.",
        "The sequence contains a directional reversal.",
    ]


def test_sequence_analysis_stores_metadata():
    analysis = StateSpaceSequenceAnalysis(
        id="ANALYSIS-012",
        sequence_id="SEQUENCE-012",
        classification=(
            StateSpaceSequenceClassification.STABLE
        ),
        metadata={
            "domain": "energy",
            "region": "global",
        },
    )

    assert analysis.metadata == {
        "domain": "energy",
        "region": "global",
    }