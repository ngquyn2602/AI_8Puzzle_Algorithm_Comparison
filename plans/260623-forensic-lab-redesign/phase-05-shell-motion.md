---
phase: 5
title: "App shell restructure + motion"
status: pending
priority: P1
effort: "0.5d"
dependencies: [4]
---

# Phase 5: App shell restructure + motion

## Overview

Restructure App.tsx shell: semantic HTML, asymmetric grid, staggered page-load motion, custom select, final polish.

## Requirements

- Functional: layout 12-col asymmetric, semantic `aside`/`main`/`section`, custom select thay native.
- Non-functional: staggered load animation 1.2s, sau đó tĩnh.

## Related Code Files

- Create: `web/src/components/custom-select.tsx` — styled select.
- Modify: `web/src/App.tsx` — restructure shell, motion classes.
- Modify: `web/src/styles.css` — keyframes `folder-open`, `pin-drop`, `string-draw`, `stagger`.

## Implementation Steps

1. Create `custom-select.tsx`:
   - Button trigger + dropdown panel.
   - Option list paper style, hover `bg-evidence/10`.
   - Keyboard nav: Arrow/Enter/Escape.
   - Focus ring visible.
2. Restyle `App.tsx` shell:
   - `<main class="bg-board min-h-[100dvh]">` (thay `min-h-screen`).
   - Grid `lg:grid-cols-[4fr_8fr]` (asymmetric 12-col).
   - `<aside>` case file list: stacked tabs dạng folder tabs, không còn box.
   - `<main>` content: sections semantic.
   - Replace native `<select>` với `<CustomSelect>`.
3. Motion keyframes trong `styles.css`:
   - `folder-open`: `from { transform: rotateX(-15deg); opacity: 0 }` `to { rotateX(0); opacity: 1 }`.
   - `pin-drop`: `from { transform: translateY(-20px) scale(0.8); opacity: 0 }`.
   - `string-draw`: `stroke-dashoffset` animate.
   - Stagger utilities: `.stagger-1 { animation-delay: 0.1s }` ... `.stagger-5 { 0.5s }`.
4. Apply staggered classes cho hero, boards, panels.
5. Final polish:
   - Remove unused CSS classes.
   - Verify no `shadow-glow` còn sót.
   - Verify no `bg-white/10` còn sót.
   - Verify no Inter/Roboto reference.
6. Verify build + manual smoke test.

## Validation

- Layout asymmetric, không centered hero.
- Custom select thay native.
- Staggered load animation chạy 1 lần.
- `min-h-[100dvh]` không `h-screen`.
- No AI-slop patterns còn sót.

## Success Criteria

- [ ] Semantic HTML (`aside`, `main`, `section`, `article`).
- [ ] Custom select keyboard-nav.
- [ ] Staggered animation 1.2s.
- [ ] No `shadow-glow`, `bg-white/10`, `h-screen`, Inter còn sót.
- [ ] Build pass + manual smoke test.

## Risk Assessment

- Risk: custom select phá accessibility. Mitigation: test keyboard nav + ARIA.
- Risk: animation lag trên mobile. Mitigation: `prefers-reduced-motion` disable animation.
