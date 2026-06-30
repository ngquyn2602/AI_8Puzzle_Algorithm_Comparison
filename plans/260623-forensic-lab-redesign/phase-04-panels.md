---
phase: 4
title: "Prediction + quiz + benchmark restyle"
status: pending
priority: P1
effort: "0.5d"
dependencies: [3]
---

# Phase 4: Prediction + quiz + benchmark restyle

## Overview

Các panel còn lại restyle theo forensic theme: prediction thành "evidence lockup", quiz thành "interrogation card", benchmark thành "lineup comparison".

## Requirements

- Functional: giữ nguyên logic, chỉ đổi visual.
- Non-functional: tất cả panel dùng surface system nhất quán.

## Related Code Files

- Modify: `web/src/components/prediction-lab.tsx` — evidence lockup pattern.
- Modify: `web/src/components/quiz-panel.tsx` — interrogation card pattern.
- Modify: `web/src/App.tsx` — benchmark cards restyle, export pack restyle.

## Implementation Steps

1. Restyle `prediction-lab.tsx`:
   - Container: `.surface-paper` với label "EVIDENCE LOCKUP".
   - Candidate buttons: polaroid-style — `bg-paper` + `shadow-pin` + slight rotate alternating.
   - Selected: ring `--evidence` thay vì amber.
   - Result: "VERDICT: CORRECT/WRONG" stamp style.
2. Restyle `quiz-panel.tsx`:
   - Container: `.surface-paper` với label "INTERROGATION".
   - Questions: numbered `Q1, Q2...` mono.
   - Options: `bg-paper-dark` + hover `bg-evidence/10`.
   - Reveal: stamp "ANSWER" rotated.
3. Restyle benchmark cards trong `App.tsx`:
   - Cards thành "lineup" row — `divide-x divide-ink/20` thay vì grid cards.
   - Mỗi row: algorithm name (display font) + metrics (mono) inline.
   - Found/optimal: stamp badge nhỏ.
4. Restyle export pack panel:
   - Button: `bg-ink text-paper` thay vì amber border.
   - List formats: mono inline tags.
5. Restyle algorithm autopsy + heuristic evidence:
   - Autopsy: `border-l-4 border-evidence pl-4` như stamped note.
   - Heuristic evidence: render dạng table nhỏ thay vì `<pre>JSON</pre>`.
6. Verify build.

## Validation

- Tất cả panel dùng paper/slate tokens, không amber.
- No `<pre>{JSON.stringify}</pre>` còn sót.
- Stamps render rotated.

## Success Criteria

- [ ] Prediction lab polaroid candidates.
- [ ] Quiz interrogation card style.
- [ ] Benchmark lineup row layout.
- [ ] Heuristic evidence table (không JSON pre).
- [ ] Build pass.

## Risk Assessment

- Risk: polaroid rotate phá layout. Mitigation: rotate `±2deg` only.
