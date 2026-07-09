---
name: feedback-efficiency-levers
description: "The remaining SAFE token and wall-clock levers after the big cuts are banked — cache-hit discipline, .claudeignore, pipeline-not-barrier gates — plus the hard quality floor that must never be cut to save tokens"
metadata:
  type: feedback
---

Once [[feedback-cost-conscious-gating]], [[feedback-token-hygiene]], and [[feedback-targeted-regate-on-fixes]] are in force, the big cuts are done — they take a PR from ~0.6–1.5M tokens to a fraction, and a measured A/B on one fix re-gate showed **−49.4% with an identical PASS verdict**. Roughly 10–20% more, plus wall-clock, is available from the levers below. Anything past them starts eroding the bug-catch rate, so stop at the quality floor.

**1. Prompt-cache discipline — measured, not assumed. The biggest remaining lever.** Cached input tokens bill at roughly 10%. Keep `agent-brief.md` and the spawn-prompt boilerplate BYTE-STABLE, with task-specific bits at the END and the boilerplate identical character for character. Any casual rewrite or reorder silently busts the cache for every agent spawned after it. Do not edit the brief or reshuffle the boilerplate without a reason. Worth instrumenting the real cache-hit rate on a spawn wave so this stops being a guess.

**2. `.claudeignore` at the repo root.** Agents burn tokens reading `node_modules`, `dist`/`build`, generated protos, coverage, and large fixtures. Cheap, zero quality risk. Per [[feedback-token-hygiene]] this is a proper loop ticket, never an ad-hoc repo edit.

**3. `pipeline()` not a barrier in gate scripts — wall-clock, not tokens.** A gate that `parallel()`s all reviews and then `parallel()`s all verifies idles the fast dimensions waiting on the slowest one. Author gates so each finding verifies the instant its dimension finishes. Speed also comes from the warm ops-helper cutting spawn latency and from keeping disjoint agents saturated — not from cutting tokens.

**4. First-gate diff-sharing — TESTED, DO NOT ADOPT.** The idea: at a PR's first gate every finder dimension re-reads the full diff independently, so give them a shared pre-chunked per-file index instead. A/B with 10 balanced-model finders (5 dimensions × 2 arms) on a 7-file fixture with 5 seeded bugs (2 genuinely cross-file): **catch rate held 5/5 in BOTH arms, including both cross-file bugs**, but the shared-index arm cost **4.9× the read round-trips (44 vs 9) and ~3% MORE tokens**. Thorough finders defensively re-pull nearly every file, and that same thoroughness — the thing that preserves the catch rate — erases the saving. Keep any such prototype flag-gated and off by default. Revisit only if a large-diff (100KB+, many-file) A/B shows a real win.

**HARD QUALITY FLOOR — never cut to save tokens.** These are what catch the CI-invisible bugs:

- 5-dimension review + adversarial verify on a PR's FIRST gate.
- Top-model QA + security verdicts on the FULL diff — the cross-cutting safety net, which is exactly why [[feedback-targeted-regate-on-fixes]] keeps them full-diff even when the review is scoped.
- The full gate on money / auth / concurrency / idempotency PRs, with `xhigh` verdicts there.

**How to apply:** levers 1 and 3 are behavioral — bake them into how briefs, spawn prompts, and gate scripts are authored. Lever 2 is engineering work, so it becomes a backlog ticket. Lever 4 is a recorded negative result: do not re-derive it.
