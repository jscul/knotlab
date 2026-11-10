# A plane of long rings

Epic `LONG-RINGS-20261110-001` (program foundations), 2026-11-10.

## The question

- **Where it comes from.** `REROUTE-20261109-001B` proved that on the square torus's law-(12, 12) automaton every grouping of the cells
  into rings that reads its distance plainly has only rings of linear size, at most 64n of them on the n × n torus, and that the two
  line networks do read it plainly, with a ring graph that is a cycle. Backlog B46 asked whether long rings running in two directions could
  read plainly with a ring graph that grows like a plane; the coordinator selected it on 2026-11-09 to follow B45.
- **The question.** Is there a grouping of the square automaton into long rings that is on time and whose ring balls grow faster than
  linearly, or does every on-time grouping have a one-dimensional ring graph?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Every periodic grouping that reads plainly is a family of parallel lines.** Of 2,070,428 groupings periodic under a sublattice of index at most 8 (sides 24 and 16; 6 on side 12), 24,060 are networks and 1,302 are on time. Each of those has all its rings non-contractible, in one homology class (p, q) up to sign, and a ring graph that is a cycle. | exploratory census, exact, pre-registered | A |
| 2 | **Lines of many slopes.** Besides the axis lines the classes (1, 1), (1, 2), (1, 3), (1, 5), (1, 7) and (3, 5) occur, up to symmetry. A grouping of class (p, q) on the n × n torus has 2n / (\|p\| + \|q\|) rings of 2n(\|p\| + \|q\|) contacts, each a staircase of staircases winding once round the torus. | exploratory census | A |

## Answer

No plane of long rings appears. Among the periodic groupings, the square automaton reads its distance plainly exactly when its rings are
parallel lines, of the axis slopes or of slopes (1, 1), (1, 2), (1, 3) and others, and then its ring graph is a cycle. Two families of
lines never cross in an on-time grouping, so what reads plainly is always one-dimensional.

## Reading

**Interpretation, not a theorem.**
- **Lines of every slope read alike.** A diagonal line is reached from a target by straight routes along a row or column at its nearest
  contacts, just as an axis line is: the single fastest way of `RESCUE-MAP-20261109-001A` again, at any rational slope the torus allows.
- **Crossing costs the reading.** Every grouping in which rings of two classes cross, or in which some ring closes up contractibly, is late
  somewhere. With Theorem 3 of `REROUTE-20261109-001B` (small rings are late), the evidence is that under law (12, 12) the plain reading
  forces one family of parallel lines.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Distances and shortest-route parities are exact.
- **Census-only.** Both conclusions: periodic groupings with period cells of at most 8 positions; non-periodic groupings are not read.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Every on-time periodic grouping is a family of parallel lines with a cyclic ring graph (1) | the 32 × 32 torus, sublattice index up to 8 (read to side 24) | pass: 984,884 patterns, 10,076 networks, 320 on time, every one a family of parallel lines with a cyclic ring graph |

The script is `stress_test.py` beside this note, its output `stress_test.json`; it ran in 638 seconds (LONG-RINGS-S1), after the
report below was sent, and was folded in afterwards.

## Literature and provenance

- **Sources.** `REROUTE-20261109-001B` (re-routing, the line networks, small rings late); `RESCUE-MAP-20261109-001A` (the single fastest
  way); Hermite normal forms of sublattices of Z².
- **Classification.** New as far as found for the question asked.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A41 (distance across time read through freezes), A45 (rings are read as declared).
- **Added.** None.
- **Scope.** The square torus's law-(12, 12) automaton at g = 2, its periodic groupings.

## Ratio

Since the epic opened:
- **Substantive.** One pre-registered census (A) and one stress test (pending).
- **Administrative.** This note and the closure.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a plane of long rings | **Status:** Partially successful | No plane of long rings among the periodic groupings: every on-time one is a family of parallel lines with a cyclic ring graph (census) |
| Local direction — the plain reading of the square automaton | Research directions | A proof for all groupings, and the non-periodic ones, are open |
| Broader exploration — G1 with G5 | Known alternatives | Rings the law can see (B45, its census running in `RING-LAW-20261109-001`); the even-index mechanism (B30) |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | Under law (12, 12) a plane's automaton reads its distance plainly only when grouped into one family of lines |

**Corrections:** none. **Goals:** a G1 checkpoint (obstruction learned); B46 taken; backlog entries added for directions 1 to 3.
**Assumptions:** none added or changed.

