# Criticality at the base

Epic `BASE-CRITICALITY-20261022-001`, closed 2026-10-22.

## The question

`EMERGENCE-BITS-20261021-001` found an unexpected result. A world woven from
not-all-equal knots on a square torus with an odd side holds a fixed amount
of hidden fact at every size, though no patch and no single cycle holds
anything. The owner approved the recommended continuation, with four
questions:
1. Does the value depend only on shape (more aspect ratios, sheared tori)?
2. How does it compare with Grimmett's randomly oriented lattice?
3. What happens in three dimensions?
4. Can it be proved bounded away from 0 and from infinity?

**The evidence:**
- [Fair distinctions make percolation](../../proofs/BASE-CRITICALITY-20261022-001A/BASE-CRITICALITY-20261022-001A-P001_percolation_reduction/proof.md)
  (A, proof);
- [Shape, rotation and the percolation mechanism](../../experiments/BASE-CRITICALITY-20261022-001B/BASE-CRITICALITY-20261022-001B-E001_shape_and_mechanism/contract.json)
  (B, confirmatory experiment;
  [result](../../artifacts/BASE-CRITICALITY-20261022-001B/BASE-CRITICALITY-20261022-001B-E001_shape_and_mechanism/result.json)).

## The mechanism (proved in A)

1. **Fair distinctions orient the hidden pair-world by coin flips.**
   - **The recolouring.** For any graph and any two-colouring g,
     τ = h ⊕ g turns not-all-equal constraints with fair visible spokes into
     uniformly random implications on the bichromatic edges, plus random
     monotone two-literal clauses on the monochromatic edges (the seam).
2. **Reach through coin-flipped implications is percolation at exactly 1/2.**
   - **The coupling.** The set reachable from any vertex set has the law of
     its bond-percolation cluster at 1/2. This is the coupling behind
     Grimmett's model.
   - **Gadgets.** Contacts in series or parallel reach at their traversal
     probability.
3. **Blocking.** If no directed path crosses the cut-open torus in one
   direction, the world is consistent. So inconsistency needs crossings both
   ways. The converse fails.
4. **Three regimes.**
   - **Below the bond threshold** emergence vanishes: the honeycomb, and
     contacts in series.
   - **At 1/2 on the square lattice** it stays bounded (Russo–Seymour–Welsh).
   - **Where two-way contacts percolate** it diverges.

## What the experiment found (B, supported)

| Question | Result |
| --- | --- |
| Shape, not size | At exact aspect ratios 2/3, 4/3, 2, 4 (sides 9 to 45), E is 0.23, 0.72, 1.16, 2.31 bits. The drifts are 0.007–0.028 bits per doubling of size; the ratio-4/3 drift (0.028 ± 0.009) is about 3σ. |
| Rotation | Rotated squares match axis-aligned ones: 0.838 against 0.837 bits (difference 0.001 ± 0.011). Rotated 1:2 tori match too (difference −0.024 ± 0.017). |
| Shear | A sheared family (shape 1/3 + 2i) is flat: slope −0.019 ± 0.013. Its mirror image, an isomorphic graph, differs by 2.5σ, which calibrates the noise. |
| The coupling | The chance of no directed up-crossing equals the percolation non-crossing chance at every size (\|z\| ≤ 2.2). |
| The mechanism in two dimensions | Below threshold: traversal 1/8 gives exactly 0; 27/64 falls 0.073 → 0.008 → 0.001 → 0. Above: 3/4 grows 5.5 → 8.7 → 11.5 → beyond 14.3 bits; 7/8 passes 14.3 at side 5; 0.67 grows 3.4 → 5.0 → 6.7 → 8.9. |
| Three dimensions | Cubic 3-tori grow from 1.24 bits (3 × 2 × 2) to 10.6 (3 × 4 × 4) to beyond 16.6 (3 × 6 × 6). The same happens at height 5. |
| What is left after crossings | Given crossings both ways, 18–41% of worlds stay consistent at every size: 0.18 on the widest tori, 0.34–0.41 on the narrowest. |
| Wide tori | E grows by about 0.575 bits per unit of aspect ratio, with intercept near 0 (heights 9 and 15). |

