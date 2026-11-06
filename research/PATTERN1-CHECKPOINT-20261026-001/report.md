# Pattern-1 construction checkpoint (p = 7, r = 6)

Ticket `PATTERN1-CHECKPOINT-20261026-001`, 2026-10-26. Experiment `PATTERN1-CHECKPOINT-20261026-001-E001` (frozen contract,
run once). **Verdict: supported.** The checkpoint stops here for the owner's decision.

## The request

Relayed by a peer session as the owner's instruction: "try the p=7, r=6 construction for the class-(K) result, check the
predicted counts 133 and 2737, and stop to report at that checkpoint." The predictions come from scouting lane
`NEXT-DIRECTION-SCAN-20261026-001A`. The construction to test is `COPRIME-CLASS2-20261026-001D` §3: projectors, balanced
basing paths and disk framings, built end to end rather than recomputed abstractly or found by an insertion search.

## Group and action

- p = 7, r = 6, ζ = 3 (a primitive sixth root of unity mod 7).
- **N** is the free class-2 group of exponent 7 on e₁, e₂, e₃:
  - A = span(z₁₂, z₁₃, z₂₃) and B = span(e₁, e₂, e₃);
  - the cocycle β is upper triangular: β(e₁, e₂) = z₁₂, β(e₁, e₃) = z₁₃, β(e₂, e₃) = z₂₃.
- **G = N ⋊ C₆.** The generator acts on e₁, e₂, e₃ by ζ = 3, ζ² = 2, ζ³ = 6, and on z₁₂, z₁₃, z₂₃ by ζ³, ζ⁴, ζ⁵. This is class (K)
  with pattern 1: three distinct characters, every pair a hard pair.
- **N_ψ** is counted for the onto meridian character ψ (sector ψ¹). It is the number of
  (c₁, c₂, c₃) ∈ H¹(M; F_ζ) × H¹(M; F_ζ²) × H¹(M; F_ζ³) with c₁ ⌣ c₂ = 0, c₁ ⌣ c₃ = 0 and c₂ ⌣ c₃ = 0.
  It is a fixed-character kernel count, not a total homomorphism count.

## The fixtures

