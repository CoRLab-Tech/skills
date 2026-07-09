---
name: feedback-loop-strategy-profiles
description: "Four switchable loop strategies — auto / fast / balanced / heavy — selected via LOOP_STRATEGY in the loop .env (default auto); the profile sets model routing, gate rigor, re-gate depth, and WIP for every spawn the loop authors that tick"
metadata:
  type: feedback
---

The loop's rigor is a **switchable strategy**, so the owner can trade thoroughness for speed on demand. Named profiles, not a continuous knob — points an owner can reason about beat a slider nobody can calibrate mid-race.

`auto` is the DEFAULT: it gives every ticket **the rung its complexity asks for**, and revises that judgment only when QA reveals the ticket is not what it looked like (see below). The three fixed profiles it selects among are `fast` (ship quickly, rails only), `balanced` (risk-scaled rigor per [[feedback-cost-conscious-gating]]), and `heavy` (maximal rigor, every check on every PR). Pin one of the three when you want a constant regime rather than an adaptive one.

## The switch

- **`LOOP_STRATEGY` in the loop `.env`** (`auto` | `fast` | `balanced` | `heavy`), default `auto`. The loop reads it at the TOP of every tick and applies the matrix below to every spawn and gate it authors that tick.
- **The owner switches two ways:** edit `LOOP_STRATEGY` in `.env`, or just say "switch to auto/fast/balanced/heavy" — the loop updates the var AND, for agents already in flight, `SendMessage`s each one to apply the new profile to its REMAINING steps (the live-steer mechanic from [[feedback-cost-conscious-gating]]). A switch never rewrites work already gated.
- **Per-ticket override:** a ticket's `LOOP-PLAN` marker ([[feedback-queue-triage-plan]]) may carry `strategy:<fast|balanced|heavy>` to override the global default for that one ticket — global `fast` but this one PR forced `heavy`. Absent → the global `LOOP_STRATEGY`. An explicit per-ticket override also **pins** that ticket: `auto` will still ratchet it upward on evidence, but never below the pinned rung.

## `auto` — the rung that the ticket's complexity asks for

`auto` is not a fifth column in the matrix. It is a **policy for choosing** among `fast` / `balanced` / `heavy`, **per ticket**, from the ticket's assessed complexity and risk. The principle: *spend what this task actually demands — no more, and no less.*

**`auto` does not count failures.** A bounce is not a coin dropped into a machine that buys one more rung. The rung is always a function of what the ticket **is**, never of how many times it has failed. A bounce matters only when it *teaches you something new about what the ticket is* — and then the rung moves to whatever that new understanding demands, which may be one step, two steps, or none at all.

**Step 1 — classify when the ticket is pulled.** The floor is `fast`; complexity and risk are what lift it. Classify from the ticket, its diff footprint in the plan, and the files it will touch:

| Signal | Entry rung |
|---|---|
| Default — no signal below fires | `fast` |
| Touches a money-movement, auth/security, concurrency, or idempotency surface | `balanced` |
| Money *math*, a saga or concurrency core, an auth surface, or a new external adapter | `heavy` |
| A new service skeleton, or a public contract change | `balanced` |
| Cross-cutting: touches ≥ 3 services, or a shared component / global CSS / theme token | `balanced` |
| Mirrors an already-merged sibling pattern | `fast` — the architecture decision is already made ([[feedback-cost-conscious-gating]]) |

When two signals fire, take the higher rung. When genuinely ambiguous, route up — an unnecessary `balanced` gate is cheap next to a missed money bug.

**Step 2 — re-classify when QA hands back new information about the ticket.** A QA `fail`, a confirmed blocking finding, a human change request, a failed attempt, or a red `main` traced to this PR is a **prompt to re-run Step 1 with what you now know** — not an escalation in itself. Ask one question: *does this evidence change what the ticket is?*

**It changes the classification when the defect reveals a surface or a structure the entry classification did not know about.** Then the rung jumps straight to whatever Step 1 assigns to that surface — `fast` → `heavy` in one move if that is what the table says:

| What QA revealed | New rung |
|---|---|
| The confirmed defect is a concurrency, idempotency, auth, cross-tenant, or money-math bug | whatever Step 1 gives that surface — usually `heavy` |
| The fix must touch files outside the ticket's planned footprint | at least `balanced` — the ticket is cross-cutting after all |
| The regression landed in a dimension the review did not cover | `balanced` |
| The acceptance criterion was missed because the domain was misunderstood | `balanced` |
| The ticket turns out to depend on a contract or schema it was not supposed to change | `balanced` |

