# Closure of the tractability epic

Status: Proved

Epic `CYCLE-TRACTABILITY-20261021-001` closed on 2026-10-21. This is a ledger:
one line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is
`research/CYCLE-TRACTABILITY-20261021-001/tractability.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The equal-top lift of any finite structure composes like cycles. Its free sets are the partial transversals of the components, and it is homomorphically equivalent to the structure. | New to the program; elementary (a standard product) | `CYCLE-TRACTABILITY-20261021-001A-P001`, Theorem 1 |
| 2 | The core question is settled negatively, in two of the owner's three ways. The core of a law composing like cycles need not compose like cycles (K₃), and such laws can have non-Taylor cores (K₃, not-all-equal) with NP-complete constraint problems. | New to the program; classical hardness | `…001A-P001`, Corollary 2 |
| 3 | The shifted lift is a core whenever the structure is, composes like cycles, and keeps the constraint problem. So being a core does not help: without constants, composing like cycles does not imply polynomial time unless P = NP. | New to the program; elementary | `…001A-P001`, Theorem 3 |
| 4 | A law composing like cycles that is a core with no nontrivial automorphism is tractable. Both hypotheses are needed: one-in-three's equal-top and shifted lifts are NP-complete. | Short application of a classical step and the utility proof | `…001A-P001`, Proposition 4 |
| 5 | Correction of the previous closure. "The NP-hard examples are exactly where it fails" is wrong, since x ≤ y is tractable and also fails. The correct statement: cycle-like composition, with constants, certifies tractability; the program's NP-hard examples all lack it. | Correction | decision note |

## Recommendation

**Continue** with the holes connection, as a fresh epic.
- **The claim to test:** group-like knots are exactly those that both remember
  loops and compose like cycles, so holes behave like homology over finite
  fields modulo the tops.
- **The ties:**
  - `KNOT-LOOPS-20261019-001`: only group-like knots remember a loop;
  - `HOLES-COHOMOLOGY-20261019-001`: one H¹ class per loop.
- **Then:** what it implies for contact networks.
- **The queue:** the contact, network and distance questions stay there.
- **Interest:** 2/3.
- **Execution:** started, under the owner's instruction.
