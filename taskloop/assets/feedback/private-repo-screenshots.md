---
name: feedback-private-repo-screenshots
description: "For private GitHub repos, host PR screenshots inside the PR branch — not raw.githubusercontent.com URLs"
metadata:
  type: feedback
---

For PRs against **private** GitHub repos, do not reference screenshots via `raw.githubusercontent.com/<owner>/<repo>/...` URLs. Those URLs require auth and render as broken images in the PR for anyone without a valid GitHub session against that repo. Instead, commit screenshots into the PR branch itself.

**Why:** A prior PR had screenshots pushed to a separate `assets/...` branch and referenced via `raw.githubusercontent.com`; they all rendered as broken in the PR until they were moved into the PR branch. Public-repo URLs work without auth; private-repo URLs do not. Hosting the screenshots inside the PR branch ensures the GitHub web UI renders them via its session cookie, no extra plumbing.

**How to apply:**
- Commit screenshots into the PR branch under `.pr-screenshots/<issue-key>/` and reference them in the PR body via `https://github.com/<owner>/<repo>/blob/<sha>/.pr-screenshots/<issue-key>/<file>.png?raw=1` — these render with the reviewer's GitHub session.
- Alternatively, rely on the GitHub PR's **Files changed** tab, which renders image files inline.
- Lifecycle (deterministic, no cleanup step): the folder **ships with the merge** as the change's visual record. Keep it small — a handful of compressed PNGs per issue, no videos (link a comment attachment for those). It is an explicit, intentional exemption from the scoped-diff rule ([[feedback-minimal-diff-scope]]); never add a "remove before merge" note that no step executes, and never push cleanup commits after the gates have gone green.
- Do NOT use `raw.githubusercontent.com` URLs for private repos.
- Skip the separate `assets/<slug>-screenshots` branch — it adds cleanup overhead and the URLs don't render anyway.
- Linked to [[feedback-pr-visual-evidence]].
