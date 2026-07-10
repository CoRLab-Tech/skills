# Stop workflow

Cleanly tear down the autonomous loop for the current project. The loop will not resume until the user runs `/taskloop start` again.

## Step 1 — Record the owner's decision

```bash
SLUG=$(pwd | sed 's|[^A-Za-z0-9]|-|g')
MEM="$HOME/.claude/projects/${SLUG}/memory"
touch "$MEM/.owner-stop"
```

The marker is what lets `hook-loop-guards` (guard 5, never-self-halt) tell an owner-ordered stop apart from the loop self-halting: with it present, a final `ScheduleWakeup stop:true` is allowed; without it, denied. `start` removes the marker.

## Step 2 — Find and stop ALL loop-owned monitors

The loop owns up to **three** background tasks, and stop must tear down every one — a surviving PR watcher keeps waking Claude on every comment, and a surviving reconciler keeps **mutating tracker state** after "stopped":

- `$MEM/monitor.sh` — the tracker-queue poller
- `$MEM/monitor-prs.sh` — the PR watcher
- `$MEM/reconcile-merged.sh` — the level-triggered reconciler (Plane/GitHub projects)

Search the harness's task list for tasks whose command starts with each path; call `TaskStop` on every match. If none is running, just print a no-op confirmation and exit.

## Step 3 — Cancel any pending ScheduleWakeup

The harness doesn't expose a "cancel pending wakeup" tool. Instead, do **not** call `ScheduleWakeup` this turn. The previously-scheduled one will still fire once; when it does, the `.owner-stop` marker permits ending the dynamic loop with `ScheduleWakeup stop:true` (guard 5 allows it), and the loop stays down.

## Step 4 — Confirm

```
✅ taskloop stopped for <project name>
   Stopped: monitor.sh <id>, monitor-prs.sh <id>[, reconcile-merged.sh <id>]
   Owner-stop marker written; no further wakeups will be armed.
   (One pending wakeup may still fire once — it will shut itself down.)
   Resume with `/taskloop start`.
```

## Notes

- Do not delete `$MEM` contents on stop. The user might want to resume later.
- Do not unset env vars or modify `.env`.
- This workflow is fast (no I/O beyond the marker and `TaskStop`). Safe to call multiple times.
