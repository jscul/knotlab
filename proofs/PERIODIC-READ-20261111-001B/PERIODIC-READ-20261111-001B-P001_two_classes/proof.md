# Two classes of knots and the global hollow triples

Status: Proved

Ticket `PERIODIC-READ-20261111-001B`, 2026-11-11. The lemma and the registered checks G1 and G2 were frozen in
`research/PERIODIC-READ-20261111-001/preregistration.md` before `check.py` ran.

## Standard statement

Let H be a finite 3-uniform hypergraph whose edges split into two classes A and B with equal pair counts: every pair of vertices
lies in as many edges of A as of B (for instance exactly one of each). Then A, B and H have the same proper 2-colourings. In particular every edge
of A is never monochromatic under a proper 2-colouring of B. The triangulations Z²/L of the torus by the triangular lattice
(literature; the guide's six-regular one-pair weaves) split so, into the triangles {x, x+(1,0), x+(1,1)} and {x, x+(0,1), x+(1,1)}.

## Words

In the guide's glossary: a knot pattern's knots are the edges, its states the proper 2-colourings, a co-knotted pair a pair in some
edge. From `OVERLAP-READ-20261111-001`: a set is forced by a set of knots when their states alone restrict it.

## Proof

Write c_X(p) for the number of edges of X containing the pair p. By hypothesis c_A = c_B on every pair. By
`OVERLAP-READ-20261111-001B`'s L5 (two hypergraphs with the same pair counts have the same proper 2-colourings, from the identity
Σ_p c(p)·[σ separates p] = 2(|E| − m(σ))), A and B have the same proper 2-colourings. A colouring is proper for H = A ∪ B exactly
when it is proper for both, so H has them too. An edge t of A is then never monochromatic under a proper colouring of B. In the
triangular lattice every edge {x, x+u} lies in one triangle of each kind, so in a quotient by L every pair gets as many triangles of
each kind as there are lattice edges over it; the counts are equal, and exactly one of each when the quotient is a simplicial two-fold
weave, as in all the weaves used here. ∎

**The global hollow triples.** Swap knots of a six-regular one-pair weave as `NAE-SURFACE-20261111-001` did: remove a knot t of one
class and add others. If the other class is untouched, it still forces t, so t is restricted in the new pattern; if t's pairs stay
free, t is an unnamed hollow triple, forced by a whole class: half the knots. That is the reading checked as G1 and G2.

## Nearest known result

An instance of trades in design theory (Hedayat and Li 1979: two block systems with the same pair coverage) and of the triangle
gadget of NAE-3SAT to maximum cut (Garey, Johnson and Stockmeyer 1976). The application to the swap-made bases is new as far as
found. Classification: known-with-delta, folklore risk high.

## Checks

`check.py` (result in `result.json`). C1: on all 272 six-regular one-pair weaves Z²/L with 12 to 24 distinctions, the two classes
and the whole weave have the same states (brute force). G1 (registered): in 91 of the 98 global bases every added set that only the
whole base forces is a removed source knot; it fails on 7 (status failed, recorded as such). G2 (registered): in all 85 bases whose
removed knots lie in one class, the other class forces each removed knot. Measured: in the other 13, the other class's remaining
knots with the swapped-in knots force each removed knot. C2 (mutation): a random set of as many knots forces them in none of the 85.
After the run (`research/PERIODIC-READ-20261111-001/derived_global.py`): of the 7 exceptions, 3 have their other global triples
forced by a proper ball once the removed knots are put back; 4 do not.

## Review

An independent referee found the lemma correct and `check.py` correct, asked for the statement with equal pair counts (now made), noted
that G2 is a corollary of the lemma, and that on the three smallest weaves "only the whole base forces it" degenerates (two steps reach
every knot). It characterized G1's exceptions: none has a pair-count certificate; on 25 distinctions one implication along an odd cycle
wrapping once around the weave holds six triples; on 26 and 27 the extra triples have forcing sets of 10 and 9 knots within two steps;
on 35 a triple of three distinctions in a row has one of 26 knots within three steps.

