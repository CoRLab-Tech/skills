# Plane provider adapter

> **Verified end-to-end against the corlab self-hosted instance (`plane.corlab.tech`, Plane v1.3.1). Ready-queue poll, state transition, and comment posting all confirmed live.**

Plane is driven **MCP-first**: the loop's in-conversation verbs (get / list / transition / comment / create) call the official **Plane MCP server** (`plane-mcp-server`, registered as the `plane` MCP server). The background `monitor.sh` cannot reach MCP — a bash poller has no MCP access — so it polls the **REST API** with curl. Every verb also has a curl fallback for when the MCP server isn't available in the current project.

Works against both self-hosted Plane and Plane Cloud (`https://api.plane.so`); only `PLANE_BASE_URL` / `PLANE_WORKSPACE_SLUG` differ.

## Prerequisite: the Plane MCP server

The MCP-first verbs require the `plane` MCP server to be reachable from the current project. Register it **once at user scope** so every repo the loop runs in can see it:

```bash
uvx --help >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh   # installs uv/uvx
claude mcp add plane -s user \
  -e PLANE_API_KEY="<token>" \
  -e PLANE_WORKSPACE_SLUG="<slug>" \
  -e PLANE_BASE_URL="https://<host>/api" \
  -- "$(command -v uvx)" plane-mcp-server stdio
```

MCP tools load at Claude Code **startup** — after adding the server, a restart (or `/mcp` reconnect) is needed before the `plane` tools appear. The token, slug, and base URL are baked into the MCP server's env, so MCP tool calls only pass `project_id` and `work_item_id` — never the slug or token.

If the `plane` MCP server is not present, fall back to the curl recipes below (they need only `$MEM/.env`).

## Required env vars

```
PLANE_API_KEY            # Workspace API token — Settings > API Tokens (/settings/api-tokens/). Sent as the X-Api-Key header.
PLANE_BASE_URL           # API root, e.g. https://plane.corlab.tech/api  (Plane Cloud: https://api.plane.so). No trailing /v1.
PLANE_WORKSPACE_SLUG     # workspace slug, e.g. corlab
PLANE_PROJECT_ID         # UUID of the project (resolved at init)
PLANE_PROJECT_IDENTIFIER # short project code, e.g. MCP — builds the human key <IDENTIFIER>-<sequence_id>
PLANE_READY_STATUS       # ready state name, default "Todo"
PLANE_REVIEW_STATUS      # post-PR review state name, default "In Review"
PLANE_BLOCKED_STATUS     # blocked/timeboxed landing state, default "Blocked" (init creates it if missing)
```

These mirror the three env vars the `plane` MCP server itself was registered with (`PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`, `PLANE_BASE_URL`) so the curl and MCP paths stay consistent.

## Auth (REST)

Every REST request carries the token in the **`X-Api-Key`** header (no `Bearer`, no `Authorization`):

```
-H "X-Api-Key: $PLANE_API_KEY" \
-H "Accept: application/json"
```

The public token API lives under **`/api/v1/`** (NOT `/api/`, which is the cookie-authed app API and 401s the token). Full base for project calls:

```
$PLANE_BASE_URL/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PLANE_PROJECT_ID
```

Project-scoped writes require the token's user to be a **member of that project** — a workspace admin who is not a project member gets `403 "You do not have permission to perform this action."` Add the user to the project (or create the project as that user) at init.

## States: resolve UUIDs once

Plane transitions and PQL filters use **state UUIDs**, not names. The default project ships five states:

| Name | Group |
|---|---|
| Backlog | `backlog` |
| Todo | `unstarted` |
| In Progress | `started` |
| Done | `completed` |
| Cancelled | `cancelled` |

New work items default to **Backlog**, so `Todo` is a clean "ready" signal (a human promotes Backlog → Todo when the item is actionable). There is **no review state by default** — see the review-state note under init.

Enumerate states and cache the UUIDs for `PLANE_READY_STATUS`, `In Progress`, `PLANE_REVIEW_STATUS`, `Done`:

- **MCP:** `list_states(project_id=$PLANE_PROJECT_ID)` → array of `{id, name, group}`.
- **curl:**
  ```bash
  set -a; . "$MEM/.env"; set +a
  curl -sS -H "X-Api-Key: $PLANE_API_KEY" -H "Accept: application/json" \
    "$PLANE_BASE_URL/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PLANE_PROJECT_ID/states/"
  ```
  Returns `results[]` of `{id, name, group, ...}`.

## Verify ready queue (one-shot health check)

Used at `init`, `start`, and `status`.

- **MCP:** resolve the ready state UUID from `list_states`, then
  `list_work_items(project_id=$PLANE_PROJECT_ID, pql='state = "<ready-uuid>"', expand="state", fields="id,sequence_id,name,priority,state")`.
  PQL filters by state **UUID** (`state = "<uuid>"`) or by group (`stateGroup = "unstarted"`) — there is no filter-by-state-**name**, so resolve the name→UUID first.
- **curl:** fetch and filter client-side by the expanded state name (robust; no dependency on undocumented filter params):
  ```bash
  set -a; . "$MEM/.env"; set +a
  curl -sS -G -H "X-Api-Key: $PLANE_API_KEY" -H "Accept: application/json" \
    --data-urlencode "expand=state" \
    --data-urlencode "order_by=-updated_at" \
    --data-urlencode "per_page=100" \
    "$PLANE_BASE_URL/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PLANE_PROJECT_ID/issues/"
  ```
  The response is **cursor-paginated**: work items are under `results[]`; each has `sequence_id`, `priority`, `updated_at`, `name`, and (with `expand=state`) a nested `state.{name,group,id}`. Keep only rows where `state.name == PLANE_READY_STATUS`.

A 200 with a (possibly empty) `results[]` means auth + slug + project ID are valid. A 401 means the token is wrong; a 404 means the slug or project ID is wrong.

The human key the user references is `<PLANE_PROJECT_IDENTIFIER>-<sequence_id>` (e.g. `MCP-1`).

## Get-issue recipe

- **MCP:** `retrieve_work_item(project_id, work_item_id, expand="state,assignees,labels")` for the UUID, or `retrieve_work_item_by_identifier(work_item_identifier="MCP-1", expand="state")` when you only have the human key — pass the full `<IDENTIFIER>-<sequence_id>` string as a single argument (the tool splits it internally; there is no separate project_id/sequence_id param). `list_work_items` already returns enough (`id`, `sequence_id`, `name`, `priority`, `state`) to branch from — prefer it for the queue sweep.
- **curl:** `GET .../issues/<work_item_uuid>/?expand=state,labels` returns `id`, `sequence_id`, `name`, `description_html`, `priority`, `state`, `labels`.

Field notes:
- `description_html` is HTML (not markdown). Read it as the issue body.
- Plane surfaces **no suggested git branch** — slugify `name` into `feature/<IDENTIFIER>-<sequence_id>-<slug>` yourself.
- `labels` is an array of UUIDs unless expanded; use `expand=labels` to get names for monorepo target disambiguation.

## Transition state recipe

Set the work item's `state` to the target state UUID (resolved from the states table above).

- **MCP:** `update_work_item(project_id, work_item_id, state="<state-uuid>")`.
- **curl:**
  ```bash
  curl -sS -X PATCH -H "X-Api-Key: $PLANE_API_KEY" -H "Content-Type: application/json" \
    "$PLANE_BASE_URL/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PLANE_PROJECT_ID/issues/<work_item_uuid>/" \
    -d '{"state":"<state-uuid>"}'
  ```

Supported targets used by the loop:

| Logical target | Plane state name | Source |
|---|---|---|
| `in_progress` | `In Progress` | default state |
| `in_review` | `$PLANE_REVIEW_STATUS` | env (default `In Review`) |
| `blocked` | `$PLANE_BLOCKED_STATUS` | env (default `Blocked`; created at init in the `backlog` group, color `#EF4444`) |
| `done` | `Done` | default state |

## Post-comment recipe

Comment bodies are **HTML** (`comment_html`), not markdown. Wrap plain text/links in a `<p>…</p>`.

