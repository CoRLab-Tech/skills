---
name: feedback-trust-local-gates-not-remote-ci
description: "Finalize on the agent's LOCAL foreground gates (full test suite + typecheck + lint + build); do not wait on or re-run remote CI for PR branches — but `main` post-merge stays the non-negotiable backstop"
metadata:
  type: feedback
---

Where a project's remote CI costs money or throttles under parallelism, **if the LOCAL gates pass, do not verify or wait on the remote CI for a PR branch.** A burst of ~10 branch pushes can throttle a GitHub Actions org into 2-second failures with no log blob, while `main` and older branches stay green — a red that reflects the runner, not the code.

**How to apply:**

- The source of truth for "green" is the agent's FOREGROUND gates run in its worktree ([[feedback-gates-run-foreground]]): `typecheck` + `lint` + the FULL test suite ([[feedback-run-full-test-suite]]) + `build`. Every implementation and fix agent runs these before pushing and reports them.
- Finalize on: (a) the agent's reported local gates green, (b) the orchestrator's own diff inspection, and (c) for money / security / concurrency PRs, the adversarial gate ([[feedback-cost-conscious-gating]]). Do NOT add "remote CI green" as a finalize precondition.
- Do **not** poll remote CI before finalizing, and do **not** `gh run rerun` a failed remote CI — it burns Actions minutes for no benefit when the code is already verified locally. Ignore a red remote CI that is plainly throttling or infra (fast failures with no logs).
- In PR comments, write "local gates green (full test suite + typecheck + lint + build)" rather than "CI verify green", so a reader knows what was actually verified.
- This **supersedes** the remote-CI-watching part of [[feedback-regression-is-blocker]] and [[feedback-run-full-test-suite]] for the *finalize* decision on a PR branch. A genuine test failure the agent reports locally is still a hard blocker — the rule removes the dependency on the remote runner, not the dependency on green tests.

**Post-merge backstop on `main` — non-negotiable.** Branch-local gates run on the BRANCH, not on the merge result. With many PRs in flight, two individually-green branches can be red together (a semantic conflict, not a textual one). `main`'s CI runs once per merge and is not subject to the per-branch throttle — keep watching IT. After each merge or merge batch, check `main`'s CI result; if remote Actions is unavailable, run the full suite locally on fresh `origin/main` instead. A red `main` is a drop-everything blocker per [[feedback-regression-is-blocker]] — this rule never applied to `main`, only to PR branches.

Local caches can also mask a missing or undeclared dependency that only fails on a clean install. If `main`'s CI goes red on install or lockfile while local is green, trust the CI on that one and fix the manifest.

**Why:** the remote CI is a cost and a throttling bottleneck under high parallelism, while the local foreground gates already run the identical commands the CI workflow runs. Depending on the remote runner buys nothing on a PR branch and burns money re-running throttled jobs — but dropping `main`'s post-merge check would trade a real safety net for nothing.

**Adopt this only when it is true for the project.** On a project with cheap, reliable CI, keep watching PR CI to completion per [[feedback-regression-is-blocker]]. The rule ships enabled because the failure it prevents (an autonomous loop wedged on a throttled runner) is expensive; flip it off in the project's memory dir if the tradeoff does not hold.
