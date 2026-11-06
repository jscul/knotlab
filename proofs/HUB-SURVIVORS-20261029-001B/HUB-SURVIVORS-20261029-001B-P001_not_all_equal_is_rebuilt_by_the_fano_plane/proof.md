# Not-all-equal is rebuilt by its copies on the Fano plane, and by nothing smaller

Status: Proved

Ticket `HUB-SURVIVORS-20261029-001B`, 2026-10-29.

## Standard statement

Let NAE ⊆ {0, 1}³ exclude exactly 000 and 111. Build a *gadget* from m copies of NAE on triples of variables, so that three
variables (the *legs*) lie in one copy each, every other variable lies in at least two copies, no copy repeats a variable, and the
copies are connected. Its relation is the set of leg tuples that extend to a 2-colouring of all variables with no monochromatic
copy.
- Put seven copies on the lines of the Fano plane, and replace one point by three legs, one on each line through it. The relation is
  exactly NAE.
- Every gadget whose relation is NAE has at least seven copies. With exactly seven copies it is this punctured Fano plane.
- The punctured Fano gadget has exactly 5 hidden completions for every tuple of NAE. So replacing every copy of NAE in any network by
  it multiplies the number of solutions by 5 per replaced copy and leaves the relation unchanged. NAE is an exact fixed point of this
  substitution, counts included.

## Nearest known result

- **Property B.** A hypergraph has property B when it is 2-colourable with no monochromatic edge (Bernstein, Erdős). The least number
  of edges in a 3-uniform hypergraph without property B is m(3) = 7. The Fano plane is the only example; arXiv 2303.03803 states
  this, and it is classical.
- **Gadgets.** Reductions for NAE satisfiability use other gadgets. A bounded search (two queries) found no use of a punctured Fano
  plane as a gadget that rebuilds NAE.
- **In the repository.** `GEOMETRY-LAW-20261029-001A` proved that without hubs (every variable in at most two copies) no gadget of a
  non-parity knot rebuilds it. NAE in particular is never rebuilt there.
- **Classification.** The ingredients are classical. The statement (NAE's smallest self-rebuilding gadget is the punctured Fano plane,
  and it is unique) is a candidate local delta.

## Setting

- **Hub gadgets.** As in the standard statement. A *hub* is a hidden variable in three or more copies. In the canonical vocabulary a
  hub is a common hub (equality fan-out), not a contact.
- **Wires.** A *wire* has two ends instead of three legs. End b lies in one copy, and end a in any number of copies (at least one).
  Its relation is the set of pairs (a, b) that extend. An *equality wire* has relation {00, 11}, an *inequality wire* {01, 10}.

## Theorem 1 (the punctured Fano plane rebuilds NAE)

Let Φ be the Fano plane on points 0, …, 6 with lines {i, i + 1, i + 3} (mod 7). Split point 0 into legs a, b, c on its three lines
{0, 1, 3}, {0, 4, 5} and {0, 2, 6}. Then the relation of this gadget is NAE.

*Proof.*
- **Constant legs are excluded.** If a = b = c = v, colouring point 0 with v gives a 2-colouring of Φ without monochromatic lines,
  which does not exist (property B fails for Φ). So 000 and 111 are excluded.
- **Every other leg tuple extends.**
  - The relation is invariant under complementing all colours. It is also invariant under permuting the legs: the stabilizer of a
    point in the automorphism group of Φ, of order 24, acts on the three lines through it as S₃.
  - So it suffices to extend (a, b, c) = (0, 0, 1). Colour points 1, …, 6 as 1, 0, 0, 1, 1, 0.
  - The lines through the split point read (0, 1, 0), (0, 1, 1) and (1, 0, 0). The other four lines read (1, 0, 1), (0, 0, 1),
    (0, 1, 0) and (1, 1, 0). None is monochromatic. ∎

The point is arbitrary, since Φ is point-transitive (check 1 verifies all seven).

## Lemma 2 (two legs on one copy force an equality wire)

Suppose a gadget Γ with relation NAE has a copy C carrying two legs, C = (l₁, l₂, h) with h hidden. Then the rest Γ − C, with ends h
and l₃, is an equality wire.

*Proof.*
- A copy carrying three legs would be the whole gadget, so l₃ lies in another copy. Since h is hidden, it lies in some copy of the
  rest, so Γ − C is a wire with ends h (any number of copies) and l₃ (one copy).
- If l₁ = l₂ = v, the copy C forces h = 1 − v. NAE then requires l₃ = 1 − v allowed and l₃ = v excluded.
- So the rest allows (h, l₃) = (1 − v, 1 − v) and excludes (1 − v, v), for both v: its relation is {00, 11}. ∎

## Lemma 3 (no small wires; computation)

No wire of at most six NAE copies is an equality or an inequality wire.

*Proof.* Exhaustive search over all wires with 2 to 6 copies, every multiset of hidden variables and every position of the two ends
(check 3, 1,017,014 wires at six copies). ∎

## Theorem 4 (minimality and uniqueness)

Every hub gadget of NAE copies with relation NAE has at least seven copies. With exactly seven copies it is the punctured Fano plane.

