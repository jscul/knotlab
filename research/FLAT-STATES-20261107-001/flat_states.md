# Flat states and the width of the sphere's count

Epic `FLAT-STATES-20261107-001` (program complexity), 2026-11-07.

## The question

**The request.** The owner asked for both of `SPHERE-COUNT-20261106-001`'s options ("Could you do both of these?"):
- **The flat-state pursuit lemma.** Build flat states on the whole sphere, re-route the vortex's boundary curves through the free region,
  and run the giant-component Duplicator for resolution width Θ(√n).
- **The literature search.** Look for planar height-function principles with known resolution bounds, hoping for a reduction.

**The agreed stop.** The width bound proved, a trapping configuration found, or a reduction to a named lemma, with the literature
verdict recorded.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Flat states exist on the whole sphere.** Sublattice-and-sign frames are flat except at the six corners, and each corner twists labels by exactly −1. So one counterclockwise vortex balances the sphere: for every point z and every cut along six disjoint paths from z to the corners, one constant label developed over the cut sphere violates exactly one line, through z. | proved (every k); 924 states checked, k = 2..12 | A |
| 2 | Re-routing the cut inside a region changes colours only there. From shortest cuts the vortex steps to each neighbour inside radius 3 (360 of 360 steps, at most 5 points changed). | proved (locality); measured (steps) | A |
| 3 | **The knot sphere contains Sperner's lemma.** Doubling a 2D Sperner colouring into labels inside a triangular region gives an assignment of K_k. Each point reads at most two Sperner colours, and the violated lines lie exactly in the fully labelled triangles oriented like the boundary; oppositely oriented ones hold full faces instead. So one-sided 2D Sperner reduces to "find a violated line" by depth-2 decision trees, and query and resolution-width lower bounds transfer. | proved; local lemma exhaustive; 3,759 colourings, m = 3..6 | B |
| 4 | **Window criterion.** Pebbled colours admit a Sperner state with a given full triangle iff an integer difference system on pebble sheets has no negative cycle. An obstruction between two positions needs a closed walk through pebbles whose free segments are short in total relative to the forced winding of its pebble chains. | proved; 1,411 of 1,411 solver comparisons | B |
| 5 | Width Ω(√n) for the knot spheres reduces to resolution width Ω(m) for grid Sperner, which reduces to a named winding-control lemma (open). No trapping configuration was found. | reduction | B |

## Answer

- **Not decided.** Whether the sphere's Euler count needs resolution width Θ(√n) is still open.
- **But the question has changed shape.** The knot's sphere is a Sperner problem on a closed surface: the six corner disclinations play
  the role of Sperner's boundary, and violated lines are its positively oriented panchromatic triangles. Any width or query lower bound
  for one-sided 2D Sperner now transfers. The frozen-state obstruction of `SPHERE-COUNT-20261106-001` is inherited unchanged: Sperner
  heights can be maximally tilted too.

## Literature verdict (the owner's second request)

**No ready-made reduction.**
- **No result for these formulas.** No source gives resolution bounds for planar not-all-equal, height-function, dimer or lozenge
  formulas.
