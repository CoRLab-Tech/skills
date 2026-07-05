---
name: feedback-loop-autonomy-pr-plane-only
description: The loop is an independent instrument — it detects PR merges/comments/CI itself and self-triggers the next task; the owner communicates ONLY via PR + tracker comments
metadata:
  type: feedback
---

The loop must NEVER depend on the owner announcing anything in chat ("merged", "commented", "CI is
red"). Two persistent monitors are its senses: the tracker ready-queue poller (`monitor.sh`) and the
PR watcher (`monitor-prs.sh`, polls every registry PR via `gh` for state/comments/reviews/CI deltas).

**Why:** the owner works asynchronously in GitHub and the tracker. A loop that waits for chat pings is
not autonomous — it strands merged PRs, unprocessed feedback, and an idle queue. This rule exists
because it happened: the owner had to say "merged" twice before the loop reacted.

**How to apply:**
- On a **MERGED** event: move the issue to the Merged state ([[feedback-ticket-done-on-merge]]), drop
  the PR from `.pr-feedback-state`, verify the head branch was auto-deleted
  (`delete_branch_on_merge=true` is set at init; delete manually if not), then IMMEDIATELY pull the
  next ready task — no pause, no ping.
- On a **comment/review/CI** event: service it before new work ([[feedback-watch-pr-comments]],
  [[feedback-regression-is-blocker]]).
- All status the owner needs goes INTO the PR (body, comments, evidence) and the tracker issue
  (comments, state transitions) — chat is not a channel the loop relies on.
