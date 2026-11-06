# Which knots competing rules on pairs can make

Status: Proved

Ticket `KNOT-COMPETITION-20261019-001A`, 2026-10-19. This proof serves open
question 10 of `docs/KNOT_INTUITION.md`. It does not choose a reading of that
question; it proves what each reading gives. It builds on
`KNOT-FOUNDATION-20261019-001E-P001`, the forgetting reading of the knot test.

## Standard statement

Call a Boolean relation R ⊆ {0,1}^m with m ≥ 3 a *knot* when it excludes at
least one point and, for every coordinate, its projection that forgets that
coordinate is all of {0,1}^(m−1). Equivalently, its excluded points are
nonempty and no two of them differ in exactly one coordinate. Call R a *least
set* of a function E : {0,1}^m → ℤ when R is exactly the set of minimizers of
E. Call E *pairwise* when it is a sum of terms that each depend on at most two
coordinates, that is, a quadratic pseudo-Boolean function.

- **(i)** For m = 3, a knot is a least set of a pairwise function exactly when
  its excluded points are a complementary pair {x, x̄}. These are the four
  not-all-equal relations. Each is the set of minimum-violation states of a
  frustrated triangle of agree and disagree preferences.
- **(ii)** For m ≥ 4, no knot is a least set of a pairwise function.
- **(iii)** With existentially quantified auxiliary variables, every relation
  on three variables with a satisfying point is the projection of the
  minimizer set of a sum of violated two-literal clauses. All 34 knots are
  among these relations.
- **(iv)** For any finite system of rules, the minimum-violation states are
  the satisfying states whenever the system is satisfiable. A system of rules
  on pairs whose solution set has every pair of coordinates free allows
  everything, so its solution set is never a knot on m ≥ 3 variables.

## Nearest known result

- **(i):** The minimizer sets of quadratic pseudo-Boolean functions are the
  vertex sets of faces of the correlation polytope, which is linearly
  equivalent to the cut polytope (Deza and Laurent 1997). In statistical
  language they are the facial sets, the supports of limits, of the binary
  pairwise exponential family (Geiger, Meek and Sturmfels 2006; Kahle 2010).
  A set Y is facial exactly when, for every circuit u of the model, the
  positive support of u lies in Y if and only if the negative support does
  (Rauh, Kahle and Ay 2011). On three variables the pairwise model has a
  single circuit, the alternating sum over the cube, so (i) is an instance of
  that criterion. The not-all-equal sets are the triangle-inequality facets.
- **(ii):** This applies the same criterion with the alternating sums over
  three-dimensional subcubes. A bounded search did not find it stated for
  relations whose every one-coordinate projection is full.
- **(iii):** This is the gadget of Garey, Johnson and Stockmeyer (1976), which
  proves MAX 2-SAT NP-complete.
- **(iv):** The first half is immediate. The second half is a special case of
  majority closure (Schaefer 1978); here it needs no auxiliary variables and
  has a two-line proof.
- **Statistical counterpart:** frustrated pairwise couplings give negative
  interaction information, the usual sign of synergy (Matsuda 2000; Rosas et
  al. 2022; Caprioglio, Mediano and Berthouze 2026). The results here are the
  zero-temperature, support-level version.

Novelty: `known-overlap-found`. The delta is (ii) as a statement about knots
of every size, the complete classification in the program's vocabulary, and a
Lean check of all four parts.

## The two readings

A system of rules has two readings when its rules cannot all hold:
- **strict:** it allows the states that break no rule;
- **competition:** it allows the states that break the fewest rules.

A rule on two variables costs one when broken, so the competition reading of
rules on pairs allows exactly the least set of a pairwise function. Parts
(i)–(ii) say which knots that can be. Part (iv) says the strict reading never
gives one.

## Proof

**Slice lemma.** For distinct coordinates i, j, k and a point x, let S(E) be
the alternating sum of E over the eight points that agree with x outside i, j
and k. The sign of each point is the parity of the number of coordinates
flipped from x. If a term depends on at most two coordinates, one of i, j and k
is not among them. Pairing each point with its flip in that coordinate cancels
the sum. By linearity S(E) = 0 for every pairwise function. In the kernel this
is `slice_vanishes`.