**Scoping notes** (disposable probes, not evidence):
- **Most contradictions are simple.** 93–97% of inconsistent worlds are
  certified by the simplest contradiction: one vertex reaching both ends of
  a negative seam edge and reached from both ends of a positive one.
- **Self-crossing columns grow slowly.** These are columns whose bottom
  vertex reaches its own top vertex; their number rises with size, from
  about 3 to about 7.
- **The wide slope** is 0.59–0.61 at heights 21 and 31.
  - If P(consistent) behaves as exp(−2πx·ratio), the slope gives x ≈ 0.064.
  - x = 1/16 would give 0.567 bits per unit ratio, within about 2%. This is
    suggestive only.

## Answers to the four questions

1. **Shape only?** Yes, in the tested range.
   - E is a function of the torus's shape: aspect ratio, rotation and shear.
   - Rotation invariance on a square grid is emergent isotropy, the usual sign
     of a conformally invariant critical point.
   - Two families drift slightly upward (up to 0.03 bits per doubling). A
     slow crossover cannot be excluded.
2. **Grimmett's model?** The comparison is exact. The coupling behind
   Grimmett's model at 1/2 gives the law of every one-direction reach.
   - Consistency is more than a crossing event: crossings both ways are
     necessary, but a large share of such worlds stay consistent by using the
     seam's clauses.
3. **Three dimensions?** Global emergence diverges.
   - **Why:** on the cubic lattice 1/2 lies far above the bond threshold
     (about 0.249). The same law that sits at criticality in two dimensions
     floods with contradictions in three.
4. **Bounds?**
   - **From infinity:** proved (A, Theorem 4(b)).
   - **From 0:** open. By the scoping notes it reduces to showing that simple
     certificates occur with probability bounded below. That needs joint
     control of forward and backward reach.

## The underlying theory (interpretation, not theorem)

**Fairness is criticality.**
- **The chain.** The visible distinctions are fair bits. Through the
  recolouring each one orients a hidden implication by a coin flip, and reach
  through coin-flipped implications is percolation at exactly 1/2.
- **Why the square lattice.** Its bond threshold is exactly 1/2 by
  self-duality. So the base logic, read with equal weight on every visible
  state, lands on a critical point with nothing tuned.
- **This answers the earlier question.** "Why does the square lattice hold a
  scale-free amount?" Because there, and only there among the tested
  surfaces, fairness equals the threshold.

**The hidden world is a pair-world, switched by triples.**
- **The pair-world.** Two-literal clauses on the hidden joints: implications
  everywhere, monotone clauses on the seam.
- **The switching.** The three-literal contacts let the visible
  distinctions orient it.
- **What emergence at scale is.** The surprise that this coin-flipped
  pair-world closes consistently around the world's odd cycle. At the
  critical point that chance depends only on the world's shape. The owner's
  2-versus-3 boundary appears here literally: the critical object is a
  pair-world, and the triples are what make it random.

**One number sets the phase:** the chance that a contact passes an
implication on, against the lattice's threshold.
- **Below** (the honeycomb; contacts in series), global emergence is
  forgotten.
- **At it** (the square lattice), it is scale-free, isotropic and set by
  shape.
- **Above** (dense contacts; three dimensions), contradictions flood the
  world.

**"Infinite cycles of logic that are universally influential."**
- **The previous epic** found three kinds: equality cycles, parity cycles,
  and global frustration on the square lattice.
- **This epic places the third.** It is a critical phenomenon, and its
  amount is a property of the world's shape, like a conformal invariant.
- **The boundary.** The lattices are declared, and nothing is said about
  space or physics.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| The square lattice's scale-free emergence is a special accident | `research/EMERGENCE-BITS-20261021-001/emergence_bits.md` | **Explained.** Self-duality puts its bond threshold exactly at the fairness 1/2 of the visible distinctions. |
