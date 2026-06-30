from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from heapq import heappop, heappush
from itertools import count
from math import exp
from random import Random
from time import perf_counter
from typing import Any, Callable, Iterable, Literal

State = tuple[int, ...]
GOAL_STATE: State = (1, 2, 3, 4, 5, 6, 7, 8, 0)
ACTIONS = {"Up": -3, "Down": 3, "Left": -1, "Right": 1}

ALGORITHM_GROUP_ORDER = [
    "Uninformed Search",
    "Informed Search",
    "Local Search",
    "Complex Environments",
    "Constraint Satisfaction Problems",
    "Adversarial / Stochastic Search",
]

ALGORITHM_GROUPS_VI = {
    "Uninformed Search": "Tìm kiếm không có thông tin",
    "Informed Search": "Tìm kiếm có thông tin",
    "Local Search": "Tìm kiếm cục bộ",
    "Complex Environments": "Môi trường phức tạp",
    "Constraint Satisfaction Problems": "Bài toán thỏa mãn ràng buộc",
    "Adversarial / Stochastic Search": "Tìm kiếm đối kháng / xác suất",
}

ALGORITHM_INFO: dict[str, dict[str, str]] = {
    "BFS": {"group": "Uninformed Search", "family": "Uninformed search", "complete": "Có", "optimal": "Có (cost=1)", "vi": "Tìm kiếm theo chiều rộng"},
    "DFS": {"group": "Uninformed Search", "family": "Uninformed search", "complete": "Không đảm bảo", "optimal": "Không", "vi": "Tìm kiếm theo chiều sâu"},
    "UCS": {"group": "Uninformed Search", "family": "Path-cost search", "complete": "Có", "optimal": "Có", "vi": "Tìm kiếm chi phí đồng nhất"},
    "IDS": {"group": "Uninformed Search", "family": "Iterative deepening search", "complete": "Có (đủ độ sâu)", "optimal": "Có (cost=1)", "vi": "Tìm kiếm sâu dần"},
    "Greedy": {"group": "Informed Search", "family": "Informed search", "complete": "Không đảm bảo", "optimal": "Không", "vi": "Tìm kiếm tham lam"},
    "A*": {"group": "Informed Search", "family": "Informed optimal search with admissible heuristic", "complete": "Có", "optimal": "Có (h admissible)", "vi": "Tìm kiếm A*"},
    "IDA*": {"group": "Informed Search", "family": "A* with iterative f-threshold deepening", "complete": "Có (đủ vòng lặp)", "optimal": "Có (h admissible)", "vi": "Tìm kiếm A* sâu dần"},
    "Simple Hill Climbing": {"group": "Local Search", "family": "Local search", "complete": "Không", "optimal": "Không", "vi": "Leo đồi đơn giản"},
    "Steepest-Ascent Hill Climbing": {"group": "Local Search", "family": "Local search", "complete": "Không", "optimal": "Không", "vi": "Leo đồi dốc nhất"},
    "Stochastic Hill Climbing": {"group": "Local Search", "family": "Randomized local search", "complete": "Không", "optimal": "Không", "vi": "Leo đồi ngẫu nhiên"},
    "Local Beam Search": {"group": "Local Search", "family": "Local beam search", "complete": "Không", "optimal": "Không", "vi": "Tìm kiếm tia cục bộ"},
    "Simulated Annealing": {"group": "Local Search", "family": "Stochastic local search with temperature schedule", "complete": "Không", "optimal": "Không", "vi": "Tôi luyện mô phỏng"},
    "AND-OR Search": {"group": "Complex Environments", "family": "Nondeterministic planning", "complete": "Bounded", "optimal": "Không", "vi": "Tìm kiếm AND-OR"},
    "No Observation Search": {"group": "Complex Environments", "family": "Belief-state search", "complete": "Bounded", "optimal": "Không", "vi": "Tìm kiếm không quan sát"},
    "Partially Observable Search": {"group": "Complex Environments", "family": "Belief update with partial observation", "complete": "Bounded", "optimal": "Không", "vi": "Tìm kiếm quan sát một phần"},
    "Online Search": {"group": "Complex Environments", "family": "Online LRTA*", "complete": "Bounded", "optimal": "Không", "vi": "Tìm kiếm trực tuyến (Online LRTA*)"},
    "CSP Definition": {"group": "Constraint Satisfaction Problems", "family": "CSP modeling", "complete": "N/A", "optimal": "N/A", "vi": "Mô hình thỏa mãn ràng buộc (CSP)"},
    "CSP Backtracking": {"group": "Constraint Satisfaction Problems", "family": "Bounded CSP backtracking search", "complete": "Bounded", "optimal": "Không claim toàn cục", "vi": "Tìm kiếm quay lui (Backtracking)"},
    "Min-Conflicts": {"group": "Constraint Satisfaction Problems", "family": "Local repair CSP", "complete": "Không", "optimal": "Không", "vi": "Tối thiểu xung đột (Min-Conflicts)"},
    "Minimax": {"group": "Adversarial / Stochastic Search", "family": "Depth-bounded adversarial game tree", "complete": "Bounded", "optimal": "Theo utility trong depth", "vi": "Tìm kiếm Minimax"},
    "Alpha-Beta Pruning": {"group": "Adversarial / Stochastic Search", "family": "Depth-bounded game tree with pruning", "complete": "Bounded", "optimal": "Giống Minimax nếu duyệt đủ cây", "vi": "Cắt tỉa Alpha-Beta"},
    "Expectimax": {"group": "Adversarial / Stochastic Search", "family": "Depth-bounded stochastic game tree", "complete": "Bounded", "optimal": "Theo kỳ vọng mô hình", "vi": "Tìm kiếm Expectimax"},
}

ALGORITHM_ALIASES: dict[str, str] = {
    "bfs": "BFS", "dfs": "DFS", "ucs": "UCS", "ids": "IDS",
    "greedy": "Greedy", "astar": "A*", "a*": "A*", "a_star": "A*", "ida": "IDA*", "ida*": "IDA*",
    "simple-hill-climbing": "Simple Hill Climbing",
    "hill-climbing": "Steepest-Ascent Hill Climbing", "hillclimbing": "Steepest-Ascent Hill Climbing",
    "stochastic-hill-climbing": "Stochastic Hill Climbing", "stochastic": "Stochastic Hill Climbing",
    "beam": "Local Beam Search", "local-beam": "Local Beam Search", "localbeam": "Local Beam Search",
    "simulated-annealing": "Simulated Annealing", "sa": "Simulated Annealing", "annealing": "Simulated Annealing",
    "and-or": "AND-OR Search", "andor": "AND-OR Search",
    "no-observation": "No Observation Search", "noobservation": "No Observation Search",
    "partial-observation": "Partially Observable Search", "partiallyobservable": "Partially Observable Search",
    "online": "Online Search", "lrta": "Online Search",
    "csp": "CSP Definition", "csp-definition": "CSP Definition",
    "csp-backtracking": "CSP Backtracking", "backtracking": "CSP Backtracking",
    "min-conflicts": "Min-Conflicts", "minconflicts": "Min-Conflicts",
    "minimax": "Minimax", "alpha-beta": "Alpha-Beta Pruning", "alphabeta": "Alpha-Beta Pruning",
    "expectimax": "Expectimax",
}

