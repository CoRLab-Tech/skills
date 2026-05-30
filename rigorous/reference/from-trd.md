# rigorous from-trd

Take an externally-authored binding specification (a "caiet de sarcini", TRD, SoW, RFP, or similar) and transform it into the team's actionable engineering canon: posture docs, per-UC shapes, meta-docs generators, and enforcement hooks. The output is a repo where every requirement in the spec has a traceable home, every rule lives in exactly one place, and stale-ness becomes structurally impossible.

This is an orchestration command. It runs an audit, asks for one architectural decision (the Constitutional Map), then drives a series of focused PRs that each go through the standard shape → craft → critique loop.

## When to invoke

- You inherited a project where a binding spec is sitting beside code that drifted from it.
- A new tender / contract drops a multi-hundred-page TRD and you need to turn it into shape-able work.
- A repo's docs grew organically and contradict each other (e.g., the same rule stated three ways across three files).
- The team uses CLAUDE.md / AGENTS.md / ARCHITECTURE.md but nobody knows which one owns a given rule.

## Skip for

- Single-page specs that fit in one shape.
- Projects where the team is happy with existing docs.
- Pure greenfield (no binding spec yet) — use `teach` + `shape` instead.

## Pre-flight (gates)

Same as the rest of rigorous: `PRINCIPLES.md` must exist (run `teach` first if it doesn't). The other context files (`STACK.md`, `TESTING.md`) help but don't block.

Additionally, `from-trd` reads a per-project config at `.rigorous/trd-config.yml`:

```yaml
trd_path: docs/<spec-filename>.md
trd_language: ro           # ro | en | ru — binding spec stays in this language verbatim
uc_header_regex: '^### (UC\d{2,3}) — (.+)$'   # how to find requirements in the spec
shape_filename_pattern: 'shape-uc-{nn}-{slug}.md'
posture_docs:
  workflow: AGENTS.md         # "how we work"
  architecture: ARCHITECTURE.md  # "how the system looks"
  stack: STACK.md
  testing: TESTING.md
  principles: PRINCIPLES.md
  design: DESIGN.md           # optional, FE-heavy projects
informational_marker: 'în scopuri informative'   # spec-specific phrase marking out-of-scope UCs
docs_generator_outputs:
  - docs/status.md
  - docs/shapes-index.md
  - docs/roadmap.md
```

If the config is absent, the command interviews the user for these fields and writes it. Re-running with the file present skips that interview.

## Process

Eight phases. Each completes a focused PR. Each PR follows the full rigorous loop (shape → craft → critique → review-ready) and posts a Telegram / equivalent ping at PR open if hooks are wired.

### Phase 0 — Bootstrap

1. Verify pre-flight gates.
2. Load or create `.rigorous/trd-config.yml`.
3. Read the binding spec; extract the requirements inventory using `uc_header_regex` (count, IDs, titles).
4. Detect any informational-only requirements via `informational_marker` (these get an `ℹ external` status downstream, no shape required).
5. Survey existing docs: list what's already in the repo, classify by candidate ownership (workflow / architecture / stack / etc.).

Output: a single-page summary the user signs off on. No file edits yet.

### Phase 1 — Audit (multi-agent)

6. Dispatch a Workflow with seven parallel agents, each on a distinct dimension. The agents read the docs in scope and return findings as structured JSON. After the fan-out, every finding is passed through an adversarial verifier (a second agent that reads the cited files and confirms the contradiction is real).

The seven dimensions:

| Dimension | What it looks for |
|---|---|
| `tech-contradictions` | Conflicting tech choices, port numbers, service counts, schema names, auth flows across STACK / ARCHITECTURE / shapes |
| `process-strictness` | Rules stated as suggestions where they should be mandatory; duplicated workflow definitions; missing strictness in commit/PR/test gates |
| `frontend-coherence` | DESIGN.md vs PRODUCT.md vs ui-shape.md contradictions; design system reuse vs local wrapper; token/font/spacing drift |
| `cross-ref-integrity` | Broken file refs, dead section pointers, UC IDs cited that don't exist in spec |
| `spec-vs-shape` | Shape declares X, spec requires Y; UCs missing from shape catalog; UC numbering renamed inconsistently |
| `structure-hygiene` | Scratch files at repo root; duplicate paragraphs across files; two parallel organization schemes; stale meta-docs |
| `ambiguity-gaps` | Terms used with multiple meanings; "see X" without a concrete link; conventions implicit but not written; missing answers for common edge cases |

The Workflow uses `model: opus` for both finder and verifier agents — anything weaker produces noise. Verifier is biased toward keeping a finding (better one false positive than missing a real contradiction).

7. Present the prioritized findings (P0 / P1 / P2) to the user. P0s are contradictions that produce wrong code or behavior; P1s are ambiguities a reader will trip on; P2s are hygiene.

Output: a written audit report committed to `docs/audit-<date>.md` (optional, controlled by user) or just consumed inline.

### Phase 2 — Constitutional Map

8. Propose a single-owner-per-concern table based on the audit + the posture_docs from the config. Each row is `concern → canonical owner doc → other docs treat by link-only`. Standard rows include:

- "How we work" → workflow doc (commit discipline, naming, shape→craft→critique cycle, LOC thresholds, slash commands).
- "How the system looks" → architecture doc (services, ports, schemas, flows).
- "Tech pinned + rationale" → stack doc (no version overrides in shapes).
- "Read-order at session start" → workflow doc §0.
- "Project state" → generated meta-docs (status / shapes-index / roadmap).
- "Terminology glossary" → workflow doc §Glossary.
- "Canonical design system" → design doc; STACK/ARCHITECTURE only refer.
- "Canonical shape catalog" → per-UC + per-ops filename pattern; phase-style shapes deprecated.

9. User ratifies, edits, or rejects. The map is committed as `docs/shape-ops-docs-consolidation.md` (the master shape) and becomes the contract for the remaining phases.

### Phase 3 — Sync architecture with live code (PR-1)

10. Read all code that backs the posture doc claims: app entrypoints, env schemas, migration filenames, auth implementation, design-system linkage. Compute the diff between architecture-doc claims and code reality. Fix the doc to match code. Resolve every P0 from the audit that lives in the architecture doc.

Each architecture mismatch becomes a one-line edit, cited in the commit message body.

### Phase 4 — Posture single-owner (PR-2)

11. Move every duplicated rule into its canonical owner per the Constitutional Map. Convert duplicate sections in CLAUDE.md / session-bootstrap.md / pr-verification-checklist.md (or equivalents) into pointers-with-link. Reduce CLAUDE.md to a thin entry-point.

12. Resolve numeric divergences (LOC thresholds, retention windows, cap values) to a single canonical value. Update any enforcing hooks to match.

### Phase 5 — Shape catalog cleanup (PR-3)

13. For each shape file:
    - If it's per-UC and matches the canonical pattern: keep.
    - If it's per-phase or per-iteration and covers UCs that overlap with per-UC shapes: absorb the overlapping content into the per-UC shape, add `> Superseded by: <canonical>` at the start of the absorbed section, and mark the phase shape `PARTIALLY SUPERSEDED` in its header.
    - If a phase shape covers UCs with no per-UC shape: leave it in place (JIT extraction, see Phase 8).

14. Move clearly-scratch files (root-level dumps, snapshots, debug output) into `docs/.archive/` with a README explaining what each is. Rename misnamed files (e.g., a tender metadata file misnamed `overview.md`).

### Phase 6 — Meta-docs generator (PR-4)

15. Generate `tools/scripts/refresh-docs-status.mjs` from the embedded template (below). The script reads:
    - Binding spec (per `trd_path` + `uc_header_regex`)
    - Shape files (filename glob)
    - GitHub PR state (`gh pr list --json ...`)
    - Caiet-informational marker (skips out-of-scope requirements)

Outputs three markdown files per `docs_generator_outputs`. Each output carries a SHA1(body) header so manual edits are detected on next run. The script supports `--check`, `--force`, and a `pnpm docs:refresh` wrapper.

16. Add the three generated files to `.prettierignore` so prettier doesn't reformat tables and invalidate the SHA1 on commit.

### Phase 7 — Translation pass (PR-6, optional, split into 3 sub-PRs)

If the team's policy is "code AND prose docs in English" but the repo has prose in another language, run a translation pass. Three sub-PRs to keep diffs reviewable:

17a. Root posture docs + ops docs (PRINCIPLES / STACK / TESTING / DESIGN / PRODUCT / PR-checklist / session-bootstrap). Update `R3` rule in the workflow doc to explicitly state "code AND prose docs in target language".

17b. All shape docs in bulk (mechanical batch). Run in parallel via 2–3 sub-agents partitioned by file count. Each agent applies the same preservation rules:

- Code samples, identifiers, file paths, fenced blocks: verbatim.
- Binding-spec citations: keep original language in italics + brief gloss in target language right after.
- UI copy strings (the literal strings that will appear in the product UI): verbatim — they're i18n source.
- Proper names of external systems: verbatim.

17c. The largest single FE shape doc (e.g., `ui-shape.md`). Light-touch only — UI mockups stay verbatim; only narrative prose translates. Optional screenshot spot-check after.

Each sub-PR uses a 1:1 translation glossary committed to the sub-shape to enforce consistency across files.

### Phase 8 — JIT extraction policy (PR-5)

18. The remaining phase-style shapes still cover requirements without dedicated per-UC shapes. Don't pre-emptively split them. Codify the rule in the workflow doc §Shape naming:

> A per-requirement shape is created the first time an engineer plans implementation work on that requirement. Until then, the existing phase shape is canonical. When extracting: copy the section into the new shape, link back with `> Superseded by: <canonical>` from the phase shape's section header.

Phase shapes move to `.archive/` only after every requirement they cover has a per-requirement shape — not before.

### Phase 9 — Enforcement hooks (PR alongside Phase 6)

19. Install two local hooks (commit them as project tooling at `tools/scripts/check-*.sh`):

- **Pre-PR gate**: blocks `gh pr create` unless (a) e2e ran in scope, (b) `/rigorous critique` was invoked, (c) no open tasks remain. Scope = since last `git checkout -b`. Exempts diffs limited to `tools/` or `docs/` paths.
- **Communication trigger**: at Stop event, if the assistant's final turn contains attention-needed phrases ("waiting for approval", "go ahead?", explicit ask) AND no notification has been sent, block the stop. Forces the user-notification discipline mechanically rather than by memory.

The team wires these into per-user `.claude/settings.local.json` (not committed) so contributors without the notification credentials aren't blocked. Document the wire-up snippet in `tools/scripts/HOOKS.md`.

## Output discipline

Each phase produces exactly one focused PR. Each PR:

1. Has a sub-shape committed under `docs/shape-ops-docs-consolidation-prN.md` listing files modified + test plan + tradeoffs + open questions.
2. Runs `/rigorous critique` on the staged diff before commit. Block-level findings fixed pre-commit; nice-to-haves listed in PR description.
3. Cites the sub-shape in the commit body per the shape-ref hook.
4. Posts a notification at PR open if the trigger hook is configured.

The series typically lands as ~8 PRs over the working session.

## Cost discipline

The Phase 1 audit costs ~500k-1M output tokens (seven Opus auditors + verifiers). Run it once per project. Don't re-run on small follow-ups — for incremental work, manually invoke `audit` on a specific dimension.

The translation pass (Phase 7) costs another ~300-500k tokens. Optional and one-time.

Tooling install (Phases 6, 9) and JIT policy (Phase 8) are cheap.

## What from-trd is not

- Not a code rewrite. It edits docs, generates tooling, and adds enforcement. It never modifies production code in `apps/` or `libs/`.
- Not interactive code generation. The per-requirement shapes it creates are *planning* documents the engineer fills in during their `craft` cycle, not finished implementation specs.
- Not a one-shot. It's a session-spanning command — typically 4–8 hours of orchestration, with explicit user check-ins at Phase 0 (inventory), Phase 1 (audit findings), Phase 2 (Constitutional Map), and at each PR review.
- Not a substitute for the engineer's own thinking. The Constitutional Map is *proposed* by the command but *ratified* by the user. The per-UC shapes have open questions the engineer answers during craft.

## Embedded templates

The skill ships four parameterized templates under `templates/`:

- `master-shape.md.tmpl` — the Constitutional Map header used in Phase 2.
- `sub-shape.md.tmpl` — the per-PR sub-shape used in every phase.
- `per-uc-shape.md.tmpl` — the per-requirement planning shape used in Phase 8 / JIT.
- `refresh-docs-status.mjs.tmpl` — the meta-docs generator used in Phase 6.

Each template uses `{{var}}` placeholders bound to fields in `.rigorous/trd-config.yml`. The command writes them out concretized after the user confirms config in Phase 0.

## When to escalate

- If the audit returns >20 P0 findings: stop and surface to the user. The repo may need a bigger restructure than `from-trd` is designed for.
- If the Constitutional Map needs more than the eight standard rows: the project is unusual; the command falls back to interactive per-row decision rather than pre-set defaults.
- If the binding spec is in a language with no Romanian / English mapping in the translation glossary: ask the user to provide a 1:1 glossary of the 20–30 most common terms before running Phase 7.