- **MCP:** `create_work_item_comment(project_id, work_item_id, comment_html="<p>PR opened: https://github.com/org/repo/pull/123</p>")`.
- **curl:**
  ```bash
  curl -sS -X POST -H "X-Api-Key: $PLANE_API_KEY" -H "Content-Type: application/json" \
    "$PLANE_BASE_URL/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PLANE_PROJECT_ID/work-items/<work_item_uuid>/comments/" \
    -d '{"comment_html":"<p>PR opened: <a href=\"https://github.com/org/repo/pull/123\">#123</a></p>"}'
  ```

The comment (and attachment) paths accept both `/issues/<id>/comments/` and `/work-items/<id>/comments/` — they are aliases.

## Create-backlog-issue recipe (TODO mirroring)

Used by the `todo-opens-backlog-task` rule. New Plane work items land in the **project's default state** — `Backlog` on a stock project (verified live), but the default flag is mutable per project. Check once at init that the state with `"default": true` in the `/states/` response belongs to the `backlog` group; if it does, simply omit `state` below, otherwise pass the Backlog state UUID explicitly.

- **MCP:** `create_work_item(project_id, name="<distilled TODO title>", description_html="<p>context, file:line, deferral reason</p>")`.
- **curl:**
  ```bash
  curl -sS -X POST -H "X-Api-Key: $PLANE_API_KEY" -H "Content-Type: application/json" \
    "$PLANE_BASE_URL/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PLANE_PROJECT_ID/work-items/" \
    -d '{"name":"<title>","description_html":"<p>context, file:line, deferral reason</p>"}'
  ```

The PR doesn't exist yet at creation time — after `gh pr create`, post the PR URL onto this issue via the post-comment recipe above.

The response carries `id` (UUID) and `sequence_id` — the human key to write back into the code comment is `<PLANE_PROJECT_IDENTIFIER>-<sequence_id>` (e.g. `TODO(MCP-7): ...`). Never pass the ready-state UUID here — backlog only, per [[feedback-only-ready-not-backlog]].

## Project + identifier + review-state resolution (init only)

The user gives the project **name**; resolve it to the UUID and identifier:

```bash
set -a; . "$MEM/.env"; set +a
curl -sS -H "X-Api-Key: $PLANE_API_KEY" -H "Accept: application/json" \
  "$PLANE_BASE_URL/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/" \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); r=d.get("results",d);
[print(p["id"], p.get("identifier"), p.get("name")) for p in (r if isinstance(r,list) else [])]'
```

Match on `name`, then store `PLANE_PROJECT_ID` (the `id`) and `PLANE_PROJECT_IDENTIFIER` (the `identifier`). If several match, list them and re-ask.

**Review state:** default Plane has no `In Review` state. At init, check `list_states` for `PLANE_REVIEW_STATUS`. If absent, either:
- create it (confirm first — it changes the user's project):
  - **MCP:** `create_state(project_id, name="In Review", color="#F59E0B", group="started")` — `color` (a hex string) is **required**.
  - **curl:** `POST .../states/ -d '{"name":"In Review","color":"#F59E0B","group":"started"}'` — omitting `color` returns 400.
- or ask the user to point `PLANE_REVIEW_STATUS` at an existing state.

## Notes and quirks

- **`/api/v1/` prefix**, header **`X-Api-Key`** — the single most common self-host mistake is hitting `/api/` (session-authed) and getting a misleading 401.
- New work items default to **Backlog**, not Todo — the ready queue stays clean without extra config.
- Cursor pagination: iterate `next_cursor` only if the ready queue can exceed `per_page=100`; the loop takes one issue at a time so page one ordered by `-updated_at` is enough for the sweep.
- PQL filters on state **UUID** / **group**, not state name — always resolve the name via `list_states` first. Group `unstarted` includes only `Todo` by default here, but a project can add more unstarted states, so filter by the specific `Todo` UUID, not the group. See [[feedback-only-ready-not-backlog]].
- Comments and descriptions are HTML, not markdown — do not post raw markdown.
- MCP tools take `project_id` + `work_item_id` (UUIDs); the slug/token/base come from the MCP server's own env. curl calls pass everything explicitly from `$MEM/.env`.
