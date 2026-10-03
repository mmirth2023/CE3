from __future__ import annotations

from datetime import datetime
from typing import Any

from .models import (
    PropagationPath,
    PropagationStatus,
    PropagationType,
)


class PropagationEngine:
    """
    Constructs canonical propagation paths from explicitly supplied
    structural and evidentiary information.

    The engine represents how a change may move between system
    components.

    It does not:
    - infer causality,
    - predict future outcomes,
    - assess economic consequences,
    - determine regime transitions,
    - assign calibrated probabilities.
    """

    def build(
        self,
        *,
        propagation_id: str,
        source_id: str,
        target_id: str,
        propagation_type: PropagationType,
        identified_at: datetime,
        status: PropagationStatus = PropagationStatus.UNKNOWN,
        strength: float = 0.0,
        confidence: float = 1.0,
        relationship_id: str | None = None,
        dependency_id: str | None = None,
        intermediate_ids: list[str] | None = None,
        source_event_ids: list[str] | None = None,
        source_observation_ids: list[str] | None = None,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        rationale: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> PropagationPath:
        """
        Construct a propagation path from explicitly supplied inputs.
        """
        return PropagationPath(
            id=propagation_id,
            source_id=source_id,
            target_id=target_id,
            propagation_type=propagation_type,
            status=status,
            identified_at=identified_at,
            valid_from=valid_from,
            valid_to=valid_to,
            strength=strength,
            confidence=confidence,
            relationship_id=relationship_id,
            dependency_id=dependency_id,
            intermediate_ids=intermediate_ids or [],
            source_event_ids=source_event_ids or [],
            source_observation_ids=source_observation_ids or [],
            rationale=rationale,
            metadata=metadata or {},
        )

    def build_observed(
        self,
        *,
        propagation_id: str,
        source_id: str,
        target_id: str,
        propagation_type: PropagationType,
        identified_at: datetime,
        strength: float = 0.0,
        confidence: float = 1.0,
        relationship_id: str | None = None,
        dependency_id: str | None = None,
        intermediate_ids: list[str] | None = None,
        source_event_ids: list[str] | None = None,
        source_observation_ids: list[str] | None = None,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        rationale: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> PropagationPath:
        """
        Construct a propagation path explicitly classified as observed.
        """
        return self.build(
            propagation_id=propagation_id,
            source_id=source_id,
            target_id=target_id,
            propagation_type=propagation_type,
            identified_at=identified_at,
            status=PropagationStatus.OBSERVED,
            strength=strength,
            confidence=confidence,
            relationship_id=relationship_id,
            dependency_id=dependency_id,
            intermediate_ids=intermediate_ids,
            source_event_ids=source_event_ids,
            source_observation_ids=source_observation_ids,
            valid_from=valid_from,
            valid_to=valid_to,
            rationale=rationale,
            metadata=metadata,
        )

    def build_supported(
        self,
        *,
        propagation_id: str,
        source_id: str,
        target_id: str,
        propagation_type: PropagationType,
        identified_at: datetime,
        strength: float = 0.0,
        confidence: float = 1.0,
        relationship_id: str | None = None,
        dependency_id: str | None = None,
        intermediate_ids: list[str] | None = None,
        source_event_ids: list[str] | None = None,
        source_observation_ids: list[str] | None = None,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        rationale: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> PropagationPath:
        """
        Construct a propagation path explicitly classified as supported.
        """
        return self.build(
            propagation_id=propagation_id,
            source_id=source_id,
            target_id=target_id,
            propagation_type=propagation_type,
            identified_at=identified_at,
            status=PropagationStatus.SUPPORTED,
            strength=strength,
            confidence=confidence,
            relationship_id=relationship_id,
            dependency_id=dependency_id,
            intermediate_ids=intermediate_ids,
            source_event_ids=source_event_ids,
            source_observation_ids=source_observation_ids,
            valid_from=valid_from,
            valid_to=valid_to,
            rationale=rationale,
            metadata=metadata,
        )

    def build_structurally_possible(
        self,
        *,
        propagation_id: str,
        source_id: str,
        target_id: str,
        propagation_type: PropagationType,
        identified_at: datetime,
        strength: float = 0.0,
        confidence: float = 1.0,
        relationship_id: str | None = None,
        dependency_id: str | None = None,
        intermediate_ids: list[str] | None = None,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        rationale: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> PropagationPath:
        """
        Construct a propagation path explicitly classified as
        structurally possible.

        This represents structural connectivity rather than observed
        transmission.
        """
        return self.build(
            propagation_id=propagation_id,
            source_id=source_id,
            target_id=target_id,
            propagation_type=propagation_type,
            identified_at=identified_at,
            status=PropagationStatus.STRUCTURALLY_POSSIBLE,
            strength=strength,
            confidence=confidence,
            relationship_id=relationship_id,
            dependency_id=dependency_id,
            intermediate_ids=intermediate_ids,
            valid_from=valid_from,
            valid_to=valid_to,
            rationale=rationale,
            metadata=metadata,
        )

    def build_contradicted(
        self,
        *,
        propagation_id: str,
        source_id: str,
        target_id: str,
        propagation_type: PropagationType,
        identified_at: datetime,
        strength: float = 0.0,
        confidence: float = 1.0,
        relationship_id: str | None = None,
        dependency_id: str | None = None,
        intermediate_ids: list[str] | None = None,
        source_event_ids: list[str] | None = None,
        source_observation_ids: list[str] | None = None,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        rationale: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> PropagationPath:
        """
        Construct a propagation path explicitly classified as contradicted.
        """
        return self.build(
            propagation_id=propagation_id,
            source_id=source_id,
            target_id=target_id,
            propagation_type=propagation_type,
            identified_at=identified_at,
            status=PropagationStatus.CONTRADICTED,
            strength=strength,
            confidence=confidence,
            relationship_id=relationship_id,
            dependency_id=dependency_id,
            intermediate_ids=intermediate_ids,
            source_event_ids=source_event_ids,
            source_observation_ids=source_observation_ids,
            valid_from=valid_from,
            valid_to=valid_to,
            rationale=rationale,
            metadata=metadata,
        )