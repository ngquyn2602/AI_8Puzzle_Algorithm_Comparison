import base64
import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from eight_puzzle_detective_core import GOAL_STATE, benchmark, is_solvable, legal_moves, manhattan, misplaced, solve, validate_path
from main import app

client = TestClient(app)


def test_solvability_parity_detects_unsolvable_state():
    assert is_solvable((1, 2, 3, 4, 5, 6, 0, 7, 8)) is True
    assert is_solvable((1, 2, 3, 4, 5, 6, 8, 7, 0)) is False


def test_legal_moves_keep_valid_board_shape():
    moves = legal_moves((1, 2, 3, 4, 5, 6, 0, 7, 8))
    assert {action for action, _ in moves} == {"Up", "Right"}
    assert all(set(state) == set(range(9)) for _, state in moves)


def test_heuristics_ignore_blank_and_manhattan_dominates_misplaced():
    state = (1, 2, 3, 4, 5, 6, 0, 7, 8)
    assert misplaced(GOAL_STATE) == 0
    assert manhattan(state) >= misplaced(state)
    assert manhattan(GOAL_STATE) == 0


def test_astar_solves_easy_case_with_valid_certificate():
    result = solve("astar", (1, 2, 3, 4, 5, 6, 0, 7, 8))
    assert result.found is True
    assert result.path_cost == 2
    assert result.path[-1] == GOAL_STATE
    assert validate_path(result.path) is True
    assert result.certificate["path_valid"] is True


def test_solver_accepts_reference_algorithm_names():
    result = solve("A*", (1, 2, 3, 4, 5, 6, 0, 7, 8))
    assert result.algorithm == "astar"
    assert result.found is True
    assert result.path[-1] == GOAL_STATE


def test_unsolvable_stops_before_expansion():
    result = solve("astar", (1, 2, 3, 4, 5, 6, 8, 7, 0))
    assert result.found is False
    assert result.expanded == 0
    assert "Unsolvable" in result.message


def test_api_run_case_returns_trace_and_certificate():
    response = client.post("/api/run", json={"case_id": "case-easy-two-moves", "algorithm": "astar"})
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert data["certificate"]["path_valid"] is True
    assert data["trace_rows"]
    assert data["heuristic_evidence"]


def test_api_export_returns_full_pack_files():
    response = client.post("/api/export", json={"case_id": "case-easy-two-moves"})
    assert response.status_code == 200
    files = response.json()["files"]
    assert set(files) == {"detective-report.md", "trace.csv", "detective-report.html", "detective-report.docx", "detective-report.pdf"}


def test_api_export_pdf_has_required_pdf_structure():
    response = client.post("/api/export", json={"case_id": "case-easy-two-moves", "formats": ["pdf"]})
    assert response.status_code == 200
    encoded = response.json()["files"]["detective-report.pdf"]
    pdf = base64.b64decode(encoded)
    assert pdf.startswith(b"%PDF-1.4")
    assert b"xref" in pdf
    assert b"trailer" in pdf
    assert b"startxref" in pdf
    assert pdf.rstrip().endswith(b"%%EOF")


def test_api_benchmark_includes_standard_and_educational_rows():
    response = client.post("/api/benchmark", json={"case_id": "case-easy-two-moves"})
    assert response.status_code == 200
    algorithms = {row["algorithm"] for row in response.json()["rows"]}
    assert "csp" not in algorithms, "CSP Definition removed from benchmark — not a solver"
    assert "simple-hill-climbing" in algorithms
    assert {"bfs", "dfs", "ucs", "ids", "greedy", "astar", "ida", "hill-climbing", "stochastic-hill-climbing", "beam", "simulated-annealing", "minimax", "alpha-beta", "expectimax"}.issubset(algorithms)


def test_csp_definition_is_listed_but_not_benchmarked():
    response = client.get("/api/algorithm-groups")
    assert response.status_code == 200
    csp_aliases = {
        row["alias"]
        for row in response.json()["algorithms_by_group"]["Constraint Satisfaction Problems"]
    }
    assert {"csp", "csp-backtracking", "min-conflicts"}.issubset(csp_aliases)


