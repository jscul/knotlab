# Counting one twist off the bound

Epic `TWIST-COUNT-20261030-001`, 2026-10-30.

## The question

- **The owner's request (2026-10-30).** "Yes, please continue." This approved the recommendation of `SEYMOUR-COUNT-20261030-001`.
  - Keep a three-fold space's incidence graph, and change its signs away from the knot's own class, so that the space becomes colourable.
  - Is counting still easy for every sign class (the ease lives in the graph), or hard for some family (the knot's own impossibility is the
    boundary)?
- **Scoping (not evidence).** In the Hadamard basis every planar piece is a matchgate under any signs. A piece carrying the knot's own signs
  keeps a trisum junction a matchgate; two twisted pieces at one square do not.
- **Intuitions targeted:**
  - the two/three boundary as emergence, in counting;
  - interference: signs that cancel.

**The evidence:**
- [The knot's junction is a similitude](../../proofs/TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude/proof.md)
  (A, proof with exact and symbolic computations);
- [A junction crosses wires softly, never sharply](../../proofs/TWIST-COUNT-20261030-001B/TWIST-COUNT-20261030-001B-P001_branched_twists_and_crossovers/proof.md)
  (B, proof with exhaustive computations).

## Outcome in one paragraph

**Counting stays easy well past one twist. It can only become hard where twists branch, and there the knot's junction crosses wires softly
but never sharply.**
- **The junction is a similitude (A, proved).**
  - At a trisum square, a side carrying the knot's own signs acts on the other closed side as a similitude of the matchgate identity.
  - Its multiplier is α² + αβ + β² = |α + β e^{iπ/3}|², the norm of the side's leaning split at the knot's own angle.
- **Unbranched twists are easy (A, proved).** Unless some square has twisted sides on all three branches, a root exists from which every
  junction is a matchgate. Counting is then polynomial: one Pfaffian per planar piece (FKT).
  - This covers one twist and twists along any path of the tree.
  - The knot's own class is the case with no twists at all.
- **No sharp crossing (B, proved).** A not-all-equal line forbids one pattern only, so with nonnegative counts the square's lines can never
  force a relation between the host's two line-neighbours without pinning them. No junction is a crossover; the square's points can carry a
  wire, its lines cannot.
- **Soft crossings (B, exact).** Twisted truncated-octahedron pages give 256 junctions that pass both wires with small weight, off the
  matchgate class. One has straight entries (40000, −1112, 3336, −192).
- **Hardness is not proved.**

## What was proved

| Result | Content |
| --- | --- |
| A, Lemma 1 | #col = (3/2)^n Σ_χ (−1/3)^{\|χ\|/2} (−1)^{\|σ∩χ\|} for every signing; one flipped incidence gives #col(H − L). |
| A, Lemmas 2–3 | Branch tensors are even, and planar pages are matchgates under any signs. Untwisted means the split form. Twistedness is inherited. |
| A, Theorem 4 | Junction with an untwisted side: MGI(ĤW) = ±(α² + αβ + β²) MGI(ĤF). |
| A, Lemma 5, Theorem 6 | A good root exists iff no square has three twisted branches; then counting is polynomial. |
| A, Proposition 7 | Junctions of two twisted pages can leave the matchgate class (exclusive crossings included). |
| B, Lemma 1, Theorem 2 | The junction on a slice; the square's lines carry no hard wire, so no junction is a crossover (nonnegativity essential). |
| B, Proposition 3 | Soft crossings exist (truncated-octahedron pages); prisms and Omni(K₂,₃) give only exclusive crossings. |

## Reading

- **The knot's mechanism, seen through a twist.**
  - Easy counting on the knot's spaces came from determinants. Seen through a twist, it is a local property of every junction: a side with
    the knot's signs is a similitude at the knot's own angle.
  - Twists may wander along a path of pieces without breaking it. Only a branching of twists does.
- **Interference, again.** The soft crossing exists because signs cancel the turning paths exactly while letting the crossing path through.
  - That is the interference that separated two from three in earlier epics.
  - The lines' not-all-equal rule still forbids a sharp crossing: they forbid one pattern only, and counts cannot cancel.
- **Where the boundary would be.** If soft crossings can be sharpened by interpolation, counting is #P-hard exactly where twists branch.
  Easiness would then be a property of the knot's sign class together with the tree of pieces, not of the graph alone.
- **Provenance.**
  - Planar not-all-equal counting and matchgates are classical (Valiant; Cai–Gorenstein).
  - The similitude, the no-hard-wire theorem and the soft crossings were found in no source.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — counting one twist off the bound | **Status:** Partially successful | Easy for every unbranched twist (proved). The matchgate mechanism provably stops at branched twists. A junction is never a sharp crossover but can be a soft one. Hardness not settled. |
| Local direction — counting under twisted signs on the knot's graphs | Continue (one concrete step) | The soft crossing is exact and its weights look multiplicatively independent, so interpolation is the natural next attempt. |
| Broader exploration — counting on and near Seymour's bound | Known alternatives | Mapped: the bound (determinants), unbranched twists (matchgates). Unmapped: branched twists, deficiency ≥ 1, non-regular systems. |
| Long-term goal — the two/three boundary in counting | Capability gained | The tractable island is larger and explained locally: a junction similitude at the knot's angle. The hard side is reduced to sharpening one gadget. |
| Next recommendation — soft crossings to hardness | **Next step:** Continue, as a fresh epic. Prove that counting colourings under branched twists is #P-hard. Sharpen the soft crossing by interpolation: odd series compositions give straight entries (a^k, b^k, c^k, d^k), and polynomially many k recover the sharp crossover. Reduce from colouring counts of general cubic signed systems. | That would make the boundary two-sided: polynomial on the bound and along unbranched twists, #P-hard where twists branch, with the knot's sign class as the dividing line. |
| Interest — that recommendation | **3/3 — Hot** | The gadget is in hand and exact. Its straight entries 2⁶5⁴, −2³·139, 2³·3·139 and −2⁶·3 have independent prime exponents (5, 139, 3), which is the lattice condition interpolation needs. Main uncertainties: a citation (or proof) that the non-planar source is #P-hard on cubic bipartite instances; routing the wires inside cubic bipartite Pfaffian hosts. |
| Execution — that next action | Deferred to the owner (fresh epic) | First discriminator: the lattice condition for the exhibited gadget and the plumbing of one crossing inside a planar brace, checked against direct counts. Stop if the source problem's hardness or the plumbing fails. |

**Recommendation.** **Continue**, as a fresh epic: soft crossings to hardness (3/3). Two alternatives were considered.
- **A polynomial algorithm for branched twists (1/3).** It would need a tractable class beyond matchgates. Soft crossings off the matchgate
  class make that unlikely.
- **A write-up of the counting line (1/3).** Seymour's bound and unbranched twists are coherent, but the boundary is one-sided until the hard
  side is settled.
