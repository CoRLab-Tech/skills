# Init workflow

One-time per-project setup. Generates the memory directory, config files, monitor script, and copies the universal feedback rules.

## Preconditions

- Current working directory is a git repo (or a folder containing per-service repos for monorepos).
- User has one of: a Linear API key; Jira Cloud credentials (host + email + API token); or a Plane workspace API token (self-hosted or cloud).
- `gh` CLI is authenticated against the GitHub org that owns the target repo(s). For the GitHub Issues provider, `jq` must also be on `PATH`.
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
- **GitHub Issues** — states as labels, driven entirely by `gh`; no second tracker to authenticate. Recipes documented; **not yet verified end-to-end**
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

### GitHub Issues path

Read `references/providers/github.md`. Then ask `AskUserQuestion` for:

1. **Repo** — `<org>/<repo>` holding the issues. Often the same repo the loop opens PRs against.
2. **Label names** — defaults `ready` / `in-progress` / `in-review` / `blocked` / `merged`. Accept the defaults unless the repo already uses a different vocabulary.

Verify with the "Verify queue" recipe: exit 0 and a JSON array (possibly `[]`) means auth and repo are good; a non-zero exit means the token or the repo is wrong. Then run `gh label list` and, **after asking** (this mutates the owner's repo), create whichever of the five labels are missing.

Tell the user the two consequences of modelling states as labels, because they are not obvious:

- the loop **never closes an issue** — a merged PR only adds the `merged` label; closing stays the owner's call;
- therefore the loop must write `Refs #123` in PR bodies, **never** `Closes #123`, and must not create branches with `gh issue develop`. Both would auto-close the issue on merge.

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
   - **Custom** — follow-up questions: the **ladder** (ordered model ids, cheapest first), then top model, deep floor, balanced floor. Every one of the three must be on the ladder.

   Both standard profiles use the ladder `haiku < sonnet < opus < fable`.

   Record the answers for the hook render below and write `$MEM/feedback/model-routing-profile.md` (standard feedback frontmatter, name `feedback-model-routing-profile`). It states the **ladder** first, then top / deep / balanced / light, the date, and the note that the tiers, the verdict-pin, and never-downgrade come from the universal `model-effort-routing` rule — only the ids and their order are per-project. Index it in `MEMORY.md`.

   ```
   LADDER   = haiku, sonnet, opus, fable    # cheapest first; ids AND order live only here
   top      = opus
   deep     = opus
   balanced = sonnet
   light    = haiku
   ```

   **Assert before going further** — every rung the profile names must be on the ladder. A `TOP_MODEL` that is not on the ladder used to break the verdict pin silently; a `DEEP_MODEL` that is not on it cannot floor anything:

   ```bash
   node -e '
   const L=JSON.parse(process.argv[1]), P=process.argv.slice(2);
   const bad=P.filter(m=>!L.includes(m));
   if(bad.length){console.error(`taskloop init: ${bad.join(", ")} not on the ladder (${L.join(" < ")}). Fix the profile before arming the loop.`);process.exit(1)}
   console.log("profile ok:", L.join(" < "));
   ' '["haiku","sonnet","opus","fable"]' "$TOP_MODEL" "$DEEP_MODEL" "$BALANCED_MODEL"
   ```
5. **Loop strategy** — ask via `AskUserQuestion` ("How rigorous should the loop be by default?"), per `assets/feedback/loop-strategy-profiles.md`:
   - **auto (Recommended, default)** — each ticket gets the rung its complexity asks for (`fast` unless a money/auth/concurrency/cross-cutting signal fires). When QA hands back a defect that reveals a surface the classification missed, the ticket is re-classified — possibly straight to `heavy`. A defect *inside* the known complexity (a typo, a missing test) does not move the rung. Failures are never simply counted.
   - **balanced** — a constant risk-scaled gate on every ticket.
   - **heavy** — every check on every PR; for money / auth / concurrency-heavy codebases.
   - **fast** — reduced gate everywhere with NO escalation, owner accepts the risk; for prototypes and spikes.

   Write the answer as `LOOP_STRATEGY` in `.env`. Tell the user they can switch later by editing that var or by saying "switch to auto/fast/balanced/heavy" mid-run, and that any single ticket can be pinned with a `strategy:` field in its `LOOP-PLAN` marker.
6. **Auto-merge** — ask via `AskUserQuestion` ("May the loop merge its own no-risk PRs without waiting for a human review?"), per `assets/feedback/automerge-risk-lanes.md`:
   - **off (Recommended, default)** — every merge waits for a human approval (`merge-on-approval`). Today's behavior, unchanged.
   - **on** — a ticket with no rung-lifting Step-1 risk signal (the table in `assets/feedback/loop-strategy-profiles.md`: money, auth/security incl. cross-tenant, concurrency, idempotency, a public contract change, a new service or external adapter, cross-cutting footprint) gets lane `merge: auto`: once every gate is green and NO human has touched the PR, the loop merges it itself. Risk-flagged tickets still wait for approval; the lane only ever ratchets `auto → review`.

   Write the answer as `LOOP_AUTOMERGE` in `.env`. Tell the user they can switch later by editing the var or saying "automerge on/off" mid-run, and that any single ticket can be pinned to the review lane with `merge: review` in its `LOOP-PLAN` marker. If **on**: warn that branch protection requiring approving reviews blocks the auto lane on that repo — the loop surfaces the mismatch once and falls back to the review lane rather than bypass it.
7. **Review recall** — ask whether to install the `review-recall.sh` cron (a periodic Telegram ping listing review-ready PRs still unmerged). If yes, ask for the working-hours window (default 9–18). Default: yes.
8. **Anything else worth saving as a project rule?** — open text. If non-empty, immediately call `add-rule` workflow to create `feedback/<slug>.md`.

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

For GitHub Issues:

```
GITHUB_REPO=<org>/<repo>
GITHUB_TOKEN=<PAT with `repo` scope>   # optional — omit to use the `gh auth` session
READY_LABEL="ready"
IN_PROGRESS_LABEL="in-progress"
IN_REVIEW_LABEL="in-review"
BLOCKED_LABEL="blocked"
MERGED_LABEL="merged"
```

Provider-neutral vars, appended for every provider:

```
LOOP_STRATEGY=auto              # auto | fast | balanced | heavy — read at the top of every tick
LOOP_AUTOMERGE=off              # on | off — the auto merge lane (automerge-risk-lanes); read at the top of every tick
GH_AUTHOR=<the login the loop commits as>
REPOS="<owner/repo> [<owner/repo> ...]"
```

Then `chmod 600 "$MEM/.env"`.

### `monitor.sh`

Render the provider's `assets/monitor-<provider>.sh.tmpl` by substituting `{{ENV_FILE}}` → `$MEM/.env` and `{{STATE_FILE}}` → `$MEM/.monitor-state`. Write to `$MEM/monitor.sh`, then `chmod +x`.

### `monitor-prs.sh` (the loop's own eyes on its PRs)

Render `assets/monitor-github-prs.sh.tmpl` substituting `{{REGISTRY_FILE}}` → `$MEM/.pr-feedback-state` and `{{STATE_FILE}}` → `$MEM/.pr-monitor-state`. Write to `$MEM/monitor-prs.sh`, `chmod +x`. This watcher makes the loop **independent**: it detects MERGED / CLOSED / new-comments / CI changes on its own PRs by itself — the owner never has to announce a merge in chat; all owner communication flows through PR comments and tracker comments.

### `hook-agent-routing.mjs` (mechanical model routing)

Render `assets/hook-agent-routing.mjs.tmpl` from the routing profile chosen in Step 4: `{{LADDER_JSON}}` → the profile's ladder as a JSON array, cheapest first (`["haiku","sonnet","opus","fable"]` for both standard profiles), `{{TOP_MODEL}}` → the profile's top (`fable` for Mythos, `opus` for High), `{{DEEP_MODEL}}` → `opus` (both standard profiles; custom's answer otherwise), `{{BALANCED_MODEL}}` → `sonnet` (or custom's answer), `{{MEM}}` → the absolute memory-dir path. Write to `$MEM/hook-agent-routing.mjs`.

The hook derives its rank ordering from `{{LADDER_JSON}}` — nothing about model order is hardcoded in the script. A harness that adds a rung is a one-line profile edit, not a code change.

Besides routing, this hook writes the **append-only spawn ledger** to `$MEM/telemetry/spawns-YYYY-MM.jsonl` — one line per `[LOOP-AGENT]` spawn. Telemetry writes are best-effort and wrapped in `try/catch`: a failing ledger must never block a spawn.

### `hook-loop-guards.mjs` (the rules that refuse to be ignored)

Render `assets/hook-loop-guards.mjs.tmpl` substituting four placeholders. Write to `$MEM/hook-loop-guards.mjs`.

- `{{MEM}}` — the absolute memory-dir path.
- `{{EVIDENCE_DIR}}` — the repo-relative directory where UI screenshots are committed (ask, or infer from an existing path; `docs/evidence` is the common choice).
- `{{TRACKER_CREATE_CMD_RE}}` — regex **source** matching a command that CREATES a ticket for this provider (it lands inside `new RegExp('…')`, so escape backslashes as for a JS string literal). It must match creation ONLY — never a comment POST, never a GET, because commenting on an existing ticket is exactly what the dedupe rule prefers. Per provider:
  - **plane**: a POST whose URL *terminates* at `/issues/` — order-independent via a lookahead: `(?=[\\s\\S]*(-X|--request)\\s*[\\x27\\x22]?POST)[\\s\\S]*\\/api\\/v1\\/workspaces\\/[^\\s\\x22\\x27]+\\/projects\\/[^\\s\\x22\\x27/]+\\/issues\\/?([\\x22\\x27]|\\s|$)` (`\x22`/`\x27` are the quote characters, spelled as hex escapes to survive the JS string literal); a URL continuing into `/issues/<id>/comments/` must not match.
  - **github**: `(?:^|[;&|]\\s*|\\n\\s*)gh\\s+issue\\s+create\\b` — anchored to command start, same reason as the `gh pr ready` guard.
  - **jira / linear**: the create endpoint from the provider reference, POST-only, terminal path.
  - No command route → `(?!)` (matches nothing).
- `{{TRACKER_CREATE_TOOLS_RE}}` — regex source matching the provider's MCP create-tool **names** (plane: `^mcp__plane__create_(work_item|intake_work_item)$`). No MCP tools → `(?!)`.

Guard 3, `pr-visual-evidence`, blocks `gh pr ready` when a PR touches a UI surface and either commits no screenshots or commits them without naming them in the description. It shells out to `gh pr view`; any failure allows, so a missing `gh` or a bad PR number never produces a false denial. The escape hatch is the literal phrase `no visual surface` in the PR body — an assertion a reviewer can challenge, rather than a silent omission — and **every use of the escape is logged** to the ledger as `pr-visual-evidence-escape-used`, so a habit of escaping is one grep away from being noticed.

Guard 4, `dedupe-before-filing`, blocks ticket creation (either route above) unless the project's `find-existing-ticket` script ran within the last **15 minutes** — the script appends a stamp to `$MEM/telemetry/dedupe-stamps.jsonl` on every run and the guard checks its freshness. Deliberately **fail-closed**, unlike the `gh` checks: the stamp is a local file the loop's own tooling writes, so an unreadable stamp means "the search did not run", not "the environment broke". This is what turns the follow-up filter's dedupe step from prose into mechanism. Install the script alongside: render the provider example from `assets/` (Plane: `find-existing-ticket.py.plane.example`) into `$MEM/find-existing-ticket.py` with the project's ids; for other providers port it — the contract is ~100 lines: search title+description of EVERY ticket in EVERY state for the given root-cause terms, print matches loudest-first with a DO-NOT-FILE verdict when a live match exists, and stamp the ledger.

Guards 1 and 2 deny the two things agents demonstrably did when they were only prose: **backgrounding a gate command inside a subagent** (the background child dies with the subagent's turn — a silent dead run), and **committing a message that carries AI attribution**. Denials feed `permissionDecisionReason` back to the model, which reads it and retries, and every decision — denies and audited allows — is appended to `telemetry/guards-*.jsonl`.

Known blind spot, worth stating: the commit guard reads the shell command, so it catches `-m "…"` and heredoc-fed messages, but **not** `git commit -F <file>` where the trailer lives in a file the hook never sees. Projects that care can add a repo-side `commit-msg` hook for that path.

### Install both hooks

In the **project's** `.claude/settings.local.json` (create if missing, MERGE if it exists — never clobber; ensure it is gitignored). Matchers are regex over the tool name; every matching hook runs, and the most restrictive decision wins, so the two never conflict:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task|Agent",
        "hooks": [
          { "type": "command", "command": "node <MEM>/hook-agent-routing.mjs" }
        ]
      },
      {
        "matcher": "Bash|<the provider's MCP create-tool names, e.g. mcp__plane__create_work_item|mcp__plane__create_intake_work_item>",
        "hooks": [
          { "type": "command", "command": "node <MEM>/hook-loop-guards.mjs" }
        ]
      }
    ]
  }
}
```

The guards matcher must name the tracker's MCP create tools alongside `Bash`, or guard 4 never sees MCP-route ticket creation. Providers with no MCP tools keep plain `Bash`.

Pipe-test the guard before moving on — a hook that is installed but never denies is worse than none, because it reads as protection. Write each payload to a FILE and pipe the file: embedding a create-URL inline in your own shell command would trip guard 4 on the test itself.

```bash
# must DENY (a subagent backgrounding a gate): agent_id is what marks a subagent
echo '{"agent_id":"a1","tool_input":{"command":"pnpm test","run_in_background":true}}' | node "$MEM/hook-loop-guards.mjs"
# must ALLOW (the same command in the foreground)
echo '{"agent_id":"a1","tool_input":{"command":"pnpm test"}}' | node "$MEM/hook-loop-guards.mjs"
# guard 4, MCP route: must DENY with no fresh stamp, ALLOW right after running find-existing-ticket.py
echo '{"tool_name":"<mcp create tool>","tool_input":{"name":"t"}}' | node "$MEM/hook-loop-guards.mjs"
# guard 4 must NOT fire on a comment POST — commenting is the alternative the rule prefers
```

(`<MEM>` expanded to the absolute memory-dir path.) Pipe-test all four before moving on — this is the mechanical half of the `model-effort-routing` rule, and a hook that is installed but silently wrong is worse than none:

```bash
H="node $MEM/hook-agent-routing.mjs"
# 1. verdict pin: must emit updatedInput with the profile's TOP model, in EVERY profile
echo '{"tool_input":{"prompt":"[LOOP-AGENT issue:X tier:light verdict:yes] t","model":"haiku"}}' | $H
# 2. verdict pin holds even against the ladder's highest rung, when that is not the profile's top
echo '{"tool_input":{"prompt":"[LOOP-AGENT issue:X tier:light verdict:yes] t","model":"fable"}}' | $H
# 3. deep floor: must emit the deep-floor model (silent pass-through is correct iff that floor IS sonnet)
echo '{"tool_input":{"prompt":"[LOOP-AGENT issue:X tier:deep verdict:no] t","model":"sonnet"}}' | $H
# 4. off-ladder model: must WARN and leave the model untouched — never silently re-point it
echo '{"tool_input":{"prompt":"[LOOP-AGENT issue:X tier:deep verdict:no] t","model":"not-a-model"}}' | $H
```

Test 2 is the one that matters most and is easiest to get wrong: the pin is an **identity** check (`model !== TOP_MODEL`), not a rank comparison. A rank comparison passes `fable` through untouched whenever the profile's top is not itself the ladder's highest rung — and the verdict then runs on a model the owner never chose.

### `targeted-regate.mjs` (the fix-round re-gate)

Render `assets/targeted-regate.mjs.tmpl` substituting `{{TOP_MODEL}}` and `{{BALANCED_MODEL}}` from the Step 4 routing profile. Write to `$MEM/targeted-regate.mjs`. This is the executable half of the `targeted-regate-on-fixes` rule — without it the rule describes a re-gate the loop has no script to run. Invoke it as `Workflow({scriptPath: "<MEM>/targeted-regate.mjs", args: {...}})`; the arg contract is documented at the top of the file.

### `agent-brief.md` (what spawned agents read at startup)

Render `assets/agent-brief.md.tmpl`, substituting `{{PROVIDER}}`, `{{PROJECT_NAME}}`, `{{REPO}}`, `{{BRANCH_PREFIX}}` (the loop's branch namespace), `{{READY_STATUS}}` / `{{REVIEW_STATUS}}` / `{{BLOCKED_STATUS}}`, `{{TEST_CMD}}` (the project's per-project test command), and the three issue-reference placeholders below. Write to `$MEM/agent-brief.md`.

The branch prefix and the way an issue is *named* are separate, because on GitHub they differ:

| Placeholder | Linear / Jira / Plane | GitHub Issues |
|---|---|---|
| `{{ISSUE_PREFIX}}` — branch shape `<branch-prefix>/<issue-prefix>-<N>-<slug>` | the tracker key, e.g. `ABC` | the literal `issue` |
| `{{ISSUE_REF}}` — commit subject, registry entry, status line | `ABC-<N>` | `#<N>` |
| `{{ISSUE_LINK_KEYWORD}}` — how the PR body references the issue | `Refs` (any word; the tracker links by key) | **`Refs`, never `Closes`/`Fixes`/`Resolves`** — a closing keyword makes GitHub close the issue on merge, which is the owner's decision, not the loop's |

