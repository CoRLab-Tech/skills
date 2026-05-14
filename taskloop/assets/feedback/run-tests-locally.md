---
name: feedback-run-tests-locally
description: "Always run the project's test suite locally before opening a PR — tsc + eslint are not enough"
metadata:
  type: feedback
---

Before pushing and opening a PR, run the project's unit test suite locally (`npm test` for npm-based services, `yarn test` / `npx jest` for yarn-based ones). Type-checking and linting are not substitutes. CI runs the same command in the PR build workflow and will fail the PR if any test breaks — that's a wasted iteration.

**Why:** A previous correction made it explicit: `tsc --noEmit` + `eslint` passing routinely hide failing tests. CI then caught them and the PR had to be re-pushed. Running tests locally before push is the cheapest way to avoid that whole round-trip.

**How to apply:**
1. Determine the package manager: `package-lock.json` → `npm test`; `yarn.lock` → `yarn test`. Use the **exact** command CI runs (check the workflow YAML) — `npx jest` directly bypasses npm/yarn lifecycle hooks and may behave differently.
2. Capture the exit code explicitly: `cmd > /tmp/log 2>&1; echo "exit=$?"`. Do NOT pipe to `tail` then read `$?` — that reports the pipe's last segment, not the test runner.
3. The test step belongs **after** `tsc --noEmit` and `eslint` in the verification ritual, before commit + push.
4. If a test fails (whether related to your change or not), fix it before opening the PR. If the failure is genuinely pre-existing and unrelated, surface it clearly in the PR body rather than silently ignoring.
5. Linked to [[feedback-run-full-test-suite]] (which mandates the full suite, no path filter) and [[feedback-playwright-testing]] (the UI gate).
