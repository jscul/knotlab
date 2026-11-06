# Closure of the scouting epic after the Rowell result

Status: Proved

Epic `NEXT-DIRECTION-SCAN-20261026-001` closed on 2026-10-26.
- **What this is.** A ledger: no new claim. All three lanes are documentation tickets.
- **The decision note** is `research/NEXT-DIRECTION-SCAN-20261026-001/decision.md`.
- **The lane reports** are `research/NEXT-DIRECTION-SCAN-20261026-001{A,B,C}/report.md`. The scouting agents' harness refused
  to save them, so the top-level task wrote them from the agents' final reports and reran every lane's scripts in a temporary
  mirror of the repository; all outputs were identical apart from timing.

## Conclusions

| # | Conclusion | Label | Evidence |
| --- | --- | --- | --- |
| 1 | For coprime class-2 groups of class (K), one alternating invariant 3-form carries every obstruction component, and with the edge gadgets the count is a Bulatov–Grohe partition function whose weight matrix has rank one exactly when there is no hard pair. For p odd over prime fields this sketches the dichotomy for the whole class. | Computed (199 cases, 15 groups); hardness sketched, not proved | `NEXT-DIRECTION-SCAN-20261026-001A` |
| 2 | For UT₃(F₄) ⋊ C₃ the exact reduction also preserves approximation, so approximating knot-group counts is #BIS-hard. The Heisenberg pure-leaf recipe is not approximation-preserving; S₄ has no verdict. | Proved (direct consequence); the rest computed | `NEXT-DIRECTION-SCAN-20261026-001B`; now Proposition 18 of `ROWELL-NOTE-20261026-001-P001` |
| 3 | The K1–K3 test does not see the hard pair: every group law is a Latin knot, and every nonzero trilinear zero set is a knot in the vector reading. The positive bridge (in the signed reading, the count is the emergence) is classical. | Computed and proved (one-line arguments); negative for the bridge | `NEXT-DIRECTION-SCAN-20261026-001C` |
| 4 | A prior-art check for the note: Rowell's part (b) already fails on links for S₃ and the odd dihedral groups. | Proved and checked end to end | Proposition 1 of `ROWELL-NOTE-20261026-001-P001` (evidence in its `links/`) |

## Challenged assumptions

- "The Rowell refutation needs our knot results." False for links: S₃ suffices there. The knot results remain the new part,
  since on knots metabelian targets are easy.
- "Pairwise versus three-way will match not-a-knot versus knot." False under K1–K3 (lane C).
- "The Potts gadgets are essential." Lane A indicates that Bulatov–Grohe makes any non-rank-one block suffice.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: the three-lane scan | **Status:** Successful | Every lane returned decision-ready evidence; every replay reproduced. |
| Local direction: counting complexity of solvable targets | Continue, bounded | The class-(K) dichotomy is the lead with evidence behind it. |
| Broader exploration: the complexity program | Known alternatives | Nilpotent groups on links (1/3); an S₄ tangle scan (1/3); signed-atom Holant networks (1/3). The K1–K3 bridge found nothing. |
| Long-term goal: the complexity side of the 2-versus-3 thesis | Obstruction learned | The line is pairwise versus three-way with no bounded place; K1–K3 does not certify it. |
| Next recommendation: the class-(K) dichotomy | **Next step:** Continue, with a short epic proving the p-odd, prime-field dichotomy for class (K), gated on a pattern-1 projector knot (predicted N = 133 and 2737) | Stop if the gate fails, or if a published statement is found. |
| Interest | **2/3: Promising** | The gain is generality; the criterion itself does not change. |
| Execution | Planned | It awaits the owner's choice. |
