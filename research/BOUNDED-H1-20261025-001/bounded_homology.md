# Counting with bounded first homology

Epic `BOUNDED-H1-20261025-001`, closed 2026-10-25.

## The question

The owner approved the recommendation made at the close of `DICHOTOMY-3D-20261025-001`.
- **The question.** Is counting maps into S₄ #P-hard on 3-manifolds with bounded first homology, while every metabelian group stays
  polynomial there?
- **The background.** Galindo's 2026 theorem settles the case where homology may grow: hard exactly for non-abelian groups.

**Intuitions this epic targets.**
- **The complexity side of the thesis.**
- **Patterns of patterns.**
  - A metabelian group has one level of pattern above its abelian quotient.
  - S₄ has two: S₄ → S₃ → Z₂, with V₄ above S₃.

**The evidence:**
- [S4 colourings of knots are #P-hard](../../proofs/BOUNDED-H1-20261025-001A/BOUNDED-H1-20261025-001A-P001_s4_colourings_of_knots_are_sharp_p_hard/proof.md)
  (A, proof);
- [Metabelian targets stay polynomial with bounded homology](../../proofs/BOUNDED-H1-20261025-001B/BOUNDED-H1-20261025-001B-P001_metabelian_targets_stay_polynomial/proof.md)
  (B, proof);
- [bounded scan](scan.md);
- scoping, which is scratch and not evidence.

## Outcome in one paragraph

**With bounded homology, the line moves up one level.**
- **Metabelian groups stay polynomial.** More generally, so does every group with an abelian normal subgroup and a nilpotent quotient
  (B). The maps into the quotient are boundedly many, and the lifts above them are linear algebra.
- **S₄ is #P-hard on knots (A).** Its knot complements have H₁ = Z, so this is hardness with bounded homology.
- **The mechanism is exact.**
  - Draw a plane graph's alternating knot with every edge tripled. A full 3-twist is invisible to S₃, so the S₃ colourings are free
    vertex potentials, 3ⁿ of them.
  - Over each potential, the S₄ lifts number 2 to the number of components of the alternating link of the monochromatic subgraph: the
    bicycle law.
  - The count becomes a twelve-state spin model.
  - With edges subdivided it is exactly the Potts model at q = 12, v = 1/2, which gives hardness for links with one query.
  - Gadgets whose tree and separating-forest counts are odd keep the diagram a knot. With them, interpolation recovers the planar
    chromatic polynomial at 12.
- **Still open.** Closed manifolds with bounded H₁. Surgery or gluing turns knots into closed manifolds, but the longitude values and
  the 4-cycle colourings must be controlled.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Pretzel knots P(3, …, 3) | 5ⁿ + 1 colourings: too structured | Scratch |
| Alternating diagrams with tripled edges | 3-colourings are free potentials; S₄ lifts depend only on where potentials jump | Proved (A, Lemmas 1.1, 2.1) |
| First law: lifts = 2^{c(H)} | Held on small graphs, failed on 8–9 vertex graphs | Scratch, corrected |
| Bicycle law: lifts = 2^{c(H) + dim B(H)} | Exact on more than 170,000 colourings; proved by the twist lemma and left-right cycles | Proved (A, Theorem 1) |
| Subdivided edges | 2^{−n} 4^m Z_Potts(G; 12, 1/2): links, one query | Proved (A, Theorem 2) |
| First guess "no gadget keeps knots and is Potts" | Too strong: knot-keeping gadgets exist with β ≠ 0 | Scratch, corrected |
| Odd tree and forest gadgets plus doubled non-tree edges | Knots; interpolation recovers P(H, 12) | Proved (A, Theorem 3) |
| Abelian-by-nilpotent targets | Polynomial with bounded mod-p homology | Proved (B) |

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1 | Bicycle law: Col(D(G⁽³⁾)) = Σ_φ 2^{c(H_φ) + dim B(H_φ)}, a twelve-state model with edge matrix J − 2N. |
| A, Theorem 2 | Links: Col = 2^{−n}·4^m·Z(G; 12, 1/2). #P-hard with one query. |
| A, Theorem 3 | Knots: counting homomorphisms from knot groups to S₄ that send meridians to transpositions is #P-hard (Turing). |
| B | Abelian-by-nilpotent targets, including every metabelian group, are polynomial with bounded mod-p first homology. This covers knot groups with a meridian class, and closed 3-manifolds with bounded \|H₁\|. |

## What this changes

- **For the complexity side of the thesis.**
  - With growing homology, the line is abelian versus non-abelian (Galindo).
  - With bounded homology, it moves to the second pattern level. One twisted level above a bounded abelian quotient is linear.
  - S₄ is hard because its lifts over an exponential level of patterns (the S₃ colourings) depend on that level, and the dependence is
    non-affine.
  - This is the program's affine/non-affine line applied to patterns of patterns.
- **For the knot reading.**
  - The hard instances are genuine knots, and the hardness lives at the crossings.
  - A twist of three crossings is invisible to the first pattern level and decisive for the second.
  - The bits of the second level run along the left-right cycles of the monochromatic subgraph.
  - The count is a bicycle (cycle-and-cut) structure: knots bound by contacts.
- **A relational reading.** The potentials pair with bit-curves, and the twelve states are (cut side, colour, bit). As in the doubles of
  `HARD-3D-20261025-001`, a colouring is paired with a dual object.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Galindo's theorem leaves no complexity question in 3D counting | `DICHOTOMY-3D-20261025-001` closure | **False.** With bounded homology the line moves, and S₄ is #P-hard there while metabelian groups are not. |
| Only simple groups give hard knot-colouring counts | Kuperberg–Samperton scope | **False.** S₄, which is solvable, is #P-hard on knots and links. |
| No knot-preserving gadget gives a Potts model | This epic's scoping | **Wrong as stated.** Some knot-keeping gadgets have β ≠ 0, and interpolation reaches the chromatic polynomial. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Bicycle law | Medial-link and left-right-cycle structure: the program's knot and contact view | `candidate-local-delta`; no overlap found; folklore risk low to medium |
| Links: Potts(12, 1/2) identity | The bicycle law plus Fourier and subdivision | Same |
| Knots: #P-hardness for S₄ | Gadget algebra plus spanning-tree parity | First solvable group with hard knot colourings, as far as the bounded scan found; folklore risk low to medium |
| Polynomial side | Twisted cohomology in the style of Matei and Suciu | Folklore risk high |

**Did the perspective do real work?** Yes.
- **The objects.** The hard instances are knots read as loops bound at contacts (crossings).
- **The insight.** The deciding insight was a parity structure: bicycles, which are cycles that are also cuts.
- **The source of the theorem.** It came from computing colourings of contact patterns, not from the literature.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: S₄ with bounded homology | **Status:** Partially successful | Knots (H₁ = Z) hard and metabelian groups polynomial, both proved. Closed manifolds with bounded H₁ not yet. |
| Local direction: tripled alternating knots | Continue | The bicycle law and the gadgets give exact control. The closed version needs only the longitude and the other meridian classes. |
| Broader exploration: complexity with restricted topology | Known alternatives | Knots, links and homology spheres (Bridges–Samperton); which solvable groups are hard with bounded homology (SL(2,3) and Fitting height); approximation. |
| Long-term goal: the complexity side of the thesis | Capability gained | The hardness line responds to topology. With bounded homology it sits at the second pattern level, a sharper form of affine/non-affine. |
| Next recommendation: closed manifolds with bounded H₁ | **Next step:** Continue with a fresh epic | First discriminator: on the tripled alternating knots, the longitude values and the 4-cycle colourings, then the count of the closed manifold S³₂(K) (H₁ = Z/2). |
| Interest: that recommendation | **2/3: Promising** | It completes the approved question with an exact construction already in hand. The uncertainty is bookkeeping: if the longitude splits colourings unevenly, other gluings are needed. |
| Execution | Deferred to the owner | Bound: one epic. Stop if no surgery or gluing on these knots isolates the transposition count. |

**Alternatives:**
- **Which solvable groups are hard with bounded homology (2/3).**
  - Fitting height 2 against 3.
  - SL(2,3), whose quadratic obstruction suggests polynomial.
  - GL(2,3), whose quotient by its centre is S₄.
- **A short note on the bicycle law and S₄ knot colourings (2/3).** The first solvable group with hard knot colourings, if it holds up,
  is of real magnitude. Sharing it is the owner's call.
- **Return to the program's core intuitions (1/3).**
