---
name: feedback-fail-gracefully-timebox
description: "A task that can't be completed after ~3 honest attempts is surfaced and released — never infinite retries, never force-pushed 'solutions', never broken code shipped"
metadata:
  type: feedback
---

Some tasks won't converge: the issue is underspecified, the tests can't pass without a decision only a human can make, the environment is missing something. After **~3 honest attempts** (or the equivalent timebox) at making the gates pass, the loop stops grinding, documents, releases the task, and moves on. It never ships code that doesn't pass the gates just to "finish".

**Why:** An autonomous loop's worst failure modes are silent: burning hours re-attempting the same wall, or "solving" it by weakening tests / skipping gates / force-pushing something that compiles. A loud, well-documented failure costs one issue; a silent bad merge costs a production incident plus the trust in the loop.

**How to apply:**
- Count an "attempt" as a full implement→verify cycle that ends with a failing gate (tests, CI, review findings, QA verdict). After the 3rd, stop.
- Post a comment on the tracker issue: what was tried (each approach, one line), the exact blocker (failing test output, missing credential, ambiguous requirement), and what's needed to unblock (a decision, an env var, a clarification).
- Transition the issue to the **Blocked** state with the `BLOCKED:` comment — `init` guarantees the state exists ([[feedback-status-mirrors-work]]; Plane: created in the `backlog` group so it sits in the human triage lane, outside the loop's queue) — on a project initialized before this rule, create it NOW with the init recipe. Only when the tracker genuinely cannot hold a Blocked state (creation forbidden or unsupported), fall back to **Backlog** + the `BLOCKED:` comment. **Never release it into the ready status**: the ready status is the loop's own pull queue, so releasing there re-enqueues the stuck task for the loop itself and recreates the infinite retry this rule exists to prevent. Do NOT leave it silently parked in "In Progress" either — In Progress means someone is working on it, per [[feedback-status-mirrors-work]]. A human moving it back to ready later is the explicit retry signal.
- Belt-and-suspenders at pull time: skip any ready issue whose most recent comment is the loop's own `BLOCKED:` note with no human activity after it — the human hasn't re-triaged, so nothing changed.
- Clean up: if no PR was opened, delete the local branch. If **any** PR exists — draft or not — convert it to draft (`gh pr ready <num> --undo`), post the blocker note on it, and mark its registry entry `blocked` (that flag is what excludes it from the WIP cap — [[feedback-wip-limit-open-prs]]); never leave a released task's PR in a non-draft state where it looks like it awaits review (or worse, gets auto-merged — merge-on-approval must never touch drafts).
- If the released task is later re-triaged and re-pulled, **resume** the existing PR branch (rebase onto fresh `origin/<default>`, clear the registry `blocked` flag) — never open a second PR for the same issue. The PR goes ready-for-review only through the normal lifecycle: all gates green, together with the ticket transition.
- **Forbidden shortcuts, always:** deleting/weakening failing tests to pass ([[feedback-new-code-needs-tests]]), skipping any gate, force-pushing over shared history, or pushing directly to the default branch — all work reaches the default branch via PR ([[feedback-pull-main-each-task]]).
- Then pick the next ready task — one stuck issue must not stall the queue.
