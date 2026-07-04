---
name: feedback-security-review-gate
description: "Every PR passes a security review — the security-review skill when available, else a manual checklist pass — before the issue transitions"
metadata:
  type: feedback
---

Every PR the loop opens gets a **security pass** alongside the correctness gates. When the `security-review` skill is available in the session, invoke it against the branch's pending changes. When it isn't, run a manual pass over the diff against the checklist below. Blocking findings are treated exactly like failing tests.

**Why:** `/review` and `rigorous` hunt correctness and design; neither is tuned for exploitability. Autonomous code that ships without a security lens is how injection points, broken authz, and leaked internal URLs reach production with nobody having ever looked.

**How to apply:**
- After `gh pr create`, alongside the other gates ([[feedback-run-code-review]], [[feedback-rigorous-pr-critique]]): run the `security-review` skill (Skill tool) on the branch if available; otherwise review the diff manually for at minimum — injection (SQL/shell/template), authz on every new/changed endpoint (object-level, not just authenticated), secrets or internal hostnames in code or logs, SSRF on user-supplied URLs, path traversal on user-supplied paths, unsafe deserialization, XSS on rendered user input, missing rate limits on unauthenticated endpoints, and **new or changed dependencies** — exact package name against the official docs (typosquat check), advisory/audit result (`npm audit` or ecosystem equivalent), lockfile churn limited to the new package's closure ([[feedback-dependency-hygiene]]).
- Findings rated blocking (realistically exploitable) → fix on the PR branch before the issue transitions to review. Non-blocking observations → note them in the PR body.
- Changes touching auth, permissions, file upload/download, payment, or user-input parsing get the deepest look — those diffs are never "too small to bother".
- Record in the PR body that a security pass ran and what it covered — the human reviewer should not have to guess.
