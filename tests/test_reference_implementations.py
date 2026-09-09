"""
Tests for Reference Implementations: Systems Buffer, Distributed Log, Swarm Dialectic, Forensic Bates.
Includes deep adversarial and refusal path assertions.
"""

import tempfile
from pathlib import Path
import pytest

from src.apex_process.reference.systems_buffer import (
    BoundedRingBuffer,
    BufferRefusalError,
    ERR_SYS_BUFFER_OVERFLOW,
    ERR_SYS_BUFFER_UNDERFLOW,
    ERR_SYS_OUT_OF_BOUNDS,
)
from src.apex_process.reference.distributed_log import (
    DistributedLogCommitter,
    ERR_DIST_SPLIT_BRAIN,
    ERR_DIST_IDEMPOTENCY_COLLISION,
    ERR_DIST_INVALID_PAYLOAD,
)
from src.apex_process.reference.agent_dialectic import (
    DialecticConsensusEngine,
    ERR_SWARM_CONSENSUS_REJECTED,
    ERR_SWARM_EMPTY_PROPOSAL,
)
from src.apex_process.reference.security_hasher import (
    ForensicBatesManifestCompiler,
    ERR_SEC_TAMPER_DETECTED,
    ERR_SEC_ZERO_BYTE_EVIDENCE,
    ERR_SEC_FILE_NOT_FOUND,
)


# ============================================================================
# Category 01: BoundedRingBuffer Tests
# ============================================================================

def test_ring_buffer_happy_path():
    buf = BoundedRingBuffer[int](capacity=3)
    assert buf.is_empty is True
    assert buf.is_full is False
    assert buf.count == 0

    buf.push(10)
    buf.push(20)
    assert buf.count == 2
    assert buf.peek(0) == 10
    assert buf.peek(1) == 20

    assert buf.pop() == 10
    assert buf.pop() == 20
    assert buf.is_empty is True


def test_ring_buffer_adversarial_overflow():
    buf = BoundedRingBuffer[str](capacity=2)
    buf.push("A")
    buf.push("B")
    assert buf.is_full is True

    # Third push must raise BufferRefusalError with ERR_SYS_BUFFER_OVERFLOW
    with pytest.raises(BufferRefusalError) as exc_info:
        buf.push("C")
    assert exc_info.value.code == ERR_SYS_BUFFER_OVERFLOW


def test_ring_buffer_adversarial_underflow():
    buf = BoundedRingBuffer[float](capacity=5)
    with pytest.raises(BufferRefusalError) as exc_info:
        buf.pop()
    assert exc_info.value.code == ERR_SYS_BUFFER_UNDERFLOW


def test_ring_buffer_adversarial_out_of_bounds_peek():
    buf = BoundedRingBuffer[int](capacity=4)
    buf.push(99)
    # Peek index 1 when count is 1
    with pytest.raises(BufferRefusalError) as exc_info:
        buf.peek(1)
    assert exc_info.value.code == ERR_SYS_OUT_OF_BOUNDS
    # Negative index
    with pytest.raises(BufferRefusalError) as exc_info:
        buf.peek(-1)
    assert exc_info.value.code == ERR_SYS_OUT_OF_BOUNDS


# ============================================================================
# Category 02: DistributedLogCommitter Tests
# ============================================================================

def test_distributed_committer_happy_path():
    committer = DistributedLogCommitter(current_term=1)
    res = committer.commit(term=1, idempotency_key="tx-100", payload={"account": "A", "delta": 50})
    assert res.success is True
    assert res.status_code == "SUCCESS"
    assert res.replayed is False
    assert res.commit_receipt is not None
    assert committer.log_length == 1


def test_distributed_committer_idempotent_replay():
    committer = DistributedLogCommitter(current_term=1)
    res1 = committer.commit(term=1, idempotency_key="tx-100", payload={"account": "A", "delta": 50})
    # Replay same payload
    res2 = committer.commit(term=1, idempotency_key="tx-100", payload={"account": "A", "delta": 50})
    assert res2.success is True
    assert res2.replayed is True
    assert res2.commit_receipt == res1.commit_receipt
    assert committer.log_length == 1


def test_distributed_committer_adversarial_split_brain_refusal():
    committer = DistributedLogCommitter(current_term=5)
    # Outdated leader term 4
    res = committer.commit(term=4, idempotency_key="tx-stale", payload={"data": "leak"})
    assert res.success is False
    assert res.status_code == ERR_DIST_SPLIT_BRAIN
    assert "outdated" in res.details.lower()


def test_distributed_committer_adversarial_idempotency_collision():
    committer = DistributedLogCommitter(current_term=2)
    committer.commit(term=2, idempotency_key="tx-dup", payload={"v": 1})
    # Replay same key with conflicting payload
    res = committer.commit(term=2, idempotency_key="tx-dup", payload={"v": 999})
    assert res.success is False
    assert res.status_code == ERR_DIST_IDEMPOTENCY_COLLISION


