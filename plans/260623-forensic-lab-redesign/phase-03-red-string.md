---
phase: 3
title: "Trace table + red string signature"
status: pending
priority: P1
effort: "0.75d"
dependencies: [2]
---

# Phase 3: Trace table + red string signature

## Overview

Trace story replay thành signature element: red string board. Mỗi node là pin trên slate board, nối bằng SVG path `stroke=evidence`. Trace table đồng bộ restyle.

## Requirements

- Functional: render trace rows dạng pins + red string; table vẫn show data g/h/f.
- Non-functional: SVG path animate `stroke-dashoffset` trên load.

## Related Code Files

- Create: `web/src/components/red-string-board.tsx` — SVG canvas với pins + string.
- Modify: `web/src/components/trace-table.tsx` — monospace, tabular-nums, sticky header, hover row highlight.
- Modify: `web/src/App.tsx` — replace TraceTable panel với grid: RedStringBoard (left) + TraceTable (right).

## Implementation Steps

1. Create `red-string-board.tsx`:
   - SVG viewBox `0 0 800 300`.
   - Mỗi trace row (max 8) là pin ở position `(x, y)` với `x = step * 90 + 40`, `y` alternating 80/200.
   - Pin: circle r=8 `fill=paper` `stroke=evidence strokeWidth=2` + push-pin SVG on top.
   - String: `<path d="M ... C ..."` `stroke=evidence strokeWidth=1.5 fill=none opacity=0.7` với bezier giữa các pin.
   - Label dưới pin: step number (mono) + `f={n}`.
   - Animation: `stroke-dasharray` + `stroke-dashoffset` animate từ full → 0 trong 1.2s với stagger.
2. Restyle `trace-table.tsx`:
   - Header: `bg-slate-soft text-paper text-xs uppercase tracking-wider sticky top-0`.
   - Body: `font-mono tabular-nums text-paper-dark`.
   - Hover row: `bg-evidence/10`.
   - Container: `max-h-[400px] overflow-y-auto` thay vì `min-w-[720px]`.
3. Update `App.tsx`: grid `lg:grid-cols-[1fr_1fr]` cho red string + table.
4. Verify build.

## Validation

- SVG render pins + string.
- Table dùng mono + tabular-nums.
- Không horizontal scroll trên mobile (table trong scroll container dọc).

## Success Criteria

- [ ] Red string board render ≤ 8 pins.
- [ ] SVG path animate stroke-dashoffset.
- [ ] Table sticky header + scroll-y.
- [ ] Build pass.

## Risk Assessment

- Risk: SVG path layout tràn viewBox. Mitigation: scale step theo số rows.
- Risk: animation lag. Mitigation: dùng CSS animation, không JS.
