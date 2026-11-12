# Referee report RANDOM-FATES-R1: stage 1's census of random meeting patterns

**Verdict: Confirmed with fixes.** The census is sound. Every one of the 2,985 recorded growths regenerates exactly from its seed with
the referee's own code. Every number the note quotes recomputes from the records with independent aggregation. Re-reading the census's
bases with the referee's own reader agrees on every tie summary checked (2,146 bases), and changes no prediction's verdict.

The fixes are about wording. The answer and the owner report say living patterns read as rulers "under every weighting tried" and that
"nothing is tied". The census's own data contradict both: living newest-four patterns are full of shortcuts and ties, and most living
X(0.2) bases have a tie. Conclusion 2 omits n = 50. "Independent of n" is consistent with the data, but only weakly pinned at k = 10
and 20. Conclusion 4's "no final jump" does not hold for X(0.5).

Referee: the background referee thread, 2026-11-12. My code (`ref_fates.py`, `ref_regen.py`, `ref_summary.py`, `ref_reread.py`,
`ref_fresh.py`) imports neither `fates.py` nor `census.py`. The processes follow the pre-registration's table, drawing their random
numbers in the frozen order so the census's own bases can be regenerated. I checked that order against the table by reading the code.
Growth uses Glucose 4, where the census used CaDiCaL, and the tie classes and least bonds come from my own reader. Validation: V2. The
advisor model was not consulted for this job.

## 1. Integrity of the record

- **The frozen code is unchanged.** `census.py` and `fates.py` are touched by one commit only, the freeze (507421630).
- **The roster.** 2,985 of the 2,990 pre-registered runs are recorded, with no duplicate and no extra. The 5 missing are exactly U300
  runs 0 to 4, the pending minimal-contradiction runs (RANDOM-FATES-A2).
- **The resume.** It used the same code and seeds, and neither double-counted nor skipped. Every recorded growth regenerates
  from its seed with my code: death knot (U), or dead, knots, size and size at the end (the others). There are 0 differences in
  2,985 runs. So the 969 runs from the registered unit and the 2,016 from `resume_driver.py` are what the frozen seeds give.
- **The guarded summary.** Its diff against `census.py` is two lines, not one. One sets the path (`HERE`) so the copy runs from
  `research/`; the other is the `.get()` guard. Both are harmless.
- **U300's readings rest on 25 runs, not 30.** Runs 0 to 4 are also read runs, so every U300 reading (P1 and P2 at n = 300) comes
  from runs 5 to 29. The missing five are fixed by index, not by outcome, so this is no selection, but the count should be stated
  where U300 readings are quoted.

## 2. The numbers, recomputed from the records

| Claim | Record | Referee |
| --- | --- | --- |
| U median density, n = 50, 100, 200, 300 | 2.09 to 2.16 | 2.16, 2.12, 2.09, 2.10 |
| Still a base at 2,000 moves: X(0.1 to 0.5) | 100, 100, 45, 0, 0% | the same |
| O global (0 to 0.3) / O local (0.05 to 0.3) | all at q ≤ 0.1, 89%, 6% / all, all, 71%, 0 | the same |
| Newest-five and newest-six ending, q ≥ 0.5 / q = 0.3 | 99 to 100% / 8 to 15% | 99 to 100% / 8 and 15% |
| P1: U100 f0.75 d = 3 | 86%, 13% shortcuts | 86.3%, 13.3% shortcuts; every other registered cell ≥ 96% |
| P2: largest-class share at k = 10 / 5 / 1 | 25 to 34% / 52 to 75% / 87 to 89% | 25 to 34% / 52 to 75% / **87 to 90%** (n = 50 is 0.900) |
| P3: minimal contradiction over the death knot, n = 50, 100, 200 | 55, 73, 86% | 0.550, 0.731, 0.862 |
| Shortcuts at d = 3, k = 50 / k = 10 | 11 to 27% / 97 to 99% | 11 to 27% / 97 to 99% |
| P5c: X and O last bases with a class ≥ 10% | 99% | 99.3% (148 of 149) |
| X(0.3), X(0.35) at k = 50 / k = 1 | 0.35, 0.43 / 0.38, 0.46 | 0.353, 0.425 / 0.379, 0.457 |
| P5a: newest-w cores ≤ 20 knots within span 20 | 98% | 98.3%; knots 10 to 12 (IQR), index span 4 to 9 (IQR) |
| P5b: Spearman, age against the largest class | 0.61 (ties by order) | 0.63 with tied ranks averaged |
| P6: X(0.1), X(0.2), O global (0, 0.05, 0.1) ruler shares; B3/B1 | 92 to 100%, Og(0.1) d = 3 at 90%; 43 to 150 | the same; Og(0.1) d = 3 at 0.896 |
| P7: newest-four shortcut share d = 2, 3 / tie reach ≤ 8 / B6 | 73%, 94% / all / 35, 36 | 73.3%, 93.5% / all (max 7) / 35, 36 |
| C1 / C2 | all / 720 of 720 | 390 of 390 / 720 of 720 |

