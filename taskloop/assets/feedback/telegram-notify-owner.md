---
name: feedback-telegram-notify-owner
description: Ping the owner on Telegram (~/.claude/bin/tg-notify, creds in the macOS Keychain) at attention-worthy moments — blocked, review-ready with all PR links, or gone idle
metadata:
  type: feedback
---

The loop pings the owner on Telegram via the global helper `~/.claude/bin/tg-notify` (bot token +
chat id live in the macOS Keychain under services `claude-telegram-bot-token` /
`claude-telegram-chat-id`, account `claude` — never in files or repos). Messages are HTML,
one-glance short: **project · what happened · link(s)**.

**Ping exactly at these moments:**
1. **Blocked** — the loop released a task after failed attempts, or needs the owner (auth, a
   decision, an inaccessible resource): what is blocked + what he must do.
2. **Review-ready** — an issue moves to the review state: task key + **every PR link tied to that
   task**. A PR with no tracker issue → just the PR link. Finished work with no PR → say what
   finished.
3. **Idle** — queue empty or WIP-capped with nothing actionable: ONE ping when entering idle, not
   one per tick; ping again only when leaving and re-entering idle.

**Never ping** routine progress, commits, or every loop tick — protect the channel's signal. If the
Keychain entries are missing, tg-notify exits 1: tell the owner once (in the PR/tracker comment)
instead of failing silently, and continue the loop.
