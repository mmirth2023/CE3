from __future__ import annotations

from datetime import datetime, timezone

from ce3.evidence.provenance import ProvenanceGraph

from .models import Event, EventSeverity


def normalize_claim_to_event(
    graph: ProvenanceGraph,
    claim_id: str,
    *,
    conflict_id: str,
    event_id: str,
    event_type,
    title: str,
    description: str,
    occurred_at: datetime | None = None,
    detected_at: datetime | None = None,
    severity: EventSeverity = EventSeverity.UNKNOWN,
    location: str | None = None,
    actors: list[str] | None = None,
    affected_entities: list[str] | None = None,
) -> Event:
    """
    Convert a validated claim into a normalized CE³ Event.

    This function does not invent evidence. The event retains the
    originating claim ID so the provenance chain remains auditable.
    """

    if claim_id not in graph.claims:
        raise ValueError(
            f"Unknown claim_id: {claim_id}"
        )

    evidence_profile = _claim_profile(
        graph,
        claim_id,
    )

    now = datetime.now(timezone.utc)

    if occurred_at is None:
        occurred_at = now

    if detected_at is None:
        detected_at = now

    return Event(
        id=event_id,
        conflict_id=conflict_id,
        event_type=event_type,
        occurred_at=occurred_at,
        detected_at=detected_at,
        title=title,
        description=description,
        severity=severity,
        location=location,
        actors=actors or [],
        affected_entities=affected_entities or [],
        claim_ids=[claim_id],
        confidence=evidence_profile,
        metadata={
            "evidence_profile": evidence_profile,
        },
    )


def _claim_profile(
    graph: ProvenanceGraph,
    claim_id: str,
) -> float:
    """
    Produce a conservative diagnostic confidence value.

    This is intentionally not presented as a calibrated probability.
    """

    evidence = graph.evidence_for_claim(claim_id)

    if not evidence:
        return 0.0

    supporting = []
    contradicting = []

    for link in evidence:
        observation = graph.observations[
            link.observation_id
        ]

        source = graph.sources[
            observation.source_id
        ]

        score = (
            link.quality
            * source.historical_reliability
        )

        if link.relation.value == "supports":
            supporting.append(score)

        elif link.relation.value == "contradicts":
            contradicting.append(score)

    support = (
        max(supporting)
        if supporting
        else 0.0
    )

    contradiction = (
        max(contradicting)
        if contradicting
        else 0.0
    )

    return max(
        0.0,
        min(
            1.0,
            support - (contradiction * 0.5),
        ),
    )