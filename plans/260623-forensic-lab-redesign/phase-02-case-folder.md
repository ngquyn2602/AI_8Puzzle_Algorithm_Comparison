---
phase: 2
title: "Case folder hero + puzzle board restyle"
status: pending
priority: P1
effort: "0.5d"
dependencies: [1]
---

# Phase 2: Case folder hero + puzzle board

## Overview

Hero thành manila folder mở với stamp "CASE FILE #08-A", tab folder màu evidence. Puzzle board restyle thành paper texture với tab stamp.

## Requirements

- Functional: hero hiển thị case title, case id, lesson; puzzle board hiển thị start/goal side-by-side trong folder.
- Non-functional: folder phải nhìn như paper thật (texture, shadow folder edge).

## Related Code Files

- Create: `web/src/components/case-folder.tsx` — manila folder hero.
- Create: `web/src/components/push-pin.tsx` — SVG push pin decor.
- Modify: `web/src/components/puzzle-board.tsx` — paper texture, tab stamp, monospace numbers.
- Modify: `web/src/App.tsx` — replace hero block với `<CaseFolder>`.

## Implementation Steps

1. Create `push-pin.tsx`: SVG push pin (phosphor-style), props `color` + `className`.
2. Create `case-folder.tsx`:
   - Outer: `.surface-paper` + `shadow-folder` + tab góc trên trái.
   - Tab: `bg-evidence` text "CASE FILE #08-A".
   - Inside: grid 2 cột (start/goal board), case title (Newsreader), lesson (Be Vietnam Pro italic).
   - Stamp góc phải: rotated `border-2 border-evidence text-evidence` "CLASSIFIED".
3. Restyle `puzzle-board.tsx`:
   - Board: `bg-paper-dark` + inner shadow.
   - Tiles: `bg-paper` + `text-ink` + font-mono cho numbers.
   - Blank tile: dashed border.
   - Label: uppercase tracking + `text-ink-soft`.
4. Update `App.tsx`: replace hero `<div>` block với `<CaseFolder case={activeCase} algorithm={algorithm} />`.
5. Verify build.

## Validation

- Hero render folder shape với tab.
- Puzzle board dùng paper tokens, không còn amber.
- Numbers dùng JetBrains Mono.

## Success Criteria

- [ ] Folder hero có tab + stamp.
- [ ] Puzzle board paper texture.
- [ ] Push-pin SVG render.
- [ ] Build pass.

## Risk Assessment

- Risk: folder shape quá phức tạp. Mitigation: dùng CSS clip-path hoặc pseudo-element đơn giản.
