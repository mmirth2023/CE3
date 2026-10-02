import pytest

from ce3.materiality.engine import MaterialityEngine
from ce3.materiality.models import MaterialityLevel


def test_low_inputs_produce_no_materiality():
    engine = MaterialityEngine()

    assessment = engine.assess(
        magnitude=0.0,
        structural_relevance=0.0,
        persistence=0.0,
        confidence=0.0,
    )

    assert assessment.level == MaterialityLevel.NONE


def test_small_change_produces_low_materiality():
    engine = MaterialityEngine()

    assessment = engine.assess(
        magnitude=0.3,
        structural_relevance=0.3,
        persistence=0.2,
        confidence=0.8,
    )

    assert assessment.level == MaterialityLevel.LOW


def test_moderate_change_produces_medium_materiality():
    engine = MaterialityEngine()

    assessment = engine.assess(
        magnitude=0.5,
        structural_relevance=0.5,
        persistence=0.5,
        confidence=0.5,
    )

    assert assessment.level == MaterialityLevel.MEDIUM


def test_high_change_produces_high_materiality():
    engine = MaterialityEngine()

    assessment = engine.assess(
        magnitude=0.8,
        structural_relevance=0.8,
        persistence=0.7,
        confidence=0.8,
    )

    assert assessment.level == MaterialityLevel.HIGH


def test_extreme_change_produces_critical_materiality():
    engine = MaterialityEngine()

    assessment = engine.assess(
        magnitude=1.0,
        structural_relevance=1.0,
        persistence=1.0,
        confidence=1.0,
    )

    assert assessment.level == MaterialityLevel.CRITICAL


def test_assessment_preserves_component_scores():
    engine = MaterialityEngine()

    assessment = engine.assess(
        magnitude=0.7,
        structural_relevance=0.8,
        persistence=0.6,
        confidence=0.9,
    )

    assert assessment.magnitude == 0.7
    assert assessment.structural_relevance == 0.8
    assert assessment.persistence == 0.6
    assert assessment.confidence == 0.9


def test_assessment_contains_explainable_rationale():
    engine = MaterialityEngine()

    assessment = engine.assess(
        magnitude=0.7,
        structural_relevance=0.8,
        persistence=0.6,
        confidence=0.9,
    )

    assert len(assessment.rationale) == 5
    assert "magnitude=0.70" in assessment.rationale
    assert "structural_relevance=0.80" in assessment.rationale
    assert "persistence=0.60" in assessment.rationale
    assert "confidence=0.90" in assessment.rationale


@pytest.mark.parametrize(
    "field,value",
    [
        ("magnitude", -0.1),
        ("magnitude", 1.1),
        ("structural_relevance", -0.1),
        ("structural_relevance", 1.1),
        ("persistence", -0.1),
        ("persistence", 1.1),
        ("confidence", -0.1),
        ("confidence", 1.1),
    ],
)
def test_invalid_scores_are_rejected(field, value):
    engine = MaterialityEngine()

    values = {
        "magnitude": 0.5,
        "structural_relevance": 0.5,
        "persistence": 0.5,
        "confidence": 0.5,
    }

    values[field] = value

    with pytest.raises(ValueError):
        engine.assess(**values)