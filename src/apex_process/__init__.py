"""
APEX Omniversal Development Process Engine
GlacierEQ / APEX Estate — Holographic Mesh Architecture
"""

__version__ = "1.0.0"
__author__ = "GlacierEQ APEX Mastermind"

from .core.taxonomy import (
    CATEGORIES,
    LIFECYCLE_STAGES,
    EPISTEMIC_TIERS,
    BODYBUILDER_GATES,
    CategoryInfo,
    LifecycleStage,
)
from .core.epistemic import EpistemicGate, EpistemicTier
from .core.receipt import CryptographicReceiptEngine
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
    "CryptographicReceiptEngine",
    "ASTStubSentinel",
    "StubDefect",
    "GateAuditor",
    "GateAuditReport",
    "ProjectForge",
]
