# Twisted three-literal worlds: where the twist decides contradiction

Epic `TRIPLE-TWIST-20261023-001`, closed 2026-10-23.

## The question

The owner asked for a cheap feasibility check of the three-literal side, run alongside the complete map of twist relations:
- reread the contact-census and base-three results;
- try to define a twisted three-literal world where the twist matters;
- see whether a lone-contradiction event can be defined;
- keep a quick failure as a useful negative.

**Why it was open.** Everything since the criticality epic lives on the two-literal side.
- **There:** the twisted double cover is the implication digraph of a two-literal formula, a contradiction is a cycle x ⇝ ¬x ⇝ x,
  and a lone contradiction loop shields exactly the twist dual to it.
- **The previous epic's warning:** with independent fair literal polarities a twist is invisible by symmetry, so a three-literal
  world needs correlated polarities.

**The evidence:**
- [Twisted three-place worlds](../../proofs/TRIPLE-TWIST-20261023-001A/TRIPLE-TWIST-20261023-001A-P001_three_place_twists/proof.md)
  (A, proof);
- [The census of twisted three-place contacts](../../experiments/TRIPLE-TWIST-20261023-001B/TRIPLE-TWIST-20261023-001B-E001_contact_census/contract.json)
  (B, confirmatory experiment;
  [result](../../artifacts/TRIPLE-TWIST-20261023-001B/TRIPLE-TWIST-20261023-001B-E001_contact_census/result.json));
- **Scoping (scratch, not evidence):** exact unsatisfiability counts of the monotone world on small triangular tori, colouring
  existence on 20 tori up to 7 × 7, and a first survey of ten contacts.

## Outcome in one paragraph

**The feasibility check is positive.** A well-defined twisted three-literal world exists in which the twist matters for
contradiction, and a lone-contradiction event can be defined.
- **When a twist is a class (proved).** A twist is a cohomology class only for complement-closed contacts, whose two relations are
  swapped by flipping all three places. For other contacts a contractible seam is a physical defect: it raises contradictions on a
  planar patch from 0 to 201 of 300 for "x or 1-in-3".
- **The natural first candidate is frozen.** Monotone clauses from four-place not-all-equal never contradict on small triangular
  tori in any twist. A twisted not-all-equal colouring exists, except on four non-simplicial two-row tori, where every x was
  enumerated and none contradicts.
- **The census splits exactly.** Of the 120 complement-closed placements on the triangular lattice:
  - 66 contradict on planar patches (local);
  - 54 have doubly allowed patterns that tile the plane, and none of these ever contradicts on a planar patch.
- **The twist decides.** For 30 tiling placements that are neither two-literal nor parity worlds, the twists of each torus split into
  fitting ones, which never contradict, and the others.
- **Contradictions wind along odd classes (proved).** Every minimal contradiction winds (7481 of 7481 measured; proved). The twist
  measured from every fitting twist is nonzero on its winding. A line-shaped contradiction therefore runs along a class that this
  relative twist makes odd, as contradiction loops do on the two-literal side.

## The census (B, supported)

| Class | Placements | Pair | Parity | Three-place | What happens |
| --- | --- | --- | --- | --- | --- |
| Local | 66 | 53 | 1 | 12 | Planar patches contradict (scoping minimum 145 of 200); no doubly allowed assignment on any torus |
| Tiling | 54 | 24 | 0 | 30 | No planar contradiction; on tori, contradictions only in twists where the tiling does not close |

**The 30 three-place tiling placements, by how often a non-fitting twist contradicts** (5 fresh tori, 200 samples each):

| Regime | Placements | Contradiction frequency outside fitting twists | Minimal contradictions |
| --- | --- | --- | --- |
| Fits every twist | 127 (the monotone contact), 223 | none (all twists fit) | none |
| Rigid | 12, among them 45, 61 and 135 | at least 90% | 8 to 34 triangles; 1552 lines, 488 crosses |
| Intermediate | 8, among them 62, 109 and 155 | between 0.5% and 97% | 9 to 50 triangles; 419 lines, 811 crosses |
| Rare | 111, 125, 159, 215 | 0% to 3% | 30 to 61 triangles; crosses only (129) |
| Quiet | 123, 183, 191, 239 | none, although some twists do not fit | none |

