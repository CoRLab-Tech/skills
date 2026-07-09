---
name: feedback-queue-triage-plan
description: "Whenever the ready queue's content changes, the loop autonomously triages it — inferring order and parallel groups — and marks every ready ticket with the LOOP-PLAN vocabulary; no questions asked"
metadata:
  type: feedback
---

New todos don't just enter a line — they get **triaged**. Whenever the ready queue's content changes (new issue, removed issue, edited title/description, new human comment) and at every `start`, the loop analyzes ALL ready issues together, infers which depend on which and which can run in parallel, and **marks the verdict on each ticket** using the internal vocabulary below. Fully autonomous: the loop decides alone, records its reasoning, and never asks the owner — unless a ticket already states its own ordering, which always wins.

**The vocabulary — one `LOOP-PLAN` comment per ready ticket** (HTML for Plane, markdown elsewhere):

```
🧭 LOOP-PLAN v1
order: 2                 ← topological position; lower numbers run first
group: P1                ← same group id = safe to run concurrently (file-disjoint)
depends-on: MCP-4        ← issue keys this task must wait for ("—" if none)
parallel-with: MCP-9     ← file-disjoint siblings in the same group ("—" if none)
tier: standard           ← light | standard | deep | frontier — drives model/effort routing ([[feedback-model-effort-routing]])
strategy: fast           ← optional: auto|fast|balanced|heavy — this ticket's gate rung ([[feedback-loop-strategy-profiles]])
reason: touches only apps/api/pricing; MCP-4 migrates the schema this reads
```

**Why:** an unordered queue forces every tick to re-derive the same dependency reasoning from scratch — inconsistently. A marked plan makes the order visible to the human on the tickets themselves, feeds [[feedback-parallel-disjoint-tasks]] deterministic groups instead of ad-hoc partitioning, and survives session restarts.

**Only the explicit ready status is a work queue.** The loop triages and pulls issues whose status is the configured ready status (Linear `Todo`; Plane `$PLANE_READY_STATUS`; Jira `$JIRA_READY_STATUS`). It never picks up `Backlog`, even though those are technically unstarted: backlog means "I have not decided whether this is real work", while the ready status means "yes, start this". Every provider query — the `start` verify, the monitor poll, the tick — filters strictly on the configured status name, never on a broader bucket like Linear's `unstarted` type or Plane's `unstarted` group, both of which swallow Backlog. Two exceptions: an issue the owner references directly by id or URL (the reference IS the triage signal), and an explicit owner override for that turn.

**How to apply:**
- **Analysis inputs, in priority order:** (1) explicit human markers — "depends on/after/blocked by" in the text, native tracker relations, priority fields — these are law, never overridden; (2) native relations where the tracker has them (Plane MCP: `list_work_item_relations`); (3) inferred structure — layering (schema → API → UI), one task's output named in another's description, shared files/modules (infer from descriptions + repo layout, same method as [[feedback-parallel-disjoint-tasks]]).
- Tickets whose text already pins order or parallelism are taken verbatim — the plan comment just mirrors what the human wrote, flagged `reason: stated on ticket`.
- Ambiguity is resolved conservatively and autonomously: unclear overlap → same group is forbidden (sequential, per [[feedback-parallel-disjoint-tasks]] "when in doubt, treat as overlapping"); unclear order → priority then `updatedAt`. Note the uncertainty in `reason`. Ambiguity here is never a reason to ask the owner or to punt the ticket.
- **Marking:** post the `LOOP-PLAN` comment via the provider's post-comment verb. Where the tracker supports it cheaply, also mirror `depends-on` as a native blocked-by relation (Plane MCP: `create_work_item_relation`). On re-triage, **update the loop's own previous plan comment** (Plane MCP: `update_work_item_comment`) — never stack duplicates — and only touch tickets whose plan actually changed.
- **Anti-self-trigger guards (mandatory):** persist the plan plus a queue signature in `$MEM/.queue-plan`. The signature covers issue ids + titles + description hashes + human comment count — NEVER the loop's own `LOOP-PLAN` comments or their timestamps. Re-triage only when that signature changes, at most once per tick. Two exceptions bypass the signature guard: a ready ticket whose plan comment is missing any current-vocabulary field (e.g. a pre-tier `LOOP-PLAN` without `tier:`) is stale and gets re-triaged before it can be pulled; and `start` always runs the triage check regardless of the signature. Without this, the plan comment bumps `updated_at`, the monitor fires, the loop re-plans, forever.
- **Consumption:** the pull step takes tasks in `order`; a whole `group` may launch together as parallel worktree agents up to the WIP headroom ([[feedback-parallel-disjoint-tasks]], [[feedback-wip-limit-open-prs]]). A task whose `depends-on` is unmerged is not pulled *onto `main`* — but it is still pullable **stacked on the blocker's branch** once that branch carries the dependency code ([[feedback-continuous-flow-from-ready]]). In-review doesn't count as done for a `main`-based branch; it does count as available for a stacked one.
- **`order` is a pull sequence, not a merge barrier.** Between tasks with no `depends-on` edge, the loop NEVER waits: the moment order-1's PR is open, order-2 gets pulled on the next pass. Only three things keep a ready task un-pulled — file overlap with a running agent, a genuine external blocker ([[feedback-block-stuck-tickets-visibly]]), or zero WIP headroom. A queue full of independent tasks drains continuously while their PRs sit in review; waiting for "everything to merge" before pulling the next ready ticket is a bug, not caution.
- **In-flight work is frozen:** the analysis inputs include the loop's own In Progress tickets and the paths they touch. A ready ticket overlapping an in-flight task gets `depends-on: <in-flight key>` (not pullable until that PR merges). Re-triage NEVER reorders, regroups, or reassigns tasks already being implemented — the plan governs what is pulled next, not what is running. And re-triage never lowers a `tier:` below the highest rung already attempted on that issue — the escalation ladder ([[feedback-model-effort-routing]]) writes its up-tier into the plan, and a recompute must not undo it. The same ratchet protects `strategy:`: under `auto` that field carries the ticket's current assessed complexity, which QA may already have revised upward ([[feedback-loop-strategy-profiles]]), so a recompute may raise it but never lower it.
- When a dependency merges or a human edits a ticket, the next triage naturally reshuffles `order` — that is expected and needs no announcement.
