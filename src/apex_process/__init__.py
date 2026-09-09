"""
APEX Omniversal Development Process Engine
GlacierEQ / APEX Estate — Holographic Mesh Architecture
"""

__version__ = "1.1.0"
__author__ = "GlacierEQ APEX Mastermind"

from .core.taxonomy import (
    CATEGORIES,
    LIFECYCLE_STAGES,
    EPISTEMIC_TIERS,
    BODYBUILDER_GATES,
    CategoryInfo,
    LifecycleStage,
)
from .core.epistemic import EpistemicGate, EpistemicTier, SpikeManager, SpikeManifest
from .core.receipt import CryptographicReceiptEngine
from .core.resilience import (
    DualPathRouter,
    CircuitBreaker,
    CircuitState,
    OperationCriticality,
    ResilienceResult,
)
from .core.pointer import PointerResolver, PointerManifest
from .auditors.ast_sentinel import ASTStubSentinel, StubDefect
from .auditors.gate_auditor import GateAuditor, GateAuditReport
from .scaffolders.project_forge import ProjectForge

__all__ = [
    "CATEGORIES",
    "LIFECYCLE_STAGES",
    "EPISTEMIC_TIERS",
    "BODYBUILDER_GATES",
    "CategoryInfo",
    "LifecycleStage",
    "EpistemicGate",
    "EpistemicTier",
    "SpikeManager",
    "SpikeManifest",
    "CryptographicReceiptEngine",
    "DualPathRouter",
    "CircuitBreaker",
    "CircuitState",
    "OperationCriticality",
    "ResilienceResult",
    "PointerResolver",
    "PointerManifest",
    "ASTStubSentinel",
    "StubDefect",
    "GateAuditor",
    "GateAuditReport",
    "ProjectForge",
]
