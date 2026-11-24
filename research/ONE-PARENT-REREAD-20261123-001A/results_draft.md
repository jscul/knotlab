# A one-parent birth that also takes a distinction its parent shares: draft result

Ticket `ONE-PARENT-REREAD-20261123-001A`, experiment `ONE-PARENT-REREAD-20261123-001A-E001`, 2026-11-23. Draft written
by the implementing sub-agent from the frozen [pre-registration](preregistration.md) (sha256 36ecc92c...6e8c, freeze
commit f3f5c9a1d1). The verdicts below apply its "Fails when" column to the data; the thread judges them. Referee
pending. Readings taken where the note was open, and the limits met, are in
[deviations.md](../../experiments/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread/deviations.md).
Outputs: `artifacts/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread/`;
`summary.json` there holds every number below. Ticket A's engine `rlaw.py` had the sha256 named in the contract
(29aa3d91...d8f8) at every import and at the end.

Words. A *re-reading birth* is a one-parent birth that takes its parent's loose distinction and one distinction the
parent shares (rule Q); *sibling births* are the re-reading births of one parent in one round. A *hidden excess* is a
four-correlation score above 2 with both complete records unchanged by the far setting, under the supplied setting
births and with every allowed word of the finished structure counted equally. A *gain* is a hidden excess at a grown
stage of a part that has none at stage 0. H(t) is the largest number of holders of one distinction at stage t.

**With one law for every newborn (every newborn not-all-equal), 8 of the 27 parts that one added knot lifts gain a
hidden excess at round 1, and only where the two sibling births take different shared distinctions, which is a choice
neither convention makes: 61/30 in six parts and 31/15 in two. Under either convention no part gains. With laws given
to newborns, all 27 gain at round 1 (one sibling not-all-equal and the other parity: 109/54 or 55/27, under either
convention) and no other part gains at any stage. Every gain at round 1 is lost when the shared input is removed. In the
sparse draws the oldest-first convention adds one holder a round to one distinction (up to 14 holders by round 12);
under the newest-first one H never grows after round 3 (at most 6). Growth becomes mostly bounded, and 13 parity
histories that live under ordinary growth close under rule Q, so P6 fails.**

## 1. Denominators

| Test | What was run | Enumerated in full | Drawn |
| --- | --- | --- | --- |
| (a) sources | 7 recorded sources, not-all-equal, ordinary growth and rule Q (O, N), 12 rounds or 5,000 knots | all 21 histories | none |
| (b) draws | 280 funded sparse draws per law (seed 2026112301; 69, 29, 69, 113 by arm), parity and not-all-equal, ordinary growth and rule Q (O, N) | all 1,680 histories | the draws themselves are the review-leads sample |
| (c) census | 5,761 parts (two holders at most, no hidden excess, no stall at once); 587 have more than 20 distinctions at stage 0 and make no round; 5,174 grow. The 6,312 that stall are counted (each stalls under rule Q too) | round-1 choices: all for 5,164 parts (1 to 64 choices); 3,787 parts with every choice and every law assignment of every history | 10 parts with 72 or 128 choices: O, N and 62 drawn (seed 2026112370); 5,709 histories of 1,377 parts with 4,096 drawn assignments (seed 2026112371) |
| (c) histories | 30,868 = 5,761 (O) + 5,761 (N) + 19,346 (choice); 29,694 grow; 21,468 distinct structures counted part by part | 23,985 grown histories with every assignment | 620 choice histories from drawn choices |
| (c) tables | uniform arm: 45,439 (one per grown stage); mixed arm: 49,377,668 (stage, assignment), 14,588,787 effective, 10,087,841 contracted after caching | uniform arm: every table except the drawn choices of 10 parts | mixed arm: tables of the 5,709 drawn-assignment histories |

The 27 liftable parts are covered in full: 6 histories each (O, N and their 4 round-1 choices), 7 knots, every
assignment (4 newborns, 81 assignments), stages of 9, 10 and 11 knots.

## 2. Verdicts

