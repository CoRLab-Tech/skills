---
name: feedback-ci-failure-triage
description: "GitHub CI is the authority on a PR branch. When a check fails, triage the CAUSE first: a code failure is a hard blocker; a billing or infrastructure failure falls back to local foreground gates plus an explicit PR comment saying CI was red and why the loop proceeded"
metadata:
  type: feedback
---

**Default: trust GitHub CI.** It runs on the merge-relevant commit, on a clean checkout, with no local cache to hide a missing dependency. Watch it to completion and treat a red check as a hard blocker ([[feedback-regression-is-blocker]]). The loop does not get to grade its own homework while a red check sits on the PR.

**The exception is a check that never actually ran your code.** When Actions is out of billing, disabled org-wide, or throttled by a burst of branch pushes, the job fails without executing a single test. That red says nothing about the diff, and a loop that treats it as a code blocker wedges permanently on an unpayable runner.

So on **every failing check, triage the cause before reacting:**

**Code failure → hard blocker. No fallback, ever.** A named test failed, a type error, a lint violation, a build error — the logs exist and name the defect. Fix it on the branch, re-run the full local suite, push, re-watch. Never substitute a local run for a red check that genuinely ran your code.

**Billing or infrastructure failure → local fallback, loudly.** Requires *positive evidence*, not a guess:

- the job fails in seconds with no log blob (`BlobNotFound`, empty log, "job was not started");
- an explicit billing / quota / spending-limit / "Actions disabled" / payment message;
- an org-wide `402` or `403` from the Actions API;
- a control observation: `main` and older branches stay green, or a burst of freshly-pushed branches all fail identically and instantly, on code that differs.

Only then:

1. Run the FULL gate locally, in the foreground, on the branch ([[feedback-gates-run-foreground]]): typecheck + lint + the full suite ([[feedback-run-full-test-suite]]) + build.
2. **Post an explicit PR comment.** Never let the PR read as if CI passed. State, in this order: that CI is **red**; the quoted infra/billing reason; that the loop therefore verified locally; the exact commands run and their results. For example: *"CI is red — the `verify` job failed in 2s with no log blob (Actions spending limit reached), so it never ran this diff. Verified locally on the branch instead: `pnpm typecheck` ✓, `pnpm lint` ✓, `pnpm test` ✓ (412 passed), `pnpm build` ✓."*
3. Proceed to `gh pr ready` only if the local gate is green ([[feedback-draft-until-gated]]). A local red is a blocker exactly like a CI red.
4. **Ping the owner once** ([[feedback-telegram-notify-owner]]): billing is something only they can fix, and every subsequent PR will hit the same wall.

**Fail closed on ambiguity.** If you cannot produce the positive evidence above, it is a code failure. A loop that guesses "probably billing" and skips to a local run will eventually ship a genuinely broken PR with a comment claiming it verified. The whole rule rests on that asymmetry: mislabelling infra as code costs one wasted investigation; mislabelling code as infra ships the bug.

**Do not `gh run rerun` a billing-failed job** — it cannot succeed and burns the loop's tick. Re-running a *throttled* job once is acceptable; twice is a loop.

**`main` after a merge is never covered by this fallback.** Branch gates run on the branch, not on the merge result: under parallel PRs two individually-green branches can be red together. `main`'s post-merge CI runs once per merge and is the only merge-result verification there is — a red `main` is a drop-everything blocker ([[feedback-regression-is-blocker]]). If Actions is unavailable even for `main`, run the full suite on a fresh `origin/main` checkout instead, and say so.

**Why:** remote CI and local gates fail for different reasons, and the useful question is never "which do I trust in general" but "did this check actually execute the code". A local cache can hide a missing or undeclared dependency that only surfaces on a clean install — which is precisely why CI stays the authority whenever it runs. When it cannot run, the honest move is to verify locally and say loudly that you did, rather than to quietly redefine red as green.
