# What a three-place line sees

Epic `LINE-DETECTOR-20261023-001`, closed 2026-10-23.

## The question

The owner approved the recommendation of `TRIPLE-SHIELD-20261023-001`: find "the detector".
- **The question.** What local structure makes a three-place line's count depend on the twist that crosses it?
- **Where to start.** The most lopsided dual pairs (on 3 × 3, placement 54: 6 against 468; placement 62: 24 against 7308).
- **Stop if** no structure explains a ratio there.

**The evidence:**
- [Contradiction patterns along eight classes](../../experiments/LINE-DETECTOR-20261023-001A/LINE-DETECTOR-20261023-001A-E001_contradiction_patterns/contract.json)
  (A, frozen confirmatory experiment, partially supported;
  [result](../../artifacts/LINE-DETECTOR-20261023-001A/LINE-DETECTOR-20261023-001A-E001_contradiction_patterns/result.json));
- [All or nothing in direction](../../proofs/LINE-DETECTOR-20261023-001B/LINE-DETECTOR-20261023-001B-P001_trichotomy/proof.md)
  (B, proof);
- **scoping (scratch, not evidence):** extra cylinders for lone lines, a classification by minimal contradictions, and SAT
  certificates, all on 3 × 3.

## Outcome in one paragraph

**The lopsided ratios were mostly not the line seeing the twist, and the real two-versus-three contrast lies one level lower.**
- **The blind spot.** A lone line was checked against three cylinders, and in each twist only one other odd class among them can
  contradict. The two twists of a dual pair check different classes.
  - On 3 × 3, every lone line of placements 54 and 62 also contradicts along an odd class that was never checked, so their ratios
    measure only the blind spot.
  - On 3 × 4, more than 99.8% of them do.
- **Why the blind spot exists.** This is the new theorem (B).
  - In every two-literal tiling world, shared coins included, a configuration contradicts along no class, along one class, or
    along every odd class: the trichotomy. So three cylinders suffice there.
  - Three-place worlds can be selective: they contradict along some odd classes and not others. Twelve of the 30 three-place
    placements do so on every torus computed.
- **Still true.** Lines pure among eight classes still differ across dual pairs at three places (placement 111 on 3 × 4: 395160
  against 547584). So a three-place line does see the crossing twist, but by a different amount than the lone counts suggested.
  For placement 109 along (1,0) the direction is even reversed.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Check lone lines of 54 and 62 against five more cylinders | Every one also contradicts along (1,−1) in twist 01 and along (2,−1) in twist 00 | Scoping; certified both ways by SAT |
| Classify every configuration by the windings of its minimal contradictions | Wrong notion: even the orientation world has 5664 against 2028 such "pure" lines, because a contradiction winding two ways can have all its minimal contradictions along one class | Scoping; the notion was dropped |
| Use cylinders instead: pure means only the line's own cylinder contradicts | Equals the line event of the shielding theorem on the two-literal side | Proved (B, Corollary) |
| Look at which odd classes contradict at three places | Partial and irregular sets, even with a satisfiable direction between two contradicting ones | Scoping; certified (B, Proposition 4) |
| Freeze predictions from 3 × 3 and test on 3 × 4 and 4 × 4 | Trichotomy everywhere on the two-literal side; the same 12 selective three-place placements; pure lines still unequal; the blind spot explains most but not all of the 54 and 62 effect | A, partially supported |

## What was measured (A, partially supported)

| Prediction | Outcome |
| --- | --- |
| P1: no even class contradicts | Holds on every torus |
| P2: no two-literal placement is selective (theorem) | Holds: all 24 placements, every configuration of 3 × 3 and 3 × 4, and 2^22 samples per twist on 4 × 4 |
| P3: the 12 placements selective on 3 × 3 are selective on 3 × 4 | Holds, with no others (17712440 selective configurations on 3 × 4); their 4 × 4 representatives are selective in the sample |
| P4: no lone line of the 54 and 62 families is pure among the eight on 3 × 4 | **Fails.** In one twist of each pair a few are: 6 of 20586 (54) and 1176 of 788304 (62); none in the other twist |
| P5: some dual pair of lines pure among the eight differs on 3 × 4 | Holds (placement 111: 395160 against 547584; 109 along (1,1): 144442 against 91728) |

**Checks.**
- **Controls.** All passed. The torus, cylinder, lone and cross counts implied by the patterns equal the frozen record of
  `TRIPLE-SHIELD-20261023-001A-E001` for every placement and twist on 3 × 3 and 3 × 4.
- **The independent checker.**
  - It recomputed the fitting twists, controls and verdict.
  - It certified 660 configurations along all eight classes with its own SAT encoding, none undetermined. These include 81
    selective patterns and 71 lone lines.

## What was proved (B)

