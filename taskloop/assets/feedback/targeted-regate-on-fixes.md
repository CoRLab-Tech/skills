---
name: feedback-targeted-regate-on-fixes
description: "A PR's FIRST gate run is always full; fix rounds re-run only the gates that blocked, scoped to the fix delta — but the QA + security verdicts always re-judge the FULL diff on the top model"
metadata:
  type: feedback
---

A PR's **first** gate run is always the full suite of mandated gates — full local tests, code review, rigorous critique, QA agent, security pass. A **fix round** (addressing blocking findings or requested changes on the same PR) does not mechanically re-run everything from scratch: most of that spend re-reads a large unchanged diff to re-confirm findings that already passed.

**How a fix round re-gates:**
- **Full test suite: always.** Compute is not the expensive part — a fix that breaks a distant test must be caught here ([[feedback-run-full-test-suite]]).
- **Review-type gates: only the ones that blocked.** Re-run just the gate(s)/dimension(s) whose findings caused the fix, and scope their re-read to the fix delta (the changed hunks + immediate context), not the full diff again.
- **QA + security verdicts: always, on the FULL current diff, on the profile's top model** ([[feedback-qa-agent-review]], [[feedback-security-review-gate]], [[feedback-model-effort-routing]]). This is the non-negotiable safety net for cross-cutting regressions in the dimensions the targeted re-review skipped — the cheap part is the re-reading, never the judging.
- **Escalation guard:** before going targeted, compare the fix delta against the blocking findings' files. If the fix touches files OUTSIDE that footprint (beyond trivial lockfile/snapshot churn), the "fix stayed inside the findings" premise is false — run the full gate suite instead.
- A fix round that itself produces new blocking findings restarts this cycle; repeated non-convergence exits via [[feedback-fail-gracefully-timebox]], never via thinner gates.

**Why:** measured on a production loop (2026-07-08): PRs went through 3–4 FULL re-gate rounds each, every round re-reading a 100KB+ diff across all review dimensions when the fix touched one. Going targeted cut ~40–50% of fix-round token cost with ~zero catch-rate loss — because the full-diff top-model verdicts were kept, and they were what caught the cross-cutting bugs. The corollary is equally firm: NEVER thin a PR's first gate — the full first pass is what caught ~30 real CI-invisible bugs in the same run.
