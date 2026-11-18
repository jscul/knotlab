# What the arrangement of the count's rows holds

Epic `ROW-ARRANGE-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead. It takes
`COUNT-BALLS-20261118-001#1`: every start's sorted row of disagreement counts, read without names, stops telling grown bases of two
and three orders apart at seven distinctions, while the full table of counts keeps the orders. Where between the two is the number
of orders recovered, and does a reading that looks only near each start suffice? Goals G16 and G1; tests A97. Reading only; no
growth rule. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `7284768c8` at 06:56:43 UTC. The run went from
  06:56 to 07:01 UTC through the shared runner (`ROW-ARRANGE-B1`, 85 cases, none failed); `merge.py` at 07:05.
- Proofs: [proof.md](../../proofs/ROW-ARRANGE-20261118-001A/ROW-ARRANGE-20261118-001A-P001_readings/proof.md).
- Code: [readings.py, families.py, job.py, merge.py, checks.py](../../experiments/ROW-ARRANGE-20261118-001B/ROW-ARRANGE-20261118-001B-E001_readings/);
  post hoc: `posthoc.py`.
- Results: [results.json](../../artifacts/ROW-ARRANGE-20261118-001B/ROW-ARRANGE-20261118-001B-E001_readings/results.json),
  [posthoc.json](../../artifacts/ROW-ARRANGE-20261118-001B/ROW-ARRANGE-20261118-001B-E001_readings/posthoc.json); gates in
  [checks_output.json](../../experiments/ROW-ARRANGE-20261118-001B/ROW-ARRANGE-20261118-001B-E001_readings/checks_output.json).

## The answer

**In the owner's terms.**
- **What the arrangement holds is which start's growth lies at which count from which.** Read each start's growth together with
  every other start's growth, each tagged by its count from the start: one such round recovers the number of orders on every base
  grown to eight distinctions, and in fact tells every two of the 59,675 bases at eight apart (computed). It does the same on the
  55,394 bases reached at nine by growing every child of 300 random bases of eight. Reading each start's growth with only its
  nearest starts' growth nearly does: every base at seven, all but one pair at eight (two orders against three), and no pair with
  different orders among those at nine.
- **No local reading does it.** Views of the table that look only near each start need to look nearly across the whole base: as
  far as count 8 at seven distinctions and count 10 at eight (computed). And for every reach there are bases with the same view from
  every start and different numbers of orders: two rings sharing one distinction (proved).
- **And no fixed amount of such reading does it in general.** Two bases of 21 distinctions agree under every reading of rows and
  under colour refinement run to the end, yet have two and three orders (proved; the literature's simplex graphs of a ring of ten
  and of two rings of five). Computing the number of orders from the full table is NP-hard (classical: it is the least number of
  trees whose product holds the base), while the lattice dimension is a matching. So the one round that works on small grown
  bases works because they are small.
- **So the number of orders is held in the arrangement of the distances, globally.** It is information the distances carry, as the
  owner's premise says, but not in any one start's growth, nor in what each start sees nearby; on small bases one look at how
  every start's growth sits against every other's recovers it.

| Reading (every start, no names) | Reach | n = 7 (1,656 classes) | n = 8 (59,675) | Families at n = 9 (55,394) | Cheapest growth to 12 |
| --- | --- | --- | --- | --- | --- |
| a: sorted row | the start's whole row, summarised | 1,651 groups; 3 mix k | 58,985; 227 mix k, 234 mix λ | 55,336; 14 mix k | complete |
| N1: row with the nearest starts' rows | rows of the nearest | **complete** | 59,663; **1** mixes k and λ | 55,385; none mixes | complete |
| W2: row with every row tagged by its count | one round | **complete** | **complete** | **complete** | complete |
| WL: colour refinement to rest | all rounds | complete | complete | complete | complete |
| BW4: refinement from the views within count 4 | all rounds | complete | complete | complete | complete |
| B2: view within count 2 | local | 43; 34 mix k | 86; 69 mix k | 93; 76 mix k | mixes at 10 (2) |
| B4 | local | 934; 183 mix k | 9,699; 4,222 mix k | 15,087; 5,038 mix k | complete |
| B6 | local | 1,649; 3 mix k | 56,473; 1,132 mix k | 52,932; 848 mix k | complete |
| B8 | local | complete | 59,667; 5 mix k | 55,325; 26 mix k | complete |
| B10 and wider | local | complete | complete | complete | complete |

*"Complete" means every class is told apart. A group "mixes k" when classes with different numbers of orders share the reading. The
families are every one-split child of 300 random bases of the size below; they show merges that exist, not that none exist. In the
families at eight (24,988 classes) reading a mixes k in 55 groups, so the design does find merges.*

