---
name: feedback-run-full-test-suite
description: "Run the FULL test suite (no path filter) and confirm every test passes before opening a PR"
metadata:
  type: feedback
---

After implementing any code change, run the **entire test suite** of the affected service (e.g. `yarn test` or `npm test` with no path filter) and confirm **every test passes** before pushing or opening a PR. Running only the modified spec file is not enough.

**Why:** A targeted spec run only proves the file you touched still compiles and its own tests pass — it cannot catch regressions in other suites that import the same module, share mocks, or rely on side effects you altered. Coverage thresholds also fail differently when only one spec runs. Confidence requires the whole suite green.

**How to apply:**
- After every Edit/Write step that changes runtime code or test fixtures, run the full suite in the affected service before `git push`.
- If the suite has coverage thresholds (check `jest` config in `package.json`), they're evaluated against the actual run. A single-spec run will skew totals. Run the full suite so thresholds match CI.
- If any test fails, fix it before opening the PR. Do not push and rely on CI to surface it.
- Sits on top of [[feedback-run-tests-locally]]: that rule mandates running tests locally; this one mandates running the *full* suite, not just the modified file.
- When a service's full suite is genuinely too slow / requires external infra to boot, say so explicitly in the PR description and run as much as can be run locally — never silently skip.
