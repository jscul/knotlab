# Distance across time

Epic `DISTANCE-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `LATTICE-NET-20261108-001` and `GENUS-CUT-20261108-001` built adjacency, native paths, separation and genus
  across time in networks of rings, and left distance to the owner's ruling on counted length. On 2026-11-08 the owner ruled: "I
  think yes, length can count as magnitude. We should be willing to explore things like this without getting my approval first." The
  coordinator relayed the direction the same day.
- **The question.** Does a network of persistent contacts read a distance across time natively? Is there a native reading (the first
  lag at which a contact needs a ring, contacts counted along a route, disjoint cuts) that behaves like a length or a metric, and does it
  match graph distance on the lattices?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Counted length is read by the substrate (A40 confirmed).** Along a route isolated by freezing every contact off it, the far contact first needs the near ring g·L + 1 lags after the start, L the route's contacts and g the spacing, and these lags add when routes are joined. At unequal spacing the lag is 1 plus the cells the route carries. | frozen test, exact: 2,250 routes, 7,285 splits, 372 routes at unequal spacing; proved for every network | A, B |
| 2 | **Time of flight.** The earliest lag at which any freeze makes a contact need a ring is 1 plus the fewest cells of a route between them, g·δ + 1 with δ the contact graph's directed distance. δ is a directed metric between contacts, not symmetric: influence goes one way round every ring. | proved; checked at the cell level on 18,052 pairs | B |
| 3 | **Cut counts.** The most pairwise disjoint freeze sets that leave two rings in different native pieces is the ring graph's distance D, on every network. The most that block a contact from a ring for good is δ. | proved; checked on 5,164 and 2,308 cuts | B |
| 4 | **Composition along a route.** An isolated route with no other arcs among its contacts composes at the recurring lags its dynamics fixes (A37): the far contact needs the near ring exactly when C(T − L − 1, own cells + m) is odd for some m below the near corner's own cells, every route contact persists, and the first composing lag is conclusion 1's. | proved; checked at the cell level on 502 routes | B |
| 5 | **The plain first need is the cone filtered by parity.** Without freezing, a contact first needs a ring at the directed distance exactly when an odd number of shortest routes arrive from one of the ring's contacts, and later or never otherwise. On the square torus, for contacts of one kind at offset (a, b), it is on time exactly when a AND b = 0 (Lucas); on the plane it never comes at offsets with v2(a) = v2(b), a third of them. It is not a metric. | proved; triangle counts computed | B |
| 6 | **Against graph distance on the lattices.** From a contact to its translate, δ = (m/2)·D on the square, triangular and honeycomb lattices (m = 4, 6, 3 contacts per ring). From a ring to a contact, D = ⌈δ/2⌉ on the square lattice (proved), D = ⌈δ/3⌉ on the triangular (computed to side 12), and ⌈3D/2⌉ − 1 ≤ δ ≤ ⌈3D/2⌉ on the honeycomb (computed to side 11). | proved; computed where marked | B, stress test |

## Answer

Yes, in two exact forms. **Counted contacts**, read as the most disjoint cuts that separate two rings into native pieces, are the ring
graph's distance D on every network, by proof. **Counted lags**, read as the earliest need any freeze allows (the time of flight) or as
the most disjoint sets that block for good, are the contact graph's directed distance δ, a directed metric; it equals (m/2)·D between
translates on all three lattices and D = ⌈δ/2⌉ on the square lattice, by proof. The plain first need without freezing is the same
light cone filtered by the parity of the number of shortest routes: on time on the Platonic, genus-2 and genus-3 networks, late or
absent on the lattices, and not a metric. The coordinator's expected shape holds, with two refinements: the cut count that matches
graph distance is the pieces reading, and the blocking reading gives δ, not D.

## Reading

**Interpretation, not a theorem.**
- **Distance across time is native.** The program's order was adjacency, paths, separation, then distance. All four are now read in one
  substrate across time, with distance counted (A40): a network of persistent contacts measures how far apart its rings are by the
  most cuts that separate them, and how long influence takes by the earliest need a freeze can arrange.
- **Two lengths, not one.** The cut length counts rings crossed and is symmetric. The time length counts cells along the flow and is
  directed, because rule 60 and law (12, 12) read leftward and influence goes one way round every ring. At equal spacing they are
  comparable within a factor fixed by the lattice (m/2 between translates).
- **Freezing does real work.** Without it the lengths are filtered by the parity of route counts: where shortest routes pair up the
  substrate reads nothing at the distance. The symmetry that makes returns cancel, which keeps contacts persistent
  (`LOOP-NET-20261108-001A`), is the symmetry that makes routes cancel; at random spacing the plain first need almost always meets the
  cell length (98% to 100% of pairs), but no contact keeps its witnesses (computed). Reading distance through cuts is recorded as A41.
- **Polygons, not circles.** The lattices read a taxicab, a hexagonal and a three-step honeycomb length. Their balls are polygons, as the
  periodic laws' were (`LOGIC-CIRCLE-20261107-001`).
- **Given, not grown.** The networks are given, not grown from a law.

## Lag cutoffs and census-only claims

- **No lag cutoff in the theorems' checks.** Walk counts follow rows of A^k until the next lies in the span of the earlier ones;
  cell-level readings stop at the lag a theorem names or follow rows of M^T to their span.
- **Census-only.** The triangular and honeycomb bands for rings and contacts (sides 4 to 12 and 3 to 11); the triangle-inequality
  counts; full reach on honeycomb tori (below); unequal spacing to lag 300.
- **Full reach on honeycomb tori (computed).** Ring to ring, every ring needs every ring on sides 3, 6, 9 and 12; on sides 4, 5, 7, 11
  and 13 each ring never needs exactly one ring, and on sides 8 and 10 thirteen. So full reach appears to hold exactly when 3 divides
  the side, unlike the square torus, where the side's parity decides (`LATTICE-NET-20261108-001A`).

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| A40's frozen test (conclusion 1) | routes of 11 and 12 contacts at spacing 5 on the square torus of side 8 and the Klein quartic network | pass: 18 of 18 |
| D = ⌈δ/3⌉, triangular (6) | sides 11 and 12 (checked to 10) | pass |
| The honeycomb band (6) | sides 10 and 11 (checked to 9) | pass |
| Translates (6) | square 11, 12, triangular 10, 11, honeycomb 9, 10 | pass: 194,360 pairs |
| Square closed forms and D = ⌈δ/2⌉ (5, 6) | sides 14 and 15 (checked to 13) | pass |
| Honeycomb full reach (census) | sides 6, 8, 10 to 13 (checked on 3, 4, 5, 7, 9) | extends the pattern: none on 6 and 12, one on 11 and 13, thirteen on 8 and 10 |

The script is `stress_test.py` beside this note, its output `stress_test.json`.

## Literature and provenance

- **Sources.** The most disjoint s–t cuts equal the s–t distance (Robacker 1956; Fulkerson's max-potential min-work), the dual of
  Menger's theorem; light cones of additive cellular automata over GF(2) (Martin, Odlyzko and Wolfram 1984) and Pascal's triangle mod 2
  under doubling (Willson); Lucas' and Kummer's theorems; medial graphs of maps; the hexagonal norm on Eisenstein integers; regular maps
  from GL(2,3) and PSL(2,7) (Coxeter and Moser), the Klein quartic map {7,3}.
- **The coordinator's sandbox.** The coordinator relayed an independent computation from the published libraries (2026-11-08): the
  cone, the isolated lag g·δ + 1 at the cell level on 2,566 pairs, the square torus's closed forms and D = ⌈δ/2⌉, the pieces cut count
  D, and ring-to-ring triangle counts. Every number it reported that this epic also computed agrees.
- **Classification.** Known-with-delta. The min-max theorem, the walk counts and the parity criteria are classical; the delta is reading
  them across time as native lengths of networks of persistent contacts, and the parity filter as the price of persistence.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags), A38 (a cut freezes a contact), A40 (counted
  length is a native magnitude), confirmed here by its frozen test.
- **Added.** A41, distance across time is read through freezes.
- **Scope.** Networks of rule-60 rings with law (12, 12) contacts, no two corners of one length between the same two contacts.

## Ratio

Since the epic opened:
- **Substantive.** One frozen test (A), one proof (B) with twelve checks, one stress test.
- **Administrative.** The pre-registration, this note and the closure.

## Pending the owner

- None new: the ruling on counted length was given and is recorded as A40.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — distance across time | **Status:** Successful | Two exact native lengths, the cut length D and the time length δ, proved on every network; A40 confirmed by its frozen test |
| Local direction — composed topology across time | Research directions | Adjacency, paths, separation, genus and distance are read in one substrate; reading distance without freezing is open |
| Broader exploration — G5 with G1 | Known alternatives | Growing a network of rings from a law (the growth thread); full reach on honeycomb and cut-open tori; B13, B14 |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | A network of persistent contacts measures distance across time, natively and exactly |

**Corrections:** none. **Goals:** a G5 and G1 checkpoint (capability gained). **Assumptions:** A40 added and confirmed by its frozen
test; A41 added (distance across time is read through freezes).

- **What the attempt leaves open.** Which persistent networks read distance without freezing; why full reach on honeycomb tori follows
  3 dividing the side; the triangular and honeycomb bands as theorems.
- **The missing bridge to the program's composed topology.** A network whose surface and lengths a law makes, so that dimension and
  shape are read across time from a law, not from a given lattice.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Distance without freezing (G5) | 2/3 — Substantial | 3/3 — Ready | On orientably regular maps from small groups and on tori, find where every ring–contact plain first need is on time (all Platonic, genus-2 and genus-3 networks tested are; tori of side 5 on are not) → a criterion, or the first regular map that fails | Selected · awaiting go-ahead |
| 2 | Full reach on honeycomb tori (G5) | 2/3 — Substantial | 3/3 — Ready | Prove that a honeycomb torus has full reach exactly when 3 divides its side, by the powers of its three-term walk polynomial → a theorem, or the first side that breaks the pattern | Alternative · deferred |
| 3 | Distance in a grown network (G1, with G5) | 3/3 — Major | 1/3 — Stated | When the growth thread has a law that grows a network of rings, read its cut and time lengths and how their balls grow → a dimension read across time from a law, or the obstruction | Alternative · deferred |
| 4 | The triangular and honeycomb bands as theorems (G5) | 1/3 — Minor | 3/3 — Ready | Extend the proof of Theorem 5 from translates to rings and contacts → D = ⌈δ/3⌉ and the honeycomb band proved | Alternative · deferred |

1. **Without freezing.** Payoff 2: a native distance with no intervention would answer the brief's open wish and tell which networks
   read their own lengths plainly; Concreteness 3: the cone theorem reduces it to the parity of shortest-route counts, computable on
   any map. Main uncertainty: whether the regular networks' success is only small diameter.
2. **Honeycomb full reach.** Payoff 2: it maps where composition reaches, with LATTICE-NET's antipode and FULL-REACH's powers of two;
   Concreteness 3: the census fixes the statement. Uncertainty: the sides 8 and 10 with thirteen misses may need a second mechanism.
3. **Grown networks.** Payoff 3: dimension and shape across time from a law are the program's question 9 in time; Concreteness 1: it
   waits on the growth thread's law.
4. **Bands.** Payoff 1: a sharpening of computed bounds; Concreteness 3: the pivot argument carries over.

**Recommendation.** Research directions, selected #1, awaiting the coordinator's go-ahead within the thread cap; stop it at a
criterion or at the first regular map whose plain first need is late.
