# Which recorded signals an ordinary process can send: draft results

Ticket `REVIEW-LEADS-20261123-001E`, experiment `REVIEW-LEADS-20261123-001E-E001`. Written by the implementing sub-agent for the thread, which owns the analysis and the verdict. Frozen note: [preregistration.md](preregistration.md). Code: `experiments/REVIEW-LEADS-20261123-001E/REVIEW-LEADS-20261123-001E-E001_signal_routes/`. Outputs and logs: `artifacts/REVIEW-LEADS-20261123-001E/REVIEW-LEADS-20261123-001E-E001_signal_routes/` (`logs/summary_tables.md` holds every table below in full). Readings and additions: `deviations.md` in the experiment family. Every recorded run stayed under 2m30 of wall clock and 1.2 GB. **Draft, referee pending.**

Words. A "round" is one complete parent step. An "allocation" is the choice, for every knot, of which of its named loose distinctions is paid to which of its children. "Uniform present words" gives every allowed word of the grown structure equal weight. The "old-word weighting" gives every old allowed word equal weight, divided among its extensions. TV is total variation.

## Gate (row G): passed

Ten histories times two laws (seven-knot source, five-founder clock, smallest two-sided stall with both additions, smallest parity closing in two versions, three archived explosive starts, two concealed-shortage types).

| check | clean histories | injected fault |
|---|---|---|
| R1, one loose distinction added to an existing knot after round 3 (after round 1 for the one history with a single round) | 0 violations in 20 of 20 rows | flagged in 20 of 20 rows |
| R2, the all-parent join veto of the written-bit study, 64 valued versions per row | 0 of 1,280 versions differ in births, all 1,280 lawful | flagged in 20 of 20 rows: 64 of 64 versions differ in 19 rows, 55 of 64 in the closing start 00 under parity |

## R1, holdings: P1 holds

42 history-and-law rows (21 histories, both laws), 403 rounds in all, up to 9,993 knots (seven-knot source) and 2,087,258 distinctions (archived explosive start 13, a six-knot start from the archive of explosive growth). **Zero** knots whose set of distinctions differs from its set at birth. The fault was flagged in **28 of 28** rows that have a funded round (27 at the third round, one after its only round). The other 14 rows are stalled starts with no round to edit.

| history | rounds | knots reached | note |
|---|---:|---:|---|
| seven-knot source | 12 | 9,993 | both laws |
| five-founder clock | 31 (six returns of the marked turn) | 160 | both laws |
| archived explosive 00 | 22 / 64 | 1,084 / 1,987 | parity ends (closes) at 22 rounds; not-all-equal stops before a round that would pass 2,000 knots |
| archived explosive 04 | 7 | 1,300 | next round would pass 2,000 knots (rounds are atomic) |
| archived explosive 13 | 6 | 1,368 | same |
| smallest stall, four settings | 0, 0, 0, 12 | 5 / 65 | only setting 11 (both additions) is funded |
| smallest parity closing, four settings | 1 (parity, setting 00; closes) or 12 | 4 to 148 | |
| concealed-shortage preparation | 12 (four types, funded) or 0 (four types, unedited) | 168 / 62 | |

Audits beyond the definition: the engine agrees with the compact reference operator in 407 rounds and disagrees in none (12 rounds of over 400 births were not cross-checked); in every funded round **every loose distinction is paid** (0 unpaid in 403 rounds); an old distinction gains a second holder only from a new knot (0 exceptions); a stalled start stays the same stall (see the routes table).

## R2, values: P1 holds

42 rows, 64 lawful valued versions each, **2,688 versions, 0 differ** in births, parents or numbers of fresh distinctions (4,800 births in the reference runs, 307,200 compared), and all 2,688 valued histories stay lawful. Horizons were fixed from run time (seven-knot source 6 rounds; clock 16 rounds, three returns; archived explosive starts to 1,000 knots, that is 18, 6 and 5 rounds; all others 8 rounds or 300 knots). Parity versions are uniform on the allowed words; not-all-equal versions are uniform by rejection except the 8 concealed-preparation rows, which use Moser-Tardos resampling (lawful, not uniform).

## R3, allocations: P2 holds; P3 holds

Every allocation class was enumerated at funded step 1 of the three structures and at funded step 2 of the stall; 200 random allocations at step 2 of the seven-knot source and the clock (births and word counts only); the clock's step 2 also exhaustively as a supplementary row. In every row, in **all** classes: the round's births and the later births (parents and fresh counts, to the horizon) did not change (**0 changes**), the grown structure is the image of the canonical one under an explicit relabelling of loose distinctions (0 failures), and the number of allowed words of the grown structure is the same (cross-checked by an independent variable-elimination count: every class of the 32-class rows; the first 64, 12 random and every 97th class of the seven-knot row). Old-word weighting: **0 changes** in every class. Parity, uniform present words: **0 changes**. Not-all-equal, uniform present words: **every class except the canonical one changes the distribution**.

