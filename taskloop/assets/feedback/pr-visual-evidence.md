---
name: feedback-pr-visual-evidence
description: "PRs for UI changes must include screenshot(s) or short video of the change"
metadata:
  type: feedback
---

When the PR opened by the loop involves any UI/visual modification, attach screenshot(s) — or a short screen recording when motion/interaction matters — to the PR description. Before/after coverage is **mandatory** (see [[feedback-design-vs-implementation]]), plus every relevant state (e.g. partial / fully populated / error / empty combinations).

**Why:** Reviewers should see the visual outcome directly in the PR rather than running the branch locally. Visual evidence accelerates review and acts as a regression record. The Playwright captures from [[feedback-playwright-testing]] double as PR evidence, so the cost is near-zero.

**How to apply:**
- During the Playwright verification step, use `mcp__playwright__browser_take_screenshot` (or capture a video clip) for each relevant state.
- Commit the captures into the PR branch and reference them from the PR body/comments — the mechanism from [[feedback-private-repo-screenshots]] works for public repos too and is the only image-hosting path `gh` can drive (the CLI cannot upload to GitHub's attachment CDN; "pasting" is browser-only).
- Reference them in the PR body under a "Screenshots" / "Visual evidence" section.
- For private repos, host the images inside the PR branch rather than referencing `raw.githubusercontent.com` URLs — see [[feedback-private-repo-screenshots]].
