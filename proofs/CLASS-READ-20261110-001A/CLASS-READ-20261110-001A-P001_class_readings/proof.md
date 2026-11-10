# Class readings

Status: R0 proved (from `GATES-20261110-001A`, P2); the census computed exhaustively per network (SAT over every state of every class
or class pair). `check.py` (7 seconds), as frozen in `research/CLASS-READ-20261110-001/preregistration.md` (commit `10e19e0a3`). The
counts of satisfying states quoted at the end were computed after the run.

## Setting

Closed thin tori (3,2,2) as leaves, none of these networks used in `GATES-20261110-001`. A leaf's four classes form an affine plane over
F2 with its acting class ω = (0,1) (the torus's unsatisfiable class). G1: one leaf, 6,800 networks (three names from its 15 point pairs,
10 tops); G2: two leaves, 67,500 networks.

## Results

**G1, one leaf.** Every network reads one of three sets of classes:

| Classes read (O = 1) | Networks |
| --- | --- |
| {ω} | 6,032 |
| {ω, (1,0)}, the line through ω in direction (1,1) | 718 |
| all four | 50 |

R0 held, and R1 held: the line through ω was read on new networks, as after `GATES-20261110-001`'s run, and again in direction (1,1).
The other two lines through ω, and every set of three classes, were never read.

**G2, two leaves.** On the nine pairs where neither leaf acts, the 67,500 networks give only four readings: nothing (65,232), the single
pair where both leaves are in (1,0) (2,088), and leaf 1 or leaf 2 in (1,0) whatever the other's non-acting class (90 each). R0 held. **R2
failed:** of the nine joint minterms only one is read. The failure line was not crossed.

## What this shows

The readings of a leaf form a chain, {ω} ⊂ {ω, σ} ⊂ everything, with σ = ω + (1,1) the one non-acting class names can tell apart; the
other two non-acting classes are never told apart from each other or from σ's complement. So names read a stored class only against two
references, ω and σ, and only upward: a reading that holds for some class holds for every class above it in the chain. Every function read
here is therefore monotone in the two indicators [the class is ω] and [the class is ω or σ], and none of the readings that would complete a
basis (the class is not σ, or is one particular other class) appears.

**Post hoc, why σ.** σ is the most constrained satisfiable class: on (3,2,2) it has 4 satisfying states against 16 and 20 for the other
two (and on (2,1,2), the leaf of `GATES-20261110-001`, σ = (0,1) has 4 against 6 and 8). Names can single out a class only by how little
its states can vary.
