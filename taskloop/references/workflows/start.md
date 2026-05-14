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
rm -f "$MEM/.monitor-state"
```

Removing the state file forces the first tick to re-emit the current actionable queue, so Claude sees what's pending immediately.

## Step 2 — Verify the queue once

Read the provider name from `$MEM/.env` (presence of `LINEAR_API_KEY` vs `JIRA_API_TOKEN` decides). Run the appropriate one-shot check from the provider doc:

- **Linear** — see "Verify Todo queue" in `references/providers/linear.md`
- **Jira** — see "Verify Ready queue" in `references/providers/jira.md`

If the queue has items, **start processing the first one immediately** following the spec in `$MEM/autonomous-loop.md`. If empty, just confirm "Monitor pornit, coadă goală" (or English equivalent) and continue to Step 3.

## Step 3 — Arm the Monitor

Call the harness's `Monitor` tool:

- `command`: `$MEM/monitor.sh` (absolute path)
- `description`: e.g. `<project name> ready queue`
- `persistent`: `true`
- `timeout_ms`: `3600000` (1 hour; harness max)

Save the returned `task_id`. That's the wake signal for the loop. Each `<task-notification>` event from this monitor wakes the loop with one line per change in the actionable queue.

## Step 4 — Arm the ScheduleWakeup safety net

Call `ScheduleWakeup`:

- `delaySeconds`: `1500` (25 min fallback heartbeat — Monitor is the primary wake signal; this only fires if no event arrives)
- `reason`: short one-liner like `"Monitor primary wake; 25-min safety heartbeat"`
- `prompt`: the literal `/loop` invocation from `$MEM/restart-instructions.md` (verbatim, including the leading `/loop ` prefix). This re-enters the `loop` skill which then reads `autonomous-loop.md` and runs one iteration.

## Step 5 — Confirm

Print a one-line confirmation referencing the monitor task_id and the wakeup target time. Do not print the full prompt — it's already in `restart-instructions.md`.

## Idempotency

If `start` is invoked while a previous Monitor is still running for this project, stop the old one first (`TaskStop <old_task_id>`) so we don't have duplicate pollers spamming events.

To find the old task id: search session task list for any task whose command starts with `$MEM/monitor.sh`.
