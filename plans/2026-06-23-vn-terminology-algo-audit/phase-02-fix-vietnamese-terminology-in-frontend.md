---
phase: 2
title: "Fix Vietnamese terminology in frontend"
status: pending
priority: P2
dependencies: []
---

# Phase 2: Fix Vietnamese terminology in frontend

## Overview

Sửa các label Tiếng Anh còn sót trong frontend (App.tsx, case-folder.tsx, trace-table.tsx) khi toàn bộ UI đã là Tiếng Việt. Đồng bộ với các sửa từ Phase 1.

## Changes

### 1. `web/src/components/case-folder.tsx` — lines 75-76

```tsx
// Before:
<PuzzleBoard state={caseItem!.start} label="Start state" />
<PuzzleBoard state={caseItem!.goal} label="GOAL state" />

// After:
<PuzzleBoard state={caseItem!.start} label="Trạng thái bắt đầu" />
<PuzzleBoard state={caseItem!.goal} label="Trạng thái đích" />
```

### 2. `web/src/App.tsx` — line 219

```tsx
// Before:
<th ...>Vị trí Goal</th>
// After:
<th ...>Vị trí đích</th>
```

### 3. `web/src/App.tsx` — line 258

```tsx
// Before:
<Panel title="Câu hỏi kiểm tra hiểu nhầm">
// After:
<Panel title="Câu hỏi kiểm tra kiến thức">
```

Lý do: "hiểu nhầm" (misunderstanding) gây confused — đây là quiz kiểm tra kiến thức, không phải quiz về hiểu nhầm. "Kiểm tra kiến thức" rõ ràng hơn.

### 4. `web/src/components/trace-table.tsx` — line 132

```tsx
// Before:
<p ...>Frontier trống — Node này không sinh successor.</p>
// After:
<p ...>Frontier trống — Node này không sinh nút kế.</p>
```

### 5. `web/src/App.tsx` — line 265

```tsx
// Before:
<button ...>Tải Markdown report</button>
// After:
<button ...>Tải báo cáo Markdown</button>
```

### 6. `web/src/index.html` — line 6 (meta description)

```html
<!-- Before: -->
<meta name="description" content="8-Puzzle Detective Lab -- điều tra vì sao thuật toán chọn node kế tiếp, soi frontier, kiểm tra heuristic evidence, benchmark và xuất full report pack." />
<!-- After: -->
<meta name="description" content="8-Puzzle Detective Lab — điều tra vì sao thuật toán chọn nút kế tiếp, soi Frontier, kiểm tra bằng chứng heuristic, đối chiếu thuật toán và xuất báo cáo." />
```

## Success Criteria

- [ ] Không còn English-only label nào trong UI chính
- [ ] Các thuật ngữ kỹ thuật được giữ Tiếng Anh có chủ đích: Frontier, Heuristic, Node, Utility, A*, BFS, DFS, PEAS, Trace, Benchmark
- [ ] `npx tsc --noEmit` pass
- [ ] `npx vite build` pass
- [ ] UI inspection: tất cả panel title, label, button text là Tiếng Việt

## Risk Assessment

- **Risk thấp**: Chỉ thay đổi string hiển thị, không đụng logic
- **Mitigation**: TypeScript typecheck + Vite build sau mỗi batch
