---
name: feedback-playwright-testing
description: "Every UI-affecting task must be verified with Playwright MCP before opening a PR"
metadata:
  type: feedback
---

After implementing any UI-affecting task, MUST verify the change end-to-end using the Playwright MCP browser tools (`mcp__playwright__browser_*`) before opening a PR or marking the task as done. Type-checks and unit tests don't prove the feature works in a real browser.

**Why:** The user insists on real browser verification. Static checks (tsc, eslint) and Jest unit tests routinely pass on changes that are broken end-to-end (selectors wrong, server contract drifted, state not wired up). Playwright is the gate that catches those classes of failure before a reviewer sees them.

**How to apply:**
- After code changes, spin up the relevant dev server (frontend port, Storybook, or the patched service) per the project's `CLAUDE.md`.
- Navigate with `mcp__playwright__browser_navigate`, exercise the golden path AND the edge cases for the changed feature.
- Capture a `mcp__playwright__browser_snapshot` and a `mcp__playwright__browser_take_screenshot` for every relevant state.
- Only then commit + push + open the PR.
- If the change has no UI surface (pure backend, infra, docs), state that explicitly in the PR body instead of skipping silently. Do not invent a fake UI check.
- The screenshots double as PR evidence per [[feedback-pr-visual-evidence]].