def test_educational_algorithms_emit_multi_step_trace():
    result = solve("csp", (1, 2, 3, 4, 5, 6, 0, 7, 8))
    assert result.certificate["mode"] == "educational-model"
    assert result.certificate["canonical_8_puzzle_solver"] is False
    assert len(result.trace_rows) >= 4
    assert all("model_step" in row for row in result.trace_rows)


def test_adversarial_algorithms_use_caro_trace():
    result = solve("minimax", (1, 2, 3, 4, 5, 6, 0, 7, 8))
    assert result.found is True
    assert result.certificate["mode"] == "caro-adversarial-demo"
    assert result.certificate["game_tree_depth"] == 5
    assert result.certificate["nodes_evaluated"] > 1
    assert result.trace_rows[0]["board_kind"] == "caro"
    assert result.trace_rows[0]["caro_board"] == ("X", "O", "X", "O", "X", ".", ".", ".", "O")
    assert result.actions == ["Đặt X ô 7"]


def test_alpha_beta_reports_depth_bounded_pruning_stats():
    minimax = solve("minimax", (1, 2, 3, 4, 5, 6, 0, 7, 8))
    alpha_beta = solve("alpha-beta", (1, 2, 3, 4, 5, 6, 0, 7, 8))
    assert alpha_beta.actions == minimax.actions
    assert alpha_beta.certificate["mode"] == "caro-adversarial-demo"
    assert "pruned_branches" in alpha_beta.certificate
    assert alpha_beta.complete == "Bounded"


def test_api_predict_accepts_correct_next_node():
    response = client.post(
        "/api/predict",
        json={"case_id": "case-easy-two-moves", "selected_state": [1, 2, 3, 4, 5, 6, 7, 0, 8]},
    )
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"correct", "expected_state", "selected_state", "explanation"}
    assert data["expected_state"] == [1, 2, 3, 4, 5, 6, 7, 0, 8]
    assert data["correct"] is True


