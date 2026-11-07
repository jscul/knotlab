# Rulers: without ends, bond distance grows linearly

Status: Proved

Ticket `LOGIC-AXIS-20261107-001A`, 2026-11-07.

## Standard statement

Let X be a shift-invariant subshift of finite type on Z^d with finitely many binary coordinates per
site. Call a finite set S of coordinates a *circuit of X* if the projection of X to S is not all of
{0,1}^S while every projection to S minus one coordinate is all of {0,1}^(S minus it), and |S| >= 3.
For coordinates u, v let delta(u,v) be the least |S| - 1 over circuits S containing both.

1. If any two finite sets of coordinates more than D apart have independent projections (strong
   irreducibility restricted to finite sets), every circuit is D-chained. Hence delta(u,v) is at least
   the separation divided by D, and the delta-balls lie inside sup-norm balls of radius D·r.
2. A group shift over F2 whose finitely supported points are dense has this property, with D the
   diameter of a generating set of the finitely supported points.
3. For the cut space of Z^d, delta is between d_∞ and (2d − 2)(graph distance + 1) + 1. On the square
   lattice, for the cycle space and the cut space alike, delta is twice the graph distance plus 1 to 7.
   So delta-balls grow like r^d. For the chain of Horn clauses w(t-1) & L(t) -> w(t),
   delta(w(s), w(t)) = t - s + 1.
4. A group shift over F2 with one coordinate per site is either full or has no nonzero finitely
   supported point.
5. Each coordinate of a circuit can be flipped by a finitely supported change, and the circuit can
   still join points arbitrarily far apart.
6. Extending a system conservatively, so that its projection to the old coordinates is unchanged,
   never increases delta.

## Nearest known result

- **Strong irreducibility and specification.** For multidimensional shifts these are standard mixing
  conditions (Burton–Steif; Boyle–Pavlov–Schraudner).
- **Algebraic Z^d-actions.** Lind and Schmidt (*J. AMS* 12, 1999) show that for expansive actions the
  homoclinic group (here: the finitely supported points) is nontrivial and dense exactly when the
  action has completely positive entropy. Lind, Schmidt and Verbitskiy (*Ergodic Theory Dynam.
  Systems* 33, 2013) prove strong and homoclinic specification for principal actions of irreducible
  atoral polynomials when d >= 2.
- **Items 2 and 4.** Item 2 is a finite-set form of "a dense homoclinic group gives specification"
  for group shifts. Item 4 is the integral-domain argument behind Ledrappier's example.
- **Classification:** `known-with-delta`. What is new is the consequence for circuits and for the
  smallest circuit through two coordinates: a *ruler*, from which the lattice's dimension is read off
  the allowed states alone. Item 5 is a program-specific observation about the source-aware reading
  of nativity (adopted 2026-10-20).

## Setting

- **Laws and variables.** A *law* on Z^d is a set X ⊆ {0,1}^V of allowed states.
  - The variables are V = Z^d × T, with T a finite set of types (distinctions per site).
  - X is cut out by finitely many local constraints, shift-invariant, and nonempty.
  - The *site* of (t, τ) is t. Distances between variables are sup-norm distances between their
    sites; dist(A, B) is the least distance between a variable of A and one of B.
- **Projections.** For finite S ⊆ V, X_S is the set of restrictions of allowed states to S.
- **Knots** (K1–K3, erasure read as forgetting) are sets S with |S| >= 3 such that:
  - X_S is not all of {0,1}^S;
  - X_{S∖v} = {0,1}^{S∖v} for every v in S;
  - K3 holds because X is nonempty.

  A designated contact does not matter: the conditions are symmetric in the variables of S.
- **Bond distance** (`NATIVE-NETWORK-20261021-001`): δ(u, v) is the least |S| − 1 over knots S
  containing u and v, or ∞ if there is none.
- **Splitting.** X *splits at range D* if X_{A∪B} = X_A × X_B for all finite A, B with dist(A, B) > D.

**Parity laws.**
- **Definition.** X is a subgroup of (F_2^T)^{Z^d}.
- **Knots.** For finite S, X_S is a subspace, and X_S ≠ F_2^S exactly when some nonzero c in F_2^S
  satisfies Σ_{s∈S} c_s x_s = 0 on all of X. So S is a knot exactly when it is the support of an implied
  parity check, no proper subset of S supports one, and |S| >= 3: a circuit of the binary matroid of the
  coordinate functionals.
