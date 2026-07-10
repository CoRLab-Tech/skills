# Sync workflow

**Hot integrity-repair + skill-version adoption for a running project.** Sync reads the skill's current
assets (the source of truth), compares them against this project's rendered memory dir, and re-creates
whatever **degraded, corrupted, or went missing during the run** — or was **added to the skill since this
project's last init/sync** — **without stopping the loop, its Monitors, or its in-flight agents**. After
repairing, it hot-reloads the running agents so the fix applies to their remaining steps, not just the
next spawn.

This is the difference from `init`: `init` bootstraps or clean-renders and assumes a quiet board; `sync`
runs mid-flight, preserves all live state, and never pauses the loop.

## Invariants — violating any of these is a bug, not a trade-off

1. **Never `TaskStop` a healthy Monitor and never skip re-arming the heartbeat** ([[feedback-never-self-halt-loop]]). Sync repairs by writing files; the loop keeps running.
2. **Never regenerate live state.** `.env`, `.monitor-state`, `.pr-monitor-state`, `.queue-plan`, `.pr-feedback-state`, and `telemetry/*` carry running state. Sync touches one only to repair a **provably corrupt** one, and only by the class-appropriate repair below (rebuild / delete-to-rebuild), never by template re-render.
3. **Never delete a project-local file that has no skill counterpart** — custom `feedback/<slug>.md` rules, evidence, notes. Sync ADDS and REPAIRS; it removes nothing it did not author.
4. **Write a file only if its content actually changed.** A no-op write to `agent-brief.md` busts the prompt cache for every future spawn ([[feedback-token-hygiene]]). Diff first, write on drift only.
5. **Idempotent.** A second sync with no drift writes nothing and steers no agent.

## Args

- `/taskloop sync` — detect and repair, then hot-reload agents.
- `/taskloop sync --check` (alias `--dry-run`) — print the drift report and stop. Changes nothing, steers no one.

## Step 0 — Resolve dirs; confirm the loop is alive

```bash
SLUG=$(pwd | sed 's|[^A-Za-z0-9]|-|g')   # the harness maps EVERY non-alphanumeric to '-', not just '/'
MEM="$HOME/.claude/projects/${SLUG}/memory"
```

If `$MEM` does not exist → print `taskloop is not initialized for this project — run /taskloop init` and stop. Sync repairs an existing install; it does not bootstrap one.

Find the running Monitor task (command starts with `$MEM/monitor.sh`) and the PR watcher (`$MEM/monitor-prs.sh`) in the harness task list — **record their task ids, do NOT stop them.** Note which `[LOOP-AGENT]` implementation agents are currently RUNNING, from the **harness task list alone** — the spawn ledger (`telemetry/spawns-*.jsonl`) is append-only with no completion records, so it can only cross-check issue/tier labels, never decide liveness (a `SendMessage` to a finished agent *resumes* it — a spend, not a steer). Running agents are the hot-reload targets in Step 5.

