# The exact two-dimensional laws: Newman–Moore, Baxter–Wu, and line collapse

Status: Proved

Ticket `SHARED-SUBDIVISION-20261029-001B`, 2026-10-29.

## Standard statement

**Setting.**
- **Coordinates.** Sites of the triangular lattice are (i, j). The triangles are up(i, j) = ((i, j), (i + 1, j), (i, j + 1)) and
  down(i, j) = ((i + 1, j), (i, j + 1), (i + 1, j + 1)), with their vertices in that order.
- **Rows and classes.** Row j is x_j = (x(i, j))_i, and S is the shift, (Sx)(i) = x(i + 1). The colour class of a site is
  (i − j) mod 3. Every triangle has one vertex in each class.
- **Exactness.** Shared subdivision by k and exactness are as in `SHARED-SUBDIVISION-20261029-001A`: the coarse sites of the torus of
  side L = k·m are (k·i, k·j).
- **Parity b.** b = 0 allows the even tuples, b = 1 the odd ones.

**Theorem 1 (Newman–Moore: parity b on up triangles).**
- **(a) Solutions.** The solutions on the torus of side L correspond to the rows x₀ with Φ^L(x₀) = x₀, where
  Φ(x) = (1 + S)x + b·1. Let N(L) be their number.
- **(b) Scale 2.** For L = 2m, restriction to the coarse sites maps the solutions onto the solutions of the m-torus. Every coarse
  solution has exactly N(m) extensions, and N(2m) = N(m)².
- **(c) Scale 3.** Not exact on the tori of side 9 and 12.
- **(d) Rigidity.** On the plane, two solutions that differ in finitely many sites are equal.

**Theorem 2 (Baxter–Wu: parity b on all triangles).**
- **(a) Solutions.** Two triangles sharing an edge force their opposite vertices to be equal. So a solution on the plane is constant
  on each colour class, with class values v₀, v₁, v₂ satisfying v₀ + v₁ + v₂ = b. On the torus of side L the solutions are these
  four patterns if 3 divides L, and the constant b otherwise.
- **(b) Scale 2.** Exact, with one extension per coarse solution.
- **(c) Scale 3.** Not exact.
- **(d) Rigidity.** Two distinct solutions on the plane differ on a whole colour class.

**Theorem 3 (line collapse: twisted not-all-equal on all triangles).**
- The six exact placement pairs of ticket A form one orbit under the rotations and reflections of the lattice and complementation.
  The *representative* excludes {011, 100} on up and on down triangles.
- **(a) Walls persist.** A *wall* is a pair of horizontal neighbours with different values. If row j has a wall at (i, i + 1), row
  j + 1 has the same values at i and i + 1.
- **(b) Solutions.** On every torus the solutions are exactly the configurations constant along columns: 2^L of them.
- **(c) Exactness.** Exact at every scale k dividing L, with 2^(L − L/k) extensions per coarse solution.
- **(d) No knot.** Two vertices of every triangle lie on one column. So the projection of the solution set onto a triangle contains
  an equality and is not a knot.
- **(e) Not rigid.** On the plane, the half-line x(0, j) = 1 for j ≥ j₀ (and 0 elsewhere) is a solution for every j₀. The half-lines
  from j₀ and j₀ + 1 differ in one site.

The other five pairs follow by symmetry, along another lattice direction.

**Proposition 4 (the three-excluded rules; computation).**
- The twelve exact three-excluded pairs form one orbit.
- On the tori of side 2 to 11, each has exactly the solutions of Baxter–Wu for one parity.
- The extra tuple, allowed by the rule but not by that parity, extends to every patch of radius 1, 2 and 3 around a triangle. So the
  coincidence is not forced locally, and a proof for every torus is open.

