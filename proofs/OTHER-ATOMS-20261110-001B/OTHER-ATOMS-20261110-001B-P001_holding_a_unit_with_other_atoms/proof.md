# Holding a unit with other atoms

Status: Exact on small cases (SAT over every state of every class). `check.py` (3 seconds), tier T2 of
`research/OTHER-ATOMS-20261110-001/preregistration.md`, frozen before any run (commit `1fd95cc5f`).

## What is checked

For each atom passing T1 with at most 8 points (ticket A): the Fano atom (7,2,1) and the thin-torus atoms (2,1,2), (3,2,2) and (4,3,2).
On K_3, at every line orbit l0 (three), two atoms (at l0 and the first line at distance 3) in all 16 classes and three atoms (at l0 and at
distances 2 and 3) in all 64; the atoms grown in turn by the first compatible bijection, chirality 0, with the first completion with no
even face (`multi_lib.py`); classes reached by flat changes on each atom's own sides. In each class:
- each atom's role, by SAT on its outer points, and the role read on its torus (line exactly in the torus's unsatisfiable class);
- **R-a**, when every atom acts: no state satisfies every line;
- **R-b**, otherwise: for each acting atom, no state satisfies every line with at most one agreeing corner at every face of its region.

## Results

24 spaces, 960 classes: R-a and R-b hold in every class, and every role equals the one read on the torus. Each atom acts in exactly one
of its handle's four classes, so the classes split 9 / 6 / 1 by the number of acting atoms with two atoms and 27 / 27 / 9 / 1 with three,
for every atom type alike. Prediction P3 held. The theorem of ticket A proves all of this for every host and every placement of atoms;
this check is an independent exact computation of the same claims on these spaces, atoms at distance 2 (overlapping gadgets) included.
