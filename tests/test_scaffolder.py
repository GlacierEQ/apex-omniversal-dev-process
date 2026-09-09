"""
Tests for Project Forge Scaffolder across categories.
"""

import tempfile
from pathlib import Path
import pytest
from src.apex_process.scaffolders.project_forge import ProjectForge
from src.apex_process.core.taxonomy import CATEGORIES


def test_scaffold_unknown_category_raises_error():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError, match="Unknown category"):
            ProjectForge.scaffold("non_existent_category", "my_proj", Path(tmpdir))


def test_scaffold_multiple_categories():
    test_cats = ["systems_and_kernels", "ai_ml_llms", "autonomous_swarms", "security_forensics"]
    with tempfile.TemporaryDirectory() as tmpdir:
        for cat in test_cats:
            proj_name = f"proj_{cat}"
            proj_path = ProjectForge.scaffold(cat, proj_name, Path(tmpdir))
            assert proj_path.is_dir()
            assert (proj_path / "ISSUE_CONTRACT.md").is_file()
            assert (proj_path / "README.md").is_file()
            assert (proj_path / "BABEL.md").is_file()
            assert (proj_path / "QUALITY.md").is_file()
            assert (proj_path / "LICENSE").is_file()
            assert (proj_path / ".github" / "workflows" / "ci.yml").is_file()
            assert (proj_path / "EVIDENCE_RECEIPT.json").is_file()
            assert (proj_path / "tests" / "test_core.py").is_file()
