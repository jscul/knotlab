# Closure of the novelty-and-utility epic

Status: Proved

Epic `CYCLE-UTILITY-20261021-001` closed on 2026-10-21. This is a ledger: one
line per conclusion, with its novelty label and evidence. It makes no new claim.
The decision note is `research/CYCLE-UTILITY-20261021-001/utility.md`, and the
novelty scan is `research/CYCLE-UTILITY-20261021-001/novelty_scan.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A bounded scan of about twenty queries in seven families found no statement of the composition characterization or its matroid form. The individual steps (strong rectangularity, Herrmann's theorem, density) are classical. | `no-overlap-in-bounded-search`; not a priority claim | novelty scan |
| 2 | A code whose composition closure composes like cycles carries only matroids representable over finite fields. The Simonis–Ashikhmin non-Pappus code has uniform fibres but generates a three-copy system that fails elimination. | New to the program; corollary plus computation | `CYCLE-UTILITY-20261021-001A-P001`, Proposition 1 |
| 3 | A single-sorted law that still composes like cycles with all constants added has a Taylor polymorphism algebra, so a polynomial-time constraint problem. One-in-three, not-all-equal and 3-colouring all fail elimination. | New to the program; short, given the Taylor criterion and the dichotomy theorem | `…001A-P001`, Proposition 2 |
| 4 | The lifted Z₃ law and K₄ compose like cycles, but their counting problems are #P-complete. | Application of Dyer and Richerby | `…001A-P001`, Proposition 3 |
| 5 | Adding constants can destroy composing like cycles (parity beside J, K₄), so whether every such law is tractable is open. | New to the program | `…001A-P001`, Proposition 4 |

## Recommendation

**Continue** with whether composing like cycles alone implies a polynomial-time
constraint problem, as a fresh epic.
- **First:** whether the core of a law composing like cycles again composes
  like cycles. A rigid core then pp-defines its constants, and Proposition 2
  applies.
- **Then:** cores with automorphisms, and a search among laws without constant
  tuples.
- **Interest:** 2/3.
- **Execution:** deferred to the owner.
