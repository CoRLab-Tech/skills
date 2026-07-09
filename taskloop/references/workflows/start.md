# Start workflow

Re-arm the polling Monitor and the ScheduleWakeup safety heartbeat so the autonomous loop resumes for the current project. No questions asked — the setup is already approved at `init` time.

## Preconditions

- The project memory dir exists: `~/.claude/projects/<slug>/memory/`
- `.env`, `monitor.sh`, `MEMORY.md` are present in it
- `restart-instructions.md` is present (rendered at init)

If any is missing, fall back to `init` workflow instead.

## Step 1 — Reset the monitor state

```bash
SLUG=$(pwd | sed 's|/|-|g')
MEM="$HOME/.claude/projects/${SLUG}/memory"
rm -f "$MEM/.monitor-state" "$MEM/.pr-monitor-state"
```

Removing the state file forces the first tick to re-emit the current actionable queue, so Claude sees what's pending immediately.

## Step 1b — Arm the telemetry (append-only spend record)

The loop must record what it spends **as it spends it**, not from memory afterwards. Arming it is two checks:

```bash
mkdir -p "$MEM/telemetry"
# the routing hook writes the spawn ledger; prove it is installed AND that it appends
echo '{"tool_use_id":"tu_smoke","tool_input":{"prompt":"[LOOP-AGENT issue:SMOKE tier:frontier verdict:yes] t","model":"haiku"}}' \
  | node "$MEM/hook-agent-routing.mjs" >/dev/null
tail -1 "$MEM/telemetry/spawns-$(date +%Y-%m).jsonl"   # must show issue:SMOKE, upgraded:true
```

If the hook is not wired into the project's `.claude/settings.local.json` as a `PreToolUse` matcher on `Task|Agent`, no spawn is ever recorded — re-install it per `init` Step 5 before continuing. A missing hook is silent: routing still happens by prose, and the ledger simply stays empty.

The probe leaves one real row behind, with `issue: "SMOKE"`. The ledger is append-only, so it stays — filter it out when analysing (`jq 'select(.issue != "SMOKE")'`). That is the cost of proving the mechanism works rather than assuming it.

Then roll up any agents that finished since the last session, and do this again at the **end of every tick**:

```bash
node "$MEM/usage-rollup.mjs"    # append-only, idempotent, skips still-running agents
```

The roll-up is cheap (hundreds of transcripts in about a second) and safe to run twice. It never rewrites a row, so a crash mid-run loses nothing.

## Step 2 — Verify the queue once

Read the provider name from `$MEM/.env` (presence of `LINEAR_API_KEY` / `JIRA_API_TOKEN` / `PLANE_API_KEY` / `GITHUB_REPO` decides). Run the appropriate one-shot check from the provider doc:

- **Linear** — see "Verify Todo queue" in `references/providers/linear.md`
- **Plane** — see "Verify ready queue" in `references/providers/plane.md`
- **GitHub Issues** — see "Verify queue" in `references/providers/github.md`
- **Jira** — see "Verify Ready queue" in `references/providers/jira.md`

If the queue has items, **triage it first** — mark every ready ticket with the `LOOP-PLAN` vocabulary (order / group / depends-on / tier), autonomously, per the `queue-triage-plan` feedback rule — then **start processing per the plan immediately** following the spec in `$MEM/autonomous-loop.md`. If empty, just confirm "Monitor pornit, coadă goală" (or English equivalent) and continue to Step 3.

## Step 3 — Arm BOTH Monitors (queue + PRs)

The loop is an **independent instrument**: it watches the tracker queue AND its own open PRs by itself. The owner communicates ONLY through PR comments and tracker comments — never expect a chat ping ("I merged it") to drive the loop.

Call the harness's `Monitor` tool TWICE:

1. **Tracker queue monitor**
   - `command`: `$MEM/monitor.sh` (absolute path)
   - `description`: e.g. `<project name> ready queue`
   - `persistent`: `true`, `timeout_ms`: `3600000`
2. **PR watcher** (rendered from `assets/monitor-github-prs.sh.tmpl` at init)
   - `command`: `$MEM/monitor-prs.sh`
   - `description`: e.g. `<project name> loop-owned PRs (merge/close/comments/CI)`
   - `persistent`: `true`, `timeout_ms`: `3600000`

The PR watcher polls every PR in `.pr-feedback-state` via `gh` and emits a line the moment a PR is **MERGED** (→ move the issue to the Merged state, clean the registry, pull the next task), **CLOSED**, or changes comments/reviews/CI. Save both `task_id`s.

## Step 4 — Arm the ScheduleWakeup safety net

Call `ScheduleWakeup`:

- `delaySeconds`: `300` (5 min fallback heartbeat — Monitor is the primary wake signal; this only fires if no event arrives)
- `reason`: short one-liner like `"Monitor primary wake; 5-min safety heartbeat"`
- `prompt`: the literal `/loop` invocation from `$MEM/restart-instructions.md` (verbatim, including the leading `/loop ` prefix). This re-enters the `loop` skill which then reads `autonomous-loop.md` and runs one iteration.

## Step 5 — Confirm

Print a one-line confirmation referencing the monitor task_id and the wakeup target time. Do not print the full prompt — it's already in `restart-instructions.md`.

## Idempotency

If `start` is invoked while a previous Monitor is still running for this project, stop the old one first (`TaskStop <old_task_id>`) so we don't have duplicate pollers spamming events.

To find the old task id: search session task list for any task whose command starts with `$MEM/monitor.sh`.