| structure, step | old distinctions | allocation classes | allowed words of the grown structure (same in every class) | parity: TV of old distinctions, both weightings | not-all-equal: classes with TV > 0 (uniform present) / largest TV | not-all-equal: old-word weighting |
|---|---:|---:|---:|---|---|---|
| seven-knot source, step 1 | 25 | 5,184 (all distinct orders) | 34,359,738,368 parity; 337,661,927,874,000 nae | 0 | 5,183 of 5,184 / **1,897,979,953,241/18,758,995,993,000 = 0.10118** | 0 |
| five-founder clock, step 1 | 18 | 32 | 262,144; 94,507,872 | 0 | 31 of 32 / **7,660,205/47,253,936 = 0.16211** | 0 |
| smallest stall (setting 11), step 1 | 15 | 32 | 32,768; 8,840,192 | 0 | 31 of 32 / **711,319/4,420,096 = 0.16093** | 0 |
| smallest stall, step 2 | 25 | 32 | 1,048,576; 4,651,429,918 | 0 | 31 of 32 / **381,303,468/2,325,714,959 = 0.16395** | 0 |
| five-founder clock, step 2 (supplementary, 28 old distinctions) | 28 | 32 | 8,388,608; 49,689,192,406 | 0 | 31 of 32 / 582,570,740/3,549,228,029 = 0.16414 | 0 |
| seven-knot source, step 2 (200 random allocations) | 50 | 6,718,464 | 36,893,488,147,419,103,232; 861,275,465,570,170,326,151,636,820 | not computed | not computed | not computed |
| clock, step 2 (200 random allocations) | 28 | 32 | as above | not computed | not computed | not computed |

The largest TV between any two classes equals the largest against the canonical one in the 32-class rows (all 496 pairs) and never exceeds it in the seven-knot row (300 random pairs). The total variation on all old distinctions equals that on the loose ones (full joint enumerated for all 32 classes of the clock's step 1 and the stall's two steps, and for 12 random classes of the seven-knot row; not for the supplementary clock step 2, which is above the cap).

