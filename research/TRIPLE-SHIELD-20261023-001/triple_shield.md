# Does shielding survive at three places?

Epic `TRIPLE-SHIELD-20261023-001`, closed 2026-10-23.

## The question

The owner approved the main route: "Dual pairs for three-place line contradictions … the one result that could show an exact
two-literal law (shielding) surviving at three places, which is the thesis boundary."
- **The two-literal law.** A lone contradiction loop along c has the same count in the twists q and q + PD(c)
  (`LOOP-SHIELD-20261023-001`).
- **Why it might survive.** At three places, minimal contradictions of tiling worlds provably wind along classes the twist makes
  odd (`TRIPLE-TWIST-20261023-001`).
- **The design caveat the owner set.** Exactness needs every configuration of the visible bits, so the first step is exact
  counts on the smallest tori. If equalities appeared, the prize would be a seam-moving argument.

**The evidence:**
- [Exact dual pairs on the smallest tori](../../experiments/TRIPLE-SHIELD-20261023-001A/TRIPLE-SHIELD-20261023-001A-E001_exact_dual_pairs/contract.json)
  (A, frozen confirmatory experiment, verdict supported;
  [result](../../artifacts/TRIPLE-SHIELD-20261023-001A/TRIPLE-SHIELD-20261023-001A-E001_exact_dual_pairs/result.json));
- [Lone lines at two and three places](../../proofs/TRIPLE-SHIELD-20261023-001B/TRIPLE-SHIELD-20261023-001B-P001_lone_lines/proof.md)
  (B, proof);
- **scoping (scratch, not evidence):** the 3 × 3 torus for all 54 placements, and placement 63 on 3 × 4 and 4 × 3.

## Outcome in one paragraph

**Shielding does not survive at three places, and the dividing line is not clause width.**
- **Where the identity holds.** It holds exactly when each fair coin decides a contact on two places. These are the four
  orientation worlds: one clause per square-lattice edge, each with its own coin. There it is a theorem on every torus (B).
- **Where it fails.** It fails for every testable dual pair as soon as one coin decides three places. That happens in
  three-place worlds, by factors from 1.08 to 2114, and in two-literal worlds where one coin sets two or three clauses at once,
  by factors up to 2.
- **The evidence.** Exact counts of every configuration on 3 × 3, 3 × 4 and 4 × 4. The 4 × 3 torus repeats 3 × 4.
- **No other relations.** In these counts, no other exact relation between three-place twists appears beyond lattice symmetries
  and vertex flips.

## What was measured (A, supported)

Dual pairs are counted with a nonzero lone count, on the fresh tori. "Unexplained" means no map (lattice symmetry, then vertex
flip) relates the two twists.

| World | Each coin decides | Unexplained pairs | Equal | Example (4 × 4) |
| --- | --- | --- | --- | --- |
| Orientation (63, 119, 187, 207) | one clause on two places | 18 | all 18 (theorem) | 39168000 = 39168000 |
| Shared coin (18 placements) | two or three clauses on three places | 32 (18 independent) | none | 9205568 vs 8957504; 118368 vs 129184 |
| Three-place (30 placements) | one relation on three places | 66 (36 independent) | none | 640592 vs 4736; 75916416 vs 768848 |

- **Controls.** All passed. The torus test agrees across three sweep directions. Placement 63 matches the square-lattice
  orientation model of `TWIST-MAP-20261023-001` in every class and twist on every torus.
- **P1** (the cylinder theorem) holds everywhere.
- **The independent checker.**
  - It certified 1617 configurations both ways, with its own solver (a strip without an assignment, or a cyclic cover with
    one).
  - It recomputed the 216 exact 3 × 3 torus counts.
  - It verified all 452 symmetry flags with explicit maps that allow any change of hidden values. These maps found no
    explanation the producer missed.
- **Independence of the tori.** 4 × 3 turned out to repeat 3 × 4 with the axes swapped (216 of 216 rows), so "independent"
  counts 3 × 4 and 4 × 4 only.

## What was proved (B)

| Result | Content |
| --- | --- |
| Theorem 1 | A cylinder along c contradicts only in twists odd on c relative to every fitting twist: an even difference is a coboundary on the cylinder, and the shifted doubly allowed assignment works. |
| Lemma 3 | In a two-literal world, a contradiction whose cluster has a rank-two period lattice contains odd walks of every odd class. Ingredients: skew symmetry, directed ear decompositions and a cone argument. So it makes every cylinder along an odd class contradict. |
| Theorem 5 | In orientation worlds, "exactly one of the three cylinders contradicts" is exactly the line event of the shielding theorem, so dual pairs are equal on every torus. |
| Proposition 6 | From the exact counts, the identity fails for every tested pair of a world in which one coin decides three places. |
| Remark 7 | Why the wall does not transfer: it flips coins edge by edge, which needs each coin to touch exactly the two ends of one edge. |

**Why the identification mattered.** The first event tried, "the cylinder along c contradicts", fails the identity even in
orientation worlds (115832 against 60456 on 3 × 3). It counts crosses, contradictions that wind in two directions. Lemma 3 shows
a cross is seen by every cylinder along an odd class. So the lone line, not the cylinder event, is the honest analogue of a lone
loop.

## The boundary this draws

- **What the identity tracks.** It holds or fails with how many hidden places one random choice reaches, not with how many
  literals a clause has.
- **How shared-coin worlds behave.** They are two-literal worlds whose coins reach three places. They fail like three-place
  worlds, though more mildly: factors up to 2, against up to 2114.