CANONICAL_ALGORITHMS = list(ALGORITHM_INFO.keys())
SOLVER_KEYS: dict[str, str] = {
    "BFS": "bfs", "DFS": "dfs", "UCS": "ucs", "IDS": "ids",
    "Greedy": "greedy", "A*": "astar", "IDA*": "ida",
    "Simple Hill Climbing": "simple-hill-climbing",
    "Steepest-Ascent Hill Climbing": "hill-climbing",
    "Stochastic Hill Climbing": "stochastic-hill-climbing",
    "Local Beam Search": "beam",
    "Simulated Annealing": "simulated-annealing",
    "AND-OR Search": "and-or",
    "No Observation Search": "no-observation",
    "Partially Observable Search": "partial-observation",
    "Online Search": "online",
    "CSP Definition": "csp",
    "CSP Backtracking": "csp-backtracking",
    "Min-Conflicts": "min-conflicts",
    "Minimax": "minimax",
    "Alpha-Beta Pruning": "alpha-beta",
    "Expectimax": "expectimax",
}
LOCAL_ALGORITHMS = {"hill-climbing", "stochastic-hill-climbing", "simple-hill-climbing", "beam", "simulated-annealing"}
ADVERSARIAL_ALGORITHMS = {"minimax", "alpha-beta", "expectimax"}
EDUCATIONAL_ALGORITHMS = {"and-or", "no-observation", "partial-observation", "online", "csp"}
CARO_START: tuple[str, ...] = ("X", "O", "X", "O", "X", ".", ".", ".", "O")
CARO_LINES = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))


def display_name(alias: str) -> str:
    """Return canonical display name (e.g. 'A*') for a solver alias ('astar')."""
    for name, key in SOLVER_KEYS.items():
        if key == alias:
            return name
    return alias


def group_of(alias: str) -> str:
    name = display_name(alias)
    return ALGORITHM_INFO.get(name, {}).get("group", "Uninformed Search")


def algorithm_groups() -> list[str]:
    return list(ALGORITHM_GROUP_ORDER)


def algorithms_by_group() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {group: [] for group in ALGORITHM_GROUP_ORDER}
    for name, info in ALGORITHM_INFO.items():
        grouped[info["group"]].append({
            "name": name,
            "alias": SOLVER_KEYS.get(name, name.lower()),
            "group": info["group"],
            "group_vi": ALGORITHM_GROUPS_VI.get(info["group"], info["group"]),
            "family": info["family"],
            "vi": info["vi"],
            "complete": info["complete"],
            "optimal": info["optimal"],
        })
    return grouped


def peas_model(alias: str) -> list[dict[str, str]]:
    name = display_name(alias)
    group = group_of(alias)
    info = ALGORITHM_INFO.get(name, {})
    env_map = {
        "Uninformed Search": "Môi trường 8-Puzzle 3x3 tất định, quan sát đầy đủ, chi phí mỗi bước = 1.",
        "Informed Search": "Môi trường 8-Puzzle chuẩn kèm heuristic h(n) ước lượng khoảng cách tới đích.",
        "Local Search": "Không gian trạng thái 8-Puzzle nhìn như landscape theo h(n); chỉ giữ 1 hoặc vài ứng viên.",
        "Complex Environments": "Mô hình mở rộng: trạng thái niềm tin, quan sát thiếu, học trực tuyến hoặc hành động không xác định.",
        "Constraint Satisfaction Problems": "CSP planning theo thời gian: biến X[t][p], A[t], ràng buộc Initial/Goal/AllDifferent/Transition.",
        "Adversarial / Stochastic Search": "Caro mini-game: MAX là X, MIN/Chance là O; 8-Puzzle chuẩn không có đối thủ.",
    }
    if group == "Adversarial / Stochastic Search":
        return [
            {
                "aspect": "Performance (Hiệu suất)",
                "definition": f"{name}: chọn nước đi có utility tốt nhất cho MAX trong trò Caro 3x3. Đầy đủ: {info.get('complete', 'N/A')}. Tối ưu: {info.get('optimal', 'N/A')}.",
            },
            {
                "aspect": "Environment (Môi trường)",
                "definition": "Bàn Caro 3x3: MAX là X, MIN hoặc Chance là O, trạng thái kết thúc là thắng/thua/hòa.",
            },
            {
                "aspect": "Actuators (Bộ chấp hành)",
                "definition": "Đặt quân X vào ô trống; Alpha-Beta cắt nhánh, Expectimax gán kỳ vọng cho phản ứng xác suất.",
            },
            {
                "aspect": "Sensors (Cảm biến)",
                "definition": "Quan sát bàn X/O, ô trống, dòng thắng tiềm năng, utility, alpha/beta hoặc kỳ vọng Chance.",
            },
        ]
    return [
        {
            "aspect": "Performance (Hiệu suất)",
            "definition": f"{name}: đạt Goal nếu là solver phù hợp; giảm chi phí đường đi, số node mở rộng/sinh ra, thời gian chạy và bộ nhớ. Đầy đủ: {info.get('complete', 'N/A')}. Tối ưu: {info.get('optimal', 'N/A')}.",
        },
        {
            "aspect": "Environment (Môi trường)",
            "definition": env_map.get(group, "Môi trường 8-Puzzle 3x3 với tuple 9 phần tử và goal cố định."),
        },
        {
            "aspect": "Actuators (Bộ chấp hành)",
            "definition": "Solver chuẩn: di chuyển ô trống Lên/Xuống/Trái/Phải nếu hợp lệ. Mô phỏng học thuật: chọn action, cập nhật niềm tin, ràng buộc hoặc điểm utility.",
        },
        {
            "aspect": "Sensors (Cảm biến)",
            "definition": "Quan sát board 3x3, vị trí ô trống, action hợp lệ, kiểm tra Goal, g(n)/h(n)/f(n); mô hình belief/game/CSP quan sát thêm niềm tin, ràng buộc và utility.",
        },
    ]


def action_vi(action: str) -> str:
    return {"Up": "Lên", "Down": "Xuống", "Left": "Trái", "Right": "Phải", "Start": "Bắt đầu"}.get(action, action)


def action_arrow(action: str) -> str:
    return {"Up": "↑", "Down": "↓", "Left": "←", "Right": "→", "Start": "●"}.get(action, "·")


@dataclass(frozen=True)
class DetectiveCase:
    id: str
    title: str
    start: State
    goal: State = GOAL_STATE
    algorithm: str = "astar"
    lesson: str = "Dự đoán node kế tiếp bằng cách đọc bằng chứng Frontier."


@dataclass
class Node:
    state: State
    parent: "Node | None" = None
    action: str = "Start"
    g: int = 0
    h: int = 0

    @property
    def f(self) -> int:
        return self.g + self.h


