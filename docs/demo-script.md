# Demo Script

## 1. Start services

1. Start backend with `uvicorn main:app --app-dir api --reload --port 8000`.
2. Start frontend with `npm --prefix web run dev`.
3. Open `http://localhost:5173`.

## 2. Detective case flow

1. Choose `Easy two-move clue`.
2. Keep algorithm `A*`.
3. Click `Run investigation`.
4. Explain that A* chooses nodes by `f(n)=g(n)+h(n)`.
5. Show path cost, expanded count, certificate, and trace story.

## 3. Next-node prediction

1. Open the `Prediction Lab` panel.
2. Pick the board state you think the algorithm will inspect next.
3. Click `Check prediction` and read the expected state plus explanation.
4. Tie the result back to the priority rule shown in the trace story.

## 4. Misconception quiz

1. Open the `Misconception Quiz` panel.
2. Answer the BFS vs UCS, A* admissibility, DFS optimality, and parity questions.
3. Reveal answers and discuss why each misconception matters.

## 5. Heuristic evidence

1. Open the heuristic evidence board.
2. Point out each tile contribution.
3. Compare `misplaced` intuition with Manhattan distance.

## 6. Trap and limitation flow

1. Choose `Greedy trap` or `Local minimum alley`.
2. Run Greedy or Hill Climbing.
3. Explain why a lower local `h(n)` can still mislead search.

## 5. Academic coverage

Mention the six covered groups:

- Uninformed search: BFS, DFS, UCS, IDS.
- Informed search: Greedy, A*, IDA*.
- Local search: hill climbing, stochastic hill climbing, beam-style/randomized demos, simulated annealing.
- Complex environments: alternate-world educational models.
- CSP: modeling and constraint reasoning demo.
- Adversarial/stochastic: minimax, alpha-beta, expectimax-style demos.

## 7. Export pack

1. Click `Download Markdown report`.
2. Explain the API also returns CSV, HTML, DOCX, and PDF payloads.
3. Use the report as coursework evidence.
