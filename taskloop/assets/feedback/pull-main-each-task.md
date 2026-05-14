---
name: feedback-pull-main-each-task
description: "At the start of every loop iteration, fetch + branch from fresh origin/main of the target repo"
metadata:
  type: feedback
---

For each new task, the feature branch MUST be cut from a freshly-updated `origin/main` (or the repo's default branch) of the target service repo. Always `git fetch origin --quiet` and base the new branch off `origin/<default>` so the work isn't built on a stale local copy.

**Why:** Branching from whatever the local checkout happened to be on (often a previous task's feature branch or a days-old `main`) leads to noisy merge conflicts, missing fixes, and PRs that re-touch unrelated code. Always pulling fresh `origin/main` keeps every iteration's diff focused on the current task.

**How to apply:**
1. Before creating the feature branch: `git fetch origin --quiet`.
2. `git checkout -b <branch> origin/<default-branch>` so the new branch tracks fresh remote main.
3. If switching back to the default branch locally is unavoidable, run `git pull --ff-only origin <default>` first; never silently fast-forward through merges.
4. Do NOT branch from the currently-checked-out (possibly stale) branch the repo happened to be on at the start of the tick.
5. Applies on every iteration, including consecutive tasks in the same service repo.