**Opposite corner.** Let R be a knot that is the least set of a pairwise
function E, and shift E so that its least value is c. Then E = c on R and
E > c off R. Take an excluded point e. Its neighbours e⊕i, e⊕j and e⊕k are
allowed, because a knot never excludes two neighbouring points. If the
opposite corner e⊕i⊕j⊕k were also allowed, S(E) would be at least
E(e) − c > 0. So the opposite corner of every slice through an excluded point
is excluded too (`opposite_in_slice`).

**(ii).** Take four distinct coordinates i, j, k and l and an excluded point
e:
1. The slice through e on i, j and k makes e⊕i⊕j⊕k excluded.
2. The slice through that point on i, j and l makes e⊕k⊕l excluded.
3. Now the slice through e on k, l and i contains two excluded points, e and
   e⊕k⊕l, and both enter S(E) with sign plus.
4. Every minus point of that slice is allowed. Three are neighbours of e, and
   e⊕k⊕l⊕i is a neighbour of e⊕k⊕l.
5. So S(E) ≥ (E(e) − c) + (E(e⊕k⊕l) − c) > 0, which contradicts the slice
   lemma (`no_knot_on_four_distinct`).

**(i).** On three variables the slice through an excluded point e is the whole
cube, so its opposite ē is excluded. Every other point of the cube is a
neighbour of e or of ē, so a knot excludes nothing else (`cube_cover`,
`knot_is_nae`). Conversely, the three preferences "disagree relative to e" on
each pair cost 3 at e and at ē and 1 everywhere else (`frustrated_energy`). So
their least set is the not-all-equal relation around e (`frustrated_least`),
which is a knot (`nae_is_knot`). The classification is
`three_variable_classification`. A triangle of agree and disagree preferences
has a knot as its least set exactly when an odd number of them say disagree,
that is, when it is frustrated (`triangles_knot_iff_frustrated`).

**(iii).** Take the ten clauses l₀, l₁, l₂, w, ¬l₀∨¬l₁, ¬l₁∨¬l₂, ¬l₀∨¬l₂,
l₀∨¬w, l₁∨¬w and l₂∨¬w with a hidden w:
- If one of l₀, l₁ and l₂ holds, the best choice of w breaks exactly three
  clauses; if none holds, it breaks four (`gadget_bound`, `gadget_best`).
- Give each excluded point b its own copy, with lᵢ read as "coordinate i
  differs from b".
- The least total over all points and hidden values is three per copy. It is
  reached exactly at the points excluded by no copy (`gadget_projection`).
- With one copy per excluded point of R, those are the points of R
  (`every_relation_by_gadgets`).

**(iv).** If some state breaks no rule, the least number broken is zero, so
the two readings coincide (`readings_agree_when_satisfiable`). Under the
strict reading, suppose the solution set of rules on pairs were a knot on
m ≥ 3 variables. Then every pair of coordinates would take all four value
pairs among the solutions, because forgetting a third coordinate frees the
rest. So every rule holds at every pair of values and excludes nothing,
which contradicts the binding condition (`strict_pairwise_no_knot`).

**Weights.** Doubling one preference of the frustrated triangle makes its
least set "those two differ", with the third variable free. That is not a knot
(`weighted_triangle_not_knot`). Competition depends on how the rules are
weighted, not only on which rules there are.

**Real and rational energies.** The kernel uses integer energies. Scaling by a
positive constant does not change a least set, so rational energies reduce to
integer ones. A real energy with a given least set gives a feasible finite
system of strict and non-strict linear inequalities with rational
coefficients, which then has a rational solution. This step is argued in
prose.

## Checks

`check.py` re-derives every finite claim by its own enumeration,
independently of the Lean source and of `tools/knotlab`. It decides
feasibility exactly, by Fourier–Motzkin elimination over the rationals, for
every knot on three and four variables. It compiles the kernel with Lean
4.32.2, confirms that the kernel uses only the standard axioms, and runs each
check once on a deliberately wrong input.

## Scope

- The competition reading concerns which states a system allows. It says
  nothing about probabilities at positive temperature, where pairwise models
  give full support.
- With hidden variables, pairwise competition reaches every knot, so a knot
  in what a system allows certifies only that its rules are not pairwise rules
  that must all hold.
- Which reading the foundation adopts is open question 10. Ticket B tests
  what each reading gives for near and far.