**Corollary 5 (what exactness keeps).** On every torus of side 2 to 11, each exact rule of ticket A has the solution set of
Newman–Moore, Baxter–Wu or a line-constant family. Its projection onto the triangle up(0, 0) is a knot only in the two parity
families, and only where their solution set has more than one element:
- Newman–Moore: on the tori of side 3, 6, 7 and 9 (among 3 to 11);
- Baxter–Wu and the three-excluded rules: on the tori of side 3, 6 and 9.

It is never a knot in the line-constant family.

## Nearest known result

- **Newman–Moore.** Parity on up triangles is the triangular plaquette model of Newman and Moore (1999).
  - Its zero-temperature configurations are rows of a linear cellular automaton, Pascal's triangle mod 2.
  - Their self-similarity under rescaling by 2 is classical (Willson; Allouche, von Haeseler, Peitgen and Skordev).
  - The dependence of its degeneracy on the torus size has been studied with cellular automata (Sfairopoulos et al., arXiv
    2301.02826).
- **Baxter–Wu.** Parity on all triangles has the four Baxter–Wu ground states on tori whose side is divisible by 3, and only the
  ferromagnetic one otherwise (Baxter and Wu 1973).
- **Line collapse.** Elementary.
- **Classification.** Known with delta. The families are classical or elementary. The delta is that, within the knot census, they are
  the only exact rules, and that exactness keeps a knot only through parity.

## Proof of Theorem 1

**(a) Solutions.** The equation of up(i, j) reads x(i, j + 1) = x(i, j) + x(i + 1, j) + b, so x_{j+1} = Φ(x_j). On the torus of side
L the rows are indexed mod L. The solutions are therefore the rows x₀ with Φ^L(x₀) = x₀, extended by x_j = Φ^j(x₀). ∎

**(b) Scale 2.**
- **Two steps.** Over the two-element field (1 + S)² = 1 + S², and (1 + S)·1 = 0, so Φ²(x) = (1 + S²)x + b·1.
- **Two independent coarse rows.** Split a row into its values e on even sites and o on odd sites. The double shift S² acts on each
  as the shift of a row of length m. So Φ²(e, o) = (Φ_c(e), Φ_c(o)), where Φ_c(y) = (1 + S_c)y + b·1 is the coarse automaton.
- **Periodicity.** Φ^(2m)(x₀) = x₀ exactly when Φ_c^m(e₀) = e₀ and Φ_c^m(o₀) = o₀.
- **The restriction.** The coarse sites (2i, 2j) carry the even sites of the even rows, namely Φ_c^j(e₀). So restriction sends the
  fine solution with row (e₀, o₀) to the coarse solution with row e₀, by (a) on the m-torus.
- **The count.** Every coarse solution arises, from each of the N(m) choices of o₀. Hence N(2m) = N(m)². ∎

**(c) Scale 3.** (1 + S)³ = 1 + S + S² + S³: three steps mix the sites of the coarse sublattice with the others. Check 1 shows that
the restriction is not onto the coarse solutions on the tori of side 9 and 12. ∎

**(d) Rigidity.**
- Let δ be the difference of two solutions, with finite nonempty support. It satisfies δ_{j+1} = (1 + S)δ_j.
- Let j be the highest row where δ is nonzero. Then (1 + S)δ_j = 0, so δ_j(i) = δ_j(i + 1) for every i.
- A row of finite support that is constant along the line is zero. This contradicts the choice of j. ∎

## Proof of Theorem 2

**(a) Solutions.**
- **Opposite vertices.** If (a, b′, c) and (b′, c, d) are triangles sharing the edge b′c, then a + b′ + c = b = b′ + c + d, so
  a = d.
- **Which pairs.** The opposite pairs of the lattice differ by (1, 1), (2, −1) or (1, −2). These vectors generate the sublattice
  i − j ≡ 0 (mod 3), which has index 3.
- **On the plane.** A solution is constant on each colour class. The three class values satisfy one triangle's equation, so they sum
  to b.
