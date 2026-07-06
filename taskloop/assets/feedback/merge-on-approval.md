---
name: feedback-merge-on-approval
description: "When a loop-owned PR is approved (green CI, no unresolved threads), the loop merges it itself — no waiting for a human to click"
metadata:
  type: feedback
---

An approved PR the loop opened is the loop's to merge. During the per-tick PR sweep ([[feedback-watch-pr-comments]]), any loop-owned PR with an **APPROVED** review, **green CI**, and **no unresolved changes-requested / open threads** gets merged autonomously.

**Why:** The human already said yes — that's the approval. Making them come back later to click "merge" adds latency for zero safety: CI is green and the review is done. The loop closing its own delivery cycle is the whole point of the autonomy.

**How to apply:**
- **Loop-owned = registered, not `--author @me`.** The loop records every PR it opens (repo slug + PR number + issue key) in the project memory dir's `.pr-feedback-state` at `gh pr create` time. The sweep, the WIP cap, and this merge rule operate ONLY on registered PRs, addressed with explicit `-R <owner>/<repo>` flags. `--author @me` is a discovery aid at best — under the human's own gh credentials it returns their personal PRs too, which the loop must never touch.
- Merge only when **ALL** hold for a registered PR:
  1. `reviewDecision == "APPROVED"` (`gh pr view <num> -R <owner>/<repo> --json reviewDecision,statusCheckRollup,isDraft,headRefOid`);
  2. **the approval covers the current head** — the latest APPROVED review's `commit_id` (`gh api repos/<owner>/<repo>/pulls/<num>/reviews`) equals `headRefOid`. GitHub keeps `reviewDecision` at APPROVED after later pushes unless branch protection dismisses stale approvals — without this check the loop merges commits nobody reviewed;
  3. every status check passed ([[feedback-regression-is-blocker]]);
  4. **zero unresolved review threads** — `gh pr view --json` cannot see thread resolution; query GraphQL: `gh api graphql -f query='query{repository(owner:"<owner>",name:"<repo>"){pullRequest(number:<num>){reviewThreads(first:100){nodes{isResolved} pageInfo{hasNextPage endCursor}}}}}'` and require every `isResolved: true` across ALL pages — paginate with `endCursor` while `hasNextPage` is true; an unchecked page is an unmet condition;
  5. the PR is **not a draft** — with the draft-born lifecycle ([[feedback-status-mirrors-work]]) a draft means gates never finished (or the task was parked by [[feedback-fail-gracefully-timebox]]); either way it is not human-approved reviewable work.
- **Pre-merge recheck:** immediately before `gh pr merge`, re-fetch comments and reviews once more and abort if ANYTHING (comment, review, push) is newer than the moment the conditions above were evaluated — a human speaking up between sweep and merge always wins. Re-handle on the next pass.
- Merge with the repo's convention — check recent history (`gh pr list --state merged --limit 5 --json mergedAt,mergeCommit` / git log) for squash vs merge-commit vs rebase; default to `gh pr merge <num> --squash --delete-branch` when no convention is discernible.
- If GitHub blocks the merge (branch protection, required reviews not satisfied, merge conflict), do NOT force anything. A conflict is **trivial** only if `git merge origin/<default>` auto-resolves with no manual hunks (lockfile regeneration aside) AND the full suite is green afterwards — attempt the merge before classifying. Anything else: leave a PR comment naming the conflicting files and surface it in the tracker issue.
- After a successful merge, immediately apply [[feedback-ticket-done-on-merge]] — the tracker issue follows the PR.
- Never merge a PR that is not in the loop's registry, even if approved.
