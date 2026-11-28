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
