# The axis built from logic

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): an open end is a loose end. Results are unchanged;
the earlier text is in git history.

Epic `LOGIC-AXIS-20261107-001` (program topology), 2026-11-07.

## The question

- **The owner's picture.** On 2026-11-07 the owner asked for an investigation of the expansion of the
  smallest instance of space (one knot) as the underlying CNF grows to the infinite. They described a
  number line or Cartesian plane whose axes are themselves infinite structures of logic, so that the
  dimensions expand out in measures of logic. They approved this epic with "Yep, let's do it. Please
  get started."
- **The measure used.** Bond distance (`NATIVE-NETWORK-20261021-001`): the least size of a knot (K1–K3)
  through two distinctions, minus one. It is computed from allowed states alone.
- **The questions.**
  - On infinite uniform laws, when is bond distance a ruler?
  - What does a frozen law measure?
  - With nothing drawn, can a growing law stretch its own ruler, and what dimension results?
- **Open questions served.** Question 9 (space from a law) and question 7 (limits).

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Without ends, bond distance is a ruler.** A law that splits at range D has only D-chained knots, so bond distance >= separation/D. A parity law whose finite moves are dense (a law without ends) splits. | proved | A |
| 2 | **The lattice's dimension can be read from allowed states.** Tseitin's law on Z^D has bond distance between d_∞ and (2D−2)(d+1)+1; the gauge law on Z^2 has 2d+1 to 2d+7, the taxicab distance doubled. So bond balls grow like r^D. | proved; computed offsets only 1, 3, 5 on a 41×41 box | A |
| 3 | **The logical number line.** On the atom thread w(t−1) ∧ L(t) → w(t), the bond distance between witnesses w_s and w_t is exactly t − s + 1, and every knot through them contains the loops between them. A chain of two-place ties has no knot and no bond distance. | proved | A |
| 4 | **One bit per site freezes.** A parity law with one distinction per site is free or has no finite moves. A native parity plane needs a distinction per lattice direction. | proved (classical) | A |
| 5 | **Native in every variable, still a shortcut.** With Ledrappier on x, z free and y = x + z, every variable is flipped by a finite move, yet a six-variable knot joins points 2^k apart for every k. The per-variable source-aware reading does not give a ruler; the whole law must have no ends. | proved; correction request filed | A |
| 6 | **Conservative growth never stretches.** A conservative extension never increases bond distance. A system that keeps its old allowed states grows only by adding distinctions, never by moving existing ones apart. | proved | A |
| 7 | **The frozen axis is measured in signed bits.** In Ledrappier's law the three-place knots are exactly the Frobenius triangles, so bond balls are infinite. Along each lattice line, bond distance is at most 1 + w(n) (the non-adjacent-form weight of the separation), and equals 2 exactly at powers of two. | proved | B |
| 8 | **Conjecture: equality.** Bond distance along the axis is exactly 1 + w(n), and 1 + \|v\|_D in the plane. | conjecture; windows: n <= 128 at sizes <= 4, n = 43, 45, 51, 53 at size 5, all 168 vectors of [−6,6]^2 | B |
| 9 | **Towers with nothing drawn split by loose ends.** Gadgets adding no loose ends keep the old knot: bond distance 2 at every level (G0, the 2026-10-20 refinement; G6 with hubs). Gadgets adding loose ends stretch by a fixed factor: 3^k + 1 (star, hexagon) and 3·4^(k−1) + 1 (prism), with dimension estimates 1.26, 1.63 and 1.29. | exploratory experiment | C |
| 10 | **Loose ends are the criterion (hub-free).** A substitution keeps the old knot exactly when its gadget adds no loose end, and then every step is conservative (collapse). On tree-shaped knot graphs, bond distance = path knots + 1, so the star tower stretches as 3^k + 1. | proved | D |

## Answer

- **Can logic build an axis whose spacing it measures itself?**
  - **Yes, when nothing is opened by infinity.** The thread is an exact logical number line: one unit
    per loop.
  - **The plane.** The gauge and Tseitin planes measure distance like a taxi grid: an x-count plus a
    y-count, never the diagonal. Their bond balls give the dimension (2, or D on Z^D) from the allowed
    states alone.
- **A law opened by infinity is not a ruler.** Ledrappier's law, every distinction of which is opened by
  infinity, measures its axis by signed binary digits. Points 2^k apart are bonded as tightly as
  neighbours, and every bond ball is infinite.
- **As the system grows.**
  - **No stretching.** Keeping old allowed states never moves two distinctions apart.
  - **Collapse.** Refinement without loose ends (the 2026-10-20 law) keeps every coarse knot, so space
    collapses.
  - **Stretching.** Refinement that adds loose ends stretches the ruler by a fixed factor per level, and
    the result has a definite growth dimension: log(copies)/log(stretch), a ratio of two logical counts.