# ============================================================================
# Category 06: DialecticConsensusEngine Tests
# ============================================================================

def test_dialectic_consensus_happy_path():
    engine = DialecticConsensusEngine(task_id="TASK-SWARM-42")
    receipt = engine.evaluate_proposal(
        proposal_text="Implement zero-copy memory ring buffer",
        auditor_approval=True,
        auditor_notes="AST invariants verified; 0 stubs found; 8 tests green.",
    )
    assert receipt.consensus_achieved is True
    assert receipt.status_code == "SUCCESS"
    assert receipt.consensus_digest is not None
    assert len(receipt.consensus_digest) == 64


def test_dialectic_consensus_adversarial_auditor_rejection():
    engine = DialecticConsensusEngine(task_id="TASK-SWARM-43")
    receipt = engine.evaluate_proposal(
        proposal_text="Add return True placeholder mock",
        auditor_approval=False,
        auditor_notes="Detected Gate G8 defect: bare return True stub.",
    )
    assert receipt.consensus_achieved is False
    assert receipt.status_code == ERR_SWARM_CONSENSUS_REJECTED
    assert receipt.consensus_digest is None
    assert "Gate G8 defect" in receipt.audit_notes


def test_dialectic_consensus_adversarial_empty_proposal():
    engine = DialecticConsensusEngine(task_id="TASK-SWARM-44")
    receipt = engine.evaluate_proposal(
        proposal_text="   ",
        auditor_approval=True,
        auditor_notes="N/A",
    )
    assert receipt.consensus_achieved is False
    assert receipt.status_code == ERR_SWARM_EMPTY_PROPOSAL


def test_dialectic_consensus_adversarial_homogeneous_auditor_refusal():
    # If Reasoner == Auditor, must reject (echo chamber prevention)
    engine = DialecticConsensusEngine(
        task_id="TASK-SWARM-45",
        reasoner_id="DEEPSEEK-R1",
        auditor_id="DEEPSEEK-R1",  # Same architecture
    )
    receipt = engine.evaluate_proposal(
        proposal_text="Valid logic",
        auditor_approval=True,
        auditor_notes="Looks fine to me",
    )
    assert receipt.consensus_achieved is False
    assert receipt.status_code == "ERR_SWARM_HOMOGENEOUS_AUDITOR"
    assert "echo-chamber" in receipt.audit_notes


def test_dialectic_consensus_adversarial_missing_compiler_proof():
    engine = DialecticConsensusEngine(task_id="TASK-SWARM-46")
    # Non-zero compiler exit code
    receipt = engine.evaluate_proposal(
        proposal_text="Syntactically broken code",
        auditor_approval=True,
        auditor_notes="I think it passes",
        compiler_exit_code=1,
    )
    assert receipt.consensus_achieved is False
    assert receipt.status_code == "ERR_SWARM_MISSING_COMPILER_PROOF"
    assert receipt.compiler_verified is False


# ============================================================================
# Category 09: ForensicBatesManifestCompiler Tests
# ============================================================================

def test_forensic_bates_compiler_happy_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        td = Path(tmpdir)
        (td / "01_motion.pdf").write_bytes(b"%PDF-1.4 Motion for Relief")
        (td / "02_declaration.pdf").write_bytes(b"%PDF-1.4 Declaration of Operator")

        manifest_path = ForensicBatesManifestCompiler.write_manifest_file(td, prefix="EXHIBIT-")
        assert manifest_path.is_file()

        valid, msgs = ForensicBatesManifestCompiler.verify_bates_integrity(td)
        assert valid is True
        assert len(msgs) == 0


def test_forensic_bates_adversarial_tamper_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        td = Path(tmpdir)
        doc = td / "pleading.pdf"
        doc.write_bytes(b"ORIGINAL LEGAL PLEADING BODY")

        ForensicBatesManifestCompiler.write_manifest_file(td)

        # Adversarial tamper
        doc.write_bytes(b"ALTERED LEGAL PLEADING BODY")

        valid, msgs = ForensicBatesManifestCompiler.verify_bates_integrity(td)
        assert valid is False
        assert any(ERR_SEC_TAMPER_DETECTED in m for m in msgs)


def test_forensic_bates_adversarial_zero_byte_refusal():
    with tempfile.TemporaryDirectory() as tmpdir:
        td = Path(tmpdir)
        (td / "empty_trace.txt").write_bytes(b"")

        with pytest.raises(ValueError, match=ERR_SEC_ZERO_BYTE_EVIDENCE):
            ForensicBatesManifestCompiler.compile_manifest(td)
