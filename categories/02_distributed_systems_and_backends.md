# 🌐 CATEGORY 02: High-Throughput Distributed Systems & Backends

## 1. Scope & Architectural Mandate
Governs horizontally scalable, fault-tolerant, concurrent microservices, distributed state machines, consensus protocols, and RPC communication grids.

- **Domains**: gRPC microservices, Raft consensus logs, Conflict-Free Replicated Data Types (CRDTs), message broker topologies (Kafka/BullMQ), ACID/BASE database architectures, distributed transaction managers (2PC/Saga).
- **Key Constraints**: Partition tolerance (CAP theorem), high throughput (10k+ rps), deterministic event ordering, idempotent execution, graceful degradation under network partitions.

---

## 2. Polyglot Technology Stack
- **Primary Languages**: Go (concurrency, lightweight goroutines, networking), Rust (high-performance state engines), Python (distributed orchestration & ETL), TypeScript/Node (MCP gateways & fast APIs).
- **Protocols & Formats**: Protocol Buffers (`protobuf`), Cap'n Proto (zero-copy RPC), gRPC, WebSockets, HTTP/2 & HTTP/3.
- **Data Layers**: PostgreSQL / Supabase, Redis (distributed lock & cache), DuckDB, ClickHouse.

---

## 3. Core Invariants & Fail-Closed Boundaries
1. **Idempotency Invariant**:
   - Every mutation RPC must accept a unique `idempotency_key`.
   - Replaying the same request must yield the identical state receipt without side effects.
2. **Consensus & Ordering**:
   - Updates must use monotonically increasing term/epoch numbers or vector clocks.
   - Stale writes from split-brain leaders must be rejected with explicit fencing tokens.
3. **Refusal Reason Codes**:
   - `ERR_DIST_SPLIT_BRAIN`: Write rejected due to outdated term or invalid leader lease.
   - `ERR_DIST_IDEMPOTENCY_COLLISION`: Conflicting payload submitted for an existing idempotency key.
   - `ERR_DIST_QUORUM_UNAVAILABLE`: Insufficient node replicas available to reach consensus.
   - `ERR_DIST_DESERIALIZATION_FAILURE`: Malformed protobuf payload or unmapped enum index.
   - `ERR_DIST_CIRCUIT_OPEN`: Downstream service degraded; fast failure triggered to prevent cascade.

---

## 4. Stage-by-Stage Implementation Guide

### Stage 0: Contracting
- Define throughput SLAs, consistency level (linearizable vs eventual), and replication factor.
- Enumerate failure domains (e.g., loss of 1 of 3 nodes, network partitions).

### Stage 1: Architectural Modeling
- Define `.proto` schemas with strict backward and forward compatibility rules.
- Draft state transition diagrams for distributed transactions or Raft elections.

### Stage 2: Pro-Code Implementation
- Implement connection pooling, heartbeat health probes, and backoff retries with jitter.
- Enforce structured logging with trace IDs propagated across RPC boundaries.

### Stage 3: Adversarial Verification
- Execute chaos tests: simulate network packet drop, latency injection, kill leader node.
- Assert that split-brain writes fail-closed with `ERR_DIST_SPLIT_BRAIN`.

---

## 5. Reference Pattern: Idempotent Log Entry Committer
```python
from typing import Dict, Any, Optional
import hashlib
import time

class DistributedCommitter:
    def __init__(self, current_term: int):
        self.current_term = current_term
        self.seen_keys: Dict[str, Dict[str, Any]] = {}
        self.commit_log: list = []

    def commit_transaction(self, term: int, idempotency_key: str, payload: dict) -> Dict[str, Any]:
        # Fail-closed split-brain guard
        if term < self.current_term:
            return {
                "status": "REFUSED",
                "code": "ERR_DIST_SPLIT_BRAIN",
                "details": f"Term {term} is older than leader term {self.current_term}"
            }
        
        # Idempotency cache check
        if idempotency_key in self.seen_keys:
            existing = self.seen_keys[idempotency_key]
            # Verify payload hash matches
            payload_hash = hashlib.sha256(str(sorted(payload.items())).encode()).hexdigest()
            if existing["payload_hash"] != payload_hash:
                return {
                    "status": "REFUSED",
                    "code": "ERR_DIST_IDEMPOTENCY_COLLISION",
                    "details": "Payload mismatch for existing key"
                }
            return {"status": "SUCCESS", "receipt": existing["receipt"], "replayed": True}

        # Commit entry
        receipt = hashlib.sha256(f"{term}:{idempotency_key}:{time.time()}".encode()).hexdigest()
        payload_hash = hashlib.sha256(str(sorted(payload.items())).encode()).hexdigest()
        entry = {
            "term": term,
            "key": idempotency_key,
            "payload": payload,
            "receipt": receipt,
            "payload_hash": payload_hash
        }
        self.commit_log.append(entry)
        self.seen_keys[idempotency_key] = entry
        return {"status": "SUCCESS", "receipt": receipt, "replayed": False}
```
