"""
Resilience & Dual-Path Architecture: Countermeasure to Cascading Fail-Closed Outages.
GlacierEQ / APEX Estate — Holographic Mesh Standard.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Any, Optional, TypeVar, Tuple
import time

T = TypeVar("T")


class OperationCriticality(Enum):
    CRITICAL_INVARIANT = "CRITICAL_INVARIANT"      # Hard Fail-Closed: Memory bounds, auth, crypto, flight limits
    OPERATIONAL_WORKFLOW = "OPERATIONAL_WORKFLOW"  # Graceful Degradation: Search, cache, ingestion, telemetry


class CircuitState(Enum):
    CLOSED = "CLOSED"        # Normal execution
    OPEN = "OPEN"            # Fast-failing to protect downstream mesh
    HALF_OPEN = "HALF_OPEN"  # Testing downstream recovery


@dataclass
class ResilienceResult:
    success: bool
    status_code: str
    degraded: bool
    data: Optional[Any]
    reason: str
    execution_time_ms: float


class CircuitBreaker:
    """
    Prevents cascading fail-closed outages by tracking failures and
    short-circuiting calls with fallback data when error thresholds are breached.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_sec: float = 30.0,
        half_open_success_threshold: int = 2,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.half_open_success_threshold = half_open_success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.consecutive_successes = 0
        self.last_failure_time = 0.0

    def record_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self.consecutive_successes += 1
            if self.consecutive_successes >= self.half_open_success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.consecutive_successes = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self) -> None:
        self.last_failure_time = time.time()
        self.failure_count += 1
        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def allow_execution(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout_sec:
                self.state = CircuitState.HALF_OPEN
                self.consecutive_successes = 0
                return True
            return False
        # HALF_OPEN allows single test probes
        return True


class DualPathRouter:
    """
    Routes execution through appropriate resilience paths:
    - CRITICAL_INVARIANT: Refuses immediately with hard failure codes (No fallbacks permitted).
    - OPERATIONAL_WORKFLOW: Degrades gracefully, returns fallbacks, routes anomalies to DLQs.
    """

    @classmethod
    def execute(
        cls,
        criticality: OperationCriticality,
        primary_action: Callable[[], T],
        fallback_action: Optional[Callable[[Exception], T]] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
    ) -> ResilienceResult:
        start_time = time.time()

        # Check circuit breaker if operational workflow
        if criticality == OperationCriticality.OPERATIONAL_WORKFLOW and circuit_breaker:
            if not circuit_breaker.allow_execution():
                fallback_data = fallback_action(Exception("Circuit breaker OPEN")) if fallback_action else None
                elapsed = (time.time() - start_time) * 1000
                return ResilienceResult(
                    success=fallback_data is not None,
                    status_code="CIRCUIT_OPEN_DEGRADED",
                    degraded=True,
                    data=fallback_data,
                    reason="Downstream circuit breaker is OPEN; served fallback without cascading",
                    execution_time_ms=elapsed,
                )

        try:
            result = primary_action()
            if circuit_breaker:
                circuit_breaker.record_success()
            elapsed = (time.time() - start_time) * 1000
            return ResilienceResult(
                success=True,
                status_code="SUCCESS",
                degraded=False,
                data=result,
                reason="Nominal execution complete",
                execution_time_ms=elapsed,
            )
        except Exception as e:
            if circuit_breaker:
                circuit_breaker.record_failure()
            elapsed = (time.time() - start_time) * 1000

            # Path A: Critical Invariant -> HARD REFUSAL
            if criticality == OperationCriticality.CRITICAL_INVARIANT:
                return ResilienceResult(
                    success=False,
                    status_code="ERR_INVARIANT_HARD_REFUSAL",
                    degraded=False,
                    data=None,
                    reason=f"Safety-critical invariant breached: {str(e)}",
                    execution_time_ms=elapsed,
                )

            # Path B: Operational Workflow -> GRACEFUL DEGRADATION
            if fallback_action:
                try:
                    fallback_val = fallback_action(e)
                    return ResilienceResult(
                        success=True,
                        status_code="WARN_OPERATIONAL_DEGRADED",
                        degraded=True,
                        data=fallback_val,
                        reason=f"Primary action failed ({str(e)}); served fallback",
                        execution_time_ms=elapsed,
                    )
                except Exception as fb_err:
                    return ResilienceResult(
                        success=False,
                        status_code="ERR_FALLBACK_FAILED",
                        degraded=True,
                        data=None,
                        reason=f"Both primary and fallback failed: {str(fb_err)}",
                        execution_time_ms=elapsed,
                    )

            return ResilienceResult(
                success=False,
                status_code="ERR_OPERATIONAL_ERROR",
                degraded=False,
                data=None,
                reason=f"Operational error without fallback: {str(e)}",
                execution_time_ms=elapsed,
            )
