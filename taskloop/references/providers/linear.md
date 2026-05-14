# Linear provider adapter

> **Verified end-to-end against the ERx setup; this is the reference implementation.**

The Linear adapter uses Linear's GraphQL API at `https://api.linear.app/graphql` with a personal API key passed in the `Authorization` header (no `Bearer` prefix).

## Required env vars

```
LINEAR_API_KEY      # personal API key from https://linear.app/settings/api
LINEAR_PROJECT_ID   # UUID of the Linear project (resolved at init)
LINEAR_TEAM_ID      # UUID of the team that owns issue workflow states
```

## Auth

Every request:

```
-H "Authorization: $LINEAR_API_KEY" \
-H "Content-Type: application/json"
```

No `Bearer` prefix. The key is a 40+ char personal API key.

## Verify Todo queue (one-shot health check)

Used at `init` time and by `start` / `status` workflows.

```bash
set -a; . "$MEM/.env"; set +a
curl -sS -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"query{project(id:\\\"$LINEAR_PROJECT_ID\\\"){issues(first:10,filter:{state:{name:{eq:\\\"Todo\\\"}}}){nodes{identifier title state{name type} priority updatedAt}}}}\"}"
```

A 200 with `data.project.issues.nodes` (possibly empty) means auth + project ID are valid. A 401 means the API key is wrong; a `null` project means the project ID is wrong.

The ready status name is `Todo` (verbatim). Do **not** include `Backlog`, `In Progress`, `Ready for Review`, or `Done` — see the `only-ready-not-backlog` feedback rule.

## Get-issue recipe

Fetch the full payload the loop needs to branch and implement:

```graphql
query {
  issue(id: "<identifier-or-uuid>") {
    identifier
    title
    description
    url
    gitBranchName
    priority
    state { name type }
    labels { nodes { name } }
    project { name }
    team { key }
  }
}
```

- `identifier` is the human key like `MIH-123`. The `id` arg accepts either the UUID or the identifier.
- `gitBranchName` is Linear's suggested branch name (`mih-123-some-slug`); prefer it over hand-rolling a slug.
- `description` is markdown.

## Transition state recipe

Linear uses `WorkflowState` UUIDs, not status names. To transition:

1. **One-time** — enumerate states for the team and cache the IDs for `In Progress` and `Ready for Review`:

   ```graphql
   query {
     team(id: "<LINEAR_TEAM_ID>") {
       states {
         nodes { id name type }
       }
     }
   }
   ```

   See https://linear.app/docs/api for state types (`unstarted`, `started`, `completed`, …).

2. **Each transition** — mutation:

   ```graphql
   mutation {
     issueUpdate(id: "<issue-uuid>", input: { stateId: "<state-uuid>" }) {
       success
       issue { state { name } }
     }
   }
   ```

   The `id` here must be the **UUID**, not the `MIH-123` identifier. Resolve via the get-issue query if you only have the identifier.

Supported targets used by the loop:

| Logical target | Linear state name |
|---|---|
| `in_progress` | `In Progress` |
| `in_review` | `Ready for Review` |
| `done` | `Done` |

## Post-comment recipe

```graphql
mutation {
  commentCreate(input: { issueId: "<issue-uuid>", body: "<markdown body>" }) {
    success
    comment { id url }
  }
}
```

The `body` is markdown. Use it to post the GitHub PR URL after `gh pr create`.

## Project-ID resolution recipe (init only)

The user gives the project **name**; resolve to UUID:

```graphql
query {
  projects(filter: { name: { eq: "<name>" } }) {
    nodes { id name }
  }
}
```

If multiple match, list them with their teams and re-ask the user. If zero match, ask the user to confirm the exact name (Linear is case-sensitive on `eq`; consider `contains` as a fallback).

To resolve the team ID at the same time:

```graphql
query {
  teams(filter: { name: { eq: "<team name>" } }) {
    nodes { id name key }
  }
}
```

## Notes and quirks

- The Linear GraphQL endpoint rate-limits aggressively; the polling monitor sleeps 60s between ticks for this reason.
- `state.type` values: `triage`, `backlog`, `unstarted`, `started`, `completed`, `canceled`. Loop filters on **name** `Todo`, not on `type`, because `unstarted` also includes `Backlog`.
- Some Linear workflows do not have a `Ready for Review` state. At init time, verify it exists; if missing, ask the user to create it or pick another review-stage state.