Every spawned implementation agent reads THIS instead of `MEMORY.md` + `autonomous-loop.md` + the feedback files. Its bytes must stay stable across spawns or the prompt cache misses on every agent — see `feedback/efficiency-levers.md`.

### `usage-rollup.mjs` + `telemetry/` (the append-only spend record)

`mkdir -p "$MEM/telemetry"`. Render `assets/usage-rollup.mjs.tmpl` substituting `{{MEM}}` → the memory dir and `{{PROJECT_DIR}}` → `~/.claude/projects/<slug>` (the parent of the session dirs). Write to `$MEM/usage-rollup.mjs`.

The hook records what each agent *was*; this records what it *cost*, by summing the `usage` blocks in each finished subagent transcript and joining on `tool_use_id`. Append-only, idempotent, and it skips any agent whose transcript is still being written. Smoke-test with `QUIESCE_SEC=0 node "$MEM/usage-rollup.mjs" --dry-run | head -3` — it prints candidate rows without writing.

### `model-usage-log.md`

Render `assets/model-usage-log.md.tmpl` with `{{PROJECT_NAME}}`. Write to `$MEM/model-usage-log.md`. It holds the routing policy and the human-recorded gate-cost measurements; the per-task ledger lives in `telemetry/`, written mechanically.

### `reconcile-merged.sh` (level-triggered repair — Plane and GitHub)

