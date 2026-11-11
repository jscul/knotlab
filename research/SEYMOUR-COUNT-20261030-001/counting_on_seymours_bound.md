# Counting on Seymour's bound

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a three-fold space is a three-regular contradiction; a knot space is a three-regular contradiction; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `SEYMOUR-COUNT-20261030-001`, 2026-10-30.

## The question

- **The owner's request (2026-10-30).** "Yes, let's continue." This approved the recommendation of `THREEFOLD-SPINSUM-20261030-001`.
  - The knot's contradictions are the cubic systems on Seymour's bound for minimally non-2-colourable hypergraphs, with as many lines as points.
  - There non-colourability is a determinant condition, and the count with one contact removed is a product of determinant-like
    amplitudes.
  - Is that count polynomial-time on every such system, including non-planar glue? Does it become #P-hard just off the bound?
- **Scoping (not evidence).** A probe found that a trisum's amplitude depends on two numbers per piece, in a not-all-equal form. The epic
  took the easy side. The hard side is left to the recommendation below.
- **Intuitions targeted:**
  - the two/three boundary as emergence, on the counting side;
  - everything is relational: what the knot's pieces pass to one another.

**The evidence:**
- [The trisum law](../../proofs/SEYMOUR-COUNT-20261030-001A/SEYMOUR-COUNT-20261030-001A-P001_the_trisum_law/proof.md) (A, proof with exact
  finite computations);
- [Polynomial counting on Seymour's cubic bound](../../proofs/SEYMOUR-COUNT-20261030-001B/SEYMOUR-COUNT-20261030-001B-P001_polynomial_counting_on_seymours_cubic_bound/proof.md)
  (B, proof with an implementation checked against direct counts).

## Outcome in one paragraph

**The easy side holds: counting is polynomial on every three-regular contradiction.**
- **The knot reappears one level up (A, proved).**
  - Non-planar glue is built by trisums: three non-colourable pieces glued along a square.
  - Each piece's colourings lean to one of the square's two points, in proportions (α, β). The trisum's amplitude is
    ρ₁ρ₂ρ₃ − α₁α₂α₃ − β₁β₂β₃: the knot's not-all-equal rule applied to the pieces' leanings.
  - Pieces glued further down act only as weights on these two numbers.
- **Polynomial counting (B, proved).**
  - #col(H − L) is a product over braces. A planar brace contributes one Berman determinant.
  - Any other brace is split along Robertson–Seymour–Thomas trisectors into planar leaves. Each branch's leaning split is one weighted,
    row-restricted determinant of its leaf, and the trisum law closes the root: two determinants per leaf.
  - No signing is needed. The implementation matches direct counts on 67 braces, on seven three-regular contradictions of 22 to 118 points and on
    trisums to 480 vertices.
  - It counts 1720-vertex instances exactly in seconds, where variable elimination would need factors on 30 variables.
- **The hard side was not attempted.**

## What was proved

| Result | Content |
| --- | --- |
| A, Lemmas 1–2 | Odd square parity: exactly one square line sees c0 = c2; a closed piece's boundary carries exactly its split (support lemma). |
| A, Theorem 3 | The trisum law A(T) = ρ₁ρ₂ρ₃ − α₁α₂α₃ − β₁β₂β₃. |
| A, Propositions 4–5 | The other view of a split is swapped; children act as weights on a piece's two leanings. |
| B, Lemma 1 | Trisum trees: trisectors of cubic Pfaffian braces are independent, on no 4-cycle, with three components. Splitting ends in planar braces, with disjoint squares in a tree. |
| B, Lemma 2 | One Pfaffian sign pattern per square, consistent over all leaves and branch composites. |
| B, Proposition 3, Lemma 4 | A branch's leaning split is |det| of its leaf's weighted, row-restricted line–face matrix (Berman sign coherence with weights). |
| B, Theorem 5 | #col(H − L) in polynomial time on every three-regular contradiction, without any signing; Corollary 6: the knot's factor λ(0) too. |

## Reading

- **Why the knot's contradictions are easy.** Their non-colourability is a determinant condition (sign-nonsingularity), and so is their count with
  one contact removed: one determinant per planar piece.
  - What a piece tells the rest is two numbers per square, how its colourings lean.
  - The pieces combine by the knot's own not-all-equal rule.
- **Topology does not obstruct counting.** The surface's handles are Fano pieces (a factor 5) and trisums (a not-all-equal junction of
  planar pieces).
  - The Kasteleyn route on the surface would need 4^genus Pfaffians. The trisum tree never needs the surface.
- **Provenance and folklore risk.**
  - Planar not-all-equal counting is classical (Valiant's holographic algorithms), and Lemma 4 is immediate from Berman.
  - Robertson–Seymour–Thomas recognize these spaces in polynomial time through the same trisum structure.
  - The counting result on every three-regular contradiction was found in no source. Folklore risk is moderate: a holographic algorithm on a Pfaffian
    matchgrid could reach it, and none was found stated.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — where counting near-critical instances becomes hard | **Status:** Partially successful | The easy side is proved and implemented: #col(H − L) is polynomial on every three-regular contradiction, including non-planar glue. The hard side was not attempted. |
| Local direction — counting on Seymour's bound | Practically exhausted on the bound | The count on the bound is a product of determinants, computed exactly. Further refinements (faster trisector search, recognition) would not change the conclusion. |
| Broader exploration — three-regular contradictions and their counts (question 9) | Known alternatives | Atoms, handles, amplitude, spin structure and counting are mapped. Unmapped: counts off the bound, by sign class or by deficiency. |
| Long-term goal — the two/three boundary as emergence, in counting | Capability gained | The knot's contradictions are now a proved tractable island for counting, explained by determinants. Missing: a hardness side that would make the island a boundary. |
| Next recommendation — counting one twist off the bound | **Next step:** Continue, as a fresh epic. Keep a three-regular contradiction's incidence graph and change its sign class away from the Pfaffian one, which makes the system colourable. Is #col still polynomial for every sign class on these graphs, so that tractability lives in the graph? Or is it #P-hard for some family, so that the knot's non-colourability is itself the boundary? | The cheapest honest version of "just off the bound": same graph, same size, one sign class away. Either answer locates the easy/hard boundary. One flip changes nothing (#col(H with one sign flipped) = #col(H − L)), so the question starts at genuine twists. |
| Interest — that recommendation | **2/3 — Promising** | Planar twisted counts are Valiant-tractable, and general cubic counting is expected to be #P-hard, so the boundary sits somewhere in between. The trisum tree gives a concrete test: a twisted piece's boundary is a 16-entry tensor, not two numbers. Main uncertainty: a hardness proof may need a planar Holant dichotomy argument that the gadgets do not support. |
| Execution — that next action | Deferred to the owner (fresh epic) | First discriminator: the 16-entry boundary tensors of twisted prisms and trisums at a square. Do the tensors that occur close under a matchgate-type rule, giving a polynomial recursion? Test against direct counts on twisted trisum trees. Stop if neither a recursion nor a hardness gadget emerges from these tensors. |

**Recommendation.** **Continue**, as a fresh epic: counting one twist off the bound (2/3). Two alternatives were considered.
- **More lines than points (1/3).** Minimal non-2-colourable systems with deficiency 1 are the unsigned "off the bound". There is no structure
  theory comparable to Robertson–Seymour–Thomas there. Reductions must preserve minimality, and Szeider's fixed-parameter tractability in the
  deficiency suggests bounded deficiency may stay easy.
- **A write-up of the three-fold line with polynomial counting (1/3).** It is coherent, but its folklore risk is moderate. The owner asks
  for write-ups only for results of real magnitude.