- **What the attempt leaves open.** Whether every on-time grouping, periodic or not, is a family of parallel lines; why the classes found
  are those with |p| + |q| dividing 2n.
- **The missing bridge to the program's composed topology.** A plane read plainly: not by grouping the square automaton under law (12, 12).

**Next step:** Research directions — none selected, for the coordinator.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Only lines read plainly, proved (G1) | 2/3 — Substantial | 1/3 — Stated | Extend the even box of `REROUTE-20261109-001B`, Theorem 3, to a ring's bend: a target placed off a bend whose nearest contacts all have even counts → a proof that an on-time ring never bends at large scale, or the bend shape it cannot handle | Alternative · deferred |
| 2 | Non-periodic groupings (G1) | 1/3 — Minor | 2/3 — Testable | Search groupings near the line families by moves that keep every contact on two rings (exchanging two lines' routing along a stretch) → an on-time grouping that is not a family of lines, or none | Alternative · deferred |
| 3 | The slope rule (G5) | 1/3 — Minor | 3/3 — Ready | Build the family of class (p, q) for every primitive (p, q) with \|p\| + \|q\| dividing 2n and prove it on time by single routes → the rule, or the class that fails | Alternative · deferred |

1. **Only lines, proved.** Payoff 2: it would make the obstruction hold for every grouping of the square automaton; Concreteness 1: the box
   lemma handles small rings, but a bend on a long ring needs a new argument, and diagonal lines show the target must be placed with care.
2. **Non-periodic groupings.** Payoff 1: the census leaves only these open; Concreteness 2: line networks resisted every face toggle in
   `REROUTE-20261109-001C`, so the moves must be larger.
3. **The slope rule.** Payoff 1; Concreteness 3: the families are explicit in `result.json`.

**Recommendation.** Research directions, none selected; directions 1 to 3 go to the backlog for the coordinator to choose.

## Final report as sent

Sent to the owner on 2026-11-10 at 01:23 UTC and copied here verbatim.

A plane of long rings (B46) is closed and published (LONG-RINGS-20261110-001). I ran it while the B45 census runs in the background; B45's report follows when that census finishes.
- **No plane of long rings (pre-registered census, exact).** I read every grouping of the square torus's automaton that is periodic under a sublattice of index up to 8: 2,070,428 patterns on the 24 × 24, 16 × 16 and 12 × 12 tori. Of these, 24,060 are networks and 1,302 read their distance plainly. Every one of those is a family of parallel lines winding round the torus, all in one homology class, and its ring graph is a cycle. Both frozen hypotheses held.
- **The lines come in many slopes.** Besides the axis lines there are diagonal families of class (1, 1), (1, 2), (1, 3), (1, 5), (1, 7) and (3, 5). Class (p, q) has 2n/(|p|+|q|) rings of 2n(|p|+|q|) contacts. Every line is read the same way, by a single straight route from each target to its nearest contact. Where two directions of lines cross, or a ring closes up, some reading comes late. So under law (12, 12) a plane of rings still needs freezing.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: a plane of long rings | Partially successful | None among the periodic groupings: every on-time one is one family of parallel lines with a cyclic ring graph (census) |
| Local direction: the square automaton's plain reading | Research directions | A proof for all groupings, and groupings without a period, are open |
| Broader exploration: G1 with G5 | Known alternatives | Rings the law can see (B45, census running); the even-index mechanism (B30) |
| Long-term goal: G1 Space from a law | Obstruction learned | Under law (12, 12) a plane's automaton reads plainly only as one family of lines |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Only lines read plainly, proved (B75) | 2/3 | 1/3 | Extend the even box to a ring's bend → a proof that on-time rings never bend at large scale, or the bend it can't handle |
| 2 | Non-periodic groupings (B76) | 1/3 | 2/3 | Moves that exchange two lines' routing along a stretch → an on-time grouping that isn't lines, or none |
| 3 | The slope rule (B77) | 1/3 | 3/3 | Build and prove the class (p, q) families with \|p\|+\|q\| dividing 2n → the rule, or the class that fails |

**Corrections:** none. **Goals:** a G1 checkpoint (obstruction learned); B46 taken; B75 to B77 added to the backlog. No direction is rated 3/3, so there are no sub-goals to record. **Assumptions:** none added or changed.

Commits on main: 543d364ab (pre-registration), d1898478b (the epic) and 9298e058b (shared docs). The census took 7 minutes. The stress test one size past (the 32 × 32 torus, LONG-RINGS-S1) is running and will be folded in when it finishes. No direction is selected; your call.
