# Independent growth replay

All 52 archived detailed runs agreed birth for birth across 734 kept rounds and 135,008 births. The comparison included the names and parents of each birth, its inputs and their current holders, any additional take, its demand, and its usable and barred fresh counts. It matched 74 filtered series with 170 ticks and 164 unfiltered series with 412 ticks in the detailed listings. Each listed series gave parts off at two or more ticks. [Counts](growth_listed.json)

The 25 additional comparisons agreed on per-round totals, stop conditions and the return readings. They checked 1,800 detailed series entries with 4,787 ticks and 260 one-member summaries, counting a series once for each recorded reading. The detailed exports in the two largest examples stopped at 200 entries per reading and the one-member summaries at 50. The aggregate checks used every reconstructed series. The two-knot start under MET with NEWEST and parity gave two failing joins, 40 and 41, each made in round 5 with twelve parents and fourteen places. Direct rank calculations reproduced all 1,604 round-by-round verdicts in aggregate, including 28 failures. [Counts](growth_summary.json)

The three sampled reading cases passed C-iii, and the no-taking case failed C-iii as recorded. All four failed C. The two-knot start under STEPS-1 with short members making offshoots had six own knots per period and still made two per round after the first bar took effect. The same start under STEPS-2 for offshoots of joins, with short members waiting, had 7, 15, 32 and 74 own knots across the four periods. Its clock had the same ticks in the shared rounds with the second part barred. One additional tick occurred in the longer run. The parity case also reproduced the course differences when barring the parts given off and when barring all qualifying parts. All nine masked comparisons reproduced the corresponding barred course within the required comparison. [Counts](growth_bars.json)

## Scope of the filter

The archive's filtered series reject a part when one of its members meets any member of the live roster, including members of other parts. Section 2.2 also admits a reading restricted to meetings inside the part. At the two-knot start, each start knot is a one-member part, and the two meet through their shared distinction. The restricted reading admits both as possible series starts. It changes filtered entries in eight of the 52 detailed runs and three of the 25 comparison runs. Under STEPS-2 for offshoots of offshoots with short members making offshoots and fresh counts by parents, it admits two one-member series on that start that give parts off twice under each knot law. Stating the whole-roster reading in §2.2 makes these rows reproducible. The main tests use the unfiltered series. [Definitions](../definitions.md#2-the-made-clock) · [Detailed counts](growth_listed.json) · [Summary counts](growth_summary.json)

## Source omitted at the prefix boundary

The independently grown case was DW(5,3), the start of five members whose common knots meet one another, under STEPS-3 for offshoots of joins, COPY-LAW with short members waiting, BY-COUNT, parity, and fresh counts by parents. The run kept 14 rounds and stopped at 4,460 knots. It made 30 clocks with a stretch of four equal periods. This supplement sits outside the archived test total. [Counts by pair](growth_omitted.json)

| Clock selection | Eligible clock and tick choices | Eligible pairs | Positive fixed count across four periods |
| --- | ---: | ---: | ---: |
| Recorded grouping by set of period lengths | 4 | 26 | 0 |
| Grouping by the whole tuple of periods | 8 | 58 | 0 |
| Every clock | 45 | 330 | 0 |

## Rerun

The growth code reads starts, laws and definitions independently. The comparison code reads archived results to select the stated examples and compare results. The four phases use one process each, in sequence, with an address-space limit of 3 GiB. The complete phases each finished in under nine seconds. Peak resident memory across them was about 114 MiB. The exact-input pilots included detailed listing entries 3, 13 and 45 in file order, four census comparisons including the nine-knot ring under STEPS-8, the two-knot parity comparison with offshoots of joins, and the omitted source with the recorded clock grouping. The pilots took 0.74, 4.38, 2.80 and 0.35 seconds respectively. The measured slowest case in each group put the projected complete phases below 30, 11, 9 and 7 seconds respectively. [Selection plan](growth_plan.md)

```sh
r=research/TIME-AS-FOLD-20261125-001/referee-R1
d=$(mktemp -d "$r/replay.XXXXXX")
for phase in listed summary bars omitted
do
  .venv/bin/python -B "$r/growth_replay.py" "$phase" --pilot --output "$d/pilot_${phase}.json"
  .venv/bin/python -B "$r/growth_replay.py" "$phase" --output "$d/growth_${phase}.json"
done
```

The remaining baselines, the remaining bar tests, the changes of numbering, and the full knot census were not independently regrown here. The prefix-boundary supplement ran the four-period count check only.
