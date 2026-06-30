---
phase: 3
title: "Fix algorithm logic issues"
status: pending
priority: P0
dependencies: []
---

# Phase 3: Fix algorithm logic issues

## Overview

Sửa 4 lỗi logic thuật toán nghiêm trọng: (1) Simple Hill Climbing = Steepest-Ascent (cùng code path), (2) CSP Definition là "thuật toán chạy được" nhưng vô nghĩa, (3) benchmark thiếu DFS/IDS/stochastic variants, (4) thiếu caro case cho adversarial.

## Changes

### Issue 1 (P0): Simple Hill Climbing = Steepest-Ascent — tách riêng code path

**File:** `api/eight_puzzle_detective_core.py` — `local_demo()` (lines 533-560)

**Root cause:** Cả "Simple Hill Climbing" và "Steepest-Ascent Hill Climbing" map về cùng key `"hill-climbing"` trong `SOLVER_KEYS` (line 82-83). Trong `local_demo()`, code chỉ phân biệt `"stochastic-hill-climbing"` với phần còn lại. Cả hai thuật toán đều lấy `ordered[0]` (nước đi tốt nhất), đó là hành vi của **Steepest-Ascent**, không phải Simple.

**Behavior đúng:**
- **Simple Hill Climbing**: Duyệt láng giềng theo thứ tự phát sinh (Up/Down/Left/Right), chọn **nước đi đầu tiên** có h(n) cải thiện, không cần tìm nước đi tốt nhất.
- **Steepest-Ascent Hill Climbing**: Duyệt TẤT CẢ láng giềng, chọn nước đi có h(n) **tốt nhất**.

**Implementation:**

```python
# Step 1: Thêm key riêng cho simple hill climbing
SOLVER_KEYS = {
    ...
    "Simple Hill Climbing": "simple-hill-climbing",       # NEW — distinct key
    "Steepest-Ascent Hill Climbing": "hill-climbing",
    ...
}

# Step 2: Thêm 'simple-hill-climbing' vào LOCAL_ALGORITHMS
LOCAL_ALGORITHMS = {"hill-climbing", "stochastic-hill-climbing", "simple-hill-climbing", "beam", "simulated-annealing"}

# Step 3: Sửa local_demo() để phân biệt simple vs steepest
def local_demo(algorithm: str, start: State, goal: State, h_func, max_expansions: int = 500) -> SearchResult:
    ...
    for step in range(min(max_steps, 80)):
        neighbors = [Node(...) for a, s in legal_moves(current.state)]
        ...
        if algorithm == "simulated-annealing":
            # ... (unchanged)
        elif algorithm == "simple-hill-climbing":          # NEW BRANCH
            # Duyệt theo thứ tự phát sinh, chọn nước đi đầu tiên cải thiện
            nxt = None
            for n in neighbors:
                if n.h < current.h:
                    nxt = n
                    break
            if nxt is None:
                break  # stuck — không có láng giềng nào tốt hơn
            current = nxt
        else:
            # steepest-ascent hoặc stochastic
            ordered = sorted(neighbors, key=lambda n: n.h)
            nxt = ordered[0] if algorithm != "stochastic-hill-climbing" else rng.choice(ordered[:2])
            if nxt.h > current.h:
                break
            current = nxt
    ...
```

Điều này đảm bảo:
- Simple Hill Climbing có thể dừng ở một local minimum khác với Steepest-Ascent
- Trace và metrics khác nhau giữa hai thuật toán
- Simple Hill Climbing có thể tìm thấy đường đi ngắn hơn hoặc dài hơn tùy trường hợp

### Issue 2 (P0): CSP Definition không phải là thuật toán — đổi thành model-only

**File:** `api/eight_puzzle_detective_core.py`

**Root cause:** `"CSP Definition"` map vào SOLVER_KEYS → `"csp"` → EDUCATIONAL_ALGORITHMS → `educational_demo()` trả về dummy result. "CSP Definition" là khung mô hình ràng buộc, không phải thuật toán. Không thể "chạy" nó.

**Fix:** Xóa "CSP Definition" khỏi SOLVER_KEYS, giữ lại trong ALGORITHM_INFO để hiển thị như một mục tham khảo (có thể hiển thị PEAS model riêng), nhưng không cho phép "chạy" như một thuật toán.

```python
# Step 1: Xóa dòng này khỏi SOLVER_KEYS
# "CSP Definition": "csp",   # REMOVED — không phải thuật toán

# Step 2: Trong main.py list_algorithms(), lọc bỏ CSP Definition
# hoặc đánh dấu nó là non-runnable
```

