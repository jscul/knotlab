# The amplitude by computation

Status: Proved

Ticket `THREEFOLD-AMPLITUDE-20261030-001B`, 2026-10-30. This ticket confirms tickets A and C by exact computation. A computation does not
discharge a theorem; where a statement below is exhaustive, its range is stated.

**What it uses:**
- **`THREEFOLD-AMPLITUDE-20261030-001A`:** the amplitude, the brace amplitudes, and `amplitude_lib.py` (exact counting by variable
  elimination, Tutte matchings, arborescence numbers, the law's corner relation).
- **`THREEFOLD-AMPLITUDE-20261030-001C`:** one amplitude per system, shared with the transpose.
- **`THREEFOLD-GRAMMAR-20261030-001B`:** the SAT census of connected cubic multi-systems that are not 2-colourable, up to 10 points, and the
  decoration of cores into spaces (`census_lib.py`).
- **`THREEFOLD-GRAMMAR-20261030-001A`:** the tight-cut decomposition, brace types, Kasteleyn and Pfaffian signings (`grammar_lib.py`).
- **`computation_lib.py` (this ticket):** builders for omnitruncations of planar maps, the glue of hypermaps (coning the faces of a plane
  bipartite graph and dualizing), trisums of prisms along a square face, Kálmán's hypertrees, and spanning trees by Kirchhoff's theorem.

## Standard statement

1. **The census.** Each of the 2,652 isomorphism classes of connected cubic multi-systems with at most 10 points that are not 2-colourable
   (160 untwisted, 2,492 with one twisted incidence):
   - is not colourable;
   - has one amplitude at every line;
   - has a transpose that is not colourable, with the same amplitude at every point;
   - has amplitude equal to the product of its brace amplitudes: 1 for the two-vertex brace and the doubled square, 5 for the Heawood graph,
     the arborescence number for a planar brace, and 6 for the one non-planar brace that occurs.

   The amplitudes are 1, 2, 3 or 5 untwisted, and 1 to 6 twisted.
2. **The law up to 22 points.**
   - **Untwisted.** On each of the eight three-fold spaces with at most 22 points, at every corner line, the knot's corner relation is exact
     with λ(0) = (−1)^(n−1) 5^(Fano atoms).
   - **Twisted.** Each of the 24 twisted classes with at most 22 points has one amplitude, shared with its transpose and equal to the product
     of its brace amplitudes.
3. **Planar glue.**
   - **Omnitruncations.** On the omnitruncations of 13 planar maps, up to the dodecahedron (60 lines), the amplitude at every line equals the
     number of spanning trees of the map and all three arborescence numbers.
   - **Hypermaps.** On the glue of 6 hypermaps, the amplitude equals Kálmán's hypertree count of both hypergraphs and the arborescence numbers.
     It differs from the number of spanning trees of the hypermap.
4. **Trisums.** Two families were tested: 44 trisums of three prisms along a square face (11 triples of sizes, 4 gluings each), and 6 nested
   trisums whose first piece is itself a trisum.
   - Each is a single brace with a Pfaffian signing, not colourable with it and colourable without it.
   - Each has one amplitude, shared with its transpose.
   - **The amplitude depends on the gluing.** For example (2,3,3) gives 13 or 14, (3,3,3) gives 18 or 21, and (4,4,4) gives 36 or 52. So it
     is not a function of the pieces' amplitudes.
   - Two cubes and a 2k-prism give 3k for every gluing.

## Results

**The census.**

| | classes | amplitude distribution |
|---|---|---|
| untwisted | 160 (1, 0, 1, 1, 2, 2, 8, 12, 36, 97 for n = 1..10) | 1: 119, 2: 32, 3: 4, 5: 5 |
| one twist | 2,492 (0, 1, 1, 3, 7, 19, 54, 166, 515, 1,726) | 1: 1,698, 2: 697, 3: 61, 4: 8, 5: 27, 6: 1 |

**Omnitruncation glue: amplitude = spanning trees of the map.**

| Map | Lines | Amplitude |
|---|---|---|
| triangle, 4-cycle, 5-cycle | 6, 8, 10 | 3, 4, 5 |
| K₄ | 12 | 16 |
| cube, octahedron | 24, 24 | 384, 384 |
| triangular prism | 18 | 75 |
| square pyramid | 16 | 45 |
| wheels W₆, W₇ | 20, 24 | 121, 320 |
| K₂,₃ | 12 | 12 |
| pentagonal prism | 30 | 1,805 |
| dodecahedron | 60 | 5,184,000 |

**Hypermap glue: amplitude = hypertrees, not spanning trees.**

| Hypermap | Amplitude = hypertrees | Spanning trees |
|---|---|---|
| K₂,₃ | 3 | 12 |
| K₂,₄ | 4 | 32 |
| 6-cycle | 3 | 6 |
| cube | 16 | 384 |
| hexagonal prism | 96 | 8,100 |
| 3×4 grid | 56 | 2,415 |

**Trisums of three prisms** (2k-prisms, listed by k), along a square face. The four gluings fix the first prism and reflect the face of
the second and/or third.

| k | gluings 000, 001, 010, 011 |
|---|---|
| 2, 2, 2 | 6, 6, 6, 6 |
| 2, 2, 3 | 9, 9, 9, 9 |
| 2, 3, 3 | 13, 14, 14, 13 |
| 3, 3, 3 | 18, 21, 21, 21 |
| 2, 2, 4 | 12, 12, 12, 12 |
| 2, 3, 4 | 17, 19, 19, 17 |
| 3, 3, 4 | 23, 29, 28, 28 |
| 2, 4, 4 | 22, 26, 26, 22 |
| 4, 4, 4 | 36, 52, 52, 52 |
| 2, 2, 5 | 15, 15, 15, 15 |
| 2, 3, 5 | 21, 24, 24, 21 |

**Nested trisums.** Trisums of the (2,2,2) or (2,2,3) trisum with two prisms have amplitudes 18 and 27, the same for both gluings tested.

## Method

- **Counting.** All counts are exact: variable elimination over integers, and determinants in sympy.
- **The census** is recomputed by SAT from `census_lib.py`, with the same class counts as `THREEFOLD-GRAMMAR-20261030-001B`.
- **The spaces** up to 22 points are rebuilt by decoration and classified up to isomorphism, as in `THREEFOLD-SURFACES-20261030-001B`.
- **Hypertrees** are counted by enumerating spanning trees and collecting their degree vectors on one side.
- **Pfaffian signings** of trisums are found by the search in `grammar_lib.py`.

## Controls

- K₂,₃ has 3 hypertrees and 12 spanning trees.
- An omnitruncation without its Kasteleyn signs is colourable.
- Two gluings of the (2,3,3) trisum have different amplitudes.
- The census has twisted classes that are colourable without their twist.

## Reading

- **Tickets A and C** are confirmed on every small case and on large planar glue.
- **Non-planar glue is the one place where more is needed.** Its amplitude is a property of how the pieces are glued, not of the pieces
  alone. Two cubes and one 2k-prism are the exception seen here: every gluing gives 3k, three times the prism's amplitude.

## Nonclaims

- Nothing here is claimed beyond the stated ranges.
- The rule 3k for two cubes and a 2k-prism is observed, not proved.
