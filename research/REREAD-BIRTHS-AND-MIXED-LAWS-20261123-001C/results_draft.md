# Does a birth that takes a shared distinction let growth finish a structure with a hidden excess?: draft result

Ticket `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C`, experiment `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001`,
2026-11-23. Draft written by the implementing sub-agent from the frozen [pre-registration](preregistration.md) (sha256
4887595485b9...065a). The verdicts below apply its "Fails when" column to the data; the thread judges them. Referee
pending. Readings taken where the note was open, and the limits met, are in
[deviations.md](../../experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach/deviations.md).
Outputs: `artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach/`
(`summary.json` collects every number below). Ticket A's engine `rlaw.py` had the sha256 recorded in the contract
(29aa3d91...d8f8) at the start and at the end of this work; every script checked it.

A hidden excess is a four-correlation score above 2 with both complete records unchanged by the far setting, under the
supplied setting births and with every allowed word of the finished structure counted equally. A gain is a hidden excess
at a grown stage of a start whose stage 0 has none.

**Under rule R no start with at most two holders per distinction gained a hidden excess. Seven starts that already held
a distinction three times gained one at round 1, and each of the seven has a gain through a payment** (261 of their
321 gain tables are). In the smallest, a knot that is
short by one pays with a distinction it shares, and the newborn that receives it, a not-all-equal knot on Bob's loose y1
and that shared distinction, lifts the score from exactly 2 to 127/63, hidden. Changed to even parity, it leaves 2.
**One added not-all-equal knot with a fresh distinction lifts 27 two-holder starts to a hidden excess (1,746 sets T).**
Every such T holds exactly one loose distinction, always Bob's y2 or y3, together with one, two or three shared
distinctions, and no round-1 birth under either rule takes any of them. The smallest T has two distinctions, for
example {s1, y2}, and the largest score is 55/27.

## Denominators

