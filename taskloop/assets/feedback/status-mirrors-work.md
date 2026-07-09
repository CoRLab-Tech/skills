---
name: feedback-status-mirrors-work
description: "The ticket status is a live mirror of what the loop is doing RIGHT NOW — working = In Progress, awaiting review = In Review, can't proceed = Blocked, merged = Merged. A status that lies is a bug"
metadata:
  type: feedback
---

The tracker board is the owner's window into the loop. At every moment, every loop-owned ticket's status must state what is actually happening to it — not what happened at the last milestone. **Working on it — for ANY reason — means In Progress.** A ticket sitting in "In Review" while the loop is actively pushing commits to its PR is a lie on the board.

**The mapping, absolute:**

| Reality | Status |
|---|---|
| The loop is writing code for it — first implementation, rework after review comments, fixing red CI, resolving a merge conflict | **In Progress** |
| PR open, all gates green, waiting on a human | **In Review** |
| The loop cannot proceed — timebox exhausted, missing decision/credential, unresolvable ambiguity | **Blocked** |
| PR merged | **Merged** / closest completed state |

**Why:** the owner triages by the board. "In Review" while rework is happening makes them re-review a moving target; "In Progress" on an abandoned task makes them wait on nothing. Every stale status costs the owner a wrong decision.

**How to apply:**
- **Rework transitions both ways:** when the PR sweep picks up requested changes or a red check on an in-review ticket, transition it **back to In Progress AND convert the PR back to draft (`gh pr ready --undo`) BEFORE touching code**. When the rework is pushed, gates are green again, and review is re-requested → flip both forward: `gh pr ready` + **In Review** (and reply to the comments per [[feedback-watch-pr-comments]]). Every rework cycle repeats this — no exceptions for "small fixes".
- **The PR's draft flag mirrors the same truth:** every PR is BORN a draft (`gh pr create --draft`) and stays draft while gates run; it flips to ready-for-review in the same atomic step that moves the ticket to the review status — never before, never separately. Invariant: a non-draft loop-owned PR ⟺ its ticket sits in the review status ⟺ all gates were green at the flip.
- **Blocked is a real state, not a comment:** when [[feedback-fail-gracefully-timebox]] releases a task, it goes to the workflow's **Blocked** state. `init` ensures the state exists (Plane: `create_state(name="Blocked", color="#EF4444", group="backlog")` — the backlog group keeps it out of the loop's queue and inside the human triage lane). Only when the tracker genuinely can't hold a Blocked state, fall back to Backlog + the `BLOCKED:` comment.
- **One truthful transition per change, idempotent.** Don't flap statuses within a tick; transition when reality changes, once.
- **Reconcile at start:** the registry (`.pr-feedback-state`, [[feedback-watch-pr-comments]]) gains an entry at PULL time — issue key, branch, and each loop-made transition — not just at PR creation. On restart: (a) any registry ticket sitting In Progress with no active agent and no open PR → move to Blocked with a note; (b) for every registered OPEN PR, compare `isDraft` against the ticket status — a half-flipped step 11 (ready PR + ticket not in review, or draft PR + ticket in review) is repaired by completing the missing half when the gates were green, else flipping both back. Tickets absent from the registry were never the loop's — never touch tickets a human moved.
- The status transition is part of the same atomic step as the action that caused it — a rework that starts without the In Progress transition is as unfinished as a PR without its ticket comment ([[feedback-draft-until-gated]]).
