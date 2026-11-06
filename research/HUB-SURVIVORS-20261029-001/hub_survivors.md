# Which knots survive patterns of patterns once hubs are allowed

Epic `HUB-SURVIVORS-20261029-001`, closed 2026-10-29.

## The question

- **The owner's decisions.** On 2026-10-29 the owner put hub laws in scope ("Should hub laws be in scope?" "Yes.") and approved the
  recommended continuation ("Yes, let's continue").
- **Terminology.** The canonical common hub is decomposable shared identity, not a touch. A network hub (a distinction in three or
  more knots) is equality fan-out: pairwise structure. So hubs are a declared substrate, never counted as contact or emergence.
- **From the previous epic.** `GEOMETRY-LAW-20261029-001` proved that without hubs only parity survives patterns of patterns. So:
  which knots survive once hubs are allowed, by what mechanism, and in which shapes?
- **Intuitions targeted:** patterns of patterns and the growth of emergent information; space from logic without a drawn space;
  the universally influential cycles; the two/three boundary.

**The evidence:**
- [Hub survivors are rebuilt by parallel copies](../../proofs/HUB-SURVIVORS-20261029-001A/HUB-SURVIVORS-20261029-001A-P001_hub_survivors_are_rebuilt_by_parallel_copies/proof.md)
  (A, proof);
- [Not-all-equal is rebuilt by the Fano plane, and by nothing smaller](../../proofs/HUB-SURVIVORS-20261029-001B/HUB-SURVIVORS-20261029-001B-P001_not_all_equal_is_rebuilt_by_the_fano_plane/proof.md)
  (B, proof);
- **scoping (scratch, not evidence):** the hub censuses before the tickets (two bookkeeping errors found and corrected, below), the
  intersection closures, the "no lone one" searches.

## Outcome in one paragraph

**With hubs, emergence beyond parity survives patterns of patterns, by two mechanisms; and the smallest pattern of patterns of
not-all-equal is the Fano plane, an exact fixed point counts included.**
- **Parallel copies (A).** Hubs let copies sit on the same variables, which intersects their constraints. Gluing without hubs can
  only dilute exclusion.
  - Up to six copies, exactly seven of the 16 classes of three-place knots are rebuilt: the two parity classes; the two "x or
    (y ≠ z)" classes, the two three-excluded classes with a symmetry of order two, and twisted not-all-equal, each from four copies.
  - Each of these reaches parity or an equality by parallel intersections.
- **Non-2-colourability (B).** Not-all-equal reaches neither, yet it is rebuilt at seven copies: its copies on the lines of the
  Fano plane, with one point split into the three legs.
  - No gadget of six or fewer copies does it, and at seven copies the punctured Fano plane is the only one.
  - Each of its six allowed leg tuples has exactly 5 hidden completions, so substituting it multiplies every count by 5 per copy
    and leaves the law unchanged.
- **Never.** The two monotone atoms (OR, NAND) are never rebuilt, at any size.
- **Open.** "x or (y = z)", the no-lone-value classes and the asymmetric atoms are not rebuilt up to six copies. "No lone one" is
  also not rebuilt at seven (scoping). Larger sizes are open, since not-all-equal shows the census bound decides nothing.

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1 | Intersecting the placements of a class reaches parity for "x or (y ≠ z)" and the three-excluded classes, and an equality on two coordinates for twisted not-all-equal; the other classes reach neither. |
| A, Theorem 2 | Exhaustive over hub gadgets of three to six copies (3, 11, 104, 1065 shapes; every placement): exactly the seven classes above are rebuilt, the non-parity ones from four copies, by many shapes at six copies (77 to 186). |
| A, Theorem 3 | The monotone atoms are never rebuilt: in a gadget of at least two copies every copy holds a hidden variable, and all-ones (or all-zeros) satisfies every copy. |
| B, Theorems 1 and 4 | The punctured Fano plane rebuilds not-all-equal. Every rebuilding gadget has at least seven copies, and at seven it is the punctured Fano plane: merging the legs gives a 3-uniform hypergraph without property B (m(3) = 7, the Fano plane unique), and two legs on one copy would need an equality wire, of which none has at most six copies. |
| B, Proposition 5 | The punctured Fano gadget has 5 completions per allowed tuple, so not-all-equal is an exact counted fixed point of the Fano substitution: each level adds log₂ 5 ≈ 2.32 hidden bits per copy. |

## What this changes for the core intuitions

- **Patterns of patterns and the growth of emergent information.**
  - Without hubs, only parity's one bit per loop survives.
  - With hubs, emergence that is not parity survives too. For not-all-equal it grows by exactly log₂ 5 bits per copy at every level
    of the Fano tower, with its visible law unchanged. This is the first exact, non-parity self-similar law in the program.
- **Space from logic without a drawn space.** The smallest structure in which the frustration knot reproduces itself is a finite
  projective plane: seven points, seven lines, every two lines meeting in exactly one point. That is an incidence geometry produced by
  the law's own self-reproduction, with nothing drawn but the requirement that each level obey the same law. It is not a metric
  geometry, and larger hypergraphs without property B also work, so the law forces the Fano plane only at the smallest size.
- **The two/three boundary.**
  - Hubs are pairwise, equality fan-out. They add nothing to pairwise relations: equalities in parallel are still equalities.
  - Applied to three-place knots, the same fan-out lets knots run in parallel, and that is what keeps their structure across scales.
  - So hubs make the two-place part (sharing) and the three-place part (knots) work together.
- **Universally influential cycles.** Parity's cycles survive every coarse-graining. With hubs, not-all-equal's Fano cycles do too,
  exactly. Both are now candidates; parity's need no hubs.