- **On the torus of side L.** If 3 divides L, the classes are well defined and the same four patterns are the solutions. Otherwise
  the vectors generate the whole torus, so the solution is constant, equal to b. ∎

**(b) Scale 2.**
- The fine site (2i, 2j) has class 2(i − j) ≡ −(i − j) (mod 3). So restriction sends the pattern (v₀, v₁, v₂) to the coarse pattern
  (v₀, v₂, v₁), which is again a solution.
- This is a bijection when 3 divides m.
- When 3 does not divide m, it does not divide 2m either, and both sides are the constant b. ∎

**(c) Scale 3.**
- Every site (3i, 3j) lies in class 0, so the restriction of a pattern is the constant v₀.
- Some pattern has v₀ = 1 − b, so the constant 1 − b appears, and it is never a coarse solution.
- When 3 divides m, the three non-constant coarse patterns are also missed (check 2: tori of side 9 and 12). ∎

**(d) Rigidity.** Immediate from (a): two distinct patterns differ on a class. ∎

## Proof of Theorem 3

**Notation.** Write r for row j and s for row j + 1. For the representative:
- the triangle up(i, j) forbids r_{i+1} = s_i ≠ r_i;
- the triangle down(i, j) forbids s_i = s_{i+1} ≠ r_{i+1}.

**(a) Walls persist.** Let r_i ≠ r_{i+1}.
- If s_i = r_{i+1}, up(i, j) is violated. So s_i = r_i.
- Then s_i ≠ r_{i+1}. If also s_{i+1} = s_i, down(i, j) is violated. So s_{i+1} ≠ s_i, that is, s_{i+1} = r_{i+1}.

Check 3 confirms this exhaustively over the 16 local patterns. ∎

**(b) Solutions on the torus.**
- **Wall sets are constant.** By (a) the set of wall positions can only grow from row to row. Since rows repeat with period L, it is
  the same in every row.
- **A row with a wall.** Take a maximal run of r of constant value v between two walls. The next row agrees with r at the run's ends,
  by (a). It has no wall inside the run, since the wall sets are equal. So it is constant v on the run.
- **A constant row.** If r is constant v, then s has no wall, so s is constant w. Forbidding s_i = s_{i+1} ≠ r_{i+1} gives w = v.
- **So the column-constant configurations are all.** In every case s = r, so every solution is constant along columns.
- **And they are solutions.** A column-constant configuration reads (a, c, a) on every up triangle and (a, c, c) on every down
  triangle. Neither is excluded.
- Check 3 certifies the 2^L solutions for L = 2 to 12 by matching counts. ∎

**(c) Exactness.** A coarse solution is a column-constant configuration of the m-torus. It is the restriction of exactly those fine
column-constant configurations whose columns k·i carry the coarse values. The other L − L/k columns are free, so each coarse solution
has 2^(L − L/k) extensions. ∎

**(d) No knot.**
- **Every triangle has two vertices on one column.** up(i, j) has (i, j) and (i, j + 1), and down(i, j) has (i + 1, j) and
  (i + 1, j + 1).
- **So the projection contains an equality.** Forgetting the third vertex leaves an equality, which is constrained. That fails K2. ∎

**(e) Not rigid.** The half-line satisfies every triangle (checked by hand, and in a 24 × 24 box by check 3). The half-lines from j₀
and j₀ + 1 differ only at (0, j₀). ∎

**The other pairs.** The orbit of the representative contains the other five pairs (check 3). Rotations and reflections preserve the
sublattice of coarse sites and carry the subdivision to itself. Complementation preserves solutions. So (a) to (e) hold for each of
them, along the image direction. ∎

## Proposition 4 and Corollary 5 (computation)

- **Certification.** Each family's solution set is certified without enumeration. Every configuration of the predicted set satisfies
  every triangle, and the transfer-matrix count of solutions equals the size of the predicted set.
