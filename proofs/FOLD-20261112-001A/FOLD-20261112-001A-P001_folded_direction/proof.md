# A direction the knot law does not lengthen

Status: Partial (to be set to Proved after the referee)

Ticket `FOLD-20261112-001A`, 2026-11-12. The statement is in `research/FOLD-20261112-001/preregistration.md` ("Theorem F").

## Standard statement

Let H be the 3-uniform hypergraph on Z² whose edges are {z, z+(0,1), z+(1,−1)} and {z, z+(0,2), z+(1,1)} for every z (base 16 of
`BOND-BALLS-20261111-001`), and consider its proper 2-colourings. For every k ≥ 3 the sets B_k = {(−k, k−2), (−k, k−1), (−k, k), 0}
and, for j = 0, 1, 2, F_k^j = {0, (0,1), (0,2), (k, j−k)} are minimal non-shattered sets (not shattered, every proper subset
shattered), and every pair of 0 with a vertex of B_k or F_k^j is shattered. So the vertices (−k, k−i) and (k, j−k) are at bond distance
at most 3 from 0 for every k ≥ 3, although they are k steps away.

## Words

In the guide's glossary: distinctions are the vertices, knots the edges, states the proper 2-colourings, free means shattered, a bond a
minimal constrained set, bond distance one less than the smallest bond's size, steps apart the graph distance on co-knotted pairs.

## Proof

**The sheared frame.** The map (x, y) ↦ (x, y + x) is an automorphism of Z², so it carries states to states. It sends the edges to
{z, z+(0,1), z+(1,0)} and {z, z+(0,2), z+(1,2)}, B_k to {(−k,0), (−k,1), (−k,2), 0} and F_k^j to {0, (0,1), (0,2), (k, j)}. Work
there. Write c_x(y) for the value at (x, y).

**Column rule.** Every edge is a pair in column x with a distinction in column x+1, so a colouring is proper exactly when, for all x
and y: c_x(y) = c_x(y+1) implies c_{x+1}(y) ≠ c_x(y), and c_x(y) = c_x(y+2) implies c_{x+1}(y+2) ≠ c_x(y) (check C1 confirms this on
every pair of columns of period 3 to 8).

**The travelling triple (forcing).** If c_x(0) = c_x(1) = c_x(2) = a, the rule gives c_{x+1}(0) ≠ a (from the pair at rows 0, 1),
c_{x+1}(1) ≠ a (rows 1, 2) and c_{x+1}(2) ≠ a (rows 0, 2): the triple at column x+1 is all ā. By induction the triple at column x+k is
all a when k is even and all ā when k is odd. Hence: on B_k, the pattern with the far triple all a and 0 ≠ (−1)^k-transformed a is
excluded, so B_k is not shattered; on F_k^j, the pattern with the near triple all a and (k, j) ≠ a(−1)^k is excluded. The forcing uses
both kinds of edge (the third step needs the pair at rows 0 and 2); without the second kind the set is shattered (check C5).

**Every proper part is shattered, for every k ≥ 3.** A state of the infinite pattern that repeats with period m in y is a bi-infinite
path in the transfer graph A_m on columns of period m (an edge c → d when the column rule holds between them), and every such path is a
state. A pattern on a part of B_k (columns −k and 0) is realized exactly when some walk of length k joins a column with an infinite past
to a column with an infinite future and carries it. The Boolean powers A_m^k are eventually periodic; for m = 3 to 8 the preperiods
are at most 9 and the periods 2, so the realized patterns repeat with period 2 from k = 9, and k = 3 to 11 decide every k. Check C2-C4
computes them: every three-element part of B_k and of every F_k^j takes all eight patterns, the near and far triples take all eight, and
every pair of 0 with a far vertex takes all four, for every k ≥ 3. ∎

**The radius-3 ball.** The bond ball of radius 3 about 0 contains (−k, k−i) and (k, j−k) for all k ≥ 3 and i, j ∈ {0,1,2}: at least six
distinctions for every k ≥ 3, on a line through 0 in both directions, so it is infinite and contains at least linearly many distinctions
within r steps. Which other distinctions it holds, and the balls of larger radius, are not claimed (BOND-BALLS computed 10 shortcuts at
three steps and 10 at four on this base).

## Reconciliations

- **Not settled by the pair counts.** By `OVERLAP-READ-20261111-001B`'s L5 the states depend only on how many edges lie on each pair. In
  the sheared frame the class (1,0) lies in two edges and the classes (0,1), (1,−1), (0,2), (1,2) in one. They span both coordinates, so
  no hypergraph with the same pair counts is invariant under one shift alone, and the far triple k columns back is k steps away. The
  fold runs along the doubly covered class (1,0): it is the law's forcing, not the presentation.
- **The faithful reading stands.** Every pair of 0 with a far vertex is shattered: the law ties 0 to no single far distinction. It binds
  0 only jointly with a whole triple, and only when the triple is all equal; the states that tell the pairs apart are the repeating ones
  above.

## Nearest known result

Directional determinism of ground states (the Newman–Moore triangular plaquette model, whose ground states fix a spin from the row
below), cellular-automaton spacetime diagrams, and expansive subdynamics of Z² actions (Boyle and Lind 1997). Here the propagation is
one-sided and partial. Classification: known-with-delta.

## Checks

`check.py` (result in `result.json`): C1 the column rule; C2-C4 the parts and pairs for every k ≥ 3 by the eventually periodic transfer
powers (periods for m = 3 to 8 recorded); C5 the mutation without the second edge kind.