@dataclass
class SearchResult:
    algorithm: str
    start: State
    goal: State
    found: bool
    path: list[State] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    path_cost: int | None = None
    expanded: int = 0
    generated: int = 0
    max_frontier: int = 0
    reached_count: int = 0
    runtime_ms: float = 0.0
    trace_rows: list[dict[str, Any]] = field(default_factory=list)
    certificate: dict[str, Any] = field(default_factory=dict)
    autopsy: str = ""
    complete: str = "No"
    optimal: str = "No"
    message: str = ""


def normalize_state(values: Iterable[int]) -> State:
    state = tuple(int(v) for v in values)
    if len(state) != 9 or set(state) != set(range(9)):
        raise ValueError("State must contain each number from 0 to 8 exactly once.")
    return state


def inversions(state: State) -> int:
    tiles = [tile for tile in state if tile != 0]
    return sum(1 for i, left in enumerate(tiles) for right in tiles[i + 1 :] if left > right)


def is_solvable(start: State, goal: State = GOAL_STATE) -> bool:
    return inversions(start) % 2 == inversions(goal) % 2


def legal_moves(state: State) -> list[tuple[str, State]]:
    zero = state.index(0)
    row, col = divmod(zero, 3)
    allowed = []
    for action, offset in ACTIONS.items():
        if action == "Up" and row == 0 or action == "Down" and row == 2:
            continue
        if action == "Left" and col == 0 or action == "Right" and col == 2:
            continue
        swap = zero + offset
        board = list(state)
        board[zero], board[swap] = board[swap], board[zero]
        allowed.append((action, tuple(board)))
    return allowed


def misplaced(state: State, goal: State = GOAL_STATE) -> int:
    return sum(1 for index, tile in enumerate(state) if tile and tile != goal[index])


def manhattan(state: State, goal: State = GOAL_STATE) -> int:
    total = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue
        target = goal.index(tile)
        row, col = divmod(index, 3)
        target_row, target_col = divmod(target, 3)
        total += abs(row - target_row) + abs(col - target_col)
    return total


def heuristic_evidence(state: State, goal: State = GOAL_STATE) -> list[dict[str, Any]]:
    rows = []
    for index, tile in enumerate(state):
        if tile == 0:
            continue
        target = goal.index(tile)
        row, col = divmod(index, 3)
        target_row, target_col = divmod(target, 3)
        distance = abs(row - target_row) + abs(col - target_col)
        rows.append({"tile": tile, "current": index, "goal": target, "misplaced": int(index != target), "manhattan": distance})
    return rows


def reconstruct(node: Node) -> tuple[list[State], list[str]]:
    states: list[State] = []
    actions: list[str] = []
    cursor: Node | None = node
    while cursor:
        states.append(cursor.state)
        if cursor.parent:
            actions.append(cursor.action)
        cursor = cursor.parent
    return list(reversed(states)), list(reversed(actions))


def preview(nodes: Iterable[Node], limit: int = 6) -> list[dict[str, Any]]:
    return [{"state": n.state, "g": n.g, "h": n.h, "f": n.f, "action": n.action} for n in list(nodes)[:limit]]


def trace_row(step: int, algorithm: str, node: Node, frontier: Iterable[Node], reached: set[State], rule: str) -> dict[str, Any]:
    parent_state = node.parent.state if node.parent else node.state
    frontier_list = list(frontier)
    return {
        "step": step,
        "algorithm": algorithm,
        "algorithm_display": display_name(algorithm),
        "group": group_of(algorithm),
        "node": node.state,
        "parent_state": parent_state,
        "action": node.action,
        "action_vi": action_vi(node.action),
        "action_arrow": action_arrow(node.action),
        "depth": node.g,
        "g": node.g,
        "h": node.h,
        "f": node.f,
        "priority_rule": rule,
        "selection_key": selection_key(algorithm, node),
        "frontier_before": preview(frontier_list),
        "reached_before": list(reached)[:12],
        "frontier_count": len(frontier_list),
        "reached_count": len(reached),
        "explanation": explain_selection(algorithm, node),
    }


def selection_key(algorithm: str, node: Node) -> str:
    if algorithm in {"ucs", "bfs", "dfs", "ids"}:
        return f"g={node.g}"
    if algorithm == "greedy":
        return f"h={node.h}"
    return f"f={node.f}, h={node.h}"


def explain_selection(algorithm: str, node: Node) -> str:
    rules = {
        "bfs": f"BFS lấy node nông nhất (FIFO) — node {node.state} có độ sâu {node.g}.",
        "dfs": f"DFS lấy node sâu nhất (LIFO) — node {node.state} có độ sâu {node.g}.",
        "ucs": f"UCS lấy node có g(n) nhỏ nhất — g={node.g} cho node {node.state}.",
        "ids": f"IDS lặp DFS với giới hạn tăng dần — node {node.state} ở độ sâu {node.g}.",
        "greedy": f"Greedy lấy node có h(n) nhỏ nhất — h={node.h} cho node {node.state}.",
        "astar": f"A* lấy node có f(n)=g+h nhỏ nhất — f={node.f} (g={node.g}, h={node.h}).",
        "ida": f"IDA* DFS cắt theo ngưỡng f — node {node.state} có f={node.f}.",
        "simple-hill-climbing": f"Leo đồi đơn giản chọn láng giềng đầu tiên cải thiện — h={node.h}.",
        "hill-climbing": f"Leo đồi chọn láng giềng có h(n) nhỏ nhất — h={node.h}.",
        "stochastic-hill-climbing": f"Leo đồi ngẫu nhiên chọn trong láng giềng cải thiện — h={node.h}.",
        "beam": f"Local Beam giữ k trạng thái tốt nhất — node {node.state} có h={node.h}.",
        "simulated-annealing": f"Simulated Annealing chấp nhận neighbor theo xác suất e^(-Δh/T) — h={node.h}.",
        "and-or": f"AND-OR: OR chọn hành động, AND ghi mọi kết quả không xác định.",
        "no-observation": f"No Observation: chọn action cho trạng thái niềm tin.",
        "partial-observation": f"Partially Observable: cập nhật niềm tin theo quan sát một phần.",
        "online": f"Online LRTA*: cập nhật H(s), chuyển sang láng giềng tốt nhất.",
        "csp-backtracking": f"CSP Backtracking: gán biến theo ràng buộc, quay lui khi xung đột.",
        "min-conflicts": f"Min-Conflicts: sửa cục bộ biến vi phạm ràng buộc, chọn giá trị ít xung đột nhất.",
        "minimax": f"Minimax: MAX tối đa utility, MIN tối thiểu utility trên cây trò chơi Caro.",
        "alpha-beta": f"Alpha-Beta: Minimax có cắt nhánh không ảnh hưởng kết quả.",
        "expectimax": f"Expectimax: MAX chọn kỳ vọng cao nhất tại nút cơ hội.",
    }
    return rules.get(algorithm, f"Mô hình học thuật — node {node.state}.")


