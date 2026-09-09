"""
Tests for Gate Auditor: Verifying Gates G0 to G9.
"""

import tempfile
from pathlib import Path
import pytest
from src.apex_process.auditors.gate_auditor import GateAuditor
from src.apex_process.scaffolders.project_forge import ProjectForge


def test_scaffolded_project_passes_all_gates():
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir)
        proj_dir = ProjectForge.scaffold("systems_and_kernels", "test_ring_engine", dest)

        report = GateAuditor.audit_repository(proj_dir)
        assert report.passed_all is True
        assert report.passed_gates_count == 10
        assert report.total_gates_count == 10
        assert len(report.stub_defects) == 0


def test_empty_directory_fails_gates():
    with tempfile.TemporaryDirectory() as tmpdir:
        report = GateAuditor.audit_repository(Path(tmpdir))
        assert report.passed_all is False
        assert report.passed_gates_count < 5


def test_missing_nongoals_fails_g0():
    with tempfile.TemporaryDirectory() as tmpdir:
        td = Path(tmpdir)
        (td / "ISSUE_CONTRACT.md").write_text("# Issue Contract\nOnly problem description here without the negative scope constraints.\n")
        report = GateAuditor.audit_repository(td)
        g0 = [g for g in report.gate_results if g.gate_id == "G0"][0]
        assert g0.passed is False


def test_stub_defect_fails_g8():
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir)
        proj_dir = ProjectForge.scaffold("ai_ml_llms", "stub_test_proj", dest)

        # Inject stub into code
        bad_file = proj_dir / "src" / "stub_test_proj" / "broken.py"
        bad_file.write_text("def broken_stub():\n    pass\n")

        report = GateAuditor.audit_repository(proj_dir)
        g8 = [g for g in report.gate_results if g.gate_id == "G8"][0]
        assert g8.passed is False
        assert report.passed_all is False
        assert len(report.stub_defects) >= 1
