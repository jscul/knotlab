# Growth as a law: a beginning is a knot, and growth needs a shared coin

Epic `GROWTH-LAW-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner approved backlog B1 of the goals doc on 2026-11-08, together with B2. B1 serves G5 (question 4 of
  `docs/KNOT_INTUITION.md`, dynamics) and G1 (question 9, space from a law).
- **The question.** What can a growth order add to a law that a static law cannot, read with the canonical test? K1–K3 is
  applied to allowed states, and no scheduler may supply an input. B1 recorded three working hypotheses:
  - the order never knots with a world's states;
  - a kept history's local part is bounded, while its beginning is not certified by any bounded witness;
  - a beginning alone does work, even in one dimension.
- **The same muscle in the plane.** `GROW-COIN-20261107-001` found that label-free accretion of knot spheres keeps the roundness
  witness. `PINWHEEL-ATLAS-20261107-001C`, outward growth of the bare pinwheel patch, was retired there as backlog and is taken up
  here as ticket B.
- **Assumptions it bears on.** It is the challenge that A14 (a growing law's history is a hidden witness) names, and it tests the
  growth clause of A4, both in `docs/ASSUMPTIONS.md`.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The order never knots with the states.** For a growth rule that reads only the law, the joint law of history and states on a fixed world is a product, so no knot joins them. When worlds vary, with absent things forgotten and constraints accumulating, every knot that contains an order variable also contains an existence variable, and the knots on states alone are the seed's. Existence enters as a presence literal: "if this site grew, its knot holds" is itself a knot. A rule that reads a state does knot the order to the states, and that is the input the canonical test forbids. | proved; computed with controls | A |
| 2 | **A beginning is a knot.** The local history, at most one parent per knot, is 2-CNF and holds no knot. The knots of "time has no loop", the acyclic orientations of the world's knot graph, are exactly its cycles, each the not-all-equal relation on its seams. So on a ring the beginning is one knot binding every seam, and it contradicts the local history. On a tree the local history gives exactly one beginning. Three events' order is NAE_3. The states knot along cuts and the history along cycles, the circuits of a graph's two dual matroids. | proved; computed on rings, threads, K4, the prism, K3,3, the cube and the Petersen graph | A |
| 3 | **Euler's count.** Along any growth order, the steps' changes of the Euler characteristic sum to the world's. Beginnings and ends add one each, closing moves subtract one each, and sprouts and disc moves add nothing. So sprouting builds only trees, disc moves only discs and spheres, and a ring or a handle needs closing moves. The open-end rule grows only threads. | proved; computed | A |
| 4 | **The beginning does work in one dimension.** A radius-r law with k hidden labels that allows a thread of (2r + 1)k^(2r+1) + 2r + 3 knots allows a ring, while the open-end rule never grows one. So no bounded static witness does what the beginning does; it costs about log n bits per knot. In two dimensions a law excludes flat tori exactly when its flat configurations are aperiodic, and the seam law of `SPHERE-GROWTH-20261107-001` allows every flat torus. | proved; computed on 3,600 random laws | A |
| 5 | **The pinwheel grown by its own law leaves the pinwheel at once.** Label-free outward growth from one tile, completing collars with the 108 complete collars and coins at choices, left the pinwheel's patches in all 70 runs and all four declared orders. bfs, random and finger growth dead-ended in every run, within 18 to 304 tiles. Forced-first growth dead-ended in 6 of 10 runs, and the other 4 reached 500 tiles of collar-legal patches that are not pinwheel patches. Growth that follows a genuine pinwheel patch is never rejected. | exploratory experiment | B |
| 6 | **The first wrong move is always a coin.** Replaying ticket B's 70 runs exactly, the first move that left the pinwheel's patches was always a choice, never a forced move, at move 2 to 73 (median 6). At it exactly one option was right in 59 of 70 runs (1 of 2 in 35). The error was carried 0 to 145 moves before the run ended, with the dead tile 1 to 19 tiles away (median 3). | exploratory experiment | C |
| 7 | **Few real bits, many apparent ones.** An oracle keeping only the right options grew 1,000 tiles in all 15 runs and never stuck. After the seed's 54-way choice, 693 of its 775 choices had a single right option. It supplied 4.0 to 9.6 bits against 45.7 to 88.1 bits of apparent choice, so coins stay inside the pinwheel to 1,000 tiles with probability 2^−41 to 2^−82. The real choices thin out as the patch grows: 37 of 82 within the first 60 tiles, 12 after 400. | exploratory experiment | C |
| 8 | **A stronger local law does no better.** With the radius-2 atlas added to the collar law, 40 of 40 runs dead-ended, within 18 to 214 tiles. 35 stopped at exactly the collar-law run's size, 5 sooner, none later. Its replay control passed. | exploratory experiment | C |

## Answer

- **A growth order never knots with the world.** Written into the law, it adds a history whose local part is pairwise and whose
  global part, time without a loop, is a knot on every cycle. On a ring that knot is the beginning: one not-all-equal relation
  over every seam.
- **What growth adds.** Never a knot of the world. It adds only whether a world has a history from a beginning.
  - **In one dimension** that is everything. The open-end rule grows the number line in every order, and no static law with
    bounded hidden labels can tell its threads from rings. The number line's ends come from its beginning.
  - **On spheres** the beginning is free, since every two-sphere can be grown by disc moves. So what growth adds there is a
    bounded witness, `GROW-COIN-20261107-001`'s carried bit.
  - **In the round plane** growth cannot stand in for the hidden structure. Grown outward by its own label-free law, the pinwheel
    left its patches in every run. The first wrong move is always a coin. An oracle needs only 4 to 10 real bits to grow 1,000
    tiles past the seed, against 46 to 88 bits of apparent choice. A stronger local law gets stuck the same way.

## Reading

**Interpretation, not a theorem.**
- **For question 4.** A process written as a law is a static law on its history, so the static definition survives the change.
  The order is part of the allowed states, and its knots are read by K1–K3 like any others. They never reach the world's states.
- **A beginning is a knot.** A history splits along the program's own two/three boundary.
  - Its local part, which neighbour came first, is pairwise.
  - Its global part is constrained as a whole and free in every part, on every cycle of the world.
  - The open-end rule grows trees, whose histories are wholly pairwise. That is why its growth needs nothing global, and why it
    never closes a ring.
- **States and history are dual.** The world's states knot along cuts, and its history along cycles. The two are the circuits
  of a graph's two dual matroids, and they never knot with each other.
- **Growth needs a shared coin, on spheres and in the plane.**
  - **Spheres.** `GROW-COIN-20261107-001` found that the four equator corners must agree on one bit that no local window shows.
  - **The plane.** The pinwheel's growth needs a few bits of hierarchy, roughly one at each new level the patch reaches. Every
    tile of the growing boundary must respect them, and nothing local shows them. Independent coins at the boundary break them
    within a few choices. By 1,000 tiles nine choices in ten have a single right option, and the oracle's 4 to 10 bits are all a
    coin would need to get right.
- **A harmony is what grows in every order.**
  - **The theorem.** Dworkin and Shieh prove that every aperiodic protoset of the plane has deceptions of all orders. So a growth
    rule that inspects a bounded neighbourhood and never gets stuck, in any order, belongs to a law with a periodic tiling.
  - **The circles.** Periodic laws have polygonal circles with rational π (`LOGIC-CIRCLE-20261107-001`).
  - **So,** in the owner's words, a law that can always keep growing has a harmony among its spaces. The round circle, a ratio
    that continues, needs information that local growth cannot share.
  - **Its scope.** This is a corollary of two theorems for tilings by finitely many prototiles up to isometry. It is read here
    for the program's laws, not proved for them.

## Stress test

One size past each computed claim (`stress_test.py`, `stress_test_growth.py` and `stress_test_c.py` here, with their outputs). Each
reuses the tickets' own code. The 1,500-tile oracle finished after the epic's commit and was folded in by a follow-up commit.

| Claim | One size past | Result |
| --- | --- | --- |
| The knots of time without a loop are the cycles (A; enumerated on K4, the prism, K3,3, the cube) | K5, the Wagner graph and the Petersen graph, enumerated; a doubled seam | pass: 37, 29 and 57 knots, exactly the cycles; the doubled seam is a tie |
| Pumping at radius 1 (A; k = 2, 3) | k = 4 labels, 300 random laws (bound 197) | pass: all 298 laws with a thread at the bound have the proof's ring |
| Theorem 1(b) on sites −2..1 (A) | sites −2..2 and −3..2, the identity itself (shadow on order and states = Full × the seed's law) | pass with absent bits free; fails, as it should, with them set to 0 |
| Disc growth never sticks on K_m, m ≤ 5 (A) | m = 6, 7 | pass: one beginning, one end, never stuck in 30 runs each |
| Rings n ≤ 10 (A) | n = 11..14 | pass |
| Every coin run of the collar law leaves the pinwheel (B; seed of handedness +1, seeds 1..20) | The mirror seed (handedness −1), bfs and random, seeds 1..10; 20 more bfs seeds (21..40) | pass: 20 of 20 mirror runs and 20 of 20 new runs dead-ended, within 29 to 398 tiles; no new patch embeds |
| Four forced runs reached 500 tiles off the pinwheel (B) | The same four continued to 1,000 tiles | 3 of the 4 then dead-ended (at 543, 673 and 979 tiles); one reached 1,005 tiles, still off the pinwheel, with 89 of 1,118 interior darts breaking the radius-2 atlas |
| The radius-2 law gets stuck too (C; bfs and random) | The forced-first order, seeds 1..10, where the collar law alone let 4 runs wander 500 tiles off the pinwheel | pass: 10 of 10 dead-ended, within 124 to 309 tiles, with no interior dart off the radius-2 atlas; the four wandering seeds now stop at 124 to 309 tiles (`stress_test_c_partial.jsonl`) |
| Few real bits (C; oracle to 1,000 tiles) | The oracle to 1,500 tiles, bfs seeds 1..3 (run after the epic's commit, under the owner's rule of 2026-11-08 that long stress tests do not block progress) | pass: all three reached 1,500 tiles inside the pinwheel; from 1,000 to 1,500 tiles the real bits after the seed stayed at 8.3 and 7.2 for seeds 1 and 2 and rose from 6.2 to 7.2 for seed 3 (one more free choice, at 1,167 tiles), while the apparent bits rose by 16 to 29 (`stress_test_c.json`) |

## Correction (2026-11-08)

Logged in `docs/CORRECTIONS.md` as a narrowing, after publication, when `COLLAR-PLANE-20261108-001` found a periodic plane that obeys
the collar law. As first published, ticket B's status and conclusion 8 of the closure called the dead ends "consistent with Dworkin
and Shieh (1995)", and "Next steps" said the local direction "is exhausted in the sense of Dworkin and Shieh", so that a stronger
local law "changes when growth fails, not whether some order fails".
- **What is true.** Dworkin and Shieh's theorem is about aperiodic sets of tiles. Neither the collar law nor the radius-2 law is one:
  the rhombus lattice (four tiles around a common right angle, translated) obeys the collar law after one cut and the radius-2 law
  after two ([collar plane](../COLLAR-PLANE-20261108-001/collar_plane.md)). So the theorem says nothing about whether some growth
  order of these laws must fail, and the dead ends measured here are facts about coin growth, not consequences of aperiodicity.
- **"A harmony is what grows in every order"** stays true as stated: a law whose growth never gets stuck in any order has a periodic
  tiling. The pinwheel's undecorated laws have one, so the reading does not set them apart.
- **What stands.** Every measurement of tickets B and C: all 70 coin runs left the pinwheel, the first wrong move is always a coin,
  the oracle's real and apparent bits, and the radius-2 arm's 40 dead ends. Ticket A is unaffected.

## Literature and provenance

- **Ticket A.**
  - **Sources.**
    - **Products** have their minimal dependent sets inside one factor (folklore).
    - **Acyclic orientations** are the topes of a graph's oriented matroid. A set is independent exactly when the topes restricted
      to it take every sign vector, and a circuit misses just its two signatures (Björner, Las Vergnas, Sturmfels, White and Ziegler,
      *Oriented Matroids*, 1993).
    - **Euler's count** is the weak Morse equality of discrete Morse theory (Forman, 1998). Every triangulated 2-sphere is shellable
      (Steinitz; Bruggesser and Mani, 1971).
    - **Pumping.** One-dimensional shifts of finite type have periodic points. Certifying trees and paths takes logarithmic labels
      (proof-labeling schemes: Korman, Kutten and Peleg, 2010; Göös and Suomela, 2016).
    - **Aperiodic tile sets** forbid every torus in two dimensions (Berger, 1966; Robinson, 1971; Socolar and Taylor, 2011).
  - **Classification.** Known-with-delta, folklore-level as mathematics. The delta is the reading under K1–K3:
    - the order never knots with the states;
    - a history's local part is pairwise and its global part is a knot on every cycle, dual to the states' knots on cuts;
    - the open-end rule and the knot spheres as instances.
- **Tickets B and C.**
  - **Sources.**
    - **Deceptions.** Penrose (in *Aperiodicity and Order 2*, ed. Jarić, 1989) showed deceptions for Penrose tiles. Onoda, Steinhardt, DiVincenzo and Socolar (1988) grew perfect
      Penrose tilings by forced moves from a seed with a decapod defect. Dworkin and Shieh (*Comm. Math. Phys.* 168, 1995) prove that
      every aperiodic protoset of the plane, rotated copies allowed, has deceptions of all orders. Jeong (2007) found a 3D way around
      them for decagonal quasicrystals.
    - **The pinwheel's rules.** Matching rules with decorations for the pinwheel are due to Radin (1994), and collared tiles to
      Anderson and Putnam (1998).
  - **Not found.** Any study of growing the pinwheel. Also not found: its undecorated collar law used as a growth rule, the
    measured deceptions, and the oracle's count of real against apparent choices.
- **Where the ideas came from.** The doctrine questions (what an order may add, what a beginning is) are the program's own. The
  pinwheel experiments reuse `PINWHEEL-ATLAS-20261107-001A`'s collars and atlas. Dworkin and Shieh was found by a prior-work search
  during ticket B, after its runs had started.

## Workspace assumptions

- **Relied on.**
  - **A3, A4 and A6.** Verdicts come from allowed states, nothing supplies an input, and erasure is forgetting.
  - **A13.** Witnesses belong to the law.
  - **A23.** The atlas's rooted codes, for the radius-2 check.
  - **A24.** The pinwheel law fixes its map, so the atlas belongs to the law.
- **Challenged.**
  - **A14, a growing law's history is a hidden witness.** Confirmed for growth rules that read only the law, with absent things
    forgotten. Written into the law, a history is a witness. Its local part is bounded and pairwise, its global part is a knot per
    cycle, and it never knots with the states.
  - **A4's growth clause.** Supported. A growth order as variables of the law adds no input. Existence enters as the presence
    literal A4 prescribes, and a rule that reads a state is exactly the input A4 forbids.
- **Bears on.**
  - **A6.** Theorem 1(b) needs absent things forgotten. Fixing them instead makes order bits carry existence.
  - **A25, a law without hidden states cannot force roundness.** In the plane, the pinwheel's collar law, which has no hidden
    states, admits 500-tile collar-legal patches that are not pinwheel patches. These are finite, and they break the radius-2 law.
- **Taken by default.** Growth moves are judged by local consistency, with one step of lookahead (new entry A28). Ticket C's
  stronger arm tests one stronger law.

## Ratio

Since the epic opened:
- **Substantive.** Three evidence families changed conclusions: A (a proof), and B and C (exploratory experiments). Three
  stress-test passes, one size past each ticket's computed claims, also count as substantive.
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — what a growth order adds to a static law | **Status:** Successful | A beginning, which is a knot; never a knot of the world |
| Local direction — label-free growth of round spaces | Practically exhausted | Spheres need a carried bit; the pinwheel leaves its patches at once |
| Broader exploration — G5 and G1 lines | Known alternatives | Loops whose states change in time; the collar law's non-pinwheel patches |
| Long-term goal — G5 Dynamics (question 4), with G1 Space from a law | Capability gained (G5); obstruction learned (G1) | The static definition survives growth; round space needs shared hidden bits |

**Corrections:** none. **Goals:** a checkpoint for G5 (capability gained) and G1 (obstruction learned); backlog B1 marked taken
and B7 parked; no goal change. **Assumptions:** A14 Confirmed; A28 added (outward growth is judged by its law's local
consistency); history lines on A4, A6 and A25.

- **What is left open.** Processes whose states change in time, the second half of question 4, were not studied: every process
  here builds a world, and none updates one.
- **The local direction.** It is exhausted in the sense of Dworkin and Shieh. A stronger local law changes when growth fails, not
  whether some order fails, and ticket C's radius-2 arm shows this on the pinwheel.
- **The missing bridge to G1.** A law that lays out a round space natively, which the evidence says needs hidden information
  shared across the growing boundary.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Knots across time (G5) | 2/3 — Substantial | 2/3 — Testable | Space-time knots of rules 60, 90 and 150, one nonlinear rule, and Life → a classification, or a dynamics with no temporal knot | Selected · awaiting go-ahead |
| 2 | The collar law off the pinwheel (G1, A25) | 2/3 — Substantial | 2/3 — Testable | Translations in the 500-tile non-pinwheel patches, then a periodic search → a periodic collar-legal plane, or none to a declared size | Alternative · deferred |
| 3 | One bit per level (G1, G6) | 1/3 — Incremental | 3/3 — Ready | Oracle growth to 4,000 tiles; real bits against levels spanned → a fit, or bits that do not follow levels | Alternative · deferred |
| 4 | Every accretion law (G1) | 2/3 — Substantial | 1/3 — Stated | A deception argument for spheres → a theorem, or a law that escapes | Alternative · deferred |
| 5 | Challenge A12, bond distance (backlog B4) | 2/3 — Substantial | 2/3 — Testable | Chain distance beside bond distance on the measured laws → agreement, or the first law where they differ | Alternative · deferred |

1. **Knots across time.**
   - **Payoff 2.** It would answer question 4 for processes that change states, the half this epic leaves.
   - **Concreteness 2.** Ledrappier's law is rule 60's space-time law, and its knots are measured (`LOGIC-AXIS-20261107-001B`). K1–K3
     applies to space-time laws directly. The owner suggested Conway's Life as the picture of emergence on 2026-11-08, and knotlab's
     lesson 1.3 already reads a Life history as an allowed state.
   - **Uncertainty.** Whether nonlinear rules have temporal knots worth classifying.
   - **Status.** Bound: one epic. Not started: it is parked as backlog B7, awaiting the owner's go-ahead under the wrap-up request.
2. **The collar law off the pinwheel.**
   - **Payoff 2.** A periodic collar-legal plane would answer the atlas epic's open question at radius one: the undecorated law would
     not force aperiodicity there (A25).
   - **Concreteness 2.** Forced growth built four 500-tile patches off the pinwheel. Continued to 1,000 tiles, three of them got
     stuck and one reached 1,005, so most are deceptions rather than another plane.
   - **Uncertainty.** Whether any collar-legal plane is not a pinwheel.
3. **One bit per level.**
   - **Payoff 1.** It refines ticket C's count.
   - **Concreteness 3.** The oracle exists. The real bits should track the number of hierarchy levels a patch spans, about
     log base √5 of its radius.
4. **Every accretion law.**
   - **Payoff 2.** It would settle `GROW-COIN-20261107-001`'s deferred theorem.
   - **Concreteness 1.** No completion argument is in hand. Dworkin and Shieh cover the plane, not closed spheres.
5. **Challenge A12.**
   - **Payoff 2.** It is the register's most-used untested measure.
   - **Concreteness 2.** The laws and their code exist (backlog B4).

## Final report as sent

Sent to the owner on 2026-11-08 at 07:15 UTC and copied here verbatim.

**Growth as a law is closed and published.** See the [decision note](https://github.com/jscul/knotlab/blob/main/research/GROWTH-LAW-20261107-001/growth_law.md) and the [proof](https://github.com/jscul/knotlab/blob/main/proofs/GROWTH-LAW-20261107-001A/GROWTH-LAW-20261107-001A-P001_a_beginning_is_a_knot/proof.md).

- **A beginning is a knot (proved).** A growth order never knots with a world's states. Written into the law, its local part (which neighbour came first) is pairwise. Time without a loop is one knot per cycle of the world. In one dimension the beginning does what no bounded static witness can: no bounded law tells a long thread from a ring.
- **The plane needs a shared coin (measured).** Grown outward by its own label-free law, the pinwheel left its patches in all 70 runs, and the first wrong move is always a coin. An oracle needs only 4 to 10 real bits to reach 1,000 tiles, against 46 to 88 apparent ones. A stronger radius-2 law gets stuck too.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: what a growth order adds | **Status:** Successful | A beginning, which is a knot; never a knot of the world |
| Local direction: label-free growth of round spaces | Practically exhausted | Spheres need a carried bit; the pinwheel leaves its patches at once |
| Broader exploration: G5 and G1 lines | Known alternatives | Loops whose states change in time; the collar law's non-pinwheel patches |
| Long-term goal: G5 Dynamics, with G1 Space from a law | Capability gained (G5); obstruction learned (G1) | The static definition survives growth; round space needs shared hidden bits |

**Corrections:** none. **Goals:** checkpoint for G5 and G1; B1 marked taken; B7 parked. **Assumptions:** A14 confirmed; A28 added (growth judged by local consistency); history lines on A4, A6 and A25.

**Next step:** Continue, selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Knots across time (G5) | 2/3 Substantial | 2/3 Testable | Space-time knots of rules 60, 90, 150, a nonlinear rule and Life → a classification | Selected · started |
| 2 | The collar law off the pinwheel (G1) | 2/3 Substantial | 2/3 Testable | Periodic search seeded by the non-pinwheel patches → a periodic plane, or none | Alternative · deferred |
| 3 | One bit per hierarchy level | 1/3 Incremental | 3/3 Ready | Oracle to 4,000 tiles → bits follow levels, or not | Alternative · deferred |
| 4 | Every accretion law (G1) | 2/3 Substantial | 1/3 Stated | A deception argument for spheres → theorem | Alternative · deferred |

#1 asks the other half of question 4, loops whose states change in time. I'm starting it now, because the coordinator confirmed that wrap-up mode has ended. One stress test, the oracle grown to 1,500 tiles, is still running. It is logged in the new docs/LONG_RUNNING.md, and its result will be folded in when it ends.
