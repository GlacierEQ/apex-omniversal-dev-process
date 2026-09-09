"""
Epistemic Gate & 6-Tier Epistemic Ladder Evaluator.
GlacierEQ / APEX Estate — Anti-Hallucination Law & Spike Sandboxing.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import time
import hashlib
import json
import os
from .taxonomy import EpistemicTier


@dataclass
class SpikeManifest:
    spike_name: str
    created_at: float
    ttl_hours: float
    expires_at: float
    epistemic_tier: str
    status: str  # ACTIVE, EXPIRED, GRADUATED
    purpose: str


class SpikeManager:
    """
    Countermeasure against the L2 Cold-Start / Exploration Paralysis.
    Enables rapid zero-to-one prototyping in designated sandbox areas
    with a strict Time-To-Live (TTL), exempt from premature G0-G9 gates
    until graduation to production.
    """

    MANIFEST_NAME = "SPIKE_MANIFEST.json"

    @classmethod
    def create_spike(
        cls,
        spike_dir: Path,
        spike_name: str,
        purpose: str,
        ttl_hours: float = 72.0,
    ) -> Path:
        spike_dir = Path(spike_dir).resolve()
        spike_dir.mkdir(parents=True, exist_ok=True)
        now = time.time()
        expires = now + (ttl_hours * 3600.0)

        data = {
            "spike_name": spike_name,
            "created_at": now,
            "ttl_hours": ttl_hours,
            "expires_at": expires,
            "epistemic_tier": EpistemicTier.L0_SPIKE.value,
            "status": "ACTIVE",
            "purpose": purpose,
            "production_ready": False,
        }

        mpath = spike_dir / cls.MANIFEST_NAME
        with open(mpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return mpath

    @classmethod
    def check_spike_status(cls, spike_dir: Path) -> Tuple[bool, str]:
        """Returns (is_active, status_message)."""
        spike_dir = Path(spike_dir).resolve()
        mpath = spike_dir / cls.MANIFEST_NAME
        if not mpath.is_file():
            return False, "Not a recognized sandbox spike (missing SPIKE_MANIFEST.json)"

        with open(mpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        now = time.time()
        expires = data.get("expires_at", 0.0)
        if now > expires:
            data["status"] = "EXPIRED"
            with open(mpath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return False, f"Spike '{data.get('spike_name')}' EXPIRED at {time.ctime(expires)}"

        return True, f"Spike '{data.get('spike_name')}' ACTIVE (expires in {(expires - now) / 3600:.1f} hours)"

    @classmethod
    def graduate_spike(
        cls,
        spike_dir: Path,
        has_passing_tests: bool,
        zero_stubs: bool,
    ) -> Tuple[bool, str]:
        """Graduates a spike to production candidate status only if L2 criteria are met."""
        spike_dir = Path(spike_dir).resolve()
        mpath = spike_dir / cls.MANIFEST_NAME
        if not mpath.is_file():
            return False, "Missing SPIKE_MANIFEST.json"

        if not (has_passing_tests and zero_stubs):
            return False, "Graduation denied: Spike must have 100% green tests and zero stubs before production promotion"

        with open(mpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["status"] = "GRADUATED"
        data["graduated_at"] = time.time()
        data["epistemic_tier"] = EpistemicTier.L2_BEHAVIOR.value
        data["production_ready"] = True

        with open(mpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return True, f"Spike '{data.get('spike_name')}' successfully graduated to L2 production standard"


class EpistemicGate:
    """
    Enforces the Ascended 6-Tier Epistemic Ladder (L0 to L6).
    Guarantees the Epistemic Law of Action:
        Action Authorized <=> State >= L2 (Behavioral Proof)
        Enterprise Deliverable <=> State >= L5 (Dialectic Swarm Consensus)
    """

    TIER_RANK: Dict[EpistemicTier, int] = {
        EpistemicTier.L0_SPIKE: -1,
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
        is_spike: bool = False,
        has_live_backend: bool = False,
        has_telemetry: bool = False,
        has_swarm_consensus: bool = False,
        has_upstream_tracking: bool = False,
    ) -> EpistemicTier:
        """Determines the exact epistemic tier based on empirical proof."""
        if not has_file_presence:
            raise ValueError("ERR_EPISTEMIC_NONEXISTENT: Artifact does not exist on disk (below L0)")

        if is_spike:
            return EpistemicTier.L0_SPIKE

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
        """
        Produces a tamper-evident epistemic verification record.
        Explicitly decouples cryptographic integrity from behavioral correctness.
        """
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
            "sha256_provenance_digest": record_hash,
            "operator_signature": operator_signature,
            "law_of_action_compliant": authorized,
            # Explicit Decoupling of Integrity vs Correctness (Fix 4)
            "epistemic_integrity_notice": (
                "CRITICAL: Cryptographic SHA-256 provenance confirms absence of tampering, "
                "NOT operational correctness. Correctness is established strictly through "
                "verified behavioral test assertions (L2+)."
            ),
        }
