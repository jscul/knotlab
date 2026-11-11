# Where the unsettled runs ended

Status: Computed (`check.py`): `ADDRESS-STEER-20261110-001C` rerun exactly (same seed, order and moves), reproducing its counts (240 of
240 kept at one flip; 234 and 229 of 240 at two and three).

Words (2026-11-11). Reworded under the owner's language rule: a knot space is now a drawn knot pattern, its points
distinctions and its lines knots, and an atom (a Fano or torus atom) a piece (Intuitions guide, Glossary). The mathematics is
unchanged; the earlier text is in git history.

Its 17 unsettled runs at two or three flips:

- **7 reached the floor with the address changed.** In each, one acting piece (6 runs) or both (1 run) turned transparent during the
  return: (0, 2) → (2) twice, (0, 2) → (0) once, (1, 2) → (2) once, (0, 1) → (1) twice, (1, 2) → () once. The exact rule of
  `ADDRESS-STEER-20261110-001A` holds in all 7: every remaining acting piece holds a unit, and the freed units sit elsewhere (in the other
  pieces or at junctions). So these are learning steps in the return that wound through a piece's handle and erased its bit, as the rule
  allows; they are not exceptions to it.
- **10 stopped one unit above the floor.** Each ended at W = floor + 2 with no move that lowers W: a local minimum of the learner M1, which
  only lowers or keeps W, left by learning steps during the return.
