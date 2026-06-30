---
phase: 5
title: "Final verification and polish"
status: pending
priority: P3
dependencies: ["phase-01-fix-vietnamese-terminology-in-core-module", "phase-02-fix-vietnamese-terminology-in-frontend", "phase-03-fix-algorithm-logic-issues", "phase-04-add-cross-algorithm-path-diversity-tests"]
---

# Phase 5: Final verification and polish

## Overview

Tổng kiểm tra sau khi tất cả Phase 1-4 hoàn thành. Chạy toàn bộ test suite, typecheck, build, và manual verification để đảm bảo không có regression.

## Verification Steps

### 1. Backend — Full test suite

```bash
cd api
python -m pytest tests/ -v --tb=long
```

Expected: 21 tests (15 cũ + 6 mới từ Phase 4), tất cả PASS.

### 2. Backend — Manual algorithm run verification

Chạy thủ công từng nhóm thuật toán qua CLI:

```bash
# Uninformed — phải ra đường đi khác nhau
python api/cli.py --start 1,2,3,4,0,6,7,5,8 --algorithm BFS --trace-limit 5
python api/cli.py --start 1,2,3,4,0,6,7,5,8 --algorithm DFS --trace-limit 5
python api/cli.py --start 1,2,3,4,0,6,7,5,8 --algorithm UCS --trace-limit 5
python api/cli.py --start 1,2,3,4,0,6,7,5,8 --algorithm IDS --trace-limit 5

# Informed
python api/cli.py --start 1,2,3,4,0,6,7,5,8 --algorithm Greedy --trace-limit 5
python api/cli.py --start 1,2,3,4,0,6,7,5,8 --algorithm A* --trace-limit 5
python api/cli.py --start 1,2,3,4,0,6,7,5,8 --algorithm IDA* --trace-limit 5

# Local — Simple vs Steepest phải KHÁC NHAU
python api/cli.py --start 1,2,3,4,8,5,7,6,0 --algorithm "Simple Hill Climbing" --trace-limit 5
python api/cli.py --start 1,2,3,4,8,5,7,6,0 --algorithm "Steepest-Ascent Hill Climbing" --trace-limit 5

# Adversarial — phải dùng Caro, không phải 8-puzzle
python api/cli.py --start 1,2,3,4,5,6,7,8,0 --algorithm Minimax --trace-limit 5
python api/cli.py --start 1,2,3,4,5,6,7,8,0 --algorithm "Alpha-Beta Pruning" --trace-limit 5
python api/cli.py --start 1,2,3,4,5,6,7,8,0 --algorithm Expectimax --trace-limit 5
```

Verify mỗi trace row có `board_kind: "caro"` cho adversarial.

### 3. Frontend — Typecheck + Build

```bash
cd web
npx tsc --noEmit
npx vite build
```

Expected: zero errors.

### 4. API endpoint smoke test

```bash
# Start API server in background
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
sleep 2

# Test key endpoints
curl -s http://localhost:8000/healthz | python -m json.tool
curl -s http://localhost:8000/api/cases | python -m json.tool
curl -s http://localhost:8000/api/algorithm-groups | python -m json.tool
curl -s -X POST http://localhost:8000/api/run -H "Content-Type: application/json" -d '{"start":[1,2,3,4,5,6,0,7,8],"algorithm":"minimax"}' | python -m json.tool
curl -s -X POST http://localhost:8000/api/benchmark -H "Content-Type: application/json" -d '{"start":[1,2,3,4,5,6,0,7,8]}' | python -m json.tool

# Kill server
kill %1
```

Verify:
- `/api/cases` trả về 6 cases (bao gồm case-caro-adversarial)
- `/api/algorithm-groups` không còn CSP Definition trong danh sách thuật toán chạy được (nếu đã xóa)
- `/api/run` với minimax trả về `board_kind: "caro"` trong trace_rows
- `/api/benchmark` trả về 14 rows

### 5. Vietnamese terminology audit checklist

Đọc lại toàn bộ các string đã sửa trong Phase 1-2:

- [ ] "Tìm kiếm tia cục bộ" (không còn "chùm")
- [ ] "Cực tiểu cục bộ" (không còn "Ngõ cụt")
- [ ] "độ sâu" (không còn "depth" trong explain_selection)
- [ ] "láng giềng" (không còn "neighbor")
- [ ] "hành động" (không còn "action" trong context dịch)
- [ ] "xung đột" (không còn "conflict")
- [ ] "cây trò chơi" (không còn "cây game")
- [ ] "kết thúc" (không còn "terminal")
- [ ] "đích" (không còn "Goal" trong UI)
- [ ] "nút kế" (không còn "successor")
- [ ] "nút cơ hội" (không còn "chance node")
- [ ] "Tìm kiếm không quan sát" (thay cho bản dịch dài dòng)
- [ ] "Trạng thái bắt đầu" / "Trạng thái đích" (thay "Start state" / "GOAL state")
- [ ] "Câu hỏi kiểm tra kiến thức" (thay "kiểm tra hiểu nhầm")
- [ ] "Tải báo cáo Markdown" (thay "Tải Markdown report")

## Success Criteria

- [ ] 21 tests pass (không regression)
- [ ] TypeScript typecheck: zero errors
- [ ] Vite build: success
- [ ] API smoke test: tất cả endpoint trả về đúng format
- [ ] Manual algorithm verification: mỗi thuật toán sinh trace/đường đi khác nhau
- [ ] Vietnamese terminology: 15/15 checklist items pass
- [ ] Không còn English-only label trong UI chính
- [ ] CSP Definition không còn trong dropdown thuật toán

## Risk Assessment

- **Risk thấp**: Chỉ verification, không code change
- **Mitigation**: Nếu phát hiện regression, quay lại phase tương ứng để sửa
