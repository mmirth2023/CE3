from datetime import datetime, timezone

from ce3.evidence.provenance import (
    Claim,
    EvidenceLink,
    Observation,
    ProvenanceGraph,
    Relation,
    Source,
)

from ce3.events.models import (
    EventSeverity,
    EventType,
)

from ce3.events.normalization import (
    normalize_claim_to_event,
)


def test_claim_can_be_normalized_into_event():
    graph = ProvenanceGraph()

    graph.add_source(
        Source(
            id="S1",
            name="Test Source",
            source_type="media",
            independence_family="F1",
            historical_reliability=0.9,
        )
    )

    now = datetime.now(timezone.utc)

    graph.add_observation(
        Observation(
            id="O1",
            source_id="S1",
            observed_at=now,
            ingested_at=now,
            content="Facility X was damaged.",
        )
    )

    graph.add_claim(
        Claim(
            id="C1",
            proposition="Facility X was damaged.",
            created_at=now,
        )
    )

    graph.link_evidence(
        EvidenceLink(
            observation_id="O1",
            claim_id="C1",
            relation=Relation.SUPPORTS,
            quality=0.9,
        )
    )

    event = normalize_claim_to_event(
        graph,
        "C1",
        conflict_id="TEST-CONFLICT",
        event_id="E1",
        event_type=EventType.FACILITY_DAMAGE,
        title="Facility X damaged",
        description="Facility X sustained damage.",
        severity=EventSeverity.HIGH,
        location="Facility X",
        affected_entities=["Facility X"],
    )

    assert event.id == "E1"

    assert event.conflict_id == "TEST-CONFLICT"

    assert event.event_type == EventType.FACILITY_DAMAGE

    assert event.severity == EventSeverity.HIGH

    assert event.claim_ids == ["C1"]

    assert event.confidence > 0.0