| What | Two-holder | Three-holder |
| --- | ---: | ---: |
| Founder starts of ticket B | 12,147 | 37,814 |
| Stalled at round 1 under ordinary growth (arm 1's starts) | 6,312 | 21,575 |
| Residual stall at round 1 under R, convention O / N / both / either | 216 / 197 / 190 / 223 | 5,544 / 5,011 / 4,782 / 5,773 |
| Residual stall after round 1 | 0 | 0 |
| Make at least one round under R, O / N / either | 6,096 / 6,115 / 6,122 | 16,031 / 16,564 / 16,793 |
| Starts whose allowed round-1 choices were all grown (at most 64) / 62 more drawn (more than 64) / no allowed choice | 5,078 / 1,044 / 190 | not asked |
| Histories (conventions O and N + choice histories) | 146,044 (6,312 + 6,312 + 133,420) | 43,150 (21,575 + 21,575) |
| Histories with every choice and every assignment enumerated | 55,254 | 35,650 |
| Histories from drawn choices / with drawn law assignments | 64,728 / 61,038 | 0 / 7,500 |
| Starts covered in full (every allowed choice when asked, every assignment of every history) / partly drawn | 3,731 / 2,581 | 17,552 / 4,023 (both conventions; choices not asked) |
| Tables tested (stage, assignment), stage 0 included / at grown stages | 351,796,504 / 351,650,460 | 52,186,355 / 52,143,205 |
| Grown stages | 157,876 | 34,759 |
| Tables contracted (one per effective assignment, deviations A9) | 12,316,485 | 2,036,967 |
| Starts with a hidden excess at stage 0 (cannot gain) | 0 | 43 |

The largest number of allowed round-1 choices of a two-holder start is 51,840. Convention O's own choice is a residual
stall at 216 starts and N's at 197; at 26 of the former some other choice pays every birth. Payments happen only at round
1: round 1 of every grown history has a paying birth (two-holder: 403,876 of 1,020,289 round-1 births; three-holder:
79,761 of 199,116), and no birth of round 2 or 3 is paying, so no later round needed a convention and no `choiceN`
history arose (deviations A5). Under R a distinction reaches 4 holders in 18,428 two-holder histories and up to 6 in
three-holder ones.

Arm 2: 12,073 two-holder starts with no hidden excess at stage 0 (6,312 of them stall under ordinary growth; 416 more,
with more than 20 distinctions, stall when round 1 is played without the size stop), 31,400,282 sets T (1,360,178 of two
distinctions, 6,597,708 of three, 23,442,396 of four), 17,825,754 of them hidden. Rule R's round-1 origin is decided for
every start except 30 (151,593 sets), which have more than 4,096 allowed choices.

## Verdicts

| # | Prediction | Verdict | Evidence |
| --- | --- | --- | --- |
| G | Checks of the code | **Holds** | 500 drawn two-holder starts with no short knot: rule R by ticket A's engine gives ticket B's stars, knots and distinctions per stage and outcome on 500 of 500, and its numbers of tables, hidden tables and tables with a hidden excess on 1,176 of 1,176 stages (910,881 tables, three-law version); arm 1's reduced evaluation equals the direct contraction on all 676 grown stages. The same on 500 drawn three-holder starts: 500 of 500, 786 of 786 stages, reported. Tables equal word-by-word enumeration on 100 of 100 drawn grown stages of arm 1 (at most 24 distinctions) and 200 of 200 drawn pairs of start and T of arm 2. Allowed observer words never change: 0 changes over every assignment of every grown stage of arm 1; 2M − M_T has the start's allowed words for every T of every start. The ten known starts give 271/135 (targets 135, 136) and 541/270 (137 to 144), hidden, by the table and by enumerating every word of their four finished structures. |
| P1 | Under R no two-holder start without a hidden excess gains one | **Holds (in what was tested)** | 0 gains in 146,044 histories of the 6,312 stalled two-holder starts: both conventions, every allowed round-1 choice for 5,078 starts and 62 drawn ones for 1,044, every law assignment in 55,254 + 29,752 histories and 4,096 drawn in the rest. The largest hidden score at any grown stage is 1.692 in floating point (no hidden table within 10^-6 of 2). On the other 5,835 two-holder starts no knot is ever short, so R is ordinary growth (gate G on 500 of them) and ticket B's result stands: none gains. The drawn part is a sample, not a census. |
| P2 | Under R some stalled three-holder start gains a hidden excess through a payment | **Holds** | 7 starts, 9 histories (4 under O, 5 under N), 321 tables with a gain, all at stage 1 and all with every law assignment enumerated; 261 of the 321 are through a payment, and each of the 7 starts has one. |
| P3 | In arm 2 no T made only of loose distinctions gives a hidden excess | **Holds** | 0 gains among 2,051,018 sets with no shared distinction (1,210,623 of them hidden). |
| P4 | In arm 2 some gain has a T that is not of the known shape | **Holds** | 808 of the 1,746 gains are not of the known shape: 162 with two distinctions (one loose observer distinction and one shared) and 646 with three (one loose observer distinction and two shared). |

## Arm 1: growth under rule R

**Gains by class.**

| | Two-holder | Three-holder |
| --- | ---: | ---: |
| Histories with a gain / starts | 0 / 0 | 9 / 7 |
| Tables with a gain (all at stage 1) | 0 | 321 |
| ... from fully enumerated histories / drawn | 0 / 0 | 321 / 0 |
| ... through a payment / not | 0 / 0 | 261 / 60 |
| Starts with a gain through a payment | 0 | 7 |

**The share beside ticket B.** Of the 21,575 stalled three-holder starts, 16,793 make at least one round under R (by one
convention or the other) and 7 of those gain: 7 of 16,793 (0.042%, each start counted once). Under ordinary growth
ticket B found 34 histories that gain among its 7,957 three-holder starts that made a round (0.43%). Rule R turns 16,793
stalled starts into growing ones and 7 of them into a hidden excess.

**The nine histories with a gain.** Every start has a stage-0 table that is hidden with score exactly 2; every gain is
at stage 1.

| Start (target, knots of the target, its score) | Convention | Knots / distinctions per stage | Round 1: births, of which two or more parents, paying | Tables / gains / through a payment | Best |
| --- | --- | --- | --- | --- | --- |
| 9606 (207, 11, 127/63) | O | 10, 13 / 16, 21 | 3, 2, 1 | 27 / 6 / 6 | 127/63 |
| 13207 (224, 12, 109/54) | O | 10, 14 / 17, 25 | 4, 2, 1 | 81 / 27 / 27 | 109/54 |
| 36293 (278, 14, 211/105) | O | 12, 17 / 20, 27 | 5, 3, 1 | 243 / 27 / 0 | 1135/567 |
| 36293 | N | 12, 17 / 20, 27 | 5, 3, 1 | 243 / 99 / 72 | 127/63 |
| 36365 (278) | N | 12, 17 / 19, 29 | 5, 3, 2 | 243 / 36 / 36 | 6175/3087 |
| 43742 (285, 15, 181/90) | O | 11, 14 / 18, 21 | 3, 3, 1 | 27 / 3 / 0 | 973/486 |
| 43742 | N | 11, 14 / 18, 21 | 3, 3, 1 | 27 / 11 / 8 | 109/54 |
| 43890 (285) | N | 11, 14 / 17, 23 | 3, 3, 2 | 27 / 4 / 4 | 5293/2646 |
| 43892 (285) | N | 12, 18 / 20, 32 | 6, 3, 2 | 729 / 108 / 108 | 5293/2646 |

Among the 214 gain tables written in full (at most 50 per stage and history; all 321 counted), in every gain through a
payment the paying not-all-equal newborn takes one of Bob's observer distinctions: Bob's loose y1 with a shared s1 or y3,
Bob's loose y2 with a shared Bh5, or a shared y3 with a shared Bh5. The 60 gains not through a payment (starts 36293 and
43742, both conventions) are carried by not-all-equal newborns on loose distinctions, (Bh2, Bh5) and (Bh1, y2): ticket
B's kind of birth, made possible because the round no longer stalls. Scores of the 321 gain tables: 127/63, 109/54,
1135/567, 6175/3087, 973/486, 5293/2646, 11162/5535.

