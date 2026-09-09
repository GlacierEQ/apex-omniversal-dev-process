"""
APEX Omniversal Taxonomy: 12 Categories, 9 Lifecycle Stages, 6 Epistemic Tiers, and 10 Bodybuilder Gates.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class EpistemicTier(Enum):
    L0_PRESENCE = "L0_PRESENCE"
    L1_STRUCTURE = "L1_STRUCTURE"
    L2_BEHAVIOR = "L2_BEHAVIOR"
    L3_BACKEND = "L3_BACKEND"
    L4_TELEMETRY = "L4_TELEMETRY"
    L5_SWARM = "L5_SWARM"
    L6_AUTONOMY = "L6_AUTONOMY"


@dataclass(frozen=True)
class CategoryInfo:
    id: str
    number: int
    name: str
    description: str
    primary_languages: List[str]
    critical_invariants: List[str]
    common_refusal_codes: List[str]
    guide_file: str


@dataclass(frozen=True)
class LifecycleStage:
    stage_number: int
    id: str
    name: str
    description: str
    epistemic_level: EpistemicTier
    required_inputs: List[str]
    required_outputs: List[str]
    failure_mode: str


@dataclass(frozen=True)
class BodybuilderGate:
    gate_id: str
    name: str
    description: str
    proof_requirement: str
    blocking: bool


# The 12 Omniversal Engineering Categories
CATEGORIES: Dict[str, CategoryInfo] = {
    "systems_and_kernels": CategoryInfo(
        id="systems_and_kernels",
        number=1,
        name="Low-Level Systems & Kernel Engineering",
        description="Memory-safe, deterministic, low-latency systems interfacing with hardware or OS primitives.",
        primary_languages=["Rust", "C", "C++", "Zig", "eBPF C"],
        critical_invariants=["Zero buffer overruns", "Bounded memory footprint", "Lock-free/Acyclic concurrency"],
        common_refusal_codes=["ERR_SYS_BUFFER_OVERFLOW", "ERR_SYS_BUFFER_UNDERFLOW", "ERR_SYS_OUT_OF_BOUNDS"],
        guide_file="categories/01_systems_and_kernels.md",
    ),
    "distributed_backends": CategoryInfo(
        id="distributed_backends",
        number=2,
        name="High-Throughput Distributed Systems & Backends",
        description="Horizontally scalable, fault-tolerant microservices, consensus logs, and RPC grids.",
        primary_languages=["Go", "Rust", "Python", "TypeScript"],
        critical_invariants=["Idempotent state transitions", "Monotonic term ordering", "Partition tolerance"],
        common_refusal_codes=["ERR_DIST_SPLIT_BRAIN", "ERR_DIST_IDEMPOTENCY_COLLISION", "ERR_DIST_QUORUM_UNAVAILABLE"],
        guide_file="categories/02_distributed_systems_and_backends.md",
    ),
    "web_frontends": CategoryInfo(
        id="web_frontends",
        number=3,
        name="Modern Web Applications & Frontends",
        description="Responsive, accessible, server-rendered and client-hydrated web user experiences.",
        primary_languages=["TypeScript", "JavaScript", "Tailwind CSS"],
        critical_invariants=["Zero hydration mismatch", "Sub-1.5s LCP", "WCAG 2.1 AA accessibility"],
        common_refusal_codes=["ERR_WEB_INVALID_PAYLOAD", "ERR_WEB_UNAUTHORIZED_SESSION", "ERR_WEB_RATE_LIMITED"],
        guide_file="categories/03_web_and_frontends.md",
    ),
    "mobile_crossplatform": CategoryInfo(
        id="mobile_crossplatform",
        number=4,
        name="Mobile & Cross-Platform Development",
        description="Battery-efficient, offline-first, native and cross-platform mobile experiences.",
        primary_languages=["Swift", "Kotlin", "Dart (Flutter)"],
        critical_invariants=["Offline queue persistence", "Main-thread non-blocking", "Thermal/battery budgeting"],
        common_refusal_codes=["ERR_MOB_BIOMETRIC_FAILED", "ERR_MOB_STORAGE_CORRUPTION", "ERR_MOB_OFFLINE_QUEUE_FULL"],
        guide_file="categories/04_mobile_and_crossplatform.md",
    ),
    "ai_ml_llms": CategoryInfo(
        id="ai_ml_llms",
        number=5,
        name="Artificial Intelligence, LLMs & Machine Learning",
        description="Transformer architectures, KV cache management, quantized inference, and MCP servers.",
        primary_languages=["Python", "C++/CUDA", "Swift Metal", "MLIR"],
        critical_invariants=["Token context limits enforced", "Strict tool schema validation", "Prompt injection defense"],
        common_refusal_codes=["ERR_AI_CONTEXT_LIMIT_EXCEEDED", "ERR_AI_TOOL_SCHEMA_VIOLATION", "ERR_AI_HALLUCINATION_DETECTED"],
        guide_file="categories/05_ai_ml_and_llms.md",
    ),
    "autonomous_swarms": CategoryInfo(
        id="autonomous_swarms",
        number=6,
        name="Autonomous Swarms & Multi-Agent Systems",
        description="Dialectic multi-agent consensus, dynamic task DAGs, shared memory graphs, and self-repair.",
        primary_languages=["Python", "TypeScript"],
        critical_invariants=["Bounded iteration count", "Independent adversarial audit", "Non-clobbering state"],
        common_refusal_codes=["ERR_SWARM_MAX_ITERATIONS_EXCEEDED", "ERR_SWARM_CONSENSUS_REJECTED", "ERR_SWARM_CYCLIC_DEPENDENCY"],
        guide_file="categories/06_autonomous_swarms_and_agents.md",
    ),
    "data_engineering": CategoryInfo(
        id="data_engineering",
        number=7,
        name="Data Engineering, Analytics & Lakehouses",
        description="Petabyte-scale analytical pipelines, columnar storage, federated catalogs, and streaming ETL.",
        primary_languages=["SQL", "Python", "Rust", "Scala"],
        critical_invariants=["Idempotent ingestion", "Schema evolution governance", "Dead letter queue routing"],
        common_refusal_codes=["ERR_DATA_SCHEMA_MISMATCH", "ERR_DATA_NULL_CONSTRAINT_VIOLATION", "ERR_DATA_DLQ_OVERFLOW"],
        guide_file="categories/07_data_engineering_and_analytics.md",
    ),
    "cloud_devops_sre": CategoryInfo(
        id="cloud_devops_sre",
        number=8,
        name="Cloud, DevOps & Site Reliability Engineering (SRE)",
        description="Multi-cloud IaC, rootless container virtualization, automated rollouts, and disaster recovery.",
        primary_languages=["Terraform", "Bash/Zsh", "Dockerfile", "YAML"],
        critical_invariants=["Immutable container promotion", "Zero hardcoded secrets", "Automated health rollback"],
        common_refusal_codes=["ERR_SRE_HEALTH_CHECK_FAILED", "ERR_SRE_ROLLBACK_TRIGGERED", "ERR_SRE_SECRET_MISSING"],
        guide_file="categories/08_cloud_devops_and_sre.md",
    ),
    "security_forensics": CategoryInfo(
        id="security_forensics",
        number=9,
        name="Cybersecurity, Threat Modeling & Forensics",
        description="Zero Trust architecture, cryptographic provenance (FRE 902), and secret scrubbing.",
        primary_languages=["Python", "Rust", "C"],
        critical_invariants=["Deterministic SHA-256 digests", "Constant-time comparisons", "Air-gapped secret scrubbing"],
        common_refusal_codes=["ERR_SEC_TAMPER_DETECTED", "ERR_SEC_SECRET_LEAKAGE_PREVENTED", "ERR_SEC_SIGNATURE_INVALID"],
        guide_file="categories/09_security_and_forensics.md",
    ),
    "formal_verification_qa": CategoryInfo(
        id="formal_verification_qa",
        number=10,
        name="Formal Verification, Testing & Epistemic QA",
        description="Mathematical proofs, property-based testing, fuzzing, and the 6-Tier Epistemic Ladder.",
        primary_languages=["Lean 4", "Python (pytest)", "TypeScript (Vitest)", "Dafny"],
        critical_invariants=["The Epistemic Law of Action", "Zero-stub enforcement", "Adversarial test density"],
        common_refusal_codes=["ERR_QA_ASSERTION_FAILED", "ERR_QA_STUB_DETECTED", "ERR_QA_INSUFFICIENT_ADVERSARIAL_TESTS"],
        guide_file="categories/10_formal_verification_and_qa.md",
    ),
    "interactive_media_3d": CategoryInfo(
        id="interactive_media_3d",
        number=11,
        name="Real-Time Interactive Media, 3D & Game Engineering",
        description="High-framerate rendering loops, GPU compute shaders, ECS architectures, and deterministic multiplayer.",
        primary_languages=["C++", "C#", "Rust", "WGSL/GLSL", "TypeScript"],
        critical_invariants=["Strict 60fps/120fps frame budget", "Zero GC allocation during tick", "Deterministic lockstep"],
        common_refusal_codes=["ERR_MEDIA_FRAME_DROP", "ERR_MEDIA_SHADER_COMPILE_FAILED", "ERR_MEDIA_DESYNC_DETECTED"],
        guide_file="categories/11_interactive_media_and_3d.md",
    ),
    "aerospace_robotics": CategoryInfo(
        id="aerospace_robotics",
        number=12,
        name="Aerospace, Robotics & Mission-Critical Embedded",
        description="Hard real-time deterministic control loops, orbital mechanics, sensor fusion, and fail-safe watchdogs.",
        primary_languages=["C/C++", "Rust", "Python (ROS2)", "Ada"],
        critical_invariants=["Zero missed real-time deadlines", "Redundant sensor voting", "Static memory allocation"],
        common_refusal_codes=["ERR_AERO_DEADLINE_MISSED", "ERR_AERO_SENSOR_OUT_OF_ENVELOPE", "ERR_AERO_ACTUATOR_SATURATION"],
        guide_file="categories/12_aerospace_and_robotics.md",
    ),
}

# The 9 Omniversal Lifecycle Stages
LIFECYCLE_STAGES: List[LifecycleStage] = [
    LifecycleStage(
        stage_number=0,
        id="epistemic_inception",
        name="Epistemic Inception & Problem Contracting",
        description="Formal problem scoping, explicit non-goals, threat modeling, and L0/L1 observation classification.",
        epistemic_level=EpistemicTier.L0_PRESENCE,
        required_inputs=["Problem statement", "Context signals"],
        required_outputs=["ISSUE_CONTRACT.md", "Refusal reason code enum"],
        failure_mode="Scope sprawl, treating sightings as working software",
    ),
    LifecycleStage(
        stage_number=1,
        id="architecture_invariants",
        name="Architectural Blueprint & Invariant Design",
        description="Formal state machines, ADR documentation, fail-closed boundaries, and AST interface specifications.",
        epistemic_level=EpistemicTier.L1_STRUCTURE,
        required_inputs=["ISSUE_CONTRACT.md"],
        required_outputs=["ARCHITECTURE.md", "Type definitions / schemas"],
        failure_mode="Untyped signatures, missing fail-closed safe defaults",
    ),
    LifecycleStage(
        stage_number=2,
        id="pro_code_implementation",
        name="Pro-Code Implementation (Helix Alpha/Omega)",
        description="One Big Push atomic coding, zero magic numbers, zero stubs, and polyglot idiom enforcement.",
        epistemic_level=EpistemicTier.L1_STRUCTURE,
        required_inputs=["ARCHITECTURE.md"],
        required_outputs=["Production source code files"],
        failure_mode="Stubs, pass statements, trivial return True placeholders",
    ),
    LifecycleStage(
        stage_number=3,
        id="adversarial_verification",
        name="Adversarial Verification & Epistemic Proof",
        description="TDD red-green cycle, happy path verification, minimum 4 adversarial refusal tests, and SHA-256 receipts.",
        epistemic_level=EpistemicTier.L2_BEHAVIOR,
        required_inputs=["Production source code", "Test suites"],
        required_outputs=["100% green test receipts", "EVIDENCE_RECEIPT.json"],
        failure_mode="Happy-path only tests, confidence treated as proof",
    ),
    LifecycleStage(
        stage_number=4,
        id="distributed_state_mesh",
        name="Distributed State, Mesh & Backend Integration",
        description="RPC zero-copy schemas, transactional ACID/CRDT state boundaries, and multi-cloud sync.",
        epistemic_level=EpistemicTier.L3_BACKEND,
        required_inputs=["EVIDENCE_RECEIPT.json", "Backend configs"],
        required_outputs=["Live database schemas", "RPC protobuf definitions"],
        failure_mode="Split-brain state collisions, unhandled network partitions",
    ),
    LifecycleStage(
        stage_number=5,
        id="telemetry_self_healing",
        name="Telemetry, Observability & Closed-Loop Self-Healing",
        description="Latency profiling (TTFT), memory leak checks, in-kernel tracepoints, and AST error repair.",
        epistemic_level=EpistemicTier.L4_TELEMETRY,
        required_inputs=["Operational binaries"],
        required_outputs=["Telemetry dashboards", "Latency profile reports"],
        failure_mode="Memory leaks, unbounded latency degradation",
    ),
    LifecycleStage(
        stage_number=6,
        id="dialectic_swarm_review",
        name="Multi-Agent Dialectic Swarm Consensus",
        description="4-Phase peer review: Reasoner (R1) -> Synthesizer -> Auditor (V3) -> Perception.",
        epistemic_level=EpistemicTier.L5_SWARM,
        required_inputs=["Code changes", "Audit reports"],
        required_outputs=["Dialectic consensus receipt", "Auditor sign-off"],
        failure_mode="Fake single-agent consensus, uninspected edge cases",
    ),
    LifecycleStage(
        stage_number=7,
        id="dev_fork_evolution",
        name="Dev Fork Upstream Parity & Synaptic Reinforcement",
        description="Upstream tracking branches, decoupled overlay layers, automated weekly sync, and memory graphs.",
        epistemic_level=EpistemicTier.L6_AUTONOMY,
        required_inputs=["Upstream git remotes"],
        required_outputs=["Weekly sync workflow", "Hebbian entity mappings"],
        failure_mode="Brittle destructive in-place edits, permanent upstream drift",
    ),
    LifecycleStage(
        stage_number=8,
        id="bodybuilder_release",
        name="The Bodybuilder Production Standard (G0–G9)",
        description="Exhaustive gate verification, multi-platform CI/CD, and executive 4-part presentation funnel.",
        epistemic_level=EpistemicTier.L6_AUTONOMY,
        required_inputs=["Full repository tree"],
        required_outputs=["G0-G9 compliance pass report", "Production release tag"],
        failure_mode="Releasing unverified or marketing-only codebases",
    ),
]

# The 10 Bodybuilder Gates
BODYBUILDER_GATES: List[BodybuilderGate] = [
    BodybuilderGate("G0", "Issue Contract", "Valid ISSUE_CONTRACT.md with pain point, non-goals, and failure modes.", "File existence and schema validation", True),
    BodybuilderGate("G1", "Fail-Closed Architecture", "Documented refusal reason codes and fail-safe defaults in core engine.", "Explicit Enum or error code constants", True),
    BodybuilderGate("G2", "Adversarial Test Suite", ">= 8 total tests, >= 4 adversarial/refusal tests, 100% pass rate.", "Pytest/runner execution output with 0 failures", True),
    BodybuilderGate("G3", "Cryptographic Receipt", "EVIDENCE_RECEIPT.json with deterministic SHA-256 hashes.", "Valid JSON manifest with non-empty digests", True),
    BodybuilderGate("G4", "License Integrity", "GlacierEQ Proprietary v1.1 or verified open-source license.", "LICENSE file with recognized header", True),
    BodybuilderGate("G5", "Quality Honesty", "QUALITY.md explicitly contrasting verified invariants vs open frontiers.", "Sections for verified invariants and open frontiers", True),
    BodybuilderGate("G6", "Production CI Workflow", ".github/workflows/ci.yml running lint, tests, and gate audits.", "Valid GitHub Actions workflow file", True),
    BodybuilderGate("G7", "Babel Polyglot Spec", "BABEL.md justifying language choices and translation bridges.", "BABEL.md file with selection rationale", True),
    BodybuilderGate("G8", "Zero Stubs Invariant", "AST sentinel verifies zero pass, return True, or placeholder stubs.", "AST inspection defect count == 0", True),
    BodybuilderGate("G9", "Executive Presentation", "Professional README.md following the 4-part presentation funnel.", "README with Hero, Architecture, Benchmark, Lineage", True),
]

EPISTEMIC_TIERS: Dict[str, str] = {
    "L0": "Presence — File or symbol exists on disk. No behavior assumed.",
    "L1": "Structure — Static AST, signatures, and schemas verified.",
    "L2": "Behavior — Unit assertions green, SHA-256 verified. (Action Baseline)",
    "L3": "Backend — Live DB integration, RPC mesh, multi-cloud storage sync.",
    "L4": "Telemetry — Latency budgets, zero memory leaks, automated repair.",
    "L5": "Swarm — 4-phase dialectic consensus with cryptographic receipts.",
    "L6": "Autonomy — Dev Fork upstream tracking, Hebbian synaptic reinforcement.",
}