- **Matching principles.** Dantchev–Riis ([FOCS 2001](https://www.cs.le.ac.uk/people/ssd6/FOCS01/paper.pdf); Dantchev's thesis
  [BRICS DS-02-2](https://www.brics.dk/DS/02/2/BRICS-DS-02-2.pdf)) and Alekhnovich (TCS 2004) bound matching principles on grids, and
  Tseitin.
- **Why they don't apply.** They work in edge (dimer) variables. Our formula is the point (height) encoding, where an edge variable is
  an XOR of two points. The dimer formula simulates ours, but not conversely, and restrictions of not-all-equal clauses never produce
  parity clauses.
- **Positive planar NAE is easy.** Positive planar not-all-equal instances are always satisfiable (Pilz; Hasan et al.;
  [arXiv:2412.03395](https://arxiv.org/abs/2412.03395)). The knot needs its Kasteleyn signs.

**What the search found instead (statement 3).** The nearest known principle is 2D Sperner, and it embeds.
- **Known bounds.** Its query complexity is Θ(√N) (Crescenzi–Silvestri 1998; Friedl–Ivanyos–Santha–Verhoeven 2005). Its tree-like
  resolution size is 2^Θ(n) (Itsykson–Malova–Oparin–Sokolov 2014, [arXiv:1412.1124](https://arxiv.org/abs/1412.1124)).
- **Their adversary is our pursuit.** It keeps a path with a buffer hiding the panchromatic triangle: the Sperner form of the vortex and
  its strings.
- **Width.** A resolution-width lower bound for grid Sperner was not found.
- **Classification.** Göös et al. ([arXiv:2205.02168](https://arxiv.org/abs/2205.02168)) characterize PPADS by unary Sherali–Adams.
  - If `TWO-ROUND-BRIDGE-20261106-001B`'s level-3 Sherali–Adams refutation has small coefficients, the sphere's search problem sits in
    PPADS (black-box).
  - Statement 3 puts one-sided Sperner below it, and pigeonhole bounds it above.
  - This is interpretation; the coefficients were not checked.

## Reading

**Parity against counting, once more.**
- **Tseitin.** Its contradiction is a Z2 charge, which has no tilt to freeze.
- **The knot's sphere.** Its contradiction is a Z6 vortex charge, whose net count must balance six corner charges of −1 each.
- **Topological pattern.** Charge balance on a closed surface is the Poincaré–Hopf / Sperner pattern, so the knot's first emergence on
  the sphere is a degree principle.

**Interpretation, not a theorem.** In the knot program's terms, the closed surface supplies the "boundary" that Sperner's lemma needs
from outside. The sphere's curvature, concentrated at six corners, forces a vortex, just as Sperner's boundary forces a panchromatic
triangle.

## Ratio

Since the epic opened, two proof families changed conclusions:
- A built the flat states;
- B found the Sperner reduction and the window criterion.

Administrative work: this note and the closure.

## Pending the owner

Carried from earlier epics; nothing new here:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the flat-state pursuit lemma | **Status:** Reduced, not proved | **Done.** Flat states exist on the whole sphere with local vortex steps (A). **Moved.** The width question is now a Sperner question (B). **Not done.** Steering the vortex past pebbled chains needs a winding-control lemma. |
| Local direction — pursuit on the knot's own states | Retire in favour of Sperner | Sperner is the same height problem with no corners, no signs and exact colours, and its bounds transfer by statement 3. |
| Broader exploration — width and size for the knot's spaces | Width reduced; size untouched | **Width.** ⟸ resolution width Ω(m) of grid Sperner ⟸ winding control. **Size.** Does not transfer through a depth-2 reduction automatically; Dantchev–Riis tiling games remain the template. |
| Long-term goal — the complexity of the knot's spaces | Real progress in understanding | The sphere's count is a one-sided Sperner (degree) principle with curvature as boundary. That explains why Sherali–Adams refutes it while resolution seems to fail: the PPAD/PPADS picture, where unary Sherali–Adams captures PPADS. |
| Next recommendation — the resolution width of 2D Sperner | **Next step:** Continue. A fresh epic proving resolution width Ω(m) for grid Sperner with a corridor Duplicator (the door path with a buffer) and the window criterion. The open point is winding control: keep forced winding along pebble chains small while pebbles come and go. | **If yes.** Width Θ(√n) for the knot spheres, and a width bound for grid Sperner not found in the literature. **If no.** A Sperner trapping pattern with few pebbles, which would show small width for both. **Alternative.** Check whether the level-3 Sherali–Adams refutation of the knot spheres is unary (1/3). Cheap; it would place the sphere's count in PPADS. |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The problem is now classical-looking. The tree-like adversary already exists (Itsykson et al.), and the exact feasibility criterion is proved. **Main uncertainty.** Whether windings can accumulate when pebbles are forgotten and re-placed. |
| Execution — that action | Deferred to the owner | **Not started.** **Stop when** the winding-control lemma is proved (giving width Ω(m) for Sperner and Ω(k) for K_k), or a trapping pattern is found. |
