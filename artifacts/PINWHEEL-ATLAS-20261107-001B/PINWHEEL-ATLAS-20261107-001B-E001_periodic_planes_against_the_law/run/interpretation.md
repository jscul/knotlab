# Periodic planes against the pinwheel's law: interpretation

Experiment `PINWHEEL-ATLAS-20261107-001B-E001`, exploratory and non-promotable. Run on 2026-11-07, 470 s, as frozen in
`contract.json`.

## Readings

**The law.** Ticket A's atlas: the 1,168 radius-2 rooted codes of all pinwheel tilings, and their radius-1 truncation (198 codes).

**Controls.** Both behave as required.
- **The pinwheel itself.** The pinwheel's level-5 patch passes: none of its 6,546 tested darts at radius 1 and 5,162 at radius 2
  lies outside the law.
- **The tetrakis triangulation.** The isosceles right-triangle substitution fails at radius 1: all 80 of its tested darts lie
  outside the law.

**Candidates.** No periodic candidate passes, not even at radius 1.

| Family | Configurations | Pass at radius 1 | Pass at radius 2 |
| --- | --- | --- | --- |
| Rectangle grids, every diagonal pattern of period (p, q) ≤ (2, 2) | 26 | 0 | 0 |
| Brick rows, the same patterns (T-junctions at long-leg midpoints) | 26 | 0 | 0 |
| Domino tilings of the 2×2 torus, every diagonal choice | 32 (8 tilings) | 0 | 0 |
| … of the 2×4 and 4×2 tori | 1,152 (72 tilings) | 0 | 0 |
| … of the 2×6 and 6×2 tori | 25,600 (400 tilings) | 0 | 0 |
| … of the 4×4 torus | 69,632 (272 tilings) | 0 | 0 |
| The six two-tile shapes, each tiled by half-turns | 6 | 0 | 0 |
| The frame-consistent cut, level 5 (not periodic, not round) | 1 | 0 | 0 |

**How badly the shapes fail.** For the six two-tile shapes and the frame-consistent cut, every tested dart lies outside the law at
radius 1: 4,302 to 7,240 darts each. The torus and row families were stopped at their first dart outside the law, so only their
pass counts are recorded.

**A diagnostic, read after the run (not part of the decision).** Interior vertex degrees differ in kind.
- **The pinwheel.** At level 6 its interior vertices have degree 3, 4, 6 or 8 (3,851; 1,870; 557; 2,362).
  - **Degree 3 is the commonest.** A degree-3 vertex is the midpoint of a long leg where two right angles meet.
- **The candidates.** None has a degree-3 vertex.
  - **Uniform degrees.** The rectangle, kite and parallelogram tilings have every vertex of degree 6; the brick rows tested, degree
    4; the isosceles tilings, degrees 4 and 8.
  - **The frame-consistent cut** has degrees 3, 4, 6, 7 and 8, with a degree 7 the pinwheel never shows.

## What this says

- **Decision.** By the frozen rule, no tested periodic plane obeys the pinwheel's law, at radius 2 or even at radius 1. This is
  evidence that the law excludes periodic planes, not a theorem.
- **Unlike the sphere's tube lemma.**
  - **On the sphere.** A local law without hidden states cannot tell the round knot sphere from a long tube, because every ball of
    the tube occurs in the sphere (`SPHERE-GROWTH-20261107-001`).
  - **In the plane.** The pinwheel's own law is far more selective. The local forms of every tested periodic plane, and of the one
    tested non-round hierarchical plane, never occur in a pinwheel tiling at all.
- **Where the selectivity comes from (a reading).** Pinwheel vertices are mostly T-junctions at long-leg midpoints, in a few fixed
  combinations. Crystalline arrangements of the same triangle produce other combinations.

## Limits

- **Finite families.** The candidates are rectangle-based periodic tilings with small periods, six half-turn tilings and one
  substitution. A periodic plane built from the pinwheel's own vertex stars was not searched.
  - **Scope change.** The ticket's objective named such a search; the frozen contract replaced it by the domino tori before
    anything was run.
  - **The open question.** Whether any periodic plane obeys the law, and so whether the undecorated law forces aperiodicity, is
    still open.
- **Prior work.**
  - **Undecorated local rules.** These are Levitov's setting (Commun. Math. Phys. 119, 1988). For rhombus tilings, undecorated strong
    local rules exist only in a few symmetries; Socolar's weak rules (Commun. Math. Phys. 129, 1990) cover more.
  - **Decorated rules.** Decorated matching rules exist for substitution tilings generally (Mozes, 1989; Goodman-Strauss, Annals of
    Mathematics 1998; for the pinwheel, Radin, Annals of Mathematics 1994). Fernique and Ollinger (2010) relate combinatorial
    substitutions to sofic tilings.
  - **Not found.** An undecorated local law for the pinwheel, or this comparison with periodic planes.
- **Local only.** Passing would have meant indistinguishable within radius r, not globally a pinwheel tiling.