**The predictions:**
- **P1 (the theorems):** no placement has both certificates, no fitting twist contradicts, and no minimal contradiction is
  contractible (0 of 7481).
- **P2 (the dichotomy):** every placement has exactly one certificate, and the local set is exactly the one scoped.
- **P3 (the twist decides):** for all 20 placements of the scoped group, on every fresh torus some twists fit and some do not, and
  every non-fitting twist contradicts.
- **P4 (lines exist):** 1971 line-shaped minimal contradictions in three-place placements.
- **Odd classes, measured.** On the 4 × 6 and 6 × 6 tori with a single fitting twist, all 1746 line-shaped contradictions of
  three-place placements run along a class that the relative twist makes odd. Theorem 5(d) says this must hold.

**How the run was checked.**
- **Controls.** The solver matches brute force on 200 instances. The lattice code is right on a row and on a triangle. A contractible
  seam is a gauge for six complement-closed contacts (300 of 300 equisatisfiable) and a defect for "x or 1-in-3".
- **The independent checker.** With its own geometry and its own solver it:
  - recomputed all 960 doubly allowed assignments of the 4 × 6 and 6 × 6 tori;
  - replayed all 66 local certificates and 12 tiling patches;
  - replayed 45 minimal contradictions (sizes and ranks equal).
- **Time.** The run took 160 s.

## The proofs (A) in plain terms

- **Why a twist needs complement closure.** Moving a seam relabels the hidden bits on one side, which reads every crossing triangle
  with all three places flipped. That is harmless exactly when flipping all three places swaps the contact's two relations, so that a
  fair visible bit absorbs it.
- **Why tiling forces contradictions to wind.** Suppose a contradiction lies in a part of the torus with no winding. That part lifts
  to the plane and the twist can be gauged away there. The doubly allowed tiling then satisfies it whatever the visible bits are.
- **Why it winds where the twist is odd.** The same argument works against any fitting twist. If the twist agreed with a fitting one
  on every cycle of the contradiction, the fitting assignment would satisfy it.
- **Why the monotone world is frozen.** A twisted not-all-equal colouring satisfies both clauses on every triangle. One exists exactly
  when the cubic dual graph has a 2-factor in the twist's dual class.

## Interpretation (not theorem)

- **The base map, with twists.** The three regimes of the base-three epic reappear as three ways a twist can act:
  - **frozen** worlds keep a vacuum in every twist (the monotone world);
  - **locally frustrated** worlds contradict everywhere;
  - **tiling** worlds keep a vacuum only in the twists where it closes around the surface.
  - In the third regime the twist is the whole story: it decides whether the world can contradict at all, and every contradiction
    runs around the surface.
- **The two-literal pattern survives at three.** On the two-literal side, a contradiction is a loop along a class the twist makes odd.
  Here a minimal contradiction is a winding set of triangles, not a cycle of implications. Yet it runs along classes that the twist,
  measured from the vacuum's own twist, makes odd.
- **What three places add.**
  - **The fitting twist.** It is no longer the untwisted one. It is set by the tiling's period and the torus's size: (1,1) on odd
    tori and (0,0) on even ones for many placements.
  - **Crosses.** Contradictions can be crosses as well as lines.
  - **Rare contradictions.** In the rare regime they are large and come only as crosses.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| A three-literal world needs correlated polarities for the twist to matter | `LOOP-SHIELD-20261023-001` recommendation | **Necessary but not sufficient.** The exact condition is complement closure. Without it, a "twist" is a defect line: "x or 1-in-3" and "1-in-3 / not-all-equal" contradict on planar patches with a contractible seam. |
