---
name: feedback-use-project-skills
description: "When the repo/session exposes skills fit for the task (rigorous, impeccable, pixel-perfect, ...), use them — don't hand-roll around them"
metadata:
  type: feedback
---

Before implementing, check which skills are available (the session's available-skills list, the target repo's `.claude/skills/`, CLAUDE.md pointers). If a skill matches the nature of the task, USE it: `rigorous` for production code design/standards discipline, `impeccable` / `pixel-perfect-ui` for visual and UI work, `translate` for i18n strings, repo-specific deploy/test/run skills, and so on.

**Why:** Project skills encode the team's standards and hard-won conventions. Work done around them is technically-correct-but-off-standard, gets flagged in review, and burns an iteration. The tooling exists precisely so the loop doesn't improvise.

**How to apply:**
- At the start of the implement step, list the available skills and match them against the task type: UI/visual task → `impeccable` / `pixel-perfect-ui`; feature/refactor/bugfix → `rigorous`; locale strings → `translate`; anything with a matching repo-scoped skill → that skill.
- Invoke matched skills via the Skill tool at the right stage — while designing/implementing, not retroactively.
- Repo-scoped skills (from the target repo's `.claude/skills/`) take precedence over generic ones when both match.
- If nothing matches, proceed normally — this rule adds gates only where tooling already exists.
- The PR-time counterpart is [[feedback-pr-gate-passes]]: `rigorous` in review mode on every PR when available.