For **Plane**, render `assets/reconcile-merged-plane.sh.tmpl` substituting `{{ENV_FILE}}` → `$MEM/.env`, `{{REPOS}}`, `{{GH_AUTHOR}}`, `{{ISSUE_PREFIX}}`.

For **GitHub Issues**, render `assets/reconcile-merged-github.sh.tmpl` substituting `{{ENV_FILE}}` and `{{GH_AUTHOR}}`. It labels merged issues `merged` and **never closes them**; an issue already labelled, or already closed by the owner, is skipped.

Either way: write to `$MEM/reconcile-merged.sh`, `chmod +x`, and smoke-test once with `ONCE=1 $MEM/reconcile-merged.sh` — it prints nothing when the board is already in sync.

For Linear and Jira there is no script yet; the `reconcile-tracker-vs-github` rule still applies and the loop runs the reconcile inline each sweep via the provider's transition recipe.

### `review-recall.sh` (optional cron)

If the user opted in at Step 4, render `assets/review-recall.sh.tmpl` substituting `{{REPOS}}`, `{{GH_AUTHOR}}`, `{{PROJECT_NAME}}`, `{{START_HOUR}}`, `{{END_HOUR}}`. Write to `$MEM/review-recall.sh`, `chmod +x`, verify with `$MEM/review-recall.sh --now`, then install the crontab line printed in the script's header. It pings only when at least one non-draft loop PR is open, so a quiet board stays quiet. (Under `LOOP_AUTOMERGE=on` the recall concerns review-lane PRs — lane-auto PRs self-merge on the loop's next sweep and only linger if the sweep is stalled.)

