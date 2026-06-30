# 8-Puzzle Detective Lab Report Template

## Problem statement

Describe the 8-Puzzle state space, start state, goal state, blank tile actions, and solvability condition.

## PEAS

- Performance:
- Environment:
- Actuators:
- Sensors:

## Algorithm profile

| Algorithm | Complete | Optimal | Priority rule | Notes |
|---|---|---|---|---|
| BFS | Yes | Yes | FIFO by depth | Unit edge cost |
| DFS | No | No | LIFO by depth | Can go deep first |
| UCS | Yes | Yes | minimum `g(n)` | Same as BFS when every cost is 1 |
| Greedy | No | No | minimum `h(n)` | Fast but can be misled |
| A* | Yes | Yes with admissible heuristic | minimum `f(n)=g(n)+h(n)` | Uses cost and heuristic |
| IDA* | Yes | Yes with admissible heuristic | iterative f threshold | Memory efficient |

## Detective trace story

Explain selected node, frontier evidence, reached set, priority rule, and selection key.

## Next-node prediction

Record the state you predicted for the second trace row, the expected state returned by `/api/predict`, and the priority-rule explanation. Note any intuition you had to revise.

## Misconception quiz

Summarize answers to the BFS vs UCS, A* admissibility, DFS optimality, and parity questions, plus the takeaway from each.

## Certificate

- Solvable:
- Path valid:
- Path length:
- Inversions start/goal:

## Benchmark

Paste benchmark rows from the app/API.

## Limitations

Explain which features are canonical solvers and which are educational models only.

## Conclusion

Summarize what the detective workflow taught about search behavior and wrong intuition.
