---
name: feedback-no-secrets-in-code
description: "Scan every diff for secrets before commit — tokens, keys, passwords, connection strings never reach git"
metadata:
  type: feedback
---

Before every commit, scan the staged diff for secrets. API keys, tokens, private keys, passwords, connection strings with credentials, and signed URLs never reach git history — not in code, not in test fixtures, not in "temporary" debug output, not in screenshots committed as PR evidence.

**Why:** A secret in git history is compromised even after a revert — history is forever and forks/clones multiply it. Rotating leaked credentials costs hours and trust; the pre-commit scan costs seconds.

**How to apply:**
- Scan the staged diff before each commit: use `gitleaks protect --staged` when the tool is available; otherwise grep the diff for the classic shapes — `AKIA[0-9A-Z]{16}`, `ghp_`/`github_pat_`, `sk-`/`sk_live_`, `xox[bpars]-`, `-----BEGIN .*PRIVATE KEY`, `Authorization: (Bearer|Basic) [A-Za-z0-9+/=._-]{20,}`, `://[^/\s:]+:[^@\s]+@` (URL userinfo credentials), and case-insensitive `(api_?key|secret|token|passwd|password)\s*[:=]\s*['"][^'"]{8,}`.
- `.env*` files are never staged (verify the repo's `.gitignore` covers them; if not, add it as part of the change). The loop's own provider tokens live in the taskloop memory dir, never inside any repo.
- Values needed at runtime come from env vars or the project's secret store; tests use obviously-fake fixtures (`test-key-000...`), never real or realistic credentials.
- On a hit: unstage, replace with an env/config lookup, and re-scan. If a real secret was already committed on the branch, rewrite the branch history before pushing (the branch is unpushed local work at this point) and say so in the PR body if any doubt remains.
- Screenshots/recordings for PR evidence ([[feedback-pr-visual-evidence]]) are checked too — blur or crop tokens, signed URLs, and real user data before committing them.
