# Geometry from a law, with nothing drawn in advance

Epic `GEOMETRY-LAW-20261029-001`, closed 2026-10-29.

## The question

- **The owner's direction.** On 2026-10-28 the owner agreed to leave the counting census and "come back in at the open half of
  question 9: geometry from a law, with nothing drawn in advance". Then: "You can start that work now actually, let it run in the
  background."
- **Question 9** of the knot intuition asks which uniform, local law, not written on a space in advance, gives a shape that looks
  like a space of low dimension. `SURFACE-GLUING-20261024-001` answered it at the level of topology: native gluing of three-place
  knots builds surfaces. It added that "no geometry (metric, flatness) appears".
- **Re-posed with nothing drawn.** A uniform law can coarse-grain itself: replace each knot by a native gadget made of copies of
  the same knot. These are patterns of patterns. Which laws survive that, in which shapes, and so with which dimensions? Can a law
  fix an orientation or a scale at all?
- **Intuitions targeted:**
  - space from logic without a drawn space;
  - the two/three boundary;
  - patterns of patterns and the growth of emergent information (the post that started the program);
  - everything relational.

**The evidence:**
- [Only parity is rebuilt by native gadgets of its own copies](../../proofs/GEOMETRY-LAW-20261029-001A/GEOMETRY-LAW-20261029-001A-P001_only_parity_is_rebuilt_by_native_gadgets_of_its_copies/proof.md)
  (A, proof);
- [Four places: only parity and a chained implication survive](../../proofs/GEOMETRY-LAW-20261029-001B/GEOMETRY-LAW-20261029-001B-P001_four_place_survivors_are_parity_and_chained_implications/proof.md)
  (B, proof);
- **scoping (scratch, not evidence):** the counted flows below, and the first censuses before the tickets.

## Outcome in one paragraph

**A Boolean law glued natively fixes the topology of its space and the sign of its curvature, and nothing geometric survives
patterns of patterns.**
- **Three places (A, proved for every size).**
  - Only the two parity knots are rebuilt by native gadgets of their own copies, and every gadget shape rebuilds them.
  - Every other knot's gadgets exclude fewer tuples. Towers of patterns of patterns built from one non-parity law reach the
    free relation within three levels.
  - No three-place knot can orient a vertex.
- **Four places (B, exhaustive for two and three copies).**
  - Orientation appears: 96 relations in 6 classes can orient a vertex.
  - None of them survives. What survives is parity (every shape) and one chained implication between parities of pairs, which is
    a two-place relation on derived bits and builds only chains.
- **Counting (scoping).** Counting hidden witnesses does not rescue a scale under the two smallest substitutions. Every non-parity
  knot decays to independent biased bits, at most keeping a two-place correlation between legs that sit on one copy.
- **So.** What survives every scale is shapeless (parity) or one-dimensional (pairwise), never two-dimensional. The smallest
  enrichment with a known scale-fixing mechanism is hubs with counts.

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1 | Every native gadget of a parity knot gives back the knot (leg total fixed; classical). |
| A, Lemma 2 | In an excluded leg tuple of a gadget of a non-parity knot, both sides of every bridge hold a leg (from the cactus theorem of `NATIVE-HARDNESS-20261024-001B`). |
| A, Theorem 3 | A native gadget of a non-parity knot excludes no leg tuple if the knot has no wire face (12 knots). It excludes at most one if the knot excludes two tuples at distance two (12 knots; only the triangle can), and at most two if it excludes three (8 knots; at most one unless a copy carries two legs). |
| A, Corollary 4 | Only parity is rebuilt; towers of other knots reach the free relation within three levels (the census attains three). |
| A, Proposition 5 | Every three-bit knot's symmetry group contains a transposition, so none orients a vertex. |
| B, Theorem 1 | Among the 106 classes of four-bit knots, gadgets of two and three copies rebuild exactly the even parity class (every gadget), the odd parity class (odd numbers of copies) and the implication between pair parities (exactly the chains). Every other class loses excluded tuples. |
| B, Propositions 2 and 3 | Chains of every length rebuild the implication, so its towers are chains. 96 relations in 6 classes orient a vertex, and none is rebuilt. |

