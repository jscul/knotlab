# Bond balls on infinite overlapping bases: pre-registration

Epic `BOND-BALLS-20261111-001` (`PERIODIC-READ-20261111-001` direction 1; G1, question 9; program topology, group spacing),
2026-11-11, at the coordinator's go-ahead under the owner's standing mandate. Frozen before any registered run. The canonical K1–K3
test is unchanged.

## Words

As in the guide's glossary and lesson 4.7: **steps apart** (the shortest row of co-knotted pairs from one distinction to another, each
sharing a distinction with the next; the shared-distinction distance), **bond**, **bond distance** (one less than the size of the
smallest bond containing both), **ball**; and from `PERIODIC-READ-20261111-001`: periodic knot pattern, finite repeat, window, unit.
A **shortcut** is a pair whose bond distance is less than its steps apart plus one; the **lens** of two distinctions is the set of
distinctions within three steps of both.

## The question

On the 134 infinite two-shift bases with overlap that the not-all-equal law (NAE) reads faithfully (`PERIODIC-READ-20261111-001`),
does bond distance follow steps apart, as the ruler does on the endless six-regular weave (`RULER-20261111-001`: bond distance d + 1 at
d steps), so that bond balls grow as step balls do?

## What the shifts already dictate, and what the measurement adds

- **Step balls are dictated by the supplied shifts.** In a connected pattern repeating along two independent shifts with knots of
  bounded span, the distinctions within r steps of one number between a r² and b r² for constants a, b: steps apart is comparable to a
  norm on the shifts. So quadratic growth of step balls is settled by the test's own definition, and it is the control here, not a
  finding. The shifts are an input, as A64 records for counts of how knots meet.
- **Bond balls are not dictated.** Bond distance is read from the allowed states alone. It can be smaller than steps apart plus one
  (a shortcut, as the global hollow triples of `OVERLAP-READ-20261111-001` showed for whole bases), larger, or undefined (pairs in no
  bond at all, as in the finite overlapping bases there). Bond balls can therefore grow faster than step balls, slower, or stop. What
  the measurement adds beyond the shifts is whether the law's own distance reproduces the one the shifts supply.
- **What a finite measurement can and cannot show.** Only the first radii are read: bond distance at one, two and three steps, and
  shortcuts at four. Agreement there is evidence that bond balls follow step balls to radius four, not a growth law; a proof would be
  needed for every radius, as the plane has.

## Disclosed before freezing

A pilot outside the registered run, on three of the 134 bases (with pairs in four, three and two knots), for the first six
distinctions three steps away each: all eighteen lie in a bond of five with the origin and in no bond of four. Step shells there: 1, 12,
44, 74, 104 (the base with four knots on a pair) and 1, 8, 18, 28, 38 and 1, 8, 20, 32, 44. A timing run of the frozen code on two bases
(the first, and the one above) found every distinction three steps away in a bond of five (18 and 74) and no bond of four at four
steps (24 and 104).

## Families and readings (frozen; `contract.json`)

- **Bases:** the 134 two-shift patterns PERIODIC-READ's census read faithfully (its census.json, its code checked by hash).
- **Readings, around the origin distinction:** the step shells to four steps; for every distinction three steps away, the least bond
  containing both with the rest from the lens, of four (a shortcut) or five (bond distance four, steps plus one), else none; for
  every distinction four steps away, a bond of four (a shortcut by two). A candidate set counts as constrained when the window of
  radius 10 refutes one of its value patterns; its parts' freeness uses PERIODIC-READ's bounds, with 300 sampled periodic states
  first. One and two steps are known from PERIODIC-READ (every co-knotted pair is in a knot; every pair two steps apart in a bond of
  four).

## Predictions

- **B1 (the ruler to three steps).** On every base, every distinction three steps away lies in a bond of five with the origin and in
  no bond of four. Failure: a shortcut at three steps, or a distinction with no bond of five in the lens (bond balls stop following
  step balls at the law's own scale).
- **B2 (no shortcut at four steps).** No distinction four steps away lies in a bond of four with the origin (bonds of five there
  were not searched: too costly; so B2 tests a shortcut by two, not by one).
- Measured: step shells, by the most knots on a pair; unsettled verdicts.

## Decision rules

- **B1 and B2 hold:** on every faithful infinite base in the family the law's distance equals steps apart plus one to three steps, so
  its balls follow the step balls the shifts dictate, to radius four; the open question is whether a proof extends this to every
  radius, as for the plane.
- **B1 fails by absence:** the law stops measuring the base at three steps there; its balls stop growing at the law's scale.
- **B1 or B2 fails by a shortcut:** the law's distance is shorter than the shifts' on that base, a geometry the shifts do not supply.

## Prior work

The ruler on the endless six-regular weave (`RULER-20261111-001`, proved) and on six-regular one-pair weaves (`RULER-FLAT-20261111-001`,
proved with a margin); bond distance on finite two-fold weaves (`LONG-LOOP-20261111-001`). For periodic bases with overlap, no
measurement of bond distance was found (bounded search, including the knots-alone line's own records).

## Stop rule

One registered run, one referee pass; report and hold.

## Runtime

About ten to twenty minutes on 8 workers (0.6 s to 125 s a base in the timing pilot, on two bases); registered in
`docs/LONG_RUNNING.md`; `systemd-run --user -p MemoryMax=16G -p MemorySwapMax=0`.
