# GitHub Issues provider

Drives the 6-verb contract against GitHub Issues via the `gh` CLI. States are modelled as **labels**, because GitHub Issues has no workflow states.

> **Not to be confused with `monitor-prs.sh`.** That script is the loop's eyes on its own *pull requests* and runs for every provider. This adapter supplies the *ready queue* the loop pulls work from.

> **Status: not verified end-to-end.** The recipes below are individually correct `gh` invocations, but the adapter has not yet driven a full loop iteration on a real repository. Run one before removing this notice.

## Prerequisite

`gh` authenticated against the org (`gh auth status`), and `jq` on `PATH`. `gh` reads `GITHUB_TOKEN` from the environment automatically when present; otherwise it uses the stored `gh auth` credentials.

## Env vars

```
GITHUB_REPO=<org>/<repo>            # e.g. CoRLab-Tech/erx
GITHUB_TOKEN=<PAT with `repo`>      # optional — omit to use the `gh auth` session
READY_LABEL="ready"                 # the queue the loop consumes
IN_PROGRESS_LABEL="in-progress"
IN_REVIEW_LABEL="in-review"
BLOCKED_LABEL="blocked"
MERGED_LABEL="merged"
```

**Backlog is the absence of `READY_LABEL`.** Any open issue without it belongs to the owner's triage queue, which is exactly what `queue-triage-plan` requires — the loop never feeds itself.

## Two decisions this adapter makes, and why

**1. A merged PR labels the issue `merged` and leaves it OPEN. The loop never closes an issue.**

GitHub Issues has only `open` and `closed`. `ticket-done-on-merge` says: stop at "Merged", never claim the owner's completion state. Closing *is* that completion state here, so the loop adds `MERGED_LABEL` and stops. The owner closes.

The consequence is a rule the loop must obey when writing PR bodies:

> **Never use a closing keyword.** Write `Refs #123`, not `Closes #123` / `Fixes #123` / `Resolves #123`. A closing keyword makes GitHub close the issue on merge, which hands the loop a decision that is not its to take.

For the same reason the adapter does **not** use `gh issue develop` to create branches: a branch linked to an issue can auto-close it when its PR merges, and an auto-close nobody asked for is worse than a branch name typed by hand.

**2. The branch name carries the issue number, in a fixed shape.**

Two rules parse the issue key straight out of `headRefName`: `pr-registry-race` (which rebuilds the PR registry from `gh pr list`) and `reconcile-tracker-vs-github`. They need a shape they can regex. This adapter pins:

```
<branch-prefix>/issue-<N>-<slug>          e.g.  dascalmi/issue-123-add-retry
```

with the extraction regex `issue-(\d+)`. `ISSUE_PREFIX` for this provider is the literal string `issue`, so the shared `<prefix>-(\d+)` machinery works unchanged. Do not accept `gh issue develop`'s default `123-title` shape — a bare leading number matches far too much.

## Verify queue (health check — `init`, `start`, `status`)

```bash
set -a; . "$MEM/.env"; set +a
gh issue list --repo "$GITHUB_REPO" --label "$READY_LABEL" --state open \
  --json number,title,updatedAt,labels --limit 10
```

Exit 0 with a JSON array (possibly `[]`) means auth and repo are valid. A bad token or an unreachable repo exits non-zero — **an empty queue and a dead token must never look alike**, and the monitor below keeps them apart.

## `get_issue(id)`

```bash
gh issue view "$ID" --repo "$GITHUB_REPO" \
  --json number,title,body,url,labels,assignees,milestone
```

Mapping: `number` → id (referenced as `#123`), `title`, `body` → description (raw markdown), `url`, `labels[].name` → labels. Priority, if the project uses it, comes from labels (`P0`, `P1`, …). There is no branch hint — the loop names the branch per the convention above.

## `transition_state(id, target)`

```bash
case "$TARGET" in
  in_progress) gh issue edit "$ID" --repo "$GITHUB_REPO" \
                 --remove-label "$READY_LABEL" --add-label "$IN_PROGRESS_LABEL" ;;
  in_review)   gh issue edit "$ID" --repo "$GITHUB_REPO" \
                 --remove-label "$IN_PROGRESS_LABEL" --add-label "$IN_REVIEW_LABEL" ;;
  blocked)     gh issue edit "$ID" --repo "$GITHUB_REPO" \
                 --remove-label "$IN_PROGRESS_LABEL" --add-label "$BLOCKED_LABEL" ;;
  done)        gh issue edit "$ID" --repo "$GITHUB_REPO" \
                 --remove-label "$IN_REVIEW_LABEL" --add-label "$MERGED_LABEL" ;;   # stays OPEN
esac
```

`gh issue edit --remove-label` on a label the issue does not carry is an error; pass `|| true` when the previous state is uncertain, or read `labels` first.

## `post_comment(id, markdown)`

```bash
gh issue comment "$ID" --repo "$GITHUB_REPO" --body "PR: $PR_URL — $PR_TITLE"
```

GitHub takes raw markdown — no wrapper, unlike Jira's ADF or Plane's `comment_html`.

## `create_backlog_issue(title, body)`

```bash
URL=$(gh issue create --repo "$GITHUB_REPO" --title "$TITLE" --body "$BODY")   # no --label ready
NUM=${URL##*/}
```

Omitting `READY_LABEL` lands it in the backlog, satisfying `queue-triage-plan`'s "only the explicit ready status is a work queue". `gh issue create` prints the issue URL on stdout; the trailing path segment is the number.

## Label bootstrap

At `init`, confirm the five labels exist and offer to create the missing ones (ask first — creating labels mutates the owner's repo):

```bash
gh label list --repo "$GITHUB_REPO" --json name -q '.[].name'
gh label create ready       --repo "$GITHUB_REPO" --color 0E8A16 --description "taskloop: actionable queue"
gh label create in-progress --repo "$GITHUB_REPO" --color FBCA04
gh label create in-review   --repo "$GITHUB_REPO" --color 1D76DB
gh label create blocked     --repo "$GITHUB_REPO" --color B60205
gh label create merged      --repo "$GITHUB_REPO" --color 5319E7 --description "taskloop: PR merged; close when accepted"
```

## What this provider makes cheaper

`reconcile-tracker-vs-github` normally paginates a foreign tracker's API to compare states against GitHub merges. Here both sides are GitHub, one auth, one CLI — see `assets/reconcile-merged-github.sh.tmpl`, which is a fraction of the Plane equivalent.