| Result | Content |
| --- | --- |
| Lemma 1 | A two-literal tiling placement is the conjunction of its two-literal clauses. Its clauses on any one edge share a type, because the doubly allowed tiling would otherwise need the edge's values to be both equal and different. |
| Lemma 2 | The doubly allowed tiling turns the clause types into a coboundary of the fitting twist. So the value change around a closed implication walk is r(γ), the relative twist of its class. |
| Theorem 3 (trichotomy) | Every two-literal tiling world, shared coins included, contradicts along no class, along the multiples of one class, or along every odd class. The cause is a rank-two cluster for the third case and parallel clusters for the second. |
| Corollary | There, a lone line is a pure line and a line event. So shared-coin dual-pair failures (942 against 876 on 3 × 3) are genuine. |
| Proposition 4 | Certified three-place configurations (placements 54, 62, 111 on 3 × 3) contradict along some odd classes and have assignments along others. |
| Proposition 5 | The frozen counts above. |

## What this changes in `TRIPLE-SHIELD-20261023-001`

- **Unchanged.**
  - Its frozen counts.
  - Its theorem for orientation worlds.
  - Its finding that shared coins break the dual-pair identity, now known to break the line event itself.
- **Changed.** At three places its lone counts are not counts of lines.
  - The ratios it reported (up to 2114) overstate the effect for lines pure among eight classes.
  - For placement 109 along (1,0) they get its direction wrong.
- **To be qualified.**
  - The reading in `TRIPLE-SHIELD-20261023-001-D001`, "the line falls at a coin's reach, not clause width", holds for the
    dual-pair identity of line events.
  - The more basic boundary, the trichotomy, does fall at clause width.
  - Formally superseding that record would mean editing a closed epic's disposition, so it is left to the owner. This epic's
    record states the qualification.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| A lone line (three cylinders) is the analogue of a lone loop at three places | `TRIPLE-SHIELD-20261023-001` (decision note and Remark 7 of its proof) | **False** at three places: contradictions there are selective, and lone lines can contradict along unchecked classes. |
| The lopsided three-place ratios show the line seeing the twist | `TRIPLE-SHIELD-20261023-001` recommendation and this epic's question | **Mostly false** for the largest ratios (blind spot), **true** in a weaker form (pure lines among eight classes still differ). |
| "Coin reach, not clause width" is the dividing line | `TRIPLE-SHIELD-20261023-001-D001` | **Refined.** Coin reach decides shielding of line events; clause width decides the direction structure of contradictions. |
| A contradiction's minimal witnesses show its direction | This epic's first scoping step | **False** even at two literals: a two-way contradiction can have all its minimal witnesses along one class. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Lemma 2 (parity via the tiling) | Summing the tiling's constraints around a walk | Elementary; new to the program |
| Theorem 3 (trichotomy for twisted two-literal worlds on tori) | The lemmas of `TRIPLE-SHIELD-20261023-001B-P001`, which never used independent coins, plus Lemma 2 | New to the program; moderate folklore risk |
| Three-place selectivity (12 of 30 placements) | Certified computation and frozen exhaustive counts | Direction-dependent periodicity of two-dimensional shift spaces is classical (expansive directions, Boyle and Lind). The contrast with two-literal rigidity is the program's own. |
| The blind spot and its size | A, exact counts | A recorded computation |

**Did the perspective do real work?** Yes. Asking which classes a contradiction "sees", the topological question, uncovered both
the blind spot and the trichotomy. The proofs use classical tools.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — what a three-place line sees | **Partially successful** | The largest ratios are explained (a blind spot of the lone event, from selective contradictions). The remaining effect is real but needs every class to measure exactly. No local "detector" structure was found. |
| Local direction — dual pairs of three-place lines | Practically exhausted at this level; retire | Pure lines need all classes. Finite windows give only upper bounds, so exact shielding questions about three-place lines are not well posed with cylinders. |
| Broader exploration — the pairwise/three-way boundary | A sharper signature | The trichotomy holds for every two-literal tiling world, and 12 of 30 three-place placements break it. Open: what makes the other 18 rigid on these tori. |
| Long-term goal — emergence at the two/three boundary | Capability gained | A structural property of contradictions holds exactly at two literals, whatever the coins, and fails at three places. Missing bridge: whether rigidity characterizes two-literal contacts, or follows from an algebraic property that some three-place contacts share. |
| Next recommendation — directional rigidity | **Next step:** Continue with a fresh epic: "which contacts are all or nothing in direction?" First test the 18 rigid three-place placements with more classes (up to 16) and larger tori (sampled). Then compare the algebra (polymorphisms) of rigid and selective contacts. Alternatives: a short note on the trichotomy (1/3); the 3/4 constant (1/3). | Either rigidity is exactly two-literal, a clean statement of the thesis boundary, or an algebraic property draws a different line. |
| Interest — directional rigidity | **2/3 — Promising** | The trichotomy's proof uses only majority closure, which suggests an algebraic criterion. Main uncertainty: the 18 placements may all turn selective with more classes, which would make the criterion simply "two-literal". |
| Execution — directional rigidity | Deferred to the owner | Bound: one epic, exhaustive 3 × 3 and 3 × 4 with 16 classes, 4 × 4 sampled. Stop when every placement is classified, or if a placement stays undecided with all classes the engine can handle. |
