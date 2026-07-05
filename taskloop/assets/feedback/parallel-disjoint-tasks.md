---
name: feedback-parallel-disjoint-tasks
description: When the ready queue holds FILE-DISJOINT tasks, implement them in parallel — one agent per task in an isolated git worktree; sequential only for tasks sharing files
metadata:
  type: feedback
---

The loop is not limited to one task at a time. When several ready tasks are **disjoint in the files
they touch**, pull them together and implement each in its own **parallel agent** inside an
**isolated git worktree** (own branch from fresh origin/main, own dev server on a unique port, own
browser verification, own evidence commits). The orchestrating loop opens the PRs, does the tracker
transitions, and registers them in `.pr-feedback-state`.

**Why:** sequential work on independent tasks wastes wall-clock and the owner's review batching.
The real constraints are (a) merge conflicts — tasks sharing hot files (an `index.html`, a shared
stylesheet) MUST stay sequential, that is what caused the conflicts the first time; and (b) the
WIP cap on open PRs, which bounds how many parallel agents may launch.

**How to apply:**
- Before pulling, partition the ready queue by touched-file overlap (infer from the task
  descriptions + the repo layout). Launch one worktree agent per disjoint task, up to
  `WIP cap − currently-open loop PRs`.
- Each agent gets the FULL discipline in its prompt: branch from origin/main, minimal diff, tests +
  full suite, browser verification with screenshots committed in-branch (gitignored runtime files
  like `.env` must be copied into the worktree; the server needs a unique PORT), secrets scan,
  clean commit message with no AI attribution, push the branch, and NO PR / tracker / deploy
  actions of its own.
- The orchestrator verifies each agent's return honestly (evidence exists, suite green), then opens
  the PR with the agent's evidence embedded (`![](…/raw/<branch>/…)`), transitions the issue, and
  registers the PR for the watcher.
- Overlapping tasks stay sequential; when in doubt about overlap, treat as overlapping.
