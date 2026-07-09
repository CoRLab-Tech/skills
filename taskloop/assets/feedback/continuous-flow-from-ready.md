---
name: feedback-continuous-flow-from-ready
description: "The loop runs continuous-flow, not batch/wave — the moment capacity frees, pull the next doable ready ticket and launch it; a ticket blocked only on the loop's own open PR is doable NOW by stacking"
metadata:
  type: feedback
---

Do NOT wait for a batch or wave to complete before pulling more work. Run **continuous-flow**: keep as many parallel worktree agents in flight as the WIP cap allows, and the instant one finishes or a dependency merges, immediately pull the next ready ticket whose dependencies are satisfied. Never sit idle while doable ready work exists.

**"Doable" means the ticket's dependency code EXISTS on some branch AND it is file-disjoint from every running agent** — not "its dependencies are already merged". A ready ticket whose only blocker is one of the loop's OWN in-flight PRs is doable now by **stacking**, not something to idle-wait on:

- Branch it from the blocker's **feature branch**, not `origin/main`, and open the PR with `gh pr create --base <blocker-branch>` so the diff is only the delta. Note in the body: "Stacked on #N, auto-retargets to main when #N merges." GitHub retargets on merge; a later tick rebases onto `origin/main` and re-verifies.
- **Base-merged-mid-flight:** a stacked agent's base PR can merge — and GitHub can auto-delete the head branch — while the agent is still implementing. If the agent has not opened its PR yet, `gh pr create --base <deleted-branch>` FAILS. Watch base-PR merges every tick, and the instant a running stacked agent's base merges, `SendMessage` it: rebase onto `origin/main` (the dependency code is now on main), open the PR with the default base, re-run gates in the foreground. If the agent already opened its PR, GitHub auto-retargets it on merge — no action needed.

The ONLY things that hold a ready ticket back are (a) **file overlap with a currently running agent** — parallel agents on the same files corrupt each other, so sequence those ([[feedback-parallel-disjoint-tasks]]); (b) a genuine **external blocker** ([[feedback-block-stuck-tickets-visibly]]); or (c) the **WIP cap** ([[feedback-wip-limit-open-prs]]). "Depends on my own open PR" is none of these — stack it.

**Check the queue automatically — never wait for the owner to nudge.** On every sweep, every agent completion, and every merge, recompute the doable set (ready tickets whose dependency code exists on any branch, disjoint from running agents, under the WIP cap) and launch the newly-doable ones the same tick. If the owner ever has to ask "why aren't you pulling from the ready queue?", the loop failed this rule.

**Why:** the owner wants throughput with zero babysitting. Batching and idle-waiting on the loop's own PRs both waste capacity between merges — the queue drains at the speed of the slowest item in each wave instead of the speed of the machine.

**How to apply:** this refines the "one wave, then the next" reading of the loop spec, and composes with [[feedback-queue-triage-plan]] (the plan's `depends-on` edges say what stacks on what) and [[feedback-parallel-disjoint-tasks]] (one agent per disjoint doable unit). Gates still run per PR before the review transition. Surface the real bound — WIP cap, disk per worktree, session limits — with a log line rather than silently under-pulling.