def solve(algorithm: str, start: State, goal: State = GOAL_STATE, heuristic: str = "manhattan", max_expansions: int = 500) -> SearchResult:
    start = normalize_state(start)
    goal = normalize_state(goal)
    normalized_algorithm = algorithm.lower()
    canonical_algorithm = ALGORITHM_ALIASES.get(normalized_algorithm) or next((name for name in ALGORITHM_INFO if name.lower() == normalized_algorithm), None)
    algorithm = SOLVER_KEYS.get(canonical_algorithm, normalized_algorithm) if canonical_algorithm else normalized_algorithm
    h_func = manhattan if heuristic == "manhattan" else misplaced
    if algorithm in LOCAL_ALGORITHMS:
        return local_demo(algorithm, start, goal, h_func, max_expansions)
    if algorithm in ADVERSARIAL_ALGORITHMS:
        return caro_demo(algorithm, start, goal)
    if algorithm == "csp-backtracking":
        return csp_backtracking_demo(start, goal, h_func, max_expansions)
    if algorithm == "min-conflicts":
        return min_conflicts_demo(start, goal, max_expansions)
    if algorithm in EDUCATIONAL_ALGORITHMS:
        return educational_demo(algorithm, start, goal)
    if not is_solvable(start, goal):
        return SearchResult(algorithm, start, goal, False, message="Unsolvable by inversion parity.", certificate=certificate(start, goal, []))
    if algorithm == "ids":
        return ids(start, goal, h_func, max_expansions)
    if algorithm == "ida":
        return ida_star(start, goal, h_func, max_expansions)
    return graph_search(algorithm, start, goal, h_func, max_expansions)


def graph_search(algorithm: str, start: State, goal: State, h_func: Callable[[State, State], int], max_expansions: int) -> SearchResult:
    start_time = perf_counter()
    root = Node(start, h=h_func(start, goal))
    reached: set[State] = {start}
    trace: list[dict[str, Any]] = []
    expanded = generated = max_frontier = 0
    order = count()
    queue: deque[Node] = deque([root])
    heap: list[tuple[int, int, int, Node]] = []
    uses_heap = algorithm in {"ucs", "greedy", "astar"}
    if uses_heap:
        heappush(heap, (priority(algorithm, root), root.h, next(order), root))
    while (heap if uses_heap else queue) and expanded < max_expansions:
        frontier_nodes = [item[3] for item in heap] if uses_heap else list(queue)
        node = heappop(heap)[3] if uses_heap else (queue.pop() if algorithm == "dfs" else queue.popleft())
        trace.append(trace_row(expanded, algorithm, node, frontier_nodes, reached, rule_for(algorithm)))
        if node.state == goal:
            path, actions = reconstruct(node)
            return finish(algorithm, start, goal, True, path, actions, expanded, generated, max_frontier, reached, trace, start_time)
        expanded += 1
        for action, child_state in legal_moves(node.state):
            if child_state in reached:
                continue
            child = Node(child_state, node, action, node.g + 1, h_func(child_state, goal))
            reached.add(child_state)
            generated += 1
            if uses_heap:
                heappush(heap, (priority(algorithm, child), child.h, next(order), child))
            else:
                queue.append(child)
        max_frontier = max(max_frontier, len(heap) if uses_heap else len(queue))
    return finish(algorithm, start, goal, False, [], [], expanded, generated, max_frontier, reached, trace, start_time, "Expansion limit reached.")


def priority(algorithm: str, node: Node) -> int:
    return {"ucs": node.g, "greedy": node.h, "astar": node.f}[algorithm]


def rule_for(algorithm: str) -> str:
    return {"bfs": "FIFO by depth", "dfs": "LIFO by depth", "ucs": "min g", "greedy": "min h", "astar": "min f=g+h"}.get(algorithm, "educational rule")


def ids(start: State, goal: State, h_func: Callable[[State, State], int], max_expansions: int) -> SearchResult:
    start_time = perf_counter()
    reached: dict[State, int] = {start: 0}
    trace: list[dict[str, Any]] = []
    expanded = generated = max_frontier = 0
    rule = "depth-limited DFS, current limit {limit}"

    def dls(state: State, path: list[State], actions: list[str], depth: int, limit: int) -> tuple[bool, list[State], list[str]]:
        nonlocal expanded, generated, max_frontier
        node = Node(state, None, actions[-1] if actions else "Start", len(path) - 1, h_func(state, goal))
        if state == goal:
            trace.append(trace_row(expanded, "ids", node, [], reached, rule.format(limit=limit)))
            return True, path, actions
        if depth >= limit or expanded >= max_expansions:
            return False, [], []
        expanded += 1
        frontier: list[Node] = []
        for action, child_state in legal_moves(state):
            child_g = node.g + 1
            if child_state in reached and reached[child_state] <= child_g:
                continue
            child = Node(child_state, node, action, child_g, h_func(child_state, goal))
            reached[child_state] = child_g
            generated += 1
            frontier.append(child)
        max_frontier = max(max_frontier, len(frontier))
        trace.append(trace_row(expanded - 1, "ids", node, frontier, reached, rule.format(limit=limit)))
        for child in frontier:
            found, p, a = dls(child.state, path + [child.state], actions + [child.action], depth + 1, limit)
            if found:
                return True, p, a
            if expanded >= max_expansions:
                return False, [], []
        return False, [], []

    for limit in range(0, 32):
        reached = {start: 0}
        found, path, actions = dls(start, [start], [], 0, limit)
        if found:
            return finish("ids", start, goal, True, path, actions, expanded, generated, max_frontier, reached, trace, start_time)
        if expanded >= max_expansions:
            return finish("ids", start, goal, False, [], [], expanded, generated, max_frontier, reached, trace, start_time, "Expansion limit reached.")
    return finish("ids", start, goal, False, [], [], expanded, generated, max_frontier, reached, trace, start_time, "Depth limit reached.")


def ida_star(start: State, goal: State, h_func: Callable[[State, State], int], max_expansions: int) -> SearchResult:
    start_time = perf_counter()
    trace: list[dict[str, Any]] = []
    expanded = generated = max_frontier = 0
    reached: set[State] = {start}
    threshold = h_func(start, goal)

    def dfs(node: Node, g: int, threshold: int, path: list[State], actions: list[str]) -> tuple[int, bool, list[State], list[str]]:
        nonlocal expanded, generated, max_frontier
        f = g + node.h
        if f > threshold:
            return f, False, [], []
        if node.state == goal:
            trace.append(trace_row(expanded, "ida", node, [], reached, f"iterative f-cost threshold {threshold}"))
            return f, True, path, actions
        expanded += 1
        if expanded > max_expansions:
            return f, False, [], []
        neighbors = [Node(s, node, a, g + 1, h_func(s, goal)) for a, s in legal_moves(node.state)]
        for n in neighbors:
            if n.state not in reached:
                reached.add(n.state)
                generated += 1
        max_frontier = max(max_frontier, len(neighbors))
        trace.append(trace_row(expanded - 1, "ida", node, neighbors, reached, f"iterative f-cost threshold {threshold}"))
        minimum = 10**9
        for n in neighbors:
            if n.state in {p for p in path}:
                continue
            t, found, p, a = dfs(n, g + 1, threshold, path + [n.state], actions + [n.action])
            if found:
                return t, True, p, a
            if t < minimum:
                minimum = t
        return minimum, False, [], []

    root = Node(start, h=h_func(start, goal))
    while True:
        reached = {start}
        t, found, path, actions = dfs(root, 0, threshold, [start], [])
        if found:
            return finish("ida", start, goal, True, path, actions, expanded, generated, max_frontier, reached, trace, start_time)
        if t == 10**9 or expanded > max_expansions:
            return finish("ida", start, goal, False, [], [], expanded, generated, max_frontier, reached, trace, start_time, "Threshold limit reached." if t == 10**9 else "Expansion limit reached.")
        threshold = t


