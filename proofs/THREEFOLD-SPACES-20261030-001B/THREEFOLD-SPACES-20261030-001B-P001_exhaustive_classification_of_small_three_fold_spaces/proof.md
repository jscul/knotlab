# Exhaustive classification of small three-fold spaces

Status: Proved

Ticket `THREEFOLD-SPACES-20261030-001B`, 2026-10-30.

**What it uses:**
- `THREEFOLD-SPACES-20261030-001A`: the dictionary, the splices and the library.
- `SPACE-SELECTION-20261030-001C`, Theorem 2 (duality). A gadget whose contacts are all three-fold with odd base count, with distinct corner
  triangles, is exact at the knot iff two conditions hold for its dual triple system H (triangles as points; contacts and the corner line
  L₀ as lines):
  - H is not 2-colourable;
  - H − L₀ is 2-colourable.
- `SPACE-SELECTION-20261030-001A`: the gadget library.

## Standard statement

**Setting.** A cubic triple system has n points and n lines. Each line has three distinct points, lines may repeat, and every point is on
three lines. A twisted system additionally complements one incidence (ticket A).

**Result 1 (exhaustive, n ≤ 13).** A connected cubic triple system that is not 2-colourable exists:
- for n = 7 only as the Fano plane;
- for n = 13 only as the Fano splice. The point and line splices are isomorphic.
- for no other n ≤ 13.

No connected twisted cubic triple system on n ≤ 13 points is non-colourable.

**Result 2 (the knot's three-fold spaces up to 13 triangles).** By the duality, the knot is exact on a three-fold gadget with odd base counts,
distinct corner triangles and at most 13 triangles iff its dual is:
- the Fano plane (7 triangles: the 64 Fano gadgets of `SPACE-SELECTION-20261030-001C`); or
- the 13-point Fano splice, with any of its lines as corner line.

The 13-point system has 3 orbits of lines under its automorphism group. All 3 × 6 choices of corner line and corner placement give gadgets
exact at the knot, with λ(0) = 25.

**Result 3 (phase-pure gadgets).** Gadgets whose contacts are all two-fold with one base incidence or three-fold with odd base count:
- there are 1, 0, 2, 24, 256 and 3,248 for n = 1, …, 6;
- none has a lock (ticket A, Proposition 7);
- none is exact at the knot, since three-fold spaces need seven triangles.

## Method

- **The encoding** (`sat_lib.py`).
  - Incidence variables, with cardinality constraints for the cubic structure.
  - The WLOG normalization: line 0 = {0, 1, 2}, and point 0 on lines 0, 1, 2.
  - Non-colourability: every colouring with point 0 coloured 0 has a monochromatic line.
  - Minimality: for every line, a witness colouring of the rest. This forces connectivity, because a disconnected non-colourable system has
    redundant lines.
  - Lexicographic order of rows 1..n−1 and columns 1..n−1.
- **Soundness of the symmetry breaking.**
  - Alternately sorting rows 1..n−1 and columns 1..n−1 never decreases the matrix read row by row, so it terminates with both orders.
  - Rows through point 0 and columns on line 0 sort first, so the normalization survives.
- **Minimality loses nothing.** A connected non-colourable cubic system is minimally non-colourable (ticket A, Theorem 1).
- **Replays.** The same answers come from Glucose 4 (n ≤ 12) and from the encoding without symmetry breaking (n ≤ 9).
- **Isomorphism classes at 7 and 13.** Every symmetry-broken solution is enumerated with blocking clauses. Classes are compared by
  isomorphism of the bipartite incidence graphs.
- **The knot side.**
  - Automorphisms come from the incidence graph.
  - Gadgets are built from (H, L₀) by a perfect matching of contacts to triangles (ticket A's constructor) and evaluated exactly at the knot.
- **Phase-pure gadgets** are enumerated as restricted slot partitions, canonicalized as in `SPACE-SELECTION-20261030-001B`.

## Proof

- **Results 1 and 3** are exhaustive computations as described.
- **Result 2** follows from Result 1 and the duality. The dual of a three-fold gadget with distinct corner triangles is a connected cubic
  triple system with distinct points per line:
  - its contacts join three distinct triangles;
  - each triangle has three slots, so every point is on three lines;
  - the corner line joins the three distinct corner triangles. ∎

## What the computation checks

`check.py` (about ten minutes):
- the SAT answers for n = 3..13, untwisted and twisted, and their two replays;
- the enumeration at 7 and 13;
- the line orbits and the 18 gadgets at 13;
- the phase-pure census;
- **controls:**
  - without the non-colourability clauses the encoding is satisfiable at 8 and 9;
  - the twist removes the Fano plane;
  - a 2-colourable system's dual gadget is not exact.

## Nonclaims

- **Simple lines only.** Lines repeating a point are outside the search. They appear as pieces of tight-cut decompositions (ticket C).
- **Sizes beyond 13.** Nothing is claimed here beyond 13 points. Ticket C shows that the family continues in more ways than Fano
  compositions.
