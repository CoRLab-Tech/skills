---
name: feedback-new-code-needs-tests
description: "Every behavior change ships WITH tests for the new behavior — passing the existing suite is necessary but not sufficient"
metadata:
  type: feedback
---

Running the existing suite green ([[feedback-run-tests-locally]], [[feedback-run-full-test-suite]]) proves the change broke nothing that was already covered. It proves nothing about the new behavior. Every behavior change the loop implements ships **with tests for that behavior**: the happy path, the relevant edge cases, and — for bugfixes — a test that reproduces the bug and fails on the pre-fix code.

**Why:** Untested new code is unprotected new code — the next task's "full suite green" means nothing for behavior no test observes. For bugfixes, the reproducing test is the only proof the fix addresses the actual bug and the only guard against its regression.

**How to apply:**
- For a **bugfix**: write the reproducing test FIRST and watch it fail before implementing the fix; it passing afterwards is the fix's proof. Mention this fail→pass sequence in the PR body.
- For a **feature**: cover the primary path plus the edge cases the issue implies (empty/null input, permission-denied, concurrent/repeat calls — whatever fits the change). Match the repo's existing test style and placement; don't invent a new test layout.
- Pure refactors with zero behavior change are the exception — existing tests ARE the contract; say "no behavior change; covered by existing tests X, Y" in the PR body.
- If the touched area has **no test infrastructure at all**, don't silently skip: state it in the PR body and mirror a "add test coverage for <area>" task into the backlog ([[feedback-todo-opens-backlog-task]] mechanism).
- The PR body lists which tests cover the change — the QA agent ([[feedback-qa-agent-review]]) verifies the claim.
