# Pair failures past clean edges: linear flows in class 3, locality up to relabeling in class 4

Epic `CLASS4-PAIRS-20261028-001` (2026-10-28).

**The question.** The owner continued the previous epic's recommendation ("Yes, let's continue"): class-4 locality and flows for
the 26 census algebras whose only failing clean-edge condition is (K), pursued to a theorem, a counterexample or a precise
obstruction. The assumptions are those of `COPRIME-PAIRS-20261027-001`: graded, grading-preserving action, class ≤ 4, p ≥ 5,
r | p − 1, H₁(M; F_p) = 0, bounded sectors, S³_{d/p}(K) surgeries.

## Outcome

1. **Class 3: linear flows** (`CLASS4-PAIRS-20261028-001A`, Theorem 8, proved).
   - Suppose an edge fails only the vertex-root condition (V₃), and its dual slot carries no layer-1 data. Its vertex equations are
     still a flow conserved at every vertex (F §1). Now the flow, and every constraint on the dual slot's data, is *linear* in that
     data.
   - Each Fourier-dual edge weight is then Σ_{π₁} |U(π₁)| · [a linear form vanishes on U(π₁)]: a non-negative count. The Brunnian
     rank witness applies as before.
   - Neither off-diagonal vanishing nor diagonal bilinearity is needed: those were Theorem 6's conditions (F0)–(F2).
   - **Census.** 12 of the 16 vertex-root algebras have such an edge, 8 of them new: free class 3 on (1, 1, 4) at d = 5; on
     (0, 1, 2) and (1, 2, 2) at d = 6; on (1, 1, 6) at d = 7; on (1, 1, 8) at d = 9; on (2, 2, 8) at d = 10; on (0, 2, 4) and
     (2, 4, 4) at d = 12. With Theorem 6, the whole vertex-root family is decided, and 105 census algebras remain open.
2. **Class 4: locality up to relabeling** (`CLASS4-PAIRS-20261028-001B`, experiment). Supported.
   - Free class 4 on (1, 1), (0, 1, 1) and (1, 1, 1) at d = 5, on seven graph shapes up to K₄ in three configuration types: 63
     configurations.
   - In every one, the global and assembled local degree-4 systems have equal linear parts. Their constant parts differ by an
     element of the column space, which is a proper subspace in every configuration. So the counts agree.
   - The relabeling is needed in 35 of the 63.
   - Controls: the cumulative design fails locality, already below layer 4. An algebra whose dual slot has layer-1 data fails the
     linear structure.
   - Limits: graphs up to K₄. For (1, 1, 1), no sampled datum admits a degree-3 completion, so its counts agree by both being
     zero.
3. **Class 4: the conditional theorem** (`CLASS4-PAIRS-20261028-001C`, Theorem 7 and Corollary 7.1).
   - Theorem 7 is an implication. Assume (L4) locality up to relabeling, (LS) linear flows on single edges, and (RW) the rank
     witness. Then counting is #P-hard.
   - With non-conserved endpoint terms, the Fourier dual uses independent potentials at the two ends, and linearity still makes it
     non-negative.
   - Corollary 7.1 proves (LS) and (RW) for free class 4 on (1, 1), (0, 1, 1), (1, 1, 1) at d = 5 and their d = 10 versions. In
     these algebras the layer-k components have character k. So each block's data sit at one character (an abelian lift), the dual
     slot has no layer-1 data, and it has no degree-4 equations.
   - So six census algebras are #P-hard **if (L4) holds**. (L4) is supported by B, not proved.
4. **Census** (850 algebras):

   | status | count |
   | --- | --- |
   | polynomial | 10 |
   | hard by the triple theorem | 511 |
   | decided by reduction and inert transfer | 153 |
   | clean edges (Theorems 4, 5) | 55 |
   | conserved flows (Theorem 6) | 8 |
   | linear flows (Theorem 8) | 8 |
   | open | 105 (26 of class 3, 79 of class 4) |
   | of the open: hard if (L4) holds (Corollary 7.1) | 6 |

## How the class-4 picture changed

- **A coordinate artifact, not a leak.** The first path test showed vertex equations of a non-incident vertex changing with
  another edge's data. For each configuration, a unique translation of the first edge's degree-3 slot-2 coordinates, linear in the
  other edge's data, explained it exactly.
  - Mechanism: the second edge's bundle-1 conjugator has a degree-3 part at a character outside slot 1's roots. It moves that
    edge's zero strands (junctions). Zero-jump blocks pass the move upstream, where it is absorbed as a change of the preceding
    dual slot's leaf.
  - A reading-strand gauge did not remove it. Comparing equation values at fixed coordinates is the wrong test in class 4.