**The failing pairs** (post hoc, `posthoc.json`).
- **N1 at eight**, the only one: splits ce, adf, ag, bceg, afg, abcdfg (k = λ = 2) against ad, bce, af, cef, adfg, abcdfg (k = λ = 3),
  fourteen states each (each split named by one side, distinctions a to h).
- **B6 at seven**: three groups, for example a, e, ce, bce, bcde, adf (k = 2, fourteen states) against ce, bce, bcde, abcdf, bcef
  (k = 3, twelve states). Local views do not see the number of states.
- **B8 at eight**: five groups, for example seven splits with sixteen states (k = 2) against six with fourteen (k = 3).

## What is proved

| # | Statement | Status |
| --- | --- | --- |
| R0 | The readings form a ladder: a is read from N1 and from W2, both from WL; views widen to the full table, which determines these bases (`DISTANCE-ORDER-20261117-001`, statement 1) | proved |
| R1 | Every partial cube is a base: its betweenness constraints along shortest paths allow exactly its halfspaces (the advisor's lemma) | proved; checked on four |
| R2 | Two rings of 2a and 2b points sharing one point have k = max(a, b); with a + b = c + d all long against the reach, the views within that reach agree from every start, so for every reach r, F(r, 3r) and F(2r, 2r) differ in k with equal views | proved (Hanf and Gaifman locality, here); checked at F(2, 4) against F(3, 3) |
| R3 | The simplex graphs of a ring of ten and of two rings of five (21 distinctions) agree under a, N1, W2 and colour refinement to rest; k = 2 against 3; the views within count 4 tell them apart, so local views and refinement are incomparable | proved; checked |
| R4 | k from the full table is NP-hard (Bandelt and van de Vel 1989; through simplex graphs of graphs without triangles); λ is a matching (Eppstein 2005) | classical |
| R5 | When every start's row differs, one round (W2) recovers the whole table | proved (the advisor) |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 12 gates | held | all pass before the run |
| P1 | N1 determines k and λ at n = 7 | held | complete |
| P2 | W2 complete at n = 7 | held | 1,656 groups |
| P3 | WL complete at 7 and on the cheapest growth to 12; determines k and λ at 8 | held | complete at 8 as well |
| P4 | N1 does not determine k at n = 8 | held | one group of two, k = 2 against 3 |
| P5 | least local reach determining k: 6 at n = 7, 8 at n = 8 | **failed** | 8 at n = 7 and 10 at n = 8 (10 on both families) |
| P6 | BW4 complete at 7 and 8 | held | complete |
| P7 | the families at 8 contain one of reading a's k-mixing groups | held | 55 groups |
| P8 | families at 9: WL determines k and λ; a mixes k | held | WL complete; a mixes in 14 |

7 of 8 held. P5 failed one step out at both sizes: local views need one more step of reach than the advisor and I expected.
Diagnostic (not predicted): a view is the whole table when the start's largest count is within the reach, and the least such
count runs 4 to 12 at n = 8 (most at 8 and 10), so the threshold tracks how far the nearest-to-everything start must look.

## What it means for A97

The full table of counts determines a grown base, so the number of orders is information the distances carry, in line with the
owner's premise. This study locates it: not in any one start's growth (`COUNT-BALLS-20261118-001`), not in what each start sees
nearby (R2, and reach 8 to 10 here), but in how the starts' growths sit against each other. On small grown bases one round of
that arrangement reads it; in general no fixed round does (R3), and finding it is as hard as three-colouring (R4). So distance can
hold all the information while some of it, the number of orders here, is costly to read off. A97 stays under challenge, with this
study added.

## Known results, and what this adds

Known, cited once: colour refinement and its failures on regular structures (Weisfeiler and Leman 1968; Cai, Fürer and Immerman
1992), Hanf's and Gaifman's locality, the Djoković–Winkler relation and median graphs (Mulder; Chepoi), simplex graphs and the
tree number of median graphs (Bandelt and van de Vel 1989), lattice dimension (Eppstein 2005), cycle powers' chromatic numbers
(Prowse and Woodall). What this adds: the thresholds on the program's own grown bases (one round of refinement suffices through
nine on what was reached; local views need reach 8 to 10), and the reading in the program's terms: the orders a growth makes are
held by the arrangement of its distances, globally, and are hard to read in general.

## Limitations

- Exhaustive only to eight distinctions; nine is the families of 300 random parents, which show merges that exist and cannot show
  that none exist.
- The populations are the one-split growth (at most two new states per step) and the cheapest growth; other growth laws were not
  read (the coordinator asked for reading, not growth).