def local_demo(algorithm: str, start: State, goal: State, h_func: Callable[[State, State], int], max_steps: int) -> SearchResult:
    if algorithm == "beam":
        return local_beam_demo(start, goal, h_func, max_steps)
    rng = Random(7)
    current = Node(start, h=h_func(start, goal))
    trace: list[dict[str, Any]] = []
    path = [start]
    max_frontier = 0
    start_time = perf_counter()
    for step in range(min(max_steps, 80)):
        neighbors = [Node(s, current, a, current.g + 1, h_func(s, goal)) for a, s in legal_moves(current.state)]
        max_frontier = max(max_frontier, len(neighbors))
        trace.append(trace_row(step, algorithm, current, neighbors, {n.state for n in neighbors}, "local choice by heuristic evidence"))
        if current.state == goal:
            break
        if algorithm == "simulated-annealing":
            nxt = rng.choice(neighbors)
            temp = max(0.1, 20 * (0.95**step))
            if nxt.h <= current.h or rng.random() < exp((current.h - nxt.h) / temp):
                current = nxt
        elif algorithm == "simple-hill-climbing":
            nxt = None
            for n in neighbors:
                if n.h < current.h:
                    nxt = n
                    break
            if nxt is None:
                break
            current = nxt
        else:
            ordered = sorted(neighbors, key=lambda n: n.h)
            nxt = ordered[0] if algorithm != "stochastic-hill-climbing" else rng.choice(ordered[:2])
            if nxt.h > current.h:
                break
            current = nxt
        path.append(current.state)
    found = current.state == goal
    actions = ["Investigate" for _ in path[1:]]
    return finish(algorithm, start, goal, found, path if found else [], actions if found else [], len(trace), len(trace), max_frontier, set(path), trace, start_time, autopsy=local_autopsy(algorithm, found))


def local_beam_demo(start: State, goal: State, h_func: Callable[[State, State], int], max_steps: int, beam_width: int = 3) -> SearchResult:
    start_time = perf_counter()
    root = Node(start, h=h_func(start, goal))
    beam = [root]
    reached: set[State] = {start}
    trace: list[dict[str, Any]] = []
    expanded = generated = max_frontier = 0
    best = root

    for step in range(min(max_steps, 80)):
        beam = sorted(beam, key=lambda node: (node.h, node.g, node.state))[:beam_width]
        best = beam[0]
        candidates: list[Node] = []
        for node in beam:
            expanded += 1
            for action, child_state in legal_moves(node.state):
                if child_state in reached:
                    continue
                child = Node(child_state, node, action, node.g + 1, h_func(child_state, goal))
                candidates.append(child)
                reached.add(child_state)
                generated += 1
        max_frontier = max(max_frontier, len(candidates), len(beam))
        row = trace_row(step, "beam", best, candidates, reached, f"local beam keeps k={beam_width} best states by h(n)")
        row["selection_key"] = f"beam best h={best.h}, beam_size={len(beam)}"
        row["explanation"] = f"Local Beam duy trì {len(beam)} trạng thái tốt nhất, mở song song rồi giữ {beam_width} ứng viên có h(n) thấp nhất."
        trace.append(row)
        if best.state == goal:
            path, actions = reconstruct(best)
            result = finish("beam", start, goal, True, path, actions, expanded, generated, max_frontier, reached, trace, start_time, autopsy=local_autopsy("beam", True))
            result.certificate |= {"mode": "local-beam-search", "beam_width": beam_width}
            return result
        if not candidates:
            break
        beam = sorted(candidates, key=lambda node: (node.h, node.g, node.state))[:beam_width]

    found = best.state == goal
    path, actions = reconstruct(best) if found else ([], [])
    result = finish("beam", start, goal, found, path, actions, expanded, generated, max_frontier, reached, trace, start_time, "Beam exhausted." if not found else "", autopsy=local_autopsy("beam", found))
    result.certificate |= {"mode": "local-beam-search", "beam_width": beam_width}
    return result


def caro_demo(algorithm: str, start: State, goal: State) -> SearchResult:
    start_time = perf_counter()
    board = CARO_START
    depth = 5
    candidates, game_stats = caro_candidates(board, algorithm, depth)
    best = candidates[0]
    trace = [
        caro_trace_row(0, algorithm, board, candidates, "MAX đang cân nhắc nước đi trên bàn Caro 3x3."),
        caro_trace_row(1, algorithm, best["board"], candidates[1:], best["explanation"]),
    ]
    return SearchResult(
        algorithm,
        start,
        goal,
        True,
        path=[start],
        actions=[best["action"]],
        path_cost=1,
        expanded=game_stats["nodes"],
        generated=len(candidates),
        max_frontier=len(candidates),
        reached_count=2,
        runtime_ms=round((perf_counter() - start_time) * 1000, 3),
        trace_rows=trace,
        certificate={
            "mode": "caro-adversarial-demo",
            "caro_start": board,
            "chosen_action": best["action"],
            "utility": best["utility"],
            "game_tree_depth": depth,
            "nodes_evaluated": game_stats["nodes"],
            "pruned_branches": game_stats["pruned"],
        },
        autopsy=caro_autopsy(algorithm, best),
        complete="Bounded",
        optimal="Theo utility depth-bounded" if algorithm != "expectimax" else "Theo kỳ vọng depth-bounded",
        message="Đã chọn nước đi Caro theo cây game/chance giới hạn độ sâu.",
    )


def caro_candidates(board: tuple[str, ...], algorithm: str, depth: int) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows = []
    total_stats = {"nodes": 0, "pruned": 0}
    for index, cell in enumerate(board):
        if cell != ".":
            continue
        next_board = board[:index] + ("X",) + board[index + 1:]
        stats = {"nodes": 0, "pruned": 0}
        if algorithm == "alpha-beta":
            utility = caro_alpha_beta(next_board, depth - 1, False, -10_000.0, 10_000.0, stats)
            explanation = f"Đặt X tại ô {index + 1}: Alpha-Beta trả utility={utility:.1f}, đã cắt {stats['pruned']} nhánh trong cây con."
        elif algorithm == "expectimax":
            utility = caro_expectimax(next_board, depth - 1, False, stats)
            explanation = f"Đặt X tại ô {index + 1}: Expectimax trả utility kỳ vọng={utility:.1f} khi O là chance node."
        else:
            utility = caro_minimax(next_board, depth - 1, False, stats)
            explanation = f"Đặt X tại ô {index + 1}: Minimax trả utility={utility:.1f} sau khi MIN phản ứng tối ưu."
        total_stats["nodes"] += stats["nodes"]
        total_stats["pruned"] += stats["pruned"]
        rows.append({"index": index, "board": next_board, "action": f"Đặt X ô {index + 1}", "utility": round(utility, 2), "explanation": explanation, "nodes": stats["nodes"], "pruned": stats["pruned"]})
    return sorted(rows, key=lambda item: item["utility"], reverse=True), total_stats


