# Experiment report: class-4 gadget counts are local up to relabeling

`CLASS4-PAIRS-20261028-001B-E001`, run once under its frozen contract on 2026-10-28 (4214 s), after the construction-only check
`build_check.py`. Verdict: **supported**.
- **Contract and code:** `experiments/CLASS4-PAIRS-20261028-001B/CLASS4-PAIRS-20261028-001B-E001_class_4_gadget_counts_are_local_up_to_relabeling/`
- **Outputs:** `artifacts/CLASS4-PAIRS-20261028-001B/CLASS4-PAIRS-20261028-001B-E001_class_4_gadget_counts_are_local_up_to_relabeling/`

## What was tested

Take free class 4 on (1, 1), (0, 1, 1) and (1, 1, 1) at d = 5, p = 11, slots (1, 1, 2). These are the three d = 5 census algebras
whose only failing clean-edge condition is (K). For data of degree ≤ 2 fixed on the solution variety, the degree-4 equations of a
zero-jump gadget are affine in the degree-3 data. The run compares two systems:
- the global system of a graph gadget;
- the local system assembled from single-edge gadgets.

There are seven shapes: the path P3, an edge over an isolated vertex, the star K₁,₃, the triangle, the path with both edges into
the last vertex, the 4-cycle and K₄. Each comes in three configuration types: all vertex states equal, all random, alternating.

The predictions:
- **R1:** the configuration is on the variety, and both systems are affine.
- **R2:** the linear parts are equal.
- **R3:** the constant parts differ by an element of the column space, a relabeling.
- **R4:** hence the counts are equal.
- **R5:** the single-edge linear-flow structure.
- **R6:** the rank-witness ingredients.

## Count-locality

| case | algebra | configurations | R1 | R2 | R3 | R4 | constant parts equal | solvable (kernel dims) | holds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K11 | free class 4 on (1, 1) | 21 | 21 | 21 | 21 | 21 | 10 | 21 (0, 2, 3) | yes |
| K011 | free class 4 on (0, 1, 1) | 21 | 21 | 21 | 21 | 21 | 9 | 21 (10, 14, 18, 20, 24, 26, 32, 41) | yes |
| K111 | free class 4 on (1, 1, 1) | 21 | 21 | 21 | 21 | 21 | 9 | 0 (-) | yes |

"Constant parts equal" counts the configurations where no relabeling was needed. In the others the global and local constant parts
differ, always by an element of the column space.

The column-space test is not vacuous: A has rank below its number of rows in 63 of 63 configurations. For free class 4
on (1, 1, 1), no sampled datum admits a degree-3 completion, globally or locally. There the counts agree because both are zero,
and R2–R3 carry the evidence.

## Linear flows and the rank witness

- **K11.** Vertex terms at zero data nonzero for 0 of 10 pairs; private rows nonzero at the diagonal for 0 of 100. Failures (not affine / not additive / slot-2-free term): diagonal: 8 samples, 0/0/0; random: 7 samples, 0/0/0; pair-failing (0, D): 8 samples, 0/0/0. Rank witness: (0, D): zero data solve True, 50/50 random data violate; (D, 0): zero data solve True, 50/50 random data violate.
- **K011.** Vertex terms at zero data nonzero for 0 of 10 pairs; private rows nonzero at the diagonal for 0 of 100. Failures (not affine / not additive / slot-2-free term): diagonal: 8 samples, 0/0/0; random: 7 samples, 0/0/0; pair-failing (0, D): 8 samples, 0/0/0. Rank witness: (0, D): zero data solve True, 50/50 random data violate; (D, 0): zero data solve True, 50/50 random data violate.
- **K111.** Vertex terms at zero data nonzero for 0 of 10 pairs; private rows nonzero at the diagonal for 0 of 100. Failures (not affine / not additive / slot-2-free term): diagonal: 8 samples, 0/0/0; random: 8 samples, 0/0/0; pair-failing (0, D): 8 samples, 0/0/0. Rank witness: (0, D): zero data solve True, 50/50 random data violate; (D, 0): zero data solve True, 50/50 random data violate.

## Controls

- **X1, the cumulative design** (free class 4 on (1, 1); four shapes × three configuration types).
  - It is non-local already below layer 4. In 12 of 12 configurations, points of the
    single-edge variety violate the graph gadget's layer-2/3 private equations (R1 fails).
  - Linear parts were equal in 3 of 12, the column-space test passed in
    0 of 12, and the counts agreed in 6
    of 12.
  - The control fires, as required (matched: False).
- **X2, a dual slot with layer-1 data** (free class 4 on (1, 2), slots (1, 2, 3)). Failures (not affine / not additive /
  slot-2-free term): diagonal: 8 samples, 0/0/0; random: 8 samples, 7/0/0; pair-failing (0, D): 8 samples, 8/0/0. The linear structure fails, as required (matched: False).

## What the numbers say

- **Locality holds up to relabeling.** In every configuration of every algebra, the linear parts agree and the constant parts
  differ by an element of the column space.
- **The relabeling is real.** It is needed off the diagonal: the constant parts were literally equal only in some configurations.
- **The cumulative design breaks it,** already below layer 4. So the property comes from the zero-jump construction, not from
  the comparison method.
- **Single edges have the linear-flow structure** for the three algebras, and lose it when the dual slot has layer-1 data.

## What it does not show

- Graphs have at most 4 vertices and 6 edges. Locality on every graph (hypothesis (L4) of `CLASS4-PAIRS-20261028-001C`) is
  supported, not proved.
- The three algebras share α = β = 1 at d = 5. There the degree-3 junction twists land at character 3 = −γ, which the preceding
  dual slot carries. Algebras where they do not are untested.
- Vertex states and private data are sampled.
- X1's failures sit below layer 4. No configuration on the variety failed R2–R3, so the run exhibits no layer-4 failure for a
  discriminator to catch. Its discriminating power rests on the proper column spaces.
- For free class 4 on (1, 1, 1), the data with nonzero counts were not sampled.
