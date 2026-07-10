---
name: feedback-minimal-diff-scope
description: "Touch only what the task requires — no drive-by refactors, no reformatting churn, no opportunistic 'improvements'"
metadata:
  type: feedback
---

The diff contains what the task requires and nothing else. No drive-by refactors, no reformatting of untouched code, no renaming "while we're here", no dependency bumps the task didn't ask for, no deleting code that merely *looks* dead. Work the loop discovers but wasn't asked to do goes to the backlog, not into the diff.

**Why:** Every line beyond the task's scope is unreviewed risk wearing the task's approval: it can break functionality nobody asked to touch, it bloats review until reviewers skim, and it makes `git bisect`/reverts imprecise. Scope discipline is the single cheapest protection for existing functionality.

**How to apply:**
- Before committing, read the full diff (`git diff origin/<default>`) hunk by hunk and justify each against the issue. Anything that doesn't serve the task: revert it.
- Formatting: match the file's existing style; never run a formatter over whole files unless the repo's hooks do it anyway. If an editor/hook reformatted untouched regions, restore them.
- Discovered problems (dead code, missing tests, a needed refactor, an adjacent bug) → mirror to the backlog via the [[feedback-todo-opens-backlog-task]] mechanism instead of fixing inline. Exception: something the task's own correctness depends on — then it's in scope, and the PR body says why.
- Public contracts (API shapes, exported signatures, DB schemas, event payloads, config formats) change only when the task explicitly requires it; when they do, the PR body carries a **breaking-change note** naming the consumers checked.
- Refactor-then-fix is fine when genuinely needed — but as **separate commits** within the PR (mechanical refactor commit + behavior commit) so review and revert stay surgical.
- One standing exemption: the project's evidence directory, `<evidence-dir>/<issue-key>/` (set at init, default `docs/evidence` — the same path the pr-visual-evidence guard checks) — the PR's visual evidence ([[feedback-ui-verification-and-evidence]]) is mandated by another rule and is never scope creep.
