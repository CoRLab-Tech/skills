---
name: taskloop
description: Autonomous task-execution loop that pulls actionable issues from a task tracker (Linear, Jira, or Plane), branches from main, implements, tests, opens a GitHub PR with no AI attribution, and self-paces the next iteration. Use when the user runs `/taskloop init` (one-time per-project setup that picks a provider and generates the loop's memory/config files), `/taskloop start` (re-arms the Monitor + ScheduleWakeup so the loop resumes for the current project), `/taskloop stop`, `/taskloop add-rule [slug]`, or `/taskloop status`. Also triggers when the user says "start" / "porneste" / "resume loop" in a working directory that already has a taskloop config under `~/.claude/projects/SLUG/memory/`.
---

# Taskloop

## Overview

Taskloop wires a task tracker (Linear, Jira, Plane) to a coding agent in a tight feedback loop. Each iteration pulls one "ready" issue, branches, implements the change with full test verification, opens a PR, and transitions the issue to review — fully autonomous, no AI attribution on commits/PRs. The loop self-paces via a `Monitor` background poll plus a `ScheduleWakeup` safety heartbeat.

Configuration is **per-project** (lives under `~/.claude/projects/<slug>/memory/`) so the same skill works for any repo. The provider (Linear / Jira / Plane) is chosen once at `init` time; the loop spec and feedback rules are provider-agnostic.

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

A provider (Linear, Jira, Plane) is a thin adapter that defines:

1. **Env vars** required (API key, host, project id, ...)
2. **Monitor script** — a bash polling loop that emits one stdout line per change in the "ready" queue (so `Monitor` wakes Claude on every queue delta)
3. **Recipes** — curl/CLI snippets for: get-issue, transition-state, post-comment, create-backlog-issue

The loop spec calls these capabilities by name; swapping providers is a one-config-file change.

Provider details live in `references/providers/<name>.md`. Read only the one matching the chosen provider — never load all of them.

## Where things live

Per-project, under `~/.claude/projects/<slugified-cwd>/memory/`:

```
.env                            # API keys, project IDs, chmod 600
.monitor-state                  # ephemeral, last queue snapshot
.pr-feedback-state              # PR registry (repo+number+issue, written at gh pr create) + per-PR last-seen feedback timestamps; drives sweep/merge/WIP-cap; survives stop/start
monitor.sh                      # rendered from provider template
MEMORY.md                       # index — loaded into every conversation
autonomous-loop.md              # loop spec (provider-agnostic)
restart-instructions.md         # "start" recipe
feedback/<slug>.md              # universal + project-specific rules
```

`MEMORY.md` is the only file guaranteed-loaded; everything else is linked from it and pulled in as needed.

## First-pass workflow

1. Parse `args`. Pick subcommand per the table above.
2. Compute project memory dir: `~/.claude/projects/<slug>/memory/` where `<slug>` = absolute CWD with `/` → `-` (matches the harness's `--Users-foo-bar` convention).
3. Read the relevant `references/workflows/*.md` for step-by-step instructions and execute.
4. Use `AskUserQuestion` for any decision the workflow doesn't already pin (provider choice, secrets, project name resolution).
5. Never commit secrets. Files containing `LINEAR_API_KEY` / `JIRA_API_TOKEN` are `chmod 600` and never staged to git.

## Universal feedback rules

28 rules ship as assets. `init` copies them into the project's `memory/feedback/` and links each one from `MEMORY.md`. These rules are provider-neutral and the loop reads them every tick.

The rules list (see `assets/feedback/`):

| File | What it enforces |
|---|---|
| `no-ai-attribution.md` | Never add Co-Authored-By / "Generated with Claude" to commits or PRs |
| `pull-main-each-task.md` | Branch from fresh `origin/main` every iteration, never from stale branch |
| `playwright-testing.md` | UI changes verified via Playwright MCP before PR |
| `run-tests-locally.md` | `npm/yarn test` is mandatory before every PR |
| `run-full-test-suite.md` | Run the **full** suite (no path filter) — per-spec runs aren't enough |
| `new-code-needs-tests.md` | Every behavior change ships with tests for the new behavior; bugfixes need a fail→pass reproducing test |
| `regression-is-blocker.md` | Watch PR CI checks to completion; any failing test is a hard blocker |
| `security-review-gate.md` | Every PR passes a security pass (security-review skill or manual checklist) before transition |
| `no-secrets-in-code.md` | Scan every staged diff for secrets; tokens/keys/passwords never reach git |
| `minimal-diff-scope.md` | Touch only what the task requires; discovered work goes to the backlog, not the diff |
| `dependency-hygiene.md` | New dependencies are a vetted last resort: exact name, advisories, pinning, PR justification |
| `run-code-review.md` | Invoke `/review` on every PR opened by the loop |
| `rigorous-pr-critique.md` | When the `rigorous` skill is available, run its critique on every PR besides `/review` |
| `qa-agent-review.md` | A QA agent judges the work globally vs requirements/design/context before review transition |
| `pr-visual-evidence.md` | UI changes require screenshots/video attached to the PR |
| `design-vs-implementation.md` | Before/after screenshots mandatory for UI-affecting PRs; design vs implementation when a design exists |
| `private-repo-screenshots.md` | Host PR screenshots inside the PR branch (raw URLs 404 on private repos) |
| `watch-pr-comments.md` | Actively track the loop's open PRs; review feedback outranks new tasks |
| `read-media-in-comments.md` | Actually view comment attachments — images via Read, videos frame-extracted with ffmpeg |
| `merge-on-approval.md` | Approved + green CI + no unresolved threads → the loop merges its own PR |
| `ticket-done-on-merge.md` | Merged PR → tracker issue moves to "Merged" or the closest completed state |
| `wip-limit-open-prs.md` | Max 3 open loop-owned PRs; at the cap, service the review pipeline instead of new tasks |
| `fail-gracefully-timebox.md` | ~3 failed attempts → document blocker on the issue, release it, move on; never weaken gates to "finish" |
| `use-project-skills.md` | Use repo-appropriate skills (rigorous, impeccable, pixel-perfect, ...) when they match the task |
| `todo-opens-backlog-task.md` | Every TODO the diff introduces opens a matching backlog task in the tracker |
| `save-corrections.md` | Save every mid-run user correction as a feedback memory for future ticks |
| `only-ready-not-backlog.md` | Act only on the explicit "ready" status, never the triage backlog |
| `local-test-remote-unaffected.md` | For local tests, run only the patched service via node; point at staging for everything else |

## Adding a new provider

To support a new tracker (GitHub Issues, Asana, ClickUp, …):

1. Implement the 6-verb contract documented in `references/adding-a-provider.md`.
2. Create `references/providers/<name>.md` with env, queries, and recipes.
3. Add a `monitor-<name>.sh.tmpl` to `assets/`.
4. Add the provider to the `init` AskUserQuestion options.

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
- `references/adding-a-provider.md` — the 6-verb contract
