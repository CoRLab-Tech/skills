# Jira Cloud provider adapter

> **Recipes documented; not verified live by the skill author. First-run validation recommended.**

The Jira adapter targets Jira Cloud's REST API v3 (`https://<host>/rest/api/3/...`) using HTTP basic auth with email + API token.

## Required env vars

```
JIRA_HOST            # e.g. mycorp.atlassian.net (no protocol prefix)
JIRA_EMAIL           # Atlassian account email
JIRA_API_TOKEN       # token from https://id.atlassian.com/manage-profile/security/api-tokens
JIRA_PROJECT_KEY     # 2–4 uppercase letters, e.g. ENG
JIRA_BOARD_ID        # numeric, from the board URL
JIRA_READY_STATUS    # the "ready for the loop" status name, e.g. "Selected for Development"
JIRA_REVIEW_STATUS   # post-PR status name, e.g. "In Review"
```

## Auth

HTTP basic with `email:token`, base64-encoded:

```bash
set -a; . "$MEM/.env"; set +a
# NB: GNU base64 line-wraps at 76 chars and today's Atlassian tokens are ~190 chars — the wrapped
# header silently 401s. Prefer curl's -u form; if you must build the header, disable wrapping:
AUTH=$(printf '%s' "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64 | tr -d '\n')
curl -sS -H "Authorization: Basic $AUTH" -H "Accept: application/json" ...
```

Or use curl's `-u "$JIRA_EMAIL:$JIRA_API_TOKEN"` shorthand.

## Verify Ready queue (one-shot health check)

Used at `init`, `start`, and `status`:

```bash
JQL="project=$JIRA_PROJECT_KEY AND status=\"$JIRA_READY_STATUS\""
curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -G "https://$JIRA_HOST/rest/api/3/search/jql" \
  --data-urlencode "jql=$JQL" \
  --data-urlencode "fields=summary,status,priority,updated" \
  --data-urlencode "maxResults=10"
```

A 200 with an `issues[]` array (possibly empty) means auth + project key + status name are valid. (`/rest/api/3/search` — without `/jql` — was removed by Atlassian in 2025; a 410 there is the old endpoint, not a config error. Pagination on `/search/jql` uses `nextPageToken`, not `startAt`.) A 401 means email/token wrong; a 400 with `errorMessages` usually means the status name doesn't exist verbatim.

## Get-issue recipe

```bash
curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "https://$JIRA_HOST/rest/api/3/issue/<KEY>?fields=summary,description,status,priority,labels"
```

`<KEY>` is the human key like `ENG-123`. Returns:

- `fields.summary` — title
- `fields.description` — ADF (Atlassian Document Format) JSON, **not plain markdown**. Use the `expand=renderedFields` param if you want HTML.
- `fields.status.name` — current state
- `fields.priority.name`
- `fields.labels[]`

For a branch name, slugify `fields.summary` yourself — Jira doesn't surface a suggested branch.

## Transition state recipe

Jira transitions use **transition IDs**, not status names. The available transitions depend on the workflow and the current state.

1. **Enumerate transitions for an issue** (current state-dependent):

   ```bash
   curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
     "https://$JIRA_HOST/rest/api/3/issue/<KEY>/transitions"
   ```

   Response: `transitions[].id` and `transitions[].to.name`. Match `to.name` to the target status name.

2. **Apply the transition**:

   ```bash
   curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
     -X POST -H "Content-Type: application/json" \
     "https://$JIRA_HOST/rest/api/3/issue/<KEY>/transitions" \
     -d '{"transition":{"id":"<transition-id>"}}'
   ```

Cache transition IDs per status if you're confident they're stable; otherwise re-enumerate each time.

Supported targets used by the loop:

| Logical target | Source of target status name |
|---|---|
| `in_progress` | hardcoded `In Progress` (override if your workflow differs) |
| `in_review` | `$JIRA_REVIEW_STATUS` |
| `blocked` | hardcoded `Blocked` (override if your workflow differs) — the landing state for timeboxed/unactionable tickets (`status-mirrors-work`, `fail-gracefully-timebox`); verify at init that a transition to it exists from the working statuses, and create/choose one if not |
| `done` | hardcoded `Done` |

## Post-comment recipe

Jira Cloud requires **ADF** (Atlassian Document Format) — plain strings are rejected. See https://developer.atlassian.com/cloud/jira/platform/apis/document/.

Minimal ADF wrapper for a single paragraph:

```bash
BODY_TEXT="PR opened: https://github.com/foo/bar/pull/123"
curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -X POST -H "Content-Type: application/json" \
  "https://$JIRA_HOST/rest/api/3/issue/<KEY>/comment" \
  -d "$(cat <<EOF
{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [
          { "type": "text", "text": "$BODY_TEXT" }
        ]
      }
    ]
  }
}
EOF
)"
```

For multi-paragraph or markdown-like bodies, build the ADF document node-by-node. The ADF spec has explicit node types for `bulletList`, `codeBlock`, `link`, etc.

## Create-backlog-issue recipe (TODO mirroring)

Used by the `todo-opens-backlog-task` rule. Create the issue via the standard create endpoint (body is ADF, like comments):

```bash
curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -X POST -H "Content-Type: application/json" \
  "https://$JIRA_HOST/rest/api/3/issue" \
  -d "$(cat <<EOF
{
  "fields": {
    "project": { "key": "$JIRA_PROJECT_KEY" },
    "summary": "<distilled TODO title>",
    "issuetype": { "name": "Task" },
    "description": {
      "type": "doc", "version": 1,
      "content": [ { "type": "paragraph", "content": [ { "type": "text", "text": "<context, file:line, deferral reason>" } ] } ]
    }
  }
}
EOF
)"
```

The response's `key` (e.g. `ENG-142`) is written back into the code comment: `TODO(ENG-142): ...`. The PR doesn't exist yet at creation time — after `gh pr create`, post the PR URL onto the issue via the post-comment recipe. New issues land in the workflow's **initial status** — verify once per project that it is a backlog-type status and NOT `$JIRA_READY_STATUS`; if the initial status is the ready status, immediately transition the created issue to the backlog status via the transition recipe, or the loop will feed itself work.

## Project-key resolution (init)

The user gives the project key directly (e.g. `ENG`) — no name-to-key lookup needed. Validate by:

```bash
curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "https://$JIRA_HOST/rest/api/3/project/$JIRA_PROJECT_KEY"
```

A 200 with `key` matching the input confirms the project exists.

## Notes and caveats

- ADF round-tripping is lossy — a comment written as ADF and read back will not equal the source string. If you need to detect "did I already comment this PR URL?", store a marker locally.
- The `status` name match is exact and case-sensitive. If the user's workflow uses non-English names (e.g. `En Cours`), pass them verbatim in `JIRA_READY_STATUS` / `JIRA_REVIEW_STATUS`.
- These recipes have not been live-tested by the skill author. On first run, validate each verb (get-issue, transition, comment) manually with one issue before letting the loop drive.
