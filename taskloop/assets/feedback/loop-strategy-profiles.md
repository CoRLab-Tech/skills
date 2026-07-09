---
name: feedback-loop-strategy-profiles
description: "Four switchable loop strategies — auto / fast / balanced / heavy — selected via LOOP_STRATEGY in the loop .env (default auto); the profile sets model routing, gate rigor, re-gate depth, and WIP for every spawn the loop authors that tick"
metadata:
  type: feedback
---

The loop's rigor is a **switchable strategy**, so the owner can trade thoroughness for speed on demand. Named profiles, not a continuous knob — points an owner can reason about beat a slider nobody can calibrate mid-race.

`auto` is the DEFAULT: it starts every ticket at the cheapest rigor that can honestly do the job and **ratchets up on evidence** (see below). The three fixed profiles it selects among are `fast` (ship quickly, rails only), `balanced` (risk-scaled rigor per [[feedback-cost-conscious-gating]]), and `heavy` (maximal rigor, every check on every PR). Pin one of the three when you want a constant regime rather than an adaptive one.

## The switch

- **`LOOP_STRATEGY` in the loop `.env`** (`auto` | `fast` | `balanced` | `heavy`), default `auto`. The loop reads it at the TOP of every tick and applies the matrix below to every spawn and gate it authors that tick.
- **The owner switches two ways:** edit `LOOP_STRATEGY` in `.env`, or just say "switch to auto/fast/balanced/heavy" — the loop updates the var AND, for agents already in flight, `SendMessage`s each one to apply the new profile to its REMAINING steps (the live-steer mechanic from [[feedback-cost-conscious-gating]]). A switch never rewrites work already gated.
- **Per-ticket override:** a ticket's `LOOP-PLAN` marker ([[feedback-queue-triage-plan]]) may carry `strategy:<fast|balanced|heavy>` to override the global default for that one ticket — global `fast` but this one PR forced `heavy`. Absent → the global `LOOP_STRATEGY`. An explicit per-ticket override also **pins** that ticket: `auto` will still ratchet it upward on evidence, but never below the pinned rung.

## `auto` — the minimum sufficient rigor, ratcheted by evidence

`auto` is not a fifth column in the matrix. It is a **policy for choosing** among `fast` / `balanced` / `heavy`, **per ticket**, and revising that choice as evidence arrives. The principle: *spend the least that can honestly do this task, and let being wrong be the thing that buys more spend.*

**Step 1 — entry rung, decided once when the ticket is pulled.** The floor is `fast`; complexity and risk are what lift it. Classify from the ticket, its diff footprint in the plan, and the files it will touch:

| Signal | Entry rung |
|---|---|
| Default — no signal below fires | `fast` |
| Touches a money-movement, auth/security, concurrency, or idempotency surface | `balanced` |
| Money *math*, a saga or concurrency core, an auth surface, or a new external adapter | `heavy` |
| A new service skeleton, or a public contract change | `balanced` |
| Cross-cutting: touches ≥ 3 services, or a shared component / global CSS / theme token | `balanced` |
| Mirrors an already-merged sibling pattern | `fast` — the architecture decision is already made ([[feedback-cost-conscious-gating]]) |

When two signals fire, take the higher rung. When genuinely ambiguous, route up — an unnecessary `balanced` gate is cheap next to a missed money bug.

**Step 2 — the ratchet. Any of these escalates the ticket ONE rung, immediately and stickily:**

- The QA or security verdict returns `fail` — the ticket bounces from review back to In Progress.
- A gate finding is CONFIRMED blocking.
- A human review comment asks for a change ([[feedback-watch-pr-comments]]).
- An honest implementation attempt fails and the agent retries.
- `main` goes red post-merge and the bisect points at this PR ([[feedback-trust-local-gates-not-remote-ci]]).

`fast → balanced → heavy`, and `heavy` is the ceiling. **The ratchet only ever turns up.** A ticket that reached `heavy` stays `heavy` for every remaining round, including its fix re-gates — the whole point is that a ticket which already fooled one gate has earned the stronger one. The rung resets only when the PR merges.

**Why a ratchet and not a re-classification.** A bounce is evidence the entry classification was wrong, and the cheapest correct response to "my risk model underestimated this ticket" is to stop trusting it for this ticket. De-escalating after a passing round would let a ticket oscillate: pass at `fast`, drop rigor, regress, bounce again. Monotonic escalation converges; a two-way knob does not.

**Bookkeeping — the ratchet must be visible, or it silently resets.** On every escalation:

1. Write the new rung into the ticket's `LOOP-PLAN` marker as `strategy:<rung>` so a later tick (or a fresh session, or a different agent) reads the escalated rung and not the entry one.
2. Note the trigger in the ticket comment that already accompanies the bounce ([[feedback-status-mirrors-work]]): "QA verdict failed → escalated to `balanced`."
3. Append a row to `model-usage-log.md` with the rung and its trigger — this is the telemetry that shows whether the entry classifier is calibrated. If most tickets ratchet on their first bounce, the entry table is too optimistic and belongs one rung higher.

**`auto` re-gates through [[feedback-targeted-regate-on-fixes]] like any other profile** — but at the escalated rung. A ticket that bounced into `heavy` gets `heavy`'s full re-gate, not the targeted one.

