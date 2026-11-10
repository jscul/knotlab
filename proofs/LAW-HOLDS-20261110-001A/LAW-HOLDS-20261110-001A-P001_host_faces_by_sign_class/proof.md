# Host faces by sign class

Status: Computed exactly (SAT over every state, `check.py`), on the 15 genus-2 floor states of `ATOM-LAYERS-20261110-001` (K_2 and K_3; one
Fano atom at l0, called atom 0, and one at distance 1, 2 or 3, atom 1). Pre-registered in `research/LAW-HOLDS-20261110-001/preregistration.md`.
Nothing here is capped: for each law and face SAT decides whether any state at all is a floor state with the unit at that face.

## Results

- **The learned law decides (L1, in substance).** For the law learning left (atom 0 transparent, atom 1 acting as its line), every state
  at the floor has its unit inside atom 1 or at a junction face of atom 1: never inside atom 0 and never at the upper level, on all 15
  spaces. When the two atoms are adjacent (distance 1), one of those junction faces is shared by both atoms. L1 as stated, which allowed
  only atom 1's own junctions, fails on those 5 spaces for that shared face. This settles the capped K_3 cases of
  `RISE-ESCAPE-20261110-001`: no state of that law, reachable or not, has the unit elsewhere.
- **The hosts follow the atoms' roles (L2, in substance).** Across the 16 classes of each space (240 in all), each atom either acts as its
  line or is transparent, and:
  - both act as their lines (15): no floor state at all, since the sphere's contradiction returns;
  - one acts, one is transparent (90): the hosts lie inside the acting atom and its junctions (with the shared junction face when the
    atoms are adjacent);
  - both transparent (135): hosts in both atoms and their junctions, and at the upper level on the 90 spaces with the atoms apart
    (distance 2 or 3), not on the 45 with the atoms adjacent.
  L2 as stated fails on the shared junction face and on the adjacent both-transparent classes, which reach no upper face.

So the leftover dissonance lives in whichever atom still acts as its line: where the tension sits is decided by what has been learned,
not by where the point is. Moving it to another atom needs a change of law, and at the floor learning has no step (`RISE-ESCAPE-20261110-001`).

## Scope

K_2 and K_3, two Fano atoms (A48), the floor states left by the sight-4 learner, the weight of A49.