**It does NOT change the classification when the defect sits entirely inside the complexity you already understood.** A typo, a missing test, a forgotten log line, a naming nit, an off-by-one in code whose shape was never in doubt — these say the *implementation* was sloppy, not that the *ticket* is harder than you thought. The rung stays exactly where it was, and the fix re-gates at that rung. Buying a `heavy` gate because someone forgot a null check is how `auto` would quietly become `heavy` for everything.

**One safety valve, and it is not a counter either.** If a ticket fails **twice at the same rung** and neither failure reclassified it, that pattern is itself the new information: the rung is wrong, whatever the table said. Move it up one and record why. Two independent misses at a rigor level are evidence about the rigor level.

**The rung never drops while the ticket is open.** A re-classification that finds *less* complexity late in a ticket is almost always an artifact of the work already being done — the hard part is behind you, so the ticket looks easy. Lowering there would drop the gate exactly when the diff is largest. `heavy` is the ceiling; the rung resets only when the PR merges.

## The limits of `auto` — what may move the rung, and what may never

These are hard bounds. A rung change that cannot point at one of them is invalid and must be reverted.

**Range.** The rung is exactly one of `fast` | `balanced` | `heavy`. `fast` is the floor, `heavy` the ceiling. There is nothing below and nothing above.

**The only inputs.** The entry rung comes from the Step 1 signal table and nothing else. The rung then moves only for a signal named in the Step 2 table, or by the two-misses valve. That is the closed list.

**The forbidden reasons — none of these may move the rung, ever:**

- how many times the ticket has failed (that is a counter, not a classification);
- how many review comments it collected;
- the size of the diff in lines, or the number of files touched *within* the planned footprint;
- how long the ticket has taken, or how many tokens it has burned;
- an agent's impression that the work "feels hard", absent a named surface from the table;
- what rung the *previous* ticket ran at;
- the owner being impatient, or the queue being deep.

**One move per gate round.** A single round may reclassify a ticket at most once, however many findings it produced. Two findings that both point at the same missed surface are one discovery, not two.

**Every move names its signal, in writing, on the ticket.** Record **what was reclassified**, not that something failed ([[feedback-status-mirrors-work]]): *"QA found a cross-tenant read bypass — this is an auth surface, not a plain endpoint → `heavy`."* A comment that says only "escalated after bounce" has recorded nothing, and by this rule the move did not happen.

**`auto` never reads telemetry.** Its entire state is the `strategy:` field on the ticket's `LOOP-PLAN` marker, which lives in the tracker and survives every session, crash, and fresh agent. The loop must never consult `telemetry/`, `model-usage-log.md`, or its own past spend to decide a rung — a decision procedure that depends on logs is a decision procedure that breaks the first time a log is missing, rotated, or wrong. The telemetry exists for **the owner, after the fact**. If it shows tickets being reclassified into the same surface over and over, that is a signal for a *human* to add that surface to Step 1's table — not for the loop to adapt itself.

**`auto` re-gates through [[feedback-targeted-regate-on-fixes]] like any other profile**, at the ticket's current rung. A ticket reclassified into `heavy` gets `heavy`'s full re-gate; a ticket that stayed at `fast` because the defect was a typo gets `fast`'s cheap one.

## The matrix

Model names below are tiers, not ids: `top` / `deep` / `balanced` / `light` resolve through the project's `feedback/model-routing-profile.md`. `auto` selects one of these three columns per ticket; it never blends them.

