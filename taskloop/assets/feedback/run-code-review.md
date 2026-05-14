---
name: feedback-run-code-review
description: "After opening a PR in the autonomous loop, always run the /review skill on it"
metadata:
  type: feedback
---

After `gh pr create` succeeds, invoke the `review` skill (`/review`) on the freshly opened PR. Post the resulting review as a PR comment or use whatever output mode `/review` provides.

**Why:** Automated code review catches issues the Playwright UI gate can't — logic bugs, regressions, anti-patterns, security holes, missed edge cases. The cost is one extra step per tick; the upside is catching a class of bugs before a human reviewer has to.

**How to apply:**
- Sequence per tick: implement → Playwright verify → run full tests → commit → push → `gh pr create` → invoke the `review` skill (via the Skill tool) against the new PR URL/number → transition the tracker issue to the review status → comment on the issue with PR URL + review summary.
- Do this on **every** PR opened by the loop, not just complex ones — uniformity matters.
- If `/review` flags blocking issues, fix them before transitioning the tracker issue to "in review".
