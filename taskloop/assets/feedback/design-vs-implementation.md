---
name: feedback-design-vs-implementation
description: "UI-affecting PRs must show before/after screenshots; design-driven tasks must show design vs implementation side-by-side"
metadata:
  type: feedback
---

If a change touches the UI — or **could plausibly induce** a visual change (shared components, global CSS, theme tokens, layout containers) — the PR description MUST include **before / after** screenshots. Not optional. When the task stems from a design (Figma link, mockup, or image attachment on the tracker issue), the PR must additionally show **design vs implementation**: the design frame next to the implemented screen, same state, same viewport.

**Why:** Before/after turns a visual diff into a five-second review; design-vs-implementation makes fidelity measurable instead of vibes-based. And if the "before" capture is hard to produce, that itself signals the change has a wider blast radius than assumed.

**How to apply:**
- BEFORE implementing, capture the "before" state of the affected screens with Playwright MCP — the branch is freshly cut from main, so the pre-change UI is one navigation away. Do it first; it cannot be reconstructed after the change.
- After implementing, capture the same screens/states as "after": same viewport, same data where possible. Present as a `| Before | After |` table in the PR body.
- When the tracker issue links a design, export/screenshot the design frame and place it side-by-side with the implementation capture: `| Design | Implementation |`, matching state and viewport.
- Applies also to changes that only *might* affect UI (shared component, CSS refactor): capture the key consumers before/after to prove no unintended change.
- Host images per [[feedback-private-repo-screenshots]]. This rule sharpens [[feedback-pr-visual-evidence]] from "cover before/after if possible" to mandatory.
