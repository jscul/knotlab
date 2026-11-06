# Signed patterns of patterns: signed laws survive native coarse-graining

Status: Proved

Ticket `INTERFERENCE-20261029-001B`, 2026-10-29.

## Standard statement

- **Signed laws.** A *signed three-bit law* is a function T : {0,1}³ → {−1, 0, 1} whose support K is one of the 34 *knots*
  (relations in which every pair of coordinates is unconstrained, other than the whole cube). Sign patterns count up to a global
  sign.
- **Native gadgets.** A *native gadget* joins m copies of T, each in any coordinate order (a *placement*). Every hidden variable
  lies in exactly two distinct copies, three *legs* lie in one copy each, the copies are connected, and no copy repeats a
  variable.
- **Leg function.** The gadget's leg function is L(a, b, c) = Σ_hidden Π_copies T(·), a sum of products of the copies' values.
- **Rebuilt and exact.** The gadget *rebuilds* T when the support of L is K in some coordinate order. It is an *exact signed fixed
  point* when L is a nonzero multiple of T in some coordinate order. With all weights +1 the leg function counts hidden
  completions, the counted setting of `GEOMETRY-LAW-20261029-001A`.

**Results.**
- **Theorem 1 (towers).** Relabel the legs of an exact signed fixed point G so that G(T) = λT. Then substituting G for every copy
  of any network of copies of T multiplies its signed sum by λ per copy. The level-k tower has leg function
  λ^((m^k − 1)/(m − 1)) T, so its support is the knot at every level.
- **Lemma 2 (wires by cancellation).** Two copies sharing two hidden variables contract to a 2×2 matrix M = F_u F_wᵀ (F a
  flattening of T). M is a nonzero multiple of the identity exactly when a flattening of T has orthogonal rows of equal norm.
  With weights +1 this happens only for parity. With signs it happens for many knots.
- **Theorem 3 (census, exhaustive over native gadgets of three and five copies, every shape, placement and sign pattern).**
  - Without signs only the two parity classes are rebuilt, as `GEOMETRY-LAW-20261029-001A` proved.
  - With signs, 14 of the 16 classes are rebuilt and 12 have exact signed fixed points.
  - The native triangle (three copies, each sharing one hidden variable with each other copy) is exact for 10 classes, so the
    Sierpinski gasket carries each of them at every level.
  - The two symmetric three-excluded classes ("no lone one" and "no lone zero", the Fibonacci fusion rules) are never rebuilt.
  - The symmetric atoms (or, nand) are rebuilt but never exact.
- **Proposition 4 (not-all-equal on the triangle).** Signed not-all-equal with weight −1 on (1, 1, 0) and +1 on its other five
  tuples is reproduced exactly by the native triangle with factor 3, while the unsigned triangle allows every tuple. Every signed
  not-all-equal-type law with positive Cayley hyperdeterminant (real tensor rank 2) is exact on the triangle.
- **Proposition 5 (shared boundary).** Under the triangular-lattice substitution, which cuts every face into four with midpoints
  shared between neighbouring faces and is not finitely ramified, consider signed laws on the seven cyclically symmetric knots
  with signs constant on rotation orbits (22 laws). The per-face factor Z(subdivided)/Z agrees on the tetrahedron, octahedron and
  icosahedron only for parity.

## Nearest known result

- **In the repository.**
  - `GEOMETRY-LAW-20261029-001A`: with counts (nonnegative), only parity is rebuilt by native gadgets of its own copies, and towers
    of any other law reach the free relation within three levels.
  - `EXACT-TOWERS-20261029-001A`/`B`: exact counted fixed points of hub gadgets (parity; twisted not-all-equal from four copies;
    three-excluded from five; not-all-equal at seven, Fano), and the finitely ramified towers they build. The parity triangle
    builds the Sierpinski gasket.
  - `SHARED-SUBDIVISION-20261029-001`, closed while this ticket ran: with counts, on the triangular lattice with shared
    subdivision, only affine (parity-type) rules reproduce themselves with a knot, and not-all-equal never does. Proposition 5 is
    the signed analogue on closed spheres, computed independently. It does not consume that epic's evidence.
