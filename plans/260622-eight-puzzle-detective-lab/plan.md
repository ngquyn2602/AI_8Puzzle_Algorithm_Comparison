---
title: "8-Puzzle Detective Lab"
description: "Plan for a differentiated 8-Puzzle AI learning project with detective-style tracing, prediction, diagnosis, and coursework-grade knowledge coverage."
status: pending
priority: P2
branch: ""
tags: [ai, eight-puzzle, search, coursework, plan]
blockedBy: []
blocks: []
created: "2026-06-22T15:10:17.577Z"
createdBy: "ck:plan"
source: skill
---

# 8-Puzzle Detective Lab

## Overview

Build a new 8-Puzzle learning project that keeps the same AI knowledge depth as the reference project, but has a distinct identity: **Detective Lab**. Instead of only running algorithms and showing trace tables, the app teaches users to investigate why an algorithm selected a node, predict the next expansion, diagnose wrong intuition, and compare search behavior through guided cases.

Reference analyzed: `D:\Trí tuệ nhân tạo AI lỏ`.

## Differentiation Boundary

- Same core domain: 8-Puzzle, state space search, `g(n)`, `h(n)`, `f(n)`, frontier, reached, solvability, certificates.
- Different product angle: interactive detective missions, next-node prediction, trace diagnosis, algorithm mistake replay, and quiz-style learning checkpoints.
- Keep only academically valid claims: standard 8-Puzzle solvers stay separate from educational demos for complex environments, CSP, and adversarial/stochastic search.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Research reference scope](./phase-01-research-reference-scope.md) | Pending |
| 2 | [Design differentiated AI lab](./phase-02-design-differentiated-ai-lab.md) | Pending |
| 3 | [Plan implementation and validation](./phase-03-plan-implementation-and-validation.md) | Pending |

## Dependencies

- No unfinished overlapping local plans found during initial scan.
- User validation selected a polished web application, not Streamlit-only. Plan should use a separate web frontend plus Python-backed AI core/API so the UI can look more distinctive than the reference.

## Acceptance Criteria

- New project is recognizably different from the reference while still centered on 8-Puzzle.
- Covers the same AI knowledge scope: uninformed, informed, local, complex environment demos, CSP demos, adversarial/stochastic demos.
- Includes trace, certificate, heuristic inspector, benchmark, full report export, tests, and demo script.
- Provides a polished web UI rather than a Streamlit-only clone.
- Avoids presenting non-standard educational demos as canonical 8-Puzzle solvers.

## Validation Log

### Validation Session 1 - 2026-06-22

#### Verification Results
- **Tier:** Standard
- **Claims checked:** 12
- **Verified:** 8 | **Failed:** 1 | **Unverified:** 3
- **Failed claim fixed:** Python file names used hyphens, which are poor import targets. Updated planned files to snake_case under `api/`.
- **Unverified claims accepted as future implementation decisions:** exact frontend framework, exact export libraries, and exact API contract shape.

#### User Decisions
- Keep full 6 academic algorithm groups.
- Build a polished web application, not Streamlit-only.
- Include full export pack: Markdown, CSV, HTML, DOCX, PDF.
- Use snake_case for Python files.

#### Whole-Plan Consistency Sweep
- Files reread: `plan.md`, `phase-01-research-reference-scope.md`, `phase-02-design-differentiated-ai-lab.md`, `phase-03-plan-implementation-and-validation.md`
- Decision deltas checked: 4
- Reconciled stale references: Streamlit-only assumption, hyphenated Python file names, Markdown-only export scope, single-service architecture assumption
- Unresolved contradictions: 0
