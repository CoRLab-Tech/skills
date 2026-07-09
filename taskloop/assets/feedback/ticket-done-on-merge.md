---
name: feedback-ticket-done-on-merge
description: "When a loop-owned PR merges, transition its tracker issue to \"Merged\" — or the closest completed state the workflow has"
metadata:
  type: feedback
---

The tracker must mirror reality: the moment a loop-owned PR is merged — whether the loop merged it ([[feedback-merge-on-approval]]) or a human did — the linked issue transitions out of the review status into **"Merged"**, or, when the workflow has no such state, the **closest completed state** (typically `Done`).

**Why:** An issue sitting in "In Review" after its PR merged is a lie the whole team reads. Closing the tracker loop automatically keeps the board truthful without anyone sweeping it by hand.

**How to apply:**
- The per-tick PR sweep ([[feedback-watch-pr-comments]]) checks each PR in the loop's registry (`.pr-feedback-state`, which maps repo + PR number → issue key) for a state change to merged: `gh pr view <num> -R <owner>/<repo> --json state,mergedAt,url`. The registry entry names the issue directly — no fuzzy cross-referencing needed.
- Resolve the target state once per project by enumerating the provider's states: prefer a state named `Merged` (case-insensitive); otherwise pick the completed-group state (`Done` on Linear/Plane stock workflows, the done-category status on Jira). Cache the choice.
- **Where a `Merged` state exists, stop there.** Do not push the ticket on to `Ready for QA`, `Deployed`, or `Done` — those belong to the owner's acceptance flow, and a loop that claims them takes a decision that is not its to take. Only fall back to a completed state when the workflow has no `Merged`.
- Transition via the provider's transition recipe and post a closing comment on the issue: `PR merged: <url>` (+ merge commit SHA).
- If the tracker issue was already moved manually, skip silently — never fight a human's transition.
- Merged-PR entries are then pruned from `.pr-feedback-state`.
- The merge moment is also the retro moment: 30 seconds on what review caught that the gates missed, distilled into a feedback memory when it would change future behavior — [[feedback-continuous-learning]].

**Detection is the loop's own job.** The PR watcher (`monitor-prs.sh`) emits the merge event — the loop
reacts to it autonomously: transition the issue, clean `.pr-feedback-state`, delete the head branch if
the repo doesn't auto-delete (`gh api -X PATCH repos/<owner>/<repo> -f delete_branch_on_merge=true` is
set at init so it normally does), and immediately pull the next ready task. NEVER wait for the owner to
say "merged" in chat — the owner communicates only via PR/tracker comments.
