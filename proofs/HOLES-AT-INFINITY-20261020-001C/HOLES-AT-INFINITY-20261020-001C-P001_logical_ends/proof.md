# The ends of a constraint system: things at infinity and trends

Status: Proved

Ticket `HOLES-AT-INFINITY-20261020-001C`, 2026-10-20. It builds on
`HOLES-AT-INFINITY-20261020-001B-P001` ("B" below), which treats Tseitin
systems on infinite graphs.

## Standard statement

Take a countable system of constraints over finite domains, each constraint on
finitely many variables and each variable in finitely many constraints. Call
two solutions equivalent when they differ in finitely many variables. This
relation is the homoclinic, or asymptotic, relation of symbolic dynamics. We
study its invariants that depend on finitely many variables, the Stone space
they define, and its invariants that do not.

The results:
- **Linear systems over GF(2).** The Stone space is the solution set modulo
  the closure of the finitely supported homogeneous solutions. Every
  non-constant parity of finitely many variables is changed either by a
  finitely supported homogeneous solution or by none. This covers Tseitin
  systems and Ledrappier's system on Z², which has no finitely supported
  homogeneous solution.
- **Finite stages.** Every relation among finitely many variables is already
  the relation of a finite subsystem.
- **Two-literal systems.** No three variables of a two-literal clause system
  form a K1–K3 knot.
- **Invariants that depend on no finite set of variables** separate solutions
  in three examples:
  - implication chains;
  - proper 3-colourings of Z², through the slope of their height functions;
  - Tseitin systems on the one-way ladder.

## Nearest known results

- **The homoclinic relation and homoclinic group.** Schmidt; Lind and Schmidt,
  *Homoclinic points of algebraic Z^d-actions* (JAMS 1999). For expansive
  algebraic actions the homoclinic group is nontrivial exactly when the entropy
  is positive.
- **Ledrappier's shift** (1978): zero entropy, mixing but not mixing of all
  orders.
- **Height functions of proper 3-colourings of Z².** Frozen colourings such as
  (x + y) mod 3, and slopes. See Peled and Spinka, *Lectures on random proper
  colorings of Z^d*; Chandgotia, Peled, Sheffield and Tassy; Ray and Spinka.
- **Majority closure.** Schaefer (1978) and Baker and Pixley (1975). The
  repository's foundation records that no two-literal system defines a knot
  (`KNOT-FOUNDATION-20261019-001`).
- **Stone duality** (Stone 1936).

**Classification: known with a delta.**
- The objects and examples are classical.
- Theorem 1, Theorem 2(a)–(b), Proposition 3 and Proposition 4 are routine,
  given the above.
- The delta is reading them through the canonical knot test:
  - "loop" and "end", as sources of open distinctions, are relative to the law
    (Theorem 2(d));
  - the knot test sees things at infinity but not trends (Theorem 5).

## Setting

- **The system.** Φ is a locally finite constraint system: a countable set of
  variables with finite domains, and countably many constraints, each a
  relation on finitely many variables (its scope), with each variable in
  finitely many scopes. Sol(Φ) is closed in the product space, hence compact.
  We assume it is nonempty.
- **Readable functions.** A function on Sol(Φ) with values in a finite set is
  readable if it depends on finitely many variables. Equivalently, it is
  continuous.
- **Finite change.** For solutions s and s′, s ~ s′ means they differ in
  finitely many variables.
- **Things and ends.**
  - A readable function is **rigid** if it is constant on ~-classes.
  - A non-constant rigid function is a **thing at infinity**: it can be read
    on finitely many variables, but only an infinite change alters it.
  - ℛ(Φ) is the set of rigid {0,1}-valued functions.
  - s ≈ s′ means every rigid function agrees on s and s′.
  - The **ends** of Φ form the Stone space Ends(Φ) of ℛ(Φ).
- **Trends.** An invariant of ~ that is not constant on some ≈-class is a
  **trend**. Trends exist exactly when some ≈-class contains more than one
  ~-class. A trend is never readable. So no relation among variables, and
  hence no K1–K3 verdict, can see it.

## Statements

