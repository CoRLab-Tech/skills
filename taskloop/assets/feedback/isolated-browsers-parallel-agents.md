---
name: feedback-isolated-browsers-parallel-agents
description: "Parallel agents must NOT share the Playwright/Chrome MCP browser — it is one global instance; each parallel agent verifies with its own isolated headless browser"
metadata:
  type: feedback
---

The Playwright MCP / Chrome MCP browser is **one shared instance with global state** — one active tab, one cookie jar. When parallel implementation agents all drive it, they navigate each other's tabs mid-screenshot and share localhost cookies across ports; evidence captured through a shared browser during a parallel wave is unreliable and can silently corrupt another agent's session.

**Why:** learned from a parallel wave where agents overwrote each other's tabs and one agent found — and had to restore — another agent's auth cookie. The screenshots looked plausible; they were of the wrong agent's state.

**How to apply:**
- Implementation agents running **in parallel** ([[feedback-parallel-disjoint-tasks]]) capture browser evidence with an ISOLATED browser only: headless Chrome CLI (`chrome --headless --screenshot=<path> --window-size=<w,h> <url>`) or a small scratchpad Node/CDP driver on a dedicated debugging port per agent. Unique dev-server ports per agent stay mandatory either way.
- The shared Playwright/Chrome MCP browser is reserved for the **main loop's own single-threaded verification** ([[feedback-playwright-testing]]) — when exactly one actor is browsing, MCP is the right tool.
- The isolation requirement goes INTO each parallel agent's prompt, next to the unique-port assignment — an agent cannot be expected to discover the browser is shared.
- Evidence standards are unchanged: same golden-path + edge-case coverage, same screenshots committed in-branch ([[feedback-pr-visual-evidence]]) — only the instrument differs.
