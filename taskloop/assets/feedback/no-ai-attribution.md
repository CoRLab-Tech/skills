---
name: feedback-no-ai-attribution
description: "Never include AI/Claude co-author attribution in commits, PRs, or any output"
metadata:
  type: feedback
---

NEVER add `Co-Authored-By: Claude`, "Generated with Claude Code", "🤖 Generated with Claude Code", or any AI/assistant attribution in commit messages, PR titles, PR descriptions, PR bodies, or anywhere else the loop writes.

**Why:** Commits and PRs must look like they were authored by the human user, with no trace of AI tooling. Surfacing AI attribution invites premature dismissal of the work and clutters the project's git history with noise. Per the user's explicit standing instruction, attribution lines are scrubbed everywhere.

**How to apply:**
- When committing via `git commit`, write the message exactly as a human would; do not append `Co-Authored-By` lines.
- When opening PRs via `gh pr create`, the `--body` payload must end with the last content line — no "Generated with Claude Code" footer, no Claude Code link, no emoji robot.
- If a default template tries to inject attribution (some harnesses do), strip it before the call.
- Applies to every git/gh operation the loop performs, including amend/edit flows.
