---
name: feedback-save-corrections
description: "Always persist user corrections as feedback memories for future runs"
metadata:
  type: feedback
---

Every time the user gives a correction, preference, or "do it this way instead" instruction during an autonomous run, immediately save it as a feedback memory under the project's `memory/feedback/` directory and update `MEMORY.md` to reference it.

**Why:** The user is running this loop autonomously and does not want to repeat the same correction twice. Mid-run corrections must accumulate as durable rules so the next tick — even days later, in a fresh session — applies them automatically. Forgetting to save a correction means the user has to give it again, which defeats the autonomy.

**How to apply:**
- When the user pushes back, redirects, or adds a new rule mid-loop, run the `/taskloop add-rule <slug>` workflow (or write the file inline if `add-rule` is unavailable).
- The file format is `memory/feedback/<slug>.md` with the standard frontmatter (`name`, `description`, `metadata.type: feedback`), a one-paragraph rule body, then `**Why:**` and `**How to apply:**` sections.
- Append a one-line index entry to `MEMORY.md` pointing to the new file.
- Apply the rule on the **very next iteration** of the loop — don't wait for a session restart.
- Quote the user's correction nearly verbatim in the rule body; do not paraphrase their wording into something blander without confirmation.
