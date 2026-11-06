# Independent review of the twisted-triple-product proofs

Ticket `COPRIME-CLASS2-20261026-001A`, 2026-10-26. Documentation, not a proof.

## What was reviewed and how

**The target.**
- The realization and hardness proofs of `TRIPLE-PRODUCT-20261026-001`:
  - C, Borromean insertions steer the twisted triple product;
  - D, counting maps to UT₃(F₄) ⋊ C₃ is #P-hard with H₁ = Z/3.
- A, the counting formula, was read for context.
- The owner asked for this review before the next epic ("Yes, let's continue" to "first an independent review of C and D plus a last
  prior-art pass under TQFT names").

**Three independent passes.** Each was run by a separate agent with a fresh context.
1. **A mathematical referee.**
   - It read the primary sources: Massuyeau §2–3, Habiro (math/0001185), Jaeger–Vertigan–Welsh 1990, Samperton–Weiß v2 and
     Galindo v2.
   - It re-ran the repository checks read-only.
   - It wrote its own presentation and obstruction code and tested 87 further insertion cases. Its code and logs are archived in
     `math_review/`.
2. **A computational replay.**
   - All code was written from scratch in standard-library Python, without reading the repository's library until its own numbers
     existed.
   - It is archived in `replay/`: run `python3 run_replay.py` there (about 120 s).
3. **A prior-art pass in TQFT phrasing.** A follow-up located Rowell's original conjecture.

**What was reconciled here.** Key quotes were checked against the primary texts in this task:
- Massuyeau's Lemma 3.2;
- Kuperberg–Samperton §5.3;
- Rowell's Conjecture 3.2;
- Moussard's Proposition 2.5.

## Verdict

**No blocking gap.** The chain A → C → D is correct, and the main claim stands: counting maps to UT₃(F₄) ⋊ C₃ is #P-hard on
3-surgeries of knots.
- **Two repairs are needed before the result is presented as proved.**
  - R1: the explicit knot construction in D is a sketch.
  - R2: one novelty sentence overclaims.
- **There are nine minor clarifications.**
- **TRIPLE-PRODUCT-20261026-001 is closed**, and its artifacts are immutable. So the corrections are recorded below and carried out in
  `COPRIME-CLASS2-20261026-001B` and `COPRIME-CLASS2-20261026-001D`, whose arguments cover the same steps. Whether to re-issue
  corrected versions of the closed proofs is the owner's call.

## Findings and resolutions

| # | Severity | Location | Finding | Resolution |
| --- | --- | --- | --- | --- |
| R1a | needs repair | D §3 | "A band core linking K₀ a multiple of 3 times" is undefined, since an arc has no linking number. The correct condition is ψ ≡ 0 mod r on the closed loop: reference path of γ_u, then the band core, then the reference path of γ_v back. It matters: unbalanced gains change the count (45162496 against 31554496). | Stated this way in `COPRIME-CLASS2-20261026-001D` §3, together with the winding fix that achieves it. |
| R1b | needs repair | D §3 | The trivial leaf must carry the framing induced by its disk (Habiro's disk-leaf). With framing ±1 relative to the disk, the clasper is not trivial. | Hypothesis added (D §3, B §3). |
| R1c | needs repair | D §3, "Size" | Dragging parallel copies of bands and edges through successive surgeries can compound sizes. | Take each Y-graph, with its leaf disks, disjoint from every other one. Leaf functionals are evaluated in M, so nothing changes, and the m surgeries become disjoint tangle replacements with O(m(n + m)) crossings (D §3). |
| R1d | write-up and checks | D checks | The end-to-end instances use insertions found by search, not the general recipe. The rank certificates are sound: ranks (3,3,3; 6,6,6; 8) force w₁ + w₂ + w₃ = 0 with every wᵢ ≠ 0, which is the balanced triangle (an unbalanced one has total rank 9), and (3,3; 5) forces the digon. | Recorded as a limit in D's scope. The steering law is tested on many leaf types: 894 replay configurations, plus 87 referee cases with unequal bundles (3, 3, 6), conjugated and non-adjacent bundles, mirrored and inverted Borromean braids, and up to four intertwined insertions. |
| R2 | needs repair | D Novelty; A "gives the twisted setting's form" | Samperton–Weiß's Theorem 3.3.2 assumes \|H²(N, A)\| < C; footnote 11 asks whether that holds when twisted. In D's instances the twisted H²(M; F₄_ω) ≅ F₄^{n+2m} is unbounded, and with bounded twisted H² the count is trivially polynomial by A's formula. So D shows that bounded H₁ is not enough, not that the twisted case of their theorem fails. | Reworded in `COPRIME-CLASS2-20261026-001D` and in this epic's notes. |
| m1 | clarify | C Corollary 4 | Cite Habiro Prop. 3.3 ("every admissible tree clasper for a link in a 3-manifold is tame") and Prop. 3.4 (a trivial disk-leaf makes the clasper equivalent to γ); with K present the disk-leaf is not "trivial" in Habiro's sense, so the argument forgets K. Add the disk-framing hypothesis. Explain why the coefficient stays 3: the diffeomorphism is the identity near a meridian, so the Seifert longitude is preserved. | `COPRIME-CLASS2-20261026-001B` §3. |
| m2 | clarify | C §1, Theorem 2(a) | The cover over the regular neighbourhood N(Γ) is trivial because ψ vanishes on ∂N and H₁(∂N) → H₁(N) is onto, for both handlebodies. The same fact gives existence, not only injectivity, of the cocycle extensions. The ker ψ hypothesis is essential: in the referee's control, leaves with ψ = 2 dropped dim V from 6 to 4. | B §3. |
| m3 | clarify | C | A leaf functional needs a path from the base point to the vertex. The common factor χ₁χ₂χ₃(g) = 1 cancels in the determinant. | B §3. |
| m4 | typo | C §5 | "x_j x_o = x_i x_o" should read x_o x_j = x_i x_o. | Corrected in B. |
| m5 | clarify | D Lemma 6 | As written, the lemma needs q to be a power of 2: it uses χ = (−1)^tr and x_u + x_v. | The odd-p version, with e_p and x_u − x_v, is in `COPRIME-CLASS2-20261026-001D`. |
| m6 | clarify | D | "One oracle call" holds for the step from Z(64, 15) to the homomorphism count. Jaeger–Vertigan–Welsh's hardness of the Tutte point itself uses interpolation, a Turing reduction with many calls. | Worded this way in D. |
| m7 | clarify | C "What it says" | That the realizable forms are exactly T₀ + (alternating forms), and that the non-alternating part is a twisted Bockstein governed by the linking pairing, are interpretations. Only the inclusion ⊇ is proved. | Labelled as interpretation in B. |
| m8 | clarify | D §3 (c) | The Hantzsche–Wendt remark is heuristic. The relevant cover is +1-surgery on the lifted knot, not Σ₃(4₁) itself. | Noted. |
| m9 | code | `tp_lib.insert_at` | It assigns wrong tops when two insertions share a level. The repository checks never do this. | Noted. The new library `cp_lib.insert_at` has the same restriction, and its callers keep levels distinct. |

**Verified by the referee in primary sources:**
- Massuyeau's Lemma 3.2 for any n ≥ 0. Its proof works for any coefficient ring and applies to the closed, connected cover; the lifts
  compose through the common complement.
- The eigenspace step (ε^{3k} det = det, three terms giving 3 det = det in characteristic 2).
- Surjectivity of the leaf functionals.
- The algebra of Lemma 6, with the Fortuin–Kasteleyn/Tutte conversion.
- (79/15, 16) on (x − 1)(y − 1) = 64: #P-hard by Jaeger–Vertigan–Welsh's Theorem 2 and (5.11), and not one of the special points.
- D's base: V = F₄^d and T₀ = 0 by Mayer–Vietoris, and the band-loop functional c(x_a) + c(x_b).
- The conventions of the checks:
  - H²(π) → H²(M) → H² of the presentation complex is injective;
  - the longitude is Seifert-framed, tested on S₅ representations of five knots.
## Independent computational replay

**Setup.**
- Code was written from scratch in standard-library Python, by a separate agent that did not read `tp_lib.py` until it had its own
  numbers.
- It is archived here as `replay/`, with driver `run_replay.py` and outputs `results.json` and `run_log.txt`. It runs in about 120 s.

**Results.**

| Claim | Replayed | Result |
| --- | --- | --- |
| \|Hom\| = 1 + 128 · 4^d · 𝒩 on 3₁, 4₁, 5₂, 8₁₈, 3₁ # 3₁ | brute force over all homomorphisms | 3585, 8193, 129, 229377, 100353: exact |
| (4₁)^{#k}: d = k and T = 0 | k = 1, …, 10; brute force for k ≤ 3 | exact |
| End-to-end triangle (two knots) and digon | own presentation (closed-braid, not Wirtinger) | 45162496, 45162496, 326656: exact, for both crossing chiralities and both characters |
| Steering law | 894 new configurations on (4₁)^{#5, #6, #7}: all single insertions, all pairs and triples of the 24 nontrivial ones, 150 random | 407 nontrivial, 0 failures |
| Gadget lemma | K₂, P₃, K₃, the double edge, two disjoint edges, K₁,₃ | exact (5056, 1597696, 45162496, 326656, 25563136, 504871936) |

**Two observations.**
- **The convention must be stated.** The leaf product x_{q+2} x_{q+1} x_q is right for the crossing relation
  x_out = x_over^{−s} x_in x_over^{s}, which `TRIPLE-PRODUCT-20261026-001C` §5 states and `tp_lib.py` uses. With the opposite
  relation, the reversed product holds instead (120 of 120 configurations each way). This is a convention, not an error. Claims 1–3
  and 5 do not depend on it.
- **The surgery relation is automatic for this G.**
  - Elements of N·h have order 3.
  - ρ(λ) ∈ ρ(π″) ⊆ G″ = Z(N), and ρ(μ) acts on Z(N) without fixed points, so ρ(λ) = 1.
  - Hence |Hom(π₁(S³ ∖ K), G)| = |Hom(π₁ S³₃(K), G)| + 63 for every knot: the 63 extra maps send π into the 2-group N
    nontrivially. This was confirmed on four knots.
  - So the hardness of `TRIPLE-PRODUCT-20261026-001D` holds verbatim for knot groups.

## Prior art: the TQFT-phrased pass

**No preemption** of bounded-homology hardness for solvable targets, nor of the eigencharacter criterion. Read in full text:

- **Kuperberg and Samperton**, Geom. Topol. 22 (2018), §5.3: "Rowell [47] more precisely conjectured that #H(M, G) can be computed
  in polynomial time for any link complement M and any finite, solvable G. We are much less confident that this more precise
  conjecture is true." Their Fig. 3 marks solvable and nilpotent targets "?".
- **Rowell**, "Two paradigms for topological quantum computation", Contemp. Math. 482 (2009), arXiv:0803.1258, §3.3.5:
  "Conjecture 3.2. Let G be a finite group and L a link. (a) There exists an FPRAS for computing H_L(G) for any group G. (b) Suppose
  G is solvable. Then there is a polynomial algorithm for exact computation of H_L(G)." Here H_L(G) = |Hom(π₁(S³ ∖ L), G)| (§2).
- **Moussard**, "Equivariant triple intersections", Ann. Fac. Sci. Toulouse (2017), arXiv:1403.0446.
  - Proposition 2.5: for a Y-graph null in M ∖ K, lifted to the infinite cyclic cover, the equivariant triple intersection map
    changes by Σ_{σ∈S₃} ε(σ) Π_j δ(t_j) b(β_j, [γ_{σ(j)}])(t_j).
  - Theorem 2.7 describes all realized maps as Λ³A modulo relations.
  - This is the rational, infinite-cyclic precursor of our steering formula. Ours has finite cyclic covers, F_q coefficients, and
    leaves required only to lie in ker ψ: a bundle leaf links K three times, so it is not null.
- **Maria and Spreer**, FoCM 2020, arXiv:1607.02218. TV₄ in O(2^{β₁(T; Z₂)} n³), polynomial "for … 3-manifolds with first homology
  group of bounded rank".
- **Delaney and McPhail-Snyder**, arXiv:2608.02795 (August 2026). Turing equivalences between A-manifold invariants; no hardness, no
  homology bounds.
- **Krovi and Russell**, CMP 2015: D(A_n) invariants are #P-hard to evaluate exactly, citing Rowell; A_n is not solvable.
- **de Wild Propitius** (thesis, 1995): the duality between type-III cocycles and D₄ gauge theory; no complexity content.
- **Chlopecki and Samperton:** still not public.

## Consequence for Rowell's conjecture (decision for the owner on how to present it)

- **S₄.**
  - `BOUNDED-H1-20261025-001A` proves #P-hardness of counting S₄ colourings of knots.
  - `SL23-BOUNDED-20261025-001B` gives |Hom(π, S₄)| = 4 + R + 2T (Livingston) for knot groups.
  - S₄ is solvable, so Conjecture 3.2(b) fails for G = S₄ unless every #P function is computable in polynomial time.
- **UT₃(F₄) ⋊ C₃.** The same holds, by the +63 identity above.
- **Heisenberg groups.** It also holds for every H(F_p) ⋊ C_r with a hard pair, by `COPRIME-CLASS2-20261026-001D` Corollary 5 (knot
  groups).
- **Is it new?** No earlier refutation, proof or partial result was found for any nonabelian solvable G on links:
  - Kuperberg–Samperton call it open and doubtful;
  - Delaney–Maria–Samperton (2023) list solvable targets as unknown;
  - the pass searched 2009–2026.
- **The positive side** (also ours): abelian-by-nilpotent targets (`BOUNDED-H1-20261025-001B`) and coprime class-2 targets without a
  hard pair (`COPRIME-CLASS2-20261026-001C`) are polynomial on knots, as the conjecture predicts.

## What this changes for the epic

- **The epic proceeds.** There is no blocking gap, and the stop rule is not triggered.
- **The repairs carry into the new proofs.**
  - `COPRIME-CLASS2-20261026-001B` (steering) gets m1–m4 and m7, and cites Moussard as the rational, infinite-cyclic precursor.
  - `COPRIME-CLASS2-20261026-001D` (hardness) writes the construction out explicitly (R1a–c) and uses the corrected novelty wording
    (R2, m6).
- **Novelty labels for the closed epic, as corrected by this review:**
  - TRIPLE-PRODUCT C (steering): from "candidate new (twisted version)" to "finite-cover, F_q analogue of Moussard's equivariant
    formula". Folklore risk medium to high.
  - TRIPLE-PRODUCT D (hardness): the bounded-homology hardness stands as candidate new. The phrase "answers Samperton–Weiß's twisted
    question negatively" is withdrawn in favour of "bounded H₁ is not enough".
- **The conjecture.** The S₄ and UT₃(F₄) ⋊ C₃ consequences for Rowell's Conjecture 3.2(b) belong in the next decision note. How to
  present them is the owner's call.
