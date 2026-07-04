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
- Transition via the provider's transition recipe and post a closing comment on the issue: `PR merged: <url>` (+ merge commit SHA).
- If the tracker issue was already moved manually, skip silently — never fight a human's transition.
- Merged-PR entries are then pruned from `.pr-feedback-state`.