def caro_minimax(board: tuple[str, ...], depth: int, maximizing: bool, stats: dict[str, int]) -> float:
    stats["nodes"] += 1
    if depth == 0 or caro_winner(board) or "." not in board:
        return float(caro_utility(board))
    mark = "X" if maximizing else "O"
    values = [caro_minimax(caro_place(board, index, mark), depth - 1, not maximizing, stats) for index, cell in enumerate(board) if cell == "."]
    return max(values) if maximizing else min(values)


def caro_alpha_beta(board: tuple[str, ...], depth: int, maximizing: bool, alpha: float, beta: float, stats: dict[str, int]) -> float:
    stats["nodes"] += 1
    if depth == 0 or caro_winner(board) or "." not in board:
        return float(caro_utility(board))
    mark = "X" if maximizing else "O"
    moves = [index for index, cell in enumerate(board) if cell == "."]
    if maximizing:
        value = -10_000.0
        for index in moves:
            value = max(value, caro_alpha_beta(caro_place(board, index, mark), depth - 1, False, alpha, beta, stats))
            alpha = max(alpha, value)
            if alpha >= beta:
                stats["pruned"] += len(moves) - moves.index(index) - 1
                break
        return value
    value = 10_000.0
    for index in moves:
        value = min(value, caro_alpha_beta(caro_place(board, index, mark), depth - 1, True, alpha, beta, stats))
        beta = min(beta, value)
        if alpha >= beta:
            stats["pruned"] += len(moves) - moves.index(index) - 1
            break
    return value


def caro_expectimax(board: tuple[str, ...], depth: int, maximizing: bool, stats: dict[str, int]) -> float:
    stats["nodes"] += 1
    if depth == 0 or caro_winner(board) or "." not in board:
        return float(caro_utility(board))
    moves = [index for index, cell in enumerate(board) if cell == "."]
    if maximizing:
        return max(caro_expectimax(caro_place(board, index, "X"), depth - 1, False, stats) for index in moves)
    values = [caro_expectimax(caro_place(board, index, "O"), depth - 1, True, stats) for index in moves]
    return sum(values) / len(values)


def caro_place(board: tuple[str, ...], index: int, mark: str) -> tuple[str, ...]:
    return board[:index] + (mark,) + board[index + 1:]


def caro_trace_row(step: int, algorithm: str, board: tuple[str, ...], candidates: list[dict[str, Any]], explanation: str) -> dict[str, Any]:
    utility = caro_utility(board)
    return {
        "step": step,
        "algorithm": algorithm,
        "algorithm_display": display_name(algorithm),
        "group": group_of(algorithm),
        "node": GOAL_STATE,
        "parent_state": GOAL_STATE,
        "action": "Caro",
        "action_vi": "Nước đi Caro",
        "action_arrow": "✕",
        "depth": step,
        "g": step,
        "h": utility,
        "f": utility,
        "priority_rule": caro_rule(algorithm),
        "selection_key": f"utility={utility}",
        "frontier_before": [
            {"state": GOAL_STATE, "g": 0, "h": item["utility"], "f": item["utility"], "action": item["action"], "board": item["board"]}
            for item in candidates[:6]
        ],
        "reached_before": [],
        "frontier_count": len(candidates),
        "reached_count": step + 1,
        "explanation": explanation,
        "board_kind": "caro",
        "caro_board": board,
        "utility": utility,
    }


def caro_rule(algorithm: str) -> str:
    return {
        "minimax": "MAX chọn nước đi có utility lớn nhất sau phản ứng làm giảm utility của MIN",
        "alpha-beta": "Minimax với alpha/beta để cắt nhánh không thể đổi quyết định",
        "expectimax": "MAX chọn utility kỳ vọng khi đối thủ/Chance phản ứng xác suất",
    }[algorithm]


def caro_autopsy(algorithm: str, best: dict[str, Any]) -> str:
    return f"{display_name(algorithm)} chạy cây Caro 3x3 giới hạn độ sâu: chọn '{best['action']}' với utility={best['utility']}, đánh giá {best.get('nodes', '-')} node trong nhánh tốt nhất."


def caro_utility(board: tuple[str, ...]) -> int:
    winner = caro_winner(board)
    if winner == "X":
        return 100
    if winner == "O":
        return -100
    return caro_open_lines(board, "X") * 10 - caro_open_lines(board, "O") * 8


def caro_winner(board: tuple[str, ...]) -> str | None:
    for line in CARO_LINES:
        marks = {board[index] for index in line}
        if len(marks) == 1 and "." not in marks:
            return board[line[0]]
    return None


def caro_open_lines(board: tuple[str, ...], mark: str) -> int:
    opponent = "O" if mark == "X" else "X"
    return sum(1 for line in CARO_LINES if opponent not in {board[index] for index in line})


def csp_backtracking_demo(start: State, goal: State, h_func: Callable[[State, State], int], max_expansions: int) -> SearchResult:
    start_time = perf_counter()
    trace: list[dict[str, Any]] = []
    reached: set[State] = {start}
    expanded = generated = max_frontier = 0
    horizon_cap = min(10, max(1, max_expansions))

    def backtrack(node: Node, path: list[State], actions: list[str], horizon: int) -> tuple[bool, list[State], list[str]]:
        nonlocal expanded, generated, max_frontier
        candidates = [
            Node(child_state, node, action, node.g + 1, h_func(child_state, goal))
            for action, child_state in legal_moves(node.state)
            if child_state not in path
        ]
        candidates.sort(key=lambda item: (item.h, item.g, item.state))
        max_frontier = max(max_frontier, len(candidates))
        row = trace_row(len(trace), "csp-backtracking", node, candidates, reached, f"bounded CSP backtracking horizon={horizon}")
        row["selection_key"] = f"depth={node.g}/{horizon}, constraints=legal-transition"
        row["explanation"] = "Gán biến trạng thái kế tiếp sao cho thỏa Initial/Transition/AllDifferent; nếu nhánh không đạt Goal trong horizon thì quay lui."
        row["model_step"] = "Backtracking assignment"
        trace.append(row)
        if node.state == goal:
            return True, path, actions
        if node.g >= horizon or expanded >= max_expansions:
            return False, [], []
        expanded += 1
        for child in candidates:
            reached.add(child.state)
            generated += 1
            found, found_path, found_actions = backtrack(child, path + [child.state], actions + [child.action], horizon)
            if found:
                return True, found_path, found_actions
        return False, [], []

    for horizon in range(horizon_cap + 1):
        root = Node(start, h=h_func(start, goal))
        found, path, actions = backtrack(root, [start], [], horizon)
        if found:
            result = finish("csp-backtracking", start, goal, True, path, actions, expanded, generated, max_frontier, reached, trace, start_time, autopsy="CSP Backtracking tìm được assignment theo legal transition trong horizon bounded.")
            result.complete = "Bounded"
            result.optimal = "Trong horizon đầu tiên tìm thấy"
            result.certificate |= {"mode": "csp-backtracking-bounded", "horizon": horizon, "canonical_8_puzzle_solver": False}
            return result
        if expanded >= max_expansions:
            break
    result = finish("csp-backtracking", start, goal, False, [], [], expanded, generated, max_frontier, reached, trace, start_time, "Bounded CSP horizon/expansion limit reached.", autopsy="CSP Backtracking không tìm được assignment trong horizon/limit đã cấu hình; đây không phải proof unsolvable toàn cục.")
    result.complete = "Bounded"
    result.optimal = "Không claim toàn cục"
    result.certificate |= {"mode": "csp-backtracking-bounded", "horizon_cap": horizon_cap, "canonical_8_puzzle_solver": False}
    return result


