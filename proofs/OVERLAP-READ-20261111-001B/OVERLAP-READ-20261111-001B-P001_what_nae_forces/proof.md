# What not-all-equal forces

Status: Proved

Ticket `OVERLAP-READ-20261111-001B`, 2026-11-11. The statements L1 to L4 were frozen in
`research/OVERLAP-READ-20261111-001/preregistration.md` before the census ran; the referee's fixes to their wording are listed at the
end. L5 was added after the referee pointed to it; it was not registered.

Words (2026-11-11). The statements use the literature's words for a given substrate: a triangle is a knot, a vertex a
distinction, an edge a co-knotted pair and a triangulated surface a two-fold weave (Intuitions guide, Glossary).

## Standard statement

Let H be a 3-uniform hypergraph (a knot pattern: its edges are the knots, with no limit on how many edges contain a pair), and
consider its proper 2-colourings (no monochromatic edge; the states of the not-all-equal law, NAE).
- **L1.** If H has a proper 2-colouring, no vertex has the same colour in all of them; a pair of vertices, each free, whose joint
  colours are restricted is always equal or always different; and a triple whose pairs are unrestricted but which is restricted as a
  whole (an edge or not) misses exactly one complementary pair of colourings {a, ā}.
- **L2.** The proper 2-colourings of a Pasch configuration {a,b,c}, {a,y,z}, {x,b,z}, {x,y,c} are exactly those of the octahedron
  K(2,2,2) on the parts {a,x}, {b,y}, {c,z}: each of the four complementary triples {x,y,z}, {x,b,c}, {a,y,c}, {a,b,z} is never
  monochromatic, while every pair of the six vertices is unrestricted.
- **L3.** For every k ≥ 1 the book B_k, taken as the whole knot pattern (edges {p, q, i} for i = 1..k and nothing else), is read
  faithfully.
- **L4.** For a colouring σ let cut_c(σ) = Σ over pairs p of c(p)·[σ separates p], c(p) the number of edges containing p. Then
  cut_c(σ) = 2(|E| − m(σ)), m(σ) the number of monochromatic edges; so cut_c ≤ 2|E| with equality exactly at the proper colourings.
  If every pair in an edge lies in exactly λ ≥ 1 edges, the proper colourings are the colourings that separate exactly two thirds of
  those pairs; and a 2-(v, 3, λ) design with λ ≥ 1 has no proper 2-colouring when v ≥ 5 (sharp: v = 3 and 4 have 6 states).
- **L5 (added).** Two 3-uniform hypergraphs on the same vertices with the same number of edges on every pair (a trade, in the
  literature) have the same proper 2-colourings. Hence among knot patterns with the same pair counts at most one is read faithfully.

## Words