Two small wording slips. The last-base share is 87 to **90**%, because n = 50 is 0.90. "Within 4 to 10 consecutive distinctions"
should read 5 to 10: a core on the five distinctions of one window, with all ten triples knotted, spans 5 distinctions, index span 4.

## 3. The census's bases, re-read with the referee's reader

- **Living bases (P6, P7, C2), all 240.** The tie summary (classes, largest class, tied pairs, distinctions used) agrees exactly on all
  240. I recomputed the least bond of all 5,760 recorded pairs with a wider search: sizes 2 and 3 over every distinction; size 4 over
  every w with steps(u, w) + steps(w, v) ≤ d + 2, and size 5 with ≤ d + 1, both with no cap (the census capped at the 40 nearest).
  The differences are few and go both ways:
  - some census "rulers" at d = 3 have a size-4 bond just outside the capped lens: X(0.2) 4 pairs, Og(0.1) 3, newest-four 8;
  - some census "none" are rulers the cap cut off: X(0.1) 6, X(0.2) 7, Og 9, newest-four 9.

  No verdict changes:

  | Item | Census | Referee |
  | --- | --- | --- |
  | P6, X(0.2) d = 3 | 0.921 | 0.929 |
  | P6, Og(0.1) d = 3 | 0.896 | 0.896, still failing |
  | P6, X(0.1) d = 3 | 0.971 | 0.996 |
  | P7a shortcut share, q = 0.5 / 0.7 | 73.3% / 93.5% | 75.2% / 94.2% |
  | C2 | 720 of 720 | 720 of 720 |
- **Bases before the end (X, O, newest-five and newest-six, k = 1 to 50), all 1,819.** The tie summaries agree exactly.
- **Uniform bases (read runs 5 to 14 at every size; the full set was too slow for the shared machine, so the run was stopped after 87
  bases).** The tie summaries agree exactly on all 87 bases read, among them 27 at n = 300 at points up to the last base. I re-read the
  least bonds at P1's points f0.5 and f0.75 for 1,632 recorded pairs: 480 at each of n = 50, 100 and 200, and 192 at n = 300. The
  search covered sizes 2 to 4 over every distinction, and size 5 over every distinction at n ≤ 100, otherwise over the uncapped lens.
  1,627 pairs agree exactly. The other 5 are pairs where the census found nothing:
  - four U200 pairs at d = 3 have a size-5 bond the capped lens missed, so they are rulers;
  - one U50 pair at d = 2 has a least bond of 5, beyond the census's search to d + 2.

  So every census ruler or shortcut at these points is confirmed, exhaustively at n ≤ 100. The lens cap made P1 slightly
  conservative, and no verdict changes.
