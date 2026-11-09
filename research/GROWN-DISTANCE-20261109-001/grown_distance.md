# Distance in a grown network

Epic `GROWN-DISTANCE-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** Backlog B19, distance in a grown network, parked by `DISTANCE-20261108-001` until a law grew networks of
  rings. The band law does: it makes the torus from a loop and grows it, every stage balanced (`BAND-SURFACE-20261108-001`,
  `GROW-NET-20261108-001`), and bands make only the torus (`GENUS-BAND-20261108-001`). The coordinator opened it on 2026-11-09: start with
  the grown torus.
- **The question.** Does the torus that growth produces read distance the way the fixed torus does, by the cut length D and the time
  length g·δ + 1 with freezing (`DISTANCE-20261108-001`) and by the plain first need without it (`PLAIN-TIME-20261108-001`), and how do the
  balls of both lengths grow as it grows?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Every stage reads both freeze lengths.** The loop, the n × 2 ladder and every n × m torus read the cut length D and the time length g·δ + 1 exactly, and on the ladder and tori D = ⌈δ/2⌉. | proved; checked at the cell level | A |
| 2 | **The ladder reads distance plainly.** Every square torus whose lattice holds (2, 0) or (0, 2), the band law's n × 2 ladder and its twisted forms among them, is on time at every size: every contact needs every ring at the time length with nothing frozen. In the ladder's cover each ring's nearest contact has exactly one shortest route. | proved; checked to n = 200, at the cell level to 12 | A |
| 3 | **From the second band on, freezing is needed.** The n × m torus (2 ≤ n ≤ m) is on time exactly when n = 2 or n = m = 3: a tube of girth 3 to 5 already holds the plane's late ring at distance 4. | proved | A |
| 4 | **Balls grow as in the plane out to half the loop, then linearly.** On the n × m torus the rings within ring distance r number Σ_b min(n, 2(r − \|b\|) + 1); on the cylinder this is 2r² + 2r + 1 up to r = (n − 1)/2 and grows by exactly 2n per step once 2r + 1 ≥ n. The time length's ball of radius 2r is the ring ball of radius r about the contact's two rings. | proved | A |
| 5 | **Thin tori of every shape read plainly too.** Reading every torus, not only the rotation-invariant ones: the ladders (195 of 195), the square tori holding (2, 1) or a rotation of it (191 of 191; their mirror images, holding (1, 2), only at index 5 to 9) and the triangular tori holding a vector of length √3 (232 of 232) are on time, and every other on-time torus is small (index at most 17, 21 or 9). The rotation-invariant ones are `PLAIN-TIME-20261108-001`'s 26. | computed: square to index 100, triangular to 80, honeycomb to 50; stress test to 140 and 110 | A, stress test |

## Answer

Yes for the freeze lengths, at every stage, by proof: growth by bands keeps the torus a network on which the cut length is the ring
graph's distance and the time length is g·δ + 1. Without freezing, only the first band reads its distance: the n × 2 ladder is on time
at every size, and every later stage is late except the 3 × 3 torus. The balls are those of a tube. They grow like the plane's out to
half the loop's n rings, then by 2n rings per step, so a stage reads dimension 2 at short range and dimension 1 at long range, and further
bands only lengthen the tube.

The epic also corrects `PLAIN-TIME-20261108-001`: its 26 tori are the rotation-invariant ones, and infinitely many thin tori read
distance plainly at every size (Correction below).

## Reading

**Interpretation, not a theorem.**
- **The grown torus is a tube.** The band law keeps the seed loop as the girth and lengthens the torus one band at a time (A43). Read
  across time through freezes, its balls are the plane's only out to half the loop. A law that grows a two-dimensional space would have to
  add bands both ways, and the law does not say which way to go.
- **Thin reads plainly, thick needs freezing.** On the ladder every level flip can be made through either rung, and the two walks cancel
  in pairs mod 2, so its walk parities are a loop's, and loops are on time. With girth 3 or more, the plane's first tie of two shortest
  routes, at distance 4, fits inside the tube. So the plain first need reads distance at every size exactly where the network is
  one-dimensional at large scale (loops, pairs of rings, the thinnest tubes) and fails wherever it is two-dimensional and not tiny.
  A41's reason stands in that form.
- **Chirality again.** A tube holding (2, 1) is on time at every index read, and its mirror image, holding (1, 2), is late from index 8,
  because influence goes one way round every ring.
- **Stages, not growth in time.** Each stage is read as a fixed network (A42). A network that grows while it runs is the next question.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Route counts are breadth-first and exact; least odd walk lengths follow rows mod 2 to their span (plain_lib);
  cell-level readings stop at the lag a theorem names.
- **Census-only.** Conclusion 5: the (2, 1) tubes and the √3 tubes are computed to index 100 and 80 (stress test to 140 and 110), not
  proved at every size, and the small on-time tori are read, not explained.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The (2, 1) tubes are on time (5) | index 101 to 140 (computed to 100) | pass: 80 of 80; their mirror images late, 80 of 80 |
| The √3 triangular tubes are on time (5) | index 81 to 110 (computed to 80) | pass: 90 of 90 |
| The ladders are on time (2) | n = 201 to 230, both twists (checked to 200) | pass: 60 of 60 |
| The rectangular tori (3) | 2 ≤ n ≤ 14, n ≤ m ≤ 60 (read to 10 × 40) | pass: on time exactly n = 2 and 3 × 3 |

The script is `stress_test.py` beside this note, its output `stress_test.json` and its log `stress_test_log.txt` (16 seconds).

## Literature and provenance

- **Sources.** Geodesic counts on strips and cylinders of the square lattice; Lucas' theorem; the systole lemma of
  `PLAIN-TIME-20261108-001B`, Theorem 3, applied with the cylinder as cover; growth of balls in Z × Z_n (linear, as for any virtually cyclic
  group); Hermite normal forms of sublattices.
- **Classification.** Known-with-delta. The ingredients are classical; the delta is which tori of every shape read distance across time
  without freezing, and what the band law's stages read.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A38 (a cut freezes a contact), A40 (counted length), A41 (distance read through
  freezes; its confirmation narrowed here).
- **Added.** A42, a grown network is read stage by stage; A43, bands are added along the seed loop.
- **Scope.** Equally spaced networks of rule-60 rings with law (12, 12) contacts; tori of the square, triangular and honeycomb lattices.

## Correction

`PLAIN-TIME-20261108-001B`, Theorem 4, said that every square, triangular or honeycomb torus other than its 26 is late. Its census built
only rotation-invariant sublattices, and the bound that made large tori late assumed the shortest lattice vector is at least √N long,
which holds for those alone. Ticket A, Theorem 2, proves the ladders on time at every size, and conclusion 5 computes two more families.
The 26 are the regular tori; "only the sphere reads distance plainly at every size" holds among regular maps. Logged in
`docs/CORRECTIONS.md` (2026-11-09, Narrowing), with a correction section in the decision note of `PLAIN-TIME-20261108-001` and a
qualification of `PLAIN-TIME-20261108-001-D001` on knotlab.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with seven checks, including the census of every torus; one stress test; one correction.
- **Administrative.** This note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — distance in the grown torus | **Status:** Successful | Every stage has a verdict for both freeze lengths and the plain first need, by proof, and the balls are in closed form |
| Local direction — distance in a grown network | Research directions | The stagewise reading is settled; a network that grows while it runs is open |
| Broader exploration — G1 with G5 | Known alternatives | Growth chosen by the dynamics (B23); handles from two bands at once (B22); the computed tube families as theorems |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | The band law makes a tube: dimension 2 only out to half its loop, and only its first stage reads distance without freezing |

**Corrections:** one, Narrowing: `PLAIN-TIME-20261108-001`'s 26 tori are the rotation-invariant ones; thin tori of every size read
distance plainly. **Goals:** a G1 and G5 checkpoint (obstruction learned), B19 marked taken. **Assumptions:** A42 and A43 added; A41's
confirmation narrowed.

- **What the attempt leaves open.** Whether a network that grows while it runs keeps its contacts and reads its lengths; which way a band
  should go, and whether the dynamics can say; the (2, 1) and √3 tubes at every size.
- **The missing bridge to the program's composed topology.** A law that grows both ways, so that the grown network reads dimension 2 at
  every scale, or a reason that no band law can.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Growth while running (G1 with G5; challenges A42) | 3/3 — Major | 2/3 — Testable | Insert one band into a running 3 × m tube, its cells new open distinctions from that lag; read the contacts' witnesses across the insertion and the first need across the new band, then a band every P lags → the lengths and balls of a network growing in time, or the insertion that breaks persistence | Selected · awaiting go-ahead |
| 2 | Growth chosen by the dynamics (B23; challenges A43) | 3/3 — Major | 1/3 — Stated | Let a contact's needs pick which way the next band goes → a law that fixes the dimension it grows, or none | Alternative · deferred |
| 3 | The thin tubes as theorems | 1/3 — Minor | 3/3 — Ready | Prove the (2, 1) and √3 tubes on time by the ladder's cover argument, and close the classification of every torus by the cylinder lemma for each short vector → a complete list, or a family the method misses | Handed to the thread on which finite maps rescue late rings (coordinator, 2026-11-09) |
| 4 | Handles from two bands at once (B22) | 2/3 — Substantial | 1/3 — Stated | Glue a band pair across the n × m torus as a handle → a balanced genus-2 network to read distance on, or none | Alternative · deferred |

1. **Growth while running.** Payoff 3: distance and balls read across time in a network that a law grows in time are B19's aim proper,
   and a horizon (rings never needed because bands arrive faster than influence crosses them) would be the first native reading of a
   growing space's causal structure. Concreteness 2: the cell-level simulator is linear and exact; the insertion rule needs one default,
   which old cell keeps the contact a band splits, to be registered. Main uncertainty: whether persistence survives any insertion.
2. **Growth chosen by the dynamics.** Payoff 3: a native choice of direction would decide whether a band law can grow a plane.
   Concreteness 1: no candidate rule yet.
3. **Thin tubes.** Payoff 1: completes the correction's classification. Concreteness 3: the ladder proof's method carries over. The
   coordinator gave it, with the reason chirality decides the (2, 1) tubes, to the thread on which finite maps rescue late rings.
4. **Two bands at once.** Payoff 2: the only route to higher genus left by `GENUS-BAND-20261108-001`. Concreteness 1: no candidate gluing.

**Recommendation.** Research directions, selected #1 within the thread cap; stop it at the first insertion schedule whose lengths and
balls are read exactly, or at the insertion that breaks persistence.

## Final report as sent

Sent to the owner on 2026-11-09 at 19:42 UTC and copied here verbatim.

**Distance in a grown network (B19) is closed and published.** The grown torus reads distance with freezing at every stage. Without freezing, only its first stage reads it. ([decision note](https://github.com/jscul/knotlab/blob/main/research/GROWN-DISTANCE-20261109-001/grown_distance.md))

- **With freezing (proved):** every stage of band growth reads the cut length D and the time length g·δ + 1 exactly.
- **Without freezing (proved):** the n × 2 ladder, the first band, is on time at every size. So is every square torus whose lattice holds (2, 0). From the second band on, every stage except 3 × 3 is late.
- **Balls (proved):** the band law makes a tube. Balls grow like the plane's (2r² + 2r + 1) out to half the loop, then by 2n rings per step. That is dimension 2 at short range and 1 beyond.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: the grown torus | Successful | Every stage has a proved verdict for both freeze lengths and the plain reading; balls in closed form |
| Local direction: distance in a grown network | Research directions | Stage by stage is settled; growth while the network runs is open |
| Broader exploration: G1 with G5 | Known alternatives | Growth chosen by the dynamics (B23); handles from two bands (B22) |
| Long-term goal: G1 Space from a law | Obstruction learned | The band law grows a line of loops, not a plane |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Growth while running (B24) | 3/3 | 2/3 | Insert a band into a running 3 × m tube; read persistence across it and the first need across it, then a band every P lags → lengths and balls of a network growing in time, or the insertion that breaks persistence |
| 2 | Growth chosen by the dynamics (B23) | 3/3 | 1/3 | Let a contact's needs pick the band's direction → a law that fixes the dimension, or none |
| 3 | Thin tubes as theorems | 1/3 | 3/3 | Handed to the rescued-maps thread |
| 4 | Handles from two bands (B22) | 2/3 | 1/3 | Glue a band pair as a handle → a genus-2 network, or none |

**Corrections:** one, Narrowing. Yesterday's "exactly 26 tori read distance plainly" holds only for regular tori. The ladders (proved) and two other thin families (computed to index 100 and 80, stress-tested past that) are on time at every size. It's logged in CORRECTIONS.md and knotlab's [HISTORY.md](https://github.com/jscul/knotlab/blob/main/HISTORY.md). **Goals:** G1 and G5 checkpoint; B19 taken, B24 added. **Assumptions:** A42 and A43 added (each stage read as a fixed network; bands added along the seed loop), and A41's confirmation narrowed.

I recommend #1 next.
