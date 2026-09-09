"""
Category 02 Reference Implementation: Distributed Append-Only Log Committer.
Enforces term monotonicity, split-brain protection, and idempotent commits.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import hashlib
import json
import time

ERR_DIST_SPLIT_BRAIN = "ERR_DIST_SPLIT_BRAIN"
ERR_DIST_IDEMPOTENCY_COLLISION = "ERR_DIST_IDEMPOTENCY_COLLISION"
ERR_DIST_INVALID_PAYLOAD = "ERR_DIST_INVALID_PAYLOAD"


@dataclass(frozen=True)
class DistributedCommitResult:
    success: bool
    status_code: str
    term: int
    idempotency_key: str
    commit_receipt: Optional[str]
    replayed: bool
    details: str


class DistributedLogCommitter:
    """
    Append-only state machine log committer simulating distributed raft/paxos nodes.
    Protects against stale term split-brain scenarios and guarantees strict idempotency.
    """

    def __init__(self, current_term: int = 1):
        if current_term < 1:
            raise ValueError("Current term must be at least 1")
        self.current_term = current_term
        self._commit_log: List[Dict[str, Any]] = []
        self._seen_keys: Dict[str, Dict[str, Any]] = {}

    @property
    def log_length(self) -> int:
        return len(self._commit_log)

    def advance_term(self, new_term: int) -> None:
        if new_term <= self.current_term:
            raise ValueError(f"New term {new_term} must be strictly greater than current {self.current_term}")
        self.current_term = new_term

    def commit(self, term: int, idempotency_key: str, payload: Dict[str, Any]) -> DistributedCommitResult:
        """Commits an idempotent state update under monotonic term governance."""
        # 1. Input sanity
        if not idempotency_key or not isinstance(idempotency_key, str):
            return DistributedCommitResult(
                success=False,
                status_code=ERR_DIST_INVALID_PAYLOAD,
                term=term,
                idempotency_key=str(idempotency_key),
                commit_receipt=None,
                replayed=False,
                details="Idempotency key must be non-empty string",
            )

        if not isinstance(payload, dict):
            return DistributedCommitResult(
                success=False,
                status_code=ERR_DIST_INVALID_PAYLOAD,
                term=term,
                idempotency_key=idempotency_key,
                commit_receipt=None,
                replayed=False,
                details="Payload must be a dictionary",
            )

        # 2. Split-Brain Guard: Refuse outdated terms
        if term < self.current_term:
            return DistributedCommitResult(
                success=False,
                status_code=ERR_DIST_SPLIT_BRAIN,
                term=term,
                idempotency_key=idempotency_key,
                commit_receipt=None,
                replayed=False,
                details=f"Term {term} is outdated compared to active term {self.current_term}",
            )

        payload_json = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()

        # 3. Idempotency Check
        if idempotency_key in self._seen_keys:
            existing = self._seen_keys[idempotency_key]
            if existing["payload_hash"] != payload_hash:
                return DistributedCommitResult(
                    success=False,
                    status_code=ERR_DIST_IDEMPOTENCY_COLLISION,
                    term=term,
                    idempotency_key=idempotency_key,
                    commit_receipt=None,
                    replayed=False,
                    details="Conflicting payload detected for existing idempotency key",
                )
            # Safe replay
            return DistributedCommitResult(
                success=True,
                status_code="SUCCESS",
                term=existing["term"],
                idempotency_key=idempotency_key,
                commit_receipt=existing["commit_receipt"],
                replayed=True,
                details="Idempotent replay; state previously committed",
            )

        # 4. Commit entry
        timestamp = time.time()
        raw_receipt = f"{term}:{idempotency_key}:{payload_hash}:{timestamp}"
        receipt = hashlib.sha256(raw_receipt.encode()).hexdigest()

        entry = {
            "index": len(self._commit_log),
            "term": term,
            "key": idempotency_key,
            "payload": payload,
            "payload_hash": payload_hash,
            "commit_receipt": receipt,
            "timestamp": timestamp,
        }

        self._commit_log.append(entry)
        self._seen_keys[idempotency_key] = entry

        return DistributedCommitResult(
            success=True,
            status_code="SUCCESS",
            term=term,
            idempotency_key=idempotency_key,
            commit_receipt=receipt,
            replayed=False,
            details="Log entry successfully appended to commit ledger",
        )
