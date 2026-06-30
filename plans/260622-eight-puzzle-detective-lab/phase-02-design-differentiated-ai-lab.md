---
phase: 2
title: "Design differentiated AI lab"
status: pending
priority: P1
effort: "1d"
dependencies: [1]
---

# Phase 2: Design differentiated AI lab

## Overview

Design the new 8-Puzzle project as **8-Puzzle Detective Lab**: learners solve investigation missions where each algorithm leaves evidence in the trace, and users must explain or predict the next decision.

## Requirements

- Functional: provide a distinctive web-based 8-Puzzle app with detective missions, algorithm diagnosis, trace replay, prediction prompts, benchmark, and full report export.
- Non-functional: keep AI logic testable without UI, keep the web UI polished, bilingual-ready, and suitable for coursework demo.

## Architecture

Recommended structure for later implementation:

```text
project-root/
├── api/
│   ├── eight_puzzle_detective_core.py
│   ├── main.py
│   └── tests/
├── web/
│   ├── src/
│   └── tests/
├── docs/
└── assets/
```

Python core/API owns state, algorithms, trace rows, certificates, benchmark, and report data. Web frontend owns boards, missions, prediction prompts, replay, comparison, and export controls. This keeps the 8-Puzzle knowledge from the reference while making the product visually and structurally distinct.

## Distinctive Product Features

1. **Detective Case Mode**
   - Preset cases: `case-easy-two-moves`, `case-greedy-trap`, `case-ida-threshold`, `case-unsolvable-parity`, `case-local-minimum`.
   - Each case asks: “Which node will the algorithm inspect next?” before revealing the trace.

2. **Next Node Prediction**
   - Before expanding a step, show current frontier with `g`, `h`, `f`.
   - User selects the next node; app explains correct/incorrect answer by priority rule.

3. **Algorithm Autopsy**
   - After a run, summarize where the algorithm succeeded, wasted expansions, got trapped, pruned, or violated optimality expectations.
   - For Greedy/local search, highlight why low `h(n)` can still be misleading.

4. **Heuristic Evidence Board**
   - Visual tile-level evidence for `misplaced` and `manhattan`.
   - Show how heuristic contributions changed between current node and chosen child.

5. **Trace Story Replay**
   - Timeline view: selected node, rejected nodes, frontier before/after, reached update, and reason phrase.
   - Keep columns compatible with reference knowledge: Node, Frontier, Reached, Priority Rule, Selection Key.

6. **Misconception Quiz**
   - Short checks: BFS vs UCS when cost=1, why A* needs admissible heuristic, why DFS is not optimal, why unsolvable parity stops early.

## Algorithm Coverage

| Group | Keep | Detective treatment |
|---|---|---|
| Uninformed Search | BFS, DFS, UCS, IDS | Compare expansion order and memory trade-off |
| Informed Search | Greedy, A*, IDA* | Predict by `h` or `f`, inspect heuristic evidence |
| Local Search | Hill climbing variants, beam, simulated annealing | Diagnose local minima, plateau, randomness, restarts |
| Complex Environments | AND-OR, no observation, partial observation, online | Label as educational alternate-world cases |
| CSP | definition, propagation, consistency, backtracking, min-conflicts, graph | Use time-indexed planning and optional room/color analogy as side lab |
| Adversarial/Stochastic | Minimax, Alpha-Beta, Expectimax | Use bounded game/chance variants, not standard solver claims |

## Related Code Files

- Create later: `api/eight_puzzle_detective_core.py`
- Create later: `api/main.py`
- Create later: `api/tests/test_detective_core.py`
- Create later: `web/src/` frontend files
- Create later: `docs/demo-script.md`
- Create later: `docs/project-report-template.md`

## Implementation Steps

1. Define case presets and expected lesson per case.
2. Define shared trace schema with extra detective fields: `frontier_before`, `frontier_after`, `correct_prediction`, `explanation`.
3. Design core functions for state validation, legal actions, solvability, heuristics, algorithms, certificate, benchmark, and report data.
4. Design web screens: Case Board, Prediction Lab, Trace Replay, Heuristic Evidence, Algorithm Autopsy, Benchmark, Report.
5. Keep bilingual labels as frontend dictionaries, but implement Vietnamese first if schedule is short.
6. Define full export pack: Markdown, CSV benchmark, HTML, DOCX, and PDF.

## Success Criteria

- [ ] New app can be described in one sentence without sounding like the reference: “an 8-Puzzle search detective trainer.”
- [ ] Every reference knowledge group maps to a feature in the new design.
- [ ] UI flow encourages active learning, not just passive trace viewing.
- [ ] Educational demos are clearly labeled as models, not canonical solvers.

## Risk Assessment

- Risk: prediction UX becomes too complex. Mitigation: start with fixed preset cases and one-step prediction.
- Risk: too many tabs. Mitigation: group tabs by learning task, not by implementation module.
- Risk: report export duplicates UI text. Mitigation: generate report from structured run/case data.
