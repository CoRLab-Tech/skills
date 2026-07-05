---
name: feedback-wip-limit-open-prs
description: "Cap the loop's open unmerged PRs (default 3) — when the cap is hit, service the review pipeline instead of pulling new tasks"
metadata:
  type: feedback
---

The loop holds at most **3 open PRs** awaiting human review (override per project only if the user explicitly raises it). At the cap, the loop does not pull new ready tasks; it services the pipeline it already opened — feedback, CI, approvals, merges — until a slot frees up.

**Why:** Review bandwidth is the bottleneck, not implementation speed. Ten parallel open PRs means: each branched from a `main` that lacks the others' changes (conflict cascade on merge), reviewers skimming instead of reviewing, and stale diffs by the time anyone looks. A small WIP cap keeps every open PR fresh, conflict-free, and actually reviewed — that's what "well reviewed" means operationally.

**How to apply:**
- Before pulling a new ready task, count open loop-owned PRs from the **registry** (`.pr-feedback-state` — see [[feedback-watch-pr-comments]]), verifying each entry's current state with `gh pr view <num> -R <owner>/<repo> --json state,isDraft`. The registry spans ALL of the project's service repos — a bare `gh pr list --author @me` counts only the cwd's repo and the human's own PRs, both wrong. At ≥ the cap, skip the pull.
- At the cap, spend the tick on the pipeline instead: the full sweep of [[feedback-watch-pr-comments]] — address feedback, fix red CI, merge what's approved ([[feedback-merge-on-approval]]), transition merged tickets ([[feedback-ticket-done-on-merge]]). Merges and closes free slots naturally.
- If a full sweep freed no slot (all PRs simply await human review), post nothing, change nothing, and sleep the normal idle interval — nagging reviewers is not the loop's job.
- Draft PRs blocked per [[feedback-fail-gracefully-timebox]] count toward the cap too — they also consume reviewer attention to unblock.
- The cap is per project (per memory dir), not global across projects.