| # | Prediction | Verdict | Evidence |
| --- | --- | --- | --- |
| G | Checks of the code | **Holds** | Re-reading off equals the recorded driver on 7 of 7 sources and 280 of 280 funded draws under each law (stars, knots per stage, outcome; 0 disagreements of the elimination test with the closing shortcut under parity). On 500 drawn parts (seed 2026112372) it gives ticket B's stars, knots, distinctions and outcome on 500 of 500 and its numbers of tables, hidden tables and tables with a hidden excess on 1,179 of 1,179 stages (942,841 tables, none with an excess). Direct contraction equals word-by-word enumeration on 100 of 100 drawn grown stages (99 with re-reading births); the reduction equals direct contraction on 2,198 of 2,198 stages (2,008,615 tables, 227 parts). Every old word extends on all 5,487 rounds of (b) whose stage has at most 22 distinctions (86,653,468 words, 9,623 births of which 6,577 re-read and 156 get no fresh distinction; 5,179 projection checks equal). Allowed observer words never change: 0 changes in 49,377,668 mixed-arm and 45,439 uniform-arm tables. No knot is short in any rule-Q history (0 stalls in (a), (b) and (c); in the 28 capped histories, 8 of (a) and 20 of (b), the round after the last was not planned, the cap acting first). Stage-1 tables with exactly one not-all-equal re-reading birth with one fresh distinction and every other newborn parity equal ticket C's table 2M − M_T for that set: 1,620,589 of 1,620,589 tables, 53,973 births (every such birth in every history), and 324 of 324 tables ticket C stored. All 680 stage-1 gains (664 mixed, 16 uniform) are lost under the control. |
| P1 | Uniform arm: some part gains at round 1 for some choice | **Holds** | 16 tables, 8 parts, 16 choice histories (2 per part): 61/30 in 6 parts, 31/15 in 2. All in fully enumerated choices. |
| P2 | Uniform arm: under either convention, where siblings take the same distinction, no part gains at round 1 | **Holds** | 0 of 10,348 convention histories of the 5,174 growing parts gain at round 1 (at any stage). Beside it, not judged: 0 gains in choice histories whose siblings all took one distinction. |
| P3 | Every part that gains, in either arm, is hidden at exactly 2 at stage 0 | **Holds** | The 27 gaining parts (8 uniform, 27 mixed) are all hidden at exactly 2 at stage 0. |
| P4 | Mixed arm: all 27 liftable parts gain at round 1, and no other part gains at any stage | **Holds (partly a sample)** | 27 of 27 gain at round 1 (664 tables), 0 other parts gain at any stage. The 27 are enumerated in full; 1,387 of the other parts rest partly on drawn assignments or choices, so "no other part" is a census for 3,787 parts and a sample for the rest. |
| P5 | (b): under O some draw reaches 8 holders by round 12; under N no draw's H grows after round 3 | **Holds** | Under O, 239 not-all-equal and 161 parity draws reach at least 8 (largest 14). Under N, 0 draws (either law) grow after round 3; largest 6. |
| P6 | (b): every draw alive at 12 rounds under ordinary growth is alive at 12 rounds under rule Q | **Fails** | Under parity, 8 (O) and 5 (N) of the 202 draws alive under ordinary growth close under rule Q. Primary reading (alive = 12 rounds or 5,000 knots reached without closing or stalling): 13 failing histories. Strict reading (12 rounds made): 33 (the 13 and 20 capped histories). Under not-all-equal no draw closes (7 (O) and 3 (N) reach the cap). |

## 3. (a) The seven recorded sources, not-all-equal

| Source | Rule | Re-reading births per round (rounds with any) | Knots per stage | Growth kind | H(t), t = 0, 1, ... | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| seven_knot | ordinary, Q-O, Q-N | none | 7, 15, 27, 46, 78, 134, 235, 420, 765, 1420, 2683 (all three equal) | growing | 2 throughout | cap |
| nine_knot_drawn | ordinary | (one-parent births 1 at round 1) | 9, 24, 54, 117, 259, 597, 1426, 3516 | growing | 2 | cap |
| | Q-O | 1 at round 1 | 9, 24, 57, 134, 324, 829, 2289 | growing | 2, then 3 | cap |
| | Q-N | 1 at round 1 | 9, 24, 55, 123, 283, 686, 1784 | growing | 2, then 3 | cap |
| knots21_two_clocks | ordinary, Q-O, Q-N | none | 21, 33, 57, 113, 256, 634, 1676, 4662 (equal) | growing | 2 | cap |
| five_founder_clock | ordinary, Q-O, Q-N | none | 5, 10, ..., 65 (5 a round; equal) | bounded | 2 | horizon |
| archive_start-00 | ordinary | (3 at round 1) | 6, 14, 26, 41, 56, 70, 84, 99, 108, 127, 153, 184, 251 | growing | 2 | horizon |
| | Q-O | 3 at round 1, then 1 in each of rounds 7 to 12 | 6, 14, 22, 30, 36, 38, 39, 40, 41, 42, 43, 44, 45 | bounded | 2, 3 (rounds 1 to 7), 4, 5, 6, 7, 8 | horizon |
| | Q-N | 3 at round 1 | 6, 14, 22, 30, 38, ..., 102 (8 a round) | bounded | 2, 4 throughout | horizon |
| archive_start-04 | ordinary | (6 at round 1) | 6, 16, 32, 58, 95, 158, 285, 1300, 2081 | growing | 2 | cap |
| | Q-O | 6 at round 1, then 1 in each of rounds 5 to 12 | 6, 16, 25, 32, 33, 34, ..., 41 | bounded | 2, 4 (rounds 1 to 6), 5, 6, 7, 8, 9, 10 | horizon |
| | Q-N | 6 at round 1, then 1 in each of rounds 5 to 12 | 6, 16, 24, 27, 28, ..., 36 | bounded | 2, 6 throughout | horizon |
| archive_start-13 | ordinary | (8 at round 1) | 7, 22, 49, 105, 220, 500, 1368 | growing | 2 | cap |
| | Q-O | 8 at round 1 | 7, 22, 37, 58, 89, 146, 264, 632, 2332 | growing | 2, 5 | cap |
| | Q-N | 8 at round 1 | 7, 22, 47, 81, 140, 244, 573, 2327 | growing | 2, 5 | cap |

