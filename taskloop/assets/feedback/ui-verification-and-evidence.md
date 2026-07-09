---
name: feedback-ui-verification-and-evidence
description: "UI-affecting changes are driven in a real browser before the PR, and the captures become the PR's before/after evidence — hosted inside the PR branch so they render on private repos"
metadata:
  type: feedback
---

A UI-affecting change is verified in a **real browser** before the PR opens, and the captures taken during that verification become the PR's visual evidence. Verification and evidence are one activity, not two: the screenshots cost nothing extra because you had to drive the screen anyway.

**"No UI surface" is a defined claim, not a vibe.** It holds ONLY when the diff touches no frontend paths AND changes no API response shape, event payload, or config value that any UI consumes. A backend change that alters JSON a screen renders **has** a UI surface — drive the consuming screen. When the claim genuinely holds, state it explicitly in the PR body rather than skipping silently; the QA agent verifies the claim against the diff ([[feedback-pr-gate-passes]]). Never invent a fake UI check.

## Drive it

- Spin up the relevant dev server, Storybook, or patched service per the project's `CLAUDE.md`.
- **Capture the "before" state FIRST**, prior to implementing. The branch is freshly cut from `main`, so the pre-change UI is one navigation away — and it cannot be reconstructed afterwards.
- Exercise the golden path **and** the edge cases for the changed feature. Cover every relevant state: partial, fully populated, error, empty. Add a short screen recording when motion or interaction carries the meaning.
- Capture a snapshot and a screenshot for every relevant state, then implement, then capture the same screens as "after" — same viewport, same data where possible.
- The main loop's single-threaded verification uses the Playwright MCP browser. **Parallel implementation agents must not**: that browser is one global instance with a shared active tab and cookie jar, so concurrent agents navigate each other's tabs and cross-contaminate auth. Each parallel agent drives its own isolated headless browser ([[feedback-isolated-browsers-parallel-agents]]).

**Why drive it at all:** type-checks and unit tests routinely pass on changes that are broken end to end — wrong selector, drifted server contract, state never wired up. The browser is the only gate that catches that class.

## Present it

- Put the captures in the PR body as a `| Before | After |` table. When the task stems from a design (a Figma link, a mockup, an image on the ticket), add a `| Design | Implementation |` table too: same state, same viewport.
- Applies to changes that only *might* affect the UI — a shared component, a CSS refactor, a theme token. Capture the key consumers before and after to prove nothing moved.
- If the "before" capture is hard to produce, that is itself the signal: the change has a wider blast radius than assumed.

**Why before/after:** it turns a visual diff into a five-second review. Design-vs-implementation makes fidelity measurable instead of vibes-based.

## Host it inside the PR branch

`raw.githubusercontent.com` URLs require auth and render as **broken images** on private repos. Commit the captures into the PR branch instead — the GitHub web UI then renders them through the reviewer's own session.

- Commit under `docs/pr-evidence/<issue-key>/` (or `.pr-screenshots/<issue-key>/`).
- Reference each with **image syntax — the `!` is mandatory.** A plain `[label](url)` renders as a text link, not an image:

  ```markdown
  ![short alt text](https://github.com/<owner>/<repo>/raw/<branch>/docs/pr-evidence/<issue-key>/<file>.png)
  ```

  The `/raw/<branch>/` form (equivalently `/blob/<branch>/<file>.png?raw=true`) redirects through the reviewer's session. Both work; pick one and stay consistent.
- **Verify the embed rendered.** After `gh pr edit`, run `gh pr view <n> --json body -q .body | grep -c '!\['` and confirm the count matches the number of captures. A `0` means you shipped links, not images.
- This is the only image-hosting path `gh` can drive: the CLI cannot upload to GitHub's attachment CDN — "pasting" is browser-only. It works for public repos too, so use it everywhere.
- **Lifecycle, deterministic and with no cleanup step:** the folder ships with the merge as the change's visual record. Keep it small — a handful of compressed PNGs per issue, no videos (link a comment attachment for those). It is an explicit, intentional exemption from [[feedback-minimal-diff-scope]]. Never add a "remove before merge" note that no step executes, and never push cleanup commits after the gates have gone green.
- Do not use a separate `assets/<slug>-screenshots` branch: it adds cleanup overhead and its URLs do not render anyway.
