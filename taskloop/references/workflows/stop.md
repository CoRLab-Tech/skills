# Stop workflow

Cleanly tear down the autonomous loop for the current project. The loop will not resume until the user runs `/taskloop start` again.

## Step 1 — Find the running monitor

Look up the active background task whose command is `~/.claude/projects/<slug>/memory/monitor.sh`. Use the harness's task list — search by the command string.

If none is running, just print a no-op confirmation and exit.

## Step 2 — Stop the monitor

Call `TaskStop` with the task_id found in step 1.

## Step 3 — Cancel any pending ScheduleWakeup

The harness doesn't expose a "cancel pending wakeup" tool. Instead, do **not** call `ScheduleWakeup` this turn. The previously-scheduled one will still fire once, but when it does, the loop will see no Monitor running and the user will see explicit silence (the next tick's "queue empty" check still runs, but with no monitor it can't re-arm itself).

Alternative: tell the user that one final wakeup may fire and they can ignore it (or call `/taskloop stop` again at that point).

## Step 4 — Confirm

```
✅ taskloop stopped for <project name>
   Monitor task <id> terminated.
   No further wakeups will be armed. (One pending wakeup may still fire once.)
   Resume with `/taskloop start`.
```

## Notes

- Do not delete `$MEM` contents on stop. The user might want to resume later.
- Do not unset env vars or modify `.env`.
- This workflow is fast (no I/O beyond `TaskStop`). Safe to call multiple times.
