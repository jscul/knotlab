# A principle for the free sign: do the birth choices with the most failing pairs force it?

Epic `MOST-FAILING-20261127-001`, under G18 Comparing growth laws, at the owner's go-ahead ("Yes, let's continue with 1")
on direction 1 of the commutation-at-birth study (`LOCAL-COMMUTE-20261127-001#1`). Design and predictions frozen before
the code was run, after a review (section "Review before the freeze"; the advisor was unavailable). Results follow in
sections of their own; nothing above them changes except by a dated notice. The canonical K1–K3 test, the growth law and
the birth rule (A314) are unchanged.

## The question

With which values commute declared at birth (A314), every structure admits a state, and odd closes are attainable at
1,177 of the 1,187 closures that are not outerplanar; at each of those closures half the complete birth choices close odd
under uniform weighting, the sign being fixed by the earlier rounds' choices (the commutation-at-birth study, as
refereed). A principle that selects among the choices could make the sign a property of the structure. A homogeneous
restriction (a linear set of choices containing the classical one) can force even but never odd, and an affine condition
can select odd only by naming it. The principle tested here excludes the classical choice without naming the sign: **take
the birth choices with as many failing pairs as a state allows**, which are also the birth choices that differ from rule R
on the fewest pairs. At each closure, is the closing sign the same on every such choice (forced odd, forced even), or not
(free)?

The principle is a scaffold (A315), tested three ways:
- **the control**, the nonzero birth choices with the fewest failing pairs (the least departure from classical): if it
  forces a different sign at a closure, the sign there belongs to the principle;
- **holder types**, the maximum counted once per kind of pair (two pairs count once when their members have the same
  holders), since pairs of distinctions with the same holders have identical checks and cost, and a count of pairs then
  weighs meeting multiplicities;
- **round by round**, at the 86 later closures: at each round the most failing pairs among the choices consistent with the
  earlier rounds, with the integer program's first optimum as the tie-break (a further scaffold). At round-1 closures this
  is the same as the maximum, since every pair is decided at round 0 and the closing knot's conditions follow from the
  older ones; at later closures the maximum uses conditions that arrive after the pair is decided, so only this variant
  is a choice made at birth.

## In standard terms

The birth choices at a closure form a binary linear code: words over the closure's decidable pairs, with one parity check
for each pair of knots. The closing sign is a linear functional on the code that is not identically zero. The principle
is the code's maximum-weight words, the control its minimum-weight nonzero words, the variant a maximum with weights on
classes of positions; the question is whether the functional is constant on each set. The codes here are small: at most
97 positions and 55 free choices of basis (the code's dimension).

## Population and weighting

The 1,177 closures where birth choices attain odd, from the commutation-at-birth run (the census starts grown up to four
rounds, one vote per census start): 1,091 at round 1 and 86 later. At 82 of them the natural birth rule (every decidable
pair fails) keeps a state; there the maximum is that rule's choice alone, odd at 53 and even at 29. A second weighting,
one vote per closed-pattern type: the 173 census types of the earlier census, read as finished closed patterns (all their
unheld pairs decidable).

## Prior work in the program

`python3 -B scripts/track.py objects "birth choices most failing pairs maximum weight sign forced" --until 2026-11-27 --exclude MOST-FAILING-20261127-001`
`python3 -B scripts/track.py objects "maximum weight codeword selection principle closing sign" --until 2026-11-27 --exclude MOST-FAILING-20261127-001`

- `LOCAL-COMMUTE-20261127-001` — same object and population: its birth choices, closures and the half-and-half sign;
  this study adds a principle that selects among them.
- `NO-WHOLE-STATE-20261126-001` — a relative: rule R read off the whole forces a sign where it keeps a state (odd at 12 of
  the 17 reached types where it does, even at 5); the maximum reduces to that sign wherever rule R at birth keeps a state.
- `SIDE-SIGN-20261126-001` — a relative: signed weightings made from a swap; signs supplied, not selected.
- `OVERLAP-READ-20261111-001`, `SETTING-AS-REREAD-20261123-001`, `TWO-RELAY-PADDING-20261115-001` — unrelated objects
  matched on shared words.
- A full-text search for an earlier selection principle among commutation choices found none.

## Settled by construction (stated, not tested)

- At the 82 closures where the natural birth rule keeps a state, the maximum is that rule's choice alone (the only word
  using every pair), so the principle forces its sign: odd at 53, even at 29. The principle therefore cannot force odd
  everywhere.
- Two pairs whose members have the same holders contribute identically to every check and to the cost.
- At a closure where the four-knot closure is reached, the maximum's sign is the majority parity of the three pairings'
  counts of failing pairs (the reviewer's hand result); the control there takes a doubled meeting's two pairs when there
  is one (even).
- Where the natural rule loses its state, it has no sign of its own (its cost depends on the order of the knots), so
  nothing ties the maximum's sign to it.

## Predictions (frozen)

All counts are under one vote per census start unless marked.

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates: at the ring of three's closure the maximum is the readers' matching alone, forced odd; at every closure with at most 14 free choices, exhaustive enumeration gives the same weights and verdicts as the integer programs; every program is solved to proven optimality (zero gap), its optimum checked against the parity checks, and its sign recomputed in a second order of the knots; at the 82 closures where the natural rule keeps a state, the maximum is every decidable pair and the verdict is that rule's sign. A program not solved to optimality within its time limit is reported unsettled, never as a verdict. | any gate fails |
| P1 | The reviewer's hand cases: at census start 17's closure (four knots, single meetings) the maximum and the control coincide and both force odd; at start 24's (one doubled meeting) the maximum forces odd with 3 failing pairs and the control forces even with 2; at start 43's the maximum forces even; at start 57's the natural rule keeps a state and the maximum forces even; on the closed pattern of four knots around a fifth holding one distinction of each (the literature's wheel), the maximum is a single word of 8 failing pairs, even, and the control (four words of 3) forces even; on the wheel of five around a sixth the maximum has 15 failing pairs and is free; every closure whose control has 2 failing pairs has a doubled meeting, and the control there forces even. | any case differs |
| P2 | The maximum forces the sign (one value on every maximum-weight birth choice) at more than half of the 1,177 closures. | at half or fewer |
| P3 | Measured, not predicted: how often the maximum forces odd, even or neither, at the 1,095 closures where the natural rule loses its state and at the 82 where it keeps one; how often the control and the holder-type count force a different sign from the maximum; the round-by-round maximum at the 86 later closures; and the same counts on the 173 census types, one vote per type. | — |