## The matrix

Model names below are tiers, not ids: `top` / `deep` / `balanced` / `light` resolve through the project's `feedback/model-routing-profile.md`. `auto` selects one of these three columns per ticket; it never blends them.

| Dimension | **fast** | **balanced** (default) | **heavy** |
|---|---|---|---|
| Implementation routing | light for trivial; **balanced-medium for everything standard and deep**; top ONLY for the orchestrator and genuinely novel architecture | the four-tier ladder ([[feedback-model-effort-routing]]) with **aggressive right-sizing** ([[feedback-token-hygiene]]): light maximized wherever it qualifies, balanced for all standard work, top ONLY when genuinely fitting; route up on doubt, escalate on failure | bias UP: **deep is the default** for any real work; standard → balanced at high effort; top for anything non-trivial |
| Effort | low–medium | balanced-medium default; high on money/security or after a failed attempt | high–xhigh across the board |
| First gate (per PR) | **tests + typecheck + lint + secret scan + ONE review pass**, finalize on green. No finder panel, no adversarial verify, no top-model verdict | **risk-scaled** ([[feedback-cost-conscious-gating]]): money/security/concurrency = 5 dimensions + 3× adversarial verify; standard = 3 dimensions + 1 verifier; review and verify on the balanced model at high effort; QA + security verdicts on the top model (`xhigh` only for money/auth/concurrency); mechanical PRs get the light gate | **FULL 5-dimension + 3× adversarial verify on EVERY PR**, not risk-scaled; review and verify may run on the top model; QA + security verdicts `xhigh` ALWAYS |
| Fix re-gate | tests green + eyeball the delta, no re-gate | **targeted** ([[feedback-targeted-regate-on-fixes]]): affected dimensions + hunk-scoped verify + full-diff top-model verdicts; full on the first round or an escalation-guard trip | **FULL re-gate every fix round** |
| Runtime verify | browser check only if UI, single screenshot | browser verification required for UI changes, evidence on the PR ([[feedback-playwright-testing]], [[feedback-pr-visual-evidence]]) | exhaustive: browser + e2e + design-vs-implementation + QA-agent global review, every applicable PR |
| Extra critique passes | none | `/review` + `rigorous` on every PR ([[feedback-run-code-review]], [[feedback-rigorous-pr-critique]]); QA agent and security gate by risk | ALL passes on EVERY PR: `/review` + `rigorous` + `security-review` + QA-agent global + design-vs-implementation |
| WIP | refill aggressively, at or above the project's cap | the project's configured cap ([[feedback-wip-limit-open-prs]]) | roughly half the cap — depth over throughput, fewer concurrent agents to avoid session-limit thrash |
| Best for | prototypes, spikes, internal tooling, mechanical PRs, non-critical services, racing a deadline with owner-accepted risk | mixed codebases where most PRs carry real risk | money movement, auth/security, concurrency cores, release-critical PRs, "must not be wrong" |
| `auto` picks it when | no risk signal fires and the ticket has not bounced | a risk signal fires, or the ticket bounced once | a money/auth/concurrency core, or the ticket bounced twice |

## Rails that hold in EVERY profile — fast included, non-negotiable

1. **Secret scan on every staged diff** ([[feedback-no-secrets-in-code]]) — never cut, cheap.
2. **Green tests + typecheck + lint + build before finalize** ([[feedback-trust-local-gates-not-remote-ci]]) — never ship red, in any profile.
3. **No AI attribution; PR evidence for UI; PR link on the ticket; tracker state mirrors reality on merge** — process rails, profile-independent.

**Pinned `fast` is PURE: no escalation of any kind.** When the owner sets `LOOP_STRATEGY=fast` explicitly, money-movement, auth, concurrency, and idempotency PRs run fast's reduced gate too — the owner owns that risk by choosing the profile. The only lift is a manual per-ticket `strategy:` override. Rails 1–3 still hold: "pure" drops the *gate rigor*, not those three.

**This is exactly what `auto` changes.** `auto` also *starts* at `fast`, but it is not pure: it lifts the risky classes to `balanced` or `heavy` up front, and it ratchets on evidence. Choose pinned `fast` when you want speed and accept the risk; choose `auto` when you want speed *except* where the code says otherwise. `auto` is the default because on most codebases the risky classes are a small minority of tickets, so it buys `fast`'s wall-clock on the majority while never letting a money path through a light gate.

**Why:** the all-checks regime (`heavy`) catches CI-invisible bugs but costs ~0.6–1.5M tokens per PR and hits session limits. `balanced` holds essentially that catch rate at a fraction of the cost by scaling rigor to risk. `fast` trades the adversarial safety net for wall-clock where a wrong PASS is cheap to reverse. `auto` makes that trade per ticket instead of per project, and treats a QA bounce as proof it traded wrong.

**How to apply:** read `LOOP_STRATEGY` at the top of every tick. Under `auto`, resolve each ticket's rung — entry classification, then any `strategy:` already ratcheted into its `LOOP-PLAN` marker, whichever is higher — before spawning, and pass that rung's model, effort, and gate shape into every `agent()` call for that ticket. When the owner switches mid-run, steer in-flight agents rather than waiting for the next spawn. See [[feedback-efficiency-levers]] for what is safe to trim beyond this and what is the hard floor.
