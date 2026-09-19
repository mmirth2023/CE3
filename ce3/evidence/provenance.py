from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Relation(str, Enum):
    """Relationship between evidence objects."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    REFINES = "refines"
    SUPERSEDES = "supersedes"
    DERIVES_FROM = "derives_from"
    DUPLICATES = "duplicates"


class Source(BaseModel):
    """A publisher, sensor, observer, institution, or other origin of evidence."""

    id: str
    name: str
    source_type: str

    independence_family: str

    historical_reliability: float = Field(
        ge=0.0,
        le=1.0,
    )

    metadata: dict[str, Any] = Field(default_factory=dict)


class Observation(BaseModel):
    """A raw observation attributed to a source."""

    id: str
    source_id: str

    observed_at: datetime
    ingested_at: datetime

    content: str

    location: str | None = None

    entities: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


class Claim(BaseModel):
    """A proposition derived from one or more observations."""

    id: str

    proposition: str

    claimant: str | None = None

    created_at: datetime

    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceLink(BaseModel):
    """Links an observation to a claim with an evidentiary relationship."""

    observation_id: str
    claim_id: str

    relation: Relation

    quality: float = Field(
        ge=0.0,
        le=1.0,
    )

    rationale: str | None = None


class ProvenanceGraph(BaseModel):
    """Auditable collection of sources, observations, claims and evidence links."""

    sources: dict[str, Source] = Field(default_factory=dict)

    observations: dict[str, Observation] = Field(default_factory=dict)

    claims: dict[str, Claim] = Field(default_factory=dict)

    evidence_links: list[EvidenceLink] = Field(default_factory=list)

    def add_source(self, source: Source) -> None:
        self.sources[source.id] = source

    def add_observation(self, observation: Observation) -> None:
        if observation.source_id not in self.sources:
            raise ValueError(
                f"Unknown source_id: {observation.source_id}"
            )

        self.observations[observation.id] = observation

    def add_claim(self, claim: Claim) -> None:
        self.claims[claim.id] = claim

    def link_evidence(self, link: EvidenceLink) -> None:
        if link.observation_id not in self.observations:
            raise ValueError(
                f"Unknown observation_id: {link.observation_id}"
            )

        if link.claim_id not in self.claims:
            raise ValueError(
                f"Unknown claim_id: {link.claim_id}"
            )

        self.evidence_links.append(link)

    def evidence_for_claim(self, claim_id: str) -> list[EvidenceLink]:
        return [
            link
            for link in self.evidence_links
            if link.claim_id == claim_id
        ]

    def independence_families_for_claim(
        self,
        claim_id: str,
    ) -> set[str]:
        """Return independent evidence families supporting or contradicting a claim."""

        families: set[str] = set()

        for link in self.evidence_for_claim(claim_id):
            observation = self.observations[link.observation_id]
            source = self.sources[observation.source_id]

            if link.relation in {
                Relation.SUPPORTS,
                Relation.CONTRADICTS,
            }:
                families.add(source.independence_family)

        return families

    def contradiction_count(self, claim_id: str) -> int:
        return sum(
            1
            for link in self.evidence_for_claim(claim_id)
            if link.relation == Relation.CONTRADICTS
        )

    def duplicate_observations(self, claim_id: str) -> list[EvidenceLink]:
        return [
            link
            for link in self.evidence_for_claim(claim_id)
            if link.relation == Relation.DUPLICATES
        ]

    def audit_claim(self, claim_id: str) -> dict[str, Any]:
        """Return the complete provenance trail for a claim."""

        if claim_id not in self.claims:
            raise ValueError(f"Unknown claim_id: {claim_id}")

        links = self.evidence_for_claim(claim_id)

        evidence = []

        for link in links:
            observation = self.observations[link.observation_id]
            source = self.sources[observation.source_id]

            evidence.append(
                {
                    "observation_id": observation.id,
                    "source_id": source.id,
                    "source_name": source.name,
                    "source_type": source.source_type,
                    "independence_family": source.independence_family,
                    "relation": link.relation.value,
                    "quality": link.quality,
                    "observation": observation.content,
                }
            )

        return {
            "claim": self.claims[claim_id].model_dump(),
            "evidence": evidence,
            "independence_families": sorted(
                self.independence_families_for_claim(claim_id)
            ),
            "contradiction_count": self.contradiction_count(claim_id),
        }