def test_api_predict_rejects_wrong_next_node():
    response = client.post(
        "/api/predict",
        json={"case_id": "case-easy-two-moves", "selected_state": [1, 2, 3, 4, 5, 0, 6, 7, 8]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is False
    assert data["expected_state"] == [1, 2, 3, 4, 5, 6, 7, 0, 8]


def test_ids_iterates_depth_limits_until_found():
    result = solve("ids", (1, 2, 3, 4, 5, 6, 0, 7, 8))
    assert result.found is True
    assert result.path[-1] == GOAL_STATE
    assert validate_path(result.path) is True
    limits_seen = {row["priority_rule"] for row in result.trace_rows}
    assert any("current limit" in rule for rule in limits_seen)


def test_bfs_and_dfs_produce_different_search_order():
    start = (1, 2, 3, 4, 5, 6, 0, 7, 8)
    bfs_result = solve("bfs", start)
    dfs_result = solve("dfs", start)

    assert bfs_result.found
    assert dfs_result.found

    bfs_order = [row["node"] for row in bfs_result.trace_rows]
    dfs_order = [row["node"] for row in dfs_result.trace_rows]
    assert bfs_order != dfs_order, (
        f"BFS and DFS must visit nodes in different order. "
        f"BFS first 3: {bfs_order[:3]}, DFS first 3: {dfs_order[:3]}"
    )


def test_bfs_and_astar_differ_on_nontrivial_puzzle():
    start = (1, 2, 3, 4, 0, 6, 7, 5, 8)
    bfs_result = solve("bfs", start)
    astar_result = solve("astar", start)

    assert bfs_result.found
    assert astar_result.found

    assert astar_result.expanded <= bfs_result.expanded, (
        f"A* expanded {astar_result.expanded}, BFS expanded {bfs_result.expanded}. "
        "A* with Manhattan heuristic should expand <= BFS nodes."
    )


def test_greedy_finds_suboptimal_path_in_trap_case():
    start = (1, 2, 3, 4, 0, 6, 7, 5, 8)
    greedy_result = solve("greedy", start)
    astar_result = solve("astar", start)

    assert greedy_result.found
    assert astar_result.found

    assert greedy_result.path_cost >= astar_result.path_cost, (
        f"Greedy path cost {greedy_result.path_cost}, A* path cost {astar_result.path_cost}. "
        "Greedy should not beat A* on path cost."
    )


def test_simple_hill_climbing_differs_from_steepest_ascent():
    start = (1, 2, 3, 4, 8, 5, 7, 6, 0)
    simple_result = solve("simple-hill-climbing", start)
    steepest_result = solve("hill-climbing", start)

    simple_trace = simple_result.trace_rows
    steepest_trace = steepest_result.trace_rows
    assert simple_trace
    assert steepest_trace

    # Trace rows must differ because algorithms use different selection rules
    assert simple_trace != steepest_trace, (
        "Simple and Steepest must produce different trace rows. "
        f"Simple trace count: {len(simple_trace)}, Steepest trace count: {len(steepest_trace)}"
    )

    simple_text = " ".join(str(row.get("explanation", "")) for row in simple_trace)
    steepest_text = " ".join(str(row.get("explanation", "")) for row in steepest_trace)
    assert "đầu tiên" in simple_text.lower(), f"Simple should mention 'đầu tiên': {simple_text[:200]}"
    assert "nhỏ nhất" in steepest_text.lower(), f"Steepest should mention 'nhỏ nhất': {steepest_text[:200]}"


def test_local_beam_keeps_multiple_states_in_beam():
    result = solve("beam", (1, 2, 3, 4, 5, 6, 0, 7, 8))
    assert result.found is True
    assert result.certificate["mode"] == "local-beam-search"
    assert result.certificate["beam_width"] == 3
    assert any(row["frontier_count"] >= 3 for row in result.trace_rows)


def test_csp_backtracking_is_bounded_legal_transition_demo():
    result = solve("csp-backtracking", (1, 2, 3, 4, 5, 6, 0, 7, 8), max_expansions=100)
    assert result.found is True
    assert result.certificate["mode"] == "csp-backtracking-bounded"
    assert result.certificate["canonical_8_puzzle_solver"] is False
    assert result.certificate["path_valid"] is True
    assert result.path[-1] == GOAL_STATE
    assert result.complete == "Bounded"


def test_min_conflicts_is_local_repair_not_canonical_solver():
    result = solve("min-conflicts", (1, 2, 3, 4, 8, 5, 7, 6, 0), max_expansions=20)
    assert result.certificate["mode"] == "min-conflicts-local-repair"
    assert result.certificate["canonical_8_puzzle_solver"] is False
    assert result.path
    assert all("Local repair" == row["model_step"] for row in result.trace_rows)


def test_ucs_differs_from_bfs_with_unit_costs():
    start = (1, 2, 3, 4, 0, 6, 7, 5, 8)
    bfs_result = solve("bfs", start)
    ucs_result = solve("ucs", start)

    assert bfs_result.found
    assert ucs_result.found

    assert bfs_result.path_cost == ucs_result.path_cost, (
        f"Both BFS and UCS should find optimal-cost paths for unit-cost 8-Puzzle. "
        f"BFS: {bfs_result.path_cost}, UCS: {ucs_result.path_cost}"
    )


def test_benchmark_runs_all_algorithms():
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


def test_cli_runs_algorithm_without_http_server():
    completed = subprocess.run(
        [
            sys.executable,
            "api/cli.py",
            "--start",
            "1,2,3,4,5,6,0,7,8",
            "--algorithm",
            "A*",
            "--trace-limit",
            "2",
        ],
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    assert "8-Puzzle Detective Lab CLI" in completed.stdout
    assert "Algorithm: A*" in completed.stdout
    assert "PEAS" in completed.stdout
    assert "Trace evidence" in completed.stdout


def test_gif_assets_are_verified_web_captures():
    subprocess.run(
        [
            sys.executable,
            "scripts/generate_algorithm_gifs.py",
            "--check",
        ],
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    manifest = json.loads(Path("docs/assets/algorithm-gifs/manifest.json").read_text(encoding="utf-8"))
    assert len(manifest) == 22
    assert all(item["source"] == "web-ui-playwright" for item in manifest)
    assert all(len(item["sha256"]) == 64 for item in manifest)


def test_ids_does_not_skip_shallower_path_revisited():
    # A test case where IDS must find a solution despite states being visited
    # at different depths in the search tree.
    start = (1, 2, 3, 4, 0, 6, 7, 5, 8)
    result = solve("ids", start, max_expansions=2000)
    assert result.found is True
    assert result.path[-1] == GOAL_STATE
    assert validate_path(result.path) is True
