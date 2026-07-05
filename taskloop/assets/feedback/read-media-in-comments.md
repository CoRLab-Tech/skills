---
name: feedback-read-media-in-comments
description: "Always actually read the media in comments — images opened with the Read tool, videos frame-extracted via ffmpeg — never skip or guess"
metadata:
  type: feedback
---

Comments — on PRs and on tracker issues — routinely carry the real feedback in **attachments**: a screenshot of the broken layout, a screen recording of the misbehavior. The loop must actually LOOK at them, every time: download each attached image and read it; download each attached video and extract frames with `ffmpeg`, then read the frames. Text-only comment processing is not comment processing.

**Why:** "See screenshot" with an unviewed screenshot means the loop acts on half the feedback — and visual bug reports are precisely the ones words describe worst. A reviewer who attached a recording expects the recording to be watched.

**How to apply:**
- When sweeping comments ([[feedback-watch-pr-comments]]) or reading a tracker issue's context, collect every attachment URL (GitHub comment asset URLs, tracker attachment endpoints — for Plane the signed asset URL from the attachments API).
- **Images** (`png/jpg/gif/webp`): download to the scratchpad (`curl -sSL -o`; GitHub private assets need `gh api` / an authenticated fetch) and open with the Read tool. GIFs: extract frames like videos if multi-frame.
- **Videos** (`mp4/mov/webm`): download, then extract frames — `ffmpeg -i <video> -vf "fps=1" <scratch>/frame_%03d.png` (1 fps default; use `fps=2` for short clips, `select='gt(scene,0.3)'` for scene-change keyframes on long ones) — and Read the frames in order to reconstruct what the reporter showed.
- Check `ffmpeg` availability once (`ffmpeg -version`); if missing, install it (`brew install ffmpeg` / `apt-get install -y ffmpeg`). "Impossible to install" is a high bar: both install paths attempted with the exact error recorded. When media genuinely cannot be viewed, do NOT act on that comment's report — reply asking the reporter to describe in text what the recording shows (or attach stills), and only proceed once the requirement is understood. Never silently ignore media, and never guess at a video's content.
- What the media shows becomes part of the requirement: reference it concretely in the fix and in the PR/issue reply ("the flicker visible at ~0:04 in the recording is the re-mount; fixed by ...").
