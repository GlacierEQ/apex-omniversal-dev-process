"""
Gate Auditor: Comprehensive 10-Point Bodybuilder Gate Evaluation (Gates G0 to G9).
GlacierEQ / APEX Estate — Bodybuilder Standard.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional
import os
import re
from .ast_sentinel import ASTStubSentinel, StubDefect
from ..core.receipt import CryptographicReceiptEngine
from ..core.taxonomy import BODYBUILDER_GATES, BodybuilderGate


@dataclass
class GateResult:
    gate_id: str
    name: str
    passed: bool
    details: str
    blocking: bool


@dataclass
class GateAuditReport:
    repository_path: str
    passed_all: bool
    passed_gates_count: int
    total_gates_count: int
    gate_results: List[GateResult]
    stub_defects: List[StubDefect] = field(default_factory=list)


class GateAuditor:
    """Evaluates whether a target repository satisfies all Gates G0 through G9."""

    @classmethod
    def audit_repository(cls, target_dir: Path) -> GateAuditReport:
        target_dir = Path(target_dir).resolve()
        if not target_dir.is_dir():
            raise NotADirectoryError(f"Target is not a directory: {target_dir}")

        results: List[GateResult] = []

        # Gate G0: ISSUE_CONTRACT.md
        g0_file = target_dir / "ISSUE_CONTRACT.md"
        if g0_file.is_file():
            content = g0_file.read_text(encoding="utf-8", errors="ignore")
            has_pain = "pain" in content.lower() or "problem" in content.lower()
            has_nongoals = "non-goals" in content.lower() or "non goals" in content.lower()
            if has_pain and has_nongoals:
                results.append(GateResult("G0", "Issue Contract", True, "Valid ISSUE_CONTRACT.md with problem and non-goals", True))
            else:
                results.append(GateResult("G0", "Issue Contract", False, "ISSUE_CONTRACT.md present but missing pain point or non-goals section", True))
        else:
            results.append(GateResult("G0", "Issue Contract", False, "ISSUE_CONTRACT.md missing in root", True))

        # Gate G1: Fail-Closed Architecture (ERR_* reason codes)
        err_pattern = re.compile(r"\bERR_[A-Z0-9_]+\b")
        found_error_codes = set()
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules", "venv", ".venv")]
            for f in files:
                if f.endswith((".py", ".rs", ".ts", ".go", ".c", ".cpp", ".md")):
                    fp = Path(root) / f
                    try:
                        text = fp.read_text(encoding="utf-8", errors="ignore")
                        matches = err_pattern.findall(text)
                        found_error_codes.update(matches)
                    except Exception:
                        pass

        if len(found_error_codes) >= 3:
            results.append(GateResult("G1", "Fail-Closed Architecture", True, f"Found {len(found_error_codes)} explicit ERR_* refusal codes", True))
        else:
            results.append(GateResult("G1", "Fail-Closed Architecture", False, f"Found only {len(found_error_codes)} ERR_* codes (minimum 3 required)", True))

        # Gate G2: Adversarial Test Suite (>= 8 total, >= 4 adversarial/refusal)
        test_pattern = re.compile(r"def test_([a-zA-Z0-9_]+)")
        total_tests = 0
        adversarial_tests = 0
        adversarial_keywords = ("adversarial", "refus", "error", "overflow", "underflow", "fail", "malform", "invalid", "tamper", "bounds")

        tests_dir = target_dir / "tests"
        if tests_dir.is_dir():
            for root, _, files in os.walk(tests_dir):
                for f in files:
                    if f.startswith("test_") and f.endswith(".py"):
                        fp = Path(root) / f
                        try:
                            text = fp.read_text(encoding="utf-8", errors="ignore")
                            found = test_pattern.findall(text)
                            total_tests += len(found)
                            for tname in found:
                                if any(kw in tname.lower() for kw in adversarial_keywords):
                                    adversarial_tests += 1
                        except Exception:
                            pass

        if total_tests >= 8 and adversarial_tests >= 4:
            results.append(GateResult("G2", "Adversarial Test Suite", True, f"Verified {total_tests} tests ({adversarial_tests} adversarial)", True))
        else:
            results.append(GateResult("G2", "Adversarial Test Suite", False, f"Test count deficit: {total_tests}/8 total, {adversarial_tests}/4 adversarial", True))

        # Gate G3: Cryptographic Receipt
        receipt_file = target_dir / "EVIDENCE_RECEIPT.json"
        if receipt_file.is_file():
            valid, msgs = CryptographicReceiptEngine.verify_manifest(target_dir, receipt_file)
            if valid:
                results.append(GateResult("G3", "Cryptographic Receipt", True, "EVIDENCE_RECEIPT.json verified bit-for-bit with 0 discrepancies", True))
            else:
                results.append(GateResult("G3", "Cryptographic Receipt", False, f"Receipt verification failed: {'; '.join(msgs[:3])}", True))
        else:
            results.append(GateResult("G3", "Cryptographic Receipt", False, "EVIDENCE_RECEIPT.json missing in root", True))

        # Gate G4: License Integrity
        lic_file = target_dir / "LICENSE"
        if lic_file.is_file() and lic_file.stat().st_size > 50:
            results.append(GateResult("G4", "License Integrity", True, "LICENSE file present and populated", True))
        else:
            results.append(GateResult("G4", "License Integrity", False, "LICENSE missing or under 50 bytes", True))

        # Gate G5: Quality Honesty
        qual_file = target_dir / "QUALITY.md"
        if qual_file.is_file():
            qtext = qual_file.read_text(encoding="utf-8", errors="ignore").lower()
            if "verified" in qtext and "frontier" in qtext:
                results.append(GateResult("G5", "Quality Honesty", True, "QUALITY.md explicitly balances verified invariants vs open frontiers", True))
            else:
                results.append(GateResult("G5", "Quality Honesty", False, "QUALITY.md missing verified invariants or open frontiers section", True))
        else:
            results.append(GateResult("G5", "Quality Honesty", False, "QUALITY.md missing in root", True))

        # Gate G6: Production CI Workflow
        wf_dir = target_dir / ".github" / "workflows"
        has_ci = wf_dir.is_dir() and any(f.endswith((".yml", ".yaml")) for f in os.listdir(wf_dir))
        if has_ci:
            results.append(GateResult("G6", "Production CI Workflow", True, "GitHub Actions CI workflow found in .github/workflows/", True))
        else:
            results.append(GateResult("G6", "Production CI Workflow", False, "Missing workflow YAML in .github/workflows/", True))

        # Gate G7: Babel Polyglot Spec
        babel_file = target_dir / "BABEL.md"
        if babel_file.is_file() and babel_file.stat().st_size > 100:
            results.append(GateResult("G7", "Babel Polyglot Spec", True, "BABEL.md polyglot rationale present", True))
        else:
            results.append(GateResult("G7", "Babel Polyglot Spec", False, "BABEL.md missing or empty", True))

        # Gate G8: Zero Stubs Invariant (AST Sentinel)
        stub_defects = ASTStubSentinel.audit_directory(target_dir)
        if len(stub_defects) == 0:
            results.append(GateResult("G8", "Zero Stubs Invariant", True, "AST Sentinel confirmed 0 stubs (zero pass/return True)", True))
        else:
            results.append(GateResult("G8", "Zero Stubs Invariant", False, f"Detected {len(stub_defects)} stubs in production code", True))

        # Gate G9: Executive Presentation
        readme_file = target_dir / "README.md"
        if readme_file.is_file() and readme_file.stat().st_size >= 400:
            results.append(GateResult("G9", "Executive Presentation", True, f"README.md present ({readme_file.stat().st_size} bytes)", True))
        else:
            results.append(GateResult("G9", "Executive Presentation", False, "README.md missing or under 400 bytes", True))

        passed_count = sum(1 for r in results if r.passed)
        passed_all = passed_count == len(results)

        return GateAuditReport(
            repository_path=str(target_dir),
            passed_all=passed_all,
            passed_gates_count=passed_count,
            total_gates_count=len(results),
            gate_results=results,
            stub_defects=stub_defects,
        )