- **Minimal contradictions (the referee's own deletion, Glucose 4, newest knot first).** Every set found is minimal and contains the
  killing knot. Minimal contradictions are not unique, and only 10 to 13 of the 200 sizes coincide per n, but the distributions match:
  median share of the death knot 0.543 against the census's 0.550 at n = 50, and 0.733 against 0.731 at n = 100 (P3 held there). The
  newest-five and newest-six endings give 98.3% within 20 knots and span 20. X and O cores have the same medians: X(0.3) 90 knots over
  an index span of 218, X(0.35) 71 over 160.5, O global (0.3) 22.5 over 202.5, O local (0.3) 22.5 over 195.5. The n = 200 cores were
  not rechecked: my deletion took over half an hour per growth, and the run was stopped. P3 at n = 200 therefore rests on the census
  alone.
- **Fresh seeds (a sampling check, not a re-read).** I drew 100 new growths per setting from the seed tag "referee".
  - Every outcome share agrees with the census's within sampling error.
  - Three census shares fall outside the fresh 95% intervals: O global (0.3) 6% against 16% fresh, newest-five (0.3) 85% against
    75%, X(0.35) 0% against 2%. The largest two-sample gap, O global (0.3), has p ≈ 0.02, which is not significant across 23
    comparisons.
  - Every P4 verdict holds on the fresh sample.
  - Single-sample shares near the boundary carry about ±5 to 10 points: "6%" at O global (0.3) is one draw of something nearer 10%.

## 4. The coordinator's questions

**Are the partly failed predictions reported with the same weight as those that held?**
In the note's conclusions and its table against the pre-registration, yes. P1's, P5b's and P6's failures appear in the conclusions'
text and their "Kind" column. The answer and the owner report drop them, and add two claims the data contradict:
- **"Under every weighting tried, the patterns that live read as rulers away from any end … and nothing is tied"** (the Answer).
  Living newest-four patterns are not rulers: 73 to 94% of pairs 2 and 3 steps apart have shortcuts, and every one of the 60 bases
  has ties. Living X(0.2) bases have a tie in 21 of 30, with a largest class up to 77 distinctions. Og(0.1) has ties in 10 of 30, and
  X(0.1) in 3 of 30.
- **"Living patterns are rulers … That is a theorem wherever knots form no cycle"** (the owner report). This puts the theorem next to a
  computed claim about patterns full of cycles, where the theorem does not apply. The ruler on living X and O patterns is computed,
  and it fails at Og(0.1), d = 3.
- **Conclusion 2, "Uniform patterns read as rulers until near their end … At half and three quarters … no base has a tie".** This
  holds at n = 100 to 300 (P1's registered sizes, with its one failure). At n = 50, three quarters of the end is only about 27 knots
  before it, inside the end's stretch: 7 of 30 bases have ties, and at d = 3 only 11% of pairs have least bond 5 (88% shortcuts). It
  is consistent with the fixed-length end, but the sentence needs "at n ≥ 100".

**Is "independent of n" in (3) supported by the spread, or only asserted?** It is supported as "no trend", and weakly pinned.
- **No trend.** The medians at each k show no trend in n: the Spearman correlation of share against n, run by run, is −0.23 to 0.00.
- **Per-run onset.** The first read point at which a run's largest class passes half its distinctions has the same spread at every n,
  mostly 10 or 5 knots before the end, at n = 50 and at n = 300. That is the strongest evidence for a fixed length in knots: if the
  stretch were a fixed share of the knots, the onset would move about sixfold from n = 50 to 300.
- **Weakly pinned.** The run-to-run spread is large: the interquartile range at k = 5 runs from about 0.3 to 0.9. A bootstrap
  interval for the ratio of the n = 300 to n = 100 median includes 1 at every k, but it is wide: 0.33 to 3.1 at k = 10, 0.15 to 3.7 at
  k = 20. It is tight only at k = 1 (0.94 to 1.03).
- **So** "the same length at every size" is the simplest reading and fits, but 25 to 30 runs per size cannot exclude a length that
  grows slowly, say as √n. Say "consistent with" and give the spread.

**Is anything exploratory worded as registered?**
- **Labelled correctly.** The whole-life jumps (10 lives per setting) and the missing-knot count are marked exploratory in the
  conclusions table and the Reading.
- **Conclusion 4's heading.** "Growth that keeps adding distinctions ends without a final jump" rests on the frozen k = 1 to 50 readings
  and holds for X(0.3), X(0.35) and O at 0.2 and 0.3. It fails for X(0.5): the median share rises from 0.30 at k = 50 to 0.75 at
  k = 1. Those growths die young (median 60 knots), so 50 knots before the end is near their start. The heading should name the
  settings.
- **Stage 2's missing-knot count** is outside this job. It appears unlabelled in the owner report ("The count follows the missing
  knots").

## 5. Fixes for the thread

1. **The Answer and the owner report.** Narrow "under every weighting tried … read as rulers … and nothing is tied" to X and O
   growth at small q and uniform patterns away from the end. Say that living X(0.2) bases mostly carry ties and that living
   newest-four patterns carry shortcuts and ties. Do not attach "a theorem wherever knots form no cycle" to the computed ruler.
   **Narrowing** (Overreading).
2. **Conclusion 2.** Add "at n = 100 to 300". At n = 50, three quarters of the end is inside the end's stretch. **Not a block**.
3. **Conclusion 3.** Give "independent of n" as "consistent with a fixed length: no trend, the same per-run onset, wide intervals at
   k = 10 and 20". The last-base share is 87 to 90%. U300 readings come from 25 runs. **Not a block**.
4. **Conclusion 4.** Name the settings (X at 0.3 and 0.35, O at 0.2 and 0.3) and note X(0.5). **Not a block**.
5. **Records.** The guarded summary differs in two lines; "4 to 10 consecutive distinctions" should be 5 to 10. **Not a block**.

## Files

| Item | Script | Output |
| --- | --- | --- |
| Handover from the coordinator | | `brief.md` |
| Processes, growth and reader | `ref_fates.py` | |
| Regeneration of every growth | `ref_regen.py` | `result_regen.json` |
| Independent aggregation | `ref_summary.py` | `result_summary.json` |
| Re-reading of the census's bases | `ref_reread.py` | `result_g.jsonl`, `result_gk.jsonl`, `result_u.jsonl`, `result_cores.jsonl` |
| Fresh seeds | `ref_fresh.py` | `result_fresh.json` |

The runs were capped `systemd-run --user` units named `ref-rf-1-<part>`, each with MemoryMax 16G and no swap. Two were stopped
unfinished, as section 3 says: the full uniform re-read and the n = 200 cores.
