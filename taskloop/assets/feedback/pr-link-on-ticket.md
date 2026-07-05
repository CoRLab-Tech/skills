---
name: feedback-pr-link-on-ticket
description: Every PR the loop opens gets its link posted as a comment on the tracker issue, in the same iteration as the review transition — the notification ping never replaces the durable ticket comment
metadata:
  type: feedback
---

Opening a PR is not done until the tracker issue carries the PR link as a **comment**. The
notification channel (Telegram/chat) is transient; the ticket comment is the durable record the
owner actually navigates from.

**Why:** the tracker is the owner's primary review surface. An issue sitting in the review state
without its PR link forces the owner to hunt through the repo. This rule exists because the habit
drifted mid-run and the owner had to correct it — treat it as part of the atomic "open PR" step,
not an optional nicety.

**How to apply:**
- In the SAME loop step that opens the PR and transitions the issue to the review state, post a
  comment on the tracker issue with the PR link(s): `PR: <a href="<url>">#<n> — <title></a>`.
  One comment listing every PR tied to that issue.
- A follow-up PR for the same issue → post another comment when it opens.
- Checklist for the step: PR opened → registered for the watcher → **ticket comment posted** →
  issue transitioned → one notification ping. Missing any of these = the step is not done.
- Use the provider's post-comment recipe (Linear/Jira/Plane) from `references/providers/<name>.md`.
