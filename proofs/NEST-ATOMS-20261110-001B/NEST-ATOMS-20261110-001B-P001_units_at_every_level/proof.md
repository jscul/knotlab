# Units at every level

Status: Exact on small cases (SAT over every state of every class). `check.py` (19 seconds), ticket B of
`research/NEST-ATOMS-20261110-001/preregistration.md`, frozen in commit `4b27647cb` before any run.

## What is checked

For each leaf type (the Fano atom and the thin-torus atom (2,1,2)), with the outer host K_2: (a) one composite C(2, leaf) at L0 (genus 2,
16 classes); (b) two composites at L0 and L1 (genus 4, 256 classes); (c) the depth-two composite D(leaf) at L0 (genus 2, 16 classes).
In every class: the role of every group (leaf, composite, nested composite) by SAT on its outer points, and the AND; **R-a**, if every
top-level group acts no state satisfies every line; **R-b'**, in every state satisfying every line each group of genus g holds at least
g − 1 + [it acts] units in its region (SAT with a cardinality bound on its agreeing corners).

**Code control.** The new code on K_3 with two Fano leaves at l0 and distance 3 gives `OTHER-ATOMS-20261110-001B`'s split there: 9 classes
with no leaf acting, 6 with one, 1 with both, R-a and R-b in every class.

## Results

Six spaces, 576 classes: R-a, R-b' and the AND hold in every class. In space (b), with four leaves and two composites, the composites act
in exactly the classes where both of their leaves act, and no class has both acting with a satisfying state. The expectation held.
Theorem N and lemma U of ticket A prove all of this on every host; this is an independent exact computation of the same claims here.
