# Status workflow

Print a quick diagnostic for the current project's taskloop. Read-only — no state changes.

## Step 1 — Resolve memory dir and detect provider

```bash
SLUG=$(pwd | sed 's|/|-|g')
MEM="$HOME/.claude/projects/${SLUG}/memory"
```

If `$MEM` does not exist, print `taskloop is not initialized for this project — run /taskloop init` and stop.

Read `$MEM/.env`. Detect the provider:

- If `LINEAR_API_KEY` is present → provider is `Linear`
- Else if `PLANE_API_KEY` is present → provider is `Plane`
- Else if `JIRA_API_TOKEN` is present → provider is `Jira`
- Else → print `unable to detect provider from .env` and stop

Also read `LOOP_STRATEGY` (default `auto`) and `LOOP_AUTOMERGE` (default `off`) for the summary.

## Step 2 — Find the running Monitor task

Search the harness's background task list for any task whose `command` starts with `$MEM/monitor.sh`. Record its `task_id` and its `started_at` if available.

If none is running, mark it as `not running`.

## Step 3 — Curl the provider's "ready" queue

Source `$MEM/.env` and run the appropriate one-shot curl. Capture the issues array.

### Linear

Use the GraphQL query from `references/providers/linear.md` ("Verify Todo queue" recipe). Parse `data.project.issues.nodes`.

### Plane

Use the REST curl from `references/providers/plane.md` ("Verify ready queue" recipe). Parse `results[]` and keep rows where `state.name == PLANE_READY_STATUS`.

### Jira

Use the REST search from `references/providers/jira.md` ("Verify Ready queue" recipe). Parse `issues[]`.

Pretty-print the first 5 entries as a table with columns: `id`, `priority`, `updatedAt`, `title`.

## Step 4 — Last PR opened

```bash
gh pr list --author @me --limit 1 --json number,title,url,createdAt,state
```

Pretty-print the single entry. If none, say `no PRs found for this user`.

## Step 5 — Print summary

Format the three sections as a single readable block:

```
taskloop status — <project name> (<Provider>)

Monitor:    <running task_id since <started_at>>  |  <not running>
Config:     strategy=<auto|fast|balanced|heavy>  automerge=<on|off>
Ready queue (N actionable):
  <ID>   <priority>   <updatedAt>   <title>
  ...

Last PR:
  #<num>  <state>  <title>
  <url>
```

Do not modify any state, do not arm Monitor, do not call ScheduleWakeup.