- **The barrier.** That dimension is chosen with the gadget, which acts like a drawing. No tested law
  selects its own dimension, and none built a plane (dimension 2) with nothing drawn.

## Literature and provenance

- **Ticket A.**
  - **Sources.** Strong irreducibility; dense homoclinic groups giving specification for algebraic
    Z^d-actions (Lind–Schmidt 1999; Lind–Schmidt–Verbitskiy 2013).
  - **Where the ideas came from.** The proofs are standard. The target (circuits through two
    coordinates as a ruler, dimension read off allowed states) and item 5 come from the program's
    perspective.
  - **Folklore risk.** High for items 1, 2 and 4 as mathematics; low for the reading.
- **Ticket B.**
  - **Sources.** Ledrappier 1978; non-mixing shapes (Schmidt; Masser 2004; Derksen–Masser 2012–18);
    Arenas-Carmona–Berend–Bergelson 2008; Mason–Stothers in characteristic p; non-adjacent forms
    (Reitwiesner 1960).
  - **Not found.** A formula for the least minimal relation through two points, or the signed-binary
    construction.
  - **Folklore risk.** Moderate: Derksen–Masser's structure theorem is close.
- **Tickets C and D.**
  - **Sources.** Cut/cycle duality is classical. Dimension from ball growth in rewriting systems is
    Wolfram's method (2020); self-similar dimension is log(copies)/log(scale) (Moran; Hutchinson).
  - **The delta.** Measuring distance by bonds of the allowed states rather than by hypergraph
    adjacency, and the open-end criterion.
  - **Folklore risk.** Low to moderate.

## Reading

**Interpretation, not a theorem.**
- **The number line.** On the thread, the unit of distance is one loop, one open distinction.
- **The plane.** It is the taxicab product of two such counts, needs a distinction per axis direction
  at every point, and exists as a ruler only when finite moves reach everywhere.
- **Growth to infinity.** It happens at the edges: in conservative growth, space never stretches
  between existing distinctions.
- **Where stretching happens.** Space expands between existing distinctions exactly where growth adds
  loose ends, distinctions left free on one side.
- **The link between two intuitions.** This ties the growth of emergent information to the growth of
  space. Every stretching gadget added three loose ends and three open bits per substitution.
- **Not every new bit stretches.** Bits added as closed cycles of knots (G0) did not.

## Workspace assumption challenged

- **The assumption.** The source-aware reading (adopted 2026-10-20) treats a knot as native when each
  of its variables can be flipped by a finite change.
- **The challenge.** Ticket A shows such a knot can still bind through a frozen witness field and join
  far-apart points. The decision is filed in
  [canonical_correction_request.md](canonical_correction_request.md).

## Ratio

Since the epic opened:
- **Substantive.** Four evidence families changed conclusions: A, B and D (proofs) and C (an
  exploratory experiment).
- **Administrative.** This note, the correction request and the closure.

## Pending the owner

- **New.**
  - Whether claims about distance on infinite systems must also state whether the law has ends
    (`canonical_correction_request.md`).
- **Carried from earlier epics.**
  - Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Counted length as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the axis built from logic | **Status:** Successful | Rulers characterized (no ends gives a ruler; dimension read from allowed states); the frozen axis measured in signed bits; growth with nothing drawn stretches exactly through loose ends. Unresolved: the signed-binary lower bound, and a law that selects its own dimension. |
| Local direction — rulers on drawn lattices and frozen laws | Practically exhausted for this purpose | The lattice cases are classical in substance. The remaining frozen-law question is number theory (Derksen–Masser), not space. |
| Broader exploration — question 9, space with nothing drawn | Sharpened | Every tested way to get a dimension supplies it: a lattice, or a gadget's copies and stretch. Loose ends are now known to be necessary for stretching. |
| Long-term goal — space from logic | Obstruction learned, capability gained | Logic can measure and stretch space (a ruler from allowed states; loose ends stretch it), but no tested law chooses its dimension. |
| Next recommendation — growth at loose ends | **Next step:** Continue, as a fresh epic. Let a uniform rule act only where the relation shows an loose end (frontier growth, the thread's way of growing), with no chosen gadget shape, and measure the growth exponent of bond balls. | This is the direct test of the owner's picture of an axis growing outward. It asks whether frontier growth plus a local closing rule gives polynomial growth (a dimension) or trees and small worlds. A negative answer would be a clean obstruction. |
| Interest — that recommendation | **2/3 — Promising** | Loose ends are now known to be what stretches, and the exact connected-cut method makes bond balls computable at scale. The main risk is that random frontier growth gives trees or small worlds, as random rewriting usually does. |
| Execution — that action | Deferred to the owner | **Not started.** **Stop when** a bounded census of frontier rules (three or four rules, sizes up to about 10^4 knots) yields an exponent or an obstruction. The alternatives are the signed-binary lower bound (1/3) and the logical Cartesian product of two threads (1/3). |