**Alternate approach (nhẹ hơn):** Giữ CSP Definition trong dropdown nhưng đánh dấu "Mô hình tham khảo" và khi chọn sẽ hiển thị giải thích thay vì nút "Chạy thuật toán". Tuy nhiên approach này phức tạp hơn. **Recommend: xóa khỏi SOLVER_KEYS, giữ trong ALGORITHM_INFO.**

### Issue 3 (P1): Benchmark thiếu thuật toán — mở rộng danh sách

**File:** `api/eight_puzzle_detective_core.py` — `benchmark()` (line 737)

```python
# Before — only 8 algorithms:
for algorithm in ["bfs", "ucs", "greedy", "astar", "ida", "hill-climbing", "csp", "expectimax"]:

# After — đầy đủ 14 algorithms:
for algorithm in [
    "bfs", "dfs", "ucs", "ids",           # uninformed
    "greedy", "astar", "ida",              # informed
    "simple-hill-climbing", "hill-climbing", "stochastic-hill-climbing", "beam", "simulated-annealing",  # local
    "minimax", "alpha-beta", "expectimax", # adversarial
]:
```

Lưu ý:
- Thêm `"dfs"` và `"ids"` vào nhóm uninformed
- Thêm `"simple-hill-climbing"` (mới từ Issue 1), `"stochastic-hill-climbing"`, `"beam"` đầy đủ
- Thêm `"minimax"` và `"alpha-beta"` vào adversarial (hiện chỉ có `"expectimax"`)
- LOẠI BỎ `"csp"` khỏi benchmark (không phải solver thực sự)

### Issue 4 (P2): Caro case trong test assertion — đã thêm ở fix trước

Case `case-caro-adversarial` đã được thêm vào CASES list (line 724). Test `test_adversarial_algorithms_use_caro_trace` đã pass. Không cần thay đổi gì thêm.

## Related Code Files

- **Modify:** `api/eight_puzzle_detective_core.py` — SOLVER_KEYS, LOCAL_ALGORITHMS, local_demo(), benchmark()
- **Modify:** `api/main.py` — list_algorithms() nếu cần lọc CSP Definition

## Success Criteria

- [ ] Chạy Simple Hill Climbing → trace hiển thị "chọn láng giềng đầu tiên cải thiện"
- [ ] Chạy Steepest-Ascent → trace hiển thị "chọn láng giềng tốt nhất trong tất cả"
- [ ] Hai thuật toán sinh đường đi KHÁC NHAU trên cùng một start state không tầm thường
- [ ] CSP Definition không xuất hiện trong dropdown "Thuật toán" (hoặc xuất hiện nhưng không chạy được)
- [ ] `POST /api/benchmark` trả về 14 rows (không còn 8)
- [ ] Tất cả test pass: `python -m pytest api/tests/ -v`
- [ ] Test regression: `test_adversarial_algorithms_use_caro_trace` vẫn pass

### Validation notes (2026-06-23)

Sau validation, bổ sung các mục còn thiếu:

- **Issue 1 bổ sung**: Cần thêm `"simple-hill-climbing": "Simple Hill Climbing"` vào `ALGORITHM_ALIASES` (line 62-63) để `solve()` resolve được alias. Cần thêm case `"simple-hill-climbing"` vào `explain_selection()` (line 353-374) để trace có giải thích đúng ("chọn láng giềng đầu tiên cải thiện").
- **Issue 2 clarified**: CSP Definition — xóa khỏi `SOLVER_KEYS` và `EDUCATIONAL_ALGORITHMS`, giữ trong `ALGORITHM_INFO`. Sửa `main.py:list_algorithms()` filter bỏ entries không có trong `SOLVER_KEYS`. CSP Backtracking và Min-Conflicts giữ nguyên.
- **Pre-flight check**: Grep `web/src/` cho string `"hill-climbing"`, `"csp"` trước khi đổi SOLVER_KEYS để đảm bảo không có hardcode alias cũ ở frontend.

## Risk Assessment

- **Risk cao cho Issue 1**: Thay đổi SOLVER_KEYS có thể break dropdown algorithm ở frontend (nếu frontend hardcode alias). Cần verify CustomSelect vẫn hiển thị đúng. Đã thêm pre-flight grep check.
- **Risk trung bình cho Issue 2**: Xóa CSP Definition khỏi SOLVER_KEYS. Đã trace hết blast radius — chỉ cần sửa `list_algorithms()` filter + xóa `"csp"` khỏi `EDUCATIONAL_ALGORITHMS`.
- **Risk thấp cho Issue 3**: Chỉ thêm entry vào loop, không đụng logic.
