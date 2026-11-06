# Probes after the frozen run

Unfrozen scoping probes cited in `../class4_pairs.md` ("Probes after the frozen run"). They sharpen the statement of the remaining
obstruction (L4) and inform the recommendation. They are not evidence for any claim, and no ticket accepts them.

## Files

- `edge_conditions_mod4.py`: the clean-edge conditions modulo γ₄ for a class-4 algebra and an edge. It reports which of (K), (B₀),
  (B₁′), (B₂′), (V₃) and (V₃′) fail. The helpers are loaded read-only from the check of `CLASS4-PAIRS-20261028-001A-P001`.
  Output: `logs/edge_conditions_mod4.txt`.
- `enum_k_only_edges.py`: every edge that fails only (K) modulo γ₄, for free class 4 on at most three generators at d = 5, p = 11,
  up to scaling characters by units. Output: `logs/enum_k_only_edges.txt`.
- `probe_locality.py <preset> <seed>`: the global and assembled local degree-4 systems of the experiment
  (`CLASS4-PAIRS-20261028-001B-E001`, `c4_lib.Case.graph`, read-only). It runs on five shapes (P3, an edge over an isolated vertex,
  the star, the triangle, the reversed path) in three configuration types, seed 7. Outputs: `logs/probe_<preset>.txt`.

| preset | algebra, edge (slots) | conditions failing modulo γ₄ |
| --- | --- | --- |
| K12 | free class 4 on (1, 2), edge (1, 2) (slots 1, 2, 3) | (K) only |
| K13r | free class 4 on (1, 3), edge (3, 1) (slots 3, 1, 4): K12 scaled by 2 | (K) only |
| K12r | free class 4 on (1, 2), edge (2, 1) (slots 2, 1, 3) | (B₀), (K), (V₃) |
| K13 | free class 4 on (1, 3), edge (1, 3) (slots 1, 3, 4): K12r scaled by 2 | (B₀), (K), (V₃) |
| K012 | free class 4 on (0, 1, 2), edge (1, 2) (slots 1, 2, 3) | (B₀), (K), (V₃) |
| K012r | free class 4 on (0, 1, 2), edge (2, 1) (slots 2, 1, 3) | (B₀), (K), (V₃) |

The logs were produced by scratch copies that differed only in how they find the repository. Rerunning `probe_locality.py K12 7`
from this folder reproduced `logs/probe_K12.txt` exactly, apart from timings.

## Results

- **The edges failing only (K) at d = 5** are free class 4 on (1, 1), (0, 1, 1) and (1, 1, 1), edge (1, 1), which the experiment
  tested, and free class 4 on (1, 2), edge (1, 2).
- **K12 and K13r.** The global and local systems were equal in 15 of 15 configurations each. The degree-3 data enter no degree-4
  equation there (A = 0), so this is a weak test of (L4).
- **K12r, K13, K012, K012r.** These edges are not clean modulo γ₄, and locality breaks:
  - single-edge varieties fail on the graph's variety;
  - on the private variety, the constant parts differ outside the column space in 11 configurations: 1 for K12r, 4 for K13, 5 for
    K012 and 1 for K012r. The counts differ in 2 of them, one for K12r and one for K13.
  - Their lower vertex equations do not vanish, so they are outside the hypotheses of Theorem 7 and say nothing against (L4).
- **The linear parts agreed in all 90 probe configurations,** clean or not. That fits the twists depending only on lower data.
