# Where groups of three take over

Epic `EXPLOSIVE-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `DEAD-CAP-20261119-001#1`. Goal G17.
Framed by A110, the owner's direction: blow-up is expected, and the unlimited structure is read by sampling it. **Referee pending.**

**Record.**
- **Pre-registration:** [preregistration.md](preregistration.md), frozen in commit `bdd3e1228`, after the census exploration and a
  calibration on the reference shapes (both disclosed).
- **The run:** the shared runner (`EXPLOSIVE-B1`, `runs/explosive`, 21 cases, all ok). Each start grew in its own child process,
  limited to 2.5 GB and 30 s.
- **Code:** [filllib.py, job.py, merge.py](../../experiments/EXPLOSIVE-20261119-001B/EXPLOSIVE-20261119-001B-E001_filled/).
  merge.py's feature table had tuple keys that JSON cannot write. That was fixed after the run, changing no verdict.
- **Results:** [results.json](../../artifacts/EXPLOSIVE-20261119-001B/EXPLOSIVE-20261119-001B-E001_filled/results.json).
- **Post hoc, after the run was read:** the smallest explosive starts, grown further
  (`posthoc_smallest.py`, `posthoc_smallest.json`).
- **The advisor** checked the design before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).

## The answer

**In the owner's terms.**
- **A group of three acts like a filled triangle, as long as groups of three don't overlap.** A group of three joins three knots in
  one junction instead of three pairs. Glue a cell on each cycle of three blocks and read the map as before; that filled map
  predicts the growth's class.
  - It holds on all 1,705 such starts within five places.
  - It holds on all 474 census starts.
  - Within seven places it holds on 775 of the 776 starts whose groups of three don't overlap.
  - For round 1 this is a short argument: a junction is a cone over its parents, so one junction of three fills the cycle that
    three pair junctions leave open. Beyond round 1 it is measured, not proved.
- **The explosive kind needs overlapping groups of three and bigger knots.**
  - **Within five places it never occurs:** 0 of 2,191 starts, and the largest group anywhere is 9.
  - **Within seven places it does:** 16 of 1,000.
  - Every one of the 16 has groups of three that share a knot and a block, and a knot of seven places.
  - Their filled maps keep no cycle. So the advisor's guess, that explosion comes from a cycle surviving the filling, does not
    hold. The overlap is what does it.
- **The smallest explosive start ends, so "grows without bound" is refuted there.** It has six knots of 6, 7, 5, 4, 5 and 3 places.
  1. It grows modestly for eleven rounds (8 to 31 junctions a round).
  2. Its count then leaps to 67 and 322 in rounds 12 and 13.
  3. Round 14 makes only 9 junctions, the largest with 309 parents: one group swallows nearly every open junction.
  4. Those 9 then join in every way exactly once, smallest groups first. That is 36, 84, 126, 126, 84, 36, 9 and 1 junctions with
     2 to 9 parents, the binomial coefficients of 9.
  5. The growth closes at round 23.

  So the explosive kind here is one merging event followed by a finite burst. It has its own regularity, and finite description
  does not end there.
- **The other explosive starts could not be followed as far.** Their groups reach 22 to 974 before the child's limits stop them, so
  whether they also end after a burst is open.
- **What a sample shows (A110).** Explosive growth is rare under these weightings: none within five places, and 1.6% within seven.
  It is finitely describable in the one case followed to its end. Most groups of three behave as filled cells.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| X1 | filled b1 = 0 and decided: the filled reading equals the measured class | **failed** | within five places 1,705 of 1,705 and the census 474 of 474; within seven places 835 of 864. Of the 29 failures, 28 have overlapping groups of three and all have a knot of seven places |
| X1b | (risky) filled b1 ≥ 1 and decided: neither polynomial nor closing | **failed** | 2 of 12 within five places are polynomial: a kept cycle that is bare stays constant or polynomial, as the rank rule says (the prediction forgot bare cycles). Within seven places 99 of 99 are exponential-like |
| X2 | (risky) within five places, no explosive start | **held** | 0 of 1,717 fresh starts, and 0 of 474 in the census |
| X3 | within seven places, at least one explosive start | **held** | 16 of 1,000 |

2 of 4 held.

**Readouts.**
- **The 16 explosive starts.** All have b1 = 0 and b2 = 0 after filling, and all have groups of three sharing a point and a block.
  15 were stopped by the child's limits, and 1 was alive at round 20.
- **The reference shapes.**
  - Two triangles joined twice: all four explosive, with overlap.
  - Two triangles joined once: exponential-like.
  - The three-regular six-knot graph: one explosive with a kept cycle and no overlap; two undecided.
- **The kept-cycle stratum** within five places is rare. The sampler found 5 in 2.1 million tries.

## Assumptions

- **A110** (blow-up expected; read by sampling): history line. The first sampled reading of the explosive kind finds it rare under
  these weightings, absent within five places, and finitely describable in its smallest case. That is a regularity, not where
  description ends. Status unchanged.
- **A109:** history line. The explosive kind is entered through overlapping groups of three, and its smallest case closes after one
  merge and a binomial burst. It stays under challenge for the cases not followed to their end.

## Known results, and what this adds

- **Known, cited once.**
  - Nerves and coning: a simplex fills its boundary cycle (Borsuk 1948, the nerve theorem).
  - The binomial burst is the Boolean lattice of 9 elements.
- **What this adds.**
  - The filled map as the cheapest growth's object once groups of three appear, with its range: non-overlapping groups.
  - The explosive kind located: overlapping groups and more than five places.
  - Its smallest case followed to its end: one merge, a Boolean-lattice burst, and closing.

## Limitations

- **The filled reading beyond round 1** is measured, not proved.
- **The explosive starts** are read within each child's 2.5 GB and 30 s, or 120 s post hoc. Only the smallest was followed to its
  end.
- **Weightings and sizes.** Two weightings are used: random trees plus extra lines, within five and seven places, at 6 to 12 knots.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the explosive kind | **Status:** Partially successful (2 of 4 held; X1 and X1b failed, with their causes located) | The filled map predicts growth where groups of three don't overlap; the explosive kind needs overlapping groups and more than five places; its smallest case closes after one merge and a binomial burst |
| Local direction: what the cheapest growth builds | Research directions | Within five places the whole picture is now described: proved in the class, filled cells outside it; the explosive kind lies beyond the cap |
| Broader exploration: the eddy catalogue (A109) | Research directions | The explosive kind has a regularity in its smallest case; the rest is unread within the limits |
| Long-term goal: G17 | Capability gained | The rare explosive kind located and sampled; one case followed to its end |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Merge and burst: do the other explosive starts also end after one giant group and a Boolean-lattice burst? Count the burst instead of building it | 3/3 — it decides "grows without bound" for the kind | 2/3 — the smallest case's pattern suggests counting the subsets of the survivors instead of enumerating groups | grow the 15 stopped starts with the merge read as an event and the burst counted → stop when each ends, or one keeps growing past its burst | Alternative · proposed |
| 2 | Prove the filled reading for groups of three that do not overlap | 2/3 — it carries the identification line outside the class | 2/3 — the round-1 cone argument is in hand | extend the cover argument to a complex with filled cells → stop at a proof, or a non-overlapping start it misses | Alternative · proposed |
| 3 | Prove the ceiling of 2.3830 within five places | 2/3 | 2/3 | bound every branch system by the theta's → stop at a proof, or a start that beats it | Alternative · in the basket |