- **Uniform conjugation is a gauge.** Every block between two moved strands is conjugated by one element, which leaves its
  equations unchanged. An edge passing over an isolated vertex was exactly local.
- **The right test is affine.** For fixed degree-≤2 data, the degree-4 equations are affine in the degree-3 data. Locality up to
  relabeling means: equal linear parts, and constant parts differing by an element of the image. This is the indeterminacy of a
  Massey-type obstruction. Counts are then equal for every fixed lower datum.
- **Thin solution sets are not a failure.** For free class 4 on (1, 1, 1), most configurations admit no degree-3 completion at all:
  [X, ·] maps an 8-dimensional space into an 18-dimensional one. The global and local systems agree on that too.
- **Summand terms.** A block whose data sit at one character has an abelian representation, so no local obstruction in any class.
  The (1, 2, 3) control in class 3 shows such terms appearing when the dual slot has bracketing layer-1 data.

## Probes after the frozen run

These are unfrozen scoping probes, five shapes × three configuration types each, run to sharpen the obstruction. They are not
evidence for any claim.
- **Every (K)-only edge at d = 5 is now tested.** On at most three generators, up to scaling characters by units, the edges that
  fail only (K) modulo γ₄ are the experiment's three and one more: free class 4 on (1, 2), edge (1, 2).
- **That edge is exactly local.** In 15 of 15 configurations the global and local systems were equal, and again after scaling by 2
  (free class 4 on (1, 3), edge (3, 1)).
  - Its slot-1 twists sit at characters 4 and 0, outside slot 2's roots {2, 3}, so the absorption seen in the experiment is not
    available.
  - But the degree-3 data enter no degree-4 equation there (A = 0), so this is a weak test.
- **Edges that are not clean modulo γ₄ break locality.** These also fail (B₀) and (V₃): free class 4 on (1, 2), edge (2, 1); on
  (0, 1, 2), edges (1, 2) and (2, 1). They fail in two ways:
  - single-edge varieties fail on the graph's variety;
  - the constant parts differ outside the column space on the private variety, in 11 configurations across the four probes. The
    counts differ in 2, both for free class 4 on (1, 2), edge (2, 1), or its copy scaled by 2.
  - These edges are outside the hypotheses, and their lower vertex equations do not vanish, so they say nothing against (L4). They
    show that the column-space test detects failures at layer 4, which the frozen controls did not.
- **The linear parts agreed in all 90 probe configurations,** clean or not. Only the constant parts ever moved.
- Scripts, logs and a summary are in `probes/`.

## The precise remaining obstruction

- **(L4) unproved.** A proof needs an absorption lemma: every junction twist either lands at a character carried by a free
  degree-3 datum of the block that absorbs it, or leaves no trace. Equivalently, the degree-4 obstruction of the gadget knot is
  local modulo its indeterminacy.
  - The twists are brackets of at least two leaves of degree 3, so they depend only on degree-≤2 data. That fits the linear parts
    agreeing while only the constant parts move.
  - In the experiment's algebras the twists sit at character 3 = −γ, because 2γ + α ≡ 0 mod 5.
  - Every (K)-only edge at d = 5 is consistent with the lemma, and every non-clean edge tested breaks locality.
- **The other twenty (K)-only algebras** (d = 7, 9). 14 of them have an edge whose dual slot has no layer-1 data. They need the
  (LS) analysis (characters no longer equal layers) and (L4). Testing them needs summand braids at d = 7, 9, which the library
  lacks.
- **Class 3** (26 open). (B₀) with (V₃): the private leaves bracket below γ₃, so vertex copies get a non-central layer-2 shift.
  (B₂′) at a nonzero character.
- **Class 4, other mechanisms** (53 open besides the (K)-only family), among them the cross-layer algebra free class 4 on
  (a, −a) at order 3.

No polynomial counterexample was found.

## Challenged assumptions

- **"Class-4 gadgets leak across the graph."** Only in coordinates. Counts are local up to relabeling in every configuration
  tested on an edge that fails only (K).
