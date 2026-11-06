# Closure of the class-4 pairs epic

Status: Proved

Epic `CLASS4-PAIRS-20261028-001` closed on 2026-10-28.
- **What this is.** A ledger: one line per conclusion, with its novelty label and evidence. It makes no new claim.
- **The decision note** is `research/CLASS4-PAIRS-20261028-001/class4_pairs.md`. It holds the outcome, the steps, the probes after
  the frozen run, the challenged assumptions, the literature, the gaps and the end-of-epic assessment.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Linear flows (Theorem 8). A class-3 edge failing only the vertex-root condition, whose dual slot has no layer-1 data, gives #P-hardness: the flow and the dual slot's constraints are linear in that slot's data, so the Fourier dual counts solutions of linear equations. Decides 8 more census algebras and, with Theorem 6, the whole vertex-root family; 105 of 850 stay open. | Candidate new; folklore risk medium | `CLASS4-PAIRS-20261028-001A-P001` |
| 2 | Class-4 gadget counts are local up to relabeling. For fixed lower data the degree-4 system is affine in the degree-3 data; the global and assembled local systems have equal linear parts, and their constant parts differ by an element of the column space. Three algebras, seven shapes up to K₄, 63 configurations; the cumulative design fails. | Experimental support | `CLASS4-PAIRS-20261028-001B-E001` (supported) |
| 3 | Theorem 7, an implication: locality up to relabeling (L4), linear flows on single edges (LS) and the rank witness (RW) give #P-hardness, through a Fourier dual with independent potentials at the two ends of an edge. Corollary 7.1: (LS) and (RW) hold for six census algebras, which are hard if (L4) holds. | Candidate new, conditional; folklore risk medium | `CLASS4-PAIRS-20261028-001C-P001` |

## Challenged assumptions

The decision note records these:
- **Class-4 gadgets leak across the graph.** Only in coordinates: counts are local up to relabeling in every clean configuration
  tested.
- **Flows must vanish off the diagonal.** No: linearity in the dual slot's data makes the dual non-negative.
- **Vertex flows must be conserved.** No: independent potentials at the two ends work.
- **A canonical gauge makes equation values comparable.** No: junction twists relabel degree-3 data of other edges in any gauge.

## Remaining gaps

1. (L4) on all graphs: an absorption lemma for junction twists, that is, locality of the degree-4 obstruction modulo its
   indeterminacy. Every clean edge at d = 5 is consistent with it; every non-clean edge probed breaks locality.
2. The 105 open census algebras (6 decided if (L4) holds): 26 of class 3 ((B₀) with (V₃); (B₂′) at a nonzero character); 79 of
   class 4 (the other twenty (K)-only algebras at d = 7, 9; 53 others, among them the cross-layer algebra).
3. Class at least 5; non-graded algebras; p = 2, 3. The census covers free algebras on at most three generators with d ≤ 12.
4. Cited, not reproved: Bulatov–Grohe via Cai–Chen–Lu, Lemma I, the predecessor's summand, steering and Brunnian lemmas.
5. No human or external review.

## Recommendation

**Continue, with a fresh epic proving (L4).**
- **Method:** an additivity argument after Krushkal (μ̄-invariants of band sums, modulo indeterminacy), with an absorption lemma
  for junction twists.
- **First discriminator.** The explicit relabeling on the star K₁,₃ for free class 4 on (1, 1), where three twists meet one
  vertex.
- **Interest:** 2/3.
- **Alternative:** the class-3 (B₀) and (B₂′) families.
- **Execution:** deferred to the owner.