Ordinary growth makes one-parent births at round 1 only, 0, 1, 0, 0, 3, 6 and 8 of them (as known). Rule Q changes the
four sources that have them and leaves the other three identical (seven_knot and five_founder_clock to the last
distinction; knots21_two_clocks up to the fresh counts of the round before the cap, which the cap shortcut gives as lower
bounds, deviations B2). The re-reading births of round 1 get 2 to 7 fresh distinctions (the new meetings raise the
demand). Two archive starts that grow without bound under ordinary growth become bounded under both conventions. Under
O each ends with one birth a round that re-reads the distinction its parent re-read (distinction 95 of archive_start-00
from round 7, distinction 80 of archive_start-04 from round 5), which gains one holder a round (8 and 10 holders at
stage 12). Under N archive_start-04 also ends with one birth a round, re-reading a new distinction each round (60 to 67;
H stays 6, reached at round 1 when four siblings take one distinction), and archive_start-00 makes 8 births a round with
no re-reading after round 1. The operator test fails at step 1 for every source and rule, except knots21_two_clocks
(step 2), as under ordinary growth.

## 4. (b) The funded sparse draws

Weighting: the review-leads epic's sparse draws (labelled trees on 4 to 8 knots, each knot filled to three places plus
one loose distinction with chance 1/4, 0 to 3 extra meetings; seed 2026112301), the 280 per law whose first round
extends.

**Outcomes and growth kinds** (recorded growth kind; the kind from births alone is the same in every row).

| Law | Rule | Outcome | Growing / bounded | Births per round equal to ordinary |
| --- | --- | --- | --- | --- |
| not-all-equal | ordinary | 280 horizon | 229 / 51 | |
| | Q-O | 273 horizon, 7 cap | 23 / 257 | 13 |
| | Q-N | 277 horizon, 3 cap | 16 / 264 | 12 |
| parity | ordinary | 202 horizon, 78 closed | 151 / 129 | |
| | Q-O | 195 horizon, 78 closed, 7 cap | 23 / 257 | 62 |
| | Q-N | 202 horizon, 75 closed, 3 cap | 16 / 264 | 61 |

Under parity the closings are not the same draws: under O, 8 draws alive under ordinary growth close and 8 that close
under ordinary growth live (70 close under both); under N, 5 and 8. Under parity 90 (O) and 89 (N) births get no fresh
distinction (their parity is implied by the old knots); none under not-all-equal.

**Births per round** (sum over the draws; the number of draws still growing falls only in the last rounds and under
parity):

| Law, rule | Rounds 1 to 12 |
| --- | --- |
| not-all-equal, ordinary | 1000, 1179, 1355, 1633, 1966, 2304, 2642, 2980, 3318, 3656, 3994, 4332 |
| not-all-equal, Q-O | 1000, 888, 815, 860, 1057, 1529, 2864, 2203, 3608, 7548, 4714, 3774 |
| not-all-equal, Q-N | 1000, 852, 726, 700, 774, 935, 1232, 1734, 2679, 5141, 4310, 3158 |
| parity, ordinary | 1000, 1097, 1204, 1404, 1659, 1919, 2179, 2439, 2699, 2959, 3219, 3479 |
| parity, Q-O | 1000, 848, 741, 772, 968, 1440, 2774, 2113, 3518, 7458, 4624, 3684 |
| parity, Q-N | 1000, 812, 673, 614, 687, 847, 1143, 1645, 2590, 5052, 4221, 3069 |

