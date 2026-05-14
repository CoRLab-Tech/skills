# Adding a new provider

A provider is a thin adapter that lets taskloop drive any task tracker (GitHub Issues, Asana, Plane, ClickUp, ...) through the same 5-verb contract. The loop spec is provider-neutral; only the adapter changes.

## The 5-verb contract

Every provider must define:

1. **Env vars** — the credentials and identifiers needed to call the tracker
2. **`monitor.sh.tmpl`** — bash polling loop that emits one stdout line per change in the ready queue
3. **`get_issue(id)`** — fetch one issue's payload (id, title, description, branch hint, priority, state, url, labels)
4. **`transition_state(id, target)`** — move an issue between states; supported `target` values are `in_progress`, `in_review`, `done`
5. **`post_comment(id, markdown)`** — leave a comment on an issue (the loop uses this for the PR URL)

Each verb is documented as a curl/CLI recipe in `references/providers/<name>.md`. No code generation — the loop reads the recipes and executes them inline.

## Required env vars

List every variable the adapter reads from `$MEM/.env`. At minimum:

- An API token / API key
- A project or workspace identifier
- The "ready" status name (or its ID equivalent)
- The "in review" status name

Optional but recommended:

- Team / board identifier (for status enumeration)
- A polling interval override (default 60s)

Document each var with a one-line description and a pointer to where the user gets it.

## `monitor.sh.tmpl` shape

The monitor template is rendered at `init` time. Two placeholders are substituted:

- `{{ENV_FILE}}` → absolute path to `$MEM/.env`
- `{{STATE_FILE}}` → absolute path to `$MEM/.monitor-state`

Required behavior:

- Source `{{ENV_FILE}}` on every tick so token rotations take effect without restart.
- Poll the ready queue every `INTERVAL` seconds (default 60; env override `INTERVAL`).
- Compute a stable hash of the actionable issues (e.g., sorted `id|status|updatedAt` lines). Compare to `{{STATE_FILE}}` contents.
- On change, emit:
  - One header line: `[monitor] queue changed: N actionable issue(s)`
  - Up to 5 issue lines: `[monitor]  <ID>\t<status>\t<updatedAt>\t<title>`
  Then write the new hash to `{{STATE_FILE}}`.
- Wrap API calls with `|| true` (or equivalent) so a transient 5xx doesn't kill the monitor process.
- Use `set -u` selectively — do not crash on missing env vars; print a clear `[monitor] error: missing $FOO` and sleep.

Each stdout line wakes Claude via the harness's `Monitor` task, so verbosity matters: only print when the queue actually changes.

## `get_issue(id)` recipe

Should return (in the curl response, ideally a single API call):

- `id` / `identifier` — the human key the user references (e.g., `MIH-123`, `ENG-42`)
- `title`
- `description` — markdown if available, else the rendered representation
- `url` — link back to the issue in the tracker UI
- `branchHint` — a slugified branch name if the tracker offers one; otherwise the loop slugifies the title
- `priority`
- `state` — current state name
- `labels` — array of strings (used to disambiguate target service in monorepos)

If the tracker requires multiple calls, document the sequence.

## `transition_state(id, target)` recipe

`target` is one of three logical values; the adapter maps each to a tracker-specific status name (or ID):

| `target` | Meaning | Typical mapping |
|---|---|---|
| `in_progress` | The loop has started work | "In Progress" |
| `in_review` | PR is open, awaiting human review | "Ready for Review" / "In Review" / "Code Review" |
| `done` | Issue is complete (rarely used by the loop directly) | "Done" |

If the tracker uses opaque IDs (Linear's `stateId`, Jira's `transitionId`), document how to enumerate them once and cache. Note any per-current-state restrictions (Jira's workflow can forbid certain direct transitions).

## `post_comment(id, markdown)` recipe

The loop calls this with a short markdown body like:

```
PR opened: https://github.com/org/repo/pull/123
```

If the tracker doesn't accept raw markdown (e.g., Jira's ADF requirement), the adapter is responsible for the wrapper. Document the exact body schema.

## File layout

For provider `foo`:

```
references/providers/foo.md      # the adapter doc (env, recipes)
assets/monitor-foo.sh.tmpl       # the polling template
```

Then:

- Add `foo` to the `AskUserQuestion` options in `references/workflows/init.md` (Step 2 — pick the provider).
- Add the env-var block in Step 5 of `init.md` so `.env` is populated correctly.
- Add the verify-queue recipe link in `start.md` and `status.md`.

That's it — the loop spec, restart instructions, MEMORY.md template, and all 11 feedback rules are already provider-neutral and need no changes.

## Validation checklist before shipping a new provider

- [ ] All 5 verbs documented with concrete curl examples
- [ ] Monitor template emits a clean "queue changed" line and ≤5 issue lines
- [ ] Auth failures (401) are distinguishable from "queue empty" (200, zero issues)
- [ ] Status names are configurable via env, not hardcoded
- [ ] At least one end-to-end live run on a real project before marking the adapter "verified"
