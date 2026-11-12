# A direction the knot law does not lengthen

Status: Proved

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
{z, z+(0,1), z+(1,0)} and {z, z+(0,2), z+(1,2)}, B_k to {(−k,−2), (−k,−1), (−k,0), 0} and F_k^j to {0, (0,1), (0,2), (k, j)}. Work
there. B_k is then the translate of F_k^2 by −(k, 2), so everything proved for F_k^2 holds for B_k. Write c_x(y) for the value at (x, y).

**Column rule.** Every edge is a pair in column x with a distinction in column x+1, so a colouring is proper exactly when, for all x
and y: c_x(y) = c_x(y+1) implies c_{x+1}(y) ≠ c_x(y), and c_x(y) = c_x(y+2) implies c_{x+1}(y+2) ≠ c_x(y) (check C1 confirms this on
every pair of columns of period 3 to 8).

**The travelling triple (forcing).** If c_x(0) = c_x(1) = c_x(2) = a, the rule gives c_{x+1}(0) ≠ a (from the pair at rows 0, 1),
c_{x+1}(1) ≠ a (rows 1, 2) and c_{x+1}(2) ≠ a (rows 0, 2): the triple at column x+1 is all ā. By induction the triple at column x+k is
all a when k is even and all ā when k is odd. Hence on B_k a far triple all a forces the value at 0 (a for even k, ā for odd k), so the
pattern with the far triple all a and 0 the other value is excluded and B_k is not shattered; likewise on F_k^j a near triple all a
forces the value at (k, j). The forcing uses
both kinds of edge (the third step needs the pair at rows 0 and 2); without the second kind the set is shattered (check C5).

**Every proper part is shattered, for every k ≥ 3.** A state of the infinite pattern that repeats with period m in y is a bi-infinite
path in the transfer graph A_m on columns of period m (an edge c → d when the column rule holds between them), and every such path is a
state. A pattern on a part of F_k^j (columns 0 and k) is realized by a state of period m exactly when some walk of length k joins a
column with an infinite past to a column with an infinite future and carries it; only this direction is used. The Boolean powers A_m^k are eventually periodic; for m = 3 to 8 the preperiods
are at most 9 and the periods 2, so the realized patterns repeat with period 2 from k = 9, and k = 3 to 11 decide every k. Check C2-C4
computes them: every three-element part of every F_k^j (hence of B_k) takes all eight patterns, the triple takes all eight, and every
pair of 0 with a far vertex takes all four, for every k ≥ 3. (C2 tests the translate {(−k,0), (−k,1), (−k,2), 0} of F_k^0, a repeat.)
The theorem also holds at k = 2; at k = 1 the set contains a knot. ∎

**The radius-3 ball.** Translating F_k^j by (0, −1) and (0, −2) puts 0 in each of the three places of the near triple, so the bond ball
of radius 3 about 0 contains (k, t−k) and, by B_k's translates, (−k, k+t) for every k ≥ 3 and t = −2, …, 2: ten distinctions for every
k ≥ 3, all exactly k steps away (the referee checked k = 2 to 25), on a line through 0 in both directions. So it is infinite and
contains at least linearly many distinctions within r steps. Their bond distance is exactly 3 for k = 4 to 6 (no bond of three found,
computed by the referee); which other distinctions the ball holds, and the balls of larger radius, are not claimed.

## Reconciliations

- **Not an artefact of the presentation.** Steps apart depend only on which pairs are co-knotted, and bond distance only on the set of
  states; both are unchanged by any automorphism or re-presentation of the base, so the gap between them is intrinsic. The step metric
  is genuinely two-dimensional (shells 10, 26, 40, 54), and the far distinctions are k steps away. In the sheared frame the fold runs
  along the pair class (1, 0), the one that lies in two knots; the others lie in one. (An earlier draft argued from pair counts that no
  base with the same counts repeats along one shift only; that is not proved, and not needed.)
- **The faithful reading stands.** Every pair of 0 with a far vertex is shattered: the law ties 0 to no single far distinction. It binds
  0 only jointly with a whole triple, and only when the triple is all equal; the states that tell the pairs apart are the repeating ones
  above.

## Nearest known result

The closest precedent is Ledrappier's three-dot shift (1978), whose states are the Newman–Moore ground states: parity on the same
up-triangle hypergraph as base 16's first edge kind, where all pairs are free but {0, 2^n e1, 2^n e2} is constrained for every n, a bond
of three at 2^n steps: the "non-mixing shapes" of Kitchens and Schmidt (1993). Related: failures of strong irreducibility and block
gluing where pairs mix (Boyle, Pavlov and Schraudner 2010), signals in Z² shifts of finite type, and expansive subdynamics (Boyle and
Lind 1997). The delta here: the law is not-all-equal, not linear; the bonds have four elements, lie at every k along a line, and are read
as bond distance. Classification: known-with-delta, folklore risk moderate to high for the mechanism.

## Checks

`check.py` (result in `result.json`): C1 the column rule (the same rule encoded twice, a consistency check, not an independent test of
the shear); C2-C4 the parts and pairs for every k ≥ 3 by the eventually periodic transfer powers (periods for m = 3 to 8 recorded); C5
the mutation without the second edge kind, whose set is not refuted in a window (the referee's periodic states show it free at k = 3,
4, 7, 20).

## Review

An independent referee (its own code in the original frame: window SAT for constraint, doubly periodic states from 822 finite repeats
and an exact transfer computation for freeness) found the theorem true as stated and every step correct, and asked for these fixes,
made: the shear's image of B_k (the proof had rows 0 to 2; it is rows −2 to 0, a translate of F_k^2, so the statement stands and C2
repeats a translate of F_k^0); "realized by a state of period m"; the argument that the fold is not an artefact (now from invariance,
not pair counts); and the ball (ten distinctions per k, not six). It verified freeness and the two refuted patterns at k = 2 to 12, 20,
37, 100 and 101, and pointed to Ledrappier's shift as the nearest precedent.
