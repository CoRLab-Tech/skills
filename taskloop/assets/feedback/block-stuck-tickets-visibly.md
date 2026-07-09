---
name: feedback-block-stuck-tickets-visibly
description: "A ready or in-review ticket the loop cannot process gets an explicit WHY comment and moves to Blocked — never left sitting silently in the queue while the loop idles"
metadata:
  type: feedback
---

**Never let a ticket sit silently stuck.** If the loop cannot process a ticket right now — it is blocked on an owner decision, needs an external asset or credential the loop cannot obtain, or is otherwise unactionable — the loop MUST, in the same tick:

1. **Post a comment on the ticket** stating exactly WHY it cannot be processed: the concrete blocker plus what would unblock it.
2. **Move the ticket to `Blocked`** (the state `init` guarantees exists).

The owner then sees the situation deliberately **in the tracker** — "this ticket is blocked because X, needs Y from you" — instead of the loop quietly idling while tickets pile up in the queue.

**Why:** an owner watching a full ready queue and a silent loop has no way to tell "the loop is stuck" from "the loop is broken". Chat is not the tracker: a blocker announced in chat scrolls away, while a blocker recorded on the ticket with the ticket in `Blocked` keeps the board honest and gives the owner an explicit, actionable signal.

**How to apply:**

- Each idle or sweep tick, for every ready / in-review ticket the loop is NOT taking, decide *why*. If the reason is "blocked or unactionable" (not merely "lower priority, will get to it") → comment the concrete reason and move to `Blocked`. If it is genuinely just next in line and doable, take it — never block doable work.
- The comment names the blocker AND the unblock action. "Blocked: needs the design assets exported into the repo, or an API token and file key in env — I cannot reach the design tool headless." "Blocked: the email-provider decision is not recorded in STACK.md — owner call."
- Do NOT block a ticket that is merely waiting on one of the loop's own in-flight PRs. That is normal pipeline sequencing, and it is usually stackable ([[feedback-continuous-flow-from-ready]]). `Blocked` is for things that need the OWNER or an external unblock.
- When the blocker clears — the owner records the decision, drops the asset, merges the dependency — move the ticket back to the ready status and take it.
- Pairs with [[feedback-never-self-halt-loop]] (idle → keep moving and surface blockers, never shut down) and [[feedback-fail-gracefully-timebox]] (a task the loop tried and could not land parks the same visible way).
