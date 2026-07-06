---
name: feedback-regression-is-blocker
description: "Always run/watch the tests when a PR opens — any test regression is a hard blocker, nothing else proceeds until green"
metadata:
  type: feedback
---

Opening a PR always triggers the tests twice over: the full local suite BEFORE the PR ([[feedback-run-full-test-suite]]) and the PR's CI checks right after `gh pr create`. Watch the CI checks to completion. Any failing test — a regression — is a **HARD BLOCKER**: nothing else happens until it is fixed.

**Why:** A red PR is worse than no PR — it wastes reviewer attention, blocks the merge queue, and hides whether the feature works at all. Treating regressions as blockers keeps every loop-opened PR merge-ready at all times.

**How to apply:**
- After `gh pr create`, run `gh pr checks <num> --watch` (or poll `gh pr checks <num>` until no check is pending).
- If any check fails: STOP. Do not transition the issue to the review status, do not pull the next task. Reproduce locally, fix, re-run the full local suite, push, and re-watch the checks.
- Only a fully green check run allows the issue to move to the review status.
- **"No checks reported" on a DRAFT is ambiguous** — it means either "no CI configured" or "this repo's workflows skip drafts" (`ready_for_review` triggers, `if: !draft` jobs). Before invoking the no-CI fallback, verify the repo genuinely has no PR workflows (inspect `.github/workflows/` triggers or the default branch's required checks). Only when the repo truly has no CI does the local full-suite run become the gate — note "no CI configured" in the PR body and proceed.
- **After the step-11 `gh pr ready` flip, re-watch once** (`gh pr checks <num> --watch`): flipping to ready is exactly the event that starts draft-skipped workflows. If a newly-started check fails, flip both back (PR → draft, ticket → In Progress) and fix — step 11 is not complete until the post-flip watch is green or confirms no new checks started.
- The per-tick PR sweep ([[feedback-watch-pr-comments]]) re-checks previously opened PRs: one that has gone red since (merge conflict, flaky main) is picked up as a blocker there too, with priority over new tasks.
- If a failure is a genuinely pre-existing default-branch breakage unrelated to the diff, document it explicitly in the PR body and the tracker comment — never silently ignore a red check.
- The ONLY sanctioned exit from a red PR that won't converge is [[feedback-fail-gracefully-timebox]]: when its timebox is exhausted, mark the PR draft with the blocker documented, hand the issue back to triage, and move on — "stop everything" means no gate-skipping, not an infinite grind.
