# Lane A: does a local law favour the knot's sign class?

Ticket `NEXT-DIRECTION-SCAN-20261031-001A`, 2026-10-31. Scouting pass (documentation); no theorem is activated.

## Question

On a cubic bipartite graph (the incidence graph of a cubic triple system), a *sign class* is a signing of the incidences up to switching
(cuts). Each class has a number of proper 2-colourings: a line is satisfied when the colours of its points, each flipped by its sign, are not all
equal. The knot's class is the class with no colouring. By the dictionary of the counting note (Lemma 6), it exists exactly when the graph is
Pfaffian, and it is then unique.

The lane asks whether a simple local law selects the knot's class. Here a step flips one incidence and must lower the number of colourings.
Does descent always reach the knot's class, or are there *traps*, classes with colourings and no lower neighbour?

## Method

`descent.py` enumerates every sign class (one representative per element of the cycle space, 2^β classes) and counts all colourings with
numpy. It reports the traps and the counts by flip distance from the knot's class. Every graph is small enough for exhaustive enumeration
(up to 16,384 classes).

## Results

| Graph | Girth | Classes | No-colouring classes | Traps | Smallest trap count |
| --- | --- | --- | --- | --- | --- |
| cube (K4^(3)) | 4 | 32 | 1 | 4 | 4 |
| 6-prism | 4 | 128 | 1 | 1 | 4 |
| 8-prism | 4 | 512 | 1 | 1 | 4 |
| trisum of three cubes | 4 | 512 | 1 | 6 | 12 |
| trisum of cube, cube, 6-prism | 4 | 2048 | 1 | 3 | 12 |
| truncated octahedron | 4 | 8192 | 1 | 14 | 32 |
| Heawood (Fano) | 6 | 256 | 1 | **0** | — |
| Fano with a point block (13 points) | 6 | 16384 | 1 | **0** | — |
| Fano with a line block (13 points) | 6 | 16384 | 1 | **0** | — |
| K3,3 (control, not Pfaffian) | 4 | 16 | 0 | 6 | 2 |
| Möbius–Kantor (control) | 6 | 512 | 0 | 31 | 6 |
| Pappus (control) | 6 | 1024 | 0 | 24 | 14 |

- **Every tested Pfaffian graph has exactly one class with no colouring**, as the dictionary requires. The three non-Pfaffian controls have
  none.
- **Traps appear on exactly the Pfaffian graphs that have 4-cycles.** On the three girth-6 Pfaffian graphs, which are the Fano plane and two
  13-point Fano splices (the knot's own spaces, made of Fano atoms with no planar glue), descent reaches the knot's class from every class.
- **The count is not monotone in flip distance.** For example, on the 6-prism every class at distance 1 has 6 colourings, but some class at
  distance 2 has 4. On the 8-prism, distance 1 gives 8 and distance 2 has a minimum of 4. A trap is therefore not a near-knot class that
  merely stalls.
- **Girth 6 alone does not remove traps.** Möbius–Kantor and Pappus have girth 6 and many traps, but they have no knot class.

## Reading

- On the knot's own spaces (Fano atoms only), the colouring count is a funnel onto the knot's class. Planar glue, whose square faces carry
  the twists, creates local minima.
- The descent law is imposed, not native. No substrate rule says that a sign class moves by single flips toward fewer colourings. The finding
  therefore supports "a local law favours the knot's signs" only in this weak, observer-chosen sense.
- The coincidence of traps with 4-cycles suggests a local combinatorial cause, the square faces, rather than a selection by the knot.
- **Not established:** that every girth-6 Pfaffian graph is trap-free; that every graph with a square face has a trap; any native dynamics.

## Interest as a standalone epic

**1/3 — Exploratory poking.** The funnel on Fano spaces is a clean observation, and the trap/4-cycle split is sharp on 12 graphs. But the
dynamics is imposed, and the likely explanation (square faces as local twists) points back to the counting arc's own mechanism rather than to
native emergence.

## Files

- `descent.py`: the computation (run with `--write`).
- `results.json`: per-graph classes, counts, traps and counts by flip distance.
- `descent.log`: the run log.