Most of the later births are in the few growing draws (23 under O, 16 under N), which reach the cap or the horizon with
thousands of knots. The bounded draws end with 1 to 7 births in round 12: one or two in 234 of the 257 bounded
not-all-equal draws under O and in 238 of 264 under N.

**Re-reading births per round** (not-all-equal; ordinary one-parent births beside them): ordinary 598, 617, 714, 773,
823, 828, 828, ...; Q-O 598, 97, 219, 274, 306, 318, 322, 323, 323, 323, 323, 323; Q-N 598, 100, 228, 284, 322, 332, 335,
336, ..., 336. Every round-1 one-parent birth re-reads (its parent always shares a distinction). Draws with a re-reading
birth after round 1: 240 (O) and 247 (N) of 280; under parity 183 and 193. Under parity 48 draws have no re-reading
birth at all (their round 1 has no one-parent birth, and they close at round 1, 40 of them, or round 2, 8).

**Largest number of holders** (both laws give the same largest values at each stage):

| Stage t | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| largest H(t), Q-O | 2 | 6 | 6 | 6 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
| largest H(t), Q-N | 2 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |

Under O, H grows after round 1 in 240 not-all-equal and 183 parity draws, and in 239 and 161 of them by exactly one in
each of rounds 9 to 12 (the hub the note settles by construction); H at the last stage is 8 to 14 in 239 not-all-equal
draws. Under N, H grows after round 1 in 52 not-all-equal and 4 parity draws, only at round 2 or 3; H at the last stage
is 3 to 6 in every not-all-equal draw. Ordinary growth keeps H = 2.

**First failing step of the operator test** (both laws alike): ordinary never 247, step 3 in 30, step 2 in 1, step 1 in
2; Q-O never 166, step 2 in 105, step 3 in 7, step 1 in 2; Q-N never 164, step 2 in 104, step 3 in 10, step 1 in 2.
Ordinary to Q-O: 74 draws that never fail now fail at step 2 and 7 at step 3; the 30 that failed at step 3 fail at step
2. With three or more holders the test is a reading of the pattern only.

**How a draw closes under rule Q (P6)**, one case, arm 3 draw 17 under parity: knots (0,1,2), (0,3,4), (1,3,5),
(2,4,5,6), (6,7,8). The last knot holds the loose 7 and 8 and shares 6. Round 1 under either convention: two re-reading
births (8,6,f9) and (7,6,f10), one fresh distinction each. Round 2: their only birth takes f9 and f10, whose parity
equals that of 7 and 8, hence of 6, which the first four knots fix; so it is implied, gets no fresh distinction, and no
live knot remains (8 knots, closed). Under ordinary growth the two births get two fresh distinctions each and the draw
lives to 12 rounds (95 knots). The other 12 failing histories have the same end: a round whose sole birth is implied.

## 5. (c) The census of parts

**Growth.** Round 1 makes 151,888 births over the histories, 118,920 of them re-reading (5,076 of the 5,174 growing parts
have a re-reading birth at round 1); rounds 2 and 3 make 22,789 and 9,163 births, 4,747 and 7,524 re-reading. Fresh
distinctions of re-reading births: at round 1, one for 53,973, two for 48,418, three for 13,152, four for 3,377; at
rounds 2 and 3 always one. Sibling births at round 1 take the same distinction in 17,556 histories and different ones
in 4,315; 7,823 have no parent with two. H at the end of a history is 2 to 7 (7 in 18 histories). No history stalls;
6,161 stop after three rounds and 24,707 when a stage passes 20 distinctions (1,174 of them at stage 0).

**Uniform arm (every newborn not-all-equal).** 48 gain tables in 16 histories of 8 parts, all liftable:

| Part (target) | Round-1 choice of the two siblings | Stage 1 | Stage 2 | Stage 3 |
| --- | --- | --- | --- | --- |
| 3031 (103), 4348 (136) | different shared distinctions, both ways | 31/15 | 3830/1863 | 5284/2565 |
| 3072 (104), 3113 (105), 3277 (109), 3430 (113), 4471 (139), 4624 (143) | different, both ways | 61/30 | 3778/1863 | 5207/2565 |

