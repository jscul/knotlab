# The knot's coupling: decision at closure

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a three-regular contradiction; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `KNOT-COUPLING-20261031-001`, closed 2026-10-31. Program: complexity.

## The request

The scan `NEXT-DIRECTION-SCAN-20261031-001` recommended a coupling dichotomy in the knot's class (3/3). The owner approved it ("Yes,
let's continue"). The question was whether counting on the knot's contradictions is easy only at the knot's own law.

- **The knot's contradictions.** Connected cubic triple systems that are not 2-colourable.
- **The count.** M(H; λ) weighs each monochromatic line by λ. Not-all-equal, the knot's law, is λ = 0.

## What changed on the way

- **A cheaper route.** The scan proposed building a crossing from deep junctions. Planning found a cheaper route, which was taken. A knot's
  space minus one incidence, used as an edge gadget (an *atom*), is an exact negation at the knot's law. Away from it, the atom shifts the
  coupling, so the hard twisted systems of the counting arc can be simulated by interpolation.
- **A fifth easy coupling.** λ = −3 (u = ∞), the dimer law. There every line uses exactly two of its incidences, so the count is
  (−2)ⁿ times the number of perfect matchings of the incidence graph, a determinant on the knot's contradictions.
- **A correction to the scan.** Its lane B missed this point. Its deep-branch junctions also satisfy the matchgate identity at u = ∞.
  The correction is recorded in ticket A (Correction 9). The scan's artifacts are left unchanged.

## Results

| # | Result | Status | Evidence |
| --- | --- | --- | --- |
| 1 | The atom's edge function is [[α, β], [β, α]], with α = M(H)/2 and β = M(H with the incidence negated)/2. Chains multiply the paths through the edge by ρ^k, ρ = (α − β)/(α + β). At λ = 0 an atom is an exact negation, so odd chains on a Pfaffian negation set give knot's contradictions. | proved | A |
| 2 | Exact ratios for the Fano piece and the three incidence classes of the 13-point splice: ρ = −1 at λ = 0, degenerate at λ = ±1 and ∞, ρ = 2 at λ = −3. Every real degeneracy of one atom is covered by another, and the ratios are multiplicatively independent. | proved (exact computation) | A |
| 3 | At λ = −3 every plain cubic system has M = (−2)ⁿ #PM of its incidence graph: a determinant on the knot's contradictions, a permanent (#P-complete) in general. | proved (restates Seymour, RST and Kasteleyn) | A |
| 4 | **Theorem (the coupling dichotomy).** Counting on the knot's contradictions is polynomial exactly at λ ∈ {0, 1, −1, −3, ∞} and #P-hard at every other complex λ. | proved | B (real λ, and hardness from one good atom), C (complex λ) |
| 5 | With one line deleted (deficiency one) the same holds, except that λ = −3 is open. There the count is 2ⁿ Σ_p #PM(B − N[L] − N[p]), whose subgraphs are not Pfaffian-faithful. | proved / open | B, C |
| 6 | End to end: colouring counts of three plain Pfaffian systems (one non-planar, 30 colourings) recovered exactly from counts of knot's contradictions of up to 9629 lines. This covers real, negative and complex couplings, two atom types, and deficiency one, all with a counter independent of ticket A. | checked | B |
| 7 | The curve of the Fano and splice ratios has exactly the torsion points (1, 1) and (−1, −1), reached at λ = ∞ and λ = 0 (Beukers–Smyth). | proved (exact computation) | C |

## Reading

- **On the knot's contradictions exactly two non-trivial laws are easy.**
  - The knot's own law (λ = 0). Every count is 0, and with one line deleted it is a product of determinants.
  - The dimer law (λ = −3). The count is a determinant.
- **One structure behind both.** The knot's contradictions are the cubic systems whose incidence matrix is sign-nonsingular (Pfaffian with the
  empty signing). The dictionary gives the vanishing; Kasteleyn gives the determinant.
- **Everything else is as hard as on general systems.**
- **The mechanism is native.** At its own law the knot's atom is exactly a negation, so it cannot move the coupling. Everywhere else it
  can, and a movable coupling makes counting universal.
- **In the owner's words.** Both easy laws are cancellations: complete cancellation (the count vanishes) and the cancellation of signs
  between permutations (a determinant).

## Literature (brief check, 2026-10-31)

- **General 3-regular bipartite instances.** Counting Holant(f | =3) is classified by Fan and Cai for nonnegative f (arXiv 2011.09110) and
  extended to rational-valued f (arXiv 2110.01173). Those are dichotomies over all cubic systems, not the non-2-colourable ones.
- **Planar classifications.** Cai, Lu and Xia (arXiv 1008.0683); Cai and Fu (arXiv 1603.07046); Cai, Fu, Guo and Williams (arXiv
  1505.02993). Turner relaxes planarity of Pfaffian circuits up to one crossing (arXiv 1510.01541).
- **Classical ingredients.** The dimer point is Seymour (1974), Robertson–Seymour–Thomas (1999), Kasteleyn and Dagum–Luby (1992).
- **What was not found.** No dichotomy restricted to Pfaffian graphs or to non-2-colourable systems. Folklore risk: moderate. Every tool
  is classical, and the class and its two singled-out laws appear new.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the coupling dichotomy on the knot's contradictions | **Status:** Successful | Complete over ℂ for full systems. Deficiency one is complete except λ = −3. Checked end to end with an independent counter. |
| Local direction — counting on the knot's contradictions | Practically complete | Open: deficiency one at the dimer law, and approximate counting. Neither is likely to change the picture. |
| Broader exploration — the two/three boundary | Known alternatives | (a) mutual selection across the knot catalogue (below); (b) folding the dichotomy into the counting note; (c) deficiency one at λ = −3. |
| Long-term goal — the two/three boundary as emergence | Capability gained | The knot's contradictions select their own law natively: only the knot's law and its Kasteleyn partner, the dimer law, count easily there. Missing bridge: whether this mutual selection is special to the knot. |
| Next recommendation — mutual selection across the knot catalogue | **Next step:** Research directions. A bounded scan over the program's three-place laws (1-in-3 and 2-in-3, parity, signed not-all-equal, the topological knots). For each, ask whether its unsolvable cubic systems form a polynomially recognisable class, and which couplings that class makes easy. | It decides whether "a space selects its law" is a property of the knot alone (the two/three boundary) or of many laws. First discriminator: the decision complexity of 1-in-3 on cubic systems. Stop when each law is classified or shown to fall under a known decision dichotomy. |
| Interest — that recommendation | **2/3 — Promising** | A positive answer would make the knot's law distinguished by mutual selection. The main uncertainty: much of the decision side may be classical (bounded-degree Boolean constraint dichotomies), which would leave only the counting side new. |
| Execution — that action | Planned; awaits the owner | Alternative (2/3): fold the dichotomy into the counting note as a sixth theorem with replay. Sharing the note remains the owner's decision. |

**Recommendation.** **Research directions** (2/3): a bounded scan of mutual selection across the knot catalogue.

**Alternative.** Fold the dichotomy into the counting note (2/3).
