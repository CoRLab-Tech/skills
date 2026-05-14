---
name: feedback-pr-visual-evidence
description: "PRs for UI changes must include screenshot(s) or short video of the change"
metadata:
  type: feedback
---

When the PR opened by the loop involves any UI/visual modification, attach screenshot(s) — or a short screen recording when motion/interaction matters — to the PR description. Cover the before/after if possible, and every relevant state (e.g. partial / fully populated / error / empty combinations).

**Why:** Reviewers should see the visual outcome directly in the PR rather than running the branch locally. Visual evidence accelerates review and acts as a regression record. The Playwright captures from [[feedback-playwright-testing]] double as PR evidence, so the cost is near-zero.

**How to apply:**
- During the Playwright verification step, use `mcp__playwright__browser_take_screenshot` (or capture a video clip) for each relevant state.
- Upload them as GitHub PR attachments — either paste images into the PR body via `gh pr create --body` referencing the uploaded asset, or post them as a comment immediately after `gh pr create`.
- Reference them in the PR body under a "Screenshots" / "Visual evidence" section.
- For private repos, host the images inside the PR branch rather than referencing `raw.githubusercontent.com` URLs — see [[feedback-private-repo-screenshots]].