### Repo setting — auto-delete merged branches

Enable head-branch auto-delete on every target repo (confirm with the user once):

```bash
gh api -X PATCH repos/<owner>/<repo> -f delete_branch_on_merge=true
```

### `MEMORY.md`

Render `assets/MEMORY.md.tmpl` substituting project metadata. The index points to:
- `autonomous-loop.md`
- `agent-brief.md`
- `restart-instructions.md`
- `model-usage-log.md`
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

### `.render-manifest.json` (so `sync` can re-render deterministically)

Write every placeholder value used above into `$MEM/.render-manifest.json`, then `chmod 600` (it echoes `.env`-derived values). This is the map the `sync` workflow (`references/workflows/sync.md`) reads to re-render a drifted or deleted file without re-interviewing the owner. Include at least: `PROVIDER`, `PROJECT_NAME`, `REPO`, `REPOS`, `GH_AUTHOR`, `BRANCH_PREFIX`, `TEST_CMD`, `EVIDENCE_DIR`, `ISSUE_PREFIX`/`ISSUE_REF`/`ISSUE_LINK_KEYWORD`, `READY_STATUS`/`REVIEW_STATUS`/`BLOCKED_STATUS`, the routing profile (`LADDER`, `TOP_MODEL`, `DEEP_MODEL`, `BALANCED_MODEL`), the tracker create regexes, and `START_HOUR`/`END_HOUR` if review-recall was installed. `.env`-managed toggles (`LOOP_STRATEGY`, `LOOP_AUTOMERGE`) stay authoritative in `.env`; the manifest records only what rendering needs.

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
   Provider:  <Linear|Jira|Plane>
   Strategy:  <auto|fast|balanced|heavy>
   Automerge: <on|off>
   Memory:    ~/.claude/projects/<slug>/memory/
   Files:     .env (chmod 600), .render-manifest.json (chmod 600), monitor.sh, monitor-prs.sh,
              hook-agent-routing.mjs, hook-loop-guards.mjs, usage-rollup.mjs, targeted-regate.mjs,
              MEMORY.md, agent-brief.md, autonomous-loop.md, restart-instructions.md,
              model-usage-log.md, telemetry/ (append-only spend record), feedback/ (39 files)
   Next:      run `/taskloop start` to arm the Monitor + ScheduleWakeup,
              or just type "start" in this directory in any future session.
              Later, `/taskloop sync` hot-repairs drift and adopts new skill rules without a stop.
