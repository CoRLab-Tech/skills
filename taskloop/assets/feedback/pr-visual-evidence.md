---
name: feedback-pr-visual-evidence
description: "UI-affecting PRs carry mandatory before/after screenshots — and design vs implementation side-by-side when a design exists — plus every relevant state"
metadata:
  type: feedback
---

If a change touches the UI — or **could plausibly induce** a visual change (shared components, global CSS, theme tokens, layout containers) — the PR description MUST include **before / after** screenshots. Not optional. When the task stems from a design (Figma link, mockup, or image attachment on the tracker issue), the PR must additionally show **design vs implementation**: the design frame next to the implemented screen, same state, same viewport. Cover every relevant state (partial / fully populated / error / empty), with a short screen recording when motion or interaction matters.

**Why:** reviewers should see the visual outcome directly in the PR rather than running the branch locally. Before/after turns a visual diff into a five-second review; design-vs-implementation makes fidelity measurable instead of vibes-based. And if the "before" capture is hard to produce, that itself signals the change has a wider blast radius than assumed.

**How to apply:**
- **BEFORE implementing**, capture the "before" state of the affected screens with Playwright MCP — the branch is freshly cut from main, so the pre-change UI is one navigation away. Do it first; it cannot be reconstructed after the change.
- After implementing, capture the same screens/states as "after": same viewport, same data where possible. Present as a `| Before | After |` table in the PR body; the Playwright captures from [[feedback-playwright-testing]] double as this evidence, so the cost is near-zero.
- When the tracker issue links a design, export/screenshot the design frame and place it side-by-side: `| Design | Implementation |`, matching state and viewport.
- Applies also to changes that only *might* affect UI (shared component, CSS refactor): capture the key consumers before/after to prove no unintended change.
- Commit the captures into the PR branch and reference them from the PR body/comments — the mechanism from [[feedback-private-repo-screenshots]] works for public repos too and is the only image-hosting path `gh` can drive (the CLI cannot upload to GitHub's attachment CDN; "pasting" is browser-only).
