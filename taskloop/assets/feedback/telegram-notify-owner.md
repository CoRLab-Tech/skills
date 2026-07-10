---
name: feedback-telegram-notify-owner
description: Ping the owner on Telegram (~/.claude/bin/tg-notify, creds in the macOS Keychain) at attention-worthy moments — blocked, review-ready with all PR links, auto-merged, or gone idle
metadata:
  type: feedback
---

The loop pings the owner on Telegram via the global helper `~/.claude/bin/tg-notify` (bot token +
chat id live in the macOS Keychain under services `claude-telegram-bot-token` /
`claude-telegram-chat-id`, account `claude` — never in files or repos). The helper formats every message as `[machine tag] project · message` — pass the project with `-p <name>` (cwd basename as fallback); both elements are REQUIRED template parts so the owner sees at a glance which box and which project pings. Messages are HTML,
one-glance short: **project · what happened · link(s)**.

**Ping exactly at these moments:**
1. **Blocked** — the loop released a task after failed attempts, or needs the owner (auth, a
   decision, an inaccessible resource): what is blocked + what he must do.
2. **Review-ready** — an issue moves to the review state: **ONE MESSAGE PER TASK** (never bundle
   several tasks into one message), each with the task key + every PR link tied to THAT task. A PR
   with no tracker issue → just the PR link. Finished work with no PR → say what finished. For a
   lane-auto PR under `LOOP_AUTOMERGE=on` ([[feedback-automerge-risk-lanes]]) the message says the
   loop will self-merge on a coming sweep unless the owner comments — never imply a review is
   being waited on.
3. **Auto-merged** (`LOOP_AUTOMERGE=on` only) — a PR merged through the auto lane
   ([[feedback-automerge-risk-lanes]]): task key + PR link + the word **auto-merged**, never a bare
   "merged". This is the owner's signal that unreviewed code landed on main; it is part of the
   mandatory audit trail, not routine progress.
4. **Idle** — queue empty or WIP-capped with nothing actionable: ONE ping when entering idle, not
   one per tick; ping again only when leaving and re-entering idle.

**Never ping** routine progress, commits, or every loop tick — protect the channel's signal. The ping is **best-effort, never a gate**: if `tg-notify` is missing (non-mac machine, fresh box), the
Keychain entries are absent, or the send fails for any reason — note it ONCE in the PR/tracker comment
and continue the loop. The durable ticket comment and status transition are the mandatory parts
([[feedback-draft-until-gated]], [[feedback-status-mirrors-work]]); the ping is a convenience on top.
