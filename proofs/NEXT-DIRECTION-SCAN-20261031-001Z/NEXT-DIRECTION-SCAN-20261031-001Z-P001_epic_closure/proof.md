# Closure of the scan back toward native emergence

Status: Proved

Epic `NEXT-DIRECTION-SCAN-20261031-001` closed on 2026-10-31.
- **What this is.** A ledger: no new claim. All three lanes are documentation tickets.
- **The decision note** is `research/NEXT-DIRECTION-SCAN-20261031-001/decision.md`.
- **The lane reports** are `research/NEXT-DIRECTION-SCAN-20261031-001{A,B,C}/report.md`. Every lane's script was rerun in a temporary
  mirror of the repository, and its output was identical apart from timing.
- **The top-level basis check** is `research/NEXT-DIRECTION-SCAN-20261031-001/basis_check.py`, with its log.

## Conclusions

| # | Conclusion | Label | Evidence |
| --- | --- | --- | --- |
| 1 | On the knot's own spaces (Fano and two 13-point Fano splices), single-flip descent toward fewer colourings reaches the knot's sign class from every class. Every tested Pfaffian graph with 4-cycles has traps. | Computed (12 graphs, exhaustive); the dynamics is imposed | `NEXT-DIRECTION-SCAN-20261031-001A` |
| 2 | Junctions of knot-class pages are matchgate signatures at every coupling. At depth two, closed branches leave the pages' two-parameter family by a defect divisible by 3x² + 1. Junctions of two deep branches break the identity in 5 of 6 pairs, and the factors common to all five are exactly x, x ± 1, x² + 1, 3x² + 1: the counting point and the affine couplings. | Computed (exact polynomials, brute-force cross-checks, control); one exception (two truncated-octahedron branches) | `NEXT-DIRECTION-SCAN-20261031-001B` |
| 3 | The failure in conclusion 2 is not an artifact of the y-basis. At a generic coupling, only diagonal or antidiagonal transformations keep both vertex signatures parity-definite, and they rescale the identity. | Computed (symbolic solve); necessary condition only | `basis_check.py` |
| 4 | Counting 2-colourings one line short of Seymour's bound is #P-hard, even on connected Seymour-sparse systems of degree at most 3 (point splitting: #col(H0) = 2 #col(H1) − #col(H2)). Only the knot's subclass is known to be easy. | Proved (a one-line reduction) and checked on 54 splits | `NEXT-DIRECTION-SCAN-20261031-001C` |

## Challenged assumptions

- **"The knot's class is a free fermion along the whole coupling line."** True only for single pages. At depth two the matchgate mechanism
  pins the coupling to the counting point (conclusion 2).
- **"A native law selecting the knot's signs needs a dynamics."** Lane A's descent is imposed. Lane B's selection is by the coupling alone,
  with the signs fixed.
- **"One line short of the bound is a new counting regime."** Lane C: it is #P-hard in general, and Theorem 1 of the note already covers
  the knot's part.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the three-lane scan | **Status:** Successful | Every lane returned a decision-ready discriminator, and every replay reproduced. |
| Local direction — the counting arc's mechanisms | Continue through lane B | Lanes A and C are retired as standalone epics; their findings are recorded. |
| Broader exploration — the two/three boundary | Known alternatives | Lane A's funnel (1/3); the colourable side of H − L (1/3); approximate counting (not assessed). |
| Long-term goal — the two/three boundary as emergence | Capability gained (computed evidence) | The knot's signs keep counting planar only at the knot's own law, on every tested depth-two tree but one. |
| Next recommendation — a coupling dichotomy in the knot's class | **Next step:** Continue. Open a fresh epic: is the three-body Ising model with the knot's signs #P-hard away from x² = −1/3 and the affine couplings? | First discriminator: interpolate a crossing from a deep-branch junction inside the knot's class. Stop on a tractable route at a generic coupling, on special families keeping the identity in general, or on a published statement. |
| Interest | **3/3 — Hot** | Exact, cross-checked evidence; the payoff is a native selection theorem. Main uncertainty: the hardness step. |
| Execution | Planned | It awaits the owner's choice. |
