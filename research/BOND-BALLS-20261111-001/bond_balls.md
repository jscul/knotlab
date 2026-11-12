# Bond balls on infinite overlapping bases

Epic `BOND-BALLS-20261111-001` (`PERIODIC-READ-20261111-001` direction 1; G1, question 9; program topology, group spacing),
2026-11-11, at the coordinator's go-ahead under the owner's standing mandate. Pre-registered in commit 8506621c9 before the registered
run. The canonical K1–K3 test is unchanged.

## Words

As in the guide's glossary and lesson 4.7: **steps apart** (the shortest row of co-knotted pairs; the shared-distinction distance),
bond, **bond distance** (one less than the size of the smallest bond containing both), ball. A **shortcut** is a pair whose bond
distance is less than its steps apart plus one; the **lens** of two distinctions is the set within three steps of both. Periodic knot
patterns, finite repeats and windows are as in `PERIODIC-READ-20261111-001`.

## The question

On the 134 infinite two-shift bases with overlap that the not-all-equal law (NAE) reads faithfully, does bond distance follow steps
apart (bond distance = steps + 1), so that the law's balls grow as the step balls the two shifts dictate?

## The question in standard terms

For the proper 2-colourings of 134 periodic 3-uniform hypergraphs over Z², is the smallest non-shattered set with all co-1 subsets
shattered, containing two vertices at hypergraph distance d, of size d + 2 for d = 3, and never 4 for d = 4?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The law always reaches the next shell.** Every one of the 7,980 distinctions three steps from the origin, across all 134 bases, lies in a bond of at most five with it; each bond found is genuine (refuted by a finite set of knots, its parts realized by infinite states). | computed, frozen; checked by the referee | A |
| 2 | **But its distance is shorter on 42 bases (B1 and B2 failed).** 442 three-step distinctions lie in a bond of four with the origin (bond distance 3, not 4), 456 with a lens one step wider; 198 four-step distinctions (18 bases) do too. Under integer changes of basis the 134 bases are 108 classes, the shortcut ones 38 and the four-step ones 16. The other bases have bond distance steps + 1 at three steps where settled. | computed, frozen; recounted independently | A |
| 3 | **Along a direction the law's distance does not grow.** On base 16, three equal distinctions in a column force the triple one column over and one row along to the opposite value, column after column, so {(−k, k−2), (−k, k−1), (−k, k), origin} is a bond of four for every k from 3 to 12 (reproduced in the record with the census's own bounds, `travelling_triple.py`: the refuted pattern alternates, all four equal for odd k, the far triple equal and the origin opposite for even k). On 14 of the 16 four-step shortcut classes the referee also found bonds of four at five and six steps. There the ball of bond radius 3 runs out along one direction without end, to the reach measured. | computed (the referee, and after the run); a proof for every k needs the parts' freeness at every k | A |
| 4 | **The control holds where it is proved.** The endless six-regular weave (literature: the triangular lattice), in both of its forms, has every three-step distinction at bond distance 4, by the side-and-apex bond of `RULER-20261111-001`, and no shortcut. | computed (a check of a proof) | A |
| 5 | **Some "bond of five" verdicts are only upper bounds.** On five heavily overlapping bases (81, 82, 87, 103, 112, and possibly 94) some candidate four-sets are neither refuted nor shown free by any bound tried, so bond distance there is at most 4, perhaps 3. Shortcut bases by the most knots on a pair: 6 of 19 (one), 21 of 79 (two), 15 of 34 (three), 0 of 2 (four). | computed; the referee's audit | A |

## Answer

The knot law always reaches the next shell on these infinite bases: nothing stops it at three steps. On most of them it measures them
as the shifts do, bond distance steps plus one. On 42 (38 up to change of basis) it measures them shorter, and on at least one it
does not grow at all along one direction: distinctions twelve steps away still share a bond of four with the origin. There the law
reads a geometry the meeting pattern does not supply: one in which a whole direction is at bounded distance.

## Reading

**Interpretation, not a theorem.**
- **What the measurement added.** Step balls grow as the shifts dictate whatever the law does; the question was whether the law's own
  distance agrees. On most bases it does, which is the ruler again; on a third it does not, and the disagreement is always a shortcut,
  never an absence.
- **The law folds a direction.** Where a triple of equal distinctions forces the next triple over, without end, the allowed states
  bind distinctions along that direction at bounded bond distance however many steps apart they are. Read by the law alone, that
  direction has no length: the two-shift base is compressed along it, in the owner's word, while the meeting pattern keeps it.
- **For question 9.** Space read from a law can differ from the space its meeting pattern supplies, and the difference can be a whole
  direction, not just a constant. Whether those bases read as one-dimensional by the law's balls is the next measurement.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic. **Proved.** Nothing new (the six-regular control is `RULER-20261111-001`'s theorem).
  **Computed.** All conclusions, on the 134 bases; the frozen census to four steps (bonds of five not searched at four steps); the
  travelling triple to twelve steps on one base, after the run.

