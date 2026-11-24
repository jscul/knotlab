# A growth law in which a short knot pays with a shared distinction: draft result

Ticket `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A`, experiment `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001`.
Draft by the implementing sub-agent from the frozen pre-registration ([preregistration.md](preregistration.md), commit
43762c5b04). Verdicts apply the note's "Fails when" column to the data; the thread judges them. Referee pending. No
definition was changed and nothing was tuned after values were seen. Every reading taken where the note left a choice,
and every limit met, is in
`experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law/deviations.md`
(section A written before the first run). Full tables: `artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law/tables.md`.

Rule R, as implemented (`rlaw.py`): groups, demand and fresh counts are the recorded operator's, read from the full
holdings; a live knot that owes more than its loose distinctions gives its loose ones to its first births in the
engine's order and pays each further birth with a distinction it shares (two or more holders at the round's start),
not held by another parent of that birth and not already paid by it this round; convention O takes the oldest (smallest
name) allowed, N the newest; if none is allowed the round stalls (a residual stall). Under parity a birth gets no fresh
distinction exactly when the GF(2) vector of what it takes lies in the span of all old knots' stars.

## Verdicts

| # | Verdict | Numbers |
| --- | --- | --- |
| G | **Passed** | Every check below agrees; nothing failed. |
| P1 | **Holds** | 0 of 18,694,159,334 allowed words fail to extend, over 772,480 rounds and 6,158,480 births (4,134,008 with a shared distinction, 610 with no fresh distinction), both laws. |
| P2 | **Holds** | Residual stall at round 1 in 102 (O) and 85 (N) of the 744 per law, 80 under every allowed choice; with the 13 starts that have no live knot, 115, 98 and 93 of 744 make no birth at round 1 (15.5%, 13.2%, 12.5%), fewer than half. |
| P3 | **Holds** | Four holders reached in 108 (O) and 97 (N) of the 744 per law (never five); births per round differ between the conventions on 478 (parity) and 471 (not-all-equal) of the 744. |
| P4 | **Fails** | Under R the parity closing keeps a side whose outcome depends on the far edit (Alice: 1 at 00, 0 at 01). The ordinary half holds: both set-ups have a far-edit dependence under ordinary growth. |
| P5 | **Fails** | The bound holds under R: the largest distance of a changed birth is 3 or less at every round (bound 3t + 3 is 6 at t = 1), on 199 (O) and 200 (N) of 200 pairs per law without a residual stall. But no draw has a changed birth beyond distance 6 under ordinary growth: no start of the 200 has a knot farther than 5 from the edited knot, so the clause cannot be met on this sample. |

## Row G

