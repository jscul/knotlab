# Experiment report: class-4 gadget equations are exactly local in intrinsic coordinates

`CLASS4-LOCALITY-20261028-001A-E001`, run once under its frozen contract on 2026-10-28 (17052 s), after the construction-only check
`build_check.py`. Verdict: **invalid** (see below).
- **Contract and code:** `experiments/CLASS4-LOCALITY-20261028-001A/CLASS4-LOCALITY-20261028-001A-E001_class_4_gadget_equations_are_exactly_local_in_intrinsic_coordinates/`
- **Outputs:** `artifacts/CLASS4-LOCALITY-20261028-001A/CLASS4-LOCALITY-20261028-001A-E001_class_4_gadget_equations_are_exactly_local_in_intrinsic_coordinates/`

## What was tested

The previous epic's experiment (`CLASS4-PAIRS-20261028-001B-E001`) found the global and local layer-4 systems equal only up to a
relabeling of the layer-3 data. This run removes the relabeling at its source. The model solves each layer with a particular
solution chosen by a linear solver, which may contain an arbitrary multiple of each slot-2 block's class colouring. The intrinsic
coordinate of a slot-2 block is the colour difference between its reading strand and its base strand, divided by the class colouring
at the reading strand. That removes the solver's choice, and the prediction is that the systems are then **equal**.

- **Algebras:** free class 4 on (1, 1), (0, 1, 1) and (1, 1, 1) at d = 5, p = 11, slots (1, 1, 2).
- **Graphs:** P3, an edge over an isolated vertex, the star K₁,₃, the triangle, the reversed path, the 4-cycle and K₄.
- **Configuration types:** all vertex states equal; all random; alternating; all states nonzero multiples of one vector
  (parallel). Off the diagonal, the variety usually forces an edge's slot-1 data to zero; parallel states let them survive, which
  activates the degree-3 twist of the vertex bundle.

## Results

| algebra | configurations | on variety, affine | linear parts equal | intrinsic constant parts equal | raw constant parts differ | parallel configurations with slot-1 data off the diagonal | holds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| free class 4 on (1, 1) | 28 | 28 | 28 | 28 | 17 | 7 of 7 | yes |
| free class 4 on (0, 1, 1) | 28 | 28 | 28 | 28 | 16 | 0 of 7 | **no** |
| free class 4 on (1, 1, 1) | 28 | 28 | 28 | 28 | 18 | 7 of 7 | yes |

## Controls

Two edges that are not clean modulo γ₄ (they also fail (B₀) and (V₃)):
- **XA free class 4 on (0, 1, 2), edge (1, 2).** 15 of 15 configurations on the variety; intrinsic equality fails in 6 of them (P3 diagonal, P3 reversed diagonal, star diagonal, star mixed, triangle diagonal, triangle mixed). Matched: False.
- **XB free class 4 on (1, 2), edge (2, 1).** 7 of 15 configurations on the variety; intrinsic equality fails in 0 of them (none). Matched: True.

## Why the verdict is invalid

The frozen decision rule makes the run invalid when a negative control matches. Control XB matched: intrinsic equality held in all of
its configurations on the variety. Its edge is known to break locality only rarely; in the earlier probes of
`CLASS4-PAIRS-20261028-001`, that edge broke it in 1 of 15 configurations. None of XB's configurations here hit such a case. So the
run does not certify that the comparison would have caught a failure for that kind of edge. Choosing so weak a control was a design
error. Separately, prediction P5 failed for free class 4 on (0, 1, 1): no parallel configuration put slot-1 data off the diagonal,
so the twisted regime was not exercised for that algebra.

## What the data describe (not a confirmatory result)

- **Main configurations.** P1 to P4 held for all three algebras. In every configuration, the global layer-4 system written in
  intrinsic layer-3 coordinates equals the system assembled from single-edge gadgets, while the raw constant parts differ.
- **Control XA** (an edge that also fails (B₀) and (V₃)) broke intrinsic equality on its variety, as a working control should.
- **The twisted regime** was exercised for free class 4 on (1, 1) and on (1, 1, 1).

## What it does not show

- No confirmatory support for exact intrinsic locality (L4′): the verdict is invalid.
- Graphs have at most 4 vertices and 6 edges, the three algebras share α = β = 1 at d = 5, and states and private data are sampled.
