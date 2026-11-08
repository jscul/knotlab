# Genus read by rings of cuts

Epic `GENUS-CUT-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `LATTICE-NET-20261108-001` proved that on a torus of rings a ring of cuts that bounds separates, one round the
  torus does not, and two parallel ones do. Its direction 1, relayed by the coordinator on 2026-11-08: cut round the torus in both
  directions together and test whether it stays in one piece, then a genus-2 lattice; stop with "the most cuts that keep one piece is
  two per handle" as a theorem, or with the first surface where it fails.
- **The question.** Can a network of rings across time count its surface's handles by how many rings of cuts it survives in one piece?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The pieces are read exactly.** In any network, after any contacts are cut, the pieces read from which contacts need which rings are exactly the pieces of the ring graph without the cut contacts. Every uncut contact needs both of its rings from lag 1, and needs never cross a cut. | proved; checked on 504 cut sets | A |
| 2 | **Two rings of cuts per handle.** A family of rings of cuts keeps the network in one piece exactly when it is independent in the surface's homology mod 2. So at most 2g keep one piece on a surface of genus g, some 2g do, and one more always separates. | proved; checked on 784 families at genus 1, 2 and 6 | A |
| 3 | **The torus and genus 2.** A ring of cuts round the torus in each direction keeps it in one piece and a third separates it. On genus 2 four rings of cuts can keep one piece and five never do. The regular genus-2 network of 16 rings with three contacts each (its rotations from GL(2,3)) keeps every contact persistent at every lag at every size. | proved | A |
| 4 | **One piece is not full reach.** After a ring of cuts round the torus each way, every uncut contact still needs every ring on sides 3 to 20 except 8 and 16, where a few contacts never need three rings in the far corner. Cutting the handle removes the cancellation that kept even tori from the antipode. | computed, exact | A, check 4 and stress test |

## Answer

The stop rule's first outcome holds, for every surface: the most rings of cuts that keep a network of rings in one piece is two per
handle, by proof. No surface fails. The native step is conclusion 1: freezing contacts and reading which contacts need which rings gives
exactly the pieces of the cut surface, so the classical count of curves that leave a surface connected is read across time.

## Reading

**Interpretation, not a theorem.**
- **The genus is read across time.** A network of persistent contacts can count its handles: cut rings of contacts one after another and
  watch whether the needs between rings still hold the network together. The count at which it first falls apart is 2g + 1.
- **What the dynamics adds and what it does not.** Pieces need only the immediate needs at lag 1 and the absence of needs across a cut,
  so the count is the surface's, whatever the law does inside a piece. Full reach is where the dynamics shows: on the torus cut open,
  composition reaches every ring except on sides that are powers of two from 8.
- **For composed topology across time.** Adjacency, native paths, separation and now the genus of the surface the contacts make are
  read in one substrate, with distance still waiting on the owner.
- **Given, not grown.** The networks are given, not grown from a law.
- **Not a metric.** Counting rings of cuts counts independent cycles; no length or distance is formed.

## Lag cutoffs and census-only claims

- **This epic used no census and no lag cutoff.** Walk counts and rows of M^T are followed until the next row lies in the span of the
  earlier ones; the witnesses of the genus-2 networks are read from rows of M^T until they repeat.
- **Census-only claims elsewhere** stay as `LATTICE-NET-20261108-001` listed them: the lag-300 and lag-400 persistence counts of
  `LOOP-NET-20261108-001B` and `LOOP-ANY-20261108-001B`.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The pieces are read exactly (1) | square tori of side 9 and 10, the 7 × 7 double cover, and genus 3: a 56-ring network on the Klein quartic map {7,3} (rotations from PSL(2,7)) | pass: no mismatch on 48 cut sets |
| Two per handle (2) | the same networks | pass: the most is 2, 2, 4 and 6 |
| Full reach after cutting both ways (4) | sides 18, 19 and 20 | pass: every uncut contact needs every ring |

The genus-3 network has every return count even, so its contacts persist at every lag as well.

## Literature and provenance

- **Sources.** Cut graphs and tree–cotree decompositions on surfaces (Mohar and Thomassen, *Graphs on Surfaces*; Eppstein 2003); regular
  maps (Coxeter and Moser): the Möbius–Kantor map {8,3} and its dual {3,8} on genus 2, the Klein quartic map {7,3} on genus 3.
- **Classification.** Known-with-delta. The count 2g is classical; the delta is reading it through which contacts need which rings
  after freezing contacts.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags), A38 (a cut freezes a contact).
- **Scope.** Networks of rule-60 rings with law (12, 12) contacts on closed orientable surfaces.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with seven checks.
- **Administrative.** This note and the closure.

## Pending the owner

- **Counted length as a native magnitude**, which gates distance across time; put to the owner by the coordinator.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — genus read by rings of cuts | **Status:** Successful | Two per handle, by proof, on every surface; no surface fails |
| Local direction — composed topology across time | Research directions | Adjacency, paths, separation and genus hold across time; distance waits on the owner |
| Broader exploration — G5 with G1 | Known alternatives | Full reach after cuts (the powers of two); which lattices compose everywhere; growing a lattice from a law (G1); B13, B14 |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | A network of persistent contacts reads its surface's genus across time |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** none added.

- **What the attempt leaves open.**
  - Why full reach after cutting fails exactly on sides that are powers of two from 8.
  - Whether a law can grow such a network itself, so that the surface and its genus are made rather than given (G1).
- **The missing bridge to the program's composed topology.** Distance across time, which waits on the owner, and a network whose surface
  the law makes.

**Next step:** Research directions — the epic's question is answered on every surface; the line has reached the end of the order that
does not wait on the owner.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Grow a network of rings from a law (G1, with G5) | 3/3 — Major | 1/3 — Stated | Ask which local rule for adding rings and contacts keeps every contact persistent, starting from LOOP-NET's flip criterion → a growth rule whose networks stay regular, or the first obstruction | Alternative · deferred |
| 2 | Full reach on the cut-open torus (G5) | 2/3 — Substantial | 3/3 — Ready | Prove that on the n × n grid every contact needs every ring unless n is a power of two of at least 8, by the powers of x + 1/x + y + 1/y with walls → a theorem, or another exception | Alternative · deferred |
| 3 | Distance across time | 3/3 — Major | 1/3 — Stated | Waits on the owner's ruling on counted length | Alternative · deferred |
| 4 | Which lattices compose everywhere (from `LATTICE-NET-20261108-001`) | 2/3 — Substantial | 3/3 — Ready | Rectangular, triangular and honeycomb tori | Alternative · deferred |

1. **Growing the network.**
   - **Payoff 3.** It would turn a given surface into one a law makes, the program's question 9 across time.
   - **Concreteness 1.** No growth rule is in hand; the flip criterion says what a grown network must satisfy.
   - **Uncertainty.** Whether any local growth rule keeps the symmetry that persistence needs.
2. **Full reach.** Narrower and ready; the powers of two are the pattern to explain.
3. **Distance.** Waits on the owner.
4. **Which lattices.** Ready; it maps where composition reaches.

**Recommendation.** Research directions. The process line has run seventeen epics today and has reached the end of the program's order
short of distance, so this is a natural place to pause until the owner rules on counted length; if it continues, direction 2 is the
ready one and direction 1 the bigger one.