## Background, classical: the type of curvature

Closed native worlds of three-place knots are pants decompositions of closed surfaces with Euler characteristic minus the number
of knots (`SURFACE-GLUING-20261024-001A`, Theorem 1).
- By Gauss–Bonnet and uniformization they carry only hyperbolic metrics: each knot is a unit of negative curvature.
- A relation on k places is a sphere with k holes, of Euler characteristic 2 − k:
  - two-place relations (annuli) are flat;
  - one-place pins (disks) are positively curved;
  - flat or spherical closed worlds need pins and pairs to balance the knots.
- The metric itself is not fixed: Teichmüller space is left free.

This is a reading of classical facts, not a result of the epic.

## Scoping: counting hidden witnesses (scratch, not evidence)

- **The probe.** Each three-bit knot, as a 0/1 weight on its allowed tuples, was substituted repeatedly by the triangle of three
  copies and by the knot-with-theta of three copies. The weights count hidden witnesses and were normalized each time, over 400
  iterations.
- **Triangle, and theta with every placement averaged.** All 32 non-parity knots converge to product weights, independent biased
  bits: zero multi-information, with weight ratio λ per 1 (for example λ ≈ 1.256 for the atom excluding 000). Parity stays parity.
- **Theta with one fixed placement.** Its two legs on one copy keep a two-place correlation of 0.010 to 0.085 bits, and the third
  leg becomes independent (mutual information below 10⁻¹⁵).
- **Reading.** Counting keeps a bias at each distinction (a soft pin) and pairwise bonds, never a three-way bond. This mirrors the
  set-level result: what survives is pairwise or parity.

## What this changes for the core intuitions

- **Space from logic without a drawn space.** Native logic builds two-dimensional topology and fixes its curvature type. It fixes no
  orientation that survives, no scale and no dimension.
  - Every native world, whatever its large-scale shape, is equally coherent. Covers of coherent networks are coherent, so no law
    rules out tree-like or expander-like worlds.
  - A low-dimensional large-scale shape is therefore a fact about where a localized part sits, not a consequence of the law.
