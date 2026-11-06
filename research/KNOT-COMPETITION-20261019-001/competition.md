# Knots from competition: both readings of question 10

Epic `KNOT-COMPETITION-20261019-001`, 2026-10-19. This is the epic's decision
note. It serves open questions 10 (competition) and 9 (space from a law) in
`docs/KNOT_INTUITION.md`. The repository owner chose not to decide question 10
in advance and asked for both readings to be tested.

## The two readings

When a system's rules cannot all hold, it has two readings:
- **strict:** it allows the states that break no rule, so a frustrated system
  allows nothing;
- **competition:** it allows the states that break the fewest rules (each
  rule instance weighted one unless stated otherwise).

The readings coincide whenever some state breaks no rule. They differ only on
frustrated systems.

## Results

| # | Result | Reading | Evidence | Novelty |
| --- | --- | --- | --- | --- |
| 1 | On three variables, a knot is the least set of a pairwise function exactly when it is a not-all-equal relation (two opposite states excluded). These are the frustrated triangles, 4 of the 34 knots. | competition | `KNOT-COMPETITION-20261019-001A-P001` (Lean) | known-overlap-found (facial sets of the pairwise model; triangle facets of the cut polytope) |
| 2 | On four or more variables, no knot is the least set of a pairwise function. | competition | `…001A-P001` (Lean, every m; exact check of all 742 knots on four variables) | candidate-local-delta (a corollary of the circuit criterion for facial sets; not found stated for knots) |
| 3 | With hidden variables, ten 2-clauses per excluded state make every relation on three variables with an allowed state, every knot among them, the projection of a least set. | competition | `…001A-P001` (Lean) | textbook (Garey, Johnson and Stockmeyer 1976) |
| 4 | Rules on pairs never allow exactly a knot on three or more variables. | strict | `…001A-P001` (Lean, without hidden variables); `KNOT-FOUNDATION-20261019-001E-P001` (with them) | known-overlap-found (majority closure) |
| 5 | Doubling one preference of the frustrated triangle removes the knot: competition depends on the weights. | competition | `…001A-P001` (Lean) | elementary |
| 6 | Among 470 uniform rules on pairs around a ring, none gives near and far under the strict reading, and 178 do under competition. None has more than two separation levels. Separation follows the layout (166), flattens it on frustrated rings, or singles out the opposite variable on the ring. | both | `KNOT-COMPETITION-20261019-001B-E001` (exploratory, exact) | no-overlap-found |
| 7 | On triangle strips and rings, competition counted per triangle equals strict not-all-equal knots on the triangles. Its separation then grows with layout distance (3 to 8 on 14 vertices), like a strict chain of atoms. Counted once per pair, the same rules collapse to a few ordered states with at most two levels. | competition | `KNOT-COMPETITION-20261019-001B-E002` (confirmatory, exact up to 14 variables) | no-overlap-found for the separation measure; the compilation is Wannier's ground-state condition |
| 8 | On the triangular lattice (3×3 and 4×4 tori), competition between neighbours that should differ equals strict not-all-equal on every triangle (42 states each). It has separations 3 and 4, following the lattice. | both | `…001B-E001` | classical ground states (Wannier 1950); the separation reading is new here |

### The compilation lemma

Take any set of triangles in which every pair of a triangle should differ,
and count, for each triangle, its own broken preferences. In other words,
weight each pair by the number of triangles that contain it. A triangle
whose three pairs should all differ breaks one preference when its states
are not all equal, and three when they are. The total cost is therefore at
least the number of triangles. It equals that number exactly when every
triangle is not-all-equal. So whenever some state makes every triangle
not-all-equal, competition allows exactly the states of the strict
not-all-equal law on the triangles. On the triangular lattice every pair lies
in two triangles, so plain per-pair counting already has this form. This is
Wannier's ground-state condition, and E002 checked it for every strip and ring
in its roster.

## What this means

