---
name: feedback-gates-run-foreground
description: "Subagents run their gate suites as SEQUENTIAL FOREGROUND commands — a subagent that backgrounds a gate and ends its turn 'waiting' is a dead run that ships nothing"
metadata:
  type: feedback
---

Every long-running check inside a spawned agent — test suite, lint, typecheck, build, browser verification — runs as a **sequential foreground command**: the agent waits for each to finish and reads its output before moving on. A subagent must never launch a gate with `run_in_background`, a monitor, or a detached shell and then end its turn "until it reports green".

**Why:** learned from a 13-agent parallel wave — several agents backgrounded their suites ("I'll commit when it's green") and then STOPPED. A subagent's background children do not reliably survive the end of its turn or re-wake it; the runs died silently, no branch was pushed, and the orchestrator had to resurrect each one by hand. Slow-but-finished beats fast-but-dead every time.

**How to apply:**
- Every implementation-agent prompt the loop writes ([[feedback-parallel-disjoint-tasks]]) mandates it explicitly: gates as sequential foreground Bash calls, no `run_in_background`, no monitors, no "waiting" as a final state. Slowness under parallel load is expected and fine — raise the command timeout, don't background.
- The only valid final message from an implementation agent is the completed report: suite output, evidence paths, pushed branch name. "Suite still running" is not a report; it is a failed run.
- The orchestrator treats an agent that returned while work was still pending as failed and re-runs it — it never waits on a subagent's orphaned background task.
- Backgrounding stays legitimate for the MAIN loop session itself (Monitors, PR watcher) — the harness re-wakes the main session; it does not re-wake a finished subagent.
