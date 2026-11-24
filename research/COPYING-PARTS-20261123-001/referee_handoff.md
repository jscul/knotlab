# Referee hand-off: COPYING-PARTS-20261123-001

Ticket A is referee pending. Its pre-registration has the prior-work searches under "Prior work in the program"; run
`python3 -B scripts/track.py objects-gate research/COPYING-PARTS-20261123-001A/preregistration.md`. The definitions and the
engine are those of `RING-IN-BALANCE-20261123-001`, itself referee pending. Nothing in the next step waits for the verdict.

| Record | Claims to check | Evidence class | Code and data |
| --- | --- | --- | --- |
| Ticket A | The copying cycle of the two-knot part under FLOOR0, FLOOR1 and ONE-FEWER; the three recurrences for its count (P1 to P3) on three starts to 20,000 knots; the knot test under both knot laws on the small starts (P4, P5); the knot test on the ring of five, with the failure under ONE-FEWER with offshoots at the round of the births without a fresh distinction (P6); no copying under the ordinary count, caps and a fixed two (P7); the five-member copier under a fixed three (P8); the counts under HOLD and the jam with waiting (P9); the stop under fillers (P10); the census of 3,344 starts under six laws | Exact computation with one engine. One argument to read: the cycle and its recurrences for every round (result note, "The cycle") | `experiments/COPYING-PARTS-20261123-001A/`, `artifacts/COPYING-PARTS-20261123-001A/` (`run5_starts.json.gz` is compressed) |
| The thread's side checks | The count of two-knot parts by round on the three starts under each treatment, and the number of census starts in which a two-knot part appears, both with the pilot's program | Exact computation by the designer, on rosters without distinctions; weaker than a fresh referee | `research/COPYING-PARTS-20261123-001/checks/` (the pilot's program is a private workspace file) |

Things a referee should know. The study reuses the earlier study's engine, so an error in that engine would be shared; the
side checks with the pilot's program cover the counts but not the knot tests. The advisor reviewed the first draft cold: it
confirmed the cycle and the recurrences by hand, corrected a false settled statement, and supplied two hand predictions, one
of which (the counts under HOLD with waiting) failed. The not-all-equal test was run only on the two small starts through
round 9 or 10. The engine's constructor refuses NO-OFFSHOOT together with a short knot that makes offshoots; the code's author
ran that pair by setting the treatment after construction, and reports the prediction both with and without it.
