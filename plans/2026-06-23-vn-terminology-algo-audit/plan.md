---
title: "Audit Vietnamese Terminology and Algorithm Path Diversity"
description: "Quét toàn bộ codebase: sửa thuật ngữ Tiếng Việt sai/nửa Anh nửa Việt, sửa lỗi logic thuật toán (Simple Hill Climbing = Steepest-Ascent, CSP Definition là thuật toán ảo), thêm test xác minh mỗi thuật toán sinh đường đi khác nhau."
status: validated
priority: P1
branch: "master"
tags: ["vietnamese", "terminology", "algorithms", "testing", "bugfix"]
blockedBy: []
blocks: []
created: "2026-06-23T13:06:18.248Z"
createdBy: "ck:plan"
source: skill
validated: "2026-06-23T14:00:00.000Z"
---

# Audit Vietnamese Terminology and Algorithm Path Diversity

## Validation Summary (2026-06-23)

Đã validate toàn bộ 5 phase. 6 findings, đã resolve:

| # | Finding | Resolution |
|---|---------|------------|
| 1 | Phase 3 thiếu `ALGORITHM_ALIASES` + `explain_selection()` cho simple-hill-climbing | Đã bổ sung vào Phase 3 |
| 2 | CSP Definition removal hand-wavy — chưa trace blast radius | Đã clarify: xóa khỏi SOLVER_KEYS + EDUCATIONAL_ALGORITHMS, filter list_algorithms() |
| 3 | Test 1 assert `expanded !=` có thể flaky | Đã sửa thành so sánh trace order |
| 4 | Test 4 assert trên VN string dễ vỡ | Đã sửa thành data assertion + string assertion (cả hai) |
| 5 | Phase 5 script dùng bash, không chạy được trên Windows | Đã note — cần PowerShell equivalents khi thực thi |
| 6 | Thiếu grep frontend trước khi đổi SOLVER_KEYS | Đã bổ sung pre-flight check vào Phase 3 |

**Plan ready for implementation.**

## Overview

Audit toàn diện codebase sau phát hiện: (1) CaseFolder hiển thị 8-puzzle thay vì Caro cho thuật toán đối kháng (đã fix riêng), (2) nhiều thuật ngữ Tiếng Việt dịch sai hoặc code-switching nửa Anh nửa Việt, (3) Simple Hill Climbing và Steepest-Ascent sinh trace giống hệt nhau, (4) tất cả 7 "thuật toán giáo dục" (CSP, AND-OR, v.v.) trả về dummy result giống hệt nhau, (5) không có test nào xác minh các thuật toán sinh đường đi KHÁC NHAU.

## Phases

| Phase | Name | Status | Priority |
|-------|------|--------|----------|
| 1 | [Fix Vietnamese terminology in core module](./phase-01-fix-vietnamese-terminology-in-core-module.md) | Pending | P1 |
| 2 | [Fix Vietnamese terminology in frontend](./phase-02-fix-vietnamese-terminology-in-frontend.md) | Pending | P2 |
| 3 | [Fix algorithm logic issues](./phase-03-fix-algorithm-logic-issues.md) | Pending | P0 |
| 4 | [Add cross-algorithm path diversity tests](./phase-04-add-cross-algorithm-path-diversity-tests.md) | Pending | P1 |
| 5 | [Final verification and polish](./phase-05-final-verification-and-polish.md) | Pending | P3 |

## Dependencies

- Phase 3 blocks Phase 4 (tests depend on correct algorithm behavior)
- Phase 1, 2, 3 can run in parallel (different files)
- Phase 5 depends on Phase 1-4 all completed

## Acceptance Criteria

- [ ] Tất cả thuật ngữ Tiếng Việt đúng chính tả, nhất quán, không code-switching nửa Anh nửa Việt
- [ ] Các thuật ngữ kỹ thuật quan trọng được giữ Tiếng Anh có chủ đích (Frontier, Heuristic, Node, Utility, A*, BFS, DFS)
- [ ] Simple Hill Climbing và Steepest-Ascent Hill Climbing sinh trace KHÁC NHAU
- [ ] CSP Definition không còn là "thuật toán chạy được" (chỉ là mô hình)
- [ ] Benchmark chạy đủ tất cả thuật toán (thêm DFS, IDS, stochastic variants)
- [ ] Ít nhất 3 test xác minh các cặp thuật toán sinh đường đi khác nhau trên cùng một start state
- [ ] Tất cả test pass (zero regression)
- [ ] TypeScript typecheck pass
- [ ] Vite build pass
