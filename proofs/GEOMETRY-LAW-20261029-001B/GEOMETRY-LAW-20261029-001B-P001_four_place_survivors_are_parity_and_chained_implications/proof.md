# Four places: only parity and a chained implication survive

Status: Proved

Ticket `GEOMETRY-LAW-20261029-001B`, 2026-10-29.

## Standard statement

Let K ⊆ {0, 1}⁴ be a relation in which every three coordinates are unconstrained, other than the full cube: the complement of a
nonempty independent set of the 4-cube. There are 742 such relations, forming 106 classes under permutations of the coordinates.
A *gadget* of K joins copies of K, each with any order of its coordinates, by identifying variables in pairs between distinct copies,
leaving four variables single (the legs), with the copies connected; its relation is the projection onto the legs.
- Among gadgets of two and three copies, exactly three classes are rebuilt: the two parity classes x₁ + x₂ + x₃ + x₄ = c over GF(2)
  (c = 0 by every gadget, c = 1 by those with an odd number of copies), and the implication between the parities of two
  complementary pairs, {x : (x_i + x_j, x_k + x_l) ≠ (1, 0)}, which is rebuilt exactly by chains and by chains of every length.
- Every other class gives the full relation or a relation excluding strictly fewer tuples.
- 96 of the 742 relations, in 6 classes, have their symmetry group inside the rotations of a cyclic order of the coordinates;
  none of them is rebuilt.

## Nearest known result

- `GEOMETRY-LAW-20261029-001A-P001`: the same question on three bits, where only parity is rebuilt and the others lose excluded
  tuples (proved for every gadget size).
- The external literature cited there: fan-out-two expressibility (Feder 2001; Dalmau and Ford 2003; Kazda, Kolmogorov and
  Rolinek) and Holant clones ask which relations such gadgets define; Higuchi and Mézard (2009) find linear constraints produced
  by decimation flows. None of them classifies the relations rebuilt by gadgets of their own copies.
- **Classification.** No overlap found in the bounded scan of ticket A (candidate local delta).

## Setting

- **Knots and classes.** The 742 relations above; a *placement* is a permutation of coordinates. Rebuilding is a property of the
  class.
- **Native gadgets.** Connected, loopless (no variable joins two places of one copy), every internal variable in exactly two copies,
  four legs. Counting places, 4m = 2·(internal variables) + 4, so the network has m − 1 independent cycles.
- **Chains.** A chain of L copies is a path of copies in which consecutive copies share two variables (a pair), with two legs at each
  end copy. The chain of two copies is the *bigon*.
- **The implication class.** I = {x : (x₁ + x₂, x₃ + x₄) ≠ (1, 0)}: the implication p → q between the pair parities p = x₁ + x₂ and
  q = x₃ + x₄. It is a knot: forgetting any one coordinate frees the parity of its pair, so the other three are unconstrained.

## Theorem 1 (census: two and three copies)

Over all native gadgets with two copies (one shape, the bigon) and three copies (three shapes, one of them the chain), in every
placement of every class:
- the even parity class is rebuilt by all four shapes;
- the odd parity class exactly by the three shapes with three copies;
- the implication class exactly by the two chains;
- no other class is rebuilt, and every output that is not full is a knot excluding strictly fewer tuples than the input.

*Proof.* For parity, adding the m equations cancels every internal variable, so the legs satisfy l₁ + l₂ + l₃ + l₄ = m·c, and the
system is solvable exactly then (as in ticket A, Theorem 1). This gives c = 0 for even m and c for odd m. The remaining statements
are an exhaustive computation over the 106 classes, every shape and every placement (check 2). Every output is co-independent, as
`SURFACE-GLUING-20261024-001B-P001` (Lemmas 2 and 3) requires. ∎

## Proposition 2 (chains rebuild the implication)

For every L ≥ 2, the chain of L copies of I, each placed so that a shared pair feeds the next copy's first pair, has relation I on
its end pairs.

*Proof.* Each copy depends on each of its pairs only through the pair's parity. For either value of a shared pair's parity m there
are two assignments of the pair, so quantifying the pair away is quantifying m away. The chain's relation on the end parities p and
q is therefore ∃m₁ … m_{L−1}: p → m₁ → ⋯ → m_{L−1} → q, which is p → q: take every m_i = 0 when p = 0, and every m_i = 1 when p = 1
and q = 1, while p = 1, q = 0 is excluded by transitivity. ∎

**Towers.** Substituting every copy of a chain by a chain gives a chain. So the towers of I are chains, whose end pairs lie L^k copies
apart after k levels: they grow in one direction. I is a two-place relation, implication, read on the parities of pairs. Its
survival agrees with `SURFACE-GLUING-20261024-001A-P001`, where two-place relations glue only into lines and loops.

## Proposition 3 (orientation at four places does not survive)

Exactly 96 relations, in 6 classes, have their coordinate symmetry group inside the rotations of some cyclic order of the four
coordinates: 48 with trivial symmetry and 48 whose only symmetry is a rotation by two steps (a double transposition). These relations
can orient a vertex of a native network. None of their classes is rebuilt by a gadget of two or three copies (check 5).

## Consequence for geometry from a law

At four places a law can orient its vertices, but no orienting law survives patterns of patterns. What survives is shapeless
(parity, in every shape) or a chain (a two-place relation on derived bits). This agrees with three places (ticket A).

## Checks

`check.py` (numpy), with `result.json`, on the library `census4.py`:
- **0.** Ticket A's manifest and result are bound by hash.
- **1.** 742 knots, 106 classes, stabilizer sizes (48, 420, 126, 112, 24 and 12 relations with symmetry groups of order 1, 2, 4, 6, 8
  and 24); 96 orienting relations in 6 classes.
- **2.** The exhaustive census of Theorem 1, including co-independence of every output and the strict decrease of excluded tuples
  for every non-affine class.
- **3.** Chains of 2 to 7 copies rebuild the implication class and the even parity class.
- **4.** 300 random native gadgets of four copies, every class in random placements: only the even parity class is rebuilt (these
  gadgets have an even number of copies and none is a chain).
- **5.** No orienting class is rebuilt.
- **6.** Controls that must fire:
  - with self-gluing, 18 more classes are rebuilt by gadgets of two or three copies;
  - all-equal on four bits, which is not co-independent, is rebuilt by every native shape;
  - the bigon turns the odd parity class into the even one.

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Theorem 1 | Exhaustive computation; parity by linear algebra | Candidate local delta (computed census) |
| Proposition 2 | Transitivity of implication on pair parities | Elementary |
| Proposition 3 | Symmetry groups of the 742 relations | Computed |

## What this does not show

- Gadgets of four or more copies are only sampled (and chains of any length proved). A larger non-chain gadget could still rebuild
  another class.
- Nothing about counts: the statements concern allowed tuples only.
- Nothing beyond four places.