- **Competition makes knots from pairs; the strict reading never does.** That
  is the whole difference between the readings, and it is exactly the
  difference between 2-SAT, which is easy, and MAX-2-SAT, which is NP-hard.
- **Competition makes only one kind of knot by itself:** the not-all-equal
  triangle, a loop of preferences that cannot close. Every other knot needs
  hidden variables, and on four or more variables none arises without them.
- **Knots survive competition only when the frustration is shared
  equally.** Unequal weights make competition select a few ordered states. It
  then leaves no alternatives, and knots need alternatives (ticket C of the
  foundation epic). With balanced weights, counted per triangle, the
  alternatives survive and so do the knots.
- **Near and far is always inherited from a layout.** Strict pairwise rules
  have none. Competition gives two levels in general, and separation that
  keeps growing only on a triangulated layout counted per triangle, where it
  equals a strict law of three-place knots. No tested rule produced near and
  far that its layout lacked. Symmetric rules cannot, since every pair looks
  the same.

So, for question 9, competition is a law that turns a triangulated layout
into a chain of knots, but it does not supply the layout. For question 10, the
two readings are now mapped:
- the strict reading keeps the foundation presentation-invariant and gives
  pairs no knots;
- the competition reading needs weights, a declared measure of violation, and
  in return lets frustrated pairs make one kind of knot.

Choosing between them remains the owner's decision. The evidence does not
force it.

## Literature comparison

Searched on 2026-10-19 (about ten queries):
- **Supports of pairwise models.** The minimizer sets of quadratic
  pseudo-Boolean functions are the facial sets of the binary pairwise
  exponential family, the faces of the correlation or cut polytope (Geiger,
  Meek and Sturmfels 2006; Kahle 2010; Rauh, Kahle and Ay 2011; Deza and
  Laurent 1997). Result 1 is an instance; result 2 is a corollary not found
  stated.
- **Frustration and synergy.** Negative higher-order mutual information as the
  signature of frustration (Matsuda 2000); pairwise frustrated couplings
  producing synergy (Rosas et al. 2022; Caprioglio, Mediano and Berthouze
  2026). Results 1 and 5 are the support-level, zero-temperature version.
- **MAX 2-SAT.** Garey, Johnson and Stockmeyer (1976): result 3.
- **Frustrated magnets.** Wannier (1950) for the triangular antiferromagnet;
  the frustration index of signed graphs (Harary 1959; Aref, Mason and
  Wilson, arXiv:1710.09876) is the least violation count of agree and differ
  rules.
- **Emergent geometry from frustration without a lattice.** Nothing found.
  Degeneracy in frustrated magnets comes from local lattice constraints, in
  line with result 7.

## Red-team review of E002 (same task, not independent)

- **Identifiability.** Per-triangle and per-pair counting are different laws
  on the same pairs; the run reports both, and the compilation check ties the
  first to the strict not-all-equal law.
- **Positive control.** The strict chain of atoms grows from two to six levels
  (n = 5 to 13), so the measure can detect growth.
- **Interpretation.** The per-triangle weights encode the triangles, so the
  growth is supplied by the layout and is not space from a law. The result is
  stated that way.
- **Range.** Up to 14 variables only. The growth is consistent with one level
  per two vertices, but no asymptotic claim is made.
- **Checker.** Rows on up to nine variables were recomputed through
  `tools/knotlab`, a different code path written in the same session.

## Portfolio count

Artifacts since the foundation epic closed:
- changed a mathematical or empirical conclusion: 3 (proof A, experiments E001
  and E002);
- administrative: 2 (this note and the closure ledger).

## Still open

- **Question 10** is mapped, not decided.
- **Question 9:** a law that produces a triangulated layout, rather than
  receiving one, is still missing. Competition does not provide it.
- **Whether separation keeps growing on larger triangulated surfaces.** The
  triangular tori tested have diameter two. This needs a targeted bond search
  rather than full enumeration.
