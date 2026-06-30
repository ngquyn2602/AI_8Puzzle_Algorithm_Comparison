from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from typing import Any

from eight_puzzle_detective_core import (
    ALGORITHM_ALIASES,
    CASES,
    GOAL_STATE,
    SOLVER_KEYS,
    algorithm_groups,
    algorithms_by_group,
    display_name,
    get_case,
    group_of,
    normalize_state,
    peas_model,
    solve,
)

State = tuple[int, ...]


def parse_state(value: str) -> State:
    cleaned = value.strip().replace("[", "").replace("]", "").replace(";", ",")
    if "," in cleaned:
        parts = [part.strip() for part in cleaned.split(",") if part.strip()]
    else:
        parts = cleaned.split()
        if len(parts) == 1 and len(parts[0]) == 9 and parts[0].isdigit():
            parts = list(parts[0])
    try:
        return normalize_state(int(part) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def format_board(state: State) -> str:
    cells = ["·" if tile == 0 else str(tile) for tile in state]
    rows = [cells[index : index + 3] for index in range(0, 9, 3)]
    return "\n".join("  " + " ".join(f"{cell:>1}" for cell in row) for row in rows)


def available_algorithms() -> set[str]:
    names = {name.lower() for name in SOLVER_KEYS}
    aliases = set(ALGORITHM_ALIASES) | set(SOLVER_KEYS.values())
    return names | aliases


def validate_algorithm(value: str) -> str:
    if value.lower() not in available_algorithms():
        choices = ", ".join(sorted(SOLVER_KEYS.values()))
        raise argparse.ArgumentTypeError(f"Unknown algorithm '{value}'. Use one of: {choices}")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run 8-Puzzle Detective Lab algorithms directly with Python, no FastAPI server needed.",
    )
    parser.add_argument("--case", dest="case_id", help="Preset case id, e.g. case-easy-two-moves")
    parser.add_argument("--start", type=parse_state, help="Start board as '1,2,3,4,5,6,0,7,8' or '123456078'")
    parser.add_argument("--goal", type=parse_state, default=GOAL_STATE, help="Goal board; defaults to 1,2,3,4,5,6,7,8,0")
    parser.add_argument("--algorithm", type=validate_algorithm, help="Algorithm alias, e.g. bfs, astar, ida, alpha-beta")
    parser.add_argument("--heuristic", choices=["manhattan", "misplaced"], default="manhattan")
    parser.add_argument("--max-expansions", type=int, default=500)
    parser.add_argument("--trace-limit", type=int, default=12)
    parser.add_argument("--path-limit", type=int, default=20)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON instead of the narrative report")
    parser.add_argument("--list-cases", action="store_true", help="List preset cases and exit")
    parser.add_argument("--list-algorithms", action="store_true", help="List algorithm groups and exit")
    return parser


def resolve_input(args: argparse.Namespace) -> tuple[State, State, str]:
    if args.case_id:
        case = get_case(args.case_id)
        return case.start, case.goal, args.algorithm or case.algorithm
    if args.start is None:
        raise SystemExit("Provide --case or --start.")
    return args.start, args.goal, args.algorithm or "astar"


def result_payload(result: Any, algorithm: str) -> dict[str, Any]:
    payload = asdict(result)
    payload["algorithm_display"] = display_name(algorithm)
    payload["algorithm_group"] = group_of(algorithm)
    payload["peas"] = peas_model(algorithm)
    return payload


def print_cases() -> None:
    for case in CASES:
        print(f"{case.id}: {case.title}")
        print(f"  algorithm: {case.algorithm}")
        print(f"  lesson: {case.lesson}")
        print(format_board(case.start))


def print_algorithms() -> None:
    grouped = algorithms_by_group()
    for group in algorithm_groups():
        print(group)
        for row in grouped[group]:
            print(f"  - {row['alias']:<24} {row['vi']}")


def print_text_report(payload: dict[str, Any], trace_limit: int, path_limit: int) -> None:
    certificate = payload["certificate"]
    print("8-Puzzle Detective Lab CLI")
    print("=" * 28)
    print(f"Algorithm: {payload['algorithm_display']} ({payload['algorithm']})")
    print(f"Group: {payload['algorithm_group']}")
    print(f"Found: {payload['found']} | Message: {payload['message']}")
    print(f"Path cost: {payload['path_cost']} | Expanded: {payload['expanded']} | Generated: {payload['generated']}")
    print(f"Reached: {payload['reached_count']} | Max frontier: {payload['max_frontier']} | Runtime: {payload['runtime_ms']} ms")
    print(f"Certificate: solvable={certificate['solvable']}, path_valid={certificate['path_valid']}, inversions={certificate['inversions_start']}/{certificate['inversions_goal']}")
    print()
    print("PEAS")
    for row in payload["peas"]:
        print(f"- {row['aspect']}: {row['definition']}")
    print()
    print("Start")
    print(format_board(tuple(payload["start"])))
    print("Goal")
    print(format_board(tuple(payload["goal"])))
    print()
    print("Solution path")
    path = [tuple(state) for state in payload["path"]]
    actions = payload["actions"]
    if not path:
        print("  No solved path in this run.")
    for index, state in enumerate(path[:path_limit]):
        action = "Start" if index == 0 else actions[index - 1]
        print(f"Step {index}: {action}")
        print(format_board(state))
    if len(path) > path_limit:
        print(f"... {len(path) - path_limit} more path steps hidden")
    print()
    print("Trace evidence")
    for row in payload["trace_rows"][:trace_limit]:
        print(f"Step {row.get('step')}")
        print(f"Rule: {row.get('priority_rule')}")
        print(f"Selected by: {row.get('selection_key')}")
        print(f"Action: {row.get('action_arrow', '·')} {row.get('action')} / {row.get('action_vi', row.get('action'))}")
        print(f"Scores: depth={row.get('depth')} | g={row.get('g')} | h={row.get('h')} | f={row.get('f')}")
        print(f"Why: {row.get('explanation', '')}")
        print("Parent state")
        print(format_board(tuple(row.get("parent_state", payload["start"]))))
        print("Current state")
        print(format_board(tuple(row.get("node", payload["start"]))))
        frontier = row.get("frontier_before", [])
        if frontier:
            print("Frontier candidates before selection")
            for index, candidate in enumerate(frontier[:4], start=1):
                print(f"Candidate {index}: action={candidate.get('action')} g={candidate.get('g')} h={candidate.get('h')} f={candidate.get('f')}")
                print(format_board(tuple(candidate.get("state", payload["start"]))))
            if len(frontier) > 4:
                print(f"... {len(frontier) - 4} more frontier candidates hidden")
        print("-" * 28)
    if len(payload["trace_rows"]) > trace_limit:
        print(f"... {len(payload['trace_rows']) - trace_limit} more trace rows hidden")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args()
    if args.list_cases:
        print_cases()
        return
    if args.list_algorithms:
        print_algorithms()
        return
    start, goal, algorithm = resolve_input(args)
    result = solve(algorithm, start, goal, args.heuristic, args.max_expansions)
    payload = result_payload(result, algorithm)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print_text_report(payload, args.trace_limit, args.path_limit)


if __name__ == "__main__":
    main()
