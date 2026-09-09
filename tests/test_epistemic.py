"""
Tests for Epistemic Gate & 6-Tier Epistemic Ladder.
"""

import pytest
from src.apex_process.core.epistemic import EpistemicGate
from src.apex_process.core.taxonomy import EpistemicTier


def test_epistemic_tier_evaluation_l0():
    tier = EpistemicGate.evaluate_tier(
        has_file_presence=True,
        has_valid_ast=False,
        tests_passed=False,
        has_crypto_receipt=False,
    )
    assert tier == EpistemicTier.L0_PRESENCE
    assert EpistemicGate.is_action_authorized(tier) is False


def test_epistemic_tier_evaluation_l1():
    tier = EpistemicGate.evaluate_tier(
        has_file_presence=True,
        has_valid_ast=True,
        tests_passed=False,
        has_crypto_receipt=False,
    )
    assert tier == EpistemicTier.L1_STRUCTURE
    assert EpistemicGate.is_action_authorized(tier) is False


def test_epistemic_tier_evaluation_l2():
    tier = EpistemicGate.evaluate_tier(
        has_file_presence=True,
        has_valid_ast=True,
        tests_passed=True,
        has_crypto_receipt=True,
    )
    assert tier == EpistemicTier.L2_BEHAVIOR
    assert EpistemicGate.is_action_authorized(tier) is True
    assert EpistemicGate.is_enterprise_ready(tier) is False


def test_epistemic_tier_evaluation_l5_swarm():
    tier = EpistemicGate.evaluate_tier(
        has_file_presence=True,
        has_valid_ast=True,
        tests_passed=True,
        has_crypto_receipt=True,
        has_live_backend=True,
        has_telemetry=True,
        has_swarm_consensus=True,
    )
    assert tier == EpistemicTier.L5_SWARM
    assert EpistemicGate.is_action_authorized(tier) is True
    assert EpistemicGate.is_enterprise_ready(tier) is True


def test_epistemic_tier_evaluation_l6_autonomy():
    tier = EpistemicGate.evaluate_tier(
        has_file_presence=True,
        has_valid_ast=True,
        tests_passed=True,
        has_crypto_receipt=True,
        has_live_backend=True,
        has_telemetry=True,
        has_swarm_consensus=True,
        has_upstream_tracking=True,
    )
    assert tier == EpistemicTier.L6_AUTONOMY
    assert EpistemicGate.is_action_authorized(tier) is True
    assert EpistemicGate.is_enterprise_ready(tier) is True


def test_epistemic_nonexistent_file_raises_error():
    with pytest.raises(ValueError, match="ERR_EPISTEMIC_NONEXISTENT"):
        EpistemicGate.evaluate_tier(
            has_file_presence=False,
            has_valid_ast=False,
            tests_passed=False,
            has_crypto_receipt=False,
        )


def test_epistemic_verification_record_generation():
    rec = EpistemicGate.generate_verification_record(
        claim_description="Verify bounded ring buffer",
        assigned_tier=EpistemicTier.L2_BEHAVIOR,
        evidence_files=["src/apex_process/reference/systems_buffer.py"],
        test_assertions_count=12,
    )
    assert rec["action_authorized"] is True
    assert rec["enterprise_ready"] is False
    assert rec["epistemic_tier"] == "L2_BEHAVIOR"
    assert rec["test_assertions_count"] == 12
    assert "sha256_receipt" in rec
    assert len(rec["sha256_receipt"]) == 64
