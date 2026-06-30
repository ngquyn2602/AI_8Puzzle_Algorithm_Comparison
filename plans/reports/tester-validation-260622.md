# 8-Puzzle Detective Lab -- Tester Validation Report

Date: 2026-06-22  
Branch: master (no prior commits; initial baseline)  
Scope: Full suite (no diff history to scope against)

---

## Test Results Overview

| Metric | Value |
|---|---|
| Backend tests run | 8 |
| Backend tests passed | 8 |
| Backend tests failed | 0 |
| Frontend build | PASS (588ms, 0 errors) |

Detailed test output:

```
api/tests/test_detective_core.py::test_solvability_parity_detects_unsolvable_state PASSED
api/tests/test_detective_core.py::test_legal_moves_keep_valid_board_shape PASSED
api/tests/test_detective_core.py::test_heuristics_ignore_blank_and_manhattan_dominates_misplaced PASSED
api/tests/test_detective_core.py::test_astar_solves_easy_case_with_valid_certificate PASSED
api/tests/test_detective_core.py::test_unsolvable_stops_before_expansion PASSED
api/tests/test_detective_core.py::test_api_run_case_returns_trace_and_certificate PASSED
api/tests/test_detective_core.py::test_api_export_returns_full_pack_files PASSED
api/tests/test_detective_core.py::test_api_benchmark_includes_standard_and_educational_rows PASSED
```

---

## Coverage Metrics

| File | Stmts | Miss | Cover |
|---|---|---|---|
| api/eight_puzzle_detective_core.py | 244 | 17 | 93% |
| api/main.py | 123 | 20 | 84% |
| api/tests/conftest.py | 3 | 0 | 100% |
| api/tests/test_detective_core.py | 46 | 0 | 100% |
| **TOTAL** | **416** | **37** | **91%** |

---

## Required Coverage Areas -- Verdict

| Area | Test | Status |
|---|---|---|
| Solvability (inversion parity) | `test_solvability_parity_detects_unsolvable_state` | PASS -- tests both solvable and unsolvable states |
| Legal moves | `test_legal_moves_keep_valid_board_shape` | PASS -- verifies action set and state validity |
| Heuristics (manhattan + misplaced) | `test_heuristics_ignore_blank_and_manhattan_dominates_misplaced` | PASS -- confirms blank ignored, manhattan >= misplaced, zero at goal |
| A* solving | `test_astar_solves_easy_case_with_valid_certificate` | PASS -- path_cost=2, path valid, certificate valid |
| Unsolvable rejection | `test_unsolvable_stops_before_expansion` | PASS -- found=False, expanded=0, message contains "Unsolvable" |
| API run | `test_api_run_case_returns_trace_and_certificate` | PASS -- 200, found, certificate, trace_rows, heuristic_evidence present |
| API export | `test_api_export_returns_full_pack_files` | PASS -- all 5 formats (md, csv, html, docx, pdf) returned |
| Benchmark rows | `test_api_benchmark_includes_standard_and_educational_rows` | PASS -- bfs, astar, csp, expectimax all present |

All 8 required areas are covered and passing. No gaps in the checklist.

---

## Coverage Gaps (Uncovered Branches/Statements)

### eight_puzzle_detective_core.py (93%)

| Line(s) | Symbol | Risk | Why untested |
|---|---|---|---|
| 68 | `normalize_state` ValueError raise | Low | Invalid state tuple (wrong length/values) -- defensive input validation, reachable via API |
| 193 | `solve` calling `ids()` for algorithm="ids" | Medium | `ids()` body is never reached -- line 242 returns on first iteration, never loops. Currently dead code. |
| 230 | `graph_search` expansion limit reached branch | Low | `max_expansions=500` never hit for easy case; only reachable with hard puzzles or lower limit |
| 242-249 | `ids()` body (for loop, depth-limit header) | Medium | Dead code: `graph_search("dfs")` always returns, loop exits on iteration 0 |
| 272-275 | `simulated-annealing` branch in `local_demo` | Low | No test case uses simulated-annealing algorithm |
| 280 | `nxt.h > current.h` break in hill-climbing | Low | Reachable only when local search hits a minimum |
| 335 | `get_case` KeyError raise | Medium | No test calls `get_case` with unknown case_id |

