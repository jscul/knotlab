# Closure of the hole-criterion colouring epic

Status: Proved

Epic `HOLE-CRITERION-COLOURING-20261019-001` was closed on 2026-10-19, after
both of its tickets ended. This is a ledger: one line per conclusion, with its
novelty label and evidence. It makes no new claim. The decision note is
`research/HOLE-CRITERION-COLOURING-20261019-001/holes_and_colouring.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For every graph on 2 to 5 vertices, the complex of partial proper N-colourings has no reduced GF(2) homology in dimension s−2 once N ≥ 2s−1. Only the complete graphs need that many colours. The vanishing is not monotone in N: C₄ has a hole only at N = 4, and K_{2,3} only at N = 5. | finite evidence; the complete-graph case is Björner, Lovász, Vrećica and Živaljević (1994) | `HOLE-CRITERION-COLOURING-20261019-001A-E001` (exploratory, independently recomputed) |
| 2 | On 13 non-colourable graphs, the Nullstellensatz degree over GF(2) exceeds B_hole, as the cycle-filling argument predicts: by exactly one on 10, and by two on K₅ with 4 colours, the Moser spindle and the Mycielskian of K₄. B_hole equals the universal floor ⌊(N+1)/2⌋ on every graph, so the holes carried no graph-specific information. | finite evidence; the floor is elementary (monotonicity and Braun's moment theorem) | `…001A-E001` |
| 3 | With 3 colours, every non-3-colourable graph has B_hole = 2: it contains an induced three-vertex path or a triangle, and both have a hole. With 4 colours B_hole ≤ 3. So with a fixed number of colours the criterion certifies only constant degree, while Lauria and Nordström give linear degree for some 3-colouring instances. | elementary consequence of exact values in A-E001 | `…001A-E001` |
| 4 | Let ℓ ≥ 32 and n = 2^ℓ. For every m with n < m and 8192·m·ℓ²(2ℓ+5) ≤ n², every DAG-like Res(⊕) refutation of bit PHP with m pigeons has more than exp(n²/(8192·m·ℓ²)) lines. This is checked in Lean against Braun's replayed development. | corollary of Braun's development (arXiv:2609.23015) not stated in the preprint; no earlier DAG-like size bound for weak bit PHP found in a brief search | `HOLE-CRITERION-COLOURING-20261019-001B-P001` |
| 5 | A proper colouring with m classes maps every refutation of the bit encoding of 2^ℓ-colouring a graph, line by line, to a refutation of bit PHP with m pigeons. So conclusion 4 bounds bit-colouring for every graph whose chromatic number lies in that range, and bit-colouring is not a second family for Braun's Theorem 9.1. | standard substitution; corollary | `…001B-P001` |

## Position and next action

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: hole criterion for colouring refutations | **Status:** Successful | The criterion holds on every tested graph. It carries no graph-specific information. The bit-colouring question is settled. |
| Local direction: plain (worst-case) hole criterion | Practically exhausted for colouring; for CNF formulas too, by a prose clash argument | Small cones, paths and triangles, or two clashing clauses, always have holes. |
| Broader exploration: second family for Theorem 9.1 | Searching; one class ruled out | Not assessed: relative or equivariant hole criteria, and other injective constraint families. |
| Long-term goal: Res(⊕) lower bounds beyond bit PHP | Capability gained (modest) | Bounds now cover weak bit PHP and bit-colouring up to chromatic number about n²/(16384 ℓ³). Formulas that do not reduce to bit PHP remain open. |
| Next recommendation: Theorems 1–3 of B-P001 | **Next step:** Continue (conversion). Prepare a two-page statement with the Lean file, which Braun or a Res(⊕) reader could check by running `check.py`. | It answers a question others have studied: Efremenko, Garlík and Itsykson left DAG-like size for weak bit PHP open. |
| Interest: that conversion | **2/3 — Promising** | Machine-checked and apparently unstated. Main uncertainty: experts may see it as an immediate corollary. Not selected, at **1/3 — Exploratory poking**: search for a non-PHP family whose shape is hole-free up to linear size. |
| Execution: that conversion | Deferred | Sharing with Braun is the owner's decision. Stop if the owner declines. |
