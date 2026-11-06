# Closure of the odd-loop identity epic

Status: Proved

Epic `ODD-LOOP-20261023-001` closed on 2026-10-23. This is a ledger: one line per conclusion, with its novelty label and evidence. It makes no new claim. The decision note is `research/ODD-LOOP-20261023-001/odd_loop_identity.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The odd-loop identity holds exactly on every square-lattice torus, at every shear and for every primitive class c. The two twists odd on c give the same probability that the strong components wind along c and nothing else. | Not found in the literature; low folklore risk for the statement | `ODD-LOOP-20261023-001B-P001`, Theorem 1 |
| 2 | The proof is an explicit involution. It slides the second twist's seam onto the wall bounding the lift of the odd strong component from above, flips the bits of wall edges whose free end is their head, and gauges back. No directed cycle changes, so every cycle statistic has the same law on the two events. | Seam-moving by gauge is standard; the loop as its own barrier and the bit flips are new to the program; moderate folklore risk for the technique | `…001B-P001`, Lemmas C–D |
| 3 | odd10 + odd01 − odd11 = twice the probability of an odd loop in a diagonal class, on every torus. So the consistency relation is equivalent to D equal to that probability. | Elementary consequence | `…001B-P001`, Corollary 2 |
| 4 | Straight inert bands give an involution only on bands avoiding the row above the default seam. A stored 4 × 4 orientation breaks the unrestricted rule, and coverage falls to about a third on 6 × 5. | A recorded negative | `…001B-P001`, Proposition 3 and check.py |
| 5 | Exhaustive counts on 13 tori up to 4 × 4 (2³² orientations per shear) confirm the identity in all 126 comparisons, including diagonal classes. Shear independence of the line fails exactly at 4 × 4: 39168000 at shears 0 and 1 against 39085056 at shear 2. | A recorded computation | `ODD-LOOP-20261023-001A-E001` |

## Challenged assumptions

The decision note records five workspace assumptions this epic challenges:
- that a proof needs a seam along a straight row;
- that barrier-following seams rewire the band and break the bijection;
- that the identity is only a statement about one pair of probabilities;
- that small-torus equality marks an exact law;
- that the identity holds for any orientation law (it needs fair orientations).

## Recommendation

**Continue: where the loop shields the twist.**
- **What it tests.** The mechanism's predictions:
  - an exact identity on a genus-2 surface, only between twists that differ by the twist dual to c;
  - its failure on the 3-torus, where a loop cannot separate.
- **Interest:** 2/3.
- **Alternatives:** a bounded search for the program's next barrier question (1/3), and a self-contained note on the twisted-torus results (1/3).
- **Execution:** deferred to the owner.
