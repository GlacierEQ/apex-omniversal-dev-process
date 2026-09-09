"""
Cryptographic Receipt Engine: Deterministic SHA-256 Tree Manifest & Merkle Root.
GlacierEQ / APEX Estate — FRE 902 Forensic Standard.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import hashlib
import json
import os
import time


class CryptographicReceiptEngine:
    """
    Computes and verifies deterministic SHA-256 tree manifests for codebases.
    Ensures bit-for-bit forensic provenance and tamper detection.
    """

    DEFAULT_EXCLUDES = [
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".DS_Store",
        "venv",
        ".venv",
        "*.pyc",
        "EVIDENCE_RECEIPT.json",
    ]

    @staticmethod
    def hash_file(file_path: Path) -> str:
        """Computes deterministic SHA-256 digest of a file in 64KB chunks."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    @classmethod
    def _is_excluded(cls, rel_path: Path, excludes: List[str]) -> bool:
        parts = rel_path.parts
        for part in parts:
            if part in excludes:
                return True
            for pat in excludes:
                if pat.startswith("*") and part.endswith(pat[1:]):
                    return True
        return False

    @classmethod
    def generate_manifest(
        cls,
        target_dir: Path,
        excludes: Optional[List[str]] = None,
        operator: str = "APEX-OPERATOR-G",
    ) -> Dict[str, Any]:
        """Traverses directory, computes SHA-256 for each file, and builds Merkle root."""
        target_dir = Path(target_dir).resolve()
        if not target_dir.is_dir():
            raise NotADirectoryError(f"Target is not a directory: {target_dir}")

        effective_excludes = list(cls.DEFAULT_EXCLUDES)
        if excludes:
            effective_excludes.extend(excludes)

        file_entries: List[Dict[str, Any]] = []
        all_digests: List[str] = []

        for root, dirs, files in os.walk(target_dir):
            # Sort for determinism
            dirs.sort()
            files.sort()

            for fname in files:
                full_path = Path(root) / fname
                rel_path = full_path.relative_to(target_dir)

                if cls._is_excluded(rel_path, effective_excludes):
                    continue

                if full_path.is_file():
                    digest = cls.hash_file(full_path)
                    size = full_path.stat().st_size
                    file_entries.append({
                        "path": str(rel_path),
                        "sha256": digest,
                        "size_bytes": size,
                    })
                    all_digests.append(digest)

        # Sort file entries by path for deterministic Merkle calculation
        file_entries.sort(key=lambda x: x["path"])

        # Compute Merkle Root of all concatenated digests
        merkle_hasher = hashlib.sha256()
        for digest in sorted(all_digests):
            merkle_hasher.update(digest.encode())
        merkle_root = merkle_hasher.hexdigest()

        return {
            "version": "1.0.0",
            "timestamp": time.time(),
            "target_directory": str(target_dir),
            "operator": operator,
            "merkle_root_sha256": merkle_root,
            "total_files": len(file_entries),
            "files": file_entries,
        }

    @classmethod
    def write_manifest_to_file(
        cls,
        target_dir: Path,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Writes the generated manifest to EVIDENCE_RECEIPT.json."""
        target_dir = Path(target_dir).resolve()
        manifest = cls.generate_manifest(target_dir)
        dest = output_path if output_path else target_dir / "EVIDENCE_RECEIPT.json"

        with open(dest, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return dest

    @classmethod
    def verify_manifest(
        cls,
        target_dir: Path,
        manifest_path: Optional[Path] = None,
    ) -> Tuple[bool, List[str]]:
        """Verifies current state of disk against the recorded manifest."""
        target_dir = Path(target_dir).resolve()
        mpath = manifest_path if manifest_path else target_dir / "EVIDENCE_RECEIPT.json"

        if not mpath.is_file():
            return False, [f"Manifest file missing at {mpath}"]

        with open(mpath, "r", encoding="utf-8") as f:
            recorded = json.load(f)

        discrepancies: List[str] = []
        recorded_files: Dict[str, str] = {
            entry["path"]: entry["sha256"] for entry in recorded.get("files", [])
        }

        # Check existing files
        for rel_path_str, expected_digest in recorded_files.items():
            full_path = target_dir / rel_path_str
            if not full_path.is_file():
                discrepancies.append(f"MISSING: File deleted or moved: {rel_path_str}")
                continue
            actual_digest = cls.hash_file(full_path)
            if actual_digest != expected_digest:
                discrepancies.append(
                    f"TAMPERED: Digest mismatch for {rel_path_str} "
                    f"(expected {expected_digest[:8]}, got {actual_digest[:8]})"
                )

        # Check for unrecorded new files
        current_manifest = cls.generate_manifest(target_dir)
        current_files = {entry["path"] for entry in current_manifest["files"]}
        for curr in current_files:
            if curr not in recorded_files:
                discrepancies.append(f"UNRECORDED: New uncommitted file present: {curr}")

        return len(discrepancies) == 0, discrepancies
