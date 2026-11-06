# A planar removed side creates nothing

Status: Proved (a finite classification by exhaustive computation)

Ticket `HANDLE-EMERGENCE-20261102-001A`, 2026-11-02.

## Question

- **The setting.** Glue a knot space H1 into another, H2, along one simple 3-edge cut: a line of H1 goes into a point of H2. Then
  remove a line M on H1's side. This opens the cut (SPLICE-TREE A).
- **New knots.** A knot crossing the cut is new when eliminations from knots lying on one side cannot produce it (HUB-GLUE C).
- **The scout.** SPLICE-TREE's census scout found new knots only when H1 is non-planar.
- **The test.** Does that survive planar knot spaces beyond the census? One new knot on a planar side refutes it.

## Dependencies

- **`SPLICE-TREE-20261102-001C`.** Elimination up to tie classes, the bitmask circuits, and the size lemma (`elim_lib.py`).
- **`HUB-GLUE-20261102-001A`.** Splices and the census spaces (`glue_lib.py`).
- **`MUTUAL-SELECTION-20261031-001C`.** The census.
- **`THREEFOLD-SPACES-20261030-001`.** Failure is sign-nonsingularity. It is used only to choose signs; failure is checked directly.

## The planar spaces

- **Incidence graphs.** A knot space's incidence graph is cubic and bipartite. Every plane cubic bipartite graph gives two triple
  systems, one for each choice of which colour class holds the points (both are used; repeated lines are excluded).
- **Signs.** With Kasteleyn signs the knot fails. On every face of length 2k, the number of negative incidences is congruent to
  k + 1 mod 2. The signs come from solving these face equations over F2 (`planar_lib.kasteleyn`). Failure is then verified by
  enumerating every assignment.
  - **Agreement with sign-nonsingularity.** In a scout over 22,352 signings of the census spaces, "the knot fails" and "the ±1
    incidence matrix is sign-nonsingular" agreed every time.
- **The families.**
  - **Ladder moves.** Grown from the cube. A move picks a face and two of its edges at even distance along it, subdivides both twice
    and joins the four new vertices by a square inside the face. Three seeds give 10 and 12 points and two give 14.
  - **Prisms** over 10-, 12- and 14-cycles.
  - **The truncated octahedron**, as the permutations of four symbols joined by adjacent transpositions.

## Result

| Removed side | Removals | Six-pattern interfaces | Crossing knots | New knots |
| --- | --- | --- | --- | --- |
| 24 planar spaces beyond the census (into K4^(3), census 6, Fano, census 58) | 1612 | 724 | 432,867 | 0 |
| Planar census spaces (every ordered pair) | 560 | 96 | 39,277 | 0 |
| Non-planar census spaces (Fano, census 58) | 208 | 160 | 25,630 | 936, at 100 removals |

- **Four-pattern interfaces.** None of the 1400 creates, whether on a planar side (1352) or a non-planar one (48).
- **Every creating removal** has a six-pattern interface and a non-planar removed side.

## Proof

Exhaustive computation in `check.py`, with results in `result.json`:
- **Circuits.** Every circuit of every removal is computed by `elim_lib.circuits`. SPLICE-TREE C cross-checked it against
  `glue_lib.circuits`.
- **Generation.** It is decided by `elim_lib.closure` over tie classes, cross-checked against forward elimination in SPLICE-TREE C.
- **Exactness.** Every circuit is computed, so the classification is exact. ∎

## Checks

`check.py` (`result.json`, about two minutes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The 24 planar spaces: cubic triple systems with plane incidence graphs on which the knot fails | 24 of 24 |
| 2 | Every ordered pair of census spaces | planar sides 0 new; non-planar 936 new |
| 3 | Beyond the census | 1612 removals, 0 new |
| 4 | Interfaces | no four-pattern interface creates; creation only with six patterns and a non-planar side |

## What this does not establish

- **No proof.** This does not prove that planar sides never create. Ticket C takes up the proof.
- **Coverage.** The planar spaces come from three families of at most 14 points, spliced at one or two lines each.
- **Sufficiency.** Non-planarity is not sufficient: Fano > K4^(3) and Fano > census 56 create nothing.

## Novelty

- **New here.** The test.
- **Classical.** Kasteleyn signs and sign-nonsingularity.