- **Shapes.** No class prefers one shape: every survivor is rebuilt by many gadgets. The one exception is not-all-equal at its
  smallest size, where the Fano plane is unique.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Only parity survives patterns of patterns | `GEOMETRY-LAW-20261029-001A` | **True only without hubs.** With hubs, seven classes survive within six copies, and not-all-equal at seven. |
| Hubs add nothing but fan-out | The common-hub guardrail | **Refined.** Hubs are pairwise and never contact, but they enable parallel composition, which is what lets non-parity knots rebuild themselves. |
| Geometry from a law needs a metric | The previous epic's framing of geometry as scale and orientation | **Refined.** An incidence geometry, the Fano plane, appears as not-all-equal's minimal self-reproduction. |

## Scoping and corrections

- **Overwritten class labels.** A first census credited every rebuild to the last member of each class, which hid rebuilds of the
  others. It was replaced by a class-correct test. Ticket A of `GEOMETRY-LAW-20261029-001` used the same table only for labelling
  its flow, and its bounds and strict-decrease checks do not depend on it.
- **Skipped gadgets.** A fast enumeration listed hidden variables by size before position, which skipped gadgets (7 of 11 shapes at
  four copies). Ordered lexicographically, it matches a full canonical enumeration (3, 11, 104 shapes). Both tickets' checks contain
  this comparison and the mutated ordering as a control.
- **Degenerate gadgets.** Allowing legs in several copies or hidden variables in one copy makes rebuilding trivial: a copy carries
  the legs and the rest hangs off it. The non-degenerate definition (legs in one copy each, hidden variables in at least two) is the
  one a substitution needs.

## Literature (bounded)

- Property B: m(3) = 7, attained only by the Fano plane (Erdős; stated in arXiv 2303.03803).
- NAE reductions use other gadgets. No source found describes a punctured Fano plane rebuilding not-all-equal.
- Higuchi and Mézard (2009): decimation produces linear constraints. Here, exact substitution with hubs also keeps non-linear laws.
- Hierarchical-lattice renormalization: exact fixed points of frustrated models are rare; the Fano substitution gives one for
  not-all-equal.

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A | Parallel intersections (the program's patterns of patterns, with the owner's hubs) and an exhaustive census | Candidate local delta |
| B | Property B and the Fano plane (classical), applied to the program's question | Candidate local delta, classical ingredients |

**Did the perspective do real work?** Partly.
- **The question came from the program.** It asked which laws survive being rebuilt from their own copies, with and without hubs.
  That question led to the Fano plane.
- **The minimality proof is classical.** It rests on property B.
- **The counted fixed point.** It follows from symmetry and a count, and the program's framing made it the thing to look for.

## Gaps

1. Survival of "x or (y = z)", the no-lone-value classes and the asymmetric atoms beyond six copies (seven for "no lone one").
2. Not-all-equal wires: whether any exist at all.
3. The geometry of the Fano tower beyond one level, and the counted behaviour of the other survivors.
4. No human or external review.

## Work ratio

- **Artifacts that changed a conclusion (2):** A, B.
- **Administrative:** the closure ledger, the discovery record and its disposition.

## Recommendation

**Scoping after the proofs (scratch, not evidence).** Some survivors are exact counted fixed points: a rebuilding gadget gives the
same number of hidden completions to every allowed tuple. Within five copies, and seven for not-all-equal, these are:
- parity, with factors 1, 2 and 4;
- the three-excluded classes, with factors 1, 2 and 4 at five copies;
- twisted not-all-equal, with factor 2 at four copies and 1, 2 and 3 at five;
- not-all-equal, with factor 5 (the Fano plane).

The "x or (y ≠ z)" classes are rebuilt only as relations; none of their gadgets up to five copies has uniform counts. An exact counted
fixed point is a law that looks the same at every scale, counts included, and each level adds log₂ of its factor in hidden bits per
copy.

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: which knots survive patterns of patterns with hubs | **Status:** Successful | Survivors classified within six copies (seven classes, by parallel copies). Not-all-equal rebuilt at seven by the Fano plane, minimal and unique, and an exact counted fixed point. Monotone atoms never. |
| Local direction: the hub census | Partly open | The remaining classes beyond six copies ("no lone one" also not at seven). Not-all-equal shows a bounded census decides nothing about larger sizes. |
| Broader exploration: space from logic (question 9) | Capability gained | The first self-reproducing incidence geometry: the Fano plane as not-all-equal's minimal pattern of patterns. Hubs (equality fan-out) are what make it possible. |
| Long-term goal: emergence across scales | Capability gained | Exact non-parity scale invariance exists with hubs (not-all-equal on Fano towers, factor 5; twisted not-all-equal, factor 3). Without hubs only parity has it. |
| Next recommendation | **Next step:** Continue, with a fresh epic on exact self-similar laws | Classify the laws with exact counted fixed points and their factors (first discriminator: the census of uniform-count gadgets up to six copies, every class). Then ask what spaces their towers build, starting with the Fano tower of not-all-equal (growth, how correlations between legs behave, whether every level's law is exactly not-all-equal). |
| Interest: that recommendation | **2/3 (Promising)** | Evidence: exact fixed points exist for four non-parity classes with small factors (2, 3, 5). They tie directly to the growth of emergent information (log₂ of the factor per level) and to the universally influential cycles. Main uncertainty: the towers' "space" may be just a hierarchical lattice, a classical object; the novelty would lie in which laws are exact and why. |
| Execution: that next action | Deferred to the owner | No successor created. Alternative (1/3): settle survival of the remaining classes at larger sizes. Stop the exact-law route if the uniform-count census shows no structure in the factors. |
