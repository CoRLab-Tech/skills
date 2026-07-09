---
name: feedback-token-hygiene
description: "The standing token-economy package — model-match every task, keep a persistent light-model ops-helper, hold the prompt cache stable, keep context clean, and keep the repo cheap to read"
metadata:
  type: feedback
---

Apply this package systematically, every session. On focused work it saves 40–70% with no measurable quality loss. Ordered by impact:

**1. Right model per task — the biggest lever.**

- The **top model** ONLY for: the orchestrator loop itself, architecture and complex reasoning, and money / auth / concurrency verdicts.
- The **balanced model** for most implementation code (effort `medium` by default; `high` only on a money/security surface or after a failed attempt).
- The **light model** for simple subtasks — and actually USE IT; it is the tier that goes unused. Route to it: comment / JSDoc / doc / config / rename / test-only / fixture PRs, and all mechanical ops (see #2). Extend it even into an in-progress task's simple sub-steps.

**2. A persistent light-model ops-helper for mechanical work.** Spawn ONE light agent per session for merge sweeps, tracker transitions, registry rebuilds, ticket claims, id resolution, and status counts — and **reuse it via `SendMessage`** each sweep so its context stays warm rather than spawning a fresh one every time. It returns a short summary; the orchestrator keeps the JUDGMENT (which ticket to pull, disjointness, conflict resolution, verdicts) and never spends top-model reasoning on transition mechanics. Measured: a full sweep on the light model runs ≈42k tokens against the equivalent top-model inline reasoning, and a *cold* helper costs more than a warm one because it re-paginates the tracker every time.

**3. Prompt-cache stability.** Cached input bills at roughly 10%. Keep bytes STABLE across spawns: every implementation agent reads the SAME small `agent-brief.md`, and spawn prompts keep a stable structure with the task-specific bits at the END and the boilerplate identical character for character. A casual rewrite or reorder of the brief silently busts the cache for every agent after it.

**4. Clean context per unit of work.** Implementation agents already get fresh context per task. The orchestrator accumulates — when the session grows long, let it compact. Use a hard clear only between genuinely unrelated efforts, never mid-loop, where it would drop live orchestration state.

**5. Project hygiene.** A lean `CLAUDE.md`, few MCP servers, and a `.claudeignore` at the repo root for paths no agent should read (`node_modules`, `dist`/`build`, generated protos, coverage, large fixtures). Adding or maintaining `.claudeignore` is itself a proper loop ticket ([[feedback-todo-opens-backlog-task]]), not an ad-hoc repo edit — a stray edit on a branch collides with every live worktree.

**Observe cheap, judge dear.** The line is not task hardness, it is **observation vs judgment**. Reading a mechanical fact — an exit code, a pass/fail count, a file list, thread text — is a light-model job. Deciding something — is this code correct, is this finding real, go or no-go — is never a light-model job.

- **Running the suite is observation.** The test + typecheck + lint + build EXECUTION goes to the light model: it launches the run and reports the exit code and failing test names. All green → move on, no stronger model touched. Only on RED does it escalate, and then the *diagnosis and fix* go to the task's own tier. The green verdict is trustworthy because it is a boolean from the runner, not a judgment. Guardrail: the light model still runs the FULL suite with no path filter, and ANY ambiguity — flaky, skipped, partial — escalates rather than waving through.
- Other places never to load an expensive model's context: diff capture and per-file hunk splitting; CI and log triage; frame extraction from comment videos ([[feedback-read-media-in-comments]]); tracker / GitHub / notifier bookkeeping; rebase, merge, branch, and worktree mechanics; screenshot capture (the collecting, not the visual judging); and the mechanical half of queue-plan formatting (the triage JUDGMENT stays with the orchestrator).
- **The one line you never cross:** a go/no-go VERDICT always reads the FULL diff itself. A light-model summary is fine as orchestrator context but must NEVER stand in for the verdict's own reading.

## What is left after the big cuts, and what must never be cut

Once this package and [[feedback-cost-conscious-gating]] and [[feedback-targeted-regate-on-fixes]] are in force, the big cuts are done — together they take a PR from ~0.6–1.5M tokens to a fraction, and a measured A/B on one fix re-gate showed **−49.4% with an identical PASS verdict**. Roughly 10–20% more, plus wall-clock, remains available:

1. **Prompt-cache discipline — the biggest remaining lever.** Keep `agent-brief.md` and the spawn boilerplate byte-stable, as above. Worth instrumenting the real cache-hit rate so it stops being a guess.
2. **`.claudeignore` at the repo root**, per point 5 above. Cheap, zero quality risk, and a proper loop ticket rather than an ad-hoc repo edit.
3. **`pipeline()` not a barrier in gate scripts — wall-clock, not tokens.** A gate that `parallel()`s all reviews and then `parallel()`s all verifies idles the fast dimensions waiting on the slowest. Author gates so each finding verifies the instant its dimension finishes.
4. **First-gate diff-sharing — TESTED, DO NOT ADOPT.** Giving every finder a shared pre-chunked per-file index instead of the full diff: A/B with 10 balanced-model finders on a 7-file fixture with 5 seeded bugs (2 cross-file) held the catch rate at 5/5 in **both** arms, but the shared-index arm cost **4.9× the read round-trips and ~3% MORE tokens** — thorough finders defensively re-pull nearly every file, and that same thoroughness is what preserves the catch rate. Keep any such prototype flag-gated and off. This is a recorded negative result: do not re-derive it.

**HARD QUALITY FLOOR — never cut to save tokens.** These are what catch the CI-invisible bugs: the 5-dimension review plus adversarial verify on a PR's FIRST gate; top-model QA and security verdicts on the FULL diff (the cross-cutting safety net, which is why [[feedback-targeted-regate-on-fixes]] keeps them full-diff even when the review is scoped); and the full gate on money / auth / concurrency / idempotency PRs, with `xhigh` verdicts there.

**How to apply:** every tick — ops to the persistent light helper; trivial PRs to the light model with a light gate; standard code to the balanced model at medium effort with a reduced gate; money / auth / concurrency to the top model with a full gate and `xhigh` verdicts. Keep the brief and the spawn boilerplate byte-stable. See [[feedback-cost-conscious-gating]], [[feedback-model-effort-routing]].
