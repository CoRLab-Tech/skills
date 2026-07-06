---
name: feedback-continuous-learning
description: "The loop learns the project as it works: chat corrections, PR review comments, ticket comments, and its own failures distill into durable per-project memories — every tick starts smarter than the last"
metadata:
  type: feedback
---

The loop is not a stateless executor — it **accumulates the project**. Every source of human feedback and every own failure is raw material for a durable lesson saved under the project's `memory/feedback/` directory and indexed in `MEMORY.md`, which every future tick re-reads. Over weeks, the rule set becomes the project's institutional knowledge: conventions the reviewers keep asking for, quirks of the test suite, the owner's tastes — effectively fine-tuning by memory, no model training needed.

**The four learning sources:**

1. **Chat corrections** — the user pushes back, redirects, or adds a rule mid-run → save immediately, quote their wording nearly verbatim (don't blandify), apply on the very next iteration.
2. **PR review comments** — while addressing feedback in the sweep ([[feedback-watch-pr-comments]]): if the comment expresses something **generalizable** ("we always...", "never use X here", "why didn't you follow <pattern>?", the same nit appearing on a second PR), it's a lesson, not just a fix. Fix the PR AND save the lesson.
3. **Ticket comments** — requirements-shaped feedback on tracker issues (clarifications the owner had to give, domain vocabulary, acceptance-criteria patterns) that will apply to future tickets too.
4. **Own failures, at merge time** — when a PR merges, run a 30-second retro: what did review catch that the gates missed? What cost an extra round-trip (a convention unknown, a test quirk, an env detail)? Each answer that would change future behavior → lesson.

**Why:** the owner should never repeat a correction — not in chat, not in review comments. A lesson that stays inside one PR's comment thread is rediscovered by the reviewer on the next PR, at their expense. Distilling feedback into memories is what makes the loop *better each week on this project* instead of identically mediocre forever.

**How to apply:**
- Save via `/taskloop add-rule <slug>` (or write `memory/feedback/<slug>.md` inline with the standard frontmatter — `name`, `description`, `metadata.type: feedback` — one-paragraph rule, `**Why:**`, `**How to apply:**`), then append the one-line index entry to `MEMORY.md`.
- Every lesson records its **source**: the PR/ticket/comment link and date. When the same lesson recurs, strengthen the existing file (add the new evidence) — never create a duplicate; check `MEMORY.md` for an existing rule covering the topic FIRST.
- **Save the generalizable, skip the one-off.** "Rename this variable" is a fix; "we prefix all feature flags with `ff_`" is a lesson. When unsure whether it generalizes, save it marked `(provisional — single occurrence)` and promote the wording when it recurs.
- Human feedback is law: a lesson from the owner's own comment overrides an inferred one; if a new lesson contradicts a universal rule, save it as the project-specific override and note the conflict in the file — the owner's board, the owner's rules.
- Never store secrets, tokens, or personal data in a lesson; link to where a value lives instead.
- Lessons apply from the **very next iteration** — don't wait for a restart. The QA agent ([[feedback-qa-agent-review]]) receives the accumulated lessons as part of the project conventions it checks against.
