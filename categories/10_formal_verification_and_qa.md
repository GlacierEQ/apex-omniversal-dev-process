# 🔬 CATEGORY 10: Formal Verification, Testing & Epistemic QA

## 1. Scope & Architectural Mandate
Governs mathematical proof assistants, invariant assertions, property-based testing, fuzzing, and the 6-Tier Epistemic Verification Ladder ($\mathcal{L}_0 \to \mathcal{L}_6$).

- **Domains**: Formal theorem provers (Lean 4, Dafny, Coq/Rocq), property-based testing (Hypothesis/fast-check), automated fuzzing (AFL, libFuzzer), AST syntactic invariant checkers, continuous epistemic test runners.
- **Key Constraints**: 100% test pass rate, zero stubs (`pass`, `return True`), minimum test density ($\ge 8$ tests per leaf repo, $\ge 4$ adversarial/refusal tests), fresh verification execution.

---

## 2. Polyglot Technology Stack
- **Languages**: Python (pytest, Hypothesis), TypeScript (Vitest, Playwright), Lean 4 (formal invariant proofs), Rust (`cargo test`, `cargo-fuzz`).
- **Linters & Analyzers**: `flake8`, `mypy`, `eslint`, `clippy`, custom Python AST sentinels.

---

## 3. Core Invariants & Fail-Closed Boundaries
1. **The Epistemic Law of Action**:
   - Operational mutations must be grounded in $\mathcal{L}_2$ (Behavioral Proof: passing tests + SHA-256).
   - Enterprise production releases require $\mathcal{L}_5$ (Dialectic Swarm Consensus).
2. **Zero-Stub Enforcement**:
   - Shipped functional code must execute real domain logic. Stubs, placeholders, and unverified mock shortcuts are rejected as defects.
3. **Refusal Reason Codes**:
   - `ERR_QA_ASSERTION_FAILED`: Unit or property-based invariant test assertion failed.
   - `ERR_QA_STUB_DETECTED`: AST parser found `pass`, `return True`, or trivial placeholder.
   - `ERR_QA_INSUFFICIENT_ADVERSARIAL_TESTS`: Repository has fewer than 4 adversarial test cases.
   - `ERR_QA_UNVERIFIED_COMPLETION`: Success claimed without fresh execution output in current turn.

---

## 4. Stage-by-Stage Implementation Guide

### Stage 0: Contracting
- Specify the invariant properties to be mathematically or empirically proven.
- Draft the test matrix: Unit proofs, Adversarial refusal tests, Concurrency stress tests, Fuzzing parameters.

### Stage 1: Architectural Modeling
- Define property test generators and boundary value limits (e.g., negative integers, max string length, empty sets).
- Express state invariants in mathematical notation.

### Stage 2: Pro-Code Implementation
- Write code against failing tests (TDD Red-Green cycle).
- Ensure every branch has a deterministic return path.

### Stage 3: Adversarial Verification
- Run property-based tests across 10,000 randomized iterations.
- Run the AST stub detector across all source files.
- Execute full test suite and capture exit code 0.

---

## 5. Reference Pattern: AST Syntactic Stub Sentinel
```python
import ast
from typing import List, Dict, Any

class ASTStubSentinel(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.defects: List[Dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Inspect function body for trivial stubs
        if len(node.body) == 1:
            first_stmt = node.body[0]
            # Detect bare 'pass'
            if isinstance(first_stmt, ast.Pass):
                self.defects.append({
                    "file": self.filename,
                    "line": node.lineno,
                    "function": node.name,
                    "type": "BARE_PASS_STUB",
                    "code": "ERR_QA_STUB_DETECTED"
                })
            # Detect bare 'return True' or 'return None'
            elif isinstance(first_stmt, ast.Return) and isinstance(first_stmt.value, ast.Constant):
                if first_stmt.value.value in (True, None):
                    self.defects.append({
                        "file": self.filename,
                        "line": node.lineno,
                        "function": node.name,
                        "type": f"TRIVIAL_RETURN_{first_stmt.value.value}",
                        "code": "ERR_QA_STUB_DETECTED"
                    })
        self.generic_visit(node)
```