```

## Idempotency notes

- **Projects initialized before the routing feature** keep working exactly as before — their memory dir has no routing rule, marker contract, hook, or profile, so behavior is byte-for-byte pre-change. To adopt routing, re-run `init` (overwrite the feedback files AND render the hook + profile together). Never hand-copy the new `feedback/*.md` into an old memory dir without the hook and profile — the routing rule references both.

- **Projects initialized before the automerge feature** behave as `LOOP_AUTOMERGE=off` — the var is absent and no lane rule exists; that is safe and needs no action. To adopt, re-run `init` and overwrite the coupled set together: the feedback files (`automerge-risk-lanes`, `watch-pr-comments`, `merge-on-approval`, `queue-triage-plan`, `pr-registry-race`, `telegram-notify-owner`, `never-self-halt-loop`, `wip-limit-open-prs`, `ticket-done-on-merge`, `draft-until-gated`, `model-effort-routing`, `loop-strategy-profiles`) AND the rendered `agent-brief.md` / `autonomous-loop.md` / `restart-instructions.md` / `monitor-prs.sh` / `review-recall.sh`. Never hand-set `LOOP_AUTOMERGE=on` in an old memory dir — its sweep, registry schema, and LOOP-PLAN vocabulary predate the lane, so the switch would sit on top of rules that cannot honor it (every PR would silently default to the review lane).

- `init` re-run on an already-configured project: ask per-file whether to overwrite. Default no.
- API key already in `.env`: reuse, don't re-prompt.
- Conflicting provider chosen on re-init: clear all provider-specific env vars before writing the new set.