### main.py (84%)

| Line(s) | Endpoint/Function | Risk | Why untested |
|---|---|---|---|
| 50 | GET /healthz | Low | Health probe -- trivial, zero risk |
| 55 | GET /readyz | Low | Readiness probe -- trivial, zero risk |
| 60-61 | GET /metrics | Low | Bare Prometheus metric -- trivial |
| 66 | GET /api/cases | Low | List all cases -- straightforward |
| 71-74 | GET /api/cases/{case_id} 404 branch | Low | Error handling for missing case |
| 86-93 | POST /api/predict (prediction check) | Medium | Student-facing validation endpoint -- no test at all |
| 130-132 | `resolve_run_input` 422 error branch | Low | Missing both case_id and start in request |

---

## Suggested Additional Tests (Prioritized)

### P1 -- Medium Risk (add soon)

1. **POST /api/predict** -- Student detective prediction check. Validates that the detective selects the correct next node from frontier evidence. Missing entirely.
   - Happy path: correct prediction returns `correct: true`
   - Wrong prediction: returns `correct: false` with expected_state
   - Missing case: returns 404

2. **`get_case` with unknown ID** -- Validates error handling when case_id does not exist. Currently `KeyError` is uncaught at call sites (would become 500).

3. **`normalize_state` invalid input** -- Tests that bad input (wrong length, duplicate tiles) raises ValueError. Ensures API properly rejects malformed states.

### P2 -- Low Risk (add for completeness)

4. **`ids()` and `ida_star()` algorithm paths** -- Both are simplified wrappers in the core. `ids()` body is effectively dead code (returns on first DFS call, never iterates). Either test or fix the dead loop.

5. **`simulated-annealing` and `hill-climbing` local search** -- The benchmark endpoint includes hill-climbing but no test exercises local_demo for any LOCAL_ALGORITHM.

6. **API edge cases** -- /api/run with missing case_id and start (422), /api/export with specific format subsets, /api/cases listing all 5 cases.

---

## Frontend Build

```
web/dist/index.html         0.40 kB (gzip: 0.27 kB)
web/dist/assets/index-xxx.css  2.53 kB (gzip: 1.15 kB)
web/dist/assets/index-xxx.js  199.56 kB (gzip: 62.91 kB)
```

Build completed in 588ms with `tsc && vite build`. No TypeScript errors. No warnings.

---

## Performance

- All 8 backend tests: **0.60s** (no coverage) / **0.78s** (with coverage)
- No slow tests -- all passed in < 0.15s each
- Frontend build: **588ms** (well under budget)

---

## Critical Issues

None. All tests pass, build succeeds, all required coverage areas verified.

---

## Recommendations

1. Add test for POST /api/predict (the student-facing detective validation endpoint) -- highest priority gap.
2. Add test for `get_case` with unknown case_id to verify error handling.
3. Fix or test the `ids()` dead loop (lines 242-249) -- currently returns on iteration 0 regardless of depth limit.
4. Add a test exercising `local_demo` with simulated-annealing to cover lines 272-275.
5. Consider adding trivial tests for /healthz, /readyz, /metrics endpoints (Docker HEALTHCHECK depends on these).

---

## Unresolved Questions

- The `ids()` function (line 241-249) has a for-loop that always returns on the first iteration. Is this intentional (placeholder for future iterative deepening) or a bug? The `ida_star()` function follows the same simplified pattern.
- Are the `simulated-annealing` and `stochastic-hill-climbing` algorithms expected to produce solutions, or are they purely demonstrative (showing how local search can stall)? The educational_demo path handles this explicitly; local_demo does not.