- **In the program's terms.** Shielding is a law of pairwise contacts, and a contact whose coin reaches three places can see the
  twist that crosses its contradictions.
- **Measured, not universal.** The failure is exact on the tested tori. That is enough to show the identity is not a law of
  those worlds. It does not show that every three-way world fails on every torus.

## Post-hoc reading (exploratory, not part of the frozen verdict)

- **No other exact relations.** On 3 × 3, 3 × 4 and 4 × 4 the scan covered every pair of equal nonzero counts among torus,
  cylinder, lone and cross events of three-place and shared-coin worlds, across twists and classes. Each is explained by the
  symmetry maps, or by one structural identity: in worlds without lone lines or crosses, the cylinder count along each odd class
  equals the torus count.
- **The orientation worlds.** There, the extra relations are exactly those generated by the shielding pairs and the symmetries.
- **Lone lines are not rarer at three places.** They make up 11–23% of contradictions on average there, against 3–7% in
  orientation worlds and about 0.1% in shared-coin worlds.

## What went wrong, and what was changed before freezing

- **Equalities explained by vertex flips.** The first scoping pass found three-place equalities (placements 109, 123, 95). They
  are explained by vertex flips: gauges by a function that is not periodic, which change literal signs and, on odd sides, the
  twist. The symmetry group was extended to these flips before freezing.
- **The checker's maps.** The independent checker's first explicit maps fixed the vertex change to the flip. They missed the
  coboundary that moves a transported twist onto its standard representative, and were corrected before the run.
- **A reboot.** The machine rebooted during the 4 × 4 torus and killed the frozen run. It was relaunched unchanged. The relaunch
  reproduced the first three tori byte for byte.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| The winding contradictions of three-place tiling worlds may obey the shielding identity | `docs/KNOT_INTUITION.md`, question 9 ("Still open"); the recommendations of `TRIPLE-TWIST-20261023-001` and `TWIST-MAP-20261023-001` | **False** on every tested torus: 36 independent three-place pairs, all unequal. |
| Shielding is a two-literal law | A natural reading of `LOOP-SHIELD-20261023-001` with the program's two-versus-three thesis | **Refined.** It is a law of coins that reach two places; two-literal worlds with shared coins fail it too. |
| "The cylinder along c contradicts" is the analogue of a lone loop | This epic's first design | **False.** It includes crosses and fails even at two literals; lone lines are the analogue (Theorem 5). |
| Symmetry means lattice symmetry | This epic's first design | **Too narrow.** Vertex flips relate placements and shift twists on odd sides. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Theorem 1 (cylinders and fitting twists) | The covering argument behind `TRIPLE-TWIST-20261023-001A-P001`, Theorem 5 | Standard technique; low folklore risk as stated |
| Lemma 3 and Theorem 5 (lone lines are line events) | Skew symmetry, ear decompositions, a cone argument and Lefschetz purity | New to the program; moderate folklore risk |
| The identity fails wherever one coin decides three places | A, exact counts, independently checked | A recorded computation; the reading as "coin reach" is the project's |
| No other exact relations at three places on these tori | Post-hoc scan of A | Exploratory |

**Did the perspective do real work?** Yes.
- **Topology chose the objects.** It supplied the events (cylinders and lone lines), the rank argument (Lemma 3) and the
  question of which twist a contradiction can see.
- **The answer is the program's own.** An exact law holds for pairwise contacts and fails for three-way ones, and the line falls
  on coin reach, not on clause width.
- **The tools are standard.** The mathematical tools are classical.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the dual-pair identity for three-place line contradictions | **Successful** | Decided. It is a theorem when each coin reaches two places (B). It fails exactly for every tested pair when one coin reaches three (A, 36 three-place and 18 shared-coin independent pairs). |
| Local direction — exact twist relations in twisted fair worlds | Practically exhausted; retire | The two-literal side is fully explained: factorization, walls, the path-sign move and shielding. At three places no exact relation beyond symmetry appears on the tested tori. |
| Broader exploration — the pairwise/three-way boundary | A new exact signature | Shielding separates coin reach two from three. Other open program questions remain (the 3/4 constant and the lower bound of `SC-TORUS-EXACT-20261022-001`). |
| Long-term goal — emergence at the two/three boundary | Capability gained | An exact law holds for pairwise contacts and fails for three-way ones. Missing bridge: a mechanism that makes the failure a theorem on all tori, and a link to the knot test K1–K3. |
| Next recommendation — what a three-place line sees | **Next step:** Continue with a fresh epic, "the detector". On the smallest lopsided pairs (3 × 3 placements 54 and 62: 6 against 468, 24 against 7308), find the local structure whose count depends on the crossing twist and test it as a counting law. Then sample larger tori to see whether the ratio persists. Alternatives: a note, "shielding is a pairwise law" (1/3); the 3/4 constant (1/3). | It would turn finite counterexamples into a mechanism, a three-way contact detecting the twist that pairwise contacts cannot. |
| Interest — the detector | **2/3 — Promising** | The ratios (up to 2114, and around 100 on 4 × 4) point to a strong, probably local mechanism. Main uncertainty: lines on tori of side 3 and 4 are tiny, so the mechanism may be a small-torus effect or depend on the placement. |
| Execution — the detector | Deferred to the owner | Bound: one epic, enumeration on 3 × 3 and 3 × 4 plus sampling to side 8. Stop if no local structure explains a ratio on 3 × 3, or if sampled ratios approach 1 with size. |