In the guide's glossary (`publication/knotlab/INTUITIONS.md`): a knot pattern is the hypergraph and a base one with a state; a state
is a proper 2-colouring; free means unrestricted. In this record: a **tied pair** is a restricted pair of free vertices, a **frozen**
distinction one with a single value; a **hollow triple** is three free pairs whose triple is not free (the glossary's), and one that
is not an edge is an **unnamed hollow triple**. A hollow triple of L1's form is a **plain** NAE when it misses 000 and 111, a
**signed** NAE otherwise: NAE with some vertices read negated (the glossary's signed incidence). Each is a knot by K1–K3. Read
faithfully (KNOTS-ALONE): a state exists, nothing is frozen, no pair is tied, and the hollow triples are exactly the edges.

## Proofs

**L1.** NAE treats both values alike, so the complement σ̄ of a state is a state, and the set of patterns a set S takes is closed under
complement. A single vertex therefore takes both values (nothing is frozen). A restricted pair of free vertices takes a complement-
closed proper subset of {00, 01, 10, 11} with both values in each place: {00, 11} or {01, 10}. For a triple S with free pairs, let
A ⊊ {0,1}³ be the patterns S takes; A is complement-closed, so |A| is even, and each pair projection of A is all of {0,1}². |A| = 2
gives pair projections of size at most 2. |A| = 4 makes each pair projection a bijection onto {0,1}², so the third coordinate is a
function of the other two that is a bijection in each argument: x₃ = x₁ ⊕ x₂ or its negation, a parity set; complementing all three
coordinates changes the parity of x₁ ⊕ x₂ ⊕ x₃, so a parity set is not complement-closed. Hence |A| = 6, and the two missing patterns
form one complementary pair. The argument does not use whether S is an edge. ∎

**L2.** Colourings of the octahedron are colourings of the Pasch, since the Pasch's edges are four of its eight. Conversely let σ
colour the Pasch properly. Suppose {x,y,z} were monochromatic, by complement all 0. Then {a,y,z} forces a = 1, {x,b,z} forces b = 1,
{x,y,c} forces c = 1, and {a,b,c} is monochromatic, a contradiction. The swaps (a x)(b y) and (a x)(c z) map the Pasch to itself and
act on the complementary four as the Klein four-group, transitively: (a x)(b y) sends {x,y,z} to {a,b,z} and (a x)(c z) sends it to
{a,y,c}, and their product sends it to {x,b,c}. So no complementary triple is monochromatic. That every pair of the six is free is a
finite check: the octahedron has 18 states (of 64 colourings), listed by `check.py`, and they take all four patterns on each of the
15 pairs. (L2 also follows from L5: the Pasch and its complementary four put one edge on each of the twelve pairs across the parts.) ∎

Consequence used by the census: a knot pattern containing a Pasch whose complementary triple t is not an edge is not read faithfully.
By L2, t is restricted; if all its pairs are free it is an unnamed hollow triple, and otherwise some pair of t is restricted, which by
L1 (nothing is frozen) is a tied pair.

**L3.** The states of B_k are: p ≠ q with the pages arbitrary (2·2^k states), and p = q with every page the other value (2 states). No
vertex is frozen. Every pair is free: {p, q} takes 01 and 10 with any pages and 00, 11 with the pages opposite; {p, i} and {q, i}
take every pattern with q, resp. p, chosen opposite; two pages take every pattern with p ≠ q. Each edge {p, q, i} is restricted (it
misses 000 and 111) with free pairs. Every triple containing both p and q is an edge. Any other triple contains at most one of them
and takes every pattern: given the pattern on its vertices, set the missing one of p, q (or both, if neither is in the triple) so that
p ≠ q; then every page is free. So the hollow triples are exactly the edges, and B_k is read faithfully. ∎ Inside a larger pattern
the statement is false: B_2 with {p,u,w} and {q,u,w} added has its pages in no other edge and is not read faithfully (the referee's
example; it contains adjacent apices on {u, w}).

**L4.** A non-monochromatic edge has exactly two separated pairs and a monochromatic one none, so Σ over edges of the number of its
separated pairs is 2(|E| − m(σ)); counting the same sum by pairs gives Σ_p c(p)·[σ separates p]. If c(p) = λ ≥ 1 on the set P of
co-edged pairs, then 3|E| = λ|P|, so σ separates (2|P|/3) − 2m(σ)/λ pairs of P, and σ is proper exactly when it separates 2|P|/3.
(This needs only the pair counts, so it covers more than the two-fold weaves, which also ask for one cycle of knots at each
distinction.) In a 2-(v, 3, λ) design with λ ≥ 1, P is every pair, and a colouring with classes of sizes s and v − s separates
s(v − s) ≤ ⌊v/2⌋⌈v/2⌉ pairs, while 2|P|/3 = v(v − 1)/3; for v = 2m, m² ≥ 2m(2m − 1)/3 needs m ≤ 2, and for v = 2m + 1,
m(m + 1) ≥ (2m + 1)·2m/3 needs m ≤ 1. So v ≤ 4. ∎

**L5.** By L4, σ is proper for H exactly when cut_c(σ) = 2|E|, and both sides depend only on c (|E| = Σ_p c(p)/3). So H and H′ with the
same c have the same proper colourings. A knot pattern read faithfully has its edges as its hollow triples, which depend only on the
states; two patterns with the same states and different edges cannot both be read faithfully. ∎ So what NAE reads of a knot pattern
is decided by how many knots lie on each pair, not by which triples are knots.

## Nearest known result

- **L1** is known: the relations definable from NAE by conjunction and projection are exactly the complement-closed (complementive)
  relations, the co-clone IN2 (Böhler, Reith, Schnoor and Vollmer, "Bases for Boolean co-clones", 2005; Creignou, Khanna and Sudan,
  *Complexity Classifications of Boolean Constraint Satisfaction Problems*, 2001). L1 is that fact read on at most three distinctions
  with free projections.
- **L4** is the triangle gadget of the NAE-3SAT to maximum-cut reduction (Garey, Johnson and Stockmeyer 1976); the design bound
  extends Rosa's 1970 counting for Steiner triple systems to every λ (Colbourn and Rosa, *Triple Systems*, 1999, on colourings).
- **L2 and L5** follow from L4 with trades (Hedayat and Li, 1979; the Pasch is the smallest trade). No source stating the colouring
  consequence was found. **L3** is elementary.
- Classification: known (L1, L4), known-with-delta (L2, L5: elementary consequences, folklore risk high). What is new is the reading:
  what NAE forces on triples no knot names.

## Checks

`check.py` (result in `result.json`). C1: L1 on every distinct state set of a labeled knot pattern on 3 to 6 distinctions and 5,000
random patterns on 7 to 9, those with a state (102,924 in all), testing every triple with free pairs, edges included: no violation.
C2: L2 (the Pasch and the octahedron have the same 18 states, every pair free, each complementary triple missing exactly 000 and 111).
C3: L3 on books with 1 to 12 pages. C4: L4's identity on 2,000 random patterns with random colourings, and no state on the complete
triple systems on 5 to 8 points, the Fano plane, the affine plane of order 3 and a 2-(6, 3, 2) design. C5 and C6: mutations (the
one-in-three law, and parity, which breaks the triple part alone) break C1. C7: L5 on the Pasch and 1,000 random patterns related by a
Pasch trade.

## Review

An independent referee (a fresh agent with its own code, no shared library) found L1 to L4 proved, with these fixes, all made: the
check's coverage at 6 distinctions was a sample, not exhaustive (now exhaustive by state sets); the mutation never tested the triple
check alone (parity added); L1 needs a state to exist; L2's consequence uses L1; L3 holds for the book as the whole pattern, not
inside a larger one; L4's design clause needs λ ≥ 1. It verified L1 on all 1,048,575 patterns on 6 distinctions, L4's identity on
736,072 pattern-colouring pairs, the design bound on STS(13), STS(15) and a 2-(7, 3, 2) design, and that all 16 complement-closed
relations on three distinctions occur, so L1 cannot be sharpened. It suggested L5 and the co-clone source for L1.