**If NO Monitor is running and no loop session owns this project right now, the loop is STOPPED — deliberately** (`/taskloop stop`). Sync still repairs files (Steps 1–4's file work), but **skips** the monitor re-arm in Step 4.8, the agent hot-reload in Step 5, and the heartbeat in Step 6, and ends with: `loop is stopped — files repaired; run /taskloop start to resume.` Sync never restarts a loop the owner halted.

## Step 1 — Recover the render variables

Rendered files (`agent-brief.md`, `autonomous-loop.md`, the hooks, the monitors, …) were produced by substituting placeholders at init. To re-render deterministically, sync needs those exact values:

- **Preferred: `$MEM/.render-manifest.json`** — the substitution map init/sync writes. If present, use it.
- **Fallback (project predates the manifest):** reconstruct from durable config — `.env` (provider vars, `GH_AUTHOR`, `REPOS`, `LOOP_STRATEGY`, `LOOP_AUTOMERGE`, status names) and `feedback/model-routing-profile.md` (`LADDER`/top/deep/balanced) — and parse the rest (`PROJECT_NAME`, `REPO`, `BRANCH_PREFIX`, `TEST_CMD`, `ISSUE_PREFIX`/`ISSUE_REF`/`ISSUE_LINK_KEYWORD`, `EVIDENCE_DIR`, `START_HOUR`/`END_HOUR`) out of any rendered file that contains the value; when two files disagree, or a value cannot be recovered with confidence, `AskUserQuestion` — never guess a placeholder into a rendered file.
- **Write the manifest at the end of Step 4 when it was absent or its contents changed — never under `--check`** (`$MEM/.render-manifest.json`, `chmod 600` — it may echo `.env`-derived values), so the next real sync is deterministic even if this one had to reconstruct. A no-drift sync on a project that already has a current manifest writes nothing (invariant 5).

## Step 2 — Build the expected-file set from the skill

Enumerate what the **current skill** says a memory dir must contain — this is the contract:

- **Verbatim class:** every `assets/feedback/*.md` → `$MEM/feedback/<same>.md`, copied byte-for-byte.
- **Rendered class:** each template → its target + placeholder list — read init.md Step 5 for the render map and placeholder semantics (`agent-brief.md.tmpl`, `autonomous-loop.md.tmpl`, `restart-instructions.md.tmpl`, `monitor-<provider>.sh.tmpl`, `monitor-github-prs.sh.tmpl`, `hook-agent-routing.mjs.tmpl`, `hook-loop-guards.mjs.tmpl`, `usage-rollup.mjs.tmpl`, `targeted-regate.mjs.tmpl`, `review-recall.sh.tmpl`). A `reconcile-merged-<provider>.sh` is expected **only for the providers that ship one** (Plane, GitHub — Linear/Jira run the reconcile inline, so its absence is correct, not MISSING). The provider's `find-existing-ticket` script is expected too, but it is coupled to guard 4 (below).
- **Generated class — the installed file legitimately diverges from any template, so shape-check only, never byte-compare:** `MEMORY.md` (its `.tmpl` is only a seed; init and `add-rule` append project-local links the template cannot contain — a template re-render would DELETE them); `model-usage-log.md` (its `.tmpl` seeds a policy header, but the file exists to ACCUMULATE the owner's measured gate costs and A/B records — a re-render would erase them); `feedback/model-routing-profile.md` (produced inline by init's routing step — the ladder + four rungs); `find-existing-ticket.py` (rendered from the `.example` for Plane, hand-ported for other providers). These are NOT "extra files."
- **Expected env vars (additive):** the provider-neutral vars the current skill documents (init.md Step 5 — `LOOP_STRATEGY`, `LOOP_AUTOMERGE`, `GH_AUTHOR`, `REPOS`). A documented var absent from the running `.env` is verdict **MISSING-VAR** (repaired additively in Step 4.6; values the owner set are never judged).
- **Config outside `$MEM`:** the two `PreToolUse` hook entries in the project's `.claude/settings.local.json` (and its gitignore); the `review-recall.sh` crontab line, when installed.
- **Provider scope:** detect the provider from `.env` using the four-way check in `start.md` Step 2 (`LINEAR_API_KEY` / `PLANE_API_KEY` / `JIRA_API_TOKEN` / `GITHUB_REPO` — status.md's three-way version misses GitHub Issues) and expect only that provider's monitor/reconcile/find-existing script — never all of them.

## Step 3 — Classify each expected file (the drift report)

For each expected file assign one of **MISSING / CORRUPT / DRIFTED / OK**:

- **Verbatim feedback:** byte-compare `$MEM/feedback/x.md` against `assets/feedback/x.md`. Differ → DRIFTED; absent → MISSING; present but no closing frontmatter / truncated → CORRUPT.
- **Rendered files:** render the template with the Step-1 vars into a temp buffer and compare against the installed file **after normalizing a trailing newline** (a lone trailing-newline difference is not drift). Differ → DRIFTED (skill-template change OR runtime corruption — the repair is the same). Absent → MISSING. For the escape-heavy guard regexes in `hook-loop-guards.mjs`, a byte mismatch is a *suspicion*, not a verdict: the guard's real health signal is a passing pipe-test (Step 4.5), so re-derive those regexes from the provider reference rather than hand-diffing escapes.
- **Generated-class files:** shape-check, never byte-compare. `MEMORY.md` → parses as the index and links every present feedback file. `model-usage-log.md` → frontmatter + policy section present (never judge the accumulated measurements). `model-routing-profile.md` → declares `LADDER` + `top`/`deep`/`balanced`/`light`, and **every named rung is on the ladder** (reuse init's assertion); missing/truncated/failing-that-assert → CORRUPT. `find-existing-ticket.py` → present, non-empty, and (Step 4) executable.
- **Live state:** parse-check only. `.pr-feedback-state` must `JSON.parse` to `{"prs":[…]}`; the known bad shape is the whole object wrapped in a list `[{"prs":…}]` ([[feedback-pr-registry-race]]) → CORRUPT. `.queue-plan` / `.monitor-state` / `.pr-monitor-state` that won't parse → CORRUPT (all three are caches: the repair is delete-to-rebuild, Step 4.1). **Never diff these against a template** — drift is expected and correct.
- **Hooks install:** read `.claude/settings.local.json`; assert both `PreToolUse` matchers are present AND their `command` paths exist and are non-empty. A missing entry or a dangling path → CORRUPT (the guard is silently not firing, the worst failure — [[feedback-model-effort-routing]]). Also confirm `settings.local.json` is gitignored (init requires it) and that the `review-recall.sh` crontab line is still installed when review-recall was set up.
- **Extra files:** anything in `$MEM` with no skill counterpart AND not a generated-class file above → report as **PRESERVED (project-local)**. Never a repair target. (The routing profile and `find-existing-ticket` are generated-class, NOT extra — they must be shape-checked, not silently preserved.)

Print the report grouped by verdict. **Under `--check`, stop here** — this is the whole dry-run.

## Step 4 — Repair, hot, in dependency order

Repair only non-OK items. Order matters because some files reference others.

1. **Corrupt live state first (unblocks the watcher):**
   - `.pr-feedback-state` CORRUPT → **rebuild** via the [[feedback-pr-registry-race]] recipe (`gh pr list` per repo, re-key by branch), carrying `blocked` / `lane` / `gatedHead` / `ownActivity` forward from any salvageable entries. Never re-render, never hand-author.
   - `.queue-plan` / `.monitor-state` / `.pr-monitor-state` CORRUPT → delete; the next tick (or the watcher's next poll) rebuilds them. They are caches, not records.
   - `.env` is **never** rewritten here (Step 4.6 handles additive-only var backfill).
2. **Verbatim feedback** MISSING/DRIFTED/CORRUPT → copy from `assets/feedback/`. Leave project-local rules untouched.
3. **Coupled sets render together — including couplings that did not exist at this project's last sync.** A feedback rule that names a mechanism must never be adopted (or broadcast in Step 5) without that mechanism present in the SAME pass. The known couplings: routing rules ↔ `hook-agent-routing.mjs` + `model-routing-profile.md`; the guard rules ↔ `hook-loop-guards.mjs` + `find-existing-ticket`; the automerge lane ↔ the registry-schema-bearing files + `monitor-prs.sh` ([[feedback-automerge-risk-lanes]], and the init idempotency notes). But do not rely on this list alone: for **any** feedback file being adopted or repaired, scan its text for a named mechanism file (a `.mjs` hook, a monitor/reconcile script, a registry field, the profile) and add that file to this pass's render set. **If a named mechanism cannot be rendered this pass, do NOT copy the rule and do NOT broadcast it** — a half-adopted rule on a live loop is worse than a missing one; report it and stop that item.
4. **Rendered files** MISSING/DRIFTED → re-render with the Step-1 vars; **write only on real diff.** `chmod +x` every re-rendered shell/py script (`monitor.sh`, `monitor-prs.sh`, `reconcile-merged.sh`, `review-recall.sh`, `find-existing-ticket.py`) exactly as init does — a re-rendered monitor without its exec bit is a dead Monitor, a re-rendered guard-4 script without it is a fail-closed stall. Do `agent-brief.md` LAST and only-on-diff (cache-critical).
5. **Hooks + generated config** → re-render any missing/corrupt hook script; regenerate a CORRUPT `model-routing-profile.md` from the manifest (re-run init's ladder assertion after) and re-render `hook-agent-routing.mjs` from it in the same pass. Repair `find-existing-ticket.py` when MISSING/CORRUPT — **guard 4 is fail-closed, so its absence silently blocks all ticket filing**: for Plane render the `.example` with the manifest's project ids and `chmod +x`; for a hand-ported provider, re-port from the Plane example using the manifest ids (or `AskUserQuestion` if the port is non-trivial) rather than leaving guard 4 dark. Repair the `.claude/settings.local.json` install by **merge, never clobber** (preserve unrelated hooks), restore its gitignore entry, and reinstall a missing `review-recall.sh` crontab line; then **pipe-test every guard** (payloads in init.md's "Install both hooks" section) — a hook installed but silently wrong is worse than none, and the pipe-test, not a byte match, is the guard's health verdict. **Mid-flight, guard 4's payloads need hot-safe variants**: never run the project's real `find-existing-ticket.py` just to test the ALLOW path — that stamps the dedupe ledger and disarms the fail-closed guard for 15 minutes for every live agent. Instead point the DENY test at a temp `MEM` with an empty/backdated stamp file; if a fresh real stamp exists (a live agent legitimately searched), skip the DENY assertion rather than misread it as a failure. **A guard that fails its pipe-test is CORRUPT**: report it, do not proceed to the Step 5 broadcast for any rule coupled to it.
6. **`.env` backfill (additive only):** if the skill introduced a provider-neutral var with a safe default the running `.env` lacks (e.g. `LOOP_AUTOMERGE=off`), append the default. **Never flip a value the owner already set.**
7. **`MEMORY.md`** → rebuild the index into a buffer so every present feedback file — skill AND project-local — is linked and grouped, and **write only on real diff** (invariant 4): it is the one guaranteed-loaded file, so a needless rewrite busts the orchestrator's prompt cache every sync.
8. **Monitors:** if `monitor.sh` / `monitor-prs.sh` was MISSING/DRIFTED, re-render it (with `chmod +x`, per 4). Then check the Monitor **tasks**: a healthy running Monitor is left alone; only a **proven-dead** one is re-armed, and re-arm means tear-down-then-start-exactly-one (the single-instance invariant of [[feedback-never-self-halt-loop]]). Sync never adds a second Monitor beside a live one.

## Step 5 — Hot-reload the in-flight agents

A memory change only reaches agents spawned AFTER it — so steer the ones already running, exactly the live-steer mechanic of [[feedback-loop-strategy-profiles]] and [[feedback-cost-conscious-gating]]:

- For each running `[LOOP-AGENT]` (from Step 0), `SendMessage`: *"Loop memory was repaired/updated by sync. Before your next gate, re-read `MEMORY.md` and `agent-brief.md`; apply any changed rule to your REMAINING steps only — do not redo work already gated."* When the change is a specific behavior an agent must adopt now (a strategy switch, a new gate shape, a merge-lane rule), **name it** rather than sending a generic re-read.
- A `SendMessage` that reports "queued for delivery at next tool round" confirms the agent is live; one that "resumed" a stopped agent means it had already finished — reconcile it as a possible dead run per [[feedback-never-self-halt-loop]] instead.
- **The orchestrator (this session) re-reads the changed files immediately** before its own next action.
- Agents that are between spawns need nothing — they read the repaired files at their next startup by construction.

## Step 6 — Re-arm the heartbeat and confirm

The heartbeat gets the **same single-instance discipline as the Monitor** (Step 4.8), with one hard constraint: **pending wakeups are only knowable — and only armable — from the session that owns them.** The harness exposes no way to enumerate or cancel another session's wakeups (stop.md documents the same gap), and a `ScheduleWakeup` armed from a helper session wakes THAT session with the `/loop` prompt — a second loop instance, the exact duplication [[feedback-never-self-halt-loop]] forbids. So:

- **Sync running in the loop-owning session** (it knows its own pending wakeup): if the heartbeat is pending and on-cadence, leave it; arm a fresh one only if its own wake was already consumed this turn. Exactly one armed — never zero, never two.
- **Sync running in any other session**: arm NOTHING. Report `heartbeat state unknown — owned by the loop session; verify from there`. The loop's own sweep-every-tick guarantee ([[feedback-never-self-halt-loop]]) means a repaired file set is picked up on its next tick regardless.

Then print:

```
✅ taskloop sync — <project name>
   Repaired:  <n> (missing <a>, corrupt <b>, drifted <c>)   |  Adopted from skill: <list of new rules/templates>
   Preserved: <n project-local files untouched>
   Registry:  <rebuilt | intact>          Hooks: <reinstalled + pipe-tested | intact>
   Agents:    <k in-flight steered | none running>
   Loop:      never paused. Monitor <id> and PR watcher <id> stayed up.
```

## Notes

- **What sync is FOR vs the loop's own self-heal.** The loop already repairs the two most common runtime degradations continuously — a dead Monitor ([[feedback-never-self-halt-loop]]) and a corrupt registry ([[feedback-pr-registry-race]]). `sync` is the manual, full-surface integrity pass: it also catches a deleted or truncated rule file, a hook that fell out of `settings.local.json`, a drifted template, and — its other job — **adopts rules/templates the skill gained since this project's last init/sync** without a stop/re-init cycle.
- **Safe to run any time, repeatedly.** Under `--check` it is read-only; without it, it is idempotent and touches nothing that is already correct.
- **Provider-scoped.** Only the active provider's scripts are expected or repaired; a mismatched provider file is reported, not deleted.
