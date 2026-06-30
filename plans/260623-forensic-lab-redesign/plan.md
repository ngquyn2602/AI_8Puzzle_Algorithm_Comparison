---
title: "8-Puzzle Detective Lab — Forensic Redesign"
description: "Redesign web UI theo direction 'Case File Forensic Lab': manila folder hero, magnetic board background, red string trace signature, serif/sans/mono typography trio."
status: in_progress
priority: P1
branch: ""
tags: [frontend, redesign, ui-ux, forensic]
blockedBy: []
blocks: []
created: "2026-06-23T00:00:00.000Z"
createdBy: "ck:frontend-design"
source: skill
---

# 8-Puzzle Detective Lab — Forensic Redesign

## Overview

Nâng cấp UI/UX từ dark dashboard generic sang **Case File Forensic Lab** — desktop of a forensic AI analyst. Giữ nguyên backend + functionality, chỉ đổi frontend presentation layer.

## Differentiation Boundary

- Same: React + Vite + Tailwind v4, API contract, component responsibilities.
- Different: visual identity, typography, color system, signature element (red string board), motion.

## Design Direction

**Concept:** Case file forensic lab — manila folder + magnetic board + red string.

**Dials:** `DESIGN_VARIANCE=8`, `MOTION_INTENSITY=5`, `VISUAL_DENSITY=6`.

### Color tokens
- `--paper: #f4ead5` — manila folder base
- `--paper-dark: #e8dcc0` — folder edge
- `--ink: #1a1410` — stamp ink, warm near-black
- `--ink-soft: #4a3f33` — body text on paper
- `--evidence: #b8442e` — red stamp / red string
- `--clue: #c9851b` — amber highlighter
- `--slate: #2d3a3d` — detective board background
- `--slate-soft: #3d4a4d` — board panel

### Typography
- Display: `Newsreader` (serif, editorial)
- Body: `Be Vietnam Pro` (sans, Vietnamese-native)
- Data: `JetBrains Mono` (g/h/f, runtime, metrics)

### Signature
Red string board — trace story replay render dạng cork board với push-pin + SVG red string nối các node. Trope detective nhưng thực thi thật.

### Motion
Staggered page load: folder mở (rotateX), pins drop (translateY + scale), red string vẽ (stroke-dashoffset). Sau đó tĩnh.

### Copy voice
- EN labels: "Case file", "Trace evidence", "Heuristic breakdown", "Algorithm autopsy", "Verdict".
- VN body: mô tả, giải thích, empty states, errors.
- Sentence case, active verbs.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| A | [Foundation: tokens + fonts + global CSS](./phase-01-foundation.md) | In Progress |
| B | [Case folder hero + puzzle board](./phase-02-case-folder.md) | Pending |
| C | [Trace table + red string signature](./phase-03-red-string.md) | Pending |
| D | [Prediction + quiz + benchmark restyle](./phase-04-panels.md) | Pending |
| E | [App shell restructure + motion](./phase-05-shell-motion.md) | Pending |

## Dependencies

- No backend changes.
- Each phase must pass `npm --prefix web run build` before next phase starts.
- Phase B-E depend on Phase A tokens.

## Acceptance Criteria

- [ ] No Inter/Roboto/Arial — Newsreader + Be Vietnam Pro + JetBrains Mono loaded.
- [ ] No `shadow-glow` neon outer glow — replaced with tinted inner shadows.
- [ ] No `bg-white/10` uniform surfaces — paper + slate surface system.
- [ ] Red string board signature element renders trace as connected pins.
- [ ] Staggered page-load motion works, then static.
- [ ] EN labels + VN body consistent across all panels.
- [ ] Mobile: trace table không horizontal-scroll trong container (stack hoặc sticky).
- [ ] Focus ring visible on all interactive elements.
- [ ] Build pass, no TypeScript errors.

## Validation Log

### Validation Session 1 - 2026-06-23

#### User Decisions
- Direction: Case File Forensic Lab
- Scope: Full redesign (5 phases)
- Language: EN labels + VN body
