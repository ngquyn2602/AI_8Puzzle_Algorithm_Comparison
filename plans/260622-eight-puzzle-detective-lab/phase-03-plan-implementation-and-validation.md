---
phase: 3
title: "Plan implementation and validation"
status: pending
priority: P2
effort: "1.5d"
dependencies: [2]
---

# Phase 3: Plan implementation and validation

## Overview

Prepare the later implementation sequence and validation gates for the 8-Puzzle Detective Lab. This phase does not implement code; it defines safe execution order and acceptance checks.

## Requirements

- Functional: produce an implementation-ready breakdown for core logic, UI, tests, docs, and report export.
- Non-functional: avoid fake data, keep code modular, keep files reasonably small, and verify algorithms with deterministic tests.

## Architecture

Implement in layers:

1. **Core state layer**: parse/validate state, inversion parity, moves, path reconstruction.
2. **Heuristic layer**: `misplaced`, `manhattan`, per-tile contribution explanation.
3. **Search layer**: canonical solvers and educational demos returning a common result object.
4. **Detective layer**: cases, predictions, autopsy summaries, misconception quiz content.
5. **API layer**: HTTP endpoints expose cases, algorithm runs, prediction checks, benchmark, and export generation.
6. **Web presentation layer**: polished frontend screens, animations, responsive layout, and bilingual labels.
7. **Export layer**: Markdown, CSV, HTML, DOCX, and PDF submission pack.

## Related Code Files

- Create later: `api/eight_puzzle_detective_core.py`
- Create later: `api/main.py`
- Create later: `api/requirements.txt`
- Create later: `api/tests/test_detective_core.py`
- Create later: `web/src/` frontend files
- Create later: `web/package.json`
- Create later: `docs/demo-script.md`
- Create later: `docs/project-report-template.md`
- Modify later only if present: `README.md`

## Implementation Steps

1. Bootstrap separate `api/` and `web/` services only if implementation is requested.
2. Implement Python core state and heuristic functions first.
3. Add BFS, DFS, UCS, Greedy, A*, IDS, IDA* with shared trace schema.
4. Add local search variants and mark completeness/optimality correctly.
5. Add educational demos for complex environment, CSP, and adversarial/stochastic groups.
6. Add detective case definitions and next-node prediction explanation.
7. Expose API endpoints for cases, runs, prediction validation, benchmark, and export pack.
8. Build a polished web UI around cases instead of a raw algorithm dropdown first.
9. Add benchmark and certificate output.
10. Add full export pack: Markdown, CSV, HTML, DOCX, and PDF.
11. Add tests for solvability, path validity, heuristic properties, known cases, trace selection rules, and API contracts.
12. Run Python compile/tests and frontend type/build checks before declaring implementation complete.

## Validation Plan

- Solvability: unsolvable states stop before expansion.
- Correctness: BFS/UCS/A* solve easy preset with same optimal path length.
- Heuristics: Manhattan is greater than or equal to misplaced on tested states and both ignore tile `0`.
- Trace: selected node matches algorithm priority rule for representative steps.
- Prediction: correct answer in each case matches the trace selection key.
- Report: Markdown includes PEAS, algorithm profile, certificate, trace story, benchmark, and academic limitations.

## Success Criteria

- [ ] Core tests pass for deterministic presets.
- [ ] UI can run a detective case from start to report export.
- [ ] At least one case demonstrates each major idea: uninformed search, heuristic search, local search trap, unsolvable parity, CSP/complex/adversarial educational model.
- [ ] Generated report is suitable for coursework submission.
- [ ] README explains how this project differs from the reference.

## Risk Assessment

- Risk: implementation exceeds a single coursework file. Mitigation: keep core and UI as two main files unless real complexity forces modules.
- Risk: educational demos confuse graders. Mitigation: add visible labels: “standard solver” vs “educational model.”
- Risk: stochastic algorithms create flaky tests. Mitigation: seed all stochastic cases and assert invariant outcomes, not exact random paths unless seed-fixed.

## Next Steps

- If user approves this plan, run a validation interview or start implementation from Phase 1.
- Do not implement until the user explicitly asks to cook/execute the plan.
