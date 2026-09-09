# 🤝 CONTRIBUTING.md: The APEX Epistemic Engineering Standard

We welcome contributions to `apex-omniversal-dev-process`. However, this repository is governed by the **Ascended 6-Tier Epistemic Ladder** and the **Bodybuilder Definition of Done**.

Pull Requests that fail to meet these invariants will be automatically rejected by CI gates.

---

## 🛑 Strict Requirements for All Contributions

1. **Zero-Stub Mandate**:
   - Do **NOT** submit code containing `pass`, `return True`, `return None` placeholders, or `TODO` comments in functional surfaces.
   - The AST sentinel runs automatically on every commit and will fail the build if a stub is detected.

2. **The Epistemic Law of Action ($\mathcal{L}_2$)**:
   - Every pull request must include tests proving the behavior of the added or modified functionality.
   - PR description must provide fresh command execution output proving all tests pass.

3. **Fail-Closed Architecture & Refusal Codes**:
   - Modules must specify explicit refusal reason codes for malformed or boundary-violating inputs.
   - Minimum test requirements for any new leaf component:
     $$\text{Total Test Cases} \ge 8 \quad\land\quad \text{Adversarial/Refusal Tests} \ge 4$$

4. **Honesty Contract**:
   - If an edge case is unresolved, document it explicitly under "Open Frontiers" in `QUALITY.md`. Never disguise an unhandled exception as functional code.

5. **Cryptographic Receipt Refresh**:
   - Update `EVIDENCE_RECEIPT.json` using `python3 -m apex_process.cli receipt .` before opening the PR.
