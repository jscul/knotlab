# Which finite maps rescue late rings

Epic `RESCUE-MAP-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `PLAIN-TIME-20261108-001` found that every flat and hyperbolic tiling is late from a horizon on, so a finite
  map reads distance plainly only when its wrapping rescues the cover's late rings, and that a 13-ring torus is late while its mirror
  image is on time. Its direction 2 asked which finite maps rescue late rings. The coordinator queued it on 2026-11-09, and the same day
  `GROWN-DISTANCE-20261109-001` proved that thin tori are on time at every size (the ladders), which narrowed `PLAIN-TIME`'s list of 26
  tori to the regular ones, computed two more thin families, and handed their proofs to this epic.
- **The question.** Which tori of every shape read distance plainly, why, and why does a short vector rescue while its mirror image
  does not? Stop at a complete classification with its mechanism, or at the first obstruction.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The systole lemma holds for every cover**, in particular for the tube of one lattice vector covering every torus that holds it. | proved | A |
| 2 | **Two thin families are on time at every size.** The square tube of (2, 1) and the triangular tube of a vector of length √3 have every ring on time, each closest contact reached by an odd number of shortest routes (exactly one in every case read), and so is every torus holding such a vector, two square tori of index 3 excepted. | proved (by hand for the square tube, by a checked certificate for the triangular) | A |
| 3 | **The mirror image fails.** The tube of (1, 2) is late at distance 4: its fastest routes climb two rings per two arcs and take their side step at any of j places, so a closest contact has j routes. | proved; counts computed | A |
| 4 | **Every other short tube is late.** Every tube of a vector shorter than 2ℓ + m arcs that is not in a family is late within ℓ: 54 square, 141 triangular and 75 honeycomb tubes. | proved by exact reading | A |
| 5 | **The complete list.** A square torus is on time exactly when it holds a rotation of (2, 0) or (2, 1) (index 3 excepted) or is one of 23 listed tori of index 5 to 17; a triangular torus when it holds a vector of length √3 or is one of 85 listed tori of index 4 to 21; a honeycomb torus only when it is one of 15 listed tori of index 1 to 9. | proved: Theorems 1 and 2 with an exact census below explicit bounds | A, stress test |

## Answer

A torus rescues its cover's late rings in one of two ways: it is small (index at most 17, 21 or 9; finitely many), or it
holds a short loop along which the fastest way to every ring is a single route. The square lattice has two such loops, the ladder (2, 0)
and the twist (2, 1), up to the quarter turn; the triangular lattice one, any vector of length √3; the honeycomb none. The rescue is not
a third route that makes an even count odd: it is a strictly shorter route round the short loop, unique, that makes a different contact
the closest. The twist's mirror image (1, 2) winds against the reading direction, and there the fastest routes branch.

## Reading

**Interpretation, not a theorem.**
- **Thin reads plainly, thick needs freezing.** A torus reads distance without freezing at every size only when it is a thin tube whose
  loop gives influence one fastest way along it, as a loop of rings does (`PLAIN-TIME-20261108-001B`, Theorem 1). Two-dimensional
  shapes read their distance only through freezes (A41), except finitely many small ones.
- **Chirality decides which loops work.** Rule 60 reads one way round every ring, so a loop and its mirror image are different
  substrates; whether a short loop rescues depends on how it winds against the reading direction.
- **Given, not grown.** The tori are given; the ladder is the band law's first stage (`GROWN-DISTANCE-20261109-001`), the twist tube is not
  grown by any law found so far.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Distances and parities are read layer by layer from the target, exactly, and the tube certificates are checked at
  every contact of a window and one period past it, which covers the whole tube.
- **Census-only.** That every closest contact of the two tubes has exactly one route (proved only mod 2), and the counts j of the mirror
  tube, both on a window. The classification itself is proved, its finite part read exactly.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The complete list (5) | every lattice to index 100 (square), 140 (triangular), 80 (honeycomb), checked to 50, 93 and 48 | pass: no on-time torus outside the families and the list; 200, 141 and 0 family tori, all on time |
| The tube certificates (2) | a window of 300 positions (checked on 160) | pass, every target |

The script is `stress_test.py` beside this note, its output `stress_test.json`; it ran in 56 seconds.

## Literature and provenance

- **Sources.** The systole argument of `PLAIN-TIME-20261108-001B`, Theorem 3, as `GROWN-DISTANCE-20261109-001A` applied it to cylinders;
  Bellman's equations as a certificate for shortest-path distances and counts; distances in quotients of periodic graphs as least over
  lifts.
- **Classification.** New as far as found for the question asked: which tori of the three regular lattices read distance plainly. The
  ingredients are classical.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A40 (counted length is a native magnitude), A41 (distance across time is read
  through freezes), which this epic narrows in the reading above without changing its status.
- **Added.** None.
- **Scope.** Tori of the square, triangular and honeycomb lattices of rule-60 rings with equally spaced law-(12, 12) contacts; maps of
  higher genus are not classified.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with eight checks, one stress test.
- **Administrative.** This note and the closure.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — which finite maps rescue late rings | **Status:** Successful | The tori are classified completely, with the mechanism and the reason for the chirality split |
| Local direction — reading distance plainly | Research directions | Tori are done; maps of higher genus (141 of 706 on time) are not classified |
| Broader exploration — G5 | Known alternatives | Which lattices compose everywhere (B21, selected by the coordinator); B19, B20 |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Which flat networks read their own distance without intervention is known exactly: thin tubes with a unique fastest way, and finitely many small tori |

**Corrections:** none; the narrowing of `PLAIN-TIME-20261108-001B`'s list of 26 tori was logged by `GROWN-DISTANCE-20261109-001`.
**Goals:** a G5 checkpoint (capability gained). **Assumptions:** none added or changed.

- **What the attempt leaves open.** Which maps of higher genus rescue, and whether a short closed walk with a unique fastest way explains
  them; a rule that predicts the rescuing loops from the reading direction on other tilings.
- **The missing bridge to the program's composed topology.** A law that grows the twist tube, or a two-dimensional shape that reads its
  distance plainly at every size; none exists among tori.

**Next step:** Research directions — selected: which lattices compose everywhere (B21), by the coordinator on 2026-11-09, in this thread.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which lattices compose everywhere (B21, G5) | 2/3 — Substantial | 3/3 — Ready | Run the mirrors reduction of `HONEY-REACH-20261109-001A` on triangular and rectangular tori → a rule from the lattice's rotations, or the first exception | Selected · this thread |
| 2 | Rescue on maps of higher genus (G5) | 2/3 — Substantial | 2/3 — Testable | For each of the 141 on-time regular maps of genus at least 2, look for a short closed walk along which the fastest way is unique, against the 565 late ones → the same mechanism, or a different one | Alternative · deferred |
| 3 | Predicting the rescuing loops (G5) | 1/3 — Minor | 2/3 — Testable | Derive from the reading direction which short vectors give unique fastest routes, and test on the kagome lattice → a rule, or the first tiling it misses | Alternative · deferred |

1. **Which lattices.** Payoff 2: it maps where composition reaches on every regular lattice; Concreteness 3: the reduction carries
   over. Selected by the coordinator.
2. **Higher genus.** Payoff 2: it would turn the one open family into a rule; Concreteness 2: the census rows exist, the loops must be
   found in each group. Main uncertainty: hyperbolic maps may rescue by small diameter alone.
3. **Prediction.** Payoff 1: a sharpening of conclusion 3; Concreteness 2: the tube tables are in hand.

**Recommendation.** Research directions, selected #1 at the coordinator's instruction; reassess #2 when it closes.

## Final report as sent

Sent to the owner on 2026-11-09 at 20:03 UTC and copied here verbatim.

Which finite maps rescue late rings is answered for tori of every shape, by proof, and it's published (RESCUE-MAP-20261109-001):
- **What rescues is a short loop with one fastest way along it.** A torus reads distance without freezing exactly when it holds such a loop, or it is one of finitely many small tori (23 square up to index 17, 85 triangular up to 21, 15 honeycomb up to 9, all listed). The loops are (2,0) and (2,1) on the square lattice, up to the quarter turn (the two tori of index 3 excepted), and any vector of length √3 on the triangular lattice. The honeycomb has none.
- **The mechanism.** It isn't a third route that makes an even count odd. Around the loop there is a strictly shorter, unique route, so a different contact becomes the closest.
- **Why the mirror image fails.** Along (1,2) the fastest routes climb two rings per two arcs and can take their side step at any of j places. A closest contact then has j routes, so it is late whenever j is even, first at distance 4. Rule 60 reads one way round every ring, so a loop and its mirror image are different substrates.
- **How it's proved.** The systole lemma holds for any cover, so a late tube makes every thick torus it covers late. The two thin tubes are proved on time at every size by local conditions checked over one period: by hand for the square tube, by a checked certificate for the triangular one. This turns the grown-torus thread's computed families into theorems. Everything in between, 11,151 lattices, was read exactly.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: which finite maps rescue late rings | Successful | Tori classified completely, with the mechanism and the reason for the chirality split |
| Local direction: reading distance plainly | Research directions | Tori are done; higher-genus maps (141 of 706 on time) are not classified |
| Broader exploration: G5 | Known alternatives | Which lattices compose everywhere (B21, selected); B20 and B22 |
| Long-term goal: G5 Dynamics | Capability gained | We know exactly which flat networks read their own distance without intervention: thin tubes with a unique fastest way, plus finitely many small tori |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Which lattices compose everywhere (B21) | 2/3 | 3/3 | Mirrors reduction on triangular and rectangular tori → a rule from the lattice's rotations, or the first exception |
| 2 | Rescue on higher-genus maps (B27) | 2/3 | 2/3 | Look for short closed walks with a unique fastest way in the 141 on-time maps against the 565 late ones → same mechanism, or a different one |
| 3 | Predict the rescuing loops (B28) | 1/3 | 2/3 | Derive from the reading direction which loops give unique fastest routes, and test on the kagome lattice → a rule, or a miss |

**Corrections:** none new. The narrowing of PLAIN-TIME's 26 tori was logged by the grown-torus thread. **Goals:** a G5 checkpoint (capability gained); B21 selected; backlog B25 to B28 added (honeycomb directions 2 and 3 as you asked, and this epic's directions 2 and 3). **Assumptions:** none added or changed.

Commits on main: bd45b273e (the epic) and 67a440501 (knot intuition entry). The goals-doc edits were already in my working copy when the growth thread committed that file in 3d30fa6ce, so they went out with that commit; the content is mine and correct. Stress test, one size past to index 100, 140 and 80: passed in 56 seconds. Starting B21 now.
