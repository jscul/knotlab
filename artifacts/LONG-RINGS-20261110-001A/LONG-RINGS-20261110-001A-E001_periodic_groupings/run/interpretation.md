# Periodic groupings of the square torus's automaton: interpretation

Experiment `LONG-RINGS-20261110-001A-E001` (exploratory), run once on 2026-11-10 under the frozen contract (pre-registered in 543d364ab),
in 437 s on 6 workers. Exact: shortest-route parities for the plain first need of every ring at every target of a fundamental domain.
Every on-time grouping is listed in `result.json`.

## Control

The two axis line networks, periodic under the full lattice, are on time on all three tori, as `REROUTE-20261109-001B`, Theorem 2,
proves.

## Primary observable

| Torus | Sublattices (index) | Patterns | Networks | On time | Line classes (p, q) of the on-time groupings, up to sign and mirror |
| --- | --- | --- | --- | --- | --- |
| 12 × 12 | 27 (to 6) | 51,252 | 2,092 | 198 | (1, 0), (1, 1), (1, 2), (1, 3), (1, 5) |
| 16 × 16 | 26 (to 8) | 984,884 | 10,076 | 480 | (1, 0), (1, 1), (1, 3), (1, 7), (3, 5) |
| 24 × 24 | 42 (to 8) | 1,034,292 | 11,892 | 624 | (1, 0), (1, 1), (1, 2), (1, 3), (1, 5), (1, 7), (3, 5) |

- **H1 holds.** Every one of the 1,302 on-time groupings is a family of parallel lines. Every ring is non-contractible, and all its
  rings lie in one homology class (p, q), up to sign: half run one way and half the other.
- **H2 holds.** The ring graph of every on-time grouping is a cycle, so a ball of radius r holds 2r + 1 rings.
- **What the lines look like.** In a grouping of class (p, q) on the n × n torus all rings have 2n(|p| + |q|) contacts and there are
  2n / (|p| + |q|) of them: each ring winds once round the torus in direction (p, q) as a staircase of staircases. The classes found are
  those with |p| + |q| dividing 2n that a period of index at most 8 can carry. The axis lines are the case |p| + |q| = 1.

## Reading against the decision rule

Both hypotheses hold, so the periodic groupings give no plane of long rings. What reads plainly is a family of lines, of many slopes, and
never two families crossing. Every other periodic grouping is late somewhere.

## Nonclaims

- **Exploratory and finite:** periodic groupings with period cells of at most 8 positions (6 on the 12 × 12 torus) only. Non-periodic
  groupings are not read.
- **Law (12, 12) on the square torus only;** two-time knots only (A30).