**Theorem 1 (structure).**
1. ℛ(Φ) is a Boolean algebra of clopen subsets of Sol(Φ).
2. The map q: Sol(Φ) → Ends(Φ) is a continuous surjection onto a compact,
   Hausdorff, totally disconnected space. Its fibres are the ≈-classes, which
   are closed unions of ~-classes.
3. If some ~-class is dense, Ends(Φ) is a point.
4. If every ~-class is a single solution, every readable function is rigid and
   q is a homeomorphism.

**Theorem 2 (linear systems: loops and ends depend on the law).** Let Φ be a
locally finite system of GF(2)-linear equations. Let K be its homogeneous
solution group, K_fin the finitely supported elements of K (the law's finite
loops), and K̄ the closure of K_fin.

- **(a)** Sol(Φ) = x₀ + K. The ~-classes are the cosets of K_fin, the
  ≈-classes are the cosets of K̄, and Ends(Φ) ≅ Sol(Φ)/K̄.
- **(b)** For each finite set F of variables, the parity p_F is exactly one
  of:
  - **fixed**: it vanishes on K;
  - **loop-supplied**: it is non-zero on K_fin, so a finite change flips it;
  - **end-supplied**: it vanishes on K_fin but not on K, so it is rigid and
    open.

  The rigid functions are exactly the functions of finitely many end-supplied
  parities.
- **(c) Tseitin systems.** For Tseitin systems on connected, locally finite,
  infinite graphs:
  - K_fin is the finite cycle space;
  - the three types are those of B's Theorem 1;
  - Ends(T(G, c)) is the space M_c of B's Proposition 2.

  When c has finite support and c(V) = 1, the graph's end space embeds in
  Ends(T(G, c)) as the solutions whose hole escaped undivided to one end.
- **(d) Ledrappier's system on Z².** The system is
  x(i,j) + x(i+1,j) + x(i,j+1) = 0 for all (i,j).
  - K_fin = 0. No finite change is possible, every readable function is rigid,
    and Ends(Φ) ≅ Sol(Φ).
  - Every triangle {(i,j), (i+1,j), (i,j+1)} carries a parity knot that passes
    K1–K3, and all of its openness is supplied by ends, although Z² has only
    one end.
  - On the same grid, Tseitin's vertex law gets all of its openness from finite
    loops and has a single end class (B).

**Proposition 3 (finite stages).** Let Φ₁ ⊆ Φ₂ ⊆ … be finite constraint sets
with union Φ, and let A be a finite set of variables. The projections π_A
Sol(Φ_n) decrease and are eventually equal to π_A Sol(Φ). So every relation
among finitely many variables, and every knot among them, is the relation of a
finite stage.

Rigidity is not decided at any finite stage. B's Theorem 3 gives two systems
that agree on every constraint within radius N, in one of which a parity is
rigid while in the other it is not.

**Proposition 4 (two-literal systems).** Suppose every constraint of Φ is a
clause of at most two Boolean literals.
- For any three variables, the projection of Sol(Φ) is majority-closed. So it
  is not a K1–K3 knot.
- Things at infinity can still exist. The equality chain x_i ↔ x_{i+1} on the
  natural numbers makes x₀ rigid and open.
- Knots whose variables are all rigid exist once three-variable constraints
  are allowed. One example: a not-all-equal constraint on a₁, b₁, c₁, whose
  variables are continued by equality rays a_i ↔ a_{i+1}, b_i ↔ b_{i+1} and
  c_i ↔ c_{i+1}. By Proposition 3 this knot is the relation of the finite
  stage holding the centre. Infinity supplies its rigidity, not the relation.

**Theorem 5 (trends).**
- **(a) Implication chains.** Take x_i → x_{i+1} on Z.
  - Sol is the set of threshold sequences together with the all-0 and all-1
    sequences. These make three ~-classes, and the threshold class is dense.
  - So Ends is a point.
  - "Where the switch went" (+∞, −∞, or nowhere) is a trend.
- **(b) Proper 3-colourings of Z².**
  - The flat colouring (x + y) mod 2 has a dense class, so Ends is a point.
  - The plane colouring (x + y) mod 3 is frozen: its class is a single
    colouring.
  - The slope lim h(n, 0)/n of the height function, where it exists, is a
    finite-change invariant. It is 0 on the flat class and 1 at the plane, so
    it is a trend.