- **"Flows must vanish off the diagonal."** No: linearity in the dual slot's data makes the dual non-negative.
- **"Vertex flows must be conserved."** No: independent potentials at the two ends work.
- **"A canonical gauge makes equation values comparable."** No: junction twists relabel degree-3 data of other edges in any gauge.

## Literature

The boundaries are those of the predecessor epics: Samperton–Weiss (bounded H²), Galindo (unbounded homology),
Kuperberg–Samperton, Rowell, Moussard, Matei–Suciu, Nosaka. Bulatov–Grohe via Cai–Chen–Lu, Theorem 2.1, is used throughout.

One targeted search, for the closest classical analogue of (L4):
- Krushkal showed that Milnor's μ̄-invariants are additive under band sum of links separated by a 2-sphere, modulo the gcd of the
  two indeterminacies ("Additivity properties of Milnor's μ̄-invariants").
- I found it through secondary sources: arXiv 1812.03319 and arXiv 1603.09067. I did not read the original or verify its
  publication details.
- It has (L4)'s shape: additivity modulo indeterminacy. The difference is that the gadget's vertex blocks are shared between
  edges, so there is no separating sphere.

Novelty remains a candidate claim. Folklore risk:
- Theorem 8: medium. Positivity of character sums of linear forms is classical; using it here is the delta.
- Theorem 7: medium, and conditional.

## Gaps

1. (L4) for class 4, on all graphs: the absorption lemma above.
2. The 105 open census algebras (6 conditionally decided) and everything beyond the census: class ≥ 5, non-graded algebras,
   p = 2, 3.
3. The census covers free algebras on at most three generators with d ≤ 12.
4. No human or external review.

## Work ratio

Since the previous checkpoint:
- **Artifacts that changed a conclusion (3):** Theorem 8; the relabeling form of class-4 locality with its experiment;
  Theorem 7 with its corollary.
- **Scoping that sharpened the obstruction:** the post-run probes.
- **Administrative:** the closure ledger and records.

## End-of-epic assessment

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: the 26 class-4 census algebras failing only (K) | **Status:** partially successful | Six are decided if (L4) holds. A frozen experiment supports (L4) on graphs up to K₄, and the mechanism is identified: relabeling, the indeterminacy of a Massey-type obstruction. The twenty at d = 7, 9 are not treated. As a by-product, Theorem 8 decides the whole class-3 vertex-root family. |
| Local direction: gadget counts layer by layer | Continue | Layers ≤ 3 are theorems. At layer 4, every (K)-only edge at d = 5 is local up to relabeling, and every non-clean edge tested breaks locality. What remains is one lemma, not a new gadget design. |
| Broader exploration: complexity of 3-manifold invariants | Known alternatives | Samperton–Weiss (bounded H²) and Galindo (unbounded homology) cover other regimes. Krushkal's additivity of μ̄-invariants modulo indeterminacy is the closest classical analogue of (L4). |
| Long-term goal: the complexity side of "two versus three" | Capability gained | A pair interaction survives the Fourier dual whenever the dual slot's data enter linearly. Class 4 so far adds only a relabeling. Not an emergence result: r counts action characters. |
| Next recommendation | **Next step:** Continue, with a fresh epic proving (L4) | Prove locality modulo indeterminacy for zero-jump gadgets whose edge is clean modulo γ₄. Use an additivity argument after Krushkal, plus an absorption lemma for junction twists. First discriminator: write the relabeling explicitly on the star K₁,₃ for free class 4 on (1, 1), where three twists meet one vertex, and check that it is a translation of degree-3 data. A proof decides six algebras outright. With an (LS) census and d = 7, 9 summand braids, it would reach the other twenty. Alternative: the class-3 (B₀) and (B₂′) families (26 open). |
| Interest: that recommendation | **2/3 (Promising)** | Evidence: every (K)-only edge tested is local up to relabeling, every non-clean edge breaks it, and a classical analogue exists. Main uncertainty: shared vertex blocks leave no separating sphere, so Krushkal's argument does not transfer directly; and (LS) for the d = 7, 9 algebras is unexamined. |
| Execution: that next action | Deferred to the owner | This epic stops at its stated endpoint: Theorem 8 proved; Theorem 7 and Corollary 7.1 proved as an implication; (L4) supported by a frozen experiment and bounded by the probes. No successor created. Reassess at the star: if the relabeling there is not a translation of degree-3 data, the lemma needs a new idea. |
