# Closure of the knot-loops epic

Status: Proved

Epic `KNOT-LOOPS-20261019-001` was closed on 2026-10-19, after its three
tickets ended. This is a ledger: one line per conclusion, with its novelty
label and evidence. It makes no new claim. The decision note is
`research/KNOT-LOOPS-20261019-001/loops.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Under the forgetting reading, each transfer of a knot link (witness in, witness out, any number of middle distinctions) is a permutation or misses at most one pair. A ring of links excludes a middle pattern exactly when every transfer along it is a permutation and an odd number of them swap, also for mixed rings. | known-overlap-likely (transfer matrices; Z/2 holonomy) | `KNOT-LOOPS-20261019-001B-P001` (Lean) |
| 2 | Patterns that differ in one middle distinction are never both excluded, so a ring composes into a knot or into nothing. This extends the one-shared-distinction composition of `KNOT-FOUNDATION-20261019-001D` to closed loops. | known-overlap-likely | `…001B-P001` (Lean) |
| 3 | A knot link has only permutation transfers exactly when it is a parity relation. A ring of k copies of one link excludes something exactly when the link has a swap transfer and either k is odd or it also has an identity transfer. Only parity keeps half the patterns, one full bit, at every length; the excluded count is ((S+I)^k − (I−S)^k)/2. | known-overlap-likely; the counting step is prose plus census | `…001B-P001`; `…001A-E001` |
| 4 | The census's frozen prediction P3 (constrained at every length only for parity) is false: 1,224 four-variable placements keep an exponentially fading constraint at every length. Every other check passes exactly on 9,108 ring placements, 82,824 mixed rings and 816 chains. | finite evidence | `KNOT-LOOPS-20261019-001A-E001` (exploratory, refuted as frozen) |
| 5 | Parity networks remember one bit per independent loop of the network (1, 3, 2, 4, 4 and 4 bits on six graphs). Other knots remember at most 0.85 bits, and only where implication-like transfers can chain. Abelian Z₃ links keep log₂3 bits at every length; S₃ links keep log₂(3/2) bits and depend on the order of the loop; sampled three-valued knots without permutation transfers forget by length 7. | finite evidence; parity networks classical (cycle space) | `KNOT-LOOPS-20261019-001C-E001` (exploratory) |

## Position and next action

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: which knots remember a loop | **Status:** Successful | Rings settled in Lean; networks and many-valued links explored. |
| Local direction: rings and networks of Boolean knots | Practically exhausted for rings | Network memory without groups is small, depends on orientation, and is classical 2-SAT frustration. |
| Broader exploration: knots, holes and loops | Known alternatives | Not yet explored: non-abelian contact on networks; holes as local-to-global cohomology. |
| Long-term goal: native structure from knots | Obstruction learned | A lasting record of loops needs group-like contact. |
| Next recommendation: holes as cohomology | **Next step:** Continue in a fresh epic. Show that a network's composite is the H¹ obstruction of its contact group, then compare with cohomological k-consistency. | Bridges to contextuality and constraint-satisfaction literature. |
| Interest | **2/3 — Promising** | Main uncertainty: the abelian case is classical, and the non-abelian one may be too. |
| Execution | Not started | Needs the owner's go-ahead. |
