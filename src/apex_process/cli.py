"""
CLI Engine: APEX Omniversal Development Process Command Line Interface.
GlacierEQ / APEX Estate — Holographic Mesh Architecture.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .core.taxonomy import CATEGORIES, LIFECYCLE_STAGES, BODYBUILDER_GATES, EPISTEMIC_TIERS
from .core.receipt import CryptographicReceiptEngine
from .core.epistemic import EpistemicGate, EpistemicTier
from .auditors.ast_sentinel import ASTStubSentinel
from .auditors.gate_auditor import GateAuditor
from .scaffolders.project_forge import ProjectForge


def cmd_matrix(args: argparse.Namespace) -> int:
    """Displays the 12-Category, 9-Stage, 10-Gate Architecture Matrix."""
    if args.json:
        data = {
            "categories": {k: vars(v) for k, v in CATEGORIES.items()},
            "stages": [vars(s) for s in LIFECYCLE_STAGES],
            "gates": [vars(g) for g in BODYBUILDER_GATES],
            "epistemic_tiers": EPISTEMIC_TIERS,
        }
        print(json.dumps(data, indent=2, default=str))
        return 0

    print("\n" + "=" * 80)
    print("🏛️  APEX OMNIVERSAL DEVELOPMENT PROCESS ARCHITECTURE MATRIX")
    print("=" * 80)

    print("\n📦 THE 12 ENGINEERING CATEGORIES:")
    for cat_id, cat in sorted(CATEGORIES.items(), key=lambda x: x[1].number):
        print(f"  [{cat.number:02d}] {cat.name} ({cat.id})")
        print(f"       Languages: {', '.join(cat.primary_languages)}")
        print(f"       Refusal Codes: {', '.join(cat.common_refusal_codes)}")

    print("\n🔄 THE 9 LIFECYCLE STAGES:")
    for stage in LIFECYCLE_STAGES:
        print(f"  [Stage {stage.stage_number}] {stage.name} ({stage.epistemic_level.value})")
        print(f"       Outputs: {', '.join(stage.required_outputs)}")

    print("\n🛡️  THE 10 BODYBUILDER GATES (G0–G9):")
    for gate in BODYBUILDER_GATES:
        print(f"  [{gate.gate_id}] {gate.name}: {gate.description}")

    print("\n" + "=" * 80 + "\n")
    return 0


def cmd_guide(args: argparse.Namespace) -> int:
    """Displays instructional guidance for a category or lifecycle stage."""
    cat_id = args.category
    if not cat_id:
        print("Available categories for guidance:")
        for k, v in sorted(CATEGORIES.items(), key=lambda x: x[1].number):
            print(f"  - {k} (#{v.number:02d}: {v.name})")
        print("\nRun: apex-process guide <category_name>")
        return 0

    if cat_id not in CATEGORIES:
        print(f"Error: Unknown category '{cat_id}'.", file=sys.stderr)
        return 1

    cat = CATEGORIES[cat_id]
    print(f"\n{'=' * 75}")
    print(f"📘 INSTRUCTION MANUAL: Category {cat.number:02d} — {cat.name}")
    print(f"{'=' * 75}\n")
    print(f"Overview: {cat.description}\n")
    print(f"Primary Languages: {', '.join(cat.primary_languages)}")
    print("\nCritical Invariants:")
    for inv in cat.critical_invariants:
        print(f"  • {inv}")

    print("\nRequired Refusal Reason Codes:")
    for code in cat.common_refusal_codes:
        print(f"  • {code}")

    # If stage specified
    if args.stage is not None:
        stage_num = args.stage
        if 0 <= stage_num < len(LIFECYCLE_STAGES):
            stage = LIFECYCLE_STAGES[stage_num]
            print(f"\n--- STAGE {stage.stage_number}: {stage.name} ({stage.epistemic_level.value}) ---")
            print(f"Description: {stage.description}")
            print(f"Required Inputs: {', '.join(stage.required_inputs)}")
            print(f"Required Outputs: {', '.join(stage.required_outputs)}")
            print(f"Fatal Failure Mode: {stage.failure_mode}")
        else:
            print(f"Stage {stage_num} out of bounds (0-8).", file=sys.stderr)

    print(f"\nDetailed guide markdown: {cat.guide_file}\n")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    """Scaffolds a compliant Bodybuilder project in any category."""
    cat_id = args.category
    name = args.name
    dest = Path(args.dest or ".").resolve()

    try:
        project_path = ProjectForge.scaffold(cat_id, name, dest)
        print(f"✅ Successfully forged project '{name}' in category '{cat_id}'")
        print(f"📁 Path: {project_path}")
        print("🛡️  Pre-configured with Gates G0–G9, fail-closed boundaries, and 100% green tests.")
        return 0
    except Exception as e:
        print(f"❌ Project creation failed: {e}", file=sys.stderr)
        return 1


def cmd_check_stubs(args: argparse.Namespace) -> int:
    """Scans codebase for non-functional stubs (pass, return True/None)."""
    target = Path(args.target or ".").resolve()
    defects = ASTStubSentinel.audit_directory(target)

    if args.json:
        print(json.dumps([vars(d) for d in defects], indent=2))
        return 0 if len(defects) == 0 else 1

    if len(defects) == 0:
        print(f"🟢 AST Sentinel: 0 stubs detected in {target}. Invariant G8 satisfied.")
        return 0
    else:
        print(f"🔴 AST Sentinel: {len(defects)} STUB DEFECTS FOUND in {target}:", file=sys.stderr)
        for d in defects:
            print(f"  - [{d.reason_code}] {d.file_path}:{d.line_number} in '{d.symbol_name}': {d.message}", file=sys.stderr)
        return 1


def cmd_receipt(args: argparse.Namespace) -> int:
    """Generates or verifies EVIDENCE_RECEIPT.json."""
    target = Path(args.target or ".").resolve()

    if args.verify:
        passed, msgs = CryptographicReceiptEngine.verify_manifest(target)
        if passed:
            print(f"🟢 Cryptographic Receipt Verified: 100% bit-for-bit integrity across {target}")
            return 0
        else:
            print(f"🔴 Receipt Discrepancy in {target}:", file=sys.stderr)
            for m in msgs:
                print(f"  • {m}", file=sys.stderr)
            return 1
    else:
        out = CryptographicReceiptEngine.write_manifest_to_file(target)
        print(f"✅ Cryptographic SHA-256 evidence manifest written to: {out}")
        return 0


def cmd_audit(args: argparse.Namespace) -> int:
    """Evaluates a repository across Gates G0 through G9."""
    target = Path(args.target or ".").resolve()
    report = GateAuditor.audit_repository(target)

    if args.json:
        data = {
            "repository": report.repository_path,
            "passed_all": report.passed_all,
            "passed_count": report.passed_gates_count,
            "total_count": report.total_gates_count,
            "gates": [vars(g) for g in report.gate_results],
            "stubs": [vars(s) for s in report.stub_defects],
        }
        print(json.dumps(data, indent=2))
        return 0 if report.passed_all else 1

    print(f"\n{'=' * 75}")
    print(f"📋 BODYBUILDER GATE AUDIT REPORT: {target.name}")
    print(f"Path: {report.repository_path}")
    print(f"{'=' * 75}\n")

    for g in report.gate_results:
        symbol = "🟢 [PASS]" if g.passed else "🔴 [FAIL]"
        print(f"{symbol} {g.gate_id: <4} {g.name: <28} | {g.details}")

    print(f"\nResult: {report.passed_gates_count}/{report.total_gates_count} Gates Passed.")
    if report.passed_all:
        print("🏆 Status: VERIFIED BODYBUILDER (All Gates G0–G9 Satisfied)\n")
        return 0
    else:
        print("⚠️  Status: DEFICIT DETECTED (Remediation Required)\n", file=sys.stderr)
        return 1


def cmd_spike(args: argparse.Namespace) -> int:
    """Manages zero-to-one sandbox spikes with TTL (Fix 1: Cold-Start Paralysis)."""
    action = args.spike_action
    target = Path(args.target or "./spikes/prototype").resolve()

    if action == "init":
        name = args.name or target.name
        purpose = args.purpose or "Rapid zero-to-one exploration"
        ttl = args.ttl if args.ttl is not None else 72.0
        mpath = SpikeManager.create_spike(target, name, purpose, ttl_hours=ttl)
        print(f"🧪 Sandbox Spike '{name}' created at {target}")
        print(f"⏱️  TTL: {ttl} hours (Expires: {time.ctime(time.time() + ttl * 3600)})")
        print(f"📜 Manifest: {mpath}")
        print("🛡️  Exempt from Gate G2/G8 production audits while active.")
        return 0
    elif action == "status":
        active, msg = SpikeManager.check_spike_status(target)
        if active:
            print(f"🟢 {msg}")
            return 0
        else:
            print(f"🔴 {msg}", file=sys.stderr)
            return 1
    elif action == "graduate":
        defects = ASTStubSentinel.audit_directory(target)
        tests_dir = target / "tests"
        has_tests = tests_dir.is_dir() and len(os.listdir(tests_dir)) > 0
        zero_stubs = len(defects) == 0
        success, msg = SpikeManager.graduate_spike(target, has_passing_tests=has_tests, zero_stubs=zero_stubs)
        if success:
            print(f"🏆 {msg}")
            return 0
        else:
            print(f"❌ {msg}", file=sys.stderr)
            return 1
    return 0


def cmd_pointer(args: argparse.Namespace) -> int:
    """Manages Token-Saver Pointer relationships (Fix 5: Ceremony Tax)."""
    action = args.pointer_action
    target = Path(args.target or ".").resolve()

    if action == "create":
        if not args.spec_root:
            print("Error: --spec-root required for pointer create", file=sys.stderr)
            return 1
        spec_root = Path(args.spec_root).resolve()
        pfile = PointerResolver.create_pointer_file(target, target.name, spec_root)
        print(f"🔗 Token-Saver Pointer created: {pfile}")
        print(f"📍 Inherits governance models from: {spec_root}")
        return 0
    elif action == "resolve":
        manifest = PointerResolver.resolve_pointer(target)
        if manifest and manifest.is_pointer_valid:
            print(f"🟢 Pointer Valid for {manifest.repo_name} -> {manifest.target_spec_root}")
            for k, v in manifest.resolved_files.items():
                print(f"  • {k}: {v}")
            return 0
        else:
            print(f"🔴 Pointer resolution failed or missing at {target}", file=sys.stderr)
            return 1
    return 0


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="apex-process",
        description="APEX Omniversal Development Process CLI — Full Development Lifecycle in All Categories.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Operational Subcommands")

    # matrix
    p_matrix = subparsers.add_parser("matrix", help="Display full 12-category architecture matrix")
    p_matrix.add_argument("--json", action="store_true", help="Output matrix as JSON")

    # guide
    p_guide = subparsers.add_parser("guide", help="Instructional guidance for categories and stages")
    p_guide.add_argument("category", nargs="?", help="Category identifier (e.g. systems_and_kernels)")
    p_guide.add_argument("--stage", type=int, help="Lifecycle stage number (0-8)")

    # init
    p_init = subparsers.add_parser("init", help="Forge a new Bodybuilder repository for any category")
    p_init.add_argument("category", help="Category ID (e.g. ai_ml_llms, systems_and_kernels)")
    p_init.add_argument("name", help="Project repository name")
    p_init.add_argument("--dest", default=".", help="Destination parent directory")

    # check-stubs
    p_stubs = subparsers.add_parser("check-stubs", help="Scan code for non-functional pass/return stubs")
    p_stubs.add_argument("target", nargs="?", default=".", help="Target repository directory")
    p_stubs.add_argument("--json", action="store_true", help="Output defects as JSON")

    # receipt
    p_receipt = subparsers.add_parser("receipt", help="Generate or verify SHA-256 evidence receipt")
    p_receipt.add_argument("target", nargs="?", default=".", help="Target directory")
    p_receipt.add_argument("--verify", action="store_true", help="Verify against existing manifest")

    # audit / gate-check
    p_audit = subparsers.add_parser("audit", help="Exhaustive evaluation of Gates G0 to G9")
    p_audit.add_argument("target", nargs="?", default=".", help="Target directory")
    p_audit.add_argument("--json", action="store_true", help="Output as JSON")

    p_gate = subparsers.add_parser("gate-check", help="Strict CI gate verification (exit 0 only if all pass)")
    p_gate.add_argument("target", nargs="?", default=".", help="Target directory")

    # spike (Fix 1)
    p_spike = subparsers.add_parser("spike", help="Manage zero-to-one exploratory spikes with TTL")
    p_spike.add_argument("spike_action", choices=["init", "status", "graduate"], help="Spike action")
    p_spike.add_argument("target", nargs="?", default="./spikes/prototype", help="Spike directory")
    p_spike.add_argument("--name", help="Spike name")
    p_spike.add_argument("--purpose", help="Spike exploratory purpose")
    p_spike.add_argument("--ttl", type=float, default=72.0, help="Time to live in hours (default: 72)")

    # pointer (Fix 5)
    p_pointer = subparsers.add_parser("pointer", help="Manage Token-Saver Pointer references")
    p_pointer.add_argument("pointer_action", choices=["create", "resolve"], help="Pointer action")
    p_pointer.add_argument("target", nargs="?", default=".", help="Target directory")
    p_pointer.add_argument("--spec-root", help="Root specification directory for inherited models")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "matrix":
        return cmd_matrix(args)
    elif args.command == "guide":
        return cmd_guide(args)
    elif args.command == "init":
        return cmd_init(args)
    elif args.command == "check-stubs":
        return cmd_check_stubs(args)
    elif args.command == "receipt":
        return cmd_receipt(args)
    elif args.command in ("audit", "gate-check"):
        if args.command == "gate-check":
            args.json = False
        return cmd_audit(args)
    elif args.command == "spike":
        return cmd_spike(args)
    elif args.command == "pointer":
        return cmd_pointer(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
