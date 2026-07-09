---
name: feedback-pr-registry-race
description: "Parallel agents appending to .pr-feedback-state concurrently corrupt it — the orchestrator owns the registry and rebuilds it race-free from `gh pr list` on every sweep instead of trusting agent writes"
metadata:
  type: feedback
---

When many worktree agents finish near-simultaneously and each appends its PR to `.pr-feedback-state`, the concurrent JSON read-modify-writes race. The observed corruption is the whole `{"prs":[...]}` object getting wrapped in an extra list — `[ {"prs":[...]} ]` — which then throws on the next read, and the PR watcher goes blind: no merge events, no comment events, tickets stranded in review.

**Why:** the registry is a single JSON file with no locking. N agents doing `read → append → write` interleave and clobber each other. The failure is silent until something downstream tries to parse it.

**How to apply:**

- **The orchestrator owns the registry. Rebuild it authoritatively from `gh pr list` on every sweep** rather than trusting agent appends. This is race-free and self-healing, and it naturally drops merged and closed PRs from the watch set:

  ```bash
  gh pr list --author <me> --state open --json number,headRefName,isDraft --limit 100
  ```

  Extract the issue key from the **branch name** (the loop's branch convention embeds it), not the PR title — titles routinely omit the key. Write `{"prs":[{repo,number,issue,branch,blocked},...]}`. In a monorepo, run the listing once per target repo and concatenate.
- Agent-side appends may stay — they are harmless once the orchestrator overwrites — but never DEPEND on them for correctness.
- Preserve the `blocked` flag across a rebuild: it lives only in the registry ([[feedback-fail-gracefully-timebox]] parks are excluded from the WIP cap), so carry it forward from the previous registry by PR number rather than dropping it.
- The PR watcher (`monitor-prs.sh`) tolerates a corrupt registry by unwrapping the known bad shape and de-duplicating entries, and emits a `registry corrupt` line so the loop rebuilds. Treat that line as a rebuild trigger, not a warning to ignore.
- Shell gotchas when scripting the rebuild: `cmd | python3 - arg <<'PY'` makes the heredoc win stdin over the pipe — write the `gh` output to a temp file and pass its path as argv instead of piping. And do not put backslash-escaped quotes inside a Python f-string (`f"{o[\"k\"]}"` is a SyntaxError).

Related: [[feedback-watch-pr-comments]], [[feedback-wip-limit-open-prs]], [[feedback-reconcile-tracker-vs-github]].
