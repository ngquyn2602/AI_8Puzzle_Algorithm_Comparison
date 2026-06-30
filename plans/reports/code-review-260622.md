# Code Review Report — 8-Puzzle Detective Lab

**Date**: 2026-06-22
**Reviewer**: code-reviewer (staff engineer)
**Scope**: Full project (initial commit, no prior history)

---

### Scope
- Files reviewed: 12 (6 source, 2 test, 4 config)
  - `api/eight_puzzle_detective_core.py` (343 lines) — search core, heuristics, algorithms, trace, benchmark
  - `api/main.py` (211 lines) — FastAPI endpoints, export pack
  - `api/tests/test_detective_core.py` (64 lines) — 8 tests
  - `web/src/App.tsx` (141 lines) — main UI
  - `web/src/api-client.ts` (28 lines) — API client
  - `web/src/components/puzzle-board.tsx` (21 lines)
  - `web/src/components/trace-table.tsx` (34 lines)
  - `web/src/types.ts` (60 lines) — TypeScript types
  - `web/package.json`, `web/tsconfig.json`, `web/vite.config.ts`, `web/tailwind.config.cjs`, `web/postcss.config.cjs`, `web/src/styles.css`
- LOC: 778 source + 64 test + ~90 config = ~932 total
- Focus: Pre-commit, pre-initial-commit review of greenfield academic AI lab app
- Scout findings: Tailwind v4 config gap, IDA* not IDA*, PDF xref missing, no Docker/CI, DLS frontier trace always empty

### Overall Assessment

The detective-lab metaphor is well-executed and the educational focus is clear. The core solver algorithms (BFS, DFS, UCS, A*, IDS with DLS) work correctly. Tests pass (8/8). TypeScript compiles clean. However, there are several structural issues that need attention before this goes beyond local dev. Three are critical: IDA* is a fake implementation (A* with a renamed label), the project has zero containerization/CI despite universal rules mandating it, and Tailwind v4's config paradigm gap means custom utilities (shadow-glow) won't render.

---

## Critical Issues

### 1. IDA* Is Fake — Calls Regular A* and Relabels

**File**: `api/eight_puzzle_detective_core.py`, lines 289–298

```python
def ida_star(start, goal, h_func, max_expansions):
    result = graph_search("astar", start, goal, h_func, max_expansions)
    result.algorithm = "ida"
    for row in result.trace_rows:
        row["algorithm"] = "ida"
        row["priority_rule"] = "iterative f-cost threshold"
    return result
```

Root cause: `ida_star()` simply delegates to `graph_search("astar", ...)` which is a single-pass A* with a closed set and a heap. It performs no iterative deepening, no f-cost threshold loop, and no repeated searches with increasing bounds. The trace data is fabricated (priority rule is always "iterative f-cost threshold" but the frontier was ordered by `f = g + h` in a single A* pass).

Impact: The `case-ida-threshold` detective case will display completely wrong educational information. Any student studying IDA* via this tool receives misinformation. The `complete_flag` and `optimal_flag` for IDA* are claimed as "Yes"/"Yes" (line 305, 309), but the underlying search is just A* — so the flags are technically correct for the result, but misattributed.

Fix: Either implement true IDA* (recursive depth-first search with f-cost bound, iteratively increasing bound after each failure), or remove IDA* from `STANDARD_ALGORITHMS` and `complete_flag`/`optimal_flag` and document it as excluded. Implementing true IDA* involves:
- Starting threshold = h(start)
- DLS-like recursive search that prunes nodes with f > threshold
- On exhaustion without goal, increase threshold and restart
- Accumulate trace across iterations (as done correctly in `ids()`)

The `ids()` function (lines 241–286) correctly implements iterative deepening DFS. `ida_star()` should follow an analogous pattern with f-cost thresholds instead of depth limits.

### 2. Zero Containerization — No Dockerfiles, No Compose

The project has no `Dockerfile` for `api/`, no `Dockerfile` for `web/`, and no `docker-compose.yml` at root. This violates the universal "Containerization — STRICT" rule in the user's CLAUDE.md, which mandates:

- Per-service Dockerfiles with multi-stage builds, non-root users, HEALTHCHECK
- `docker-compose.yml` at root
- Image publish to Docker Hub under `nguyenson1710/`

Impact: No consistent deployment path, no local container-based dev, no CI build targets. The app only works via manual `python -m uvicorn` + `npm run dev`.

Fix: Bootstrap from the `CampusCore` project patterns. At minimum:
```
api/Dockerfile        # Python 3.14, uvicorn, distroless
web/Dockerfile        # Node multi-stage, nginx or vite preview
docker-compose.yml    # api:8000 + web:5173 + networks
```

