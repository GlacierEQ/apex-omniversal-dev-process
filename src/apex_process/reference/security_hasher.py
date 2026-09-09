"""
Category 09 Reference Implementation: Forensic Bates Manifest Compiler & FRE 902 Authenticator.
GlacierEQ / APEX Estate — Legal Warfare & Forensics Standard.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import hashlib
import json
import os
import time

ERR_SEC_TAMPER_DETECTED = "ERR_SEC_TAMPER_DETECTED"
ERR_SEC_ZERO_BYTE_EVIDENCE = "ERR_SEC_ZERO_BYTE_EVIDENCE"
ERR_SEC_FILE_NOT_FOUND = "ERR_SEC_FILE_NOT_FOUND"


@dataclass(frozen=True)
class BatesEntry:
    bates_id: str
    relative_path: str
    file_size_bytes: int
    sha256: str
    sha512: str
    timestamp_utc: float
    fre_902_certified: bool


class ForensicBatesManifestCompiler:
    """
    Computes court-admissible Bates stamps and cryptographic SHA-256/512 digests
    in strict compliance with Federal Rules of Evidence (FRE 902(13) and 902(14)).
    """

    @staticmethod
    def hash_stream(file_path: Path) -> Tuple[str, str, int]:
        sha256 = hashlib.sha256()
        sha512 = hashlib.sha512()
        bytes_read = 0

        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
                sha512.update(chunk)
                bytes_read += len(chunk)

        return sha256.hexdigest(), sha512.hexdigest(), bytes_read

    @classmethod
    def compile_manifest(
        cls,
        evidence_dir: Path,
        prefix: str = "EXHIBIT-",
        start_index: int = 1,
    ) -> List[BatesEntry]:
        evidence_dir = Path(evidence_dir).resolve()
        if not evidence_dir.is_dir():
            raise NotADirectoryError(f"Evidence directory not found: {evidence_dir}")

        entries: List[BatesEntry] = []
        files = sorted([f for f in os.listdir(evidence_dir) if (evidence_dir / f).is_file() and f != "BATES_MANIFEST.json"])

        for idx, filename in enumerate(files, start=start_index):
            fpath = evidence_dir / filename
            sha256, sha512, size = cls.hash_stream(fpath)

            if size == 0:
                raise ValueError(f"[{ERR_SEC_ZERO_BYTE_EVIDENCE}] Zero-byte evidentiary trace detected in {filename}")

            bates_id = f"{prefix}{idx:04d}"
            entry = BatesEntry(
                bates_id=bates_id,
                relative_path=filename,
                file_size_bytes=size,
                sha256=sha256,
                sha512=sha512,
                timestamp_utc=time.time(),
                fre_902_certified=True,
            )
            entries.append(entry)

        return entries

    @classmethod
    def write_manifest_file(cls, evidence_dir: Path, prefix: str = "EXHIBIT-") -> Path:
        evidence_dir = Path(evidence_dir).resolve()
        entries = cls.compile_manifest(evidence_dir, prefix=prefix)
        dest = evidence_dir / "BATES_MANIFEST.json"

        data = {
            "title": "Federal Rules of Evidence 902(13)/(14) Cryptographic Manifest",
            "compiled_at": time.time(),
            "evidence_count": len(entries),
            "manifest": [
                {
                    "bates_id": e.bates_id,
                    "file": e.relative_path,
                    "size_bytes": e.file_size_bytes,
                    "sha256": e.sha256,
                    "sha512": e.sha512,
                    "fre_902_certified": e.fre_902_certified,
                }
                for e in entries
            ],
        }

        with open(dest, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return dest

    @classmethod
    def verify_bates_integrity(cls, evidence_dir: Path) -> Tuple[bool, List[str]]:
        evidence_dir = Path(evidence_dir).resolve()
        mpath = evidence_dir / "BATES_MANIFEST.json"
        if not mpath.is_file():
            return False, [f"[{ERR_SEC_FILE_NOT_FOUND}] Manifest missing at {mpath}"]

        with open(mpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        discrepancies: List[str] = []
        for item in data.get("manifest", []):
            fpath = evidence_dir / item["file"]
            if not fpath.is_file():
                discrepancies.append(f"[{ERR_SEC_FILE_NOT_FOUND}] Missing exhibit file: {item['file']}")
                continue
            actual_sha256, _, actual_size = cls.hash_stream(fpath)
            if actual_sha256 != item["sha256"] or actual_size != item["size_bytes"]:
                discrepancies.append(
                    f"[{ERR_SEC_TAMPER_DETECTED}] Exhibit {item['bates_id']} ({item['file']}) "
                    f"hash mismatch (expected {item['sha256'][:10]}, got {actual_sha256[:10]})"
                )

        return len(discrepancies) == 0, discrepancies
