"""
Tests for AST Stub Sentinel: Enforcing Zero-Stub Invariant (Gate G8).
"""

import tempfile
from pathlib import Path
import pytest
from src.apex_process.auditors.ast_sentinel import ASTStubSentinel


def test_clean_python_code_has_zero_defects():
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
        f.write('''
def calculate_hash(data: str) -> str:
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest()

class DataEngine:
    def process(self, value: int) -> int:
        multiplier = 2
        return value * multiplier
''')
        f.flush()
        path = Path(f.name)

    defects = ASTStubSentinel.scan_python_file(path)
    path.unlink()
    assert len(defects) == 0


def test_detects_bare_pass_stub():
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
        f.write('''
def unwritten_function():
    pass
''')
        f.flush()
        path = Path(f.name)

    defects = ASTStubSentinel.scan_python_file(path)
    path.unlink()
    assert len(defects) == 1
    assert defects[0].defect_type == "BARE_PASS_STUB"
    assert defects[0].symbol_name == "unwritten_function"


def test_detects_trivial_return_true_stub():
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
        f.write('''
def fake_validation():
    return True
''')
        f.flush()
        path = Path(f.name)

    defects = ASTStubSentinel.scan_python_file(path)
    path.unlink()
    assert len(defects) == 1
    assert defects[0].defect_type == "TRIVIAL_RETURN_True"


def test_detects_not_implemented_raise():
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
        f.write('''
def missing_feature():
    raise NotImplementedError
''')
        f.flush()
        path = Path(f.name)

    defects = ASTStubSentinel.scan_python_file(path)
    path.unlink()
    assert len(defects) == 1
    assert defects[0].defect_type == "UNIMPLEMENTED_RAISE_STUB"


def test_detects_polyglot_rust_unimplemented():
    with tempfile.NamedTemporaryFile("w+", suffix=".rs", delete=False) as f:
        f.write('''
fn calculate_metric() -> u64 {
    unimplemented!()
}
''')
        f.flush()
        path = Path(f.name)

    defects = ASTStubSentinel.scan_polyglot_file(path)
    path.unlink()
    assert len(defects) == 1
    assert defects[0].defect_type == "RUST_UNIMPLEMENTED_MACRO"


def test_ignores_abstractmethod_decorators():
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
        f.write('''
from abc import abstractmethod

class BaseContract:
    @abstractmethod
    def abstract_interface(self):
        pass
''')
        f.flush()
        path = Path(f.name)

    defects = ASTStubSentinel.scan_python_file(path)
    path.unlink()
    assert len(defects) == 0


def test_detects_docstring_only_stub():
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
        f.write('''
def fake_docstring_function():
    """This function only has a docstring and no code."""
''')
        f.flush()
        path = Path(f.name)

    defects = ASTStubSentinel.scan_python_file(path)
    path.unlink()
    assert len(defects) == 1
    assert defects[0].defect_type == "DOCSTRING_ONLY_STUB"


def test_detects_assign_return_trivial_stub():
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
        f.write('''
def fake_mock_logic():
    result = True
    return result
''')
        f.flush()
        path = Path(f.name)

    defects = ASTStubSentinel.scan_python_file(path)
    path.unlink()
    assert len(defects) == 1
    assert defects[0].defect_type == "ASSIGN_RETURN_TRIVIAL_STUB"