*Proof.* Let Γ have m copies and relation NAE.
- **Two legs on one copy.** By Lemma 2 the other m − 1 copies form an equality wire. By Lemma 3, m − 1 ≥ 7, so m ≥ 8.
- **Legs on three distinct copies.** Identify the three legs with one new vertex p.
  - Every copy still has three distinct vertices, so the copies form a 3-uniform hypergraph H with m edges, possibly with repeats.
  - A 2-colouring of H without monochromatic edges would extend the leg tuple (v, v, v), where v is the colour of p. NAE excludes
    that tuple, so H has no property B.
  - Deleting repeated edges keeps this. So H has at least m(3) = 7 distinct edges, and m ≥ 7.
  - If m = 7, H has seven distinct edges and no property B, so H is the Fano plane, and Γ is the Fano plane with p split into its
    three lines. ∎

Check 2 confirms m ≥ 7 directly, by exhaustive search over gadgets of up to six copies (199,340 at six). Check 4 (run with `--seven`)
confirms uniqueness at seven copies at the level of gadgets, without the citation.

## Proposition 5 (an exact counted fixed point)

For every leg tuple t, let c(t) be the number of 2-colourings of the six hidden points of the punctured Fano gadget that extend t.
Then c(t) = 5 for the six tuples of NAE and c(t) = 0 for 000 and 111. Hence, for any network N of NAE copies, replacing each copy
by a punctured Fano gadget (fresh hidden points for each) gives a network with exactly 5^|N| times as many solutions on N's
variables. The substitution preserves the relation and every count, up to that factor.

*Proof.*
- The gadget's counts are invariant under permuting the legs (the point stabilizer acts as S₃ on the three lines) and under
  complementing every colour. These act transitively on the six tuples of NAE, so c is constant on NAE.
- Check 6 computes the constant, 5, at every point.
- In the substituted network each copy's hidden points are private, so the counts multiply. ∎

**Reading.** Each level of NAE's Fano tower adds exactly log₂ 5 ≈ 2.32 bits of hidden witnesses per replaced copy, and its visible
law is unchanged. In the language of renormalization, NAE is an exact fixed point of the Fano substitution. Without hubs, every
non-parity law dies within three levels (`GEOMETRY-LAW-20261029-001A`).

## Reading

- **What it says.** With hubs, not-all-equal is a law that survives patterns of patterns, which native gluing forbids
  (`GEOMETRY-LAW-20261029-001A`). Its smallest pattern of patterns is the Fano plane, PG(2, 2), with its incidence geometry: any two
  points on exactly one line, any two lines through exactly one point.
- **What it does not say.**
  - Larger hypergraphs without property B also rebuild NAE, so the law does not force the Fano plane in general.
  - The Fano plane is the least such structure, and the unique one at that size.
- **The two/three reading.** The gadget's six hidden points are hubs, each in three copies, so it uses equality fan-out. What
  rebuilds the three-place knot is the projective plane's way of making every two lines meet.

## Checks

`check.py` (numpy) on the library `nae_lib.py`, with `result.json`:
- **1.** The Fano plane has no property B, and deleting any line gives it. The punctured Fano gadget's relation is NAE at all seven
  points.
- **2.** Exhaustive over gadgets with 2 to 6 copies: none has relation NAE. Counts: 0, 6, 90, 3374 and 199,340 gadgets.
- **3.** Exhaustive over wires with 2 to 6 copies: none is an equality or inequality wire. Counts: 1, 14, 342, 14,908 and
  1,017,014 wires.
- **4.** Run with `--seven`: all 17,610,420 seven-copy gadgets were evaluated; the 90 with relation NAE (labelled copies) all merge
  into seven edges on seven points with every pair of points in exactly one edge, the Fano plane.
- **6.** The punctured Fano gadget has exactly 5 completions for each NAE tuple and none for 000 and 111, at every point.
- **5.** Controls that must fire:
  - the punctured Fano gadget of OR is not OR;
  - a mutated plane (one line changed) is 2-colourable, and its puncture does not give NAE;
  - the wire search finds wires when NAE is replaced by parity.

The enumeration was checked against an enumeration with full canonical labelling, which gives 3, 11 and 104 shapes with three legs
at three, four and five copies for every relation. An earlier ordering of the hidden variables skipped gadgets; it was corrected
before these checks.

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Theorem 1 | The Fano plane's lack of property B and its point stabilizer | Elementary |
| Lemma 2, Theorem 4 | Merging legs into a hypergraph without property B (m(3) = 7, the Fano plane unique); the wire lemma by exhaustive search | Candidate local delta; classical ingredients |
| The question | Which laws survive patterns of patterns once hubs are allowed (`HUB-SURVIVORS-20261029-001`) | From the program |

## What this does not show

- That NAE is rebuilt only through the Fano plane at larger sizes: other hypergraphs without property B also work.
- Counts for other rebuilding gadgets: only the punctured Fano gadget is shown to be a counted fixed point.
- Lemma 3 beyond six copies: whether NAE wires exist at all is open.
