# Add-rule workflow

Add a new project-specific feedback rule that the loop will read every tick. Use this when the user gives a mid-run correction that should persist, or when review/ticket feedback distills into a durable lesson (see the `continuous-learning.md` universal rule).

## Args

The skill is called as `/taskloop add-rule <slug>` where `<slug>` is a short kebab-case identifier (e.g., `admin-endpoints-separate`, `pull-main-each-task`). If the slug is missing, ask via `AskUserQuestion`.

## Step 1 — Validate the slug

- Lowercase, kebab-case, 2–60 chars, no leading/trailing dash.
- Not already present at `$MEM/feedback/<slug>.md`. If it is, ask `AskUserQuestion`: "Overwrite?" — proceed only on yes.

## Step 2 — Gather the rule body

Ask via `AskUserQuestion` (or accept it from chat context if the trigger was a mid-run correction):

1. **One-line description** — shown in `MEMORY.md` index. Max ~140 chars.
2. **Rule body** — the actual instruction. Phrase it in the imperative; lead with what to do.
3. **Why** — the motivation (incident, preference, constraint). One short paragraph.
4. **How to apply** — when/where this rule kicks in. One short paragraph.

If the trigger is a user correction in the current chat (you're already inside the loop), skip the `AskUserQuestion` and reconstruct from context — but only if you can quote the user's correction nearly verbatim. Don't paraphrase user wording into a rule without confirming.

## Step 3 — Write the file

Path: `$MEM/feedback/<slug>.md`.

Template:

```markdown
---
name: <slug>
description: <one-line description>
metadata:
  type: feedback
---

<rule body, imperative, lead-with-action>

**Why:** <motivation>

**How to apply:** <when/where this kicks in>
```

If the body mentions related rules (e.g., builds on another `feedback-*` file), use `[[<other-slug>]]` to link them — `MEMORY.md` loaders treat this as a cross-reference.

## Step 4 — Update `MEMORY.md`

Append one line to the bottom of `$MEM/MEMORY.md`:

```markdown
- [<title-case description>](feedback/<slug>.md) — <one-line description>
```

Keep each line under ~150 chars; this file is loaded into every conversation and gets truncated after line 200.

## Step 5 — Confirm

```
✅ Rule saved: <slug>
   File: ~/.claude/projects/<slug>/memory/feedback/<slug>.md
   Indexed in MEMORY.md.
```

## What NOT to save as a rule

Per `references/providers/linear.md` (and the upstream skill philosophy):

- **Code patterns, conventions, architecture, file paths** — derivable from the codebase.
- **Git history, recent changes, who-changed-what** — `git log` is authoritative.
- **Debugging fix recipes** — the fix lives in the code; the commit message has context.
- **Ephemeral task state** — in-progress work, current conversation context.

If the user's correction is one of the above, push back: ask whether what they want is genuinely a *future-conversation behavior change*, or a one-off note for this session.

The rule slug should describe a behavior change, not a fact (e.g., `prefer-yarn-over-npm` is a rule; `service-uses-postgres-on-5435` is not).
