# Pre-registration: a parity knot among stitched copies

Epic `PARITY-MIX-20261112-001` (`LINE-LOCK-20261112-001` direction 2, chosen by the coordinator over the recommended direction 1;
G17 with G8; program mathematics, group arithmetic), written on 2026-11-12 before the census runs, at the coordinator's go-ahead under
the owner's standing mandate. Code frozen with this file in
`proofs/PARITY-MIX-20261112-001A/PARITY-MIX-20261112-001A-P001_parity_among_copies/` (`parity_lib.py`, `check.py`). The canonical K1–K3
test is unchanged.

## The question

`LINE-LOCK-20261112-001` proved that a harmony's not-all-equal stitch holds no permutive sub-stitch, so stitched harmonies alone never
carry additive (Ledrappier-type) influence. The coordinator's question: **what is the smallest change that lets influence pass through
whole counts of copies, and is that change typical or rare?** Here the change is to make some of the mixed knots parity knots.

## Words

As in `SHIFT-LOCK-20261112-001` and `LINE-LOCK-20261112-001` and the glossary. New, plain (checked with the advisor model, which replaced slice, projective, gap and reach):

- **Flip-blind parity knot** on three copies: their placewise sum (exclusive or) is all 0s or all 1s, through one hidden reference
  distinction per knot (the literature's parity up to a global flip). A **flip-blind triple** of a harmony: three of its states with
  such a sum.
- **Count r**: the copies whose count along the first copy shift is r (the literature's row of an array).
- **Up to flips**: each copy may be flipped on its own; two states of a copy count as one when they are equal or complements. Count r
  is **flip-frozen** when all states share it up to flips (the glossary's "frozen", one value in every state, is stronger); it is
  **fixed by count 0** when any two states that agree on count 0 up to flips agree on count r up to flips (the literature's entailment);
  it is **reached by propagation** when local propagation from count 0 makes all its copies known (a knot with two known members whose
  relation forces the third makes the third known: always for parity, for the not-all-equal stitch only in slots where its relation
  forces one class). Counts **fixed but unreached**: fixed by count 0, not flip-frozen, not reached by propagation. **Full fixing**: every
  count fixed by count 0, and some count not flip-frozen.

## Buildable or brought in (the coordinator's condition 4)

A three-member parity knot (sum all 0s) is not complement-closed, so the not-all-equal law cannot build it (the law's polymorphisms
include the flip; Schaefer; Geiger, Bodnarchuk): it needs a zero, as the count line found. The **flip-blind** parity knot is
complement-closed, a four-member parity per place with one hidden reference distinction per knot, so it can be built from
not-all-equal knots with hidden distinctions (a gadget; the advisor's NAE4(a, b, c, r) = ∃e: NAE(a, b, e) ∧ NAE(¬e, c, r) route, with
the flip read as the law's own symmetry). A reference shared by every knot would be a hub; one per knot is at the scale of a contact.
Recorded as **A78** (a parity knot among copies is read as flip-blind parity, built from our knots), challengeable.

## Settled by definition (stated before the run; the advisor model's, rechecked)

- A parity knot forbids its three copies from being all equal (u ⊕ u ⊕ u = u is not constant), so "locked" is replaced here by the
  reach measures.
- A harmony with no flip-blind triple ends at its first parity knot; one with a flip-blind triple keeps the knot alone.
- In an arrangement of parity knots only, the placewise differences of any two places obey Ledrappier's law, so states exist only at
  Ledrappier's sizes; on 3 × 3 every state is X(i, j) = U_{(i − j) mod 3} with U₀, U₁, U₂ a flip-blind triple; on 2^k × 2^k only the
  zero difference survives, so no state. The doubling-distance relation of Ledrappier's law is an identity there, not a finding.
- In a mixed arrangement, a parity knot with two known members makes the third known up to a flip; this is local propagation, the
  syntactic part. What is **not** settled by definition is whether some count is fixed but unreached: fixed by count 0 though
  propagation does not reach it, because the harmony's own states (each copy must be a state of the harmony) and the not-all-equal knots elsewhere constrain
  the whole together.

## The census (frozen)

- **census.** The 45 harmonies of period at most 16 (`SHIFT-LOCK-20261112-001`'s): flip-blind triples, the largest subspace of classes
  (dimension d with every non-zero element a class of the harmony's states, up to flips), which slots of the not-all-equal stitch leave
  one class (functional), and two harnesses on 3 × 3 (one parity knot; parity everywhere).
- **Placements (every harmony with a flip-blind triple; no choice by outcome).** p3: every placement of parity knots on the 9 cells of
  3 × 3 (512); p4: every placement on 4 × 4 (65,536, one per class of the repeat's 16 translations, 4,156 classes, weighted by class
  size); p6: on 6 × 6, 20 placements of k parity knots drawn uniformly for each k in 0, 3, ..., 36; p8: on 8 × 8, 10 for each k in 0, 4,
  ..., 64 (seeded). The rest of each placement's cells carry the not-all-equal one-order stitch.
- **Each placement.** A state?; flip-frozen counts; counts fixed by count 0; counts reached by propagation; counts fixed but unreached;
  full fixing.
- **Cap.** 1 hour and 16 GB per part; each harmony's rows saved as they finish; a part stopped at its cap reports the harmonies reached.

## What counts (frozen)

- **Empty beyond definition (the failure criterion).** No placement with k below nm, in the exhaustive parts p3 and p4, has a count
  fixed but unreached. Then parity among stitched copies does nothing beyond local propagation, and the epic says so (and the coordinator's
  fallback, the mean-step proof, follows).
- **Something beyond definition.** Some placement has a count fixed but unreached: count 0 fixes, through the harmony's states and
  the knots together, counts no local propagation reaches. Then report how common it is: the share of placements with such a count and
  with full fixing at each density k / nm, the smallest k with full fixing, and whether full fixing is rare below half density and
  typical above it.
- **Survival.** The share of placements with a state at each k: whether the harmony's own knots survive alongside parity.

## Predictions (frozen; the advisor's unless marked)

- Harnesses as stated (definitional; 95%).
- Most harmonies with flip-blind triples have a largest subspace of dimension 2 (60%).
- A count fixed but unreached on some placement with k < nm (85%).
- Full fixing rare at low density, typical only somewhere between half density and all parity (50%).
- At sizes not divisible by 3 (4 × 4, 8 × 8), states die out before all parity for harmonies of subspace dimension 2 (60%).
- Mine: fewer than half of the 45 harmonies have a flip-blind triple (60%).

## Known mathematics, checked before the freeze

Ledrappier's shift (1978) and its spin version, the triangular plaquette model of Newman and Moore (1999), with fractal symmetries
(Yoshida, 2013; Devakul, You, Burnell and Sondhi, 2019); closed invariant subsets of algebraic shifts (Einsiedler, 2004), so states
avoiding some values are not surprising in the endless arrangement; bootstrap percolation (Aizenman and Lebowitz, 1988; Holroyd,
2003), rigidity percolation (Jacobs and Thorpe, 1995), mixtures of linear and non-linear clauses ((2 + p)-SAT; Monasson and co-authors,
1999), locked constraint problems (Zdeborová and Mézard, 2008), cellular automata with rules varying by site (Cattaneo, Dennunzio,
Formenti and Provillard, 2009); Schaefer (1978) and the Galois connection for what not-all-equal can build. What could be new: a
quenched mixture of an additive and a non-additive three-member rule on a harmony's states, the counts that count 0 fixes but
propagation does not reach, and how often they appear.

## Seen before the freeze (disclosed)

A smoke test on the alternation 01 only: it has no flip-blind triple and one parity knot on 3 × 3 leaves no state; 4 × 4 has 4,156
translation classes of placements.

**Referee.** The background referee thread (referee pending). Assumptions in force: A70, A75, A77, A78 (added). Nothing here bears on P
versus NP.
