# Closure of the holes-at-infinity epic

Status: Proved

Epic `HOLES-AT-INFINITY-20261020-001` closed on 2026-10-20. This is a ledger:
one line per conclusion, with its novelty label and evidence. It makes no new
claim.
- The decision note is
  `research/HOLES-AT-INFINITY-20261020-001/holes_at_infinity.md`.
- The owner's open decision, whether ends count as native loops, is
  `research/HOLES-AT-INFINITY-20261020-001/canonical_correction_request.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On an infinite, connected, locally finite graph every Tseitin system is satisfiable. A non-constant parity of finitely many edge variables is changed either by a finite circuit, or only by infinite changes: a finite cut with infinitely many vertices on both sides. Each solution records where its hole went, as a finitely additive measure on the end space. | classical (Diestel–Kühn; Bruhn–Stein; Berger–Bruhn), restated | `HOLES-AT-INFINITY-20261020-001B-P001`, Theorem 1 and Proposition 2 |
| 2 | A vertex relation passes K1–K3 exactly when its edges are open. The 3-regular tree carries a knot at every vertex, all opened by ends; a finite tree carries none. | short consequence; new to the program | `…001B-P001`, Theorem 2 |
| 3 | Adding one edge outside any finite ball turns an end-supplied parity into a loop-supplied one without changing the ball's projection. No finite part and no K1–K3 verdict decides the source. | not found stated; elementary | `…001B-P001`, Theorem 3 |
| 4 | For each end, the tangle pseudo-expectation of `SOS-SIZE-20261020-001B-P001` (Theorem 1) is the moment sequence of the uniform measure on the solutions whose hole went to that end. | not found stated; elementary | `…001B-P001`, Theorem 4 |
| 5 | Some computable tree carries a satisfiable system with no computable solution. | folklore | `…001B-P001`, Proposition 5 |
| 6 | The readable invariants of "differ in finitely many variables" form a Boolean algebra whose Stone space is the system's ends. For GF(2)-linear systems the ends are the solutions modulo the closure of the finitely supported homogeneous solutions, and every open parity is loop- or end-supplied. | known in substance (homoclinic relation; Lind–Schmidt) | `HOLES-AT-INFINITY-20261020-001C-P001`, Theorems 1 and 2 |
| 7 | On the square grid, Tseitin's vertex law has only loop-supplied openness. Ledrappier's triangle law has no finitely supported homogeneous solution, and every triangle is a parity knot opened entirely by infinity. | example classical; the reading is new to the program | `…001C-P001`, Theorem 2(d) |
| 8 | Relations among finitely many variables form at finite stages; rigidity does not. No two-literal clause system has a knot among its variables. | classical (compactness; majority closure) | `…001C-P001`, Propositions 3 and 4 |
| 9 | Trends separate solutions that every readable invariant identifies: where an implication chain's switch went, the slope of a grid 3-colouring's height function, and a circle through the end of the one-way ladder. The knot test cannot see them. | examples classical; the reading is the program's | `…001C-P001`, Theorem 5 |

## Recommendation

**Continue, as a fresh epic after the owner decides the fork.** The question
is rigidity beyond groups: do things at infinity require group-like
propagation? Run a census of edge-uniform binary laws first.

Interest 2/3. Deferred to the owner.