| Check | Result |
| --- | --- |
| R (O and N) and rlaw's ordinary mode against the recorded driver `lib.grow`, the 280 funded draws per law, 12 rounds or 5,000 knots | 280/280 identical (holdings, knots per stage, outcome) for each, both laws; no short knot, no payment; every round (2,528 parity, 3,360 not-all-equal per rule) also matched against the recorded `end_operator.step` on the same end |
| Test (b): the seven recorded sources, 16 rounds or 20,000 knots, R (O and N) against the recorded driver | 28/28 R histories identical (SHA-256 of the full holdings, knots per stage, outcome, first failing step); 0 short knots, 0 payments |
| Elimination against the shortcut (implied exactly when the round's only birth), every parity birth of all 1,024 ordinary histories | 25,257 births, 0 disagreements; the 78 closings met all implied |
| Elimination against enumeration (the parity of what a birth takes is the same on every allowed word), every stage of at most 20 distinctions in rounds 1 and 2 of R on all 1,024 draws | 5,635 births on 1,196 stages, all agree; 76 implied |
| The two closings of test (d) at setting 00, ordinary growth | implied by the shortcut, by elimination and by enumeration |
| Rounds of the test (c) runs also run by the recorded code | groups 41,967, lookaheads 41,583, whole rounds with no short knot 39,033: all equal in groups, parents and demand; fresh counts equal on 38,015 and different on 1,018, every one of them a sole birth that the replaced closing test does not find implied (see test (c)) |
| The C and Python group searches (one algorithm; deviations B1), every end and lookahead of R on all draws up to 400 candidate classes | 41,428/41,428 equal |
| The next-round cap shortcut (deviations B2) against full computation, convention O, both laws | 28/28 verified agree; of the 52 histories it ended, 22 have last lookaheads above 200,000 maximal groups and 2 (parity, arm 0 draw 50 and arm 1 draw 156) exceeded the ten-minute run; their not-all-equal histories, identical, were verified |

## P1, test (a): extension by enumeration

Every round t to t+1 of an R history whose stage t has at most 22 distinctions; every allowed word of stage t enumerated,
and for every birth every assignment of its fresh distinctions.

| Source | Histories | Rounds | Births | With a shared distinction | With no fresh distinction | Allowed words checked | Failing | Full next-stage cross-checks (equal) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| test (c), conventions O and N, both laws | 3,662 | 7,287 | 28,856 | 6,182 | 184 | 141,910,112 | 0 | 4,410 (4,410) |
| test (d), R | 48 | 48 | 144 | 16 | 4 | 83,336 | 0 | 40 (40) |
| test (e), R | 1,598 | 3,503 | 12,913 | 260 | 119 | 66,098,818 | 0 | 2,364 (2,364) |
| test (c), every allowed choice, rounds 1 and 2 | 780,267 choice histories | 761,642 | 6,116,567 | 4,127,550 | 303 | 18,486,067,068 | 0 | - |
| all | | 772,480 | 6,158,480 | 4,134,008 | 610 | 18,694,159,334 | 0 | 6,814 (6,814) |

798,642 rounds of the enumerated choices have a stage of more than 22 distinctions and are not covered.

## Test (b): the seven recorded sources

Identical under R and ordinary growth, both laws, both conventions (row G): the five-founder clock and archived start 00
alive at 16 rounds (85 and 702 knots), the other five stopped by the 20,000-knot cap as recorded; first failing step 1
for six sources and 2 for the 21-knot structure; most holders 2; no payment in any round.

## Test (c): the 744 draws per law that stall at once under ordinary growth

Outcomes under R within 12 rounds or 5,000 knots (the other 280 draws per law: identical to ordinary growth):

| Law | Convention | Residual stall at round 1 | No live knot | Residual stall later | Closed | Alive at 12 rounds | Cap | Growth kind: stalled / bounded / growing |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| parity | O | 102 | 13 | 0 | 17 | 588 | 24 | 115 / 176 / 453 |
| parity | N | 85 | 13 | 0 | 21 | 604 | 21 | 98 / 191 / 455 |
| not-all-equal | O | 102 | 13 | 0 | 0 | 605 | 24 | 115 / 160 / 469 |
| not-all-equal | N | 85 | 13 | 0 | 0 | 625 | 21 | 98 / 171 / 475 |

Under ordinary growth all 744 are of stalled kind. The recorded growth-kind function and the births-based kind agree on
every history (no residual stall after round 1).

| Law | Convention | Most holders 2 / 3 / 4 | Largest | First failing step of the operator test: none / 1 / 2 / 3 / 4+ |
| --- | --- | --- | ---: | --- |
| parity and not-all-equal (same) | O | 115 / 521 / 108 | 4 | 162 / 196 / 301 / 83 / 2 |
| parity and not-all-equal (same) | N | 98 / 549 / 97 | 4 | 152 / 215 / 299 / 77 / 1 |

The operator test: the pattern of which knot holds which distinction is, in the literature's words, a planar graph.
Under ordinary growth none of the 744 fails (none grows). Under R no stage 0 fails; "none" counts the starts that make no
birth (115, 98) and those that pass at every stage reached (47, 54).

**Every allowed choice, rounds 1 and 2** (`test_c_enum.py`; the same under both laws except where stated). Of the 1,024
draws per law, 13 have no live knot, 280 no short knot, 731 a short knot. For 80 of the 731 no allowed choice exists:
in every one some short knot owes more than it holds in all (loose and shared). The other 651 have 389,759 allowed
round-1 choices (largest 46,656 on one draw); on 22 of them convention O residual-stalls although a choice pays, on 5
convention N does. Round-2 births depend on the choice on 492 of the 651. After two rounds the most holders over all
choice histories are 4 in 272,218 (parity) and 272,122 (not-all-equal) and never more. Under parity, on one draw
(arm 3, draw 55), 3 of its 192 round-1 choices leave a short knot at round 2; it pays under each of its 64 allowed
round-2 choices. The conventions' round-2 births are among the enumerated ones in
1,275 of 1,275 cases (a consistency check: each convention is one of the choices).

**Do the conventions give the same births per round?** Parity: same on 266 of 744, different on 478 (453 of them with
both histories alive through round 2), same outcome on 664. Not-all-equal: 273, 471 (446), 696. Example (arm 0, draw 3):
O 7, 6, 4, 1, 1 and N 7, 9, 13, 18, 23 births in rounds 1 to 5.

**Sole births under R.** Once a payment has given a distinction a third holder, the sum of all knots no longer leaves
the loose distinctions alone, and a round's only birth (which takes every loose distinction) is mostly not implied:
under parity 482 (O) and 536 (N) sole births get a fresh distinction and the history continues one birth per round,
where the recorded shortcut would have closed it; 17 and 21 sole births are implied and close. These are the 1,018
rounds of row G whose fresh counts differ from the recorded operator's.

## P4, test (d): the stalling set-ups

Edits as settings (setting 1 adds the optional loose distinction at the side's holder), one complete round, the
recorded readings. Weights on the start: the prepared words (parity 256 and not-all-equal 3,086 for the five-knot stall;
8 and 34 for the three-knot closing; 32 and 428 for the supplementary six-knot closing), each cell a point mass on one
outcome pair; every allowed word of every edited stage extends. The ordinary rows reproduce the recorded tables.

| Set-up | Law | Rule | Outcomes 00, 01, 10, 11 | Alice: own / far | Bob: own / far | Four-correlation value (CHSH in the literature's name): signed, largest |
| --- | --- | --- | --- | --- | --- | --- |
| two-sided stall, 5 knots, 13 distinctions | both | ordinary | 00, 00, 00, 11 | yes / yes | yes / yes | 2, 2 |
| two-sided stall | both | R, O and N, and every allowed choice (16, 4, 4, 1 choices) | 11, 11, 11, 11 | no / no | no / no | not reported (no own-edit dependence) |
| parity closing, 3 knots, 6 distinctions | parity | ordinary | 10, 01, 00, 01 | yes / yes | yes / no | 0, 4 |
| parity closing | parity | R, O and N (no short knot: one choice) | 10, 01, 00, 01 | yes / yes | yes / no | 0, 4 |
| parity closing | not-all-equal | ordinary and R | 00, 01, 00, 01 | no / no | yes / no | 2, 2 |
| supplementary: closing with a three-parent birth, 6 knots, 11 distinctions | parity / not-all-equal | ordinary and R | as the three-knot closing | as the three-knot closing | as the three-knot closing | 0, 4 / 2, 2 |

Under R the stall disappears and with it every dependence: each mark is always handed out, so each side reads 1 in every
cell. The closing set-up has no short knot, so R plays it as ordinary growth; the replaced closing test still finds
Alice's birth implied only when Bob's holder is spent (at 01 Bob's new loose distinction leaves the birth's parity free),
so Alice's outcome still depends on the far edit.

## P5, test (e): pace

200 draws (the first 200 funded, in draw order; 96 have 4 knots, the largest 8), one loose distinction added at a knot
drawn by seed 2026112330. Largest distance of a changed birth by round:

| Law | Rule | t = 1 | 2 | 3 to 12 | Pairs with a residual stall | Pairs with a stall | Pairs above 3t + 3 | Pairs with a changed birth beyond 6 at t = 1 |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| parity | ordinary | 3 | 3 | 3 at every round | 0 | 39 | 0 | 0 |
| parity | R, O | 2 | 3 | 3 at every round | 1 | 0 | 0 | 0 |
| parity | R, N | 2 | 2 | 2 at every round | 0 | 0 | 0 | 0 |
| not-all-equal | ordinary | 3 | 3 | 3 at every round | 0 | 39 | 0 | 0 |
| not-all-equal | R, O | 2 | 3 | 3 at every round | 1 | 0 | 0 | 0 |
| not-all-equal | R, N | 2 | 2 | 2 at every round | 0 | 0 | 0 | 0 |

Every pair has a changed birth at round 1. Largest distance from the edited knot in the start: 1 in 32 draws, 2 in 78,
3 in 69, 4 in 19, 5 in 2. Under ordinary growth the edit stalls the edited start at round 1 in 39 pairs; there every
unedited birth of round 1 is changed, and the largest distance of a changed birth equals the start's largest distance
from the edited knot in 37 of the 39. The stall does reach the whole start at once; the sample's starts are too small to
put a knot beyond distance 6. No round was left uncompared.

## Payments with a shared distinction under R

| Test | Rounds with a payment / rounds | Births with a shared distinction / births |
| --- | --- | --- |
| (b) seven sources, 28 R histories | 0 | 0 |
| (c) 744 draws, parity, O / N | 629 / 7,319 and 646 / 7,504 (all at round 1) | 1,518 / 146,365 and 1,593 / 144,279 |
| (c) 744 draws, not-all-equal, O / N | 629 / 7,468 and 646 / 7,688 (all at round 1) | 1,518 / 147,138 and 1,593 / 145,218 |
| (c) every allowed choice, rounds 1 and 2 (rounds with at most 22 distinctions) | see test (a) | 4,127,550 / 6,116,567 |
| (d) two-sided stall, per law and convention | 3 / 4 (settings 00, 01, 10) | 4 / 20 |
| (e) 400 histories per law and convention, parity O / N | 38 / 4,170 and 39 / 4,133 | 63 / 42,966 and 67 / 42,073 |
| (e) not-all-equal O / N | 38 / 4,788 and 39 / 4,800 | 63 / 46,514 and 67 / 45,886 |

In tests (c) and (e) every payment is in the first round of a history (of an edited start in (e)); no later round has a
short knot under either convention.

## Faults and limits

1. The recorded group search could not finish R's rounds (minutes to hours each); an exact re-implementation is used and
   checked against it on every round small enough (deviations B1).
2. A round followed by a certain cap keeps fresh counts that are lower bounds (26 and 22 histories per law in test (c));
   no tested quantity depends on them (deviations B2).
3. P5's ordinary clause asks for a distance the sample cannot contain (deviations B7).
4. A fault in my prefix helper dropped short histories from test (a) at first; repaired and rerun, rows identical
   (deviations B3).

## Reproduce

From the repository root, with
`E=experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law` and
`P="timeout 600 prlimit --as=12884901888 .venv/bin/python -B"`. Each line is one or more runs of under ten minutes.

```
$P $E/gate.py --part a --law parity; $P $E/gate.py --part a --law nae         # G: funded draws (3 s each)
$P $E/gate.py --part b; $P $E/gate.py --part c; $P $E/gate.py --part d         # G: elimination checks (1 to 4 s)
for law in parity nae; do for a in 0 1 2 3; do $P $E/gate.py --part f --law $law --arm $a; done; done
                                                  # G: searches and shortcut; parity arms 0 and 1 run with
                                                  # --start S --stop T in chunks of 32, 8 and 1 draws (deviations B5)
for s in seven_knot nine_knot_drawn knots21_two_clocks five_founder_clock archive_start-00 archive_start-04 archive_start-13; do
  for law in parity nae; do $P $E/test_b.py --source $s --law $law --rule ref
    $P $E/test_b.py --source $s --law $law --rule R --conv O; $P $E/test_b.py --source $s --law $law --rule R --conv N; done; done
for law in parity nae; do for c in O N; do for a in 0 1 2 3; do $P $E/test_c.py --law $law --conv $c --arm $a; done; done; done
for law in parity nae; do for a in 0 1 2 3; do for s in 0 64 128 192; do
  $P $E/test_c_enum.py --law $law --arm $a --start $s --stop $((s+64)); done; done; done        # up to 160 s each
$P $E/test_d.py
for law in parity nae; do $P $E/test_e.py --law $law --rule ordinary
  $P $E/test_e.py --law $law --rule R --conv O; $P $E/test_e.py --law $law --rule R --conv N; done
for part in c d e enum; do $P $E/test_a.py --part $part; done                  # after the tests above
$P $E/summarize.py                                                             # summary.json, tables.md
```

Gate part e of `gate.py` was not run as a separate script: its checks run inside every `test_c.py` run (row G, "rounds
of the test (c) runs"). Outputs are under
`artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law/`
(PRUNED.md lists what was deleted). A rerun of all 16 test (c) runs and 6 test (e) runs reproduced every row.

## Not done

The cap shortcut is unverified on 24 of 52 histories (deviations B2, B5). Test (a) does not cover rounds whose stage has
more than 22 distinctions. The scaffold records, the assumption register and the epic ledger are the thread's.
