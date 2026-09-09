"""
Tests for Cryptographic Receipt Engine (SHA-256 tree manifests & Merkle roots).
"""

import tempfile
from pathlib import Path
import pytest
from src.apex_process.core.receipt import CryptographicReceiptEngine


def test_hash_file_deterministic():
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write("APEX CRYPTOGRAPHIC TRUTH")
        f.flush()
        path = Path(f.name)

    digest1 = CryptographicReceiptEngine.hash_file(path)
    digest2 = CryptographicReceiptEngine.hash_file(path)
    assert digest1 == digest2
    assert len(digest1) == 64
    path.unlink()


def test_generate_manifest_and_merkle_root():
    with tempfile.TemporaryDirectory() as tmpdir:
        td = Path(tmpdir)
        (td / "file_a.txt").write_text("Alpha content", encoding="utf-8")
        (td / "sub").mkdir()
        (td / "sub" / "file_b.txt").write_text("Beta content", encoding="utf-8")

        manifest = CryptographicReceiptEngine.generate_manifest(td)
        assert manifest["total_files"] == 2
        assert len(manifest["merkle_root_sha256"]) == 64
        assert len(manifest["files"]) == 2
        paths = [e["path"] for e in manifest["files"]]
        assert "file_a.txt" in paths
        assert "sub/file_b.txt" in paths


def test_manifest_write_and_verify_clean():
    with tempfile.TemporaryDirectory() as tmpdir:
        td = Path(tmpdir)
        (td / "data.py").write_text("x = 100\n", encoding="utf-8")

        mfile = CryptographicReceiptEngine.write_manifest_to_file(td)
        assert mfile.is_file()

        valid, msgs = CryptographicReceiptEngine.verify_manifest(td)
        assert valid is True
        assert len(msgs) == 0


def test_adversarial_tamper_detection_on_file_modification():
    with tempfile.TemporaryDirectory() as tmpdir:
        td = Path(tmpdir)
        p = td / "target.py"
        p.write_text("ORIGINAL CONTENT\n", encoding="utf-8")

        CryptographicReceiptEngine.write_manifest_to_file(td)

        # Modify 1 character
        p.write_text("MODIFIED CONTENT\n", encoding="utf-8")

        valid, msgs = CryptographicReceiptEngine.verify_manifest(td)
        assert valid is False
        assert any("TAMPERED" in m for m in msgs)


def test_adversarial_tamper_detection_on_file_deletion():
    with tempfile.TemporaryDirectory() as tmpdir:
        td = Path(tmpdir)
        p1 = td / "a.py"
        p2 = td / "b.py"
        p1.write_text("a", encoding="utf-8")
        p2.write_text("b", encoding="utf-8")

        CryptographicReceiptEngine.write_manifest_to_file(td)

        # Delete b.py
        p2.unlink()

        valid, msgs = CryptographicReceiptEngine.verify_manifest(td)
        assert valid is False
        assert any("MISSING" in m for m in msgs)


def test_adversarial_tamper_detection_on_unrecorded_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        td = Path(tmpdir)
        p1 = td / "a.py"
        p1.write_text("a", encoding="utf-8")

        CryptographicReceiptEngine.write_manifest_to_file(td)

        # Add new unrecorded file
        p2 = td / "rogue.py"
        p2.write_text("malicious payload", encoding="utf-8")

        valid, msgs = CryptographicReceiptEngine.verify_manifest(td)
        assert valid is False
        assert any("UNRECORDED" in m for m in msgs)