- **Outside.**
  - Exact real-space renormalization on hierarchical and fractal lattices, with real or complex weights (Gefen, Mandelbrot and
    Aharony 1980; Derrida, De Seze and Itzykson 1983, for complex fixed points and Julia sets).
  - Holographic gadgets and signed or complex signatures in counting problems (Valiant 2008; Cai and Lu).
  - These study given interactions or decide counting complexity. They do not classify which three-bit relations are reproduced,
    with signs, by native gadgets of their own copies.
- **Classification.** Theorem 1 and Lemma 2 are elementary. Theorem 3 and Propositions 4 and 5: no overlap found (candidate local
  delta).

## Theorem 1 (towers)

The leg function is multilinear in the copies, so G(cT) = c^m G(T) for m copies. Relabelling legs gives another gadget. If
G(T) = λT with T placed in order q, compose the legs with q⁻¹ to obtain G' with G'(T) = λT.

In any network of copies of T, its signed sum is multilinear in the copies. Replacing every copy by G' (with that copy's
placement) replaces each copy's tensor by λ times itself, so the sum is multiplied by λ per copy.

The level-k tower is G' applied to the level-(k − 1) tower. Its leg function is therefore λ^(1 + m + … + m^(k−1)) T, a nonzero
multiple of T. Its support, the set of states allowed under the interference reading, is the knot at every level.

The check iterates every exact fixed point found, up to three placements per shape and sign pattern, to level 4, and confirms
the leg function stays a nonzero multiple of T. The geometry of the tower depends only on the gadget's shape. The triangle's
tower is the Sierpinski gasket (`EXACT-TOWERS-20261029-001B`).

## Lemma 2 (wires by cancellation)

Two copies u, w that share two hidden variables, with free slots of coordinates i and j, contract to
M(a, c) = Σ_{g,h} T_u(a, g, h) T_w(c, g, h), where T_u and T_w are the placed copies. This is M = F F'ᵀ for the 2×4 flattenings
of the two copies at their free coordinates, with columns matched by the shared variables.

- **When the placements agree.** With F = F', M is a multiple of the identity exactly when the rows of F are orthogonal with
  equal norm.
- **Nonnegative weights.** Orthogonal rows have disjoint supports. For a knot, the two slices of a coordinate cover all four
  pairs, so disjoint slices make K the graph of a function f(b, c) whose every pair is free, which forces f = b ⊕ c or its
  complement: parity.
- **What a wire does.** The two copies act as an identity wire. Any gadget containing one reduces to a smaller gadget, so a single
  copy with a wire attached is an exact fixed point.

The check finds an unsigned wire only for parity, and counts for each class the signed laws with a wire. Every exact fixed point
of the three-copy shape with a doubled edge contracts that edge to an invertible 2×2 matrix, so the gadget is one copy with a
linear map on one leg.
- In 19,840 of the 19,872 such cases (every class, sign pattern and placement found exact) the matrix is a multiple of a signed
  permutation, a signed wire.
- In the other 32, all in the twisted three-excluded classes, it is a shear such as [[−2, 0], [2, 2]], which the law absorbs up
  to a change of coordinate order.

A first statement that the matrix is always a signed permutation was refuted by the check and corrected here.

## Theorem 3 (census)

The check enumerates:
- every native gadget shape with three copies (2 shapes) and five copies (9 shapes);
- every placement of every copy (6^m);
- every class representative;
- every sign pattern up to global sign.

For each case it computes the leg function by tensor contraction and compares it with the six placements of the law, for support
and for proportionality. Forty random gadgets are recomputed by brute-force summation as a control.

