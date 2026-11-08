# A census of networks of loops: interpretation

Experiment `LOOP-NET-20261108-001B-E001` (exploratory), run 2026-11-08 under the frozen contract: 395 plane ring graphs and 170,502
placements of figure-eights and chords, in 194 s on 16 workers. D is exact over GF(2)(z) and return counts are exact; persistence is
read to lag 300. Totals are in `result.json`; the placements that persist to lag 300 or cancel every return are in `networks.json`.

## Control

`LOOP-NET-20261108-001A`'s checks 1, 3 and 4 compare the exact D with the cell reading and with return counts.

## Part 1: plane ring graphs (H2)

| Plane ring graphs of 2 to 7 rings, equally spaced | Count |
| --- | --- |
| Graphs | 395 |
| Every return count even at every contact | 8 |
| A flip at every contact | 7: the loops of 3 to 7 rings, the tetrahedron, the octahedron |
| A flip at every contact but some return count odd | 0 (H2 holds) |
| Every return count even without a flip at every contact | 1 |

The exception has six rings and ten contacts: two rings of four contacts and four of three, with four triangular and two square faces
(edges 0-1, 0-2, 0-5, 1-2, 1-3, 1-4, 2-5, 3-4, 3-5, 4-5). Its returns cancel with no symmetry that fixes the contact.

## Part 2: figure-eights and chords at equal ring sizes (H1)

Every ring has the same size s = 5 to 9, so a ring of three or four contacts and a ring of two cannot have the same density.

| Family | Placements | Every return cancels | Persistent to lag 300 |
| --- | --- | --- | --- |
| Figure-eight of two loops of two rings | 1,014 | 20, all degenerate | 56 |
| Figure-eight of loops of two and three rings | 5,934 | 0 | 28 |
| Figure-eight of two loops of three rings | 34,854 | 0 | 0 |
| Chord (1, 1, 2) | 3,276 | 0 | 80 |
| Chord (1, 2, 2) | 18,612 | 0 | 336 |
| Theta (2, 2, 2) | 106,812 | 0 | 0 |

- **H1 holds.** No placement without a pair of equal parallel corners cancels every return. The 20 that do are figure-eights of two
  two-ring loops in which, on the shared ring and on a loop's ring, the corners from one contact to the next have the same length and
  cancel, so no influence returns.
- **Persistence through other cells is rare and unproved.** 500 of 170,502 placements keep every contact binding both rings to lag 300,
  none of them a figure-eight of two three-ring loops or a theta (2, 2, 2). Lag 300 does not decide them: at wider spacing
  `LOOP-NET-20261108-001A`'s check 9 finds figure-eights that first miss a ring at lag 630 or 1,143.

## Reading against the decision rule

- **H1** supports the obstruction beyond uniform networks for these families at equal ring sizes: where a loop of two-contact rings
  meets a ring with more contacts, no placement cancels the returns.
- **H2** agrees with `LOOP-NET-20261108-001A`'s Theorem 3, and the exception shows that even return counts do not need a symmetry.

## Nonclaims

- **Lags to 300**, sizes 5 to 9, these families, and one plane rotation per atlas graph.
- **Two-time knots only** (A30).