## Stress test

The bonds counted are settled: each is shown constrained by a window of radius 10 and its parts free by finite repeats or one-shift
repeats; the referee confirmed them with independent code and minimal forcing sets. One size past: the referee's search at five and
six steps, and the travelling triple to twelve. Absences are relative to the window and the lens, but none occurred; "bond of five"
is an upper bound where four-sets stayed unsettled (conclusion 5).

## Review

An independent referee (code sharing nothing with the census: steps by search on the infinite pattern, its own finite repeats to index
40, states with a wall checked knot by knot on windows of radius 60, other solvers) reproduced both counts base by base, and:
- **confirmed the shortcuts** on bases 14, 16, 40, 48, 81, 87, 104 (and four-step ones on 88, 94, 112, 117), each with a small set of
  knots forcing it, and explained them: four equal distinctions down a column forcing a knot all equal (14); a travelling triple
  (16, 40, 87); short chains of "two equal force the third opposite" closing on a knot (48, 81, 104);
- **found the travelling triple unbounded** on base 16 to twelve steps and bonds of four at five and six steps on 14 of 16 four-step
  classes, so B2's failure is a direction the law does not lengthen, not only a shortcut by two;
- **found B1 lens-relative** (456 shortcuts with the lens widened to four steps) and some "bond of five" verdicts unsettled on heavily
  overlapping bases; **steps apart and lenses** correct on all 134; **bond-of-five** verdicts right on a sample (on the triangular
  lattice exactly the plane's bond);
- **noted** that the 134 are 108 classes under change of basis; that 32 of the three-step and 142 of the four-step shortcuts need
  states with a wall for some part's freeness (all confirmed); that no source labels were recorded for the bonds; that a refuted
  four-set with unsettled parts would be passed over once a bond of five is found (a latent masking that did not fire); that the run
  took 1,973 s against the ten to twenty minutes registered; and that census.json does not store the bonds themselves.

## Literature and provenance

- **Known.** The ruler on the endless six-regular weave (`RULER-20261111-001`) and on six-regular one-pair weaves
  (`RULER-FLAT-20261111-001`); periodic hypergraphs and shifts of finite type as in `PERIODIC-READ-20261111-001`.
- **Not found** (bounded search): bond distance measured on periodic bases with overlap.
- **Classification.** Not assessed beyond that: a computed finding in a registered family.

## Workspace assumptions

- **Relied on.** A64 (the shifts, like counts, are supplied), A67 (three-set reading for faithfulness). **Changed.** None.

## Ratio

- **Substantive.** The census (one registered run, 1,973 s on 8 workers), the travelling triple reproduced after the run, one referee
  pass.
- **Administrative.** The pre-registration, this note, the closure.

## Corrections

None to published claims. The pre-registration's runtime (ten to twenty minutes) was short; the run took 33 minutes.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — bond balls on infinite overlapping bases | **Status:** Successful | Both predictions failed informatively: shortcuts on 42 bases, no absences |
| Local direction — NAE's distance on infinite bases | Continue | The folded direction needs a proof; the other shortcuts a rule |
| Broader exploration — G1 on bases of knots alone | Known alternatives | Rigid periodic states; settling the 160 unsettled readings |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | The law's distance can differ from the meeting pattern's, down to a direction of no length |

**Corrections:** none. **Goals:** a G1 checkpoint (capability gained), no goal change. **Assumptions:** none changed.
**Basket:** `PERIODIC-READ-20261111-001#2` (rigid periodic states, 2/3, 2/3), `PERIODIC-READ-20261111-001#3` (settle the unsettled,
1/3, 2/3), `OVERLAP-READ-20261111-001#4` (reading by pair counts, 2/3, 1/3); taken: none yet; direction 1 below is the first.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The folded direction, proved | 3/3 — Major | 2/3 — Testable | Prove the travelling triple on base 16 for every k (the forcing repeats under translation; the parts' freeness needs a uniform family of states), then sort the 38 shortcut classes by whether they fold a direction → a theorem that the law reads some two-shift bases with a direction of no length, or a k where it stops | Selected · awaiting go-ahead |
| 2 | What the other shortcuts are | 2/3 — Substantial | 3/3 — Ready | For the classes that do not fold, find the law's distance as steps under another set of moves → a rule, or shortcuts with no such rule | Alternative · deferred |
| 3 | Rigid periodic states (was `PERIODIC-READ-20261111-001#2`) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |

1. **The folded direction.** Payoff 3: a proof would show a law reading its own, lower-dimensional geometry off a two-shift meeting
   pattern, the first such case on this line. Concreteness 2: the forcing chain is explicit; the uniform freeness is the work.
2. **The other shortcuts.** Payoff 2, concreteness 3.
3. **Rigid states.** Payoff 2, concreteness 2.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
