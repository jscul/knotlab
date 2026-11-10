# Pre-registration: learning that grows a handle

Epic `GROW-HANDLE-20261110-001` (sub-goal B60; G15 with G4 and G1), written on 2026-11-10 before any grown space is built, at the
coordinator's go-ahead. Only sizes were looked at first: the octahedral knot sphere K_k has 4k² points and faces of 2 or 3 line corners.

## The question

On a sphere learning can move the forced dissonance but never remove it (`LEARN-HANDLES-20261109-001`, theorem 1). On a torus it can
remove a dissonance the class forces, by winding around the handle (theorem 3 there). Can a local growth move add the handle where the
dissonance sits, so that learning then removes it? And does it matter where the handle is grown?

## The growth move

- **The atom.** The Fano plane less one point P\*, with the signs of the Fano torus's untwisted law (all signs 0, the knot's uniform
  contradiction), whose incidence graph is the Heawood graph less a vertex.
- **The splice.** At a line l of the knot sphere K_k, remove l and P\*, and join l's three points to the three lines that went through
  P\*, in one of the three bijections compatible with both rotations (a 3-edge splice, `THREEFOLD-SURFACES-20261030-001`). The sphere's
  sides keep their signs, the atom's keep theirs, and the three new sides take the signs that leave no even face.
- **The knot space** of the spliced graph is read off its map: a builder turns a rotation system of a two-coloured cubic graph into a
  triangulated surface for `surface_lib.KnotSpace`. The builder is checked on its own first: rebuilt from their own rotation systems,
  K_2 to K_4 and the Fano torus must give the same counts (points, faces and their degrees, Euler characteristic, orientability,
  satisfiable classes, number of least states).
- **Where.** On K_2, K_3 and K_4, at the dissonance (the violated line l0 of a least state, for every line l0 up to the sphere's
  symmetry) and away from it (a line at each graph distance from l0, up to 4), with both chiralities of the atom and all three
  compatible bijections.
- **The state.** The sphere's least state x (one violated line l0, no over-agreement), extended to the atom's six points by the values
  that violate the fewest lines; it is then held fixed while learning acts (A26).

## Expectations, frozen

- **H1 (the grown space).** Every compatible splice gives a knot space on a torus (χ = 0), and the old law extends with no even face,
  uniquely up to gauge once the atom's class is fixed: the grown space's four classes match the atom's four. Expected proved by hand
  (splice lemma; parity at the three merged faces), and checked.
- **H2 (growth alone does not resolve).** The grown law is unsatisfiable: the atom acts on the three points as the line it replaced, an
  NAE relation, and in the grown law's class with the replaced line's own parity, so the sphere's contradiction survives. The other three
  classes act as the sphere's law with that line re-signed, which `RESIGN-STEER-20261107-001` proved satisfiable. So growth turns a
  dissonance the count forces into one the class forces: exactly one unsatisfiable class. Expected proved by hand, and checked by
  projecting the atom onto the three points and by SAT on every grown space.
- **H3 (learning then resolves it, through the new handle).** From the extended state learning resolves the dissonance, and every
  resolution winds through the grown handle, since every cycle on the sphere side is contractible. Proved from `LEARN-HANDLES-20261109-001`
  theorem 3 if H2 holds; checked by replaying walks into each other class.
- **H4 (placement, computed).** Grown at the dissonance, the extended state's violated line lies inside the atom, and the cheapest
  resolving walk costs a small constant that does not grow with k. Grown at distance d, the violated line stays at l0 and the cost grows
  with d. Learning works at every placement; placement sets the cost.
- **H5 (rules, computed).** The sight rule R3 of `NATIVE-TARGET-20261110-001` and the outside-distance rule R7 resolve every start;
  random moves R0 resolve within 50 V² steps.

## What would count against them

A grown law that is satisfiable (growth alone removes the dissonance; against H2), more or fewer than one unsatisfiable class, or a
result that depends on the chirality or the bijection (against H1 and H2); a start that learning cannot resolve, or a resolution that
does not wind through the atom (against H3, and against `LEARN-HANDLES-20261109-001` unless the check is wrong); a cost that does not
depend on the distance, or that grows with k at the dissonance (against H4).
