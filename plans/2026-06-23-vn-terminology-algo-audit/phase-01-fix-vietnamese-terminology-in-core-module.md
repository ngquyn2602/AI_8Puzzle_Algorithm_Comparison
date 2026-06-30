---
phase: 1
title: "Fix Vietnamese terminology in core module"
status: pending
priority: P1
dependencies: []
---

# Phase 1: Fix Vietnamese terminology in core module

## Overview

Sửa tất cả lỗi thuật ngữ Tiếng Việt trong `api/eight_puzzle_detective_core.py`: dịch sai, code-switching nửa Anh nửa Việt không nhất quán, case title sai nghĩa. Các thuật ngữ kỹ thuật cốt lõi (Frontier, Heuristic, Node, Utility, tên thuật toán) được giữ Tiếng Anh có chủ đích — đây là cách dạy CS chuẩn ở Việt Nam.

## Nguyên tắc dịch

| Từ gốc (EN) | Nên dịch (VN) | Nên giữ (EN) | Lý do |
|---|---|---|---|
| Frontier | - | Frontier | Thuật ngữ kỹ thuật AI chuẩn |
| Heuristic | - | Heuristic | Không có từ VN tương đương chính xác |
| Node | - | Node | Thuật ngữ CS chuẩn toàn cầu |
| Utility | - | Utility | Thuật ngữ game theory chuẩn |
| A*, BFS, DFS, IDA* | - | A*, BFS, DFS, IDA* | Tên riêng thuật toán |
| depth | độ sâu | - | Dễ dịch, nên dịch |
| neighbor | láng giềng | - | Có từ VN tương đương |
| successor | nút kế | - | Nên dịch |
| action | hành động | - | Nên dịch |
| terminal (state) | trạng thái kết thúc | - | Nên dịch |
| goal | đích | - | Nên dịch |
| conflict | xung đột | - | Nên dịch |
| beam | tia | - | "chùm" là sai |
| local minimum | cực tiểu cục bộ | - | "ngõ cụt" là sai hoàn toàn |

## Changes

### File: `api/eight_puzzle_detective_core.py`

#### 1. Sửa "chùm" → "tia" (Beam Search) — line 45

```python
# Before:
"Local Beam Search": {"...", "vi": "Tìm kiếm chùm cục bộ", ...},
# After:
"Local Beam Search": {"...", "vi": "Tìm kiếm tia cục bộ", ...},
```

#### 2. Sửa case title sai nghĩa — line 723

```python
# Before: "Ngõ cụt cực tiểu cục bộ" (means "dead end of local minimum" — nonsense)
DetectiveCase("case-local-minimum", "Ngõ cụt cực tiểu cục bộ", ...)
# After:
DetectiveCase("case-local-minimum", "Cực tiểu cục bộ", ...)
```

#### 3. Sửa "depth" → "độ sâu" trong explain_selection() — lines 355-358

```python
# Before:
"bfs": f"BFS lấy node nông nhất (FIFO) — node ... có depth {node.depth}.",
"dfs": f"DFS lấy node sâu nhất (LIFO) — node ... có depth {node.depth}.",
"ids": f"IDS lặp DFS với limit tăng dần — node ... ở depth {node.depth}.",

# After:
"bfs": f"BFS lấy node nông nhất (FIFO) — node ... độ sâu {node.depth}.",
"dfs": f"DFS lấy node sâu nhất (LIFO) — node ... độ sâu {node.depth}.",
"ids": f"IDS lặp DFS với giới hạn tăng dần — node ... độ sâu {node.depth}.",
```

#### 4. Sửa "neighbor" → "láng giềng" — lines 362-363, 369

```python
# Before:
"hill-climbing": "Leo đồi chọn neighbor có h(n) nhỏ nhất...",
"stochastic-hill-climbing": "Leo đồi ngẫu nhiên chọn trong neighbor cải thiện...",
"online": "Online LRTA*: cập nhật H(s), chuyển sang neighbor tốt nhất.",

# After:
"hill-climbing": "Leo đồi chọn láng giềng có h(n) nhỏ nhất...",
"stochastic-hill-climbing": "Leo đồi ngẫu nhiên chọn trong láng giềng cải thiện...",
"online": "Online LRTA*: cập nhật H(s), chuyển sang láng giềng tốt nhất.",
```

#### 5. Sửa "action" → "hành động" — line 366

```python
# Before: "AND-OR: OR chọn action, AND ghi mọi kết quả không xác định."
# After:  "AND-OR: OR chọn hành động, AND ghi mọi kết quả không xác định."
```

#### 6. Sửa "conflict" → "xung đột" — line 370

```python
# Before: "...quay lui khi conflict."
# After:  "...quay lui khi xung đột."
```

#### 7. Sửa "cây game" → "cây trò chơi" — lines 371, 593

```python
# Before (line 371): "...trên cây game Caro."
# After:              "...trên cây trò chơi Caro."

# Before (line 593): "Có (trong cây game giới hạn)"
# After:              "Có (trong cây trò chơi giới hạn)"
```

#### 8. Sửa "terminal" → "kết thúc" — line 157

```python
# Before: "...trạng thái terminal là thắng/thua/hòa."
# After:  "...trạng thái kết thúc là thắng/thua/hòa."
```

#### 9. Sửa PEAS environment text — lines 142-145

```python
# Before:
"Môi trường 8-Puzzle 3×3 deterministic, fully observable, cost mỗi bước = 1."
# After:
"Môi trường 8-Puzzle 3×3 tất định, quan sát đầy đủ, chi phí mỗi bước = 1."

# Before:
"Môi trường 8-Puzzle chuẩn kèm heuristic h(n) ước lượng khoảng cách tới Goal."
# After:
"Môi trường 8-Puzzle chuẩn kèm heuristic h(n) ước lượng khoảng cách tới đích."

# Before:
"...học trực tuyến hoặc action không xác định."
# After:
"...học trực tuyến hoặc hành động không xác định."
```

#### 10. Sửa "successor" → "nút kế" — line 132 (trace-table.tsx, handled in Phase 2)

Note: "successor" appears in trace-table.tsx not core.py.

#### 11. Rút gọn "No Observation" translation — line 48

```python
# Before:
"No Observation Search": {"...", "vi": "Tìm kiếm trạng thái niềm tin (No Observation)", ...},
# After:
"No Observation Search": {"...", "vi": "Tìm kiếm không quan sát", ...},
```

#### 12. Sửa "chance node" → "nút cơ hội" — line 373

```python
# Before: "...tại chance node."
# After:  "...tại nút cơ hội."
```

## Success Criteria

- [ ] Tất cả 12 mục trên được sửa trong `api/eight_puzzle_detective_core.py`
- [ ] Chạy `python -m pytest api/tests/ -v` — tất cả test pass (không regression)
- [ ] Các test assertion tham chiếu đến VN string (nếu có) được cập nhật theo

## Risk Assessment

- **Risk thấp**: Chỉ thay đổi string, không đụng logic
- **Mitigation**: Chạy full test suite sau mỗi batch sửa
