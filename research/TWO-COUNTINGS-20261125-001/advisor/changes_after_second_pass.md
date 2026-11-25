# Changes from the second to the third version (one line per advisor item)

The advisor's last pass: `study/countings_advisor2/answer.md`, "Freeze with the listed fixes; no further round". The
coordinator's ten-point message of 25 November. Earlier versions are kept beside these.

## Section 8, required, in order

1. **Sizes.** Part 8 re-scoped: projection on every structure of parts 2–4 with duplicates removed; the canonical
   checker only on the 33 structures (of at most 20 distinctions) and on newly built finished structures of at most 20
   distinctions, in the registered order (11-knot, 8-knot, smallest gain first), with a 20-minute count cut; no knot test
   on census growths. The 512 sign assignments are part 3, on six processes (557 s on one, measured). The fifth part is
   cut to P9 (definition: FREEDOM-CLOCKS-C `results.md` lines 3, 7, 17; data paths given), timing pass 0.0–1.6 s per
   type of width ≤ 16; the other rows marked "not recomputed (no registered definition)". The census moved to an
   engine check on 100 starts (part 9). Total restated: about 20 min on six at measured rates, at most about 60 with
   every cap reached. Canonical timing pass made now: 0.14–0.25 s per knot at 16 distinctions, 0.83 s at 18 (load 10);
   I could not reproduce the coordinator's "over a minute" per check, so part 8 carries the cut for that case.
2. **The lemma.** h4's record clause in the advisor's wording, with the eighth example E7 run (5/2, the first record
   changed by 1/4, no weight lost); h1′ reworded for two setting stages in the advisor's wording; the lost-weight rule
   added, the lemma stated for counting from the start renormalised; stated for setting knots only, the whole-stage 9/4
   classified apart in the advisor's words; the old P10 moved to Known 8; E1 and E2 marked as not single breaks; E3 and
   E5 marked as renormalised.
3. **Checkable hypotheses** (TD 9) and P2's three-way verdict (PR, P2; claim verdict 2).
4. **Implementability.** Construction orders and the census index shipped as data (construction_orders.json,
   census_index.json, with the exact generating calls); the 4n renumberings defined (TD 7.1); which of x2, x3 goes with
   a = 0 and the nine option pairs listed (TD 4.1); the functions g run (TD 4.5: 16 on the 11-knot, 256 on the 18-knot);
   the score method for each outcome class, values with nonzero weight, functions of the own setting only (TD 4.4);
   the order's index (11) and every example's record (TD 8.2); full paths for every archive; "by side tables" replaced
   by exact enumeration of the 18-knot start's 512 states.
5. **Predictions** marked as the advisor's table; the independence sentence dropped; P5 now an engine check with the
   first parting round as the verdict and distances after it; P6 split into P6a (real) and P6b (an engine check), with
   the comparison defined by carrying the renaming back.
6. **Section 9 of the claim.** Reading 1 moved to "tested, not met" (the 7-knot structure passes); reading 2 defined
   (a law's history, settings as law-made births, start before them, both records hidden, every knot passing), its
   consequence "reason 1 falls", and the 9/4 placed against it; reading 3 tied to an event (a registered ticket on the
   states of an unending growth, or the owner's word); reading 4 made one-directional. Reasons 2 and 3 merged, with
   their cost (a supplied finishing stage and a supplied weighting of histories); "the excess is what this choice
   produces, so it is not evidence for the choice" added; "the object the canonical knot test reads" dropped;
   "the working choice of the thread, reversible; not tested here" in place of a status.
7. **The knot-test finding.** Item 3 reworded in the advisor's words; the 18-knot pass marked "by projection only"
   wherever cited (finding, claim, PR, table); the 10-knot finished structures said to be untested; the line about the
   relation in all 512 corrected (the failure holds in all 512, the relation only where the tie is an inequality); the
   knot column added to the table; the carried sentence added in the advisor's words, with the named rules per study.
8. **The table's sweep sentence** (searches, hits examined against kept, directories swept and not, guide rows
   hand-picked); a verdict "outside both countings" for the 9/4 and for squared amplitudes (a class row); the claim
   retitled "Two countings of a structure's allowed states: the thread's working choice"; "by his answer on this fork";
   the owner's sentences as the advisor rewrote them, numbers checked (report).

## Optional items

- The eighth example: run (E7).
- All 27 gains: taken (part 2; estimated 5 min for the 35 parts).
- The census at 100 starts: taken, as an engine check.
- Sentence-level fixes of section 6: taken ("not chosen" for reading (e); Alice and Bob once, in the claim only; "the
  supplied rule g assigns each old state its history"; the plain picture marked "a picture of our rule, nothing the
  growth does"; counts in place of "nearly every"; "weight" for "chance"; "whatever their positions in the order" and
  "at other knots"; "registered" for the laws; the parity factor and the no-old-places case in TD 7.3; TD 7.4 "while
  the countings agree before the birth"; "with a fresh distinction" in the claim's parity line; TD 6 says the 10-knot
  starts have no finished structures registered).
- The separate tickets: named in one sentence each (PR "Later tickets"; finding), not designed.

## Not applied as worded, or where the record or the scratch output disagrees

- **The coordinator's timing** ("over a minute" per canonical check at 16–18 distinctions): not reproduced; measured
  0.14–0.83 s per check at load 10, as one command per knot. Part 8 is sized on the measured rate and keeps the
  registered count cut for the slower case.
- **"Seven examples, one hypothesis each"** has become eight (E0–E7, E0 the reference); E1 and E2 are marked as not
  single breaks, as the advisor says.
- **P9's population**: the advisor's and the record's 194 types are 183 connected types (`census_cases.json.gz`, first
  status "births") and 11 supplemental ones (`disconnected.json`); the archive holds 212 not-all-equal entries in all,
  29 of which closed or stalled. Stated so in part 5.
- **"P2 duplicates an engine check"**: kept as a prediction because its one real clause (the unmeasured structures meet
  the hypotheses) can fail; its other clause is listed with the engine checks.
- **The advisor's sentence 2 for the owner** omits the five RING-LAW starts whose births were one-input or forced, on
  which the countings did not part; added.
