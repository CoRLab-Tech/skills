---
name: feedback-never-self-halt-loop
description: "The loop halts ONLY on the owner's explicit 'stop' — never self-stop on 'idle / nothing actionable', never report PR or queue state from memory, and self-heal a monitor that proved it missed an event"
metadata:
  type: feedback
---

**The loop halts ONLY when the owner says `stop`.** Staying alive is the default. The loop is designed to self-trigger and keep watching; stopping it is the owner's decision, not the loop's.

**Do NOT call `ScheduleWakeup stop:true` on your own judgment.** The generic `/loop` escape hatch ("further iterations can't make progress → stop") does **not** apply to this taskloop — idle is a normal state, not a terminal one. When there is nothing to pull (everything in review, gated on the owner, or blocked on an external decision):

- keep the fallback heartbeat ALIVE (re-arm `ScheduleWakeup` at the cadence in `restart-instructions.md`),
- keep the persistent queue + PR Monitors running,
- and just re-sweep quietly each tick.

**Never report or act on a REMEMBERED PR/queue count.** At the START of every turn, re-run `gh pr list --author <me> --state open` and a fresh tracker fetch, and speak only from what you verify.

**Why:** on a long autonomous run the loop called `stop:true` because the board looked idle (all remaining work gated on the owner). That killed the fallback heartbeat, and the stale Monitor never fired on the owner's merges — so the loop sat blind for hours repeating "3 PRs await your merge" while those PRs had already been merged. Two mistakes compounded: self-halting a loop that is the owner's to halt, and trusting memory over a fresh sweep.

**Monitor self-heal — repair a dead monitor, don't just compensate for it.** The fresh sweep every tick is the GUARANTEE (nothing is missed even if a monitor dies); the monitor is the RESPONSIVENESS layer, and it can silently go stale. Each heartbeat tick, check monitor liveness:

- Compare `.pr-monitor-state` / `.monitor-state` mtime against the expected cadence. If a monitor's state is stale beyond a generous threshold **AND** the tick's fresh sweep surfaces an event it should have fired on but didn't (a proven miss), that monitor is dead → **re-arm it**.
- **Single-instance invariant:** re-arm means tear down the stale monitor task, then start exactly ONE fresh one. Never just add a second — two monitors both self-triggering is its own failure. Only the loop-owning instance does this; a helper instance must never arm a competing monitor.
- Staleness alone is not death (no events → no writes is legitimate). Use the proven-miss signal. The sweep-every-tick floor holds regardless; self-heal just restores the fast path.

**Agent liveness is not output-file mtime.** A running implementation agent's task output file can sit UNCHANGED for 20–30 minutes while it is perfectly healthy — a single long foreground gate (a full test run plus a build, or a container verify) does not stream to the agent's transcript until the command returns. Judge a *running* agent (no completion notification yet) by **live evidence, not mtime**: `ps aux` for a test/build/container process under its worktree, container health, and `git -C <worktree> log`/`status` for new commits. Only treat it as stuck if, across TWO ticks, there is NO live build/test process AND no new commit AND no PR. A `SendMessage` that reports "queued for delivery at next tool round" confirms it is live (an already-stopped agent would say "resumed"). The completion notification remains the authoritative done-signal; a DEAD RUN is specifically an agent that COMPLETED without a ready PR or review transition — that one you resume.

**How to apply:**

- Idle tick → re-arm the heartbeat, re-sweep, and check monitor liveness (self-heal if a monitor proved it missed an event). NEVER `stop:true` unless the owner typed `stop`.
- First action of any loop turn = fresh `gh pr list` + tracker fetch. Reconcile any newly-merged PR before saying anything ([[feedback-reconcile-tracker-vs-github]]).
- If the owner nudges the loop and nothing changed, that is fine — verify, report the *verified* state tersely, keep the heartbeat, do not shut down.
- Nothing actionable is not silence: every ticket the loop is not taking gets a reason ([[feedback-block-stuck-tickets-visibly]]).
- Stopping is owner-only. See [[feedback-loop-autonomy-pr-plane-only]] — the loop self-detects merges and comments; the owner communicates via PR, tracker, and an explicit start/stop.