| Dimension | **fast** | **balanced** (default) | **heavy** |
|---|---|---|---|
| Implementation routing | light for trivial; **balanced-medium for everything standard and deep**; top ONLY for the orchestrator and genuinely novel architecture | the four-tier ladder ([[feedback-model-effort-routing]]) with **aggressive right-sizing** ([[feedback-token-hygiene]]): light maximized wherever it qualifies, balanced for all standard work, top ONLY when genuinely fitting; route up on doubt, escalate on failure | bias UP: **deep is the default** for any real work; standard → balanced at high effort; top for anything non-trivial |
| Effort | low–medium | balanced-medium default; high on money/security or after a failed attempt | high–xhigh across the board |
| First gate (per PR) | **tests + typecheck + lint + secret scan + ONE review pass**, finalize on green. No finder panel, no adversarial verify, no top-model verdict | **risk-scaled** ([[feedback-cost-conscious-gating]]): money/security/concurrency = 5 dimensions + 3× adversarial verify; standard = 3 dimensions + 1 verifier; review and verify on the balanced model at high effort; QA + security verdicts on the top model (`xhigh` only for money/auth/concurrency); mechanical PRs get the light gate | **FULL 5-dimension + 3× adversarial verify on EVERY PR**, not risk-scaled; review and verify may run on the top model; QA + security verdicts `xhigh` ALWAYS |
| Fix re-gate | tests green + eyeball the delta, no re-gate | **targeted** ([[feedback-targeted-regate-on-fixes]]): affected dimensions + hunk-scoped verify + full-diff top-model verdicts; full on the first round or an escalation-guard trip | **FULL re-gate every fix round** |
| Runtime verify | browser check only if UI, single screenshot | browser verification required for UI changes, evidence on the PR ([[feedback-ui-verification-and-evidence]]) | exhaustive: browser + e2e + design-vs-implementation + QA-agent global review, every applicable PR |
| Extra critique passes | none | `/review` + `rigorous` on every PR ([[feedback-pr-gate-passes]]); QA agent and security gate by risk | ALL passes on EVERY PR: `/review` + `rigorous` + `security-review` + QA-agent global + design-vs-implementation |
| WIP | refill aggressively, at or above the project's cap | the project's configured cap ([[feedback-wip-limit-open-prs]]) | roughly half the cap — depth over throughput, fewer concurrent agents to avoid session-limit thrash |
| Best for | prototypes, spikes, internal tooling, mechanical PRs, non-critical services, racing a deadline with owner-accepted risk | mixed codebases where most PRs carry real risk | money movement, auth/security, concurrency cores, release-critical PRs, "must not be wrong" |
| `auto` picks it when | no risk signal fires | a risk signal fires, or QA reclassified the ticket as cross-cutting | the ticket is — or QA revealed it to be — a money/auth/concurrency surface |

## Rails that hold in EVERY profile — fast included, non-negotiable

1. **Secret scan on every staged diff** ([[feedback-no-secrets-in-code]]) — never cut, cheap.
2. **Green tests + typecheck + lint + build before finalize** ([[feedback-regression-is-blocker]], [[feedback-ci-failure-triage]]) — never ship red, in any profile.
3. **No AI attribution; PR evidence for UI; PR link on the ticket; tracker state mirrors reality on merge** — process rails, profile-independent.

**Pinned `fast` is PURE: no escalation of any kind.** When the owner sets `LOOP_STRATEGY=fast` explicitly, money-movement, auth, concurrency, and idempotency PRs run fast's reduced gate too — the owner owns that risk by choosing the profile. The only lift is a manual per-ticket `strategy:` override. Rails 1–3 still hold: "pure" drops the *gate rigor*, not those three.

**This is exactly what `auto` changes.** `auto` also lands most tickets on `fast`, but it is not pure: it lifts the risky classes to `balanced` or `heavy` up front, and it re-reads the classification when QA proves the ticket was misread. Choose pinned `fast` when you want speed and accept the risk; choose `auto` when you want speed *except* where the code says otherwise. `auto` is the default because on most codebases the risky classes are a small minority of tickets, so it buys `fast`'s wall-clock on the majority while never letting a money path through a light gate.

**Why:** the all-checks regime (`heavy`) catches CI-invisible bugs but costs ~0.6–1.5M tokens per PR and hits session limits. `balanced` holds essentially that catch rate at a fraction of the cost by scaling rigor to risk. `fast` trades the adversarial safety net for wall-clock where a wrong PASS is cheap to reverse. `auto` makes that trade **per ticket** instead of per project.

**Why complexity and not a failure counter.** A counter charges the ticket for the *implementation's* mistakes: forget a null check, buy a `heavy` gate. Do that a few times and `auto` degenerates into `heavy` for everything, which is the regime it exists to avoid. Worse, it prices rigor by how clumsy the agent was rather than by what the code can break — a sloppy typo on a doc PR would out-rank a clean first pass on a payments path. Rigor should track blast radius, and blast radius is a property of the ticket. QA's role is not to punish; it is to tell you the blast radius was bigger than you thought.

**How to apply:** read `LOOP_STRATEGY` at the top of every tick. Under `auto`, resolve each ticket's rung — the Step 1 classification, or the `strategy:` already recorded in its `LOOP-PLAN` marker, whichever is higher — before spawning, and pass that rung's model, effort, and gate shape into every `agent()` call for that ticket. When a gate comes back red, run Step 2 before re-spawning: reclassify, do not increment. When the owner switches profile mid-run, steer in-flight agents rather than waiting for the next spawn. See [[feedback-token-hygiene]] for what is safe to trim beyond this and what is the hard floor.