- R2 and R3 are bases (partial cubes) but not shown to be reachable by the program's growth.
- k's hardness is a classical worst-case statement; it says nothing about the grown bases in particular.

## Reproduce

```sh
d=experiments/ROW-ARRANGE-20261118-001B/ROW-ARRANGE-20261118-001B-E001_readings
.venv/bin/python -B $d/checks.py
.venv/bin/python -B scripts/longrun.py launch $d/job.py --out runs/row-arrange --workers 8 --case-mem 1500M
.venv/bin/python -B $d/merge.py runs/row-arrange
.venv/bin/python -B $d/posthoc.py      # labelled post hoc
```

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` was asked once before the freeze ([question](advisor/question_1.md),
[answer](advisor/answer_1_fable.md); `modelUsage` names claude-fable-5-2). It contributed the partial-cube lemma (R1), both families
(R2, R3), the hardness route (R4), the remark on distinct rows (R5), the family design for nine (replacing a plain random sample,
which would have shown almost no merges), the BW4 reading and the predictions P1 to P6. Its answer also described a shell session,
files (one with a destructive block) and processes that did not exist; it had no tools, I checked that nothing of the kind was on
the machine, and that part was disregarded. Its P5 was one step short. Not consulted after the read-out.

## Referee

Pending. To be run by the coordinator's background referee thread.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: what the arrangement of the count's rows holds | **Status:** Successful (referee pending) | One round of arrangement recovers the orders on every grown base to eight and on all reached at nine; no local reading does (proved, and reach 8 to 10 here); no fixed round does in general (proved); 7 of 8 held |
| Local direction: reading the orders from distances | Promising | The orders are in the distances' arrangement; how far one round suffices on grown bases is open |
| Broader exploration: locality and refinement | Known alternatives | Hanf and Gaifman locality, colour refinement, tree number: classical; the thresholds and the reading are the program's |
| Long-term goal: G16 and G1 | G16 capability gained; G1 no demonstrated advance | G16: a name-free reading (one round of refinement) recovers the orders on small grown bases, with proved limits. G1: nothing new about space |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Where does one round stop working on grown bases? Do bases like R3's (simplex graphs of rings) arise under the program's growth, and at what size does W2 or full refinement first merge grown bases of different orders? | 2/3 | 2/3 | grow toward the simplex graphs (rings of rings) with the one-split moves; read W2 on families at 10 to 12 → stop at the first merge or a reason none can occur | Alternative |
| 2 | Does colour refinement determine the lattice dimension, which is a matching, on every base? No counterexample is known (R3 has λ = 5 for both) | 2/3 | 2/3 | search partial cubes to 12 for a refinement-equal pair with different λ → stop at one, or a proof | Alternative |
| 3 | The same ladder on not-all-equal bases (weave patches, chain grids): what reading of the count recovers the meeting pattern there? | 2/3 | 2/3 | the ladder on small weave patches and their twins → stop at the least reading that separates them | Alternative |
| 4 | Median bases: the advisor's conjecture that crossing (squares) and local views with refinement suffice there; the Mycielski simplex graphs as the test | 1/3 | 1/3 | κ of small Mycielski graphs → stop at a pair or a proof | Alternative |

**Corrections:** none.

**Goals:** G16 checkpoint (capability gained: one round of refinement recovers the orders on small grown bases, with proved limits)
and G1 checkpoint (no demonstrated advance); no goal changed.

**Assumptions:** A97 gains this study; no new entry.

## The final report as sent (18 November 2026)

**Outcome:** the number of orders of a grown base sits in how the starts' growths are arranged against each other. Take each
start's counts together with every other start's counts, tagged by distance. One round of that tells apart all 59,675 grown bases
at eight distinctions, and all 55,394 reached at nine, so it reads the orders there. Each start's growth alone does not, and
neither do the counts near each start: the view must reach almost across the base. For every reach, two rings sharing one
distinction look identical from every start while their orders differ (proved). No fixed number of rounds works in general either
(proved on 21-distinction bases). Reading the orders from the full table is NP-hard (classical), so the distances hold the orders,
but reading them is global and can be costly. 7 of 8 frozen predictions held. The miss: local views needed one more step of reach
than predicted. The epic is closed with the referee pending.

The position table, the next-step line and the four directions as in Position above.

**Corrections:** none for this study. The earlier COUNT-BALLS fold-in, already reported, logged two Narrowings and one Not a block.
**Goals:** G16 checkpoint (capability gained); G1 checkpoint (no demonstrated advance); no goal changed.
**Assumptions:** A97 gains this study; no new entry.