- **(c) Tseitin systems on the one-way ladder.** Let D be the edge set of both
  rails and the first rung: a double ray whose two tails go to the same end,
  that is, a circle through the end.
  - For every solution x, x and x + D differ in infinitely many edges, so they
    lie in different ~-classes.
  - The ladder has one end, so they lie in the same ≈-class.
  - So the circle through the end is a trend, not a thing.

## Proofs

**Proof of Theorem 1.**
1. Rigid functions are closed under the Boolean operations.
2. For s ∈ Sol(Φ), the family U_s = {A ∈ ℛ : s ∈ A} is an ultrafilter of ℛ.
   - The map s ↦ U_s is continuous: the preimage of a basic set is some A,
     which is clopen.
   - It is onto: an ultrafilter of ℛ is a family of closed sets with the
     finite intersection property, so by compactness some s lies in all of
     them, and then U_s equals it.
   - The fibres are the ≈-classes by definition. Each is an intersection of
     clopen sets, and a union of ~-classes because rigid functions are
     ~-invariant.
3. Let C be a dense ~-class and A ∈ ℛ. Either A contains C, and then A, being
   closed, contains the closure of C, which is Sol. Or A misses C, and then A,
   being open, misses the closure of C, so A = ∅.
4. If every ~-class is a single solution, every readable function is
   invariant. The clopen sets separate the points of a product space, so q is
   a continuous bijection from a compact space to a Hausdorff space, hence a
   homeomorphism. ∎

**Proof of Theorem 2.**
- **(a) The ~-classes.** Sol(Φ) = x₀ + K. Two solutions differ in finitely many
  variables exactly when their difference lies in K_fin.
- **(a) Same coset of K̄ ⟹ s ≈ s′.**
  - Let f be rigid, read on a finite set A, and let k̄ ∈ K̄.
  - Some k ∈ K_fin agrees with k̄ on A, so f(s + k̄) = f(s + k) = f(s).
- **(a) s ≈ s′ ⟹ same coset of K̄.** Suppose s − s′ ∉ K̄.
  - Then for some finite A, the restriction (s − s′)|_A lies outside
    W_A = π_A(K_fin), since an element of K whose every finite restriction lies
    in π_A(K_fin) is in the closure.
  - Some linear functional λ on GF(2)^A vanishes on W_A and is 1 on
    (s − s′)|_A.
  - Then f(x) = λ(x|_A) is readable, invariant under K_fin, and separates s
    from s′.
- **(a) Ends.** Hence the fibres of q are the cosets of K̄, and
  Ends(Φ) ≅ Sol(Φ)/K̄.
- **(b) The three types.** p_F is constant on x₀ + K exactly when it vanishes
  on K.
  - If p_F(k) = 1 for some k ∈ K_fin, then s and s + k differ finitely and
    have different values.
  - If p_F vanishes on K_fin but not on K, it is open and K_fin-invariant, so
    rigid.
- **(b) Rigid functions.**
  - A rigid f read on A takes equal values whenever two inputs differ on A by
    an element of W_A: shift by the corresponding element of K_fin.
  - So f depends only on the class of x|_A modulo W_A. That class is read by a
    basis of the functionals that vanish on W_A, and each of these is a parity
    p_F that vanishes on K_fin: either fixed or end-supplied.
- **(c) Tseitin systems.**
  - K = Z (even-degree sets), and K_fin = Z_fin, since a finite even-degree set
    is a sum of finitely many circuits.
  - So "loop-supplied" means a circuit meets F oddly.
  - "End-supplied" means p_F vanishes on Z_fin but not on Z. By B's Theorem 1,
    that is an end-separating cut.
  - Ends = Sol/Z̄_fin, which is M_c by B's Proposition 2.
