---
name: feedback-run-code-review
description: "After opening a PR in the autonomous loop, always run the /review skill on it"
metadata:
  type: feedback
---

After `gh pr create` succeeds, invoke the `review` skill (`/review`) on the freshly opened PR. Post the resulting review as a PR comment or use whatever output mode `/review` provides.

**Why:** Automated code review catches issues the Playwright UI gate can't — logic bugs, regressions, anti-patterns, security holes, missed edge cases. The cost is one extra step per tick; the upside is catching a class of bugs before a human reviewer has to.

**How to apply:**
- `/review` runs as one of the loop spec's step-10 gates — the canonical gate order (CI watch → `/review` → `rigorous` critique → security pass → QA agent → transition) lives in the loop spec, step 10. Do not re-derive the order here.
- Do this on **every** PR opened by the loop, not just complex ones — uniformity matters.
- If `/review` flags blocking issues, fix them before transitioning the tracker issue to "in review".

**Publish the gate's evidence, not just its conclusion.** When the gate produced any finding, render a single self-contained HTML page — dimensions reviewed, every finding with its file, line and quoted source, each verifier's verdict and reason, and the final QA and security verdicts — commit it into the PR branch under `docs/evidence/` ([[feedback-private-repo-screenshots]]), and link it from the PR body.

- Render it with one light-model agent from the gate's structured result, which the orchestrator already holds. No re-reading of the diff, no extra review pass. Skip it entirely when the gate found nothing: an empty dashboard is noise.
- **Why:** the gate's decision is otherwise unauditable. A reviewer who wants to know *why* a PR was blocked — or why a finding was refuted — currently has to trust a one-line verdict. The page also makes a hallucinating dimension visible at a glance: a column of findings refuted on citation ([[feedback-cost-conscious-gating]]) is a problem with the gate, not with the PR, and nobody will notice it in prose.
- Keep it plain: a table per dimension, verdicts colour-coded, no external assets (a strict CSP blocks CDN scripts, fonts, and remote images anyway).
