# The Fano plane is the only uniform law that contradicts itself

Status: Proved by hand, with McCuaig's theorem as a cited input. The finite claims are checked by computation (`check.py`).

Ticket `UNIFORM-FANO-20261107-001A`, 2026-11-07.

## Standard statement

**Setting.** A cubic triple system H has n points and n lines, every line with three distinct points and every point on three lines.
Its incidence graph B is cubic and bipartite. A Cayley law (`UNIFORM-SPHERES-20261107-001A`) is the system with points G and lines
L(g) = (g, gx, gxy), for a finite group G = ⟨x, y⟩. Its uniform signs put the same pattern σ = (σ0, σ1, σ2) on the positions g, gx,
gxy of every line.

**Theorem.**
1. **Non-constant signs are harmless.** If σ is not constant, the all-zero assignment satisfies every line of every Cayley law.
2. **Brace lemma.** If a group of automorphisms of H is transitive on its points and on its lines, B has no nontrivial tight cut: it is
   a brace.
3. **The classification.** Such an H is not 2-colourable only if it is the Fano plane.

**Corollary.** Among Cayley laws with uniform signs, and more generally among point- and line-transitive laws with constant signs, the
Fano plane (Z7, lines {g, g+1, g+3}) is the only one whose knot is unsatisfiable. With `UNIFORM-SPHERES-20261107-001A`, every other
contradiction of the knot needs non-uniformity:
- curvature defects, which carry the count (the knot sphere);
- or a non-transitive gluing of Fano atoms (the three-fold spaces of `THREEFOLD-SPACES-20261030-001`).

## Nearest known results

- **The dictionary.** `THREEFOLD-SPACES-20261030-001A` Theorem 1 (Seymour 1974; Bassett–Maybee–Quirk): H is not 2-colourable ⟺ its
  incidence matrix is sign-nonsingular ⟺ the digraph D(H, M) has no even directed cycle, for any perfect matching M.
- **McCuaig** (*Even dicycles*, J. Graph Theory 35, 2000): F7 = D(Heawood, M) is the only strongly 2-connected digraph with no even
  dicycle. It is already used in THREEFOLD-SPACES-20261030-001A's brace case.
- **Braces.** For a bipartite graph with a perfect matching M: B is a brace ⟺ D(B, M) is strongly 2-connected (Lovász–Plummer;
  Robertson–Seymour–Thomas, Annals 1999, 7.5). Tight cuts in bipartite matching-covered graphs: one shore has one more vertex of one
  colour, and its other-colour vertices have all their neighbours inside (Lucchesi, de Carvalho, Murty).
- **Classification.** Known-with-delta. McCuaig's theorem and the dictionary are classical. The brace lemma for point- and
  line-transitive systems, and the resulting list of uniform contradictions, are new as far as found. Folklore risk is moderate:
  symmetric bipartite graphs are often shown to be braces.

## Proofs

*Proof of 1.* Under the all-zero assignment, line L(g) sees the literals σ0, σ1, σ2, which are not all equal. ∎

*Proof of 2.*
- **A modular function.** Call a vertex set Z *closed* if every line of Z has all three of its points in Z. For closed Z put
  g(Z) = |points(Z)| − |lines(Z)|. Then:
  - the cut ∂Z has exactly 3g(Z) edges;
  - intersections and unions of closed sets are closed, and g is modular on them;
  - g(Z) ≥ 1 for closed Z ≠ ∅, V. A perfect matching sends the lines of Z to distinct points of Z, so g ≥ 0, and g = 0 would make ∂Z
    empty in a connected graph.
- **Tight shores.** A tight cut with points in the majority is ∂X for a closed X with g(X) = 1. A tight cut with lines in the majority is
  the same with the two colours swapped. It is nontrivial when both shores have at least 3 vertices.
- **A smallest shore.** Suppose a nontrivial tight cut exists, and let X be a nontrivial tight shore of the smallest size. Say points are
  its majority (the other case swaps colours). Since the complement of X is also a nontrivial tight shore, |X| ≤ n.
- **Translates share at most one point.** Take an automorphism h with hX ≠ X and X ∩ hX ≠ ∅.
  - X ∪ hX ≠ V, since otherwise |X| ≥ n with X and hX disjoint.
  - So g(X ∩ hX) + g(X ∪ hX) = 2 with both terms at least 1. Hence X ∩ hX is a tight shore smaller than X, so it is trivial: a single
    point.
  - Distinct translates therefore share at most one point, and no line, because a line of both would bring its three points.
- **Counting.** Each line lies in at most one translate. By transitivity on lines, and since X contains a line (|X| ≥ 3), each line
  lies in exactly one. With p points and p − 1 lines in X, and T translates:
  - T(p − 1) = n;
  - each point lies in the same number m of translates (transitivity on points), so Tp = nm.

  Hence m = p/(p − 1), so p = 2. But X then has two points and a line, whose three points must lie in X. Contradiction. ∎

*Proof of 3.*
- **The digraph is strongly 2-connected.** Let H be point- and line-transitive and not 2-colourable. By 2, B is a brace, so D(H, M) is
  strongly 2-connected for every perfect matching M.
- **It has no even dicycle.** By the dictionary, D(H, M) has no even dicycle.
- **McCuaig.** So D(H, M) = F7, and H is the Fano plane. ∎

*Proof of the corollary.* With constant signs the knot is a proper 2-colouring. Non-constant uniform signs are satisfied by 1. A Cayley
law is point- and line-transitive (left multiplication). ∎

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Non-constant uniform signs on 439 simple Cayley laws | the all-zero assignment satisfies every line |
| 2 | Brace lemma on the census (cyclic up to 30, abelian, dihedral, A4, S4, A5, S5, PSL(2,7), wallpaper quotients, random subgroups of S_5..S_7; orders 3–720) | every simple law has a strongly 2-connected digraph (a brace) |
| 3 | 2-colourability under equal signs | only Z7(1,2), the Fano plane, fails |
| 4 | The Fano plane | not 2-colourable, sign-nonsingular (\|det\| = per = 24), F7 has no even dicycle, no nontrivial tight cut |
| 5 | Controls | the 13-point Fano splice is not 2-colourable, has a tight cut, and the brace test says no on it; Z7 with {0,1,4} is 2-colourable; a law with a repeated point is caught |

## Reading

**Interpretation, not a theorem.**
- **One exception.** A law that treats every point and every line alike can contradict itself in exactly one way: by being the Fano
  plane. The Fano plane is the smallest three-fold space, a single handle (`THREEFOLD-SURFACES-20261030-001`).
- **Every other contradiction needs non-uniformity:**
  - curvature concentrated at defects, read by the count (the knot sphere);
  - or Fano atoms glued without symmetry (the three-fold spaces).
- **For question 9.** Uniform laws are coherent worlds with one exception. The knot's contradictions, its hardness included, live where a
  law distinguishes places.

## What this does not establish

- **Weaker uniformity.** Laws with one kind of point but no transitive symmetry are not covered: the brace lemma uses transitivity on
  points and on lines.
- **Non-uniform signs** on uniform laws are not covered. They include Kasteleyn signs, which make every uniform sphere fail.
- **Machine checking.** McCuaig's theorem is cited, not replayed.