**The smallest gain, in full.** Start 9606 of target 207: the target without nae(y2,Bh2,Bh3); 10 knots, 16 distinctions.

- Alice: nae(x2,Ah1,Ah2,Ah3), nae(x1,x3,s2), even(x3,Ah3,Ah4), nae(x1,s1,Ah2), odd(Ah2,Ah3,Ah4).
  Bob: odd(y1,y3,Bh4), odd(Bh2,Bh3,Bh4), even(Bh1,Bh2,Bh3,Bh4), odd(y3,s2,Bh1), even(y2,s1,Bh1).
- Holders: Ah2, Ah3, Bh1 and Bh4 have three; x1, x3, s1, s2, Ah4, y3, Bh2 and Bh3 have two; x2, Ah1, y1 and y2 are
  loose. Stage 0 is hidden with score exactly 2. Ordinary growth stalls at round 1 because even(y2,s1,Bh1) holds one
  loose distinction (y2) and is a parent of two births.
- **Round 1 under convention O.** even(y2,s1,Bh1) gives its loose y2 to its first birth and pays its second with s1, its
  oldest allowed shared distinction (the other is Bh1). Three births, 5 fresh distinctions:
  1. parents nae(x2,Ah1,Ah2,Ah3) and even(y2,s1,Bh1), taking Ah1 and y2, fresh f16 and f17;
  2. parents odd(y1,y3,Bh4) and even(y2,s1,Bh1), taking Bob's loose y1 and **s1, paid** (two holders before, three
     after), fresh f18. This is the one paying birth;
  3. parent nae(x2,Ah1,Ah2,Ah3), taking x2, fresh f19 and f20.
