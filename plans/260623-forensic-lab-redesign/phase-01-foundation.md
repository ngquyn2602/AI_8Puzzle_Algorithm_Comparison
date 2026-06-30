---
phase: 1
title: "Foundation: tokens + fonts + global CSS"
status: in_progress
priority: P1
effort: "0.5d"
dependencies: []
---

# Phase 1: Foundation

## Overview

Đặt foundation: Google Fonts, color tokens, surface system, focus ring, custom select styling, grain noise overlay. Không động đến component logic.

## Requirements

- Functional: load 3 fonts (Newsreader, Be Vietnam Pro, JetBrains Mono), expose CSS tokens, replace `shadow-glow` với tinted shadow system.
- Non-functional: không phá build, không đổi API contract.

## Related Code Files

- Modify: `web/index.html` — add `<link>` Google Fonts, meta description, og tags.
- Modify: `web/src/styles.css` — new `@theme` tokens, grain overlay, focus ring, base typography.

## Implementation Steps

1. Update `web/index.html`:
   - Add `<link rel="preconnect">` to fonts.googleapis.com + fonts.gstatic.com.
   - Load Newsreader (400, 500, 600, italic), Be Vietnam Pro (400, 500, 600, 700), JetBrains Mono (400, 500, 700).
   - Add `<meta name="description">`, `<meta property="og:title">`, `<meta property="og:description">`, `<meta name="theme-color">`.
   - Update `<title>` thành "8-Puzzle Detective Lab — Case File".
2. Update `web/src/styles.css`:
   - Replace `@theme` block với forensic tokens (`--color-paper`, `--color-paper-dark`, `--color-ink`, `--color-ink-soft`, `--color-evidence`, `--color-clue`, `--color-slate`, `--color-slate-soft`, `--shadow-pin`, `--shadow-folder`).
   - Add `--font-display: 'Newsreader', serif`, `--font-body: 'Be Vietnam Pro', sans-serif`, `--font-mono: 'JetBrains Mono', monospace` vào `@theme`.
   - Replace `:root` font-family với `--font-body`.
   - Replace `.bg-lab` với `.bg-board`: slate gradient + SVG noise overlay (data URI).
   - Add `:focus-visible` global style: 2px solid `--color-evidence`, offset 2px.
   - Add `.surface-paper` và `.surface-board` utility classes.
   - Add `body { font-family: var(--font-body); }` + `text-wrap: balance` cho headings.
3. Verify build.

## Validation

- `npm --prefix web run build` pass.
- Built CSS chứa `--color-paper`, `--color-evidence`, `Newsreader`, `JetBrains Mono`.
- `index.html` có preconnect + 3 font families.

## Success Criteria

- [ ] 3 fonts loaded via Google Fonts.
- [ ] 8 color tokens defined.
- [ ] Focus ring global.
- [ ] `.bg-board` có noise overlay.
- [ ] Build pass.

## Risk Assessment

- Risk: Google Fonts chậm ở VN. Mitigation: preconnect + display=swap.
- Risk: noise overlay data URI làm CSS lớn. Mitigation: giữ SVG noise < 1KB.
