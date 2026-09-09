"""
Tests for apex-process CLI commands.
"""

import tempfile
from pathlib import Path
import pytest
from src.apex_process.cli import main


def test_cli_matrix_invocation(capsys):
    ret = main(["matrix"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "12 ENGINEERING CATEGORIES" in captured.out
    assert "systems_and_kernels" in captured.out


def test_cli_matrix_json(capsys):
    ret = main(["matrix", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    assert '"categories"' in captured.out
    assert '"stages"' in captured.out


def test_cli_guide_invocation(capsys):
    ret = main(["guide", "ai_ml_llms", "--stage", "2"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Artificial Intelligence, LLMs & Machine Learning" in captured.out
    assert "STAGE 2" in captured.out


def test_cli_init_and_audit_flow(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir)
        ret_init = main(["init", "distributed_backends", "test_dist_service", "--dest", str(dest)])
        assert ret_init == 0

        project_dir = dest / "test_dist_service"
        assert project_dir.is_dir()

        ret_audit = main(["audit", str(project_dir)])
        assert ret_audit == 0

        ret_stubs = main(["check-stubs", str(project_dir)])
        assert ret_stubs == 0

        ret_receipt = main(["receipt", str(project_dir), "--verify"])
        assert ret_receipt == 0