| Class (excluded tuples) | Sign patterns | Rebuilt, 3 copies | Exact, 3 copies (triangle) | Factors, 3 | Rebuilt, 5 copies | Exact, 5 copies | Factors, 5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| atom excl 111 | 64 | 48 | 0 (0) | — | 60 | 0 | — |
| atom excl 110 | 64 | 62 | 28 (0) | 1, 3 | 62 | 46 | 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 20 |
| two excluded at distance two excl 101 110 | 32 | 30 | 24 (20) | 1, 3 | 30 | 24 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14 |
| two excluded at distance two excl 100 111 | 32 | 30 | 24 (16) | 1, 3 | 30 | 26 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14 |
| atom excl 100 | 64 | 62 | 28 (0) | 1, 3 | 62 | 46 | 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 20 |
| three excluded excl 011 101 110 | 16 | 0 | 0 (0) | — | 0 | 0 | — |
| not-all-equal type excl 011 100 | 32 | 30 | 30 (28) | 1, 2, 3 | 30 | 30 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13 |
| three excluded excl 010 100 111 | 16 | 12 | 6 (4) | 2 | 14 | 14 | 1, 2, 4, 5, 6 |
| two excluded at distance two excl 010 100 | 32 | 30 | 24 (20) | 1, 3 | 30 | 24 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14 |
| parity excl 001 010 100 111 | 8 | 8 | 8 (7) | 2 | 8 | 8 | 4 |
| three excluded excl 001 010 100 | 16 | 0 | 0 (0) | — | 0 | 0 | — |
| not-all-equal type excl 000 111 | 32 | 30 | 30 (30) | 1, 3 | 30 | 30 | 1, 3, 5, 7, 9, 13 |
| atom excl 000 | 64 | 48 | 0 (0) | — | 60 | 0 | — |
| two excluded at distance two excl 000 110 | 32 | 30 | 24 (16) | 1, 3 | 30 | 26 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14 |
| three excluded excl 000 101 110 | 16 | 12 | 6 (4) | 2 | 14 | 14 | 1, 2, 4, 5, 6 |
| parity excl 000 011 101 110 | 8 | 8 | 8 (7) | 2 | 8 | 8 | 4 |

Each entry counts sign patterns up to global sign. "Rebuilt" means some gadget of that size has the knot (in some coordinate
order) as its support. "Exact" means some gadget gives a nonzero multiple of the law. "Triangle" counts the patterns exact on the
native triangle. Factors are |λ| over all exact gadgets.

- **Unsigned (every weight +1).** Only the two parity classes are rebuilt, at three and at five copies, reproducing
  `GEOMETRY-LAW-20261029-001A`.
- **Signed.** 14 classes are rebuilt and 12 have exact signed fixed points. 10 are exact on the native triangle: the four
  two-excluded-at-distance-two classes, both not-all-equal classes, the two twisted three-excluded classes and both parity
  classes.
- **Never rebuilt** within five copies: "no lone one" ({001, 010, 100} excluded) and "no lone zero" ({011, 101, 110} excluded),
  the two Fibonacci fusion rules.
- **Rebuilt but never exact:** the symmetric atoms, "or" ({000} excluded) and "nand" ({111} excluded).
- **The asymmetric atoms** ({100} or {110} excluded) are exact, but not on the triangle.

## Proposition 4 (not-all-equal on the triangle)

Let T be not-all-equal with T(1,1,0) = −1 and T = +1 on its other five tuples. Place the triangle's three copies in coordinate
orders (0,1,2), (0,2,1) and (2,0,1), the first slot being the leg and the other two shared with the neighbours. The leg function
is then 3T: it is 0 on (0,0,0) and (1,1,1), +3 on five tuples and −3 on (1,1,0). This was recomputed by brute force.

Without the sign, the same triangle allows every tuple, because positive counts cannot cancel. So `GEOMETRY-LAW-20261029-001A`'s
not-all-equal towers go free, while the signed tower is the Sierpinski gasket with signed not-all-equal at every corner, at
every level.

The check tabulates every signed law of the two not-all-equal classes (32 sign patterns each) against the sign of Cayley's
hyperdeterminant:

| Class | Hyperdeterminant > 0 | exact on the triangle | Hyperdeterminant < 0 | exact on the triangle |
| --- | --- | --- | --- | --- |
| not-all-equal {000, 111} | 24 | 24 | 8 | 6 |
| twisted not-all-equal {011, 100} | 24 | 24 | 8 | 4 |

So a positive hyperdeterminant (real tensor rank 2, the rank of the equality fan-out) is sufficient for exactness on the
triangle, but not necessary.

## Proposition 5 (shared boundary)

On the boundaries of the tetrahedron, octahedron and icosahedron, put the law on every face in its cyclic orientation order.
Then cut every face into four, with a new variable at the midpoint of every edge shared by its two faces. The check contracts
both networks exactly and compares per-face factors.

