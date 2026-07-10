---
name: feedback-pr-gate-passes
description: "The four review passes every loop PR goes through — /review, rigorous critique, security, and a QA agent judging globally — their order, what each one is for, and the blocking semantics they share"
metadata:
  type: feedback
---

Every PR the loop opens passes through four review lenses before its issue transitions to review. They hunt different things and overlap little; running one is not running the others.

**The order** (the loop spec's step-10 gate sequence): CI watch → `/review` → `rigorous` critique → security pass → QA agent → transition. Do not re-derive it elsewhere.

**The blocking semantics, stated once for all four.** A blocking finding from any pass is treated exactly like a failing test: fix it on the PR branch, push, re-run the affected gate ([[feedback-targeted-regate-on-fixes]]), and only then transition. The PR stays a draft throughout ([[feedback-draft-until-gated]]). Non-blocking observations are noted in the PR body rather than fixed. A pass whose tool is unavailable in the session is skipped **silently and explicitly** — say so in the PR body; never fake it, and never let its absence silently drop a lens.

**How many of the four run, and how deep, scales with the PR's risk** — see [[feedback-cost-conscious-gating]] and the profile in force ([[feedback-loop-strategy-profiles]]). A mechanical rename does not earn a four-lens gate. A money-movement diff earns all four at full depth.

## 1. `/review` — correctness in the diff

Invoke the `review` skill on the freshly opened PR. It hunts logic bugs, regressions, anti-patterns, missed edge cases — the classes a UI check and a type-checker structurally cannot see. Run it on **every** PR, not just the ones that feel risky: uniformity is what makes the gate's absence meaningful.

## 2. `rigorous` — design at a different altitude

When the `rigorous` skill is available, run its critique mode against the PR's diff and context. Where `/review` reads the diff for defects, `rigorous` reads it for architecture fit, error handling, edge cases, test strategy, and simplification. The two overlap little.

Post the distilled critique — actionable findings only, never the full transcript — as a PR comment, so the human reviewer sees what was already checked and fixed.

## 3. Security — exploitability

Run the `security-review` skill against the branch's pending changes. When it is unavailable, review the diff manually for at minimum: injection (SQL / shell / template); authorization on every new or changed endpoint, **object-level and not merely authenticated**; secrets or internal hostnames in code or logs; SSRF on user-supplied URLs; path traversal on user-supplied paths; unsafe deserialization; XSS on rendered user input; missing rate limits on unauthenticated endpoints; and new or changed dependencies — exact package name checked against the official docs (typosquats), advisory/audit result, lockfile churn limited to the new package's closure ([[feedback-dependency-hygiene]]).

Diffs touching auth, permissions, file upload or download, payment, or user-input parsing get the deepest look. Those are never "too small to bother". Record in the PR body that a security pass ran and what it covered.

**Why a separate lens:** `/review` and `rigorous` hunt correctness and design; neither is tuned for exploitability. Autonomous code shipped without a security lens is how injection points, broken authorization, and leaked internal URLs reach production with nobody having ever looked.

## 4. QA agent — did we build the right thing

After the technical gates pass, spawn a dedicated QA agent whose only job is to judge the work **globally** — not the diff line by line, but: does this satisfy the issue's requirements and acceptance criteria? Does it match the design? Was anything in scope missed, or anything out of scope snuck in?

- It runs on the routing profile's **top model at high effort** — never on the implementation's cheaper tier. The judge outranks the worker ([[feedback-model-effort-routing]]).
- Feed it everything: the issue's title, description, acceptance criteria and comments; linked designs; `gh pr diff <num>`; the visual evidence ([[feedback-ui-verification-and-evidence]]); the relevant `CLAUDE.md` conventions; and the accumulated project lessons ([[feedback-continuous-learning]]).
- Instruct it to (a) restate the requirements as it understands them, (b) verify each against the implementation, (c) check design fidelity and UX coherence, (d) flag anything missing or extraneous, (e) **audit the PR body's claims against the diff** — the tests it says cover the change exist and assert the new behavior, and any "no UI surface" claim holds by the definition in [[feedback-ui-verification-and-evidence]] — and (f) return `pass`, or `fail` with reasons.
- A `fail` is a blocker. Include a one-paragraph QA verdict in the tracker comment posted alongside the PR link.

**Why:** the implementer's self-review inherits the implementer's blind spots. A separate agent reading the requirements fresh, with no memory of the implementation decisions, catches "correct code, wrong feature" — which code review structurally cannot.

## Publish the gate's evidence, not just its conclusion

When the gate produced any finding, render a single self-contained HTML page — dimensions reviewed, every finding with its file, line and quoted source, each verifier's verdict and reason, the final QA and security verdicts — commit it into the PR branch under the project's evidence directory (set at init, default `docs/evidence`), and link it from the PR body.

Render it with one light-model agent from the gate's structured result, which the orchestrator already holds: no re-reading of the diff, no extra review pass. Skip it entirely when the gate found nothing — an empty dashboard is noise.

**Why:** the gate's decision is otherwise unauditable. A reviewer who wants to know *why* a PR was blocked, or why a finding was refuted, has only a one-line verdict to trust. The page also makes a hallucinating dimension visible at a glance: a column of findings refuted on citation ([[feedback-cost-conscious-gating]]) is a problem with the gate, not with the PR, and nobody will spot it in prose.
