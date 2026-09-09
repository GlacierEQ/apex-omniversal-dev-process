"""
Tests for Dual-Path Resilience & Circuit Breakers (Fix 3: Anti-Cascading Outages).
"""

import pytest
import time
from src.apex_process.core.resilience import (
    DualPathRouter,
    CircuitBreaker,
    CircuitState,
    OperationCriticality,
    ResilienceResult,
)


def test_critical_invariant_fails_closed_without_fallback():
    def failing_safety_check():
        raise ValueError("Memory buffer corrupted")

    def mock_fallback(err):
        return "insecure_fallback_data"

    # Critical invariant MUST refuse and ignore fallback
    res = DualPathRouter.execute(
        criticality=OperationCriticality.CRITICAL_INVARIANT,
        primary_action=failing_safety_check,
        fallback_action=mock_fallback,
    )

    assert res.success is False
    assert res.status_code == "ERR_INVARIANT_HARD_REFUSAL"
    assert res.data is None
    assert "safety-critical invariant breached" in res.reason.lower()


def test_operational_workflow_degrades_gracefully_with_fallback():
    def failing_cache_read():
        raise TimeoutError("Redis cache connection timed out")

    def stale_cache_fallback(err):
        return {"cached_items": ["item1", "item2"], "stale": True}

    res = DualPathRouter.execute(
        criticality=OperationCriticality.OPERATIONAL_WORKFLOW,
        primary_action=failing_cache_read,
        fallback_action=stale_cache_fallback,
    )

    assert res.success is True
    assert res.degraded is True
    assert res.status_code == "WARN_OPERATIONAL_DEGRADED"
    assert res.data == {"cached_items": ["item1", "item2"], "stale": True}


def test_circuit_breaker_tripping_and_recovery():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_sec=0.1, half_open_success_threshold=1)
    assert cb.state == CircuitState.CLOSED

    # Failure 1
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED

    # Failure 2: breaches threshold -> trips to OPEN
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.allow_execution() is False

    # Wait for recovery timeout
    time.sleep(0.12)
    # Probing transition to HALF_OPEN
    assert cb.allow_execution() is True
    assert cb.state == CircuitState.HALF_OPEN

    # Probe succeeds -> resets to CLOSED
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
