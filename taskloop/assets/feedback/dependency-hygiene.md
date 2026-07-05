---
name: feedback-dependency-hygiene
description: "New dependencies are a last resort — verify the exact name (typosquats), check advisories and maintenance, pin per repo convention, justify in the PR"
metadata:
  type: feedback
---

Adding a dependency is a supply-chain decision, not a convenience. Prefer the standard library, then code already in the repo, then an already-installed dependency. Only when none fits does a new package enter — and it enters vetted.

**Why:** Every new package is executable third-party code with transitive children, a maintenance bet, and a typosquatting target. Autonomous loops are exactly where a mistyped `npm install` slips through unnoticed — no human paused to read the package name.

**How to apply:**
- First exhaust: stdlib → existing repo utilities → already-installed deps (check `package.json`/lockfile — the helper you need often already ships with something installed).
- When a new dep is genuinely needed, verify before installing: the **exact** package name from the project's official docs (typosquats live one edit away — `lodash` vs `1odash`); weekly downloads / maintenance signals; and known vulnerabilities (`npm audit` after adding to the lockfile, or advisory pages for other ecosystems).
- Pin the version the way the repo already does (exact vs caret — copy the convention in the existing manifest) and commit the lockfile change in the same commit.
- Never add a dependency for something achievable in a few lines; never bump unrelated existing dependencies as a side effect ([[feedback-minimal-diff-scope]]) — if the lockfile churns beyond the new package, regenerate it minimally.
- The PR body justifies the addition in one line: what it does, why in-repo alternatives don't fit, and the audit result. The security gate ([[feedback-security-review-gate]]) double-checks it.
