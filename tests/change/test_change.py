from datetime import datetime, timezone

from ce3.change.engine import StateChangeEngine
from ce3.materiality.models import MaterialityLevel
from ce3.temporal.state_diff import StateDiff
from ce3.temporal.state_version import StateVersion


def make_version(
    version_id: str,
    status: str,
) -> StateVersion:
    return StateVersion(
        id=version_id,
        state_time=datetime(
            2026,
            10,
            2,
            15,
            0,
            0,
            tzinfo=timezone.utc,
        ),
        state={
            "facility_A": {
                "status": status,
            },
        },
        confidence=0.9,
    )


def test_state_change_engine_integrates_diff_and_materiality():
    previous = make_version(
        "STATE-001",
        "operational",
    )

    current = make_version(
        "STATE-002",
        "degraded",
    )

    diff = StateDiff.between(
        previous,
        current,
    )

    engine = StateChangeEngine()

    assessment = engine.assess(
        change_id="CHANGE-001",
        diff=diff,
        assessed_at=datetime(
            2026,
            10,
            2,
            15,
            5,
            0,
            tzinfo=timezone.utc,
        ),
        magnitude=0.8,
        structural_relevance=0.9,
        persistence=0.7,
        confidence=0.9,
    )

    assert assessment.id == "CHANGE-001"
    assert assessment.state_diff is diff
    assert assessment.materiality.level == (
        MaterialityLevel.CRITICAL
    )
    assert assessment.is_material is True
    assert assessment.affected_paths == [
        "facility_A.status"
    ]


def test_state_change_engine_preserves_provenance():
    previous = make_version(
        "STATE-001",
        "operational",
    )

    current = make_version(
        "STATE-002",
        "degraded",
    )

    diff = StateDiff.between(
        previous,
        current,
    )

    engine = StateChangeEngine()

    assessment = engine.assess(
        change_id="CHANGE-002",
        diff=diff,
        assessed_at=datetime.now(timezone.utc),
        magnitude=0.7,
        structural_relevance=0.8,
        persistence=0.8,
        confidence=0.9,
        source_event_ids=[
            "EV-001",
            "EV-002",
        ],
        source_observation_ids=[
            "OBS-001",
            "OBS-002",
        ],
    )

    assert assessment.source_event_ids == [
        "EV-001",
        "EV-002",
    ]

    assert assessment.source_observation_ids == [
        "OBS-001",
        "OBS-002",
    ]


def test_non_material_change_is_not_material():
    previous = make_version(
        "STATE-001",
        "operational",
    )

    current = make_version(
        "STATE-002",
        "degraded",
    )

    diff = StateDiff.between(
        previous,
        current,
    )

    engine = StateChangeEngine()

    assessment = engine.assess(
        change_id="CHANGE-003",
        diff=diff,
        assessed_at=datetime.now(timezone.utc),
        magnitude=0.1,
        structural_relevance=0.1,
        persistence=0.1,
        confidence=0.5,
    )

    assert assessment.materiality.level == (
        MaterialityLevel.NONE
    )

    assert assessment.is_material is False


def test_multiple_changed_paths_are_preserved():
    previous = StateVersion(
        id="STATE-001",
        state_time=datetime.now(timezone.utc),
        state={
            "facility_A": {
                "status": "operational",
                "capacity": 500000,
            },
            "port_B": {
                "status": "open",
            },
        },
        confidence=0.9,
    )

    current = StateVersion(
        id="STATE-002",
        state_time=datetime.now(timezone.utc),
        state={
            "facility_A": {
                "status": "degraded",
                "capacity": 300000,
            },
            "port_B": {
                "status": "closed",
            },
        },
        confidence=0.9,
    )

    diff = StateDiff.between(
        previous,
        current,
    )

    engine = StateChangeEngine()

    assessment = engine.assess(
        change_id="CHANGE-004",
        diff=diff,
        assessed_at=datetime.now(timezone.utc),
        magnitude=0.9,
        structural_relevance=0.9,
        persistence=0.8,
        confidence=0.9,
    )

    assert set(assessment.affected_paths) == {
        "facility_A.status",
        "facility_A.capacity",
        "port_B.status",
    }


def test_state_change_engine_detects_change_between_versions():
    previous = make_version(
        "STATE-001",
        "operational",
    )

    current = make_version(
        "STATE-002",
        "degraded",
    )

    engine = StateChangeEngine()

    assessment = engine.detect(
        change_id="CHANGE-005",
        previous=previous,
        current=current,
        assessed_at=datetime(
            2026,
            10,
            2,
            15,
            5,
            0,
            tzinfo=timezone.utc,
        ),
        magnitude=0.8,
        structural_relevance=0.9,
        persistence=0.7,
        confidence=0.9,
    )

    assert assessment.id == "CHANGE-005"
    assert assessment.state_diff.changed is True
    assert assessment.materiality.level == (
        MaterialityLevel.CRITICAL
    )
    assert assessment.affected_paths == [
        "facility_A.status"
    ]


def test_state_change_engine_detects_no_change_between_identical_versions():
    previous = make_version(
        "STATE-001",
        "operational",
    )

    current = make_version(
        "STATE-002",
        "operational",
    )

    engine = StateChangeEngine()

    assessment = engine.detect(
        change_id="CHANGE-006",
        previous=previous,
        current=current,
        assessed_at=datetime.now(timezone.utc),
        magnitude=0.0,
        structural_relevance=0.0,
        persistence=0.0,
        confidence=0.9,
    )

    assert assessment.state_diff.changed is False
    assert assessment.affected_paths == []
    assert assessment.materiality.level == (
        MaterialityLevel.NONE
    )
    assert assessment.is_material is False