**Per knot** (only that knot's allocation varies; every other knot canonical). Under parity every knot's loose distinctions are interchangeable under both weightings (largest TV 0). Under not-all-equal they are interchangeable under the old-word weighting and **not** interchangeable under uniform present words, at every knot that holds two or more loose distinctions:

| structure, step | knots (loose each) | largest TV when only that knot varies, uniform present, not-all-equal |
|---|---|---|
| seven-knot source, 1 | 0, 2, 3, 4 (3 each); 5, 6 (2 each) | 0.0511, 0.0532, 0.0532, 0.0505; 0.0380, 0.0380 |
| five-founder clock, 1 | 0 to 4 (2 each) | 0.0709, 0.0758, 0.0814, 0.0814, 0.0729 |
| smallest stall, 1 and 2 | 0 to 4; 5 to 9 (2 each) | 0.0798 at each of 0 to 4; 0.0815 at each of 5 to 9 |

(Knot 1 of the seven-knot source holds no loose distinction.) No knot in these structures has a spare that becomes a unary birth at the steps enumerated, so the number of classes equals the number of orders.

**Smallest example in full.** The smallest lawful start (3 knots, then fewest distinctions; the gate of the generators study passes under both laws) on which an allocation changes the old distribution has 3 knots and 6 distinctions: A = (0,3,4), C = (1,2,5), W = (0,1,2). A holds loose 3 and 4, C holds loose 5, W is spent and is the common witness of A and C. The round has two births: the pair (A,C) with 1 fresh distinction, and a unary birth at A with 2 fresh. Two allocations: (S1) the pair takes 3 and 5 and the unary takes 4; (S2) the pair takes 4 and 5 and the unary takes 3. Under parity the 8 old words have weight 2 each under both allocations (TV 0). Under not-all-equal there are 30 old words and 138 words of the grown structure in both allocations. A word is written as the values of distinctions 0 to 5; the weight is the number of words of the grown structure that extend it (3 times 1 or 2 for the pair, times 3 for the unary):

```
old word  w(S1) w(S2)      old word  w(S1) w(S2)      old word  w(S1) w(S2)
110000    3     3     101010    3     6     110101    3     6
101000    3     3     011010    3     6     001101    3     6
010100    6     3     010110    6     6     101101    3     6
110100    6     3     001110    6     6     100011    6     3
001100    6     3     011110    6     6     010011    6     3
101100    6     3     100001    6     6     110011    6     3
011100    6     3     110001    6     6     001011    6     3
010010    3     6     101001    6     6     101011    6     3
110010    3     6     100101    3     6     010111    3     3
001010    3     6     010101    3     6     001111    3     3
```

Twenty words differ by 3, so TV = 60/(2·138) = **5/23 = 0.2174** under uniform present words; under the old-word weighting every word has weight 1 and TV = 0. The same start under parity: TV 0. In the same smallest closing family the TV is 11/59 (closing start 10) and 23/122 (closing start 11) under not-all-equal and 0 under parity.

**Supplementary (not in the frozen definition): where the difference sits.** Under not-all-equal and uniform present words, for a change of the allocation of one knot u: the distribution of the loose distinctions of **any single other knot** is unchanged (TV 0 for every pair, all structures and steps); u's own loose marginal changes by at most 0.00005 (seven-knot source) and by 0 in the clock and the stall; the **joint** law of the loose distinctions of u and of another knot v changes by up to 0.0814 (clock), 0.0798 and 0.0815 (stall, steps 1 and 2) and 0.0380 (seven-knot source) when v is two shared distinctions away from u (no common child with u), by 0.0017 to 0.0025 (clock, stall) and 0.0165 (seven-knot source) at one, and by 0.0004 (seven-knot source) to 0.0017 (step 2 of the stall and clock) at three. The effect is a change of a correlation, with every one-knot marginal at the other knots fixed. (Separation here counts the shared distinctions crossed between the two knots in the ordinary graph.)

## R4, groups: P4 holds

**Reading.** The functions that form the proposed groups (`holders_of`, `loose_of`, `neighbours_of`, `proposed_groups`, `groups_from_adjacency`, `lookahead_demand`) and the reference operator's (`from_stars`, `neighbors`, `_maximal_groups`, `_proposals`, `proposals`) take only the supports (or the live counts and witness sets built from them). None has a parameter or reads a name for a value, a word, a law, a reference or a veto. In `plan_round` the law argument is used only after the groups are formed (to decide the implied sole birth and the fresh counts), apart from an assertion that it is a known law; the injected veto is the only value-keyed hook.

**Replays.** 12 histories times two laws, 168 stages, 5,126 groups: (1) renaming all distinctions and renumbering all knots at random: **0 of 168** stages not covariant; (2) eight histories per row grown with a **random allocation at every round**, and one valued version per row: **0 of 1,152** allocation stages and **0 of 168** valued stages with different groups; (3) the reference operator's proposals equal ours on 61 of 61 connected stages and its birth roster is identical under the two laws on 61 of 61. Control: the veto engine gives different groups under different values in 24 of 24 rows, so the replay can fail. Supplementary: adding a loose distinction at a knot that is already live left the groups unchanged in 644 of 644 edits (and changed funding in the 2 edits made at a stalled start's deficient knot).

## R5, order: replayed

Rebuilt from the recorded witness (eight-knot clock with an attached original, nine common births), recomputing the eligible births from the holdings after every birth: at birth 10 both the clock's own pair (4,6) and the pair of 4 with the attached original (4,8) are eligible, and both take the one remaining loose distinction of knot 4. Control (4,6): the marked tick is realized at birth 21 (ancestry isomorphic to the reference, 12 further births). Treatment (4,8): knot 4 is spent, the pair (4,6) is never again eligible, no later birth can give it a loose distinction, and the tick is impossible (future bound empty). After the control tick the outside pair (4,8) is no longer eligible. Both laws, both namings of the source: **4 of 4**. Old knots' holdings unchanged in every arm. Diagnostic: on the same prefix the complete-round rule stalls (12 knots short) while the serial rule has 24 eligible births, so the complete round has no order to choose; that prefix was made by serial births and need not be reachable by complete rounds.

## Table of routes

