# S4 counting on closed manifolds with bounded first homology

Epic `CLOSED-H1-20261025-001`, closed 2026-10-25.

## The question

The owner approved the recommendation made at the close of `BOUNDED-H1-20261025-001`; the go-ahead was relayed by a peer session.
- **The question.** Does the S₄ knot hardness extend to closed 3-manifolds with bounded first homology? The first test was longitude
  values, the other meridian classes, and surgery on the tripled knots.
- **A mid-epic redirection.** The owner, through Codex, asked for two things before any closed-manifold claim:
  - an independent replay of the knot hardness;
  - a comparison with the closest literature.

  Both were done first.

**Intuitions this epic targets.**
- **The complexity side of the thesis.** Where the easy/hard line sits once homology is bounded.
- **Patterns of patterns.** S₄ has an S₃ level and a V₄ level.
- **Everything is relational.** The counts are fixed by what the boundary torus can see.

**The evidence:**
- [Independent replay of the S4 knot hardness](../../proofs/CLOSED-H1-20261025-001A/CLOSED-H1-20261025-001A-P001_independent_replay_of_the_s4_knot_hardness/proof.md)
  (A, proof and V1 replay);
- [The two connected quandles of order 6 colour every knot equally](../../proofs/CLOSED-H1-20261025-001B/CLOSED-H1-20261025-001B-P001_two_connected_quandles_of_order_6_colour_every_knot_equally/proof.md)
  (B, proof);
