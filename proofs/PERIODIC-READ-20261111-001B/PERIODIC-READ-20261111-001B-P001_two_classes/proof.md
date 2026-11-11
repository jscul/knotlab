# Two classes of knots and the global hollow triples

Status: Partial

Ticket `PERIODIC-READ-20261111-001B`, 2026-11-11. The lemma and the registered checks G1 and G2 were frozen in
`research/PERIODIC-READ-20261111-001/preregistration.md` before `check.py` ran.

## Standard statement

Let H be a finite 3-uniform hypergraph whose edges split into two classes A and B such that every pair of vertices lying in some edge
lies in exactly one edge of A and exactly one edge of B. Then A, B and H have the same proper 2-colourings. In particular every edge
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
triangular lattice every edge {x, x+u} lies in one triangle of each kind, and the quotient by L keeps this when the quotient is a
triangulation (no triangle collapses), so the torus triangulations split as stated. ∎

**The global hollow triples.** Swap knots of a six-regular one-pair weave as `NAE-SURFACE-20261111-001` did: remove a knot t of one
class and add others. If the other class is untouched, it still forces t, so t is restricted in the new pattern; if t's pairs stay
free, t is an unnamed hollow triple, forced by a whole class: half the knots. That is the reading checked as G1 and G2.

## Nearest known result

An instance of trades in design theory (Hedayat and Li 1979: two block systems with the same pair coverage) and of the triangle
gadget of NAE-3SAT to maximum cut (Garey, Johnson and Stockmeyer 1976). The application to the swap-made bases is new as far as
found. Classification: known-with-delta, folklore risk high.

## Checks

PENDING