- Stage 1: 13 knots, 21 distinctions. **Laws:** birth 2 not-all-equal, nae(y1,s1,f18); birth 1 even or odd parity,
  (Ah1,y2,f16,f17); birth 3 any law, (x2,f19,f20): 6 of the 27 assignments. **Score 127/63, hidden** (both complete
  records unchanged by the far setting).
- **Through a payment:** with birth 2 even parity and the other laws kept, the score is exactly 2, hidden.
- **By enumeration of every word of the four finished structures** (stage 1 with the setting births nae(x1, x2 or x3, za)
  and nae(y1, y2 or y3, zb), 23 distinctions; 2,688, 3,024, 2,688 and 3,024 allowed words): hidden (largest change of
  a complete record with the far setting 0) and exactly 127/63, the same four record tables as from the old-word
  table. The same holds for all six assignments of the gain.
- Under convention N the same start pays with Bh1 instead of s1; then no table of its stage 1 exceeds 2 (12 of the 27
  are hidden, the best at exactly 2).

**Where the two-holder starts stay.** No hidden table at any grown stage of any of the 146,044 two-holder histories comes
within 10^-6 of 2; the largest hidden score is 1.692 (floating point). No stalled two-holder start has a hidden table at
stage 0 with a score within 10^-6 of 2 (unlike the 27 starts that gain in arm 2, none of which stalls).

## Arm 2: one added knot

Each T is one not-all-equal knot on T and one fresh distinction (new table 2M − M_T).

**By the shared distinctions in T and its size** (sets / hidden / gains):

| Shared in T | 2 distinctions | 3 distinctions | 4 distinctions | All |
| --- | --- | --- | --- | --- |
| none | 305,229 / 231,340 / 0 | 677,120 / 432,034 / 0 | 1,068,669 / 547,249 / 0 | 2,051,018 / 1,210,623 / **0** |
| one | 681,183 / 530,373 / **162** | 2,344,787 / 1,513,146 / 0 | 5,158,174 / 2,717,576 / 0 | 8,184,144 / 4,761,095 / 162 |
| two or more | 373,766 / 291,550 / 0 | 3,575,801 / 2,356,041 / **646** | 17,215,553 / 9,206,445 / **938** | 21,165,120 / 11,854,036 / 1,584 |

Every gain's T has exactly one loose distinction; the rest are shared (one of two, two of three, three of four).

**By observers:** inside one observer's three distinctions 96,584 / 88,285 / 54; observer distinctions of one side only
and others 17,363,016 / 10,405,538 / 1,672; both sides 8,131,533 / 3,549,985 / 20; none 5,809,149 / 3,781,946 / 0. The
loose distinction of every gain is Bob's y2 or y3 (873 each). The 54 gains inside one observer are T = {y1, y2} and
{y1, y3} in each of the 27 starts, the form of Bob's setting birth, with y1 shared.

**By origin:** sets that a round-1 birth takes under ordinary growth 7,046 / 4,531 / 0; under rule R for some allowed
choice 110,295 / 86,253 / 0 (103,249 of them under R only); under ordinary growth with some placement of the parents'
loose distinctions (supplementary) 18,960 / 12,395 / 0; neither 31,138,394 / 17,631,988 / 1,746; not decided 151,593 / 107,513 / 0. **No gain's T is taken
by any round-1 birth, under ordinary growth or under rule R** (for all 1,746 the R origin is decided: none). In the 27
starts that gain, the two loose distinctions y2 and y3 belong to one knot, the only live one, so round 1 makes two
births with one parent each under either rule.