def min_conflicts_demo(start: State, goal: State, max_steps: int) -> SearchResult:
    start_time = perf_counter()
    current = start
    path = [current]
    actions: list[str] = []
    trace: list[dict[str, Any]] = []
    reached: set[State] = {current}
    rng = Random(11)
    step_cap = min(max_steps, 20)

    for step in range(step_cap):
        conflicts = conflict_positions(current, goal)
        node = Node(current, None, "Repair", step, len(conflicts))
        candidates = min_conflict_candidates(current, goal, node)
        row = trace_row(step, "min-conflicts", node, candidates, reached, "local repair: choose conflicted tile and minimize violated positions")
        row["selection_key"] = f"conflicts={len(conflicts)}"
        row["explanation"] = "Min-Conflicts sửa assignment bằng swap tile gây xung đột; đây là repair trace, không phải chuỗi legal blank moves."
        row["model_step"] = "Local repair"
        trace.append(row)
        if not conflicts:
            break
        best_score = min((candidate.h for candidate in candidates), default=len(conflicts))
        best_candidates = [candidate for candidate in candidates if candidate.h == best_score]
        if not best_candidates:
            break
        chosen = rng.choice(best_candidates)
        current = chosen.state
        path.append(current)
        actions.append(chosen.action)
        reached.add(current)

    found = current == goal
    cert = certificate(start, goal, path) | {
        "mode": "min-conflicts-local-repair",
        "canonical_8_puzzle_solver": False,
        "repair_goal_reached": found,
        "path_valid": validate_path(path),
    }
    return SearchResult(
        "min-conflicts",
        start,
        goal,
        found,
        path,
        actions,
        None,
        expanded=len(trace),
        generated=sum(row.get("frontier_count", 0) for row in trace),
        max_frontier=max((row.get("frontier_count", 0) for row in trace), default=0),
        reached_count=len(reached),
        runtime_ms=round((perf_counter() - start_time) * 1000, 3),
        trace_rows=trace,
        certificate=cert,
        autopsy="Min-Conflicts có thể sửa arrangement về Goal, nhưng swap repair không phải đường đi legal blank-move của 8-Puzzle.",
        complete="Không",
        optimal="Không",
        message="Local repair model, not a standard 8-Puzzle solver.",
    )


def conflict_positions(state: State, goal: State) -> list[int]:
    return [index for index, tile in enumerate(state) if tile != 0 and tile != goal[index]]


def min_conflict_candidates(state: State, goal: State, parent: Node) -> list[Node]:
    candidates: list[Node] = []
    for index in conflict_positions(state, goal):
        tile = state[index]
        target = goal.index(tile)
        repaired = list(state)
        repaired[index], repaired[target] = repaired[target], repaired[index]
        candidate_state = tuple(repaired)
        candidates.append(Node(candidate_state, parent, f"Repair tile {tile}", parent.g + 1, misplaced(candidate_state, goal)))
    return sorted(candidates, key=lambda node: (node.h, node.state))


def educational_demo(algorithm: str, start: State, goal: State) -> SearchResult:
    start_time = perf_counter()
    story = educational_story(algorithm)
    trace: list[dict[str, Any]] = []
    reached: set[State] = {start}
    parent: Node | None = None
    state = start

    for step, scene in enumerate(story):
        action = "Start"
        if step:
            moves = legal_moves(state)
            action, state = moves[(step - 1) % len(moves)]
            reached.add(state)
        node = Node(state, parent, action, step, misplaced(state, goal))
        frontier = [Node(child, node, move, step + 1, misplaced(child, goal)) for move, child in legal_moves(state)]
        row = trace_row(step, algorithm, node, frontier, reached, scene["rule"])
        row["selection_key"] = scene["key"]
        row["explanation"] = scene["explanation"]
        row["model_step"] = scene["label"]
        trace.append(row)
        parent = node

    model_certificate = certificate(start, goal, []) | {
        "mode": "educational-model",
        "canonical_8_puzzle_solver": False,
        "model": display_name(algorithm),
    }
    return SearchResult(
        algorithm,
        start,
        goal,
        False,
        expanded=len(trace),
        generated=sum(int(row.get("frontier_count", 0)) for row in trace),
        max_frontier=max((int(row.get("frontier_count", 0)) for row in trace), default=0),
        reached_count=len(reached),
        runtime_ms=round((perf_counter() - start_time) * 1000, 3),
        trace_rows=trace,
        certificate=model_certificate,
        autopsy="Đây là mô hình học thuật; dùng solver chuẩn nếu cần đường đi 8-Puzzle canonical.",
        complete="Model",
        optimal="Model",
        message="Educational model, not a standard solver.",
    )


