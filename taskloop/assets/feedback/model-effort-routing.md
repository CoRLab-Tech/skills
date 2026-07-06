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
| `light` | Mechanical, bounded, no design: typo/copy fixes, config values, dependency pins, doc edits, media frame extraction, registry bookkeeping | fastest available (e.g. `haiku`) | low–medium |
| `standard` | Typical feature/bugfix: a few files, known patterns, no architectural choice | balanced tier or the session's model (e.g. `sonnet`) | medium–high |
| `deep` | Architecture, cross-module refactors, debugging races/heisenbugs, performance work, security-sensitive surfaces (auth, payments, uploads), anything with advanced-reasoning smell | most capable available (e.g. the Mythos-class `fable` where the harness exposes it, else `opus`) | high–xhigh |

**Verdicts are not a tier — they are always the top.** The QA agent gate ([[feedback-qa-agent-review]]), the security pass ([[feedback-security-review-gate]]), blocking-finding adjudication in reviews, the merge decision checks ([[feedback-merge-on-approval]]), and the timebox release call ([[feedback-fail-gracefully-timebox]]) run on the **most capable model the harness exposes, at high effort — regardless of the task's tier**. A light task still gets a top-model verdict; the cheap part is the typing, never the judging.

**Why:** a fleet that runs everything on the top model wastes budget on mechanical work; a fleet that runs everything cheap ships subtle garbage that the gates (also cheap) wave through. Routing by tier keeps the cost curve sane, and pinning verdicts to the top model means quality is bounded by the best judge available, not the cheapest worker.

**How to apply:**
- **Tier is assigned at triage** and recorded in the `LOOP-PLAN` marker with the reasoning; the signals: files touched (1 vs many), design freedom (none vs choices to make), blast radius (leaf module vs shared contract), domain risk (CRUD vs auth/payment/concurrency), and any advanced-thinking smell in the ticket (profiling, race, "investigate", "why does...").
- **Mechanics per harness surface:** the Agent tool takes `model:`; Workflow `agent()` takes `{model, effort}`; custom agent definitions pin both in frontmatter. When the harness exposes NO model control, run everything on the session model — never engineer a downgrade.
- **When in doubt, route UP.** Ambiguous tier = the higher tier. A wrong up-route costs money; a wrong down-route costs quality — the rule's name is routing, not rationing.
- **Escalation ladder on failure:** a failed implement→verify attempt on a `light`/`standard` task up-tiers the NEXT attempt (standard → deep model at high effort) before the timebox counts it out — many "stuck" tasks are just under-modeled. A failure on the top tier counts double toward the timebox: more model won't fix an underspecified ticket.
- **The orchestrator is a judge:** the main loop session itself does verdict-grade work (gate adjudication, merge calls, triage), so run taskloop sessions on the most capable model available. If the session model is weaker, spawn verdict work as subagents pinned to the top model instead of judging inline.
- Model names drift across harness versions — the rule is tiers ("fastest / balanced / most capable available"), the parenthesized names are today's examples. Never hardcode a model id into a project's memory files.