- [S4 counting is #P-hard on closed manifolds with first homology Z/2](../../proofs/CLOSED-H1-20261025-001C/CLOSED-H1-20261025-001C-P001_s4_counting_is_sharp_p_hard_on_closed_manifolds_with_h1_z2/proof.md)
  (C, proof);
- [bounded scan](scan.md);
- scoping, which is scratch and not evidence.

## Outcome in one paragraph

**S₄ counting is #P-hard on closed 3-manifolds with H₁ = Z/2. On the way, a 2013 quandle conjecture fell.**
- **The replay.** An independent code path confirms the knot hardness of `BOUNDED-H1-20261025-001A`, and an audit of its proof finds no
  gap (A).
- **The peripheral data are rigid (B).**
  - A transposition colouring always has trivial longitude. The lift to GL(2, 3) would otherwise make two commuting elements
    anticommute.
  - The boundary torus sees exactly half of the twisted lifting cohomology (half-lives-half-dies). So over every S₃ colouring,
    transposition lifts and 4-cycle lifts are equinumerous.
  - Hence the two connected quandles of order 6 colour every knot equally. Clark, Elhamdadi, Hou, Saito and Yeatman conjectured this
    in 2013 after checking 2,977 knots. Every 3-colourable knot also has a non-trivial C[6,2] colouring, as Carter, Oshiro and Saito
    conjectured in 2009.
- **Closed counts (C).**
  - Surgery with coefficient p keeps the colourings whose meridian and longitude satisfy μ^p λ = 1.
  - With the peripheral data fixed, C₂ + C₄ = 8 + 3T for every knot. Using a connected sum with the trefoil instead,
    3·C₂(K) + C₂(K # 3₁) = 16 + 12T, which uses only manifolds with H₁ = Z/2.
  - So two queries recover the #P-hard transposition count.
- **The contrast.** Abelian-by-nilpotent targets (all metabelian groups) are polynomial there (`BOUNDED-H1-20261025-001B`).

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Peripheral statistics of 10 small knots and the tripled knots | No transposition colouring with longitude z, and #4-cycle = #transposition colourings everywhere | Scratch |
| Trefoil surgeries as convention tests | S³₂(3₁) gives 58 = Hom(binary octahedral, S₄); S³₆(3₁) gives 90 = 10 × 9 | Proved (C, check part 1) |
| Lift to SU(2) or GL(2, 3) | Lifts of t and z anticommute, so the longitude is never z | Proved (B(a)); known technique (Johnson–Livingston) |
| Half-lives-half-dies with the self-dual module V₄ | The boundary image is a line; with (a) it is a graph over the meridian | Proved (B(b)) |
| Literature, on the owner's steer | The equal-count statement is the open 2013 conjecture | Scan |
| Independent replay | 19 diagrams, 16 bicycle-law graphs, 6 links, 4 gadget knots, 3 interpolations, all matching | Proved (A) |
| Surgery identities | Exact on 13 knots by brute force over all S₄ maps of the closed groups | Proved (C) |

## What was proved

| Result | Content |
| --- | --- |
| A | V1 replay of `BOUNDED-H1-20261025-001A`: diagrams, bicycle law, Potts identity, gadget knots, interpolation. No gap in the written proof. |
| B | For every knot: transposition longitudes are trivial; over every S₃ colouring the lifts for a fixed transposition and for a fixed 4-cycle meridian are equinumerous, and the 4-cycle lifts share one longitude. So C[6,1] and C[6,2] colour every knot equally (2013 conjecture), and 3-colourable knots are non-trivially C[6,2]-colourable (2009 conjecture). |
| C | C₂ + C₄ = 8 + 3T and 3·C₂(K) + C₂(K # 3₁) = 16 + 12T for every knot. So S₄ counting is #P-hard on closed manifolds with H₁ = Z/2 (two queries per knot). |

## Observed, not proved

**The 4-cycle longitude is c^{2h}, where 2^h is the number of transposition lifts over the S₃ colouring with a fixed meridian.**
- This held on all 230 S₃ colourings of the 27 knots in B's check (scratch).
- If it holds in general, a single surgery would carry the count: C₂ = 4 + 3(3·S(2) − S(−2)), with S(x) = Σ_φ x^{h(φ)}. It would then
  remain to show that this combination is #P-hard.
- It looks like a quadratic refinement, an Arf invariant of the lifting cohomology.

## What this changes

- **For the complexity side of the thesis.**
  - The bounded-homology line now has both sides on closed manifolds. Metabelian (abelian-by-nilpotent) targets are polynomial, and S₄
    is #P-hard, with H₁ as small as Z/2.
  - Homology spheres cannot carry this: a solvable target sees only the trivial map.
  - The open middle is the solvable groups that are not abelian-by-nilpotent but have Fitting height 2, such as SL(2, 3).
- **For the knot reading.**
  - The longitude, the loop that bounds the knot's surface, cannot carry the second-level bit of a transposition colouring. Its lift
    would have to anticommute with the meridian it commutes with.
  - The boundary torus sees half of what the inside can do. That half is all the counting needs.
- **A relational reading.**
  - The equality of the two quandles' counts says nothing about either quandle alone.
  - It is a statement about how a knot's interior relates to its boundary: a Lagrangian that is a graph over the meridian.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Closing up needs gluing gadgets that control 4-cycle colourings | `BOUNDED-H1-20261025-001` recommendation | **Unnecessary.** The 4-cycle colourings are already as many as the transposition ones, so plain surgery suffices. |
| A search for transposition colourings with longitude z might find one | This epic's scoping | **Impossible**, by the GL(2, 3) lift. The search was stopped. |
| The equal-count property of the order-6 quandles is only empirical | Clark et al., Remark 6.6 | **Proved** for classical knots. The virtual counterexample shows why 3-manifold topology is needed. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A, replay | Requested by the owner via Codex | Verification, V1 |
| B(a), trivial transposition longitudes | Peripheral obstruction through a central extension | Folklore risk high (Johnson–Livingston theory) |
| B(b–c), equal lifts and the 2013 conjecture | Half-lives-half-dies for the twisted lifting cohomology, found by reading the closed counts | `candidate-local-delta`. The conjecture is restated as open by Clark, Elhamdadi, Saito and Yeatman (JKTR 2014, §5). No later proof was found in the bounded scan. Overlap risk medium (Ishikawa 2025, abstract only). |
| C, closed hardness | Surgery bookkeeping on top of A and B | `candidate-local-delta`. No bounded-homology hardness for a solvable group found. Folklore risk low to medium. |

**Did the perspective do real work?** Partly.
- The decisive steps are standard 3-manifold topology (central extensions, half-lives-half-dies).
- The question came from the knot reading: what the loop bounding the knot's surface carries, and what the boundary sees.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: S₄ on closed manifolds with bounded H₁ | **Status:** Successful | Proved with H₁ = Z/2, after an independent replay of the knot hardness. |
| Local direction: S₄ with bounded homology | Exhausted for the approved question | The remaining S₄ refinement is the single-query version, through the observed parity law. |
| Broader exploration: the bounded-homology dichotomy | Known alternatives | Is SL(2, 3) (Fitting height 2, not abelian-by-nilpotent) polynomial or hard? GL(2, 3)? Approximate counting? |
| Long-term goal: the complexity side of the thesis | Capability gained | Both sides of the bounded-homology line are now proved on closed manifolds. |
| Next recommendation: SL(2, 3) with bounded homology | **Next step:** Research directions | First test: does the quadratic lifting obstruction of SL(2, 3) over A₄ make the count polynomial with bounded H₁, or do knot gadgets make it hard? |
| Interest: that recommendation | **2/3: Promising** | It decides whether the line is "abelian-by-nilpotent" or "Fitting height 2": one sharper statement about pattern levels. |
| Execution | Deferred to the owner | Bound: one epic. Stop if SL(2, 3) splits into cases no single method handles. |

**Alternatives:**
- **A short note (2/3).** The proof of the 2013 conjecture and the closed hardness. Sharing it is the owner's call. Ishikawa's full text
  should be read first.
- **The parity law for 4-cycle longitudes (1/3).** It would give a single-query result and an Arf-invariant reading.
- **The other Galkin pairs of the 2013 conjecture (1/3).** Off the main intuitions.
- **Return to the core intuitions (1/3).**
