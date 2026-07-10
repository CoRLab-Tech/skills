---
name: feedback-draft-until-gated
description: "Every loop PR opens as a DRAFT and stays draft until ALL gates pass; marking it ready-for-review is the same step as the review transition and the owner ping, so the owner can never merge an ungated PR"
metadata:
  type: feedback
---

A PR that has not passed the loop's gates must be a **draft**, not ready-for-review — otherwise the owner can merge it before the gates run. Draft status is the enforcement mechanism: GitHub blocks merge on a draft, so the owner only ever sees mergeable PRs that already passed the full gate.

1. Open every PR with `gh pr create --draft`. It stays a draft through CI and the review / critique / security / QA gates.
2. ONLY when ALL gates are green does the loop, in one step: `gh pr ready <N>` → register the PR for the watcher (recording `gatedHead` — [[feedback-automerge-risk-lanes]]) → **post the PR link as a comment on the tracker issue** → move the issue to the review status ([[feedback-status-mirrors-work]]) → ping the owner once ([[feedback-telegram-notify-owner]]; for a lane-auto PR the ping says the loop will self-merge unless the owner comments). These are not five optional niceties; they are one event — the "gates passed" signal. Missing any of them means the step is not done.

   **The ticket comment is not optional and the ping does not replace it.** The notification channel is transient; the ticket comment is the durable record the owner navigates from, and the tracker is their primary review surface. An issue sitting in the review state without its PR link forces the owner to hunt through the repo. Post `PR: <link> — <title>`, one comment listing every PR tied to that issue, via the provider's post-comment recipe. A follow-up PR for the same issue posts another comment when it opens.
3. If a gate REJECTS or CI is red, the PR stays draft: fix on the branch, re-run the affected gates ([[feedback-targeted-regate-on-fixes]]), and only then ready + transition + ping. A ticket that bounced back to In Progress re-readies and re-pings as a follow-up.

**Why:** the gates are worthless if the owner can merge before they finish. Draft is the only state GitHub enforces mechanically, so it is the only honest "not yet verified" marker.

**How to apply:**

- Never `gh pr ready` before every gate is green. The review transition in the loop spec implies the `gh pr ready` that precedes it.
- **"Green" means green CI**, which runs on drafts: a `on: pull_request` workflow with no draft guard runs the verify job on draft PRs, so waiting for it while the PR is still a draft is valid and required. The one exception is a check that never executed the code — see [[feedback-ci-failure-triage]], under which a green local gate plus an explicit "CI was red for billing/infra, I verified locally" PR comment is what unlocks `gh pr ready`.
- If a freshly-opened PR shows `no checks reported`, re-trigger CI by pushing a **real-diff** commit (an EMPTY commit does not fire `synchronize`); if that still does not start CI, recreate the PR on a fresh branch (a fresh `opened` event reliably triggers it).
- Do **not** use `gh pr close && gh pr reopen` to re-trigger: closing a PR detaches its CI triggers, so later pushes silently produce no run.
- `ready_for_review` is NOT in the default `pull_request` event types, so `gh pr ready` alone does not start CI. Never mark ready on a PR whose verification — local or remote — never ran.
- Drafts in the gates phase still count against the WIP cap — they are active work heading to review ([[feedback-wip-limit-open-prs]]).
