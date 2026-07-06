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
| `light` | Mechanical, bounded, no design: typo/copy fixes, config values, dependency pins, doc edits, media frame extraction, registry bookkeeping | fastest rung (e.g. `haiku`) | low–medium |
| `standard` | Typical feature/bugfix: a few files, known patterns, no architectural choice | balanced rung (e.g. `sonnet`) | medium–high |
| `deep` | Serious engineering: architecture inside known patterns, cross-module refactors, debugging races/heisenbugs, performance work, security-sensitive surfaces (auth, payments, uploads) | strong rung (e.g. `opus` — it keeps this seat even when a Mythos-class top exists) | high–xhigh |
| `frontier` | The rare hardest work: novel architecture with no pattern to lean on, "nobody knows why" investigations, adversarial/security design, anything the deep rung already failed once | the profile's top (e.g. the Mythos-class `fable` where exposed, else folds into `opus`) | xhigh |

Four rungs because the ladder has four rungs — with `haiku → sonnet → opus → fable` all available, a three-floor scheme wastes one, and the 5–25× cost ratios between rungs are exactly where routing pays.

**Verdicts are not a tier — they are always the top.** The QA agent gate ([[feedback-qa-agent-review]]), the security pass ([[feedback-security-review-gate]]), blocking-finding adjudication in reviews, the merge decision checks ([[feedback-merge-on-approval]]), and the timebox release call ([[feedback-fail-gracefully-timebox]]) run on the **most capable model the harness exposes, at high effort — regardless of the task's tier**. A light task still gets a top-model verdict; the cheap part is the typing, never the judging.

**Why:** a fleet that runs everything on the top model wastes budget on mechanical work; a fleet that runs everything cheap ships subtle garbage that the gates (also cheap) wave through. The pattern is literature-backed: cascade/routing systems (FrugalGPT, RouteLLM, AutoMix) hold ~95% of frontier quality while routing most calls to cheaper rungs at 45–85% cost cuts; Anthropic's own multi-agent research system runs an Opus-class lead over Sonnet-class workers and beat single-agent by >90%; and the escalate-on-failure ladder is AutoMix's generate→verify→escalate loop. LLM-as-judge findings cut both ways (a weak judge over strong debaters can hold up in debate settings), but for single-artifact gate verdicts the judge must not be weaker than the work it judges — self-preference and capability gaps bite there — so verdicts stay pinned to the top.

**How to apply:**
- **Tier is assigned at triage** and recorded in the `LOOP-PLAN` marker with the reasoning; the signals: files touched (1 vs many), design freedom (none vs choices to make), blast radius (leaf module vs shared contract), domain risk (CRUD vs auth/payment/concurrency), and any advanced-thinking smell in the ticket (profiling, race, "investigate", "why does...").
- **Mechanics per harness surface:** the Agent tool takes `model:`; Workflow `agent()` takes `{model, effort}`; custom agent definitions pin both in frontmatter. When the harness exposes NO model control, run everything on the session model — never engineer a downgrade.
- **The marker contract (mechanically enforced):** every agent prompt the loop writes BEGINS with `[LOOP-AGENT issue:<key> tier:<light|standard|deep|frontier> verdict:<yes|no>]`. A PreToolUse hook installed at init (`hook-agent-routing.mjs` in the memory dir) reads the marker on every spawn and **raises under-floor calls in place** over the 4-rung ladder: verdict/frontier → pinned to the profile's top; deep → floored at the strong rung; standard → floored at balanced. Rank-compared, so it never downgrades (a `fable` spawn under an `opus`-topped profile passes untouched), never blocks, and ignores prompts without the marker — prose can be forgotten, the hook cannot.
- **When in doubt, route UP.** Ambiguous tier = the higher tier. A wrong up-route costs money; a wrong down-route costs quality — the rule's name is routing, not rationing.
- **Escalation ladder on failure:** a failed implement→verify attempt up-tiers the NEXT attempt one rung (light → standard → deep → frontier) before the timebox counts it out — many "stuck" tasks are just under-modeled. A failure on the profile's top rung counts double toward the timebox: more model won't fix an underspecified ticket.
- **The orchestrator is a judge:** the main loop session itself does verdict-grade work (gate adjudication, merge calls, triage), so run taskloop sessions on the most capable model available. If the session model is weaker, spawn verdict work as subagents pinned to the top model instead of judging inline.
- **The concrete model ids come from the project's routing profile**, chosen at init (`feedback/model-routing-profile.md`: Mythos = fable-topped, High = opus-topped, or Custom) and baked into the hook. The tiers, the verdict-pin principle, and never-downgrade are non-negotiable; only the ids and the top's scope are per-project. Model names drift across harness versions — never hardcode an id outside the profile file and the rendered hook.
