"""
Tests for Sandbox Spike Manager (Fix 1: Beating Cold-Start Paralysis).
"""

import tempfile
from pathlib import Path
import pytest
from src.apex_process.core.epistemic import SpikeManager
from src.apex_process.core.taxonomy import EpistemicTier


def test_create_and_check_spike_active():
    with tempfile.TemporaryDirectory() as tmpdir:
        spike_path = Path(tmpdir) / "spikes" / "prototype_alpha"
        mpath = SpikeManager.create_spike(spike_path, "prototype_alpha", "Testing new algorithm", ttl_hours=24.0)
        assert mpath.is_file()

        active, msg = SpikeManager.check_spike_status(spike_path)
        assert active is True
        assert "ACTIVE" in msg


def test_expired_spike_status():
    with tempfile.TemporaryDirectory() as tmpdir:
        spike_path = Path(tmpdir) / "spikes" / "old_spike"
        # Negative TTL to simulate expiration
        SpikeManager.create_spike(spike_path, "old_spike", "Expired exploration", ttl_hours=-1.0)

        active, msg = SpikeManager.check_spike_status(spike_path)
        assert active is False
        assert "EXPIRED" in msg


def test_spike_graduation_gates():
    with tempfile.TemporaryDirectory() as tmpdir:
        spike_path = Path(tmpdir) / "spikes" / "grad_spike"
        SpikeManager.create_spike(spike_path, "grad_spike", "Validating production promotion")

        # Graduation fails if tests missing or stubs present
        grad1, msg1 = SpikeManager.graduate_spike(spike_path, has_passing_tests=False, zero_stubs=True)
        assert grad1 is False
        assert "denied" in msg1.lower()

        # Graduation succeeds when tests pass and stubs are 0
        grad2, msg2 = SpikeManager.graduate_spike(spike_path, has_passing_tests=True, zero_stubs=True)
        assert grad2 is True
        assert "graduated" in msg2.lower()
