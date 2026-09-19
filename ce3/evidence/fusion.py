from __future__ import annotations

from typing import Any

from .provenance import (
    EvidenceLink,
    ProvenanceGraph,
    Relation,
)


def _saturating_combine(scores: list[float]) -> float:
    """
    Combine independent evidence signals without allowing repeated
    evidence to increase the score linearly.

    This is a diagnostic aggregation mechanism, not a calibrated
    probability.
    """

    remaining = 1.0
    combined = 0.0

    for score in sorted(scores, reverse=True):
        score = max(0.0, min(1.0, score))

        combined += remaining * score
        remaining *= 1.0 - score

    return combined


def weighted_claim_support(
    graph: ProvenanceGraph,
    claim_id: str,
) -> float:
    """
    Calculate diagnostic support for a claim.

    Evidence from the same independence family is reduced to its
    strongest supporting signal before families are combined.
    """

    family_scores: dict[str, float] = {}

    for link in graph.evidence_for_claim(claim_id):
        if link.relation != Relation.SUPPORTS:
            continue

        observation = graph.observations[link.observation_id]
        source = graph.sources[observation.source_id]

        score = link.quality * source.historical_reliability

        family = source.independence_family

        family_scores[family] = max(
            family_scores.get(family, 0.0),
            score,
        )

    return _saturating_combine(list(family_scores.values()))


def weighted_claim_contradiction(
    graph: ProvenanceGraph,
    claim_id: str,
) -> float:
    """
    Calculate diagnostic contradiction strength.

    Contradictory evidence is grouped by independence family in the
    same manner as supporting evidence.
    """

    family_scores: dict[str, float] = {}

    for link in graph.evidence_for_claim(claim_id):
        if link.relation != Relation.CONTRADICTS:
            continue

        observation = graph.observations[link.observation_id]
        source = graph.sources[observation.source_id]

        score = link.quality * source.historical_reliability

        family = source.independence_family

        family_scores[family] = max(
            family_scores.get(family, 0.0),
            score,
        )

    return _saturating_combine(list(family_scores.values()))


def claim_evidence_profile(
    graph: ProvenanceGraph,
    claim_id: str,
) -> dict[str, Any]:
    """
    Produce the structured evidence profile for a claim.

    The output deliberately separates evidence strength,
    independence, contradiction and diagnostic scores.
    """

    evidence_links = graph.evidence_for_claim(claim_id)

    support_links = [
        link
        for link in evidence_links
        if link.relation == Relation.SUPPORTS
    ]

    contradiction_links = [
        link
        for link in evidence_links
        if link.relation == Relation.CONTRADICTS
    ]

    support_families: set[str] = set()
    contradiction_families: set[str] = set()

    for link in support_links:
        observation = graph.observations[link.observation_id]
        source = graph.sources[observation.source_id]
        support_families.add(source.independence_family)

    for link in contradiction_links:
        observation = graph.observations[link.observation_id]
        source = graph.sources[observation.source_id]
        contradiction_families.add(source.independence_family)

    total_families = support_families | contradiction_families

    independence_density = (
        len(total_families) / len(evidence_links)
        if evidence_links
        else 0.0
    )

    support_score = weighted_claim_support(
        graph,
        claim_id,
    )

    contradiction_score = weighted_claim_contradiction(
        graph,
        claim_id,
    )

    return {
        "claim_id": claim_id,

        "evidence_count": len(evidence_links),

        "support_count": len(support_links),
        "contradiction_count": len(contradiction_links),

        "support_independence_families": sorted(
            support_families
        ),

        "contradiction_independence_families": sorted(
            contradiction_families
        ),

        "independence_family_count": len(
            total_families
        ),

        "evidence_independence_density": independence_density,

        "weighted_support": support_score,

        "weighted_contradiction": contradiction_score,

        "net_diagnostic_signal": (
            support_score - contradiction_score
        ),

        "interpretation": (
            "Diagnostic aggregation only; "
            "not a calibrated probability."
        ),
    }