- **(c) Geometric ends inside.**
  - An end ω gives the ultrafilter {X ∈ 𝔅 : ω lives in X} of 𝔅 modulo the
    finite sets. Conversely, a non-principal ultrafilter picks one infinite
    component of G − S for each finite S. These components are nested and
    determine an end. So the end space is the Stone space of 𝔅 modulo the
    finite sets (classical).
  - Its points are the multiplicative measures δ_ω.
  - When c(V) = 1, δ_ω ∈ M_1 is the class of solutions whose hole went entirely
    to ω.
- **(d) K_fin = 0.** Suppose k ∈ K_fin is non-zero. Let j* be the highest row
  meeting its support.
  - For every i, the equation at (i, j*) gives k(i, j*) = k(i+1, j*), since row
    j* + 1 is zero.
  - So row j* is constant, and having finite support it is zero. This
    contradicts the choice of j*.
- **(d) Every triangle is a knot.**
  - Every row r extends to a solution. Rows above are determined:
    x(i, j+1) = x(i,j) + x(i+1,j). Rows below are solvable: choose x(0, j−1),
    then propagate x(i+1, j−1) = x(i, j−1) + r(i) to the right and the
    corresponding rule to the left.
  - So (x(0,0), x(1,0)) takes all four values, and x(0,1) is their sum. The
    projection onto a triangle is therefore the even parity on three variables,
    which passes K1–K3 (knotlab).
  - Since K_fin = 0, every open parity is end-supplied. ∎

**Proof of Proposition 3.**
- More constraints give fewer solutions, so the projections decrease, and as
  finite sets they stabilize at some P ⊇ π_A Sol(Φ).
- Conversely, take a ∈ P. The closed sets {s ∈ Sol(Φ_n) : s|_A = a} are
  nonempty and decreasing. By compactness they meet, and a point of the
  intersection is a solution of Φ with s|_A = a. ∎

**Proof of Proposition 4.**
- **No knot.** By Proposition 3, it suffices to consider a finite stage. The
  majority of three assignments that satisfy a two-literal clause satisfies
  it: one of the clause's two literals is true in at least two of the three.
  Projections preserve majority closure.
  - A majority-closed relation is the intersection of its binary projections
    (Baker–Pixley).
  - A K1–K3 relation has all binary projections full (K2) but is not full
    (K1).
- **The equality chain** has two solutions, all-0 and all-1, which differ
  everywhere. So x₀ is open and no finite change alters it.
- **The not-all-equal centre.**
  - Its projection allows six of the eight states. K1 holds. Every pair
    extends, so K2 holds. K3 holds.
  - Changing a₁ forces a change along its whole ray, so a₁ is rigid; the same
    holds for b₁ and c₁. ∎

**Proof of Theorem 5.**
- **(a) Implication chains.**
  - The solutions are the non-decreasing 0/1 sequences: constant, or with one
    switch.
  - Any two thresholds differ finitely. The all-0 and all-1 sequences differ
    from every other solution infinitely.
  - Every window pattern of a solution is non-decreasing, so some threshold
    shows it, and the threshold class is dense. Theorem 1.3 applies.
- **(b) Height functions.**
  - A proper 3-colouring c lifts to h: Z² → Z with |h(u) − h(v)| = 1 on edges
    and h ≡ c mod 3. The increment along an edge is +1 when the colour rises by
    1 mod 3, and −1 otherwise.
  - Around a unit square the four increments sum to 0 mod 3 and lie in
    {−4, −2, 0, 2, 4}, so they sum to 0. Since the unit squares generate the
    cycles of Z², h is well defined.
- **(b) The flat class is dense.** Let t be a proper colouring, W a finite
  box, and h_t a lift of t. Add 3 if needed so that h_t has the parity of
  x + y.
  - For m ≥ 0, put H(v) = max_{w∈W} (h_t(w) + 6m − |v − w|₁).
  - Each term is a height function in v, and all terms have the same parity.
    The maximum of two height functions of the same parity is again one, so H
    is a height function.
  - On the box W, h_t is 1-Lipschitz in the L1 distance, so H = h_t + 6m there.
  - Let g = max(H, flat), where flat(v) = (x + y) mod 2 ∈ {0, 1}. For m large,
    g = h_t + 6m on W. Far from W, H < 0 ≤ flat, so g = flat outside a finite
    set.
  - Then g mod 3 is a proper colouring that differs finitely from the flat one
    and agrees with t on W.
