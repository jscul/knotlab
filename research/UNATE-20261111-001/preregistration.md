# Pre-registration: are maps of held points unate

Epic `UNATE-20261111-001` (backlog B136, G15 with G16), written on 2026-11-11 before the frozen searches run, at the coordinator's
go-ahead. Code frozen with this file in `proofs/UNATE-20261111-001A/UNATE-20261111-001A-P001_are_maps_of_held_points_unate/`
(`unate_lib.py`, `check.py`).

## The question

`THREE-IN-20261110-001` found, exactly on every class of six spaces, no map of three held points that is parity, majority or non-unate
(an input that moves the output both ways). Is every map of held points in every knot space unate, a theorem bounding what a learned knot
memory computes, or is there a gadget that computes a non-unate map such as parity?

## Is unateness forced by the definition? No (by hand, before any run)

A map of held points is the projection of the floor states (the states satisfying every line) onto the held points and the output. Its
definition gives exactly one constraint, theorem D of `IN-OUT-20261110-001`: flipping every point changes nothing, so the map is self-dual.
Self-dual non-unate maps exist as functions (parity of three inputs is one), so nothing in the definition excludes them. In general NAE
logic they are expressible: NAE-3SAT is NP-complete, so the polymorphisms of NAE on three places are only the projections and their
negations, and by the Galois connection of Post's lattice every relation closed under complement, the graph of three-input parity
included, is primitive-positive definable from NAE (with hidden points and equality). Any bound must therefore come from the shape of a
knot space: every point on exactly three lines, the lines and points forming a 2-coloured triangulation of a surface, and a Kasteleyn law.

## Prior work (checked before freezing)

- Planar NAE-3SAT is solvable in polynomial time (Moret 1988, by reduction to planar max-cut), while general NAE-3SAT is NP-complete.
  A planar gadget that crossed two wires would contradict that unless P = NP, so planarity limits what knot spheres can express.
- For planar constraint problems the Galois connection between polymorphisms and definable relations does not carry over (noted in the
  planar valued-CSP literature), so expressiveness under planarity needs its own treatment.
- A handle lets two wires cross without meeting. Knot spaces with handles (every learned memory has them) are therefore not limited the way
  planar ones are, and I expect them to express non-unate maps. No reference found states a unateness bound for NAE gadgets on surfaces.

## Not blind

To test the search code I ran it once on one off-plan space (seven points, seed 999, genus 4, not among the frozen seeds). It found 500
total majority maps (one re-read by SAT: the output is the minority of the three inputs) and no non-unate map. So majority is known to
occur in general knot spaces; `THREE-IN-20261110-001`'s "no majority" holds for its interfaces only.

## The searches (frozen; all exact)

- **Census 1.** `THREE-IN-20261110-001`'s census (radius 1) on `DEEP-MEM-20261111-001`'s spaces T1 and T3, every class.
- **Census 2.** On S1, radius 2: two sides of a group and one point of its radius-2 neighbourhood held, the output any point of that
  neighbourhood, every class.
- **Random small knot spaces.** n = 6, 8, 10, 12 points (and as many lines), seeds 0 to 199 for each n: a random 3-regular bipartite
  incidence with every line on three distinct points, a random rotation at every vertex, built into a 2-coloured triangulation of an
  orientable surface; its Kasteleyn law and every class; every floor state enumerated; every interface of three held points and one
  output read. Disconnected spaces are skipped and counted.
- **Re-read.** The first instance of each non-unate, majority, parity or other kind, read again by SAT.

## Mark and predictions

- **N:** some map of held points is not unate (mark holds if any non-unate map is found anywhere in the searches).
- Predictions: the censuses find no non-unate map (local structure, as before); the random search finds one (handles let wires cross), so
  N holds and unateness is not a theorem of knot spaces.
- **If N fails:** a proof attempt follows, by hand, with a referee pass; the epic stops at a theorem or at a clear statement of the step
  the proof cannot get past, with no further census.
- **If N holds:** the smallest instance found is the answer (a knot space whose held points compute a non-unate map), and no proof is
  attempted.

Assumptions in force: A20, A46, A47, A58. The searches are expected to take more than ten minutes and are registered in
`docs/LONG_RUNNING.md`.