| route | sender's act (in the stalling studies) | ordinary growth | an allocation | a fresh value | a serial order | evidence |
|---|---|---|---|---|---|---|
| fixed address | add one loose distinction at a chosen one of two existing knots of the prepared start | **No** | No | No | No | R1: 0 of 42 rows change a knot's holdings; the fault that does is flagged 28 of 28. R3: births, funding, later births and word counts identical in all classes. R2: 0 of 2,688. R5: old holdings unchanged |
| address keyed to an old value | the same addition, the knot named by an old value the sender reads | **No** (the act is an edit, and births do not depend on values) | No for the edit; an allocation chosen from an old value is possible but moves only the law of old values (not-all-equal, uniform present words) | No | No for the edit; an order keyed to a value is an external rule | R2: 0 of 2,688 versions change a birth, while the injected value-keyed veto changes births in 20 of 20 gate rows. R3 |
| withholding the spare | the sender leaves out the optional distinction so that a neighbour's knot lacks it and funding changes | **No** (every loose distinction of a live knot is paid in a funded round) | No (an allocation pays all) | No | **Yes, in a sense**: an outside birth taken first spends the last loose distinction a clock birth needs and the tick is lost | R1: 0 unpaid loose distinctions in 403 rounds. R3: every allocation pays all. R5: 4 of 4 replays. A schedule of births is not part of complete-round growth |
| repairing a visible shortage on a free message | add a loose distinction at the deficient knot so a stalled round funds | **No** (a stall repeats with the same shortages) | not applicable (a stall has no births) | No | **Not a repair**: the serial rule has no stall (24 eligible births where the complete round stalls) | Stall replays: 5 stalled starts (three smallest-stall settings, two concealed types), both laws, three re-plans each, identical shortages; all 64 valued versions of each stall; R1: no edit |
| revealing the hidden labels | give the reader the preparation's hidden type (a change of the reader's record, not of the structure) | **No act of the sender**; the two detector sides of the concealed preparation never meet (no common live descendant, no finite separation, 20 rounds, 4 types, both laws) and the four types have the same birth statistics in every round | No | No | No | `routes_evidence.json`; R1 to R3 |
| biasing the weight of a hidden type | change the preparation weights over starts | **No** | Not between starts: the number of allowed words is the same in every class. Within one start, under not-all-equal and uniform present words, weight moves among old values (TV 0.10 to 0.22 in the replays); never under parity or the old-word weighting | No | No | R3 (ii), (iii) |
| the smallest parity closing | add a spare at a spent holder; the other side reads whether its mark's child has no fresh distinction (the sole implied birth) | the closing is an ordinary event fixed by the holdings (start 00: one birth, no fresh, closed); the edit that changes it is route 1 | No: births fixed; allocations move only old values (TV 11/59, 23/122 under not-all-equal, 0 under parity) | No (64 of 64 versions identical) | not tested | `routes_evidence.json`, R1 to R4 |

What stays open inside one ordinary history: **the allocation** (not-all-equal with uniform present words changes correlations of old values with every one-knot marginal at other knots unchanged; nothing under parity or under the old-word weighting), **the fresh values** (free, but births and funding ignore them), and, only outside complete-round growth, **a serial order**.

## Exact commands

All run from the repository root as `timeout 600 prlimit --as=12884901888 .venv/bin/python -u -B <script> <arguments>` (`experiments/REVIEW-LEADS-20261123-001E/REVIEW-LEADS-20261123-001E-E001_signal_routes/run_all.sh` lists them; it ran once for the gate and everything after it, then `routes_evidence.py` ran separately). With `EXP=experiments/REVIEW-LEADS-20261123-001E/REVIEW-LEADS-20261123-001E-E001_signal_routes`:

```
$EXP/gate.py
$EXP/r1_holdings.py --group source|clock|stall|closing|concealed
$EXP/r1_holdings.py --history explosive_00|explosive_04|explosive_13 --law parity|nae
$EXP/r2_values.py --group source|clock|stall|closing|concealed
$EXP/r2_values.py --group explosive --law parity|nae
$EXP/r3_allocations.py --structure seven|clock --law parity|nae --sample-step2 200
$EXP/r3_allocations.py --structure stall --law parity|nae
$EXP/r3_allocations.py --structure clock --law parity|nae --beyond-cap
$EXP/minimal_start.py
$EXP/r4_groups.py
$EXP/r5_order.py
$EXP/routes_evidence.py
.venv/bin/python -B $EXP/summarize.py > artifacts/REVIEW-LEADS-20261123-001E/REVIEW-LEADS-20261123-001E-E001_signal_routes/logs/summary_tables.md
```

Hashes of the code at the start of the recorded run: `logs/code_sha256.txt` (`summarize.py` was repaired afterwards for two table-printing faults; `routes_evidence.py` was added). Development runs that preceded it are kept in `artifacts/.../dev_runs/`.

## Not done, and limits

- Funded step 2 of the seven-knot source (50 old distinctions) and of the clock (28) were not enumerated in the recorded checks (200 random allocations only, for births and word counts); the clock's step 2 was enumerated as a labelled supplementary row.
- Funded step 2 of the smallest stall was enumerated, step 3 onward never. The structures are three small starts, one smallest start and the histories above; nothing here is a statement about all lawful starts.
- Under not-all-equal the old-word weighting makes the old distribution uniform on every allocation (every old word extends); this is checked per class here, not proved in general.
- The 8 not-all-equal concealed-preparation rows of R2 used lawful but not uniform valued versions.
- Scaffolds in this study (to record at close): the list of routes, the replayed histories, the injected faults, the reference word of the veto, the horizons and caps, the canonical allocation at step 1 when starting step 2, the identification of exchangeable unary births, and the choice of the three structures for R3.