**Base knots** (braid closures with cp_lib's words), with +6 surgery:
- K₂: 3₁ # 3₁ # 6₁ # 5₂, for the slots x_u, x_v, y, t.
- Digon: 3₁ # 3₁ # 6₁ # 6₁ # 5₂ # 5₂.

Mod 7 their Alexander roots are ζ^{±1} (3₁), ζ^{±2} (6₁) and ζ³ (5₂).

**Reference loops.** In each summand, a band loop around two adjacent arcs whose cocycle values differ. The first such pair is
taken in each summand, subject to independence within each slot character.

**Pure leaves (eigenprojectors).** Each leaf is a comb of band-summed copies of the reference loop:
- copy j is repeated m_j = 6⁻¹χ⁻ʲ mod 7 times, giving 21, 28 and 21 copies for χ = 3, 2, 6;
- the band of copy j winds j times around a strand of the summand;
- direction −1 was calibrated beforehand to give χʲ, that is, conjugation by tʲ.

**Balanced band sums.** ℓ_e = x_u − x_v is the comb at u, then a band routed above the diagram, then the comb at v traversed
backwards.

**Y-graphs.** Every leaf is 0-framed (its disk framing). Each Y-graph is surgery on its six-component link: the three leaves
plus 0-framed Borromean rings, each ring Hopf-clasped to its leaf's root through an edge routed above the diagram.

**Size.** K₂ has 7 components and 1,761 crossings; the digon has 13 components and 4,124 crossings.

**Reproducible descriptions.** `artifacts/PATTERN1-CHECKPOINT-20261026-001/…/surgery_K2.json` and `surgery_digon.json` give
the braid word, the arc choices and every component as a 3D polygon with its framing.

## Results

| Run | H₁ | dim H¹ for χ = 3, 2, 6, 4, 5 | N_ψ (sector ψ¹) | Sector ψ⁵ | Prediction |
| --- | --- | --- | --- | --- | --- |
| **K₂, projector construction** | Z/6, ψ onto | 2, 1, 1, 1, 2 | **133** | 2401 | 133, 2401 ✓ |
| **Digon, projector construction** | Z/6, ψ onto | 2, 2, 2, 2, 2 | **2737** | 117649 | 2737, 117649 ✓ |
| K₂ base alone | Z/6 | 2, 1, 1, 1, 2 | 2401 | 2401 | ✓ |
| Digon base alone | Z/6 | 2, 2, 2, 2, 2 | 117649 | 117649 | ✓ |
| Digon, unbalanced band (one winding) | Z/6 | 2, 2, 2, 2, 2 | 361 | 117649 | ✓ |
| K₂, reversed windings | Z/6 | 2, 1, 1, 1, 2 | 2401 | 133 | ✓ |
| K₂, unprojected single copies | Z/6 | 2, 1, 1, 1, 2 | 133 | 133 | ✓ |

**Further checks.**
- In both fixtures every leaf's functional is nonzero exactly on its slot character.
- In the digon:
  - ℓ₁ = ℓ₂ on V_ζ (balanced);
  - y₁, y₂ are independent, and so are t₁, t₂;
  - with the unbalanced band, ℓ₂ = ref_u − 5·ref_v (gain ζ⁻¹), not proportional to ℓ₁.
- Surgery on the clasper links alone, with the base knot forgotten, has trivial first homology.

**What the controls show.**
- The projectors confine the change to the predicted sector: with pure leaves the ψ⁵ sector keeps its base value. Reversing
  the windings moves the change from sector ψ¹ to sector ψ⁵, and unprojected copies change both.
- Balancing matters: a single winding on one band changes 2737 to 361.

**Machinery controls, rerun in the frozen run, all pass.**
- On 3₁, 4₁, 5₂ and 6₁, the cohomology dimensions equal cp_lib's.
- Lane A's two insertion knots give 938791 and 49735.
- Chirality and framing agree with cp_lib: 121 maps to A₅ from +1 surgery on the trefoil, 1 from −1 surgery.
- The Borromean rings give 138 maps to S₃ from the link group and 48 from its 0-surgery T³.
- A Y-graph realized as its six-component link reproduces the cabled-Borromean braid insertion: 938791, H = 18865, H₁ = Z/6.
- The winding calibration holds for j = 1 and 2.

The total run time was 917 s.

## Counting method and reused code

- **New code**, in the experiment directory:
  - `pc_core.py`: polygons, generic projection, crossings with depth checks, Wirtinger arcs, relators x_j = x_o^{−s} x_i x_o^{s},
    Seifert longitudes, framing relators, linking matrices; twisted Fox calculus mod 7 with a per-generator ψ; the Heisenberg
    lifting obstruction (relator z-components on lifts, reduced modulo the image of the twisted Fox matrix); the kernel count from
    the three cup-product bimaps.
  - `pc_build.py` and `pc_fixtures.py`: the construction.
  - `validate.py`: the machinery controls.
  - `predict.py`: the gadget tensor counts 133, 2737, 361, 2401 and 117649.
  - `run.py`: the frozen run.
- **Reused read-only** from `COPRIME-CLASS2-20261026-001B-P001`: cp_lib's group arithmetic (`Group`), braid words,
  `connected_sum`, and its presentation and cohomology, used for comparisons.
- **Scoping before the freeze** is disclosed in the contract and in `scoping/`. No fixture count was computed before the
  freeze.

## Gaps between these fixtures and the uniform theorem

- **Scope of the test.** It covers two small graphs at one (p, r). The construction's correctness for every graph rests on the
  proof in `COPRIME-CLASS2-20261026-001D` §3. The polynomial size bound is not tested.
- **The surgery model.** The Y-graph surgery is computed through its six-component link. That equivalence is cited (Habiro;
  Garoufalidis–Goussarov–Polyak) and checked here against the braid insertion; it is not reproved.
- **Where the projectors were tested.** At these bases each slot character is carried by its own summand type, so sector ψ¹
  would give 133 even without projectors (the unprojected control). The projectors are tested through purity and through
  sector ψ⁵. Bases where one summand carries several slot characters, as in patterns 2 and 4 or a general class-(K) group, were
  not built.
- **What remains of the class-(K) route.** Writing out the sector isolation, knot groups when some κ_{1,σ} ≠ 0, and p = 2 and
  extension fields remain open. This checkpoint confirms only the realization step for pattern 1 at p = 7, r = 6.
- **Review.** The same research program wrote the code, the construction and the predictions; there has been no external
  review.

## Assessment

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: the pattern-1 construction checkpoint | **Status:** Successful | Both fixtures match their predictions (133, 2737), and every control and machinery check passes. |
| Local direction: realizing class-(K) gadgets by explicit surgeries | Continue, if the owner chooses | The missing end-to-end pattern-1 instance now exists, with the projectors, basing and framings exercised. |
| Broader exploration: the complexity program | Known alternatives (unchanged) | Nilpotent groups on links, an S₄ tangle scan, and signed-atom Holant networks, each 1/3. |
| Long-term goal: the complexity side of the 2-versus-3 thesis | No new capability | The step confirms a construction; the dichotomy itself is unproved. |
| Next recommendation: the class-(K) dichotomy | **Next step:** Continue, with a short epic proving the p-odd, prime-field dichotomy for class (K) (lane A's Bulatov–Grohe route), now that its realization gate has passed | Owner's decision. A first task would be writing out the sector isolation (block-diagonal sum, Goldberg–Grohe–Jerrum–Thurley Lemma 6.4). |
| Interest | **2/3: Promising** | Unchanged: the gain is generality, and the knot-group case with κ_{1,σ} ≠ 0 is still open. |
| Execution | Stopped at the checkpoint | As instructed; nothing beyond the two fixtures and their controls was run. |