**The starts that gain.** 27, each of 7 knots and 12 or 13 distinctions, none stalled: the target without one knot, for
targets 102 to 114 (without even(y3,Bh1,Bh2) or odd(y2,Bh1,Bh2)), 135 to 144 (the ten known starts, without
nae(y3,Bh1,Bh2,Bh3)) and 176, 177, 180, 181 (10 knots, without three). Each stage 0 is hidden with score exactly 2.

**The least T that works** has two distinctions: one loose observer distinction of Bob and one shared distinction (162
gains, 6 in each of the 27 starts; for start 2990, {s1, y2}, {s1, y3}, {s2, y2}, {s2, y3}, {y1, y2}, {y1, y3}).

**The largest score** is 55/27 (24 gains, in starts 2990, 3031, 4307 and 4348 of targets 102, 103, 135 and 136; for
example T = {s1, y2} in start 2990). Scores of the 1,746 gains: 253/126 (496), 541/270 (472), 508/253 (192), 271/135
(160), 109/54 (152), 127/63 (108), 111/55 (94), 510/253 (36), 55/27 (24), 112/55 (12).

**The known shape** (one loose observer distinction and three shared): 938 of the 1,746 gains, in all 27 starts (918
with observer distinctions of one side only, 20 with both sides). The ten known starts with T = {y3, Bh1, Bh2, Bh3}
give 271/135 (2) and 541/270 (8), as stated before the freeze; their best T scores more (55/27 for targets 135 and 136,
109/54 for the others).

**The smallest gain, in full** (fewest knots, then distinctions, then |T|, then the smallest score; 102 gains tie on
the first three). Start 3072 of target 104: the target without odd(y2,Bh1,Bh2); 7 knots, 12 distinctions.

- Alice: nae(x1,x3,s1), even(x1,Ah1,Ah2), nae(x2,x3,s2), odd(x2,Ah1,Ah2). Bob: even(y1,Bh1,Bh2), odd(s1,Bh1,Bh2),
  even(y1,y2,y3,s2).
- Loose: y2 and y3; every other distinction has two holders. Stage 0: 16 allowed observer words, each counted 4 times;
  hidden, score exactly 2.
- Added knot: nae(s1, y2, fT), on the shared s1 (held by nae(x1,x3,s1) and odd(s1,Bh1,Bh2)) and Bob's loose y2, with
  one fresh distinction fT. Each allowed word of the start now counts twice when s1 and y2 differ and once when they
  are equal; each of the 16 entries of the old-word table becomes 8 or 4.
- **Score 109/54, hidden.** By enumeration of every word of the four finished structures (15 distinctions; 256, 288,
  192 and 216 allowed words): hidden (largest change of a complete record with the far setting 0) and exactly 109/54,
  the same four record tables as from the old-word table.
- No round-1 birth makes this knot: round 1 makes two one-parent births, on y2 and on y3.

## Checks and verification

- Gate parts (`gates_*.json`): g1two and g1three as in row G above; `known` 10 of 10; `pairs` 200 of 200 equal by
  enumeration (and equal evaluation); `stages` 100 of 100 (direct contraction equal to enumeration, the reduced table
  proportional to it, the same evaluation), drawn among 40,027 grown stages of at most 24 distinctions.
- The evaluator agrees with the recorded scorer `evaluate(M)` of `docs/prompts/missed_leads_checks/finished_weighting_chsh.py`
  (hiding and score) on all 214 written gain tables of arm 1, their 214 tables with paying births made even, the 1,204
  arm-2 gain tables written with their table, 1,000 drawn arm-2 tables and 1,000 drawn arm-1 tables.