### 3. No CI/CD Pipelines

No `.github/workflows/` directory exists. Per bootstrap checklist (rule #17) and Dependabot (rule #29), the repo needs:
- `ci.yml` — build + test + lint + coverage
- `docker-publish.yml` — multi-arch push to Docker Hub
- `codeql.yml` — SAST
- `trivy.yml` — vulnerability scan
- `.github/dependabot.yml`

Impact: No automated quality gates, no automated Docker publishing, no vulnerability scanning.

### 4. No Git History — Uncommitted Work

`git log` reports "does not have any commits yet". All files are staged (from `git status`). No initial commit exists. This is not a review finding per se, but a process note: the review is being done on a pre-commit snapshot.

---

## High Priority

### 5. Tailwind CSS v4 Config Not Loaded — shadow-glow Won't Render

**Files**: `web/tailwind.config.cjs`, `web/src/styles.css`, `web/postcss.config.cjs`

The project uses Tailwind CSS v4 (`@tailwindcss/postcss` v4.3.1) but configures custom extensions via `tailwind.config.cjs` (v3-era JavaScript config):

```js
// tailwind.config.cjs
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      boxShadow: { glow: '0 0 35px rgba(245, 158, 11, 0.25)' },
      colors: { ink: '#101828', clue: '#f59e0b', lab: '#0f172a' }
    }
  }
};
```

In Tailwind v4, the PostCSS plugin (`@tailwindcss/postcss`) does **not** auto-discover `tailwind.config.js`. Configuration must be either:
- a `@config "./tailwind.config.cjs"` directive in `styles.css`, or
- migrated to CSS-native `@theme` blocks

Neither is present. `styles.css` has no `@config` or `@theme` directive.

Impact: The `shadow-glow` utility class used on the CTA button (App.tsx line 83), hero panel (line 61), and puzzle board (puzzle-board.tsx line 12) will **not** apply any box shadow. The amber glow effect central to the detective visual theme is invisible.

Note: `bg-lab` works because it is defined as a plain CSS class in `styles.css` (lines 16-21), not via Tailwind config. The `ink` and `clue` colors are defined but never used (grep-confirmed zero hits), so their absence is harmless.

Fix: Add `@config "./tailwind.config.cjs";` at the top of `web/src/styles.css`, OR migrate config to `@theme`:

```css
@import "tailwindcss";
@theme {
  --color-ink: #101828;
  --color-clue: #f59e0b;
  --color-lab: #0f172a;
  --shadow-glow: 0 0 35px rgba(245, 158, 11, 0.25);
}
```

### 6. PDF Export Missing Cross-Reference Table

**File**: `api/main.py`, lines 200–211

The `pdf_bytes()` function generates a minimal PDF but omits the `xref` (cross-reference) table. Every valid PDF requires:

```
%PDF-1.4
1 0 obj ... endobj
2 0 obj ... endobj
...
xref                    <-- MISSING
0 N
0000000000 65535 f
...
trailer << /Root 1 0 R >>
startxref               <-- MISSING
%%EOF
```

Without the `xref` table and `startxref` pointer, the PDF file is malformed. While some PDF readers (Chrome, Preview on macOS) may recover, others (Adobe Acrobat validation, PDF/A tools) will reject it.

Additional: Non-ASCII characters (e.g., Vietnamese in the default description text) are silently dropped by `.encode("latin-1", "ignore")`, producing garbled output.

Impact: The `detective-report.pdf` in the export pack may fail to open or display in some readers.

Fix: Generate a proper `xref` table with byte offsets, or use a library like `reportlab` / `fpdf2` instead of hand-rolling PDF. A minimal correct xref for 5 objects:

```python
xref_entries = ["0 6", "0000000000 65535 f "]
offset = len(header) + 1
for obj in objects:
    xref_entries.append(f"{offset:010} 00000 n ")
    offset += len(obj) + 1
xref_table = "xref\n" + "\n".join(xref_entries)
```

### 7. DLS Trace Shows Empty Frontier for All IDS Rows

**File**: `api/eight_puzzle_detective_core.py`, line 252

In `ids()`'s nested `dls()` function:
```python
trace.append(trace_row(expanded, "ids", node, [], reached, rule.format(limit=limit)))
```

The `frontier` positional argument is always `[]` (empty list). The `frontier` is populated on lines 258-265 AFTER the trace is recorded. This means all IDS trace rows show `frontier_before: []` regardless of actual frontier state.

Impact: The educational value of the trace — seeing which candidate nodes were considered — is lost for IDS. Students see the chosen node but not the alternatives it was selected from.

Fix: Move the trace append after frontier construction, or compute frontier candidate list before the trace:

```python
frontier_nodes: list[Node] = []
for action, child_state in legal_moves(state):
    if child_state in reached:
        continue
    ...
    frontier_nodes.append(child)
trace.append(trace_row(expanded, "ids", node, frontier_nodes, reached, rule.format(limit=limit)))
```

### 8. Dead Variable: `order` in `ids()`

**File**: `api/eight_puzzle_detective_core.py`, line 246

```python
order = count()
```

`order` is declared as `nonlocal` in `dls` but never referenced inside `dls`. The `count()` iterator is never consumed. It is a leftover from the `graph_search` pattern where the heap uses `(priority, h, order, node)` for tie-breaking. In DLS, there is no heap, so `order` has no purpose.

Impact: None on correctness, but indicates incomplete cleanup after refactoring.

---

## Medium Priority

### 9. API Client Object-Spread Antipattern

**File**: `web/src/api-client.ts`, lines 6–9

```ts
const response = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init
});
```

The `...init` spread appears after the explicit `headers:` property. If any future caller passes a `headers` key in `init`, the `...init` spread will **overwrite** the merged headers, discarding `Content-Type: application/json`.

This is dormant (no current caller passes `headers`), but the structural antipattern guarantees a bug when headers are needed.

Fix: Reorder — spread `init` first, then override `headers`:

```ts
const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers as Record<string, string> ?? {}) },
});
```

### 10. Unused V3 `tailwindcss` Package in Dependencies

**File**: `web/package.json`, line 24

Both `@tailwindcss/postcss` (v4) and `tailwindcss` are listed. In a Vite + PostCSS v4 setup, only `@tailwindcss/postcss` is needed. `tailwindcss` is the v3 CLI package; in v4 it is the main package but `@tailwindcss/postcss` is the PostCSS plugin. Having both can cause version mismatch confusion.

Currently both resolve to v4.3.1 (verified in lockfile), so no conflict in practice. But having `tailwindcss` as a direct dependency is misleading — it suggests CLI usage that does not exist in this project.

Fix: Remove `"tailwindcss": "latest"` from `dependencies` (keep `@tailwindcss/postcss` and `autoprefixer` in devDependencies).

### 11. `node.parent` Always `None` in DLS Nodes

**File**: `api/eight_puzzle_detective_core.py`, line 251

```python
node = Node(state, None, actions[-1] if actions else "Start", len(path) - 1, h_func(state, goal))
```

The `parent` parameter is hardcoded to `None`. While DLS reconstructs the path via recursive call chain (not parent pointers), setting `parent=None` means any downstream code that walks `node.parent` will get a broken chain. The `reconstruct()` function is not called on DLS nodes (path is built via recursion), so this is harmless for current code.

The `trace_row` records `action` from `actions[-1]`, which is correct. But the `preview()` helper called on the frontier (always empty, see issue #7) would access `n.g`, `n.h`, `n.f`, `n.action` — all of which are populated correctly.

Impact: Dormant. No current code depends on `parent` being set for DLS nodes.

### 12. `hasattr`-Level Robustness Gap in `explain_selection`

**File**: `api/eight_puzzle_detective_core.py`, lines 168–178

```python
def explain_selection(algorithm: str, node: Node) -> str:
    rules = {
        "bfs": "BFS inspects the oldest shallow frontier node.",
        ...
    }
    return f"{rules.get(algorithm, '...')} Selected {node.state}."
```

If an algorithm string is not in the dictionary, it falls back to a generic message. This is fine. However, algorithms like `hill-climbing`, `csp`, `expectimax` produce trace rows with `explain_selection` showing the generic fallback. This is acceptable for educational demos but worth noting.

### 13. No `error.tsx` / `loading.tsx` Boundaries

**File (missing)**: `web/src/error.tsx`, `web/src/loading.tsx`

While this is a Vite app (not Next.js), so `error.tsx`/`loading.tsx` convention doesn't apply. However, the app has no error boundary component wrapping the main content. An unhandled React error in `PuzzleBoard` or `TraceTable` would crash the entire app to a white screen.

Impact: Low for this academic app, but worth adding a simple `<ErrorBoundary>` wrapper.

---

## Low Priority

### 14. `local_demo` Actions Are Always "Investigate"

**File**: `api/eight_puzzle_detective_core.py`, line 284

```python
actions = ["Investigate" for _ in path[1:]]
```

This replaces the actual move names (Up/Down/Left/Right) with the detective metaphor. The trace rows still show the correct `node.action` field, so the information is not lost. Purely cosmetic.

### 15. PDF Length Truncation at 3500 Characters

**File**: `api/main.py`, line 201

```python
safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")[:3500]
```

Reports longer than 3500 characters are silently truncated in the PDF output. The markdown and HTML exports have no such limit.

### 16. No `.editorconfig` or `CODEOWNERS`

Bootstrap checklist (rule #17) mandates `.editorconfig`, `.github/CODEOWNERS`. Neither exists.

---

## Edge Cases Found by Scout

| # | Description | Severity |
|---|-------------|----------|
| E1 | **Tailwind v4 + JS config gap**: `shadow-glow` utility not compiled — cosmetic but jarring | High |
| E2 | **DLS frontier always empty in trace**: trace_row called before frontier built | High |
| E3 | **PDF missing xref + startxref**: malformed PDF, non-ASCII dropped | High |
| E4 | **Local search max_frontier overcount**: `max_frontier = max(max_frontier, len(trace))` on line 285 — trace length is step count, not frontier size | Medium |
| E5 | **Solved path validation: `actions` field mismatch for local search**: `actions = ["Investigate"]` are not actual move names, but `validate_path` checks states, not actions | Low |

### E4 Detail

```python
# local_demo, line 285
return finish(..., max_frontier, ...)
# max_frontier passed as: len(trace)
```

Wait — `max_frontier` in `local_demo` is set as `len(trace)` on line 285. But `trace` records one row per expansion step. The actual maximum frontier size in local search is at most 4 (max legal moves from any state). Setting `max_frontier = len(trace)` is misleading — it conflates expansion count with frontier size. The result's `max_frontier` field would show a number (up to 80) that's actually the number of steps taken, not the frontier size.

---

## Positive Observations

1. **Search core correctness**: BFS, DFS, UCS, Greedy, and A* all work correctly via the unified `graph_search`. The priority-based heap vs FIFO/LIFO queue dispatch is clean. All 8 tests pass.
2. **IDS implementation is real**: Unlike IDA*, the `ids()` function genuinely implements iterative deepening DLS with a recursive `dls()` inner function, correct depth limiting, and per-limit re-expansion. The trace accumulates across limits.
3. **Type annotations are thorough**: `State`, `Node`, `SearchResult`, `DetectiveCase` are all typed. TypeScript types mirror the Python data structures.
4. **Test coverage of key paths**: Solvability, legal moves, heuristic correctness, A* solution, unsolvable fast-fail, API endpoint integration, export pack all tested.
5. **Heuristic evidence computation is correct**: Both `misplaced` and `manhattan` correctly ignore the blank tile (line 97: `if tile and tile != goal[index]`; line 104: `if tile == 0: continue`).
6. **Solvability check prevents wasted search**: Unreachable states are caught by inversion parity before any expansion for standard algorithms.
7. **Detective metaphor is consistent**: The `autopsy`, `certificate`, `case_id`, `lesson` pattern is applied uniformly across the API, core, and UI.
8. **TypeScript compiles clean**: `npx tsc --noEmit` produces zero errors.

---

## Recommended Actions

### Must-Fix Before First Release
1. **Implement true IDA*** with iterative f-cost threshold loop (alternatively: remove IDA* claim and document)
2. **Add `@config` directive to styles.css** or migrate to `@theme` CSS blocks
3. **Add Dockerfiles and docker-compose.yml** following CampusCore patterns
4. **Add `.github/workflows/ci.yml`** with build, lint, test, coverage gates

### Should-Fix
5. **Fix PDF xref table** and use UTF-8 or properly handle non-Latin1 text
6. **Fix DLS frontier tracking** — record frontier before appending trace row
7. **Fix API client spread order** — `...init` before explicit `headers:`
8. **Remove dead `order` variable** from `ids()` function
9. **Fix `max_frontier` in `local_demo`** — compute from actual neighborhood size, not trace length

### Nice-to-Have
10. Add React error boundary component
11. Remove unused `tailwindcss` package (keep only `@tailwindcss/postcss`)
12. Add `.editorconfig` and `.github/CODEOWNERS`

---

## Metrics
- Type Coverage (TypeScript): strict mode, full typing — no `any` usage
- Type Coverage (Python): all public functions annotated
- Test Coverage: 8 tests (core + API), all passing, no coverage % measured
- Linting Issues: 0 TypeScript errors; Python lint not run
- Build Status: not attempted (no Docker, no CI)

## Unresolved Questions
- No `.env.example` or `.env.production.example` found (privacy block prevented checking)
- Is the `CORS_ORIGINS` env var realistic for production, or should it be locked to specific origins?
- Are non-search educational algorithms (minimax, alpha-beta, expectimax, and-or, no-observation, etc.) intended to be implemented later? Currently they all route to `educational_demo()` which returns a placeholder message.
- Should the benchmark include local search algorithms (currently included: hill-climbing, csp, expectimax)? CSP and expectimax are placeholder algorithms that always return "not found".