- **Proposition 4.** The three-excluded relation contains the tuples of the matching parity, so every Baxter–Wu solution of that
  parity solves it. On the tori of side 2 to 11 the counts are equal (check 4).
- **The extra tuple.** For the representative, it extends to the patches of radius 1, 2 and 3 around the triangle up(0, 0)
  (exhaustive search).
- **Corollary 5.** Every exact rule of ticket A (22 at scale 2, 6 at scale 3) is certified to be in one family on every torus of
  side 2 to 11. Its projection onto up(0, 0) is tested against K1–K3 on the tori of side 3 to 11 (check 5).

## Reading

- **What exactness keeps.** On a genuinely two-dimensional subdivision, a law reproduces itself exactly only in two ways:
  - it is parity, or behaves exactly like parity on tori: Newman–Moore, Baxter–Wu, and the three-excluded rules;
  - or it collapses into pairwise equality along lines: twisted not-all-equal.

  No other knot does, and not-all-equal never does.
- **The two/three boundary.** Exactness on genuine two-dimensional space leaves either linear three-place structure or pairwise
  structure. Every other knot's three-place structure is lost.
- **Rigidity and the source-aware reading.**
  - The parity families have no finite change between solutions on the plane. Under the canonical source-aware reading, no knot is
    native at their solutions.
  - Line collapse is not rigid, but no triangle of it carries a knot.
- **Arithmetic, not geometry.** Newman–Moore and Baxter–Wu are exact at scale 2 and not at scale 3.
  - For Newman–Moore the reason is the two-element field: (1 + S)² = 1 + S².
  - For Baxter–Wu the reason is that 2 ≡ −1 (mod 3) permutes the colour classes.
  - Line collapse is exact at every scale.

## Checks

`check.py` (numpy) on `shared_lib.py`, with `result.json`:
- **0.** The dependency artifacts are bound by hash.
- **1.** Newman–Moore: N(L) for L = 1 to 12 (the automaton and the transfer matrix agree); N(2m) = N(m)²; scale 2 onto with N(m)
  extensions for even L up to 12; scale 3 not exact (L = 9, 12); a nonzero finitely supported row is never fixed by 1 + S.
- **2.** Baxter–Wu: the opposite-vertex lemma; certified solution sets for L = 2 to 12; exact at scale 2 (L = 6, 8, 10, 12) with one
  extension, not at scale 3 (L = 9, 12).
- **3.** Line collapse:
  - the six pairs are one orbit;
  - walls persist;
  - the certified solution sets are the 2^L line-constant configurations for L = 2 to 12;
  - exact at scales 2 and 3 with 2^(L − L/k) extensions;
  - no triangle projection is a knot (L = 3 to 12);
  - half-lines in a box.
- **4.** The three-excluded rules: one orbit; certified Baxter–Wu solution sets for L = 2 to 11; the extra tuple extends to patches of
  radius 1 to 3.
- **5.** The family and knot test of every exact rule of ticket A.
- **6.** Controls:
  - the wall lemma fails for not-all-equal;
  - the half-line violates parity on all triangles;
  - Newman–Moore at scale 3 on the 12-torus is not exact.

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Theorem 1 | The plaquette model as a linear cellular automaton; (1 + S)² = 1 + S² | Classical in substance; the exact count N(2m) = N(m)² written here |
| Theorem 2 | Opposite-vertex equality; colour classes | Classical (Baxter–Wu ground states) |
| Theorem 3 | Wall persistence | Elementary; not found as such |
| Proposition 4, Corollary 5 | Certified computation on tori up to side 11 | Candidate local delta |

## What this does not show

- **Proposition 4 on every torus.** It is computed up to side 11, and no local lemma of radius 3 or less explains it.
- **Other substitutions.** Other subdivisions, lattices or face patterns are not covered.
- **Nativeness in the line-collapse family.** Whether a knot is native at some of its non-periodic solutions on the plane is open.
  The family is not rigid there.
