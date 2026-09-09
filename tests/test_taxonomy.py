"""
Tests for taxonomy: 12 Categories, 9 Lifecycle Stages, 10 Bodybuilder Gates.
"""

import pytest
from src.apex_process.core.taxonomy import (
    CATEGORIES,
    LIFECYCLE_STAGES,
    BODYBUILDER_GATES,
    EPISTEMIC_TIERS,
    EpistemicTier,
)


def test_categories_count_and_numbering():
    assert len(CATEGORIES) == 12
    numbers = [c.number for c in CATEGORIES.values()]
    assert sorted(numbers) == list(range(1, 13))


def test_category_required_fields():
    for cat_id, cat in CATEGORIES.items():
        assert cat.id == cat_id
        assert len(cat.name) > 5
        assert len(cat.description) > 15
        assert len(cat.primary_languages) >= 2
        assert len(cat.critical_invariants) >= 2
        assert len(cat.common_refusal_codes) >= 3
        # Check that refusal codes follow ERR_* format
        for code in cat.common_refusal_codes:
            assert code.startswith("ERR_")


def test_lifecycle_stages_count_and_ordering():
    assert len(LIFECYCLE_STAGES) == 9
    stage_nums = [s.stage_number for s in LIFECYCLE_STAGES]
    assert stage_nums == list(range(9))


def test_lifecycle_stage_epistemic_monotony():
    # Verify stages advance or maintain epistemic tier
    tier_ranks = {
        EpistemicTier.L0_PRESENCE: 0,
        EpistemicTier.L1_STRUCTURE: 1,
        EpistemicTier.L2_BEHAVIOR: 2,
        EpistemicTier.L3_BACKEND: 3,
        EpistemicTier.L4_TELEMETRY: 4,
        EpistemicTier.L5_SWARM: 5,
        EpistemicTier.L6_AUTONOMY: 6,
    }
    ranks = [tier_ranks[s.epistemic_level] for s in LIFECYCLE_STAGES]
    for i in range(len(ranks) - 1):
        assert ranks[i] <= ranks[i + 1], f"Stage {i} ({ranks[i]}) regressed at stage {i+1} ({ranks[i+1]})"


def test_bodybuilder_gates_count_and_ids():
    assert len(BODYBUILDER_GATES) == 10
    gate_ids = [g.gate_id for g in BODYBUILDER_GATES]
    assert gate_ids == [f"G{i}" for i in range(10)]


def test_epistemic_tiers_descriptions():
    assert len(EPISTEMIC_TIERS) == 7
    assert "L0" in EPISTEMIC_TIERS
    assert "L2" in EPISTEMIC_TIERS
    assert "L5" in EPISTEMIC_TIERS
