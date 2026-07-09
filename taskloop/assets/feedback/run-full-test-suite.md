---
name: feedback-run-full-test-suite
description: "Run the FULL test suite locally before every PR — the exact command CI runs, no path filter; tsc + eslint are not enough"
metadata:
  type: feedback
---

Before pushing and opening a PR, run the **entire test suite** of the affected service locally and confirm **every test passes**. Type-checking and linting are not substitutes — `tsc --noEmit` + `eslint` passing routinely hide failing tests. And running only the modified spec file is not enough either: a targeted run cannot catch regressions in other suites that import the same module, share mocks, or rely on side effects you altered, and coverage thresholds evaluate differently on partial runs.

**Why:** CI runs the same command in the PR build and will fail the PR if any test breaks — that's a wasted iteration. Confidence requires the whole suite green, locally, before the push.

**How to apply:**
1. Use the **exact** command CI runs — check the workflow YAML. `package-lock.json` → `npm test`; `yarn.lock` → `yarn test`. Bare `npx jest` bypasses npm/yarn lifecycle hooks and may behave differently.
2. No path filter — the full suite. If the suite has coverage thresholds (check the jest config), a single-spec run skews totals; run everything so thresholds match CI.
3. Capture the exit code explicitly: `cmd > /tmp/log 2>&1; echo "exit=$?"`. Do NOT pipe to `tail` then read `$?` — that reports the pipe's last segment, not the test runner.
4. The test step comes **after** `tsc --noEmit` and `eslint` in the verification ritual, before commit + push.
5. If any test fails — related to your change or not — fix it before the PR. If the failure is genuinely pre-existing and unrelated, surface it explicitly in the PR body rather than silently ignoring. Never push and rely on CI to catch it.
6. The "can't run the full suite" exception is bounded, not self-declared: it applies ONLY when the suite needs credentials/infra this machine lacks, or when a **measured** run exceeds ~30 minutes wall-clock (attempt it before claiming). The PR body must then name the exact command attempted, the concrete blocker or measured runtime, and precisely which subset WAS run.
7. Linked to [[feedback-new-code-needs-tests]] (tests ship WITH the change) and [[feedback-ui-verification-and-evidence]] (the UI gate).
