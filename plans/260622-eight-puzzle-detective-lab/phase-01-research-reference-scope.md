---
phase: 1
title: "Research reference scope"
status: pending
priority: P1
effort: "0.5d"
dependencies: []
---

# Phase 1: Research reference scope

## Overview

Capture what the reference 8-Puzzle project already teaches so the new project can keep the same knowledge coverage without copying the exact presentation style.

## Requirements

- Functional: identify required algorithms, UI learning flows, reports, tests, and academic explanations from the reference.
- Non-functional: keep the new plan honest about what is a canonical solver versus an educational model.

## Architecture

The reference is a Python coursework app with a core algorithm module and Streamlit/Tkinter UI. The new project should preserve the educational architecture: core logic separated from presentation, trace data structured as rows, and report/export functions built from core run results.

## Reference Findings

- Main domain: 8-Puzzle with tuple state representation, solvability parity, legal blank moves, and goal validation.
- Core concepts: Node, Frontier, Reached, Expanded, Generated, `g(n)`, `h(n)`, `f(n)`, complete, optimal, priority rule, selection key.
- Main heuristics: `misplaced` and `manhattan`; both explained per tile.
- Algorithm scope: 27 algorithms/variants grouped into 6 academic families.
- Standard solvers: BFS, DFS, UCS, IDS, Greedy, A*, IDA*, hill climbing variants, local beam, simulated annealing.
- Educational demos: AND-OR, no observation, partial observation, online search, CSP modeling/propagation/backtracking/min-conflicts/constraint graph, Minimax, Alpha-Beta, Expectimax.
- UI expectations: Vietnamese/English, preset states, start/goal matrix, trace table, comparison table, heuristic tab, experiment tab, report export.
- Validation: algorithm certificate, unsolvable detection, path validity, heuristic validity, deterministic benchmark.

## Related Code Files

- Read: `D:\Trí tuệ nhân tạo AI lỏ\README.md`
- Read: `D:\Trí tuệ nhân tạo AI lỏ\GIAI_BAI_TOAN_8_PUZZLE.md`
- Read: `D:\Trí tuệ nhân tạo AI lỏ\eight_puzzle_search_app.py`
- Read: `D:\Trí tuệ nhân tạo AI lỏ\thu_duc_graph_coloring.py`
- Read: `D:\Trí tuệ nhân tạo AI lỏ\requirements.txt`

## Implementation Steps

1. Build a coverage matrix from the reference: concepts, algorithms, UI features, validation, export, and testing.
2. Mark each item as required, optional, or reference-specific.
3. Identify elements that must be rephrased or redesigned to avoid looking like a direct clone.
4. Preserve two canonical heuristics as baseline: `misplaced` and `manhattan`.
5. Preserve the 6 academic algorithm groups, but change how they are taught and navigated.
6. Record constraints: no fake solvers, no misleading claims, bounded demos clearly labeled.

## Success Criteria

- [ ] Reference scope matrix exists in implementation notes or docs.
- [ ] Required AI concepts are not lost.
- [ ] Non-standard demos are clearly separated from canonical 8-Puzzle solvers.
- [ ] New project identity is chosen before code starts.

## Risk Assessment

- Risk: copying reference layout too closely. Mitigation: use a different learning metaphor and interaction model.
- Risk: reducing academic coverage while changing the product. Mitigation: maintain coverage matrix against reference sections.
- Risk: overbuilding extra algorithms. Mitigation: keep same coursework algorithm scope first; add extras only after core passes.