- **(b) The plane is frozen.** Let h(x, y) = x + y, let g agree with h outside
  a finite set, and put D = g − h, which is even.
  - Along an edge from u to v in the +x or +y direction,
    D(v) − D(u) = (g(v) − g(u)) − 1 ∈ {0, −2}.
  - So D does not increase in the +x direction. Moving that way eventually
    leaves the finite set, which gives D ≥ 0. Moving in the −x direction gives
    D ≤ 0. So D = 0.
- **(b) The slope is a trend.**
  - A finite change alters h only on finitely many vertices: lift both
    colourings from a common far vertex, and the lifts agree on the infinite
    component of the complement of the change.
  - So the slope is invariant. It is 0 for the flat colouring, whose heights
    are bounded, and 1 for the plane.
  - The plane and the flat colouring lie in one ≈-class, because Ends is a
    point, but in different ~-classes.
- **(c) The ladder's circle.**
  - D has even degree everywhere, so x + D is a solution, and D is infinite.
  - The one-way ladder has no end-separating cut, so Z = Z̄_fin, and x and
    x + D lie in the same ≈-class (Theorem 2(a)). ∎

## Checks

`check.py` calibrates the statements on declared instances. It rewrites
`result.json` and replays it.

- **Theorem 2 on Tseitin's grid.** Over the 24 edges incident to the 3×3 box,
  all 2^24 parities were checked:
  - 512 fixed;
  - 16,776,704 loop-supplied;
  - none end-supplied.

  The finite loops inside the box of radius 5 span 64 dimensions.
- **Theorem 2 on Ledrappier's grid.** Over the 9 sites of the 3×3 box, all 512
  parities were checked:
  - 16 fixed;
  - 496 end-supplied;
  - none loop-supplied.

  There is no finitely supported homogeneous solution inside boxes of radius
  3–7. Each triangle's relation is the even parity on three variables, and
  knotlab calls it a knot.
- **Proposition 3.** The projections were stable at three consecutive radii
  for both linear systems and for all two-literal systems.
- **Proposition 4.**
  - In 12 random satisfiable (planted) two-literal systems on Z, all 120
    triples of variables near the origin are majority-closed and none is a
    knot.
  - The equality chain's x₀ is open, and it has exactly one solution once its
    tail is fixed.
  - The not-all-equal centre with equality legs is a knot that is not
    majority-closed, with exactly one solution once its leg ends are fixed.
- **Theorem 5(a).** The implication chain's 6 window patterns are all shown by
  thresholds. All-0 and all-1 admit no finite change inside the window; a
  threshold admits 11.
- **Theorem 5(b).**
  - 150 random proper colourings of a 4×4 window were patched into the flat
    colouring. The results are valid, agree on the window, and change it only
    within radius 13 of a box of radius 24.
  - With its boundary fixed, the plane colouring has exactly one completion in
    boxes of side 4–6.
- **Theorem 5(c).** The ladder's circle D has even degree, meets every fixed
  parity evenly, and changes some readable parity.

**Controls**, each a mathematically wrong input that the checks reject:
- counting Ledrappier's boundary-supported homogeneous solutions (22 of them)
  as loops calls all 496 open parities loop-supplied;
- adding a three-variable parity to the two-literal systems produces knots and
  breaks majority closure;
- an unconstrained chain has 128 completions of its tail, so it is not rigid;
- a two-literal centre on the rigid legs gives no knot;
- patching into the frozen plane leaves every box, in 20 of 20 cases;
- the frozen test applied to the flat colouring finds 2 completions.

## What this does not show

- **The general theory is not new.** It is the homoclinic relation of symbolic
  dynamics, specialized to finite supports. What is new is the reading through
  the knot test.
- **Rigidity outside linear systems is not classified.** The non-linear
  examples here have either a dense class (no things at infinity) or rigidity
  inherited from equality chains. Whether a non-linear law can supply rigid
  distinctions in another way remains open.
- **Nothing here is metric.** The slope of a height function is an invariant of
  the law's solutions. Reading it as geometry would need the native-path work
  that the foundations require first.