| Scale-free behaviour must be tuned | The usual picture of critical points | **Not at the base.** Fair visible distinctions on a self-dual lattice are critical with nothing adjusted. |
| Global emergence is a crossing probability | The natural guess after the reduction | **False.** Two-way crossings are necessary, yet 18–41% of such worlds stay consistent at every size, by using the seam's clauses. |
| Only reversible contact carries emergence at scale | The base-three memory theorem (one-dimensional structures) | **Sharpened.** On surfaces, irreversible not-all-equal contact holds a scale-free amount exactly at criticality, none below it, and an unbounded amount above it. |
| Dimension plays no role at the base | Implicit in the base-level framing | **It does.** The same law in three dimensions is supercritical, and global emergence diverges. |

## Provenance and novelty

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Recolouring on any graph | Gauge transformations; the previous torus recolouring | Classical gauge; the reading is new |
| Reach is percolation at 1/2, with gadgets | Grimmett's model | Known coupling (Grimmett 2001; recorded by Zhelezov 2013); the gadget version is elementary |
| Blocking, two-way necessity, failure of the converse | Reading the recoloured instance on a cut torus | New to the program; no lattice version of random two-literal instances found |
| The three regimes | Standard percolation theorems applied | Classical ingredients; the reduction is new to the program |
| Shape dependence, rotation and shear invariance, the residual, three dimensions, the wide slope | The experiment | Empirical, new to the program |

**Folklore risk:**
- **Moderate** for the reduction: each step is standard, and the
  combination was not found in a bounded search.
- **Low** for the measured shape function.

**Did the base-level lens do work?** Yes.
- **What it posed.** It asked the question that exposed the mechanism: why a
  logic of fair distinctions should be critical.
- **The answer.** It is self-duality meeting fairness, which is not visible
  from the usual random-constraint framing.

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the proof and the experiment.
- 2 are administrative: this note and the ledger.

## Recommendation

| Option | What it would do | Interest |
| --- | --- | --- |
| **1. Which three-literal contacts are critical?** (recommended) | A census of the placed three-variable links on square tori with odd sides: which give zero, extensive, or scale-free global emergence. Start with "x or (h ≠ h′)". It is consistent exactly when its h ≠ h′ edges, an independent percolation at 1/2, form no cluster winding in an odd class. So its emergence is a classical critical wrapping quantity with a known conformal formula (Pinson 1994): an exact, independent test of the critical picture. | 2/3 |
| 2. The lower bound at criticality | Prove that simple certificates occur with probability bounded below, finishing "bounded away from 0" for not-all-equal worlds. | 1/3 to 2/3 |
| 3. Bank both epics | A self-contained note on emergence in bits and its critical regime; sharing is the owner's call. | 2/3 for reviewability |

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — criticality at the base | **Successful** | The mechanism is proved: fairness gives percolation at 1/2, and the square lattice is critical by self-duality. Shape dependence, rotation and shear invariance, the regimes in two and three dimensions, and the coupling are confirmed. The lower bound at criticality is open. |
| Local direction — not-all-equal worlds on surfaces | Practically complete except the lower bound | Every question the owner asked is answered or reduced to a named open step. |
| Broader exploration — the base-level theory | Known alternatives | Other contacts may realize other critical quantities; one reduces exactly to a classical wrapping probability. |
| Long-term goal — emergence from logic | Capability gained | Global emergence now has a phase diagram set by one number, and the base logic is critical without tuning on self-dual surfaces. |
| Next recommendation — which contacts are critical | **Next step:** Continue. A fresh epic: census of placed three-variable links on square tori with odd sides, with an exact test of "x or (h ≠ h′)" against Pinson's wrapping formula | If several contacts are critical with different universal functions, criticality is a generic property of fair three-literal contact on self-dual surfaces. If only not-all-equal is, it is special to that contact. |
| Interest — that next step | **2/3 — Promising** | The exact reduction for "x or (h ≠ h′)" makes a sharp, independent test available. The census is cheap. The uncertainty is how many classes appear. |
| Execution — that next step | Deferred to the owner | One bounded epic. Stop if the census finds no critical contact beyond not-all-equal and its relabelings. |
