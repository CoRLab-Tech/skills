# Init workflow

One-time per-project setup. Generates the memory directory, config files, monitor script, and copies the universal feedback rules.

## Preconditions

- Current working directory is a git repo (or a folder containing per-service repos for monorepos).
- User has one of: a Linear API key; Jira Cloud credentials (host + email + API token); or a Plane workspace API token (self-hosted or cloud).
- `gh` CLI is authenticated against the GitHub org that owns the target repo(s).
- For Plane: the `plane` MCP server should be registered at user scope for the MCP-first verbs (the curl fallback works without it). See `references/providers/plane.md` → "Prerequisite".

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

- **Linear** — works out of the box; verified end-to-end
- **Plane** — self-hosted or cloud; MCP-first, verified end-to-end
- **Jira (Cloud)** — recipes documented; not end-to-end tested by the skill author

Save the choice for the rest of the flow. **Read only the relevant `references/providers/<choice>.md`** — do not load the others.

## Step 3 — Provider-specific interview

### Linear path

Read `references/providers/linear.md`. Then ask `AskUserQuestion` for:

1. **Linear API key** — the personal API key from https://linear.app/settings/api. If the user already has it in `~/.config/taskloop/linear.key` or env `LINEAR_API_KEY`, reuse without prompting.
2. **Linear project name** — exact name as in Linear. Resolve to ID via the GraphQL recipe in `references/providers/linear.md` (look up by name). If multiple projects match, list them and ask again.
3. **Linear team name** — exact team name (needed for issue status enumeration).

Verify the API key and project ID by hitting the `issues(first:1, filter:{state:{name:{eq:"Todo"}}})` query and ensuring it returns 200. If it 401s, the key is wrong — ask again.

### Plane path

Read `references/providers/plane.md`. Then ask `AskUserQuestion` for:

1. **Plane API token** — workspace API token from Settings > API Tokens (`/settings/api-tokens/`). Reuse from the `plane` MCP server env or `PLANE_API_KEY` if already present, without prompting.
2. **Base URL** — API root, e.g. `https://plane.corlab.tech/api` (self-hosted) or `https://api.plane.so` (cloud). No trailing `/v1`.
3. **Workspace slug** — e.g. `corlab`.
4. **Project name** — resolve to `PLANE_PROJECT_ID` + `PLANE_PROJECT_IDENTIFIER` via the "Project + identifier resolution" recipe in `references/providers/plane.md`. If several match, list and re-ask.
5. **Ready status name** — default `Todo`.
6. **Review status name** — default `In Review`.

Verify by hitting the "Verify ready queue" curl (`.../issues/?expand=state&per_page=1`) and ensuring 200 (401 → token wrong; 404 → slug/project wrong). Then run `list_states` (MCP or curl) and confirm the review status exists; if missing, offer to create it (`create_state` / `POST .../states/`, group `started`) or point `PLANE_REVIEW_STATUS` at an existing state. Also confirm a **Blocked** state exists — if missing, create it without asking (`create_state(name="Blocked", color="#EF4444", group="backlog")`): the status-mirrors-work rule requires it as the landing state for timeboxed tasks. Confirm the token's user is a project member (project-scoped writes 403 otherwise).

If the `plane` MCP server is not registered at user scope, offer to add it now (see `references/providers/plane.md` → "Prerequisite"); the loop still works via curl if declined.

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
4. **Model routing profile** — ask via `AskUserQuestion` ("Which model routing profile for this project's agents?"). The ladder has four rungs (light/standard/deep/frontier + verdicts pinned to the top):
   - **High (Recommended, default)** — top = `opus` (verdicts + frontier fold into it), deep = `opus`, balanced = `sonnet`, light = `haiku`. Strong quality at standard cost.
   - **Mythos (extra)** — top = `fable` (the Mythos-class rung above opus) for verdicts + frontier; **deep stays `opus`** — opus keeps its seat; balanced = `sonnet`, light = `haiku`. Maximum judgment quality, extra cost only where it buys something.
   - **Custom** — follow-up questions: top model (`fable`/`opus`), deep floor (`opus`/`sonnet`), balanced floor (`sonnet`/`opus`).

   Record the answers for the hook render below and write `$MEM/feedback/model-routing-profile.md` (standard feedback frontmatter, name `feedback-model-routing-profile`) stating: top / deep / balanced models, the date, and the note that the tiers, the verdict-pin, and never-downgrade come from the universal `model-effort-routing` rule — only the model ids are per-project. Index it in `MEMORY.md`.