- **Finite moves.** F is the set of allowed states of finite support, the law's *finite moves*. As
  Laurent polynomials it is a submodule of R^T, with R = F_2[x_1^±, …, x_d^±].

## 1. Splitting makes every knot chained

**Theorem 1.** Suppose X splits at range D. Then:
- every knot S is *D-chained*: for every partition S = A ⊔ B into nonempty parts, dist(A, B) <= D;
- consequently |site(u) − site(v)|_∞ <= D·(|S| − 1) for u, v in S, so δ(u, v) >= |site(u) − site(v)|_∞ / D;
- every bond ball {v : δ(u, v) <= r} lies inside the sup-norm ball of radius D·r about site(u), and
  has at most |T|·(2Dr + 1)^d variables.

*Proof.*
1. Let S = A ⊔ B with A, B nonempty and dist(A, B) > D.
2. A ⊆ S ∖ {b} for any b ∈ B. By K2, X_{S∖b} is full, and every projection of a full relation is full,
   so X_A is full. Likewise X_B is full.
3. Splitting gives X_S = X_A × X_B, which is full. This contradicts K1.
4. So the graph on S that joins variables at distance <= D is connected. A path in it from u to v has at
   most |S| − 1 steps of length <= D. ∎

## 2. Parity laws without ends split

**Proposition 2.** Let X be a parity law whose finite moves F are dense in X (product topology). By
HOLES-AT-INFINITY C-P001, X / closure(F) are the law's ends, so this says the law has no ends. Then:
- F is a finitely generated R-module, say by g_1, …, g_r;
- with D = max_i diam(sites of supp g_i), X splits at range D.

*Proof.*
1. F is a submodule of the Noetherian module R^T, so it is finitely generated. Every finite move is a
   finite sum of shifts of the g_i.
2. Let A, B be finite with dist(A, B) > D, and let c ∈ F_2^{A∪B} vanish on X_{A∪B}. Write c = c_A + c_B.
3. A shift g of a generator has sites of diameter <= D, so its support meets at most one of A and B.
   In either case ⟨c_A, g⟩ ∈ {⟨c, g⟩, 0} = {0}.
4. Hence c_A vanishes on all of F. Because c_A has finite support it is continuous, so it vanishes on
   closure(F) = X.
5. So the annihilator of X_{A∪B} is the direct sum of the annihilators of X_A and X_B, and
   X_{A∪B} = X_A × X_B. ∎

For finite systems (boxes) the same argument applies with F = X.

## 3. Lattices and the thread: rulers with the lattice's dimension

