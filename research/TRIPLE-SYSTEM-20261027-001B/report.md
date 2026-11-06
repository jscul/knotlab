# Experiment report: steering of the four-way form for nonabelian triple systems

`TRIPLE-SYSTEM-20261027-001B-E001`, run once under its frozen contract on 2026-10-27 (58 s).
- Contract and code: `experiments/TRIPLE-SYSTEM-20261027-001B/TRIPLE-SYSTEM-20261027-001B-E001_triple_system_steering_on_gadget_surgeries/`
- Outputs: `artifacts/TRIPLE-SYSTEM-20261027-001B/TRIPLE-SYSTEM-20261027-001B-E001_triple_system_steering_on_gadget_surgeries/`

**Verdict: supported** under the frozen rule. There were no machinery failures and no prediction failures, and all five negative
controls failed to match.

## What was tested

- **The setting.** G = N ⋊ C₂ with N = exp(𝔫) given by a graded Lie algebra of class 3 or 4, on 2-surgeries of closed braids.
- **The measurement.** A general BCH braid model, `lm.py`, solves the layers in order and pairs the top-layer −1 obstructions
  with (J^T s, 0).

| Rule | Prediction | Fixtures | Outcome |
| --- | --- | --- | --- |
| R2 base and R0 abelian | every free datum lifts | sums of T(2, 5), T(2, 7) and 4_1 for all nine algebras; three abelian algebras on every fixture | 42 / 42 |
| R1 steering | Q = 2 Σ Σ_j ⟨W_j⁽³⁾(ℓ(x)), ℓ_j(s)⟩: the Dynkin form of the degree-3 Lie part of the conjugators on all free −1 classes | six nonabelian algebras (u₄; free class 3 on (y1−, y2−), (y1−, y2−, y3−) and (x+, y1−, y2−); class 4 on (x+, y−); class 4 on (x+, y1−, y2−) with layer-1 data on y1) on six fixtures at p = 5, 7, 11, including gadgets K3 and C4 | 36 / 36 exact (32 samples each) |
| R3 model agreement | the BCH model equals the 4×4 matrix model for u₄ | five fixtures at p = 5, 7 | 5 / 5 |
| R4 lifting | a lift exists exactly when Q(x; ·) = 0, with \|Z¹\|² completions (independent BCH group law on the Wirtinger presentation) | free class 3 on (y1−, y2−), 24 layer-1 data | 24 / 24 (9 lift) |

**Negative controls.** All five failed to match:
- κ = 1;
- the P4B tensor for a P4 insertion;
- one edge dropped;
- leaves 0 and 2 swapped;
- the rule with layer-1 data only, for the class-4 cross-layer algebra. This shows that the free layer-2 class enters the form.

## What it shows

- **The general rule holds.** The steering rule of ticket C holds beyond u₄:
  - for several −1 generators;
  - for mixed signs;
  - in class 4, where the obstruction pairs layer-2 and layer-3 free classes through the triple bracket.
- **No base or abelian obstruction.** Bases and abelian triple systems never obstruct.

## Limits

- The non-central class-4 case is not exercised: two layer-1 −1 directions with nonzero triple brackets, where the layer-3
  obstruction blocks layer 4 on generic samples. The proof treats it by characters.
- 32 random samples per fixture.
- Class at most 4.
