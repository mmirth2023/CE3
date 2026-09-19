from datetime import datetime, timezone

from ce3.evidence.provenance import (
    Claim,
    EvidenceLink,
    Observation,
    ProvenanceGraph,
    Relation,
    Source,
)
from ce3.evidence.fusion import claim_evidence_profile


def test_independence_and_contradiction():
    graph = ProvenanceGraph()

    graph.add_source(
        Source(
            id="S1",
            name="Publisher A",
            source_type="media",
            independence_family="F1",
            historical_reliability=0.9,
        )
    )

    graph.add_source(
        Source(
            id="S2",
            name="Publisher B",
            source_type="media",
            independence_family="F1",
            historical_reliability=0.8,
        )
    )

    graph.add_source(
        Source(
            id="S3",
            name="Satellite",
            source_type="satellite",
            independence_family="F2",
            historical_reliability=0.95,
        )
    )

    graph.add_source(
        Source(
            id="S4",
            name="Local Observer",
            source_type="observer",
            independence_family="F3",
            historical_reliability=0.7,
        )
    )

    now = datetime.now(timezone.utc)

    graph.add_observation(
        Observation(
            id="O1",
            source_id="S1",
            observed_at=now,
            ingested_at=now,
            content="Publisher A reports damage.",
        )
    )

    graph.add_observation(
        Observation(
            id="O2",
            source_id="S2",
            observed_at=now,
            ingested_at=now,
            content="Publisher B reports damage.",
        )
    )

    graph.add_observation(
        Observation(
            id="O3",
            source_id="S3",
            observed_at=now,
            ingested_at=now,
            content="Satellite imagery shows structural damage.",
        )
    )

    graph.add_observation(
        Observation(
            id="O4",
            source_id="S4",
            observed_at=now,
            ingested_at=now,
            content="Local observer reports no visible damage.",
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

    graph.link_evidence(
        EvidenceLink(
            observation_id="O2",
            claim_id="C1",
            relation=Relation.SUPPORTS,
            quality=0.9,
        )
    )

    graph.link_evidence(
        EvidenceLink(
            observation_id="O3",
            claim_id="C1",
            relation=Relation.SUPPORTS,
            quality=0.8,
        )
    )

    graph.link_evidence(
        EvidenceLink(
            observation_id="O4",
            claim_id="C1",
            relation=Relation.CONTRADICTS,
            quality=0.6,
        )
    )

    profile = claim_evidence_profile(
        graph,
        "C1",
    )

    assert profile["evidence_count"] == 4

    assert profile["support_count"] == 3

    assert profile["contradiction_count"] == 1

    assert profile["independence_family_count"] == 3

    assert profile["evidence_independence_density"] == 0.75

    assert profile["weighted_support"] > 0.0

    assert profile["weighted_contradiction"] > 0.0