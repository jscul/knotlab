# Free tori

Status: Computed, exhaustive per torus (SAT over every state of each law). `check.py` (23 seconds), pre-registered in the addendum of
`research/OTHER-ATOMS-20261110-001/preregistration.md` (commit `6f43acb56`) before it ran.

## What is checked

Every simple lattice torus with at most 30 points, and every thin torus of even index with at most 40 points, grouped up to isomorphism
and mirror image by the exact canonical form of ticket A: 157 types. One point P per type, since lattice tori are point-transitive. For
each of the four classes: whether the Kasteleyn law has a satisfying state, and, for each of P's three sides, whether the law with that
side's sign flipped (two even faces, the side's ends) has one. The torus is **free** at P in a class when all three do.

## Results

- **D1.** All 157 types are free at their point in every class.
- **D2.** The class-forced types are the Fano torus (7,2,1) and one thin torus of each even index from 4 to 40, each with exactly one
  unsatisfiable class; every other type to 30 points has all four classes satisfiable.
- **D3.** On ticket A's 29 types, the role read from these facts alone (acts as its line where the torus is unsatisfiable, transparent
  where it is satisfiable) equals the role found on every splice: 6,960 class readings over 1,740 splices, no disagreement.

All three predictions held. With ticket A's theorem, every class-forced atom here (the Fano atom and the thin-torus atoms of even index to
40 points) acts as its line in exactly one class on any host, and holds a unit there; every other atom here is transparent in every class.
Not checked: tori that are not lattice quotients, and lattice tori past these sizes.
