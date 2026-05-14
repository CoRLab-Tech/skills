# Init workflow

One-time per-project setup. Generates the memory directory, config files, monitor script, and copies the universal feedback rules.

## Preconditions

- Current working directory is a git repo (or a folder containing per-service repos for monorepos).
- User has at least one of: a Linear API key, or Jira Cloud credentials (host + email + API token).
- `gh` CLI is authenticated against the GitHub org that owns the target repo(s).

## Step 1 — Compute the project memory directory

```bash
SLUG=$(pwd | sed 's|/|-|g')
MEM="$HOME/.claude/projects/${SLUG}/memory"
```

If `$MEM` already exists, ask the user via `AskUserQuestion`:
- "Overwrite" → continue, but per-file confirm before clobbering
- "Cancel" → stop, print the existing config path

Create the directory: `mkdir -p "$MEM/feedback"`.

## Step 2 — Pick the provider

Ask via `AskUserQuestion`:

- **Linear** — works out of the box; recommended
- **Jira (Cloud)** — recipes documented; not end-to-end tested by the skill author

Save the choice for the rest of the flow. **Read only the relevant `references/providers/<choice>.md`** — do not load the other.

## Step 3 — Provider-specific interview

### Linear path

Read `references/providers/linear.md`. Then ask `AskUserQuestion` for:

1. **Linear API key** — the personal API key from https://linear.app/settings/api. If the user already has it in `~/.config/taskloop/linear.key` or env `LINEAR_API_KEY`, reuse without prompting.
2. **Linear project name** — exact name as in Linear. Resolve to ID via the GraphQL recipe in `references/providers/linear.md` (look up by name). If multiple projects match, list them and ask again.
3. **Linear team name** — exact team name (needed for issue status enumeration).

Verify the API key and project ID by hitting the `issues(first:1, filter:{state:{name:{eq:"Todo"}}})` query and ensuring it returns 200. If it 401s, the key is wrong — ask again.

### Jira Cloud path

Read `references/providers/jira.md`. Then ask `AskUserQuestion` for:

1. **Atlassian host** — `<workspace>.atlassian.net` (no protocol prefix)
2. **Email** — the user's Atlassian account email
3. **API token** — from https://id.atlassian.com/manage-profile/security/api-tokens
4. **Project key** — usually 2–4 uppercase letters (e.g., `ENG`, `ABC`)
5. **Board ID** — numeric, found in the URL of the project's board page
6. **"Ready" status name** — default `Selected for Development`
7. **"In review" status name** — default `In Review`

Verify by GET-ing `https://<host>/rest/api/3/project/<key>` with basic auth. If 401/404, ask again.

## Step 4 — Universal questions

After the provider interview:

1. **GitHub org/repo** — `<org>/<repo>` for single-repo, or just `<org>` for monorepos where each subfolder is its own repo.
2. **Monorepo y/n** — if yes, ask for a brief description of how subfolders map to repos (e.g., "each top-level folder is a service named `<folder>` and maps to `git@github.com:<org>/<folder>.git`").
3. **Scope exclusions** — comma-separated list of folder names to skip when sweeping the monorepo (e.g., `legacy-folder, sandbox`). Optional; default empty.
4. **Anything else worth saving as a project rule?** — open text. If non-empty, immediately call `add-rule` workflow to create `feedback_<slug>.md`.

## Step 5 — Write files

All paths are inside `$MEM` unless stated otherwise.

### `.env` (chmod 600)

Write the env vars. For Linear:

```
LINEAR_API_KEY=<key>
LINEAR_PROJECT_ID=<id>
LINEAR_TEAM_ID=<id>
```

For Jira:

```
JIRA_HOST=<host>
JIRA_EMAIL=<email>
JIRA_API_TOKEN=<token>
JIRA_PROJECT_KEY=<key>
JIRA_BOARD_ID=<id>
JIRA_READY_STATUS=Selected for Development
JIRA_REVIEW_STATUS=In Review
```

Then `chmod 600 "$MEM/.env"`.

### `monitor.sh`

Render the provider's `assets/monitor-<provider>.sh.tmpl` by substituting `{{ENV_FILE}}` → `$MEM/.env` and `{{STATE_FILE}}` → `$MEM/.monitor-state`. Write to `$MEM/monitor.sh`, then `chmod +x`.

### `MEMORY.md`

Render `assets/MEMORY.md.tmpl` substituting project metadata. The index points to:
- `autonomous-loop.md`
- `restart-instructions.md`
- All `feedback/*.md` files (universal + any project-specific added in Step 4)

### `autonomous-loop.md`

Render `assets/autonomous-loop.md.tmpl`. Placeholders:
- `{{PROVIDER}}` — `Linear` or `Jira`
- `{{READY_STATUS}}` — provider-specific (`Todo` for Linear, env-var driven for Jira)
- `{{REVIEW_STATUS}}` — `Ready for Review` for Linear, env-var driven for Jira
- `{{PROJECT_NAME}}`
- `{{TEAM_NAME}}` (Linear) / `{{PROJECT_KEY}}` (Jira)

### `restart-instructions.md`

Render `assets/restart-instructions.md.tmpl`. Same placeholder set. The body explains: kill old `.monitor-state`, arm `Monitor` with `$MEM/monitor.sh`, arm `ScheduleWakeup` with the full `/loop` prompt.

### `feedback/*.md`

Copy every file from `assets/feedback/` into `$MEM/feedback/` verbatim. These are already provider-neutral.

## Step 6 — Optional CLAUDE.md tag

Ask: "Append a short note to the project's CLAUDE.md so future Claude sessions know taskloop is configured?"

If yes, append (or create) at `$CWD/CLAUDE.md`:

```markdown
## Taskloop

This project is wired into [taskloop](https://github.com/CoRLab-Tech/skills/tree/main/taskloop). The loop's spec and feedback rules live in `~/.claude/projects/<slug>/memory/MEMORY.md`. To resume the loop: type `start` (or run `/taskloop start`).
```

## Step 7 — Confirm

Print a summary:

```
✅ taskloop initialized for <project name>
   Provider: <Linear|Jira>
   Memory:   ~/.claude/projects/<slug>/memory/
   Files:    .env (chmod 600), monitor.sh, MEMORY.md, autonomous-loop.md,
             restart-instructions.md, feedback/ (11 files)
   Next:     run `/taskloop start` to arm the Monitor + ScheduleWakeup,
             or just type "start" in this directory in any future session.
```

## Idempotency notes

- `init` re-run on an already-configured project: ask per-file whether to overwrite. Default no.
- API key already in `.env`: reuse, don't re-prompt.
- Conflicting provider chosen on re-init: clear all provider-specific env vars before writing the new set.
