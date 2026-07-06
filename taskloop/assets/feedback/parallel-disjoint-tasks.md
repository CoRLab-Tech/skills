---
name: feedback-parallel-disjoint-tasks
description: When the ready queue holds FILE-DISJOINT tasks, implement them in parallel — one agent per task in an isolated git worktree; sequential only for tasks sharing files
metadata:
  type: feedback
---

The loop is not limited to one task at a time. When several ready tasks are **disjoint in the files
they touch**, pull them together and implement each in its own **parallel agent** inside an
**isolated git worktree** (own branch from fresh origin/main, own dev server on a unique port, own
browser verification, own evidence commits). The orchestrating loop opens the PRs **as drafts**, runs the
step-10 gates per PR, performs the step-11 atomic flip per issue, and registers everything in `.pr-feedback-state`.

**Why:** sequential work on independent tasks wastes wall-clock and the owner's review batching.
The real constraints are (a) merge conflicts — tasks sharing hot files (an `index.html`, a shared
stylesheet) MUST stay sequential, that is what caused the conflicts the first time; and (b) the
WIP cap on open PRs, which bounds how many parallel agents may launch.

**How to apply:**
- The partition comes from the queue triage plan: read each ready ticket's `LOOP-PLAN` marker
  ([[feedback-queue-triage-plan]]) — a shared `group` id means the triage already established
  file-disjointness. Only partition ad hoc (descriptions + repo layout) when no plan exists yet,
  and record the result by running the triage. Launch one worktree agent per task in the group,
  up to `WIP cap − currently-open loop PRs`, respecting `order` and unmerged `depends-on`.
- Each agent is launched with the model/effort its ticket's `tier` prescribes ([[feedback-model-effort-routing]]); verdict work stays with the orchestrator on the top model. Each agent gets the FULL discipline in its prompt: branch from origin/main, minimal diff, tests +
  full suite, browser verification with screenshots committed in-branch (gitignored runtime files
  like `.env` must be copied into the worktree; the server needs a unique PORT), secrets scan,
  clean commit message with no AI attribution, push the branch, and NO PR / tracker / deploy
  actions of its own.
- The orchestrator verifies each agent's return honestly (evidence exists, suite green), then opens
  the PR **as a draft** (`gh pr create --draft`) with the agent's evidence embedded
  (`![](…/raw/<branch>/…)`), registers it for the watcher, runs the step-10 gates on it, and only
  when all gates are green performs the step-11 atomic flip for that issue (gh pr ready + ticket
  comment + review transition) — never "open and transition" in one motion.
- Overlapping tasks stay sequential; when in doubt about overlap, treat as overlapping.
