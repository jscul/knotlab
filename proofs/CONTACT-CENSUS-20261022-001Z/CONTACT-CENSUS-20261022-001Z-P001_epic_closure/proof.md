# Closure of the contact-census epic

Status: Proved

Epic `CONTACT-CENSUS-20261022-001` closed on 2026-10-22. This is a ledger:
one line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is `research/CONTACT-CENSUS-20261022-001/census.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The 204 placements of the 34 three-variable knots as one contact per edge of a square-lattice torus, with hidden joints and a fair visible spoke, form 10 classes with equal consistency laws under spoke swap, joint-value swap and reversal. | Elementary; new to the program | `CONTACT-CENSUS-20261022-001A-P001`, Theorem 1 |
| 2 | Six classes (144 placements) have a vacuum, a constant joint value that satisfies every edge, and hold nothing. | Elementary | `…001A-P001`, Theorem 2 |
| 3 | Parity holds exactly the cycle rank. Swap-or-order is frustrated by a 2 × 3 domino (8 of its 128 spoke patterns). Both grow with the area. | Elementary; the parity count is classical | `…001A-P001`, Theorem 3 |
| 4 | Not-all-equal and "x or (h ≠ h′)" are consistent on every bipartite graph, so they have no frustrating patch and hold only global emergence. | Elementary | `…001A-P001`, Theorem 4 |
| 5 | "x or (h ≠ h′)" is consistent exactly when its disequality edges, bond percolation at 1/2, are bipartite: no cluster has a cross topology and none winds in a class of odd length. | Elementary reduction; it is a bond-diluted antiferromagnet, so moderate folklore risk | `…001A-P001`, Theorem 5 |
| 6 | At fixed shape, its emergence is bounded away from 0 and from infinity on non-bipartite square tori. Argued in prose from crossing bounds and positive correlation; not machine-checked. | Classical ingredients | `…001A-P001`, Theorem 6 |
| 7 | Pinson's formulas predict its limit: 1.508460 bits on square tori with both sides odd, 1.985201 on 1:2 tori with one odd side, 0.677388 with rows 3k (odd) and columns 2k, and 1.789802 with both sides odd at ratio 3:5. | Classical formula (cited, not proved), new application | `…001A-P001`, Pinson's prediction |
| 8 | Measured on six shapes, the emergence of "x or (h ≠ h′)" matches Pinson's limits within about 1.5 standard errors. Not-all-equal is flat at 0.835 bits on square tori and "x or (h ≠ h′)" at 1.521 bits over sides 9–65. The vacuum classes never failed. Parity gave 9.91 ± 0.10 and 15.6 ± 0.3 bits against exactly 10 and 16, and swap-or-order grew from 4.29 to 11.46 bits. All 12 placements of each critical class agree. | Empirical, confirmatory | `CONTACT-CENSUS-20261022-001B-E001` |

## Challenged assumptions

The decision note records four workspace assumptions this epic challenges:
- that not-all-equal is the critical contact;
- that the scale-free amount is unidentified;
- that a lower bound at criticality is out of reach;
- that most three-literal contacts carry emergence at scale.

## Recommendation

**Continue** with not-all-equal's critical invariant.
- **The test:** a shape scan of not-all-equal, together with a search for an
  exact reduction to a known directed or two-component percolation topology
  or a matching Coulomb-gas formula.
- **Interest:** 2/3.
- **Alternatives:** banking the three epics as a note (1/3), and a proof of
  not-all-equal's lower bound (1/3).
- **Execution:** deferred to the owner.
