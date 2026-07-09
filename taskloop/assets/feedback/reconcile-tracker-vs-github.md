---
name: feedback-reconcile-tracker-vs-github
description: "Periodically reconcile tracker states against GitHub PR merges — the PR watcher is edge-triggered and misses any PR merged outside its registry, stranding tickets in review"
metadata:
  type: feedback
---

The PR watcher only bookkeeps PRs whose MERGED event it catches. A PR merged outside that flow — it predates the registry, the registry was corrupt ([[feedback-pr-registry-race]]), or it merged during an incident when bookkeeping skipped — never transitions its ticket, and the ticket sits in review forever. Drift runs the other way too: a finalized open PR's ticket can slip back to the ready status.

**Why:** the PR watcher is **edge-triggered** (it catches merge events); a full reconciliation is **level-triggered** (it compares the actual states). Only the level-triggered pass repairs what the edge-triggered one missed. On one long run this found 2 of 120 merged PRs stranded in review, plus two finalized open PRs whose tickets had drifted back to the ready queue.

**How to apply — run this reconciliation periodically (on each merge wave, or every few ticks). It is idempotent and self-heals:**

1. `gh pr list --state merged --limit 120 --json number,headRefName,title,mergedAt` (once per target repo).
2. Extract the issue key from each `headRefName` — the loop's branch convention embeds it.
3. Paginate the tracker's issues once and build `key → (id, state)`; fetch the states map.
4. For each merged PR whose ticket is NOT in a completed state → transition it to `Merged` ([[feedback-ticket-done-on-merge]]).
5. Also verify every finalized OPEN PR's ticket sits in the review status, not drifted back to the ready queue.

Throttle the tracker calls (a short sleep between writes, retry on 429). Skip silently when the ticket is already correct — never fight a human's transition.

Where a project wants this without a live loop tick, run it as a background reconciler under `Monitor`: it emits one line per ticket it moves and stays silent when everything is in sync, so it doubles as a wake signal. The Plane reference implementation ships as `reconcile-merged.sh` in the project's memory dir; for other providers, drive steps 3–4 through the provider's own transition recipe.

Related: [[feedback-ticket-done-on-merge]], [[feedback-status-mirrors-work]], [[feedback-never-self-halt-loop]] (the fresh sweep is the guarantee; reconciliation is what makes the sweep authoritative).