- Every gain was recomputed by direct contraction with its actual law assignment (asserted equal to the reduced
  table's evaluation).
- **Full enumeration of gains** (every word of the four finished structures, ticket B's `brute_joint_all` and
  `evaluate_joint`). Arm 2: all 1,746 gains (15 or 16 distinctions with the added knot and the setting births), every
  one hidden with the same exact score as its table, and for the 1,204 written with their table the same four record
  tables. Arm 1: 164 of the 214 gain tables written in full (stages of 21 to 29 distinctions: 20, 4, 27, 77 and 36
  tables at 21, 23, 25, 27 and 29), every one hidden with the same exact score and the same four record tables.

## Readings taken, limits, not done

- Readings fixed before the runs are in deviations.md section A: classes and stalls read from ticket B's record; the
  engine with the not-all-equal structure rule and no knot cap; names, oldest and newest as ticket B numbers them;
  choices enumerated or drawn as products of per-knot options, later rounds by convention O; one generator per history
  for drawn laws; tables counted as distinct prefixes; the exact reduction of A9; the seeds of the checks; the ordinary
  origin with the recorded wrapper's placement and no size stop; the known shape read as one loose observer
  distinction and three shared; the definitions of "smallest".
- The three-holder starts were grown under the two conventions only (the note asks for every choice on two-holder
  starts only); a null there would have been weaker.
- P1 rests in part on samples: 1,044 two-holder starts had 62 of their allowed choices drawn, and 61,038 two-holder
  histories had 4,096 law assignments drawn. Of the 6,312 stalled two-holder starts, 3,731 are covered in full (every
  allowed round-1 choice and every law assignment of every history) and 2,581 in part.
- Not enumerated word by word: the 50 gain tables of one stage of 32 distinctions (start 43892 under convention N,
  5293/2646; each would take about 4 x 10^9 words of the stage), and the 107 gain tables counted but not written in
  full (49 of start 36293 under N, 58 of start 43892 under N). They rest on the contraction, recomputed for every gain
  by direct contraction with its actual assignment, which agreed with enumeration wherever both were run.
- Five enumeration runs of ten tables each reached the ten-minute limit and were redone in smaller runs (deviations
  B5); no run of either arm did.
- The supplied scaffolds of this study: the starts (parts of the census's structures) and their observers; the setting
  births; the equal weighting of finished words; rule R, its conventions and the drawn choices; the law of each
  newborn; arm 2's knot, which is supplied and not grown.

## Commands

Run from the repository root, in this order (every run with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`
and under `timeout 600 prlimit --as=12884901888`; at most six at once; chunks as listed in
`arm1_jobs.txt`, `arm2_jobs.txt`, `verify_jobs.txt` of the artifacts folder, each run's output line in
`arm1_runs.log`, `arm2_runs.log`, `verify_runs.log`):

```bash
E=experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach
W="timeout 600 prlimit --as=12884901888 .venv/bin/python -B"
for p in g1two g1three known pairs; do $W $E/gates.py --part $p; done          # row G, first parts
# arm 1: --cls two --lo L --hi L+1000 for L = 0..6000 step 1000; --cls three --lo L --hi L+3000 for L = 0..21000 step 3000
$W $E/arm1.py --cls two --lo 0 --hi 1000        # ... (15 runs, arm1_jobs.txt)
# arm 2: --lo L --hi L+2000 for L = 0..12000 step 2000
$W $E/arm2.py --lo 0 --hi 2000                  # ... (7 runs, arm2_jobs.txt)
$W $E/gates.py --part stages --lo 0 --hi 50; $W $E/gates.py --part stages --lo 50 --hi 100
$W $E/gates.py --part scorer                    # first run kept as gates_scorer_first.*; rerun from verify_jobs.txt
$W $E/gates.py --part verify --lo 0 --hi 1770 --maxd 23
$W $E/gates.py --part verify --lo 1770 --hi 1771 --maxd 25
# then every line of verify_jobs.txt: $W $E/gates.py <line>
# five runs of verify_jobs.txt (ten 27-distinction tables each) reached the limit (deviations B5); redone:
#   every line of verify_jobs_redo.txt: $W $E/gates.py <line>
$W $E/gates.py --part verify --lo 1910 --hi 1960 --maxd 29   # counts the 50 tables of 32 distinctions, not enumerated
$W $E/report_c.py                               # summary.json
```
