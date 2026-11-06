# Closure of the criticality-at-the-base epic

Status: Proved

Epic `BASE-CRITICALITY-20261022-001` closed on 2026-10-22. This is a ledger:
one line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is
`research/BASE-CRITICALITY-20261022-001/criticality.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For any two-colouring, not-all-equal constraints with fair visible spokes are equivalent to uniformly random implications on bichromatic edges plus uniformly random monotone two-literal clauses on monochromatic edges. | Classical gauge; the reading is new | `BASE-CRITICALITY-20261022-001A-P001`, Theorem 1 |
| 2 | In a uniformly random orientation, reach from any vertex set has the law of bond percolation at 1/2; with gadgets, at their traversal probability. | Known coupling (Grimmett's model); the gadget version is elementary | `…001A-P001`, Theorem 2 |
| 3 | A world with no directed crossing of its cut torus in one direction is consistent, so inconsistency needs crossings both ways. The converse fails. | New to the program | `…001A-P001`, Theorem 3 |
| 4 | Emergence vanishes below the lattice's bond threshold, stays bounded on the square lattice at 1/2, and diverges when two-way contacts percolate. The lower bound at criticality is open. | Classical ingredients; the reduction is new to the program | `…001A-P001`, Theorem 4 |
| 5 | Emergence depends on shape, not size. Means are 0.23, 0.72, 1.16 and 2.31 bits at aspect ratios 2/3, 4/3, 2 and 4, with drifts of at most 0.028 bits per doubling. It is rotation-invariant (difference 0.001 ± 0.011 bits) and stable under shear. The percolation coupling holds. Contacts below threshold drive it to 0, contacts above threshold and cubic 3-tori drive it beyond 14–16 bits, and 18–41% of worlds crossed both ways stay consistent. | Empirical, confirmatory; new to the program | `BASE-CRITICALITY-20261022-001B-E001` |

## Recommendation

**Continue** with a census of which three-literal contacts are critical.
- **The test:** a census of placed three-variable links on square tori with
  odd sides. It includes an exact test of "x or (h ≠ h′)", whose emergence is
  a critical wrapping quantity of bond percolation with a known conformal
  formula.
- **Interest:** 2/3.
- **Alternatives:** a proof of the lower bound at criticality, and banking
  both epics.
- **Execution:** deferred to the owner.