**Proposition 3b (Tseitin's law on Z^D, D >= 2).** The variables are the edges, and the edges at every
vertex sum to 0.
- **The setting.**
  - The allowed states are the even subgraphs.
  - The finite cycles are dense: close a finite window of an even subgraph through the connected
    annulus outside it.
  - Plaquettes generate the finite cycles, with D = 1.
  - The knots are the finite bonds δ(U): U finite, U and its complement connected.
- **The bound.** For edges e, f let d be the least graph distance between an endpoint of e and one of f.
  Then |site(e) − site(f)|_∞ <= δ(e, f) <= (2D − 2)(d + 1) + 1.

*Proof.*
- **Lower bound.** Theorem 1 with Proposition 2.
- **Upper bound.**
  1. Let a ∈ e and c ∈ f be the closest endpoints, at distance d.
  2. The other endpoint a′ of e satisfies d(a′, c) >= d by the choice of a and c. So a′ is on no
     shortest a–c path, and likewise c′ is on none.
  3. Let U be the vertex set of a shortest path. It is connected, and its complement is connected
     since D >= 2. Exactly one endpoint of e and one of f lie in U.
  4. Hence δ(U) is a bond through e and f, with |δ(U)| = 2D(d + 1) − 2d = (2D − 2)(d + 1) + 2. ∎

**Proposition 3a (gauge law on Z^2).** The variables are the edges, and every plaquette's four edges sum
to 0.
- **The setting.**
  - The allowed states are the gradients dφ (Z^2 is simply connected).
  - The finite moves are the gradients of finite φ, which are dense. Vertex flips generate them, with
    D = 1.
  - The implied checks are the finite even edge sets, so the knots are the simple cycles.
- **The bound.** For edges e, f at graph distance d (closest endpoints), 2d + 1 <= δ(e, f) <= 2d + 7.
  Computed on a 41×41 box, δ − 2d takes only the values 1, 3 and 5.

*Proof.*
- **Lower bound.** A cycle through e and f consists of e, f and two vertex-disjoint paths joining their
  endpoints. Each path has length >= d.
- **Upper bound, by planar duality.**
  1. The simple cycles of Z^2 are the bonds of its dual lattice, which is again Z^2 with the unit
     squares as vertices. Each edge corresponds to the dual edge joining the two squares beside it.
  2. Every square beside e has both endpoints of e as corners, and likewise for f. So some square beside
     e and some square beside f are at dual distance d* <= d + 2.
  3. Apply Proposition 3b's construction in the dual, with D = 2. It gives a cycle through e and f of
     length 2d* + 4 <= 2d + 8: the boundary of a shortest path of squares. ∎

Tseitin's law on Z^2 is the gauge law of the dual lattice, so it obeys the same two-sided bound in the
dual distance.

**Corollary (dimension from allowed states).** For these laws a bond ball of radius r has between c·r^D
and C·r^D variables, where D = 2 for the gauge law and Tseitin's on Z^2, and D >= 2 for Tseitin's on
Z^D.
- **Upper count.** Theorem 1.
- **Lower count.** The upper bounds.
- **What this means.** Bond distance is computed from allowed states alone, so the growth exponent of
  bond balls recovers the lattice's dimension without the drawing. On the gauge law it is ℓ¹
  (taxicab) distance, up to a factor 2 and a bounded error: an x-count plus a y-count.

**Proposition 3c (the atom thread on Z).** There are two types per site, a loop L_t and a witness w_t.
At every t the atom ¬w_{t−1} ∨ ¬L_t ∨ w_t holds. Then for s < t:
- δ(w_s, w_t) = t − s + 1;
- every knot through w_s and w_t contains L_{s+1}, …, L_t.

*Proof.*
1. **Cutting at a loop.** Fix s < r <= t. Glue any two allowed states x and y at r:
   - use x at sites < r;
   - set L_r = 0, and take w_r from y;
   - use y at sites > r.

   L_r = 0 frees w_r, so the result is allowed.
2. So whenever L_r ∉ S, X_S factors as (variables of S at sites < r) × (the rest). Both factors
   are nonempty, since one contains w_s and the other w_t. By K2 both are full, so X_S is full and S is
   not a knot.
3. Hence every knot through w_s and w_t contains every L_r with s < r <= t, so δ >= t − s + 1.
4. **The knot that attains it.** S = {w_s, L_{s+1}, …, L_t, w_t} projects to the single clause
   ¬w_s ∨ ¬L_{s+1} ∨ … ∨ ¬L_t ∨ w_t.
   - Any assignment that satisfies this clause extends: up to the first L_r = 0, set the witnesses to
     the forced values; from there on, set them to w_t's value.
   - So this set is a knot of size t − s + 2.
   - The same gluing shows the thread splits at range 1. ∎

So on the thread, the smallest knot joining two witnesses contains exactly the loops between them.
Bond distance counts loops: a number line whose unit is one open distinction. A chain of two-place
ties x_t = x_{t+1} has no knot at all (check 5), so it carries no bond distance.

## 4. One distinction per site: no finite moves

**Proposition 4.** Let X be a parity law with |T| = 1. Then either X = F_2^{Z^d} or F = {0}.

*Proof.*
1. If X is not full, some nonzero p ∈ R is an implied check: Σ_s p_s x(t + s) = 0 for all x ∈ X and
   all t, by shift invariance.
2. For finite c ∈ F this says p(x^{−1})·c = 0 in R.
3. R is an integral domain, so c = 0. ∎

**Consequence.** Ledrappier's law, the Newman–Moore law and every other one-bit parity law on a
lattice has no finite moves. All of their openness is supplied by ends, so Proposition 2 never applies
to them (see ticket B for what happens instead). A native parity plane needs at least two distinctions
per site, as the gauge and Tseitin laws have: one per lattice direction.

## 5. Native in every variable, still a shortcut

**Proposition 5.** Take three types x, y, z on Z^2:
- Ledrappier's law on x: x(t) + x(t + e_1) + x(t + e_2) = 0;
- z free;
- y = x + z at every site.

Then for every k:
1. the six variables y, z at the sites 0, 2^k e_1 and 2^k e_2 form a knot;
2. every variable is flipped by the finite move that changes y_p and z_p together.

Hence every knot of this law is native at every allowed state under the source-aware reading, yet
δ(y_0, y_{2^k e_1}) <= 5 for every k.

*Proof.*
1. **Ledrappier's implied checks.** They are the ideal I = (1 + x_1 + x_2) of R: the allowed states are
   the annihilator of I, and by Pontryagin duality the annihilator of the allowed states is I again.
   - I has no one-term element: a monomial is a unit, and 1 + x_1 + x_2 is not.
   - I has no two-term element. Under the map R → F_2(x), x_2 ↦ 1 + x, whose kernel is I, the element
     1 + x_1^a x_2^b goes to 1 + x^a (1 + x)^b. That is nonzero unless a = b = 0, since x and 1 + x are
     distinct primes.
2. **The knot.**
   - An implied check with coefficients (α, β, γ) on (x, y, z) must have γ = β, because z is free, and
     α + β ∈ I.
   - On the six variables α = 0, so β is an element of I supported on {0, 2^k e_1, 2^k e_2}.
   - The only nonzero one is the Frobenius power (1 + x_1 + x_2)^(2^k) = 1 + x_1^(2^k) + x_2^(2^k).
   - So the six variables carry exactly one implied check, and it uses all of them: they are a knot.
3. **The moves.** The move flipping y_p and z_p together leaves x fixed and keeps y = x + z. ∎

**Reading.** Per-variable nativity (adopted 2026-10-20) checks where each distinction's openness comes
from. It does not check where a knot's *binding* comes from. Here the binding passes through the
witness field x, which is frozen: its openness is supplied entirely by ends. The law has ends:
closure(F) = {(0, z, z)} ≠ X. Theorem 1 then needs splitting, and this law does not split.

This is recorded as a decision for the owner in the epic's correction request.

## 6. Conservative extensions never stretch

**Proposition 6.** Let V ⊆ V′ and let X′ be a law on V′ with X′_V = X. Then:
- X′_S = X_S for every S ⊆ V, so every knot of X inside V is a knot of X′, and δ_{X′} <= δ_X on V;
- in a chain of conservative extensions, the bond distance between old distinctions is non-increasing;
- for the inverse limit it equals the limit of the chain's values, since every knot of the limit is
  finite and appears at a finite stage (compactness; HOLES-AT-INFINITY B).

*Proof.* Projections compose. ∎

So a system that grows by adding constraints and variables while keeping its old allowed states never
moves two existing distinctions apart. Space can grow only by adding new distinctions at larger bond
distance; it never stretches between existing ones.

## Checks

`check.py` runs nine checks, each with a control that is rejected (`result.json`):
- the dependency digests;
- splitting on random far-apart sets of gauge and Tseitin boxes (300 pairs each);
- exhaustive chaining of all knots of size <= 8 through a central edge of 6×6 gauge and Tseitin boxes;
- the gauge plane: knot search against an independent shortest-cycle flow on a 7×7 box (no
  disagreements), and the bounds on about 400 pairs of a 41×41 box, with offsets observed only in
  {1, 3, 5};
- the Tseitin path cut on 80 interior pairs of a 7×7×7 box;
- the thread windows (m = 5, every pair checked);
- injectivity for 39 random one-type checks;
- the product law for k = 1, 2, 3 and the identity for k = 1..6;
- six conservative refinements.

## Nonclaims

- Nothing here selects a substrate: these laws are written on a declared lattice. Ticket C asks what
  happens with nothing drawn.
- Bond distance stays the program's extended bond distance: it carries no coordinates, no embedding,
  and no metric beyond itself.
