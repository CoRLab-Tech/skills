---
name: taskloop
description: Autonomous task-execution loop that pulls actionable issues from a task tracker (Linear, Jira, Plane, or GitHub Issues), branches from main, implements, tests, opens a GitHub PR with no AI attribution, and self-paces the next iteration. Use when the user runs `/taskloop init` (one-time per-project setup that picks a provider and generates the loop's memory/config files), `/taskloop start` (re-arms the Monitor + ScheduleWakeup so the loop resumes for the current project), `/taskloop stop`, `/taskloop add-rule [slug]`, or `/taskloop status`. Also triggers when the user says "start" / "porneste" / "resume loop" in a working directory that already has a taskloop config under `~/.claude/projects/SLUG/memory/`.
---

# Taskloop

## Overview

Taskloop wires a task tracker (Linear, Jira, Plane, GitHub Issues) to a coding agent in a tight feedback loop. Each iteration pulls one "ready" issue, branches, implements the change with full test verification, opens a PR, and transitions the issue to review — fully autonomous, no AI attribution on commits/PRs. The loop self-paces via a `Monitor` background poll plus a `ScheduleWakeup` safety heartbeat.

Configuration is **per-project** (lives under `~/.claude/projects/<slug>/memory/`) so the same skill works for any repo. The provider (Linear / Jira / Plane / GitHub Issues) is chosen once at `init` time; the loop spec and feedback rules are provider-agnostic.

## Subcommand routing

The skill is invoked with an `args` string. Parse the first whitespace-delimited token:

| First token | Action | Workflow guide |
|---|---|---|
| `init` (or empty args) | One-time per-project setup | `references/workflows/init.md` |
| `start` | Re-arm Monitor + ScheduleWakeup for current project | `references/workflows/start.md` |
| `stop` | TaskStop monitor, no further wakeups | `references/workflows/stop.md` |
| `add-rule <slug>` | Add a project-specific feedback rule | `references/workflows/add-rule.md` |
| `status` | Print monitor task id, last actionable issue, last PR | `references/workflows/status.md` |
| anything else | Print usage and stop | inline below |

If the args is empty, default to `init` only when the project's memory dir doesn't exist yet. Otherwise default to `start`.

**Usage line (print when args don't parse):**

```
/taskloop <init|start|stop|add-rule <slug>|status>
```

## Provider concept

A provider (Linear, Jira, Plane, GitHub Issues) is a thin adapter that defines:

1. **Env vars** required (API key, host, project id, ...)
2. **Monitor script** — a bash polling loop that emits one stdout line per change in the "ready" queue (so `Monitor` wakes Claude on every queue delta)
3. **Recipes** — curl/CLI snippets for: get-issue, transition-state, post-comment, create-backlog-issue

The loop spec calls these capabilities by name; swapping providers is a one-config-file change.

Provider details live in `references/providers/<name>.md`. Read only the one matching the chosen provider — never load all of them.

## Where things live

Per-project, under `~/.claude/projects/<slugified-cwd>/memory/`:

```
.env                            # API keys, project IDs, LOOP_STRATEGY, LOOP_AUTOMERGE, chmod 600
.monitor-state                  # ephemeral, last queue snapshot
.pr-feedback-state              # PR registry (repo+number+issue+merge lane+gatedHead+ownActivity, written at gh pr create) + per-PR last-seen feedback timestamps; drives sweep/merge/WIP-cap; survives stop/start
.queue-plan                     # last LOOP-PLAN triage + queue signature (ids/titles/desc-hashes/human-comment counts — never the loop's own plan comments)
monitor.sh                      # rendered from provider template
monitor-prs.sh                  # the loop's own eyes on its PRs (merge/comment/CI deltas)
reconcile-merged.sh             # level-triggered repair of tickets the PR watcher's edge trigger missed (Plane, GitHub)
review-recall.sh                # cron: periodic ping listing review-ready PRs still unmerged
hook-agent-routing.mjs          # PreToolUse gate on Task|Agent: upgrades under-modeled [LOOP-AGENT] spawns + writes the spawn ledger
hook-loop-guards.mjs            # PreToolUse gate on Bash: denies a backgrounded gate inside a subagent, and a commit carrying AI attribution
usage-rollup.mjs                # sums finished subagent transcripts into telemetry/usage-*.jsonl
targeted-regate.mjs             # Workflow script for fix-round re-gates (targeted-regate-on-fixes rule)
telemetry/spawns-YYYY-MM.jsonl  # append-only: issue, tier, strategy, requested → routed model, effort (hook-written)
telemetry/usage-YYYY-MM.jsonl   # append-only: per-agent token totals joined to the spawn that caused them
telemetry/guards-YYYY-MM.jsonl  # append-only: every tool call a guard denied, and why
MEMORY.md                       # index — loaded into every conversation
agent-brief.md                  # condensed startup brief spawned agents read INSTEAD of the full memory set
autonomous-loop.md              # loop spec (provider-agnostic)
restart-instructions.md         # "start" recipe
model-usage-log.md              # routing policy + measured gate costs (the per-task ledger lives in telemetry/)
feedback/<slug>.md              # universal + project-specific rules
```

**Telemetry is written by mechanism, never by convention.** The hook cannot forget to record a spawn, and the roll-up cannot forget what an agent cost. Both files are append-only and idempotent. Nothing in the loop reads them back — `auto` decides a rung from the ticket's `LOOP-PLAN` marker alone, so a missing or rotated log can never change what the loop does. The telemetry is for the owner, after the fact.

`MEMORY.md` is the only file guaranteed-loaded; everything else is linked from it and pulled in as needed.

## First-pass workflow

1. Parse `args`. Pick subcommand per the table above.
2. Compute project memory dir: `~/.claude/projects/<slug>/memory/` where `<slug>` = absolute CWD with `/` → `-` (matches the harness's `--Users-foo-bar` convention).
3. Read the relevant `references/workflows/*.md` for step-by-step instructions and execute.
4. Use `AskUserQuestion` for any decision the workflow doesn't already pin (provider choice, secrets, project name resolution).
5. Never commit secrets. Files containing `LINEAR_API_KEY` / `JIRA_API_TOKEN` are `chmod 600` and never staged to git.

## Universal feedback rules

39 rules ship as assets. `init` copies them into the project's `memory/feedback/` and links each one from `MEMORY.md`, grouped by when it applies. They are provider-neutral.

**Prose is the weakest form of enforcement.** Every rule that was empirically ignored in a real run has been converted into a mechanism, and new rules should be too. What is mechanical today:

| Mechanism | Enforces |
|---|---|
| `hook-agent-routing.mjs` (PreToolUse on `Task\|Agent`) | the model/effort ladder; also writes the append-only spawn ledger |
| `hook-loop-guards.mjs` (PreToolUse on `Bash`) | `gates-run-foreground` and `no-ai-attribution` — both denied, not merely discouraged |
| `targeted-regate.mjs` schema | a review finding without a verbatim `quote` cannot exist |
| `monitor-prs.sh` / `reconcile-merged.sh` | merge, comment and CI events arrive as signals, not as chat |
| `usage-rollup.mjs` | the spend record; the loop cannot forget to write it |
| GitHub | a draft PR cannot be merged |

The rules, by when they apply (see `assets/feedback/`):

**Always — every tick:** `never-self-halt-loop`, `loop-strategy-profiles`, `queue-triage-plan`, `continuous-flow-from-ready`, `wip-limit-open-prs`, `status-mirrors-work`, `pull-main-each-task`, `gates-run-foreground`, `draft-until-gated`, `regression-is-blocker`, `no-ai-attribution`

**While implementing:** `minimal-diff-scope`, `new-code-needs-tests`, `run-full-test-suite`, `no-secrets-in-code`, `dependency-hygiene`, `todo-opens-backlog-task`, `use-project-skills`, `local-test-remote-unaffected`, `parallel-disjoint-tasks`, `isolated-browsers-parallel-agents`, `fail-gracefully-timebox`, `block-stuck-tickets-visibly`

**Gating a PR:** `pr-gate-passes` (the four lenses: `/review`, `rigorous`, security, QA agent), `ui-verification-and-evidence`, `cost-conscious-gating`, `targeted-regate-on-fixes`, `ci-failure-triage`

**After the PR is open:** `watch-pr-comments`, `read-media-in-comments`, `merge-on-approval`, `automerge-risk-lanes`, `ticket-done-on-merge`, `pr-registry-race`, `reconcile-tracker-vs-github`, `telegram-notify-owner`

**Cost, routing, learning:** `model-effort-routing`, `token-hygiene`, `continuous-learning`

**The promotion bar for a new rule** (`continuous-learning`): it is kept only if it is verified, names the failure pattern concretely, and records the alternative that was ruled out. The rule set is read every tick, so every weak rule is a permanent tax on every future iteration. Prefer strengthening an existing rule over adding a sibling; prefer a hook over a paragraph.

## Adding a new provider

To support a new tracker (Asana, ClickUp, Shortcut, …):

1. Implement the 6-verb contract documented in `references/adding-a-provider.md`.
2. Create `references/providers/<name>.md` with env, queries, and recipes.
3. Add a `monitor-<name>.sh.tmpl` to `assets/`.
4. Add the provider to the `init` AskUserQuestion options.
5. Optionally add a `reconcile-merged-<name>.sh.tmpl` (see the Plane one). Without it the `reconcile-tracker-vs-github` rule still applies — the loop just runs the reconcile inline each sweep through the provider's transition recipe instead of as a background script.

The loop spec template is already provider-neutral; only the adapter changes.

## Key constraints

- **Per-project memory** — never write to another project's memory dir from this one. Slug the CWD precisely.
- **Idempotency** — running `init` twice on the same project should detect existing config and ask whether to overwrite individual files, not silently clobber.
- **AskUserQuestion before destructive writes** — secrets, slug collisions, overwrite existing rule files.
- **No AI attribution anywhere** — neither in skill output (commit messages, PR bodies) nor in scaffolded files. The bundled feedback rule enforces this on the loop, but the skill itself must also obey it when writing commits via git.

## Reference index

Read these only when the workflow points to them:

- `references/workflows/init.md` — full init interview + file generation
- `references/workflows/start.md` — Monitor + ScheduleWakeup arming
- `references/workflows/stop.md` — clean teardown
- `references/workflows/add-rule.md` — adding a project-specific feedback rule
- `references/workflows/status.md` — diagnostics
- `references/providers/linear.md` — Linear adapter (verified end-to-end)
- `references/providers/jira.md` — Jira Cloud adapter (recipes documented, not live-tested)
- `references/providers/plane.md` — Plane adapter, MCP-first with curl monitor/fallback (verified end-to-end)
- `references/providers/github.md` — GitHub Issues adapter, states as labels via `gh` (recipes documented, not live-tested)
- `references/adding-a-provider.md` — the 6-verb contract
