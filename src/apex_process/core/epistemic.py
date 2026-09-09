"""
Epistemic Gate & 6-Tier Epistemic Ladder Evaluator.
GlacierEQ / APEX Estate — Anti-Hallucination Law.
"""

from typing import Dict, Any, List, Optional
import time
import hashlib
from .taxonomy import EpistemicTier


class EpistemicGate:
    """
    Enforces the Ascended 6-Tier Epistemic Ladder (L0 to L6).
    Guarantees the Epistemic Law of Action:
        Action Authorized <=> State >= L2 (Behavioral Proof)
        Enterprise Deliverable <=> State >= L5 (Dialectic Swarm Consensus)
    """

    TIER_RANK: Dict[EpistemicTier, int] = {
        EpistemicTier.L0_PRESENCE: 0,
        EpistemicTier.L1_STRUCTURE: 1,
        EpistemicTier.L2_BEHAVIOR: 2,
        EpistemicTier.L3_BACKEND: 3,
        EpistemicTier.L4_TELEMETRY: 4,
        EpistemicTier.L5_SWARM: 5,
        EpistemicTier.L6_AUTONOMY: 6,
    }

    @classmethod
    def evaluate_tier(
        cls,
        has_file_presence: bool,
        has_valid_ast: bool,
        tests_passed: bool,
        has_crypto_receipt: bool,
        has_live_backend: bool = False,
        has_telemetry: bool = False,
        has_swarm_consensus: bool = False,
        has_upstream_tracking: bool = False,
    ) -> EpistemicTier:
        """Determines the exact epistemic tier based on empirical proof."""
        if not has_file_presence:
            raise ValueError("ERR_EPISTEMIC_NONEXISTENT: Artifact does not exist on disk (below L0)")

        if not has_valid_ast:
            return EpistemicTier.L0_PRESENCE

        if not (tests_passed and has_crypto_receipt):
            return EpistemicTier.L1_STRUCTURE

        # Base L2 achieved
        current = EpistemicTier.L2_BEHAVIOR

        if has_live_backend:
            current = EpistemicTier.L3_BACKEND
            if has_telemetry:
                current = EpistemicTier.L4_TELEMETRY
                if has_swarm_consensus:
                    current = EpistemicTier.L5_SWARM
                    if has_upstream_tracking:
                        current = EpistemicTier.L6_AUTONOMY

        return current

    @classmethod
    def is_action_authorized(cls, tier: EpistemicTier) -> bool:
        """The Epistemic Law of Action: Local operational mutations require state >= L2."""
        return cls.TIER_RANK[tier] >= cls.TIER_RANK[EpistemicTier.L2_BEHAVIOR]

    @classmethod
    def is_enterprise_ready(cls, tier: EpistemicTier) -> bool:
        """Enterprise deliverables require state >= L5 (Dialectic Swarm Consensus)."""
        return cls.TIER_RANK[tier] >= cls.TIER_RANK[EpistemicTier.L5_SWARM]

    @classmethod
    def generate_verification_record(
        cls,
        claim_description: str,
        assigned_tier: EpistemicTier,
        evidence_files: List[str],
        test_assertions_count: int,
        operator_signature: str = "APEX-OPERATOR-G",
    ) -> Dict[str, Any]:
        """Produces a tamper-evident epistemic verification record."""
        timestamp = time.time()
        authorized = cls.is_action_authorized(assigned_tier)
        enterprise = cls.is_enterprise_ready(assigned_tier)

        raw_payload = f"{claim_description}:{assigned_tier.value}:{test_assertions_count}:{timestamp}"
        record_hash = hashlib.sha256(raw_payload.encode()).hexdigest()

        return {
            "record_id": f"EPI-REC-{record_hash[:12]}",
            "claim": claim_description,
            "epistemic_tier": assigned_tier.value,
            "action_authorized": authorized,
            "enterprise_ready": enterprise,
            "test_assertions_count": test_assertions_count,
            "evidence_files": evidence_files,
            "timestamp": timestamp,
            "sha256_receipt": record_hash,
            "operator_signature": operator_signature,
            "law_of_action_compliant": authorized,
        }
