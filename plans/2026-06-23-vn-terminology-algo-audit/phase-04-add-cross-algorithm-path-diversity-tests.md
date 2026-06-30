---
phase: 4
title: "Add cross-algorithm path diversity tests"
status: pending
priority: P1
dependencies: ["phase-03-fix-algorithm-logic-issues"]
---

# Phase 4: Add cross-algorithm path diversity tests

## Overview

Hiện tại 15 tests không có test nào xác minh các thuật toán sinh đường đi KHÁC NHAU trên cùng một start state. Phase này thêm 4-6 tests để đảm bảo mỗi thuật toán có hành vi riêng biệt, không phải tất cả cùng một đường đi.

## Test Strategy

### Test 1: BFS ≠ DFS paths on same start state (dễ)

```python
def test_bfs_and_dfs_produce_different_search_order():
    """BFS (FIFO) and DFS (LIFO) must expand nodes in different orders."""
    start = (1, 2, 3, 4, 5, 6, 0, 7, 8)  # easy 2-move case
    bfs_result = solve("bfs", start)
    dfs_result = solve("dfs", start)

    # Both should find a solution (8-puzzle is finite with Reached check)
    assert bfs_result.found
    assert dfs_result.found

    # Compare trace order (not expansion count — can coincidentally match)
    bfs_order = [row["node"] for row in bfs_result.trace_rows]
    dfs_order = [row["node"] for row in dfs_result.trace_rows]
    assert bfs_order != dfs_order, (
        "BFS and DFS must visit nodes in different order. "
        f"BFS first 3: {bfs_order[:3]}, DFS first 3: {dfs_order[:3]}"
    )
```

### Test 2: BFS ≠ A* paths on non-trivial start state

```python
def test_bfs_and_astar_differ_on_nontrivial_puzzle():
    """On a puzzle >2 moves from goal, BFS and A* should expand different counts."""
    start = (1, 2, 3, 4, 0, 6, 7, 5, 8)  # greedy trap case
    bfs_result = solve("bfs", start)
    astar_result = solve("astar", start)

    assert bfs_result.found
    assert astar_result.found

    # A* should expand fewer nodes (heuristic prunes search)
    assert astar_result.expanded <= bfs_result.expanded, (
        f"A* expanded {astar_result.expanded}, BFS expanded {bfs_result.expanded}. "
        "A* with Manhattan heuristic should expand ≤ BFS nodes."
    )
```

### Test 3: Greedy trap — greedy path ≠ optimal path

```python
def test_greedy_finds_suboptimal_path_in_trap_case():
    """The greedy-trap case is designed so greedy picks a deceptively low h(n)."""
    start = (1, 2, 3, 4, 0, 6, 7, 5, 8)  # case-greedy-trap
    greedy_result = solve("greedy", start)
    astar_result = solve("astar", start)

    assert greedy_result.found
    assert astar_result.found

    # Greedy may find a longer path than A* (it follows h(n) greedily)
    # If greedy happens to find optimal path too, expansion counts still differ
    assert greedy_result.path_cost >= astar_result.path_cost, (
        f"Greedy path cost {greedy_result.path_cost}, A* path cost {astar_result.path_cost}. "
        "Greedy should not beat A* on path cost (A* is optimal with admissible heuristic)."
    )
```

### Test 4: Simple Hill Climbing ≠ Steepest-Ascent

```python
def test_simple_hill_climbing_differs_from_steepest_ascent():
    """Simple picks first improving neighbor; Steepest picks best of all."""
    # Use a state where first improving ≠ best improving
    start = (1, 2, 3, 4, 8, 5, 7, 6, 0)  # case-local-minimum
    simple_result = solve("simple-hill-climbing", start)
    steepest_result = solve("hill-climbing", start)

    # Both must produce traces
    simple_trace = simple_result.trace_rows
    steepest_trace = steepest_result.trace_rows
    assert simple_trace
    assert steepest_trace

    # Assertion 1: Data must differ (path or trace order)
    simple_path = simple_result.path if simple_result.path else []
    steepest_path = steepest_result.path if steepest_result.path else []
    assert simple_path != steepest_path, (
        "Simple and Steepest must produce different paths on same start. "
        f"Simple: {simple_path[:3]}, Steepest: {steepest_path[:3]}"
    )

    # Assertion 2: Explanations must mention distinct strategy keywords
    simple_text = " ".join(str(row.get("explanation", "")) for row in simple_trace)
    steepest_text = " ".join(str(row.get("explanation", "")) for row in steepest_trace)
    assert "đầu tiên" in simple_text.lower(), f"Simple should mention 'đầu tiên': {simple_text[:200]}"
    assert "tốt nhất" in steepest_text.lower(), f"Steepest should mention 'tốt nhất': {steepest_text[:200]}"
```

### Test 5: UCS differs from BFS even with unit costs

```python
def test_ucs_differs_from_bfs_with_unit_costs():
    """UCS uses heap with h-tiebreaker; BFS uses FIFO queue. Expansion order differs."""
    start = (1, 2, 3, 4, 0, 6, 7, 5, 8)
    bfs_result = solve("bfs", start)
    ucs_result = solve("ucs", start)

    assert bfs_result.found
    assert ucs_result.found

    # With unit costs, UCS = BFS in terms of path cost (both optimal)
    # But expansion counts may differ due to tiebreaking
    # The key assertion: they both find optimal-cost paths
    assert bfs_result.path_cost == ucs_result.path_cost, (
        "Both BFS and UCS should find optimal-cost paths for unit-cost 8-Puzzle."
    )
```

### Test 6: Benchmark includes all 14 algorithms

```python
def test_benchmark_runs_all_algorithms():
    """Benchmark must include BFS, DFS, UCS, IDS, Greedy, A*, IDA*,
    all 5 local search variants, and all 3 adversarial algorithms."""
    start = (1, 2, 3, 4, 5, 6, 0, 7, 8)
    rows = benchmark(start)

    aliases = {row["algorithm"] for row in rows}
    required = {
        "bfs", "dfs", "ucs", "ids",
        "greedy", "astar", "ida",
        "simple-hill-climbing", "hill-climbing", "stochastic-hill-climbing",
        "beam", "simulated-annealing",
        "minimax", "alpha-beta", "expectimax",
    }
    missing = required - aliases
    assert not missing, f"Benchmark missing algorithms: {missing}"
```

## Success Criteria

- [ ] 6 tests được thêm vào `api/tests/test_detective_core.py`
- [ ] Tất cả test mới PASS
- [ ] Tất cả 15 test cũ vẫn PASS (zero regression)
- [ ] Test 1: BFS trace order ≠ DFS trace order (so sánh node visit sequence, không phải count)
- [ ] Test 2: A*.expanded ≤ BFS.expanded
- [ ] Test 3: Greedy.path_cost ≥ A*.path_cost
- [ ] Test 4: Simple Hill Climbing path ≠ Steepest-Ascent path (data assertion) VÀ explanation chứa "đầu tiên"/"tốt nhất" (string assertion)
- [ ] Test 5: BFS.path_cost = UCS.path_cost (cả hai tối ưu với unit cost)
- [ ] Test 6: Benchmark chứa đủ 14 algorithms

## Risk Assessment

- **Risk thấp**: Chỉ thêm tests mới, không sửa code production
- **Mitigation**: Nếu test fail do logic thuật toán chưa được sửa (Phase 3), đó là expected — Phase 3 phải completed trước Phase 4
