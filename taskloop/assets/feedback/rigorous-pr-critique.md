---
name: feedback-rigorous-pr-critique
description: "Besides /review, when the rigorous skill is available run its critique on every PR the loop opens"
metadata:
  type: feedback
---

The standard `/review` pass ([[feedback-run-code-review]]) is mandatory but not sufficient. When the `rigorous` skill is available in the session, additionally run its critique/review mode against **every** PR the loop opens. Both gates must pass before the issue transitions to the review status.

**Why:** `/review` hunts correctness bugs in the diff; `rigorous` critiques from a different altitude — design and architecture fit, error handling, edge cases, test strategy, simplification. The two overlap little; running both catches classes of problems either alone would miss.

**How to apply:**
- Sequence after `gh pr create`: run `/review` first, then invoke the `rigorous` skill (via the Skill tool) in its review/critique mode against the PR's diff and context.
- Treat blocking findings from either gate exactly like failing tests: fix on the PR branch, push, and re-run the gate before transitioning the tracker issue.
- Post the distilled critique (actionable findings only, not the full transcript) as a PR comment, so the human reviewer sees what was already checked and fixed.
- If `rigorous` is not available in the session, skip silently — `/review` alone then satisfies [[feedback-run-code-review]].
- Uniformity matters: every PR, not just the ones that feel risky.