- By round: 16 at each stage, all continuing the stage-1 gain; no gain first appears at stage 2 or 3.
- By choice: all 48 have siblings taking different distinctions at round 1 (later rounds have single re-reading births).
  In these 8 parts the other four histories (O, N and the two choices that give both siblings one distinction) have no
  gain at any stage, and neither has any history of the other 19 liftable parts; at stage 1 all of those are hidden at
  exactly 2.
- By laws: every newborn is not-all-equal in this arm; the 16 stage-1 gains hold the two re-reading births only, the 32
  gains at stages 2 and 3 also the round-2 two-parent birth (and at stage 3 the round-3 re-reading birth).
- By fresh counts: every re-reading birth in every gain has one fresh distinction.
- Other parts: none. Control: 16 of 16 stage-1 gains lost.

**Mixed arm (each newborn even parity, odd parity or not-all-equal).** 6,332 gain tables in 162 histories (every history)
of the 27 liftable parts; no other part gains.

| Stage | Tables | O / N / choice | Laws of the re-reading births | Scores |
| --- | --- | --- | --- | --- |
| 1 | 664 | 108 / 108 / 448 | one not-all-equal, one parity: 648 (all 27 parts, every history, same or different distinctions); both not-all-equal: 16 (8 parts, different distinctions only); both parity: 0 | 109/54 (552, 23 parts), 55/27 (96, 4 parts), 61/30 (12), 31/15 (4) |
| 2 | 1,344 | 216 / 216 / 912 | as stage 1 (continuations) | 109/54, 55/27, 61/30, 31/15, 3778/1863, 3830/1863 |
| 3 | 4,324 | 702 / 702 / 2,920 | 3,028 continue a stage-1 gain; 1,296 are new: both round-1 births parity, the round-2 birth parity, and the round-3 re-reading birth not-all-equal | 109/54 (3,312), 55/27 (576), 61/30 (324), 31/15 (64), 3778/1863 (24), 5207/2565 (12), 3830/1863 (8), 5284/2565 (4); the new ones 109/54 and 55/27 only |

- By choice (round 1): same distinction 4,104 tables, different 2,228; at stage 1, 432 and 232.
- By fresh counts: every re-reading birth in every gain has one fresh distinction (rule Q gives these births
  max(D, 1) = 1; their only meeting is the pair of siblings).
- Two-parent births not-all-equal in a gain: 0 at stage 1, 16 at stage 2, 48 at stage 3.
- The 1,296 new stage-3 gains: the round-2 two-parent birth takes the two siblings' fresh distinctions, and its one
  re-reading birth at round 3 takes its own loose distinction and one sibling's fresh distinction. Through the parity
  newborns its two inputs are tied to the other sibling's two inputs. Checked on part 3072 under O (siblings on y3, s2
  and y2, s2; round 2 on f12, f13; round 3 on f14, f12): with the three earlier newborns even parity, or the first odd,
  or all three odd, the stage-3 table is proportional to the stage-1 table with the second sibling not-all-equal; with
  only the second sibling, or only the round-2 birth, odd it is not; the score is 109/54, hidden, in all five.
- Control: 664 of 664 stage-1 gains lost (every one falls back to exactly 2, hidden).

**Where the other parts stay.** 51 parts are hidden at exactly 2 at stage 0. The 24 that are not liftable (two each of
targets 99 to 110) all grow, every assignment of their 96 histories enumerated; no table of theirs at a grown stage
exceeds 2 (the largest hidden score is exactly 2), and in the uniform arm all 288 of their grown-stage tables are hidden
at exactly 2. The other 5,710 parts (below 2, or
not hidden) never come within 10^-6 of 2: the largest hidden score at any grown stage is 1.692 (mixed arm) and 1.582
(uniform arm) in floating point.

**Known values reproduced.** On the ten parts of the exploration (targets 135 to 144), rule Q gives each sibling one
fresh distinction, as the exploration assumed; both parity gives exactly 2 in all 160 tables; both not-all-equal gives
exactly 2 in 34 of 40 choices and 31/15 or 61/30 in 6 (parts 4348, 4471, 4624, different distinctions); exactly one
not-all-equal gives 55/27 or 109/54, hidden.

### The smallest gain of each arm, in full

Order: fewest knots at the gaining stage, then fewest distinctions, then the smallest score. Both are in part 3072
(target 104, start bitmask 223), 7 knots, 12 distinctions:

Alice nae(x1,x3,s1), even(x1,Ah1,Ah2), nae(x2,x3,s2), odd(x2,Ah1,Ah2); Bob even(y1,Bh1,Bh2), odd(s1,Bh1,Bh2),
even(y1,y2,y3,s2). y2 and y3 are loose; every other distinction has two holders. Stage 0 is hidden with score exactly
2. Round 1 has no group (one live knot): even(y1,y2,y3,s2) makes two one-parent births, handing out y3 then y2; it shares
s2 (with nae(x2,x3,s2); the oldest) and y1 (with even(y1,Bh1,Bh2); the newest). Each sibling gets one fresh
distinction (lookahead demand 1: the two siblings form one pair).

- **Uniform arm: 61/30.** Choice history 1 (not a convention): the first sibling takes y3 and **s2** (two holders before,
  three after), the second y2 and **y1** (likewise); knots nae(y3,s2,f12) and nae(y2,y1,f13). Stage 1: 9 knots, 14
  distinctions, **score 61/30, hidden**. By enumeration of every word of the four finished structures (16
  distinctions; 576, 480, 432 and 360 allowed words): hidden (largest change of a complete record with the far setting
  0), exactly 61/30, the four record tables equal to the old-word table's. Control: nae(y3,f12), nae(y2,f13) gives
  exactly 2, hidden, also by enumeration. With both siblings on s2 (convention O) or both on y1 (convention N) the
  uniform arm stays at exactly 2.
- **Mixed arm: 109/54.** Convention N: both siblings take y1; laws even and not-all-equal: even(y3,y1,f12),
  nae(y2,y1,f13). Stage 1: 9 knots, 14 distinctions, **score 109/54, hidden**. By enumeration (16 distinctions; 320, 288,
  240 and 216 allowed words): hidden (largest change 0), exactly 109/54, record tables equal. Control: even(y3,f12),
  nae(y2,f13) gives exactly 2, hidden, also by enumeration.

All 6,380 gain tables (both arms) were enumerated word by word in the same way and agree in hiding, exact score and
record tables; the evaluator agrees with the recorded scorer on all of them, on their 680 control tables and on 1,000
drawn census tables.

## 6. Readings, limits, what was not done, commands

**Readings** (deviations A): rule Q as a subclass of ticket A's engine, groups and stall of ordinary growth on full
holdings; "shares" read at the start of the round; oldest and newest by name; a birth's fresh count max(D, 3 − i, 1)
with i its number of inputs and D rlaw's lookahead demand from the round's input sets; parity closing by elimination;
the next-round cap shortcut in (a) and (b), whose lower-bound fresh counts enter no reported number; "alive at 12
rounds" read two ways (P6 fails under both); P5 pooled over both laws; choices and assignments drawn with one generator
per part and per history; ticket C's reduction re-read with the number of inputs and re-verified; the control for stage-1
gains only. Seeds chosen here for row G: 2026112372 to 2026112376.

**Limits.** A finite census on parts of the listed structures, 3 rounds or 20 distinctions; 1,387 parts rest partly on
drawn assignments or choices; the sparse draws are one sample of small starts; the conventions, the choices, the laws of
the mixed arm, the observers, the setting births and the equal weighting are supplied. Development runs before the
readings were fixed are listed in deviations A0; they included the sight of the parity closings and caps of (b) before
P6's reading was written.

**Not done.** The control for gains at stages 2 and 3 (the note defines it for stage 1). Every choice for the 10 parts
with more than 64.

**Commands, in run order** (from the repository root; every Python run as
`timeout 600 prlimit --as=12884901888 .venv/bin/python -B <script> <args>` with one thread per numerical library):

1. Development runs of deviations A0 (inline, printed only; the census `dev` files were deleted).
2. `bash experiments/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread/run_jobs.sh experiments/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread/jobs_1.txt`
   (34 runs, six at a time: `q_sources.py --law nae`; `q_draws.py --law nae|parity --arm 0..3`;
   `q_census.py --lo 0 --hi 1000` to `--lo 5000 --hi 6000`; `q_rowg.py --part off` on sources and draws under both laws;
   `q_rowg.py --part stalled`; `--part parts500` in two slices; `--part reduction` in two; `--part addedknot` in four).
3. `bash .../run_jobs.sh .../jobs_2.txt` (8 runs: `q_rowg.py --part stages` in two slices, `--part extension`,
   `--part scorer`, `--part verify` in four slices).
4. `.../q_report.py`, six times (`logs/report_1.log` to `report_6.log`; later runs added cross tables and the numbers
   read after the results, deviations B1 and B6; none changed an earlier number).

Every run ended with status 0 in at most 145 seconds; none was stopped or repeated.