5. **Anything else worth saving as a project rule?** — open text. If non-empty, immediately call `add-rule` workflow to create `feedback/<slug>.md`.

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
JIRA_READY_STATUS="Selected for Development"
JIRA_REVIEW_STATUS="In Review"
```

For Plane:

```
PLANE_API_KEY=<token>
PLANE_BASE_URL=<https://host/api>
PLANE_WORKSPACE_SLUG=<slug>
PLANE_PROJECT_ID=<uuid>
PLANE_PROJECT_IDENTIFIER=<code>
PLANE_READY_STATUS="Todo"
PLANE_REVIEW_STATUS="In Review"
PLANE_BLOCKED_STATUS="Blocked"
```

Then `chmod 600 "$MEM/.env"`.

### `monitor.sh`

Render the provider's `assets/monitor-<provider>.sh.tmpl` by substituting `{{ENV_FILE}}` → `$MEM/.env` and `{{STATE_FILE}}` → `$MEM/.monitor-state`. Write to `$MEM/monitor.sh`, then `chmod +x`.

### `monitor-prs.sh` (the loop's own eyes on its PRs)

Render `assets/monitor-github-prs.sh.tmpl` substituting `{{REGISTRY_FILE}}` → `$MEM/.pr-feedback-state` and `{{STATE_FILE}}` → `$MEM/.pr-monitor-state`. Write to `$MEM/monitor-prs.sh`, `chmod +x`. This watcher makes the loop **independent**: it detects MERGED / CLOSED / new-comments / CI changes on its own PRs by itself — the owner never has to announce a merge in chat; all owner communication flows through PR comments and tracker comments.

### `hook-agent-routing.mjs` (mechanical model routing)

Render `assets/hook-agent-routing.mjs.tmpl` from the routing profile chosen in Step 4: `{{TOP_MODEL}}` → the profile's top (`fable` for Mythos, `opus` for High), `{{DEEP_MODEL}}` → `opus` (both standard profiles; custom's answer otherwise), `{{BALANCED_MODEL}}` → `sonnet` (or custom's answer). Write to `$MEM/hook-agent-routing.mjs`.

Then install the PreToolUse hook in the **project's** `.claude/settings.local.json` (create the file if missing, MERGE if it exists — never clobber; ensure it is gitignored):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task|Agent",
        "hooks": [
          { "type": "command", "command": "node <MEM>/hook-agent-routing.mjs" }
        ]
      }
    ]
  }
}
```

(`<MEM>` expanded to the absolute memory-dir path.) Pipe-test before moving on: `echo '{"tool_input":{"prompt":"[LOOP-AGENT issue:X tier:deep verdict:no] t","model":"haiku"}}' | node $MEM/hook-agent-routing.mjs` must emit an `updatedInput` with the top model. This is the mechanical half of the `model-effort-routing` rule — the marker contract is enforced even when prose is forgotten.

### Repo setting — auto-delete merged branches

Enable head-branch auto-delete on every target repo (confirm with the user once):

```bash
gh api -X PATCH repos/<owner>/<repo> -f delete_branch_on_merge=true
```

### `MEMORY.md`

Render `assets/MEMORY.md.tmpl` substituting project metadata. The index points to:
- `autonomous-loop.md`
- `restart-instructions.md`
- All `feedback/*.md` files (universal + any project-specific added in Step 4)

### `autonomous-loop.md`

Render `assets/autonomous-loop.md.tmpl`. Placeholders:
- `{{PROVIDER}}` — `Linear`, `Jira`, or `Plane`
- `{{READY_STATUS}}` — provider-specific (`Todo` for Linear/Plane, env-var driven for Jira)
- `{{REVIEW_STATUS}}` — `Ready for Review` for Linear, `In Review` for Plane, env-var driven for Jira
- `{{PROJECT_NAME}}`

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
   Provider: <Linear|Jira|Plane>
   Memory:   ~/.claude/projects/<slug>/memory/
   Files:    .env (chmod 600), monitor.sh, MEMORY.md, autonomous-loop.md,
             restart-instructions.md, feedback/ (33 files)
   Next:     run `/taskloop start` to arm the Monitor + ScheduleWakeup,
             or just type "start" in this directory in any future session.
```

## Idempotency notes

- `init` re-run on an already-configured project: ask per-file whether to overwrite. Default no.
- API key already in `.env`: reuse, don't re-prompt.
- Conflicting provider chosen on re-init: clear all provider-specific env vars before writing the new set.
