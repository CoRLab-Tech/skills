---
name: feedback-model-effort-routing
description: "Every agent the loop spawns gets a model + effort matched to the task's complexity tier — cheap where it's safe, maximal where it matters, and every go/no-go verdict belongs to the MOST capable model available"
metadata:
  type: feedback
---

The loop never launches an agent on a default model by inertia. Before every spawn it asks two questions: *how hard is this work?* (→ tier) and *is this a verdict?* (→ pin to the top). The goal is spend-smart-lose-nothing: mechanical work runs on the fastest tier, real engineering on a strong tier, and **anything that decides go/no-go runs on the most capable model available, at high effort, always** — quality gates are never where savings come from.

**The tiers** (assigned per task at triage time — the `tier:` field in the `LOOP-PLAN` marker, [[feedback-queue-triage-plan]]):

| Tier | What qualifies | Model | Effort |
|---|---|---|---|
| `light` | Mechanical, bounded, no design, **no UI surface**: config values, dependency pins, doc edits, media frame extraction, registry bookkeeping. A copy/typo fix that renders in the UI is `standard` — it drags mandatory browser verification with it | fastest rung (e.g. `haiku`) | low–medium |
| `standard` | Typical feature/bugfix: a few files, known patterns, no architectural choice | balanced rung (e.g. `sonnet`) | medium–high |
| `deep` | Serious engineering: architecture inside known patterns, cross-module refactors, debugging races/heisenbugs, performance work, security-sensitive surfaces (auth, payments, uploads) | strong rung (e.g. `opus` — it keeps this seat even when a Mythos-class top exists) | high–xhigh |
| `frontier` | The rare hardest work: novel architecture with no pattern to lean on, "nobody knows why" investigations, adversarial/security design, anything the deep rung already failed once | the profile's top (e.g. the Mythos-class `fable` where exposed, else folds into `opus`) | xhigh |

Four rungs because the ladder has four rungs — with `haiku → sonnet → opus → fable` all available, a three-floor scheme wastes one, and the 5–25× cost ratios between rungs are exactly where routing pays.

**Verdicts are not a tier — they are always the top.** The QA agent and security passes ([[feedback-pr-gate-passes]]), blocking-finding adjudication in reviews, the merge decision checks ([[feedback-merge-on-approval]]), and the timebox release call ([[feedback-fail-gracefully-timebox]]) run on the **profile's top model — the most capable configured — at high effort, regardless of the task's tier**. A light task still gets a top-model verdict; the cheap part is the typing, never the judging.

**Why:** a fleet that runs everything on the top model wastes budget on mechanical work; a fleet that runs everything cheap ships subtle garbage that the gates (also cheap) wave through. The pattern is literature-backed: cascade/routing systems (FrugalGPT, RouteLLM, AutoMix) hold ~95% of frontier quality while routing most calls to cheaper rungs at 45–85% cost cuts; Anthropic's own multi-agent research system runs an Opus-class lead over Sonnet-class workers and beat single-agent by >90%; and the escalate-on-failure ladder is AutoMix's generate→verify→escalate loop. LLM-as-judge findings cut both ways (a weak judge over strong debaters can hold up in debate settings), but for single-artifact gate verdicts the judge must not be weaker than the work it judges — self-preference and capability gaps bite there — so verdicts stay pinned to the top.

**How to apply:**
- **Tier is assigned at triage** and recorded in the `LOOP-PLAN` marker with the reasoning; the signals: files touched (1 vs many), design freedom (none vs choices to make), blast radius (leaf module vs shared contract), domain risk (CRUD vs auth/payment/concurrency), and any advanced-thinking smell in the ticket (profiling, race, "investigate", "why does...").
- **Mechanics per harness surface:** the Agent tool takes `model:`; Workflow `agent()` takes `{model, effort}`; custom agent definitions pin both in frontmatter. When the harness exposes NO model control, run everything on the session model — never engineer a downgrade.
- **The marker contract (mechanically enforced):** every agent prompt the loop writes BEGINS with `[LOOP-AGENT issue:<key> tier:<light|standard|deep|frontier> verdict:<yes|no>]`. A PreToolUse hook installed at init (`hook-agent-routing.mjs` in the memory dir) reads the marker on every spawn. It never blocks, and it ignores prompts without the marker — prose can be forgotten, the hook cannot.

- **The ladder lives in the profile, ids and order together.** `feedback/model-routing-profile.md` declares `LADDER` (cheapest first) and the four rungs; the hook derives its rank map from that array and hardcodes no ordering. `init` asserts every named rung is on the ladder before the loop is armed. A harness that adds a rung — as `fable` once was — is a one-line profile edit, not a code change.

- **Verdicts and `frontier` are pinned by IDENTITY, not by rank.** The model must *be* the profile's top; an unset model is pinned too, so a mid-session `/model` downgrade cannot leak into a verdict. Identity, because a rank comparison silently fails whenever the profile's top is not itself the ladder's highest rung: a spawn asking for the higher rung compares equal-or-above and passes through, and the verdict then runs on a model the owner never chose. A pin must be immune to unknown ids; only identity is.

- **`deep` and `standard` carry a FLOOR, compared by rank**, applied when a model is **explicitly** set below it. An unset model inherits the session, which already sits at or above the deep floor. A known model above its floor passes untouched — the hook never downgrades.

- **A model that is not on the ladder at all is left UNTOUCHED, with a visible warning** and an `off_ladder` row in the spawn ledger. We cannot know whether an unknown id sits above or below the floor, and guessing "below" would silently downgrade a deliberately-chosen better model. The asymmetry decides it: under-modelling is recoverable — the escalate-on-failure ladder re-runs a failed attempt one rung up — while a silently downgraded frontier agent is not. When the profile's own `DEEP_MODEL` or `BALANCED_MODEL` is off-ladder, the hook cannot floor that tier and says so instead of pretending.
- **When in doubt, route UP.** Ambiguous tier = the higher tier. A wrong up-route costs money; a wrong down-route costs quality — the rule's name is routing, not rationing.
- **Escalation ladder on failure:** a failed implement→verify attempt up-tiers the NEXT attempt one rung (light → standard → deep → frontier) before the timebox counts it out — many "stuck" tasks are just under-modeled. The escalated tier is written back to the ticket's `LOOP-PLAN` `tier:` field in place (so it survives restarts), and re-triage never lowers a tier below the highest rung already attempted for that issue ([[feedback-queue-triage-plan]]). A failure on the profile's top rung counts double toward the timebox: more model won't fix an underspecified ticket.
- **The orchestrator is a judge:** the main loop session itself does verdict-grade work (gate adjudication, merge calls, triage), so run taskloop sessions on the most capable model available. If the session model is weaker, spawn verdict work as subagents pinned to the top model instead of judging inline.
- **The concrete model ids come from the project's routing profile**, chosen at init (`feedback/model-routing-profile.md`: Mythos = fable-topped, High = opus-topped, or Custom) and baked into the hook. The tiers, the verdict-pin principle, and never-downgrade are non-negotiable; only the model ids are per-project. Model names drift across harness versions — never hardcode an id outside the profile file and the rendered hook.
