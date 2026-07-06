---
name: feedback-qa-agent-review
description: "Before moving an issue to review, a dedicated QA agent judges the work globally against requirements, design, and the full task context"
metadata:
  type: feedback
---

After the PR is open and the technical gates have passed, spawn a dedicated **QA agent** (Agent tool, general-purpose) whose only job is to judge the work **globally** — not the diff line-by-line, but: does this actually satisfy the tracker issue's requirements and acceptance criteria? Does it match the design? Is the form/UX coherent? Was anything in scope missed, or anything out of scope snuck in?

**Why:** The implementer's self-review inherits the implementer's blind spots. A separate agent reading the requirements fresh — with no memory of the implementation decisions — catches "correct code, wrong feature" mistakes that code review structurally cannot.

**How to apply:**
- The QA agent runs on the **routing profile's top model, at high effort** — never on the implementation's (possibly cheaper) tier; the judge outranks the worker ([[feedback-model-effort-routing]]).
- Feed the QA agent everything the task context offers: the full issue title/description/acceptance criteria plus its tracker comments, linked design references, the PR diff (`gh pr diff <num>`), the visual evidence captured for the PR, and the relevant CLAUDE.md conventions.
- Instruct it explicitly to: (a) restate the requirements as it understands them, (b) verify each one against the implementation, (c) check design fidelity and form/UX, (d) flag anything missing or extraneous, (e) audit the PR body's claims against the diff — the tests it says cover the change exist and assert the new behavior, and any "no UI surface" claim holds per the definition in [[feedback-playwright-testing]] — and (f) return a verdict: **pass** or **fail with reasons**.
- A fail verdict is a blocker: fix, then re-run the QA gate before transitioning the issue to the review status.
- Include a one-paragraph QA verdict summary in the tracker comment posted alongside the PR URL.
- Runs on every task, UI or not — for non-UI tasks the design-fidelity check simply drops out.
