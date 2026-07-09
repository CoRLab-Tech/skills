---
name: feedback-cost-conscious-gating
description: "Scale gate rigor and model to PR risk — review/verify on the balanced model, top-model verdicts only, xhigh effort only on money/auth/concurrency, full gate only where a wrong PASS is expensive"
metadata:
  type: feedback
---

The full gate — 5 review dimensions × per-finding adversarial verify × 2 verdicts, all on the top model — costs roughly 0.6–1.2M tokens per PR, plus a second full re-gate per fix round. It is the dominant cost of an autonomous loop and the usual cause of session-limit failures. It also catches real production bugs, so the answer is not to delete it: **scale it to risk.** This rule tempers the "verdicts always on the top model" line of [[feedback-model-effort-routing]] with a cost ceiling.

**How to gate:**

- **Review + verify dimensions → the balanced model** (`sonnet` in the stock profiles) at effort `high`. Not the top model.
- **QA + security verdicts → the top model.** Effort `xhigh` ONLY for money-movement / auth-security / concurrency-core PRs; every other verdict runs the top model at `high`. `xhigh` roughly doubles a verdict's thinking tokens for marginal gain on non-critical judgments — reserve it for the risk classes where a wrong PASS costs money or a breach. A deep-but-not-money PR (a read endpoint, a hardening follow-up) gets a top-model `high` QA verdict and a balanced-model `high` security scan, not two `xhigh` verdicts.
- **Right-size the TIER, not just the gate.** A task that mirrors an already-merged sibling pattern is `standard`, NOT `deep`, even on a money-ish service — the architecture decision is already made, so it is typing against a template, not engineering. Reserve `deep` for genuine money *math*, a new service skeleton, an external adapter, a saga or concurrency core, or an auth surface. "When in doubt, route up" still holds for genuine ambiguity, but "mirrors a merged sibling" is not ambiguous.
- **Standard-tier implementation effort → `medium` by default**; `high` only on a money/security surface or after a failed attempt. High effort is a hidden multiplier and most pattern work converges at medium.
- **Scale review breadth to risk:** money / security / concurrency PRs keep 5 dimensions + 3× adversarial verify per finding; standard PRs get 3 dimensions + 1 verifier per finding. Do not run a three-refuter panel on a nit.
- **Full gate only for money / security / concurrency / idempotency / build-integration PRs.** For mechanical or purely additive PRs — renames, config-only, docs, a pure new module with no money or security surface — skip the full gate: run tests + lint + typecheck + ONE review pass on the balanced model, and finalize on green.
- **Do not full-re-gate a trivial fix.** See [[feedback-targeted-regate-on-fixes]]. If only the QA/security verdicts failed (say, on a session limit), re-run just those two agents on the unchanged diff, not the whole gate.
- **Steer in-flight agents when the owner flags live token burn.** A memory or policy change only affects agents spawned AFTER it. If the owner says spend is bleeding NOW, do not wait for the next spawn — `SendMessage` every already-running loop agent to apply the reduced gate to its REMAINING steps (the gate step is usually still ahead of them). Keep the full gate on the money/auth/concurrency ones; reduce the rest.
- **Compact the gate's output, not its reading.** Extract only `pass` / `qa.verdict` / `security.verdict` / `confirmedBlocking` from a gate result — never re-read the full transcript into the orchestrator.
- **Every finding cites its source; the verifier checks the citation first.** A review dimension must return, alongside its claim, the **verbatim line it is quoting** from the diff or file, with the path and line number. The adversarial verifier's first move is to open that exact location and compare: if the quoted text is not there, or does not say what the finding claims, the finding is **REFUTED on the spot** — no further reasoning, no benefit of the doubt. Only a finding whose citation checks out earns a real adversarial pass.

  This costs almost nothing: the verifier already reads the finding's hunk ([[feedback-targeted-regate-on-fixes]]), so the check is a string comparison it performs before spending any judgment. What it buys is the elimination of the gate's most expensive failure mode — a plausible, well-argued finding about code that does not exist, which sends a fix agent to rewrite something that was already correct. An unciteable finding is a hallucination with good grammar.

**Why:** the strong gate earns its cost exactly where a wrong PASS is expensive and nowhere else. Risk-scaling holds essentially the whole catch rate at a fraction of the spend.

**How to apply:** bake the balanced model into the review + verify `agent()` calls and the top model into the QA + security verdict calls. Classify each PR's risk before choosing full-gate vs light check. The profile's concrete model ids come from `feedback/model-routing-profile.md`; the tiers and the verdict pin come from [[feedback-model-effort-routing]]. Which regime is in force is [[feedback-loop-strategy-profiles]].
