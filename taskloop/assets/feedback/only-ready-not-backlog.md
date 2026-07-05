---
name: feedback-only-ready-not-backlog
description: "The loop must act only on the explicit `ready` status — never the triage backlog"
metadata:
  type: feedback
---

The autonomous loop must **only act on issues whose status is the explicit `ready` status** (Linear: `Todo`; Plane: `$PLANE_READY_STATUS`, default `Todo`; Jira: whatever `JIRA_READY_STATUS` is configured to). Do not pick up `Backlog` issues, even though they're technically unstarted. Skip them silently — they belong to the user's triage queue, not the loop's work queue.

**Why:** Backlog means "I haven't decided yet whether this is real work"; the explicit ready status means "yes, please start this." Treating backlog as actionable jumps the gun on issues the user is still triaging, and frequently picks up tickets that turn out to be duplicates, no-ops, or stale.

**How to apply:**
- In every provider query the loop makes (start verify, monitor poll, loop tick), filter strictly on the configured ready status name. Don't fall back to broader buckets like Linear's `unstarted` type (which includes `Backlog`).
- The polling `monitor.sh` script must use the same filter — if it currently emits backlog rows as actionable, fix it.
- When the user says "all tasks" or "everything", still respect this rule unless they explicitly override for that turn.
- If a backlog issue is referenced by id (user pastes a tracker URL), it's OK to act — the explicit reference IS the triage signal.
- Provider-specific reminders:
  - **Linear**: filter on `state.name == "Todo"`, not on `state.type == "unstarted"`.
  - **Plane**: filter on the resolved `$PLANE_READY_STATUS` state **UUID** (PQL `state = "<uuid>"`) or the expanded `state.name` — never on the `unstarted` group, which can include more states, and never Backlog (new work items default there).
  - **Jira**: use `$JIRA_READY_STATUS` verbatim in the JQL `status = "..."` clause.
