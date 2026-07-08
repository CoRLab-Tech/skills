---
name: feedback-watch-pr-comments
description: "Actively track every PR the loop opened; new review comments / requested changes take priority over new tasks"
metadata:
  type: feedback
---

The loop owns its PRs until they merge. Every tick starts with a sweep of the still-open PRs it previously opened: new review comments, requested changes, and newly-red CI checks are detected and addressed **before** pulling a new task from the tracker.

**Why:** An unanswered review comment stalls the human reviewer and freezes the whole task — the loop happily churning out new PRs while old ones rot in "changes requested" defeats the purpose. Feedback on in-flight work is always higher-value than starting new work.

**How to apply:**
- The sweep runs over the loop's **PR registry**: `.pr-feedback-state` in the project memory dir. This file is the canonical registry schema — every other rule references it, none redefine it. An entry is **born at pull time** (issue key + branch + the loop's own status transitions, so a crash before any PR exists still leaves a trail for reconcile — [[feedback-status-mirrors-work]]); the repo slug + PR number are added at `gh pr create` time, plus the per-PR last-seen feedback timestamp and a `blocked` flag set when [[feedback-fail-gracefully-timebox]] parks the PR. Sweep each registered PR with explicit repo scoping — `gh pr view <num> -R <owner>/<repo> --comments` and `gh api repos/<owner>/<repo>/pulls/<num>/reviews` — for feedback newer than last-seen, then update the timestamp. Bare `gh pr list --author @me` is NOT the source of truth: it scopes to the cwd's repo (wrong for multi-repo projects, where the registry spans ALL service repos) and under the human's credentials it includes their personal PRs.
- Every comment's attachments are actually viewed — images via Read, videos via ffmpeg frame extraction — per [[feedback-read-media-in-comments]]. Never respond to a comment whose media wasn't looked at.
- **Requested changes** → transition the ticket back to **In Progress** and the PR back to draft first ([[feedback-status-mirrors-work]]); if the entry carries the `blocked` flag (a fail-gracefully park being resumed by human feedback), clear it as part of the In Progress transition. Implement on the same PR branch, push, reply to each comment concretely, then flip both forward — `gh pr ready` + review status + re-request review — once gates are green. "Gates green" on a fix round means the TARGETED re-gate ([[feedback-targeted-regate-on-fixes]]): full suite + only the blocked review gates scoped to the fix delta + full-diff QA/security verdicts — not a mechanical full re-run.
- **Questions** → answer as a PR comment, specifically — no boilerplate.
- While addressing feedback, listen for the **generalizable**: a comment that states a convention, a preference, or a recurring nit is a lesson, not just a fix — distill it into a feedback memory per [[feedback-continuous-learning]].
- **Approved + green CI + no unresolved threads** → merge it yourself per [[feedback-merge-on-approval]].
- Also check registered PRs whose state turned **merged** (`gh pr view <num> -R <owner>/<repo> --json state,mergedAt`): their tracker issues transition to "Merged"/closest completed state per [[feedback-ticket-done-on-merge]].
- Priority order per tick: red CI on an open PR ([[feedback-regression-is-blocker]]) > requested changes > unanswered questions > approved-PR merges > merged-PR ticket transitions > new ready task.
- Merged or closed PRs leave the watch list once their ticket transition is done; prune their entries from the state file.