- **The two/three boundary, one level up.** At the level of patterns of patterns, the boundary reappears as "pairwise or parity".
  - Two-place structure survives and builds lines (B's chained implication; the counted pairwise bonds).
  - Of the genuinely three-way structure, only parity survives, and in every shape.
  - All other emergence dies within three levels.
- **Growth of emergent information.** Naming patterns and combining the names does not grow emergent information, except for
  parity: one bit per loop at every level. This sharpens `EMERGENCE-BITS-20261021-001` (one bit per independent loop, filled only
  by parity) from networks to towers.
- **"Infinite cycles of logic that are universally influential".** Parity is the only three-place law that survives every
  coarse-graining. If anything in the base is universal across scales, it is parity's cycles: the holes, one first-cohomology class
  per loop. This is a reading, not a theorem.
- **Everything relational.** Counts carry harmonies on surfaces (the Fibonacci rates of `SURFACE-GLUING-20261024-001`), but under
  substitution they keep only fields and pairwise bonds.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Geometry might come from a law once topology does | Question 9's open half; the surface-gluing note's "no geometry appears" | **Refined.** Native laws fix curvature type, and nothing geometric survives patterns of patterns. |
| Three-place knots can carry orientation | Implicit in reading knots as oriented pieces | **False.** No three-bit knot orients a vertex. Orientation needs four places, and no orienting four-place law survives. |
| Counting hidden witnesses might supply what sets lack | The relational intuition; the Fibonacci harmonies | **Not under substitution (scoping).** Counts keep only fields and pairwise bonds. |

## Literature (bounded scan, four queries)

- Feder, *Fanout limitations on constraint systems* (2001); Dalmau and Ford (2003); Kazda, Kolmogorov and Rolinek, *Even
  delta-matroids and the complexity of planar Boolean CSPs* (2019): what two-occurrence gadgets express and decide.
- Holant clones (arXiv 1811.00817) and triangle gadgets of ternary signatures in the Holant^c dichotomy: closures under gadgets.
- Higuchi and Mézard, *Decimation flows in constraint satisfaction problems*, J. Stat. Mech. (2009) P12009: decimation produces
  linear constraints over GF(2). This is the closest analogue: linear structure as the survivor of a flow. Our operation is exact
  substitution with every internal variable hidden.
- Migdal–Kadanoff and Berker–Ostlund hierarchical lattices: real-space renormalization with a given substitution. Counted flows
  with hubs are of this kind.

No source states which relations are rebuilt by gadgets of their own copies.

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A, Theorem 3 and Corollary 4 | The question came from the program (patterns of patterns, native gadgets). The proof applies the program's own structure theorem for native contradictions (`NATIVE-HARDNESS-20261024-001B`). | Candidate local delta |
| A, Proposition 5; B | Symmetry orbits and an exhaustive census | Computed; candidate local delta |
| Curvature type | Gauss–Bonnet and uniformization | Classical background |

**Did the perspective do real work?** Yes for A. The native-gluing condition, the knot axiom K2 and the cactus theorem of native
contradictions, all from the program, supplied the proof. The question, which laws survive being built from their own copies, came
from the program's founding post. B is computation guided by A.

## Gaps

1. Four places: gadgets of four or more copies are sampled, not exhaustive. Five or more places: not studied.
2. Counted flows: two substitutions only, scoping, no proof.
3. Hubs, signs and larger distinctions: not studied here.
4. No human or external review.

## Work ratio

- **Artifacts that changed a conclusion (3):** A, B, and the counted-flow scoping (which changed the recommendation).
- **Administrative:** the closure ledger, the discovery record and its disposition.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: geometry from a law, nothing drawn | **Status:** Successful (a precise negative) | Native Boolean laws fix topology and curvature type. Nothing geometric survives patterns of patterns: only parity (every shape) and pairwise chains. Orientation needs four places and does not survive. |
| Local direction: native gluing, sets and counts | Practically exhausted under its assumptions | Sets: proved at three places for every size, exhaustive at four for two and three copies. Counts: product weights and pairwise bonds in scoping. |
| Broader exploration: space from logic (question 9) | Known alternatives | Hubs (a distinction in three relations) are the one structure beyond native topology. They carry three dimensions (`HUB-DIMENSION-20261024-001`) and hardness (`NATIVE-HARDNESS-20261024-001`), they allow parallel composition (all-equal is rebuilt), and with counts they gave the program's one scale-fixing mechanism so far: fair contacts are critical exactly on the self-dual square lattice (`BASE-CRITICALITY-20261022-001`). The canonical gate treats hubs as common hubs, not contacts. |
| Long-term goal: space from logic without a drawn space | Obstruction learned | Native space is two-dimensional, hyperbolic in type and geometrically floppy. Geometry, like dimension three and hardness, lives beyond native contact. |
| Next recommendation | **Next step:** Research directions, a bounded comparison of two ways forward | (1) **Hubs with counts:** whether a law fixes a dimension through self-duality with nothing drawn but a substitution rule. First discriminator: fair contacts on self-dual hierarchical substitutions (the Wheatstone bridge, critical at 1/2) against non-self-dual ones (the diamond, critical at (√5 − 1)/2). (2) **The universally influential cycles:** make "only parity survives every coarse-graining" precise for infinite towers (question 7). The owner should also decide whether hub laws, which the canonical gate does not count as contact, are in scope. |
| Interest: that recommendation | **2/3 (Promising)** | Evidence: the hub route has an in-program mechanism (fairness is criticality on self-dual lattices) and a cheap discriminator. Main uncertainty: hierarchical-lattice percolation is classical, so a positive answer may be known, and hubs sit outside native contact. |
| Execution: that next action | Deferred to the owner | This epic stops at its endpoint. No successor created. Reassess after the owner's choice, and stop the hub route if fairness turns out not to be critical on self-dual substitutions with knots. |
