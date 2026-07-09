---
name: feedback-todo-opens-backlog-task
description: "Every TODO left in code must open a matching backlog task in the tracker — no orphan TODOs"
metadata:
  type: feedback
---

Whenever the implementation leaves a `TODO` (or `FIXME` / `HACK`) marker in code, immediately create a corresponding task in the tracker's **backlog** describing what remains, why it was deferred, and a pointer to the code location (file:line) and the PR.

**Why:** Orphan TODOs die in the codebase — nobody sweeps them, and the context that made them obvious evaporates within days. Mirroring each one into the tracker's backlog makes the debt visible, triageable, and owned, while the code comment and the issue reference each other.

**How to apply:**
- Before committing, scan the working tree for newly added markers: `git diff origin/<default> | grep -nE '^\+.*(TODO|FIXME|HACK)'` (two-dot/worktree form — the three-dot form only sees committed changes and would miss everything pre-commit).
- For each new marker, create a **backlog** issue via the provider's create-backlog-issue recipe (see the provider doc): title distilled from the TODO text; body = context, `file:line`, and why it was deferred. The PR doesn't exist yet at this point — after `gh pr create`, post the PR URL onto the created issue via the provider's post-comment recipe.
- Write the created issue key back into the code comment — `TODO(PROJ-123): ...` — so code and tracker stay linked; amend before pushing.
- Backlog ONLY — never the ready status. A human triages priority; the loop must not feed itself work ([[feedback-queue-triage-plan]]).
- Pre-existing TODOs in untouched code are out of scope — only markers the current diff introduces.
