"""
Category 06 Reference Implementation: 4-Phase Multi-Agent Dialectic Consensus Engine.
GlacierEQ / APEX Estate — Swarm Enterprise Standard (L5).
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import hashlib
import time

ERR_SWARM_CONSENSUS_REJECTED = "ERR_SWARM_CONSENSUS_REJECTED"
ERR_SWARM_EMPTY_PROPOSAL = "ERR_SWARM_EMPTY_PROPOSAL"
ERR_SWARM_AUDITOR_BYPASS = "ERR_SWARM_AUDITOR_BYPASS"
ERR_SWARM_HOMOGENEOUS_AUDITOR = "ERR_SWARM_HOMOGENEOUS_AUDITOR"
ERR_SWARM_MISSING_COMPILER_PROOF = "ERR_SWARM_MISSING_COMPILER_PROOF"


@dataclass(frozen=True)
class DialecticReceipt:
    consensus_achieved: bool
    status_code: str
    task_id: str
    reasoner_id: str
    synthesizer_id: str
    auditor_id: str
    consensus_digest: Optional[str]
    audit_notes: str
    compiler_verified: bool
    timestamp: float


class DialecticConsensusEngine:
    """
    Coordinates 4-Phase Dialectic Multi-Agent Consensus:
    Phase 1 (Reasoner) -> Phase 2 (Synthesizer) -> Phase 3 (Auditor) -> Phase 4 (Perception).
    Rejects unilateral agent merges; requires cryptographic cross-agent receipts.
    """

    def __init__(
        self,
        task_id: str,
        reasoner_id: str = "DEEPSEEK-R1",
        synthesizer_id: str = "QWEN-2.5-CODER",
        auditor_id: str = "DEEPSEEK-V3-AUDITOR",
    ):
        self.task_id = task_id
        self.reasoner_id = reasoner_id
        self.synthesizer_id = synthesizer_id
        self.auditor_id = auditor_id
        self._history: List[DialecticReceipt] = []

    def evaluate_proposal(
        self,
        proposal_text: str,
        auditor_approval: bool,
        auditor_notes: str,
        compiler_exit_code: int = 0,
    ) -> DialecticReceipt:
        """Evaluates an agent proposal through dialectic consensus gates."""
        timestamp = time.time()

        # 1. Reject empty proposal
        if not proposal_text or not proposal_text.strip():
            receipt = DialecticReceipt(
                consensus_achieved=False,
                status_code=ERR_SWARM_EMPTY_PROPOSAL,
                task_id=self.task_id,
                reasoner_id=self.reasoner_id,
                synthesizer_id=self.synthesizer_id,
                auditor_id=self.auditor_id,
                consensus_digest=None,
                audit_notes="Proposal text cannot be empty",
                compiler_verified=False,
                timestamp=timestamp,
            )
            self._history.append(receipt)
            return receipt

        # 2. Gate: Architectural Diversity (Fix 6: Break Swarm Echo Chamber)
        if self.reasoner_id.strip().upper() == self.auditor_id.strip().upper():
            receipt = DialecticReceipt(
                consensus_achieved=False,
                status_code=ERR_SWARM_HOMOGENEOUS_AUDITOR,
                task_id=self.task_id,
                reasoner_id=self.reasoner_id,
                synthesizer_id=self.synthesizer_id,
                auditor_id=self.auditor_id,
                consensus_digest=None,
                audit_notes=f"Reasoner and Auditor cannot be identical architecture '{self.auditor_id}' (echo-chamber violation)",
                compiler_verified=False,
                timestamp=timestamp,
            )
            self._history.append(receipt)
            return receipt

        # 3. Gate: Independent Auditor Approval
        if not auditor_approval:
            receipt = DialecticReceipt(
                consensus_achieved=False,
                status_code=ERR_SWARM_CONSENSUS_REJECTED,
                task_id=self.task_id,
                reasoner_id=self.reasoner_id,
                synthesizer_id=self.synthesizer_id,
                auditor_id=self.auditor_id,
                consensus_digest=None,
                audit_notes=f"Auditor rejected proposal: {auditor_notes}",
                compiler_verified=False,
                timestamp=timestamp,
            )
            self._history.append(receipt)
            return receipt

        # 4. Gate: Empirical Compiler / Test Execution Proof
        if compiler_exit_code != 0:
            receipt = DialecticReceipt(
                consensus_achieved=False,
                status_code=ERR_SWARM_MISSING_COMPILER_PROOF,
                task_id=self.task_id,
                reasoner_id=self.reasoner_id,
                synthesizer_id=self.synthesizer_id,
                auditor_id=self.auditor_id,
                consensus_digest=None,
                audit_notes=f"Empirical validation failed: Compiler/test exit code was {compiler_exit_code} (must be 0)",
                compiler_verified=False,
                timestamp=timestamp,
            )
            self._history.append(receipt)
            return receipt

        # 5. Formulate Cryptographic Consensus Digest
        raw_consensus = (
            f"{self.task_id}:{self.reasoner_id}:{self.synthesizer_id}:{self.auditor_id}:"
            f"{proposal_text.strip()}:{compiler_exit_code}:{timestamp}"
        )
        consensus_digest = hashlib.sha256(raw_consensus.encode()).hexdigest()

        receipt = DialecticReceipt(
            consensus_achieved=True,
            status_code="SUCCESS",
            task_id=self.task_id,
            reasoner_id=self.reasoner_id,
            synthesizer_id=self.synthesizer_id,
            auditor_id=self.auditor_id,
            consensus_digest=consensus_digest,
            audit_notes=auditor_notes,
            compiler_verified=True,
            timestamp=timestamp,
        )
        self._history.append(receipt)
        return receipt

    def get_history(self) -> List[DialecticReceipt]:
        return list(self._history)