| Knot (excluded tuples) | Orbit signs | Tetrahedron | Octahedron | Icosahedron | Exact |
| --- | --- | --- | --- | --- | --- |
| parity (001 010 100 111) | (1, 1) | 1.0000 | 1.0000 | 1.0000 | yes |
| parity (001 010 100 111) | (1, -1) | 1.0000 | 1.0000 | 1.0000 | yes |
| parity (000 011 101 110) | (1, 1) | 1.0000 | 1.0000 | 1.0000 | yes |
| parity (000 011 101 110) | (1, -1) | 1.0000 | 1.0000 | 1.0000 | yes |
| three excluded (011 101 110) | (1, 1, 1) | 1.6456 | 1.6468 | 1.6511 | no |
| three excluded (011 101 110) | (1, 1, -1) | 1.6456 | 1.6468 | 1.6511 | no |
| three excluded (011 101 110) | (1, -1, 1) | -1.1892 | 1.6468 | 1.4006 | no |
| three excluded (011 101 110) | (1, -1, -1) | -1.1892 | 1.6468 | 1.4006 | no |
| three excluded (001 010 100) | (1, 1, 1) | 1.6456 | 1.6468 | 1.6511 | no |
| three excluded (001 010 100) | (1, 1, -1) | -1.1892 | 1.6468 | 1.4006 | no |
| three excluded (001 010 100) | (1, -1, 1) | -1.1892 | 1.6468 | 1.4006 | no |
| three excluded (001 010 100) | (1, -1, -1) | 1.6456 | 1.6468 | 1.6511 | no |
| not-all-equal type (000 111) | (1, 1) | 1.3161 | 1.6818 | 1.5121 | no |
| not-all-equal type (000 111) | (1, -1) | 1.3161 | 1.6818 | 1.5121 | no |
| atom (111) | (1, 1, 1) | 2.3561 | 2.3523 | 2.3512 | no |
| atom (111) | (1, 1, -1) | 2.3561 | 2.3523 | 2.3512 | no |
| atom (111) | (1, -1, 1) | 1.0000 | 937.4054 | — | no |
| atom (111) | (1, -1, -1) | 1.0000 | 937.4054 | — | no |
| atom (000) | (1, 1, 1) | 2.3561 | 2.3523 | 2.3512 | no |
| atom (000) | (1, 1, -1) | 1.0000 | 937.4054 | — | no |
| atom (000) | (1, -1, 1) | 1.0000 | 937.4054 | — | no |
| atom (000) | (1, -1, -1) | 2.3561 | 2.3523 | 2.3512 | no |

The entries are signed per-face factors (Z(subdivided)/Z)^(1/F). A dash marks Z = 0. Only the parity laws give the same factor on all three surfaces.

So in this first discriminator, interference does not make any non-linear law self-reproducing under a substitution that is not
finitely ramified. Signs revive non-parity laws in finitely ramified towers, but not, so far, in two-dimensional ones.

A sign that is not constant on rotation orbits but is a pairwise gauge of parity also keeps parity exact: (−1)^(x₁x₂) on the even
tuples, that is, −1 on (1,1,0). It was first chosen as a control and did not fire, so it is recorded here as an observation. The
control is now a change of magnitude, parity with weight 2 on (0,0,0), which gives per-face factors 8, 7.988 and 8 and is
rejected.

## Reading

- **Counted versus signed.** Under counting, coarse-graining by native gadgets washes out every knot except parity within three
  levels (`GEOMETRY-LAW-20261029-001A`). With signs, most knot classes reproduce themselves exactly from three copies, because
  cancellation can exclude exactly the tuples that counting cannot.
- **Signs supply what hubs supplied.** `EXACT-TOWERS-20261029-001` needed hubs, and seven copies for not-all-equal (the Fano
  plane). With signs, three native copies suffice, and not-all-equal is a disguised hub: one pairwise sign gives it real tensor
  rank 2 (`INTERFERENCE-20261029-001A`), the rank of the equality fan-out.
- **What did not change.** The two Fibonacci fusion knots are not rebuilt with ±1 weights. Their natural weights involve the
  golden ratio (`INTERFERENCE-20261029-001A`), which this census does not allow. The shared-boundary substitution stays
  parity-only in its first test. So interference changes which laws survive in hierarchical spaces, but it has not yet built
  two-dimensional space.

## Nonclaims

- Weights are restricted to ±1 on the support. Other real or complex weights, such as golden-ratio weights for the Fibonacci
  knots, are not classified.
- Native gadgets of seven or more copies, and hub gadgets with signs, are not enumerated.
- The shared-boundary test covers three spheres and laws constant on rotation orbits only. It is a first discriminator, not a
  classification.