def educational_story(algorithm: str) -> list[dict[str, str]]:
    stories = {
        "and-or": [
            ("OR node", "OR chooses one action with a viable subplan", "action set", "OR node represents the agent decision."),
            ("AND outcomes", "AND requires every nondeterministic outcome to be covered", "all outcomes covered", "One action may lead to multiple possible states; the plan must cover all of them."),
            ("Subplan", "Attach a subplan to each AND outcome", "conditional subplan", "Each outcome receives its own branch."),
            ("Policy", "Merge branches into a conditional policy", "policy ready", "The result is a policy, not one canonical 8-Puzzle path."),
        ],
        "no-observation": [
            ("Belief start", "Belief state is a set of possible states", "belief size=3", "The agent cannot see the real state, so it tracks a set of possibilities."),
            ("Blind action", "Choose an action that is safe across the belief", "safe action", "The action is selected for the belief set, not one visible board."),
            ("Belief update", "Result creates a new belief set", "belief updated", "After acting, the agent updates all possible outcomes."),
            ("Goal test", "Every state in belief must satisfy the goal", "strong goal", "With no observation, goal certainty must hold for the whole belief set."),
        ],
        "partial-observation": [
            ("Prior belief", "Initialize belief before the sensor reading", "prior", "The agent starts with several possible states."),
            ("Observe", "Receive a partial observation", "sensor clue", "The sensor gives a clue, not the full board."),
            ("Filter", "Remove states inconsistent with the observation", "filtered belief", "The belief set is filtered by the observation model."),
            ("Act", "Choose an action over the filtered belief", "belief action", "The choice is belief-aware, not a shortest-path certificate."),
        ],
        "online": [
            ("Current state", "LRTA* stands at the current state", "H(s)", "The agent learns about neighbors only after reaching a state."),
            ("Lookahead", "Estimate neighbor costs", "min c+H", "It scores available actions with temporary learned heuristic values."),
            ("Learn", "Update H(s) from experience", "H(s) updated", "The heuristic is learned online instead of fixed like A*."),
            ("Move", "Commit to the best current neighbor", "online move", "The agent moves one step, observes again, then repeats."),
        ],
        "csp": [
            ("Variables", "CSP = X, D, C", "X[t][p], A[t]", "Variables describe time-indexed board positions and actions."),
            ("Domains", "Assign domains to tile and action variables", "D assigned", "Domains restrict tiles, positions, and legal actions."),
            ("Constraints", "Check Initial, Goal, AllDifferent, Transition", "C checked", "Constraints keep every board and transition legal."),
            ("Horizon", "Planning CSP needs a bounded horizon T", "bounded model", "CSP Definition is modeling; it becomes solving only after a horizon and constraint solver are chosen."),
        ],
        "csp-backtracking": [
            ("Pick variable", "Pick an unassigned CSP variable", "next variable", "Backtracking extends one variable assignment."),
            ("Try value", "Try a value that satisfies current constraints", "candidate value", "A value survives only if it respects current constraints."),
            ("Conflict", "Backtrack when a constraint fails", "constraint fail", "Bad branches are cut early."),
            ("Bounded answer", "Complete assignment within the horizon", "assignment complete", "The answer is horizon-bounded evidence, not a global optimality claim."),
        ],
        "min-conflicts": [
            ("Initial assignment", "Start from a complete but possibly invalid assignment", "conflicts>0", "Min-Conflicts repairs an existing assignment."),
            ("Choose conflicted", "Pick a variable involved in a conflict", "conflicted variable", "The focus is a variable causing constraint failures."),
            ("Repair value", "Move to the value with fewest conflicts", "min conflicts", "The chosen value reduces failed constraints as much as possible."),
            ("Iterate", "Repeat until solved or capped", "local repair", "This is local repair; it can get stuck and does not prove unsolvability."),
        ],
    }
    labels = stories.get(algorithm, stories["csp"])
    return [{"label": label, "rule": rule, "key": key, "explanation": explanation} for label, rule, key, explanation in labels]


def finish(algorithm: str, start: State, goal: State, found: bool, path: list[State], actions: list[str], expanded: int, generated: int, max_frontier: int, reached: set[State], trace: list[dict[str, Any]], start_time: float, message: str = "", autopsy: str | None = None) -> SearchResult:
    return SearchResult(algorithm, start, goal, found, path, actions, len(actions) if found else None, expanded, generated, max_frontier, len(reached), round((perf_counter() - start_time) * 1000, 3), trace, certificate(start, goal, path), autopsy or default_autopsy(algorithm, found, expanded), complete_flag(algorithm), optimal_flag(algorithm), message or ("Solved." if found else "No solution found within limit."))


def certificate(start: State, goal: State, path: list[State]) -> dict[str, Any]:
    return {"start": start, "goal": goal, "solvable": is_solvable(start, goal), "path_valid": validate_path(path), "path_length": max(0, len(path) - 1), "inversions_start": inversions(start), "inversions_goal": inversions(goal)}


def validate_path(path: list[State]) -> bool:
    return not path or all(any(child == b for _, child in legal_moves(a)) for a, b in zip(path, path[1:]))


def complete_flag(algorithm: str) -> str:
    return "Yes" if algorithm in {"bfs", "ucs", "ids", "astar", "ida"} else "No/conditional"


def optimal_flag(algorithm: str) -> str:
    return "Yes" if algorithm in {"bfs", "ucs", "astar", "ida"} else "No"


def default_autopsy(algorithm: str, found: bool, expanded: int) -> str:
    status = "đã tìm thấy lời giải" if found else "chưa chứng minh được lời giải trong giới hạn cấu hình"
    return f"{algorithm.upper()} {status} sau {expanded} lần mở rộng node. So sánh độ ưu tiên trong Frontier để hiểu đường đi quyết định."


def local_autopsy(algorithm: str, found: bool) -> str:
    status = "đã thoát tới Goal" if found else "cho thấy bằng chứng cục bộ có thể kẹt trước lời giải toàn cục"
    return f"{algorithm} {status}; tính đầy đủ và tối ưu không được bảo đảm."


CASES = [
    DetectiveCase("case-easy-two-moves", "Easy Two-Move Scenario", (1, 2, 3, 4, 5, 6, 0, 7, 8), algorithm="astar", lesson="A* combines path cost and Manhattan distance evidence."),
    DetectiveCase("case-greedy-trap", "Greedy Trap", (1, 2, 3, 4, 0, 6, 7, 5, 8), algorithm="greedy", lesson="Low h(n) can mask a worse overall path."),
    DetectiveCase("case-ida-threshold", "IDA* Threshold", (1, 2, 3, 5, 0, 6, 4, 7, 8), algorithm="ida", lesson="IDA* repeats searches under iteratively increasing f-cost thresholds."),
    DetectiveCase("case-unsolvable-parity", "Unsolvable Parity", (1, 2, 3, 4, 5, 6, 8, 7, 0), algorithm="astar", lesson="Inversion parity prevents impossible cases from expanding nodes."),
    DetectiveCase("case-local-minimum", "Local Minimum", (1, 2, 3, 4, 8, 5, 7, 6, 0), algorithm="hill-climbing", lesson="Local search algorithms can get stuck due to short-term evidence."),
    DetectiveCase("case-caro-adversarial", "Adversarial Caro", (1, 2, 3, 4, 5, 6, 7, 8, 0), algorithm="minimax", lesson="3x3 Caro: MAX is X, MIN/Chance is O. The algorithm chooses moves based on utility instead of 8-Puzzle distance."),
]


def get_case(case_id: str) -> DetectiveCase:
    for case in CASES:
        if case.id == case_id:
            return case
    raise KeyError(case_id)


def benchmark(start: State, goal: State = GOAL_STATE) -> list[dict[str, Any]]:
    rows = []
    for algorithm in [
        "bfs", "dfs", "ucs", "ids",
        "greedy", "astar", "ida",
        "simple-hill-climbing", "hill-climbing", "stochastic-hill-climbing", "beam", "simulated-annealing",
        "minimax", "alpha-beta", "expectimax",
    ]:
        result = solve(algorithm, start, goal, max_expansions=350)
        rows.append({"algorithm": algorithm, "found": result.found, "path_cost": result.path_cost, "expanded": result.expanded, "generated": result.generated, "runtime_ms": result.runtime_ms, "complete": result.complete, "optimal": result.optimal})
    return rows