| Not-all-equal on four places with a visible spoke is the natural three-literal world | Scoping for this epic | **Frozen.** It never contradicts on small triangular tori. In the base map's terms its knots are one-sided ("not all on", "not all off") and keep a vacuum. |
| Three-literal contradictions are not implication cycles, so the two-literal topology has no counterpart | The previous recommendation's framing | **Partly false.** They are not cycles, but in tiling worlds they wind, and lines run along classes the relative twist makes odd. |
| The twisted sector is the untwisted one plus a seam | Implicit in the two-literal work | **Not at three places.** The vacuum's own twist depends on the tiling and the torus size. Contradictions are governed by the twist relative to it. |
| Twisted not-all-equal colourings exist on every small triangular torus | The first draft of A's Proposition 4 | **False** on four two-row tori with shear 1, caught by its own check. The world is still frozen there, by enumeration of every x. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A twist is a class exactly for complement-closed contacts | Testing whether seams are gauges | Elementary; new to the program |
| The monotone world contradicts only without a dual 2-factor in the twist's class; frozen on small tori | Not-all-equal colourings as dual 2-factors | Classical correspondence, twisted reading new to the program; moderate folklore risk |
| Tiling forces every minimal contradiction to wind, along classes odd for the relative twist | A lifting argument | New to the program; moderate folklore risk (tilings with global obstructions are a common theme) |
| The census: 66 local and 54 tiling placements, the regimes, lines and crosses | B, exhaustive certificates and sampled frequencies | A recorded computation |

**Did the perspective do real work?** Yes.
- **The question came from the programme.** Asking for the three-place counterpart of a shielding loop produced the
  complement-closure condition and the census.
- **The winding theorem.** It is the topological content: a contradiction that cannot be local must carry homology, and the homology
  it carries is fixed by the twist.
- **What was standard.** The satisfiability solving and the lattice bookkeeping.

## Recommendation

| Option | What it would do | Interest |
| --- | --- | --- |
| **1. Continue: do three-place lines obey the dual-pair identity?** (recommended) | In an intermediate placement (62, 109 or 155), define the line event: the world contradicts and every minimal contradiction lies along c, with all minimal sets enumerated on small tori. Then test whether a twist and that twist plus the dual of c give equal probabilities, as two-literal lone loops do. | 2/3 |
| 2. A shared note on twisted tiling worlds | The complement-closure condition, the winding theorem and the census, for readers in random constraint satisfaction and tilings | 1/3 |
| 3. The rare regime | Find out whether the rare placements' contradictions vanish at scale (a frozen limit) or stay as large crosses | 1/3 |

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — twisted three-literal worlds | **Successful** | A twist is a class exactly for complement-closed contacts (proved). The census splits all 120 placements into local and tiling (exact certificates). For 30 three-place tiling placements the twist decides contradiction. Every minimal contradiction winds, along classes the relative twist makes odd (proved, and 1746 of 1746 lines measured). |
| Local direction — fair three-place contacts on the triangular lattice | Continue | The tiling worlds are the three-place counterpart of the twisted two-literal worlds, with line events defined. |
| Broader exploration — exact relations of twisted worlds | Bridged | The two-literal laws (odd loops, walls, shielding) now have a candidate home at three places. Other lattices and contacts with four hidden places are not assessed. |
| Long-term goal — emergence from logic at the two-literal/three-literal boundary | Capability gained | A three-literal world in which contradiction is global and topological, and in which the twist decides it, as the thesis's "infinite cycles" picture asks. The missing bridge: whether the exact two-literal relations, such as dual pairs, survive there. |
| Next recommendation — dual pairs for three-place lines | **Next step:** Continue. One fresh epic: enumerate all minimal contradictions on 4 × 6 and 6 × 6 tori for one or two intermediate placements. Estimate the line-event probabilities for each twist and test whether q and q + PD(c) agree. Stop if the line event cannot be computed exactly or the samples cannot resolve the comparison. | The cheapest discriminator for "does shielding survive at three places". |
| Interest — that next step | **2/3 — Promising** | The rare-loop analogy now has a theorem behind it (lines run along odd classes). The raw scoping counts look paired, for example 16 and 16 line cores in twists (1,0) and (1,1) for placement 155 on 6 × 6. Main uncertainty: the line event needs all minimal contradictions, which may be costly, and sampled probabilities may not resolve exact equality. |
| Execution — that next step | Deferred to the owner | Bound: one epic, with minimal-set enumeration on small tori and about 10⁵ samples per twist. Stop if enumeration is infeasible beyond 6 × 6. |