P2 is a judgment: the maximum-weight words of a small code are few, but genuine ties with both signs exist (the wheel of
five). P1's cases were worked by hand by the reviewer; the wheels were not checked against the run's rows.

## Runs and stop rule

One script, `most_failing.py`: each closure is regrown and its birth choices rebuilt with the commutation-at-birth study's
code (`local_commute.py`). The optima come from exact integer programs (scipy's `milp`, HiGHS, zero relative gap, 60
seconds per program); each parity check is an even sum with one integer variable, and the sign is fixed by one more such
equation. Exhaustive enumeration checks every closure with at most 14 free choices and counts its maximum and minimum
words. A prefix is timed first; the whole run is expected to take minutes under a 4 GiB cap with one thread. The study
stops when every prediction is scored.

## Review before the freeze

The advisor was unavailable (logged in `docs/ADVISOR_HIVEMIND.md`). An independent reviewer (a separate session,
read-only, reasoning by hand with no computation) checked the first draft. Changed before the freeze in response:

1. The first draft's P3 (the control forces a different sign somewhere) is settled by hand at start 24, so it moved to P1
   with the other hand cases, and the comparison became a measured count.
2. The first draft's P2 (odd forced more often than even where the natural rule loses its state) rested on that rule's
   sign, which does not exist there; the hand cases lean neither way, so it became a measured count.
3. The integer programs: zero gap required, a time limit means unsettled, a second-order sign check, and "no even nonzero
   word" read as none.
4. Two variants added: holder types (the maximum weighs meeting multiplicities, a counting artifact) and round by round
   (at later closures the maximum is not itself a choice made at birth).
5. A second weighting: the 173 census types, one vote per type.
6. Words: "free choices" for the code's dimension; "as many failing pairs as a state allows" and "differ from rule R on
   the fewest pairs" for distance words.

## Results (27 November)

The run took 186 seconds under a 4 GiB cap with one thread ([summary](summary.json), [gates](gates.json),
[rows](results.jsonl), [census types](census_types.jsonl)). Counts are one vote per census start unless marked.

| # | Verdict | Count |
| --- | --- | --- |
| G | holds | The ring of three's maximum is the readers' matching alone, forced odd; enumeration agrees with the programs at all 386 closures with at most 14 free choices; every one of the 1,177 maxima passes its parity checks and the second-order sign check; at all 82 closures where the natural rule keeps a state, the maximum is every pair and the verdict is that rule's sign; no program was left unsettled. |
| P1 | holds | Start 17: maximum and control both 3 failing pairs, both forced odd. Start 24: maximum 3, forced odd; control 2, forced even. Start 43: maximum forced even. Start 57: the natural rule keeps a state; maximum forced even. The wheel of four: one maximum word of 8 failing pairs, even; four control words of 3, even. The wheel of five: maximum 15 failing pairs, free (13 maximum words). All 1,135 closures whose control has 2 failing pairs have a doubled meeting, and there the control forces even. |
| P2 | holds | The maximum forces the sign at 948 of the 1,177 closures (81%). |

**P3, measured.**

| Principle | Forced odd | Forced even | Free |
| --- | ---: | ---: | ---: |
| The maximum, all 1,177 closures | 360 | 588 | 229 |
| — where the natural rule loses its state (1,095) | 307 | 559 | 229 |
| — where it keeps one (82) | 53 | 29 | 0 |
| — closing in round 1 (1,091) / round 2 (85) / round 3 (1) | 348 / 12 / 0 | 534 / 53 / 1 | 209 / 20 / 0 |
| The control, the fewest failing pairs above none | 1 | 1,152 | 24 |
| The maximum counted once per holder type | 619 | 241 | 317 |
| One vote per census type (173 types): the maximum | 49 | 60 | 64 |
| — the control | 1 | 64 | 108 |
| — the maximum per holder type (identical: the census types have no doubled meeting) | 49 | 60 | 64 |

- Where both force a sign, the control and the maximum disagree at 345 of 927 closures, and the holder-type count and the
  maximum at 199 of 719.
- Round by round at the 86 later closures: 19 close odd and 67 even (no dead end), agreeing with the maximum at 62 of the
  66 where the maximum forces a sign.
- Where enumerated, the maximum is a single word at 131 closures, two words at 74 and three or more at 181.

So the maximum makes the sign mostly determined, but in both directions, and the direction depends on how the principle
counts: by pairs it forces even more often than odd, by holder types odd more often than even, and on the census types,
where the two counts coincide, it splits 49 odd to 60 even with 64 free. The control forces even almost everywhere.
