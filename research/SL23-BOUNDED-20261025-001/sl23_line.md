# SL(2,3) with bounded first homology

Epic `SL23-BOUNDED-20261025-001`, closed 2026-10-25.

## The question

The owner approved the recommendation made at the close of `CLOSED-H1-20261025-001`: "Research directions: SL(2,3) with bounded
homology. It is the smallest group that would decide whether the line is 'abelian-by-nilpotent' or 'Fitting height 2'." The answer
was "Yes, continue." In the meantime, at the owner's request relayed by Codex, the prior-art comparison
`S4-LIFT-PRIOR-ART-20261025-001` was finished first. It moved the closed-manifold epic's peripheral identities to Livingston 1995.

**Intuitions this epic targets.**
- **The complexity side of the thesis.** Where the easy/hard line sits with bounded homology.
- **Patterns of patterns.** A central sign layer above an affine layer above a bounded top.

**The evidence:**
- [SL(2,3) counting is polynomial with bounded homology](../../proofs/SL23-BOUNDED-20261025-001A/SL23-BOUNDED-20261025-001A-P001_sl23_counting_is_polynomial_with_bounded_homology/proof.md)
  (A, proof);
- [The double covers of S4 are #P-hard on knots](../../proofs/SL23-BOUNDED-20261025-001B/SL23-BOUNDED-20261025-001B-P001_the_double_covers_of_s4_are_sharp_p_hard_on_knots/proof.md)
  (B, proof);
- [bounded scan](scan.md);
- scoping, which is scratch and not evidence.

## Outcome in one paragraph

**SL(2,3) is polynomial with bounded homology, so the line is not "abelian-by-nilpotent".**
- **How SL(2,3) counts.**
  - Its maps are A₄ maps whose lift through the centre {±I} is unobstructed.
  - The A₄ maps form, over each of boundedly many maps to Z₃, an affine space of twisted cocycles. That space can be exponentially
    large.
  - The obstruction is a quadratic function on that space. It takes values in the untwisted group H²(M; F₂), which bounded homology
    keeps small.
  - Gauss sums count its zeros exactly.
- **The general class.** The same holds for every group with a central (Z/2)^m layer over an elementary abelian 2-layer over a
  nilpotent quotient (A).
- **The other side.** S₄ and its double covers GL(2,3) and 2O, of Fitting height 3, are #P-hard: on closed manifolds for S₄
  (`CLOSED-H1-20261025-001C`), and on knots for all three (B).
- **So the line now sits between Fitting heights 2 and 3**, as far as tested. Whether every Fitting-height-2 group is polynomial is
  open. The gap is twisted central layers and deeper nilpotent layers, where the obstruction stops being an untwisted quadratic.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Expectation | The SL(2,3) obstruction should be quadratic in the twisted cocycle, with a bounded target | Confirmed |
| Literature (Samperton–Weiß v2, read in full) | Gauss sums for class-2 targets over the untwisted domain Hom(Γ, B); the twisted case flagged as unclear | Scan |
| SL(2,3) algorithm against brute force | 42 surgeries, then 20 larger ones, then 40 random presentations, all equal | Scratch |
| Generic algorithm (any group of class (H)) | 240 cases over SL(2,3), Q₈, D₈ and Z₂ × SL(2,3), all equal; degree-2 obstruction tested at random points | Proved (A) |
| Scale | Lift spaces of dimension 26 (k = 12 figure-eight summands) counted in 0.3 s | Check (A) |
| GL(2,3) and 2O on S³₄(K) | 8 + 2T holds on 23 of 28 knots and fails on 5 (3₁ # 3₁, 3₁ # D(C₃⁽³⁾), and the tripled diagrams of the path, C₅ and the triangle with a doubled edge); the two groups agree on all 28 | Recorded (B) |
| GL(2,3) and 2O on knots | Exactly twice the S₄ count; the unrestricted S₄ count is 4 + R + 2T | Proved (B) |

## What was proved

| Result | Content |
| --- | --- |
| A | For G with central A ≅ (Z/2)^m ≤ N ⊴ G, N/A elementary abelian and G/N nilpotent: \|Hom(P, G)\| = \|Hom(P, A)\| · Σ_ψ #{zeros of a quadratic map on the affine twisted lift space}. This is polynomial for balanced presentations, hence closed 3-manifolds, with bounded first homology. SL(2,3) qualifies but is not abelian-by-nilpotent. |
| B | Maps from knot groups to GL(2,3) or 2O are exactly twice the maps to S₄, and \|Hom(π, S₄)\| = 4 + R + 2T. So all three are #P-hard on knots, with or without the meridian condition. The closed case for the double covers is open. |

## Observed, not proved

- **A closed form.** For SL(2,3) on S³₆((4₁)^{#k}), the counts are 2·(2^{k+1} + (−1)^k)² for k ≤ 12. This is the Gauss-sum shape: a
  quadratic form whose Arf invariant alternates with k.
- **A constant offset.** For the knots tested, the SL(2,3) counts of S³₆(K) and S³₀(K) differ by exactly 6.

## What this changes

- **For the complexity side of the thesis.**
  - The affine/non-affine line of the program reappears one level up.
  - An affine level over a bounded top, with an untwisted quadratic sign on top, is still countable: Gauss sums are the quadratic
    analogue of linear algebra.
  - What breaks counting is a level whose dimension depends on the level below. That is S₄: the V₄ lifts over S₃ colourings follow
    the bicycle law.
- **Patterns of patterns.**
  - SL(2,3) has three levels: Z₃, then V₄, then a sign.
  - The sign is a quadratic pattern of the V₄ pattern, and quadratic patterns of patterns are still tractable when they take
    boundedly many values.
- **The next discriminator.**
  - Over F₂, polynomial equations are easy to count in degree 2 and #P-hard in degree 3 (Ehrenfeucht–Karpinski).
  - So the line may really be "the obstruction degree and its twisting", not the Fitting height.
  - A Fitting-height-2 group with a twisted central layer, or with a cubic obstruction, would decide it.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| The bounded-homology line might be "abelian-by-nilpotent" | `CLOSED-H1-20261025-001` recommendation | **False.** SL(2,3) is polynomial and not abelian-by-nilpotent. |
| Central extensions of S₄ inherit the closed hardness directly | Scoping | **Not directly.** On closed manifolds the lifted longitude signs vary, and the naive identity fails on some knots. |
| Gauss sums are only useful for nilpotent targets (Samperton–Weiß's setting) | Literature | **Too narrow.** They work over twisted domains when the target is untwisted. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A | Group cohomology (central lifting) plus Samperton–Weiß's Gauss sums, applied over the affine twisted level of `BOUNDED-H1-20261025-001B` | `candidate-local-delta`; folklore risk medium |
| B | Central lifting on knot groups plus Livingston 1995 | Routine (folklore risk high); its hardness consequence rests on `BOUNDED-H1-20261025-001A` |

**Did the perspective do real work?** Modestly.
- The "levels of patterns" reading suggested looking for the degree of the top level's dependence on the level below.
- The proof itself is standard obstruction theory.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: SL(2,3) with bounded homology | **Status:** Successful | Polynomial, proved and checked; the line is not abelian-by-nilpotent. |
| Local direction: central quadratic layers | Exhausted for SL(2,3) | The class (H) is covered. Odd-exponent central layers would need Gauss sums over F_p and non-bilinear cocycles. |
| Broader exploration: where the line falls | Known alternatives | Twisted central layers (Samperton–Weiß footnote 11), cubic obstructions (class-3 layers), and closed hardness for GL(2,3) and 2O. |
| Long-term goal: the complexity side of the thesis | Capability gained | The tractable side now includes one quadratic level over an affine level. Hardness so far comes only from Fitting height 3. |
| Next recommendation: twisted central layers | **Next step:** Research directions | First test: G = UT₃(F₄) ⋊ Z₃ (order 192, Fitting height 2, centre of N twisted by ω). Is its count with bounded homology polynomial, or does the twisted obstruction H²(M; F₄_ω), which can be large when H₁ is bounded, make it #P-hard? |
| Interest: that recommendation | **2/3: Promising** | It decides whether the line is "Fitting height 2" or "untwisted quadratic obstructions". Either answer is a sharper statement about patterns of patterns. |
| Execution | Deferred to the owner | Bound: one epic. Stop if the twisted obstruction space stays bounded in all cases, which would make it polynomial by the same method, or if no gadget controls it. |

**Alternatives:**
- **Closed-manifold hardness for GL(2,3) and 2O (1/3).** A Fourier analysis of the lifted longitude signs.
- **A single-query S₄ result through the parity rule for 4-cycle longitudes (1/3).**
- **A short note on the bounded-homology picture: S₄ hard, SL(2,3) easy (2/3).** It depends on the novelty of
  `BOUNDED-H1-20261025-001A`, which passed Codex's correctness review. Sharing is the owner's call.
- **Return to the core intuitions (1/3).**
