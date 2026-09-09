"""
AST Syntactic Stub Sentinel: Enforcing Zero-Regression & Zero-Stub Invariant (Gate G8).
GlacierEQ / APEX Estate — Pro-Code Doctrine.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional
import ast
import os
import re


@dataclass(frozen=True)
class StubDefect:
    file_path: str
    line_number: int
    symbol_name: str
    defect_type: str
    reason_code: str
    message: str


class ASTStubSentinel:
    """
    Parses source code abstract syntax trees to detect permissive stubs,
    unimplemented placeholders, and trivial mocks in production surfaces.
    """

    STUB_REASON_CODE = "ERR_QA_STUB_DETECTED"

    @classmethod
    def scan_python_file(cls, file_path: Path) -> List[StubDefect]:
        defects: List[StubDefect] = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError) as e:
            defects.append(
                StubDefect(
                    file_path=str(file_path),
                    line_number=getattr(e, "lineno", 1) or 1,
                    symbol_name="<FILE_PARSE>",
                    defect_type="SYNTAX_PARSE_ERROR",
                    reason_code=cls.STUB_REASON_CODE,
                    message=f"Failed to parse Python AST: {str(e)}",
                )
            )
            return defects

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip abstract methods or protocols
                is_abstract = any(
                    isinstance(dec, ast.Name) and dec.id in ("abstractmethod", "overload")
                    or (isinstance(dec, ast.Attribute) and dec.attr in ("abstractmethod", "overload"))
                    for dec in node.decorator_list
                )
                if is_abstract:
                    continue

                # Inspect single-statement function bodies
                if len(node.body) == 1:
                    stmt = node.body[0]

                    # 1. Bare pass
                    if isinstance(stmt, ast.Pass):
                        defects.append(
                            StubDefect(
                                file_path=str(file_path),
                                line_number=node.lineno,
                                symbol_name=node.name,
                                defect_type="BARE_PASS_STUB",
                                reason_code=cls.STUB_REASON_CODE,
                                message=f"Function '{node.name}' contains a bare 'pass' placeholder.",
                            )
                        )

                    # 2. Bare return True / False / None
                    elif isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Constant):
                        if stmt.value.value in (True, False, None):
                            defects.append(
                                StubDefect(
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    symbol_name=node.name,
                                    defect_type=f"TRIVIAL_RETURN_{stmt.value.value}",
                                    reason_code=cls.STUB_REASON_CODE,
                                    message=f"Function '{node.name}' contains a trivial single 'return {stmt.value.value}' stub.",
                                )
                            )

                    # 3. Bare raise NotImplementedError
                    elif isinstance(stmt, ast.Raise):
                        exc = stmt.exc
                        if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                            defects.append(
                                StubDefect(
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    symbol_name=node.name,
                                    defect_type="UNIMPLEMENTED_RAISE_STUB",
                                    reason_code=cls.STUB_REASON_CODE,
                                    message=f"Function '{node.name}' raises bare 'NotImplementedError' in non-abstract body.",
                                )
                            )
                        elif isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) and exc.func.id == "NotImplementedError":
                            defects.append(
                                StubDefect(
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    symbol_name=node.name,
                                    defect_type="UNIMPLEMENTED_RAISE_STUB",
                                    reason_code=cls.STUB_REASON_CODE,
                                    message=f"Function '{node.name}' raises 'NotImplementedError()' in non-abstract body.",
                                )
                            )

        return defects

    @classmethod
    def scan_polyglot_file(cls, file_path: Path) -> List[StubDefect]:
        """Scans Rust, TypeScript, C++, and Go files for common stub markers."""
        defects: List[StubDefect] = []
        ext = file_path.suffix.lower()

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            return defects

        patterns = {
            ".rs": [
                (re.compile(r"\bunimplemented!\(\)"), "RUST_UNIMPLEMENTED_MACRO"),
                (re.compile(r"\btodo!\(\)"), "RUST_TODO_MACRO"),
            ],
            ".ts": [
                (re.compile(r"\{\s*throw new Error\(['\"]Not implemented['\"]\);?\s*\}"), "TS_NOT_IMPLEMENTED"),
            ],
            ".js": [
                (re.compile(r"\{\s*throw new Error\(['\"]Not implemented['\"]\);?\s*\}"), "JS_NOT_IMPLEMENTED"),
            ],
            ".go": [
                (re.compile(r"\bpanic\(['\"]not implemented['\"]\)\b"), "GO_NOT_IMPLEMENTED"),
            ],
        }

        file_patterns = patterns.get(ext, [])
        for line_no, line in enumerate(lines, start=1):
            # Skip commented lines
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("#"):
                continue

            for regex, defect_type in file_patterns:
                if regex.search(line):
                    defects.append(
                        StubDefect(
                            file_path=str(file_path),
                            line_number=line_no,
                            symbol_name="<POLYGON_STUB>",
                            defect_type=defect_type,
                            reason_code=cls.STUB_REASON_CODE,
                            message=f"Found placeholder stub in line: '{stripped}'",
                        )
                    )

        return defects

    @classmethod
    def audit_directory(
        cls,
        target_dir: Path,
        excludes: Optional[List[str]] = None,
    ) -> List[StubDefect]:
        """Audits all code files in the directory for stub patterns."""
        target_dir = Path(target_dir).resolve()
        effective_excludes = [
            ".git", "__pycache__", ".pytest_cache", "node_modules", "venv", ".venv", "tests"
        ]
        if excludes:
            effective_excludes.extend(excludes)

        all_defects: List[StubDefect] = []

        for root, dirs, files in os.walk(target_dir):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in effective_excludes]

            for fname in files:
                fpath = Path(root) / fname
                ext = fpath.suffix.lower()

                if ext == ".py":
                    all_defects.extend(cls.scan_python_file(fpath))
                elif ext in (".rs", ".ts", ".js", ".go"):
                    all_defects.extend(cls.scan_polyglot_file(fpath))

        return all_defects
