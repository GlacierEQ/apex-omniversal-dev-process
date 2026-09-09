"""
Tests for Token-Saver Pointer Architecture (Fix 5: Slashing Ceremony Tax).
"""

import tempfile
from pathlib import Path
import pytest
from src.apex_process.core.pointer import PointerResolver, PointerManifest
from src.apex_process.auditors.gate_auditor import GateAuditor


def test_create_and_resolve_pointer():
    with tempfile.TemporaryDirectory() as tmp_spec, tempfile.TemporaryDirectory() as tmp_leaf:
        spec_dir = Path(tmp_spec)
        leaf_dir = Path(tmp_leaf)

        # Create governance files in spec root
        (spec_dir / "LICENSE").write_text("SHARED GLACIEREQ LICENSE BODY", encoding="utf-8")
        (spec_dir / "BABEL.md").write_text("# SHARED BABEL SPEC\n" + "x" * 150, encoding="utf-8")

        # Create pointer in leaf
        pfile = PointerResolver.create_pointer_file(leaf_dir, "leaf_service", spec_dir)
        assert pfile.is_file()

        manifest = PointerResolver.resolve_pointer(leaf_dir)
        assert manifest is not None
        assert manifest.is_pointer_valid is True
        assert "LICENSE" in manifest.resolved_files
        assert "BABEL.md" in manifest.resolved_files


def test_gate_auditor_inherits_license_and_babel_via_pointer():
    with tempfile.TemporaryDirectory() as tmp_spec, tempfile.TemporaryDirectory() as tmp_leaf:
        spec_dir = Path(tmp_spec)
        leaf_dir = Path(tmp_leaf)

        # Shared governance in root
        (spec_dir / "LICENSE").write_text("SHARED GLACIEREQ LICENSE BODY " * 5, encoding="utf-8")
        (spec_dir / "BABEL.md").write_text("# SHARED BABEL SPEC\n" + "content " * 30, encoding="utf-8")

        # Leaf has pointer, but NO local LICENSE or BABEL.md
        PointerResolver.create_pointer_file(leaf_dir, "leaf_repo", spec_dir)

        # Run auditor on leaf
        report = GateAuditor.audit_repository(leaf_dir)
        g4 = [g for g in report.gate_results if g.gate_id == "G4"][0]
        g7 = [g for g in report.gate_results if g.gate_id == "G7"][0]

        assert g4.passed is True
        assert "inherited" in g4.details.lower()
        assert g7.passed is True
        assert "inherited" in g7.details.lower()
