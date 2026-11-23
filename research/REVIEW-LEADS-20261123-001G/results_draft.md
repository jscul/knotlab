# Does repeated release need a failing pattern? Draft results

Ticket `REVIEW-LEADS-20261123-001G` (follow-up to ticket A of epic `REVIEW-LEADS-20261123-001`), 2026-11-23.
Computed by a Claude Opus sub-agent from the frozen note; analysis and verdict are the thread's. Referee pending.
[Pre-registration](preregistration.md) ·
[deviations and readings](../../experiments/REVIEW-LEADS-20261123-001G/REVIEW-LEADS-20261123-001G-E001_release_and_test/deviations.md) ·
[summary.json](../../artifacts/REVIEW-LEADS-20261123-001G/REVIEW-LEADS-20261123-001G-E001_release_and_test/summary.json)

**In both populations, under both laws, the test fails within the horizon for every start that has any birth at all, and
passes for every start that stalls at once.** All 21 proved sources fail, and so do all 182 starts of growing kind that are
not proved sources. The fixed reading is the first one: the test tracks growth and no argument is attempted. The test is
ticket A's: the pattern of which knot holds which distinction must be, in the literature's words, a planar graph.

## Gates (row G): passed

| Clause | Recorded | Found |
| --- | --- | --- |
| Seven-knot source, first failing step and knots | step 1, 15 knots, both laws | step 1, 15 knots, both laws (also with the earlier study's labelling of its distinctions) |
| Nine-knot drawn source | step 1, 24 knots, both laws | step 1, 24 knots, both laws; it is Q2 draw 60 with two extra meetings |
| Q1 verdict counts (`edits.json`, frozen reader + later parent-map proof) | 16 proved / 33 proved not / 4 undecided | 16 / 33 / 4 under each law at horizons 16 and 32 |
| Q2 verdict counts (`draws.jsonl`, demand-supplied, sizes 9–12) | 5 of 192 proved | 5 of 192 under each law (4 of 96 with two extra meetings, 1 of 96 with three); the rest are 14 proved not and 173 unresolved |

Both populations were also regenerated with the earlier study's own generators and seeds and matched the stored starts:
53 of 53 edits and 192 of 192 draws. The five proved draws match `certificates.json`. Ticket A's engine reproduces the
earlier study's recorded births per step wherever both exist: 109 of 109 and 115 of 115 ages in Q1, 670 of 670 and 695 of
695 in Q2 (parity and not-all-equal).

## The cross-table: recorded verdict against the test, by growth kind

Each cell is fail / pass within the horizon (12 parent steps or 5,000 knots). The tables are identical under parity and
not-all-equal.

**Q1, the 53 single edits of the seven-knot source**

| Recorded verdict | Stalled | Bounded | Growing | Total |
| --- | ---: | ---: | ---: | ---: |
| Proved source | – | – | 16 / 0 | 16 |
| Proved not | 0 / 19 | 3 / 0 | 11 / 0 | 33 |
| Undecided | – | – | 4 / 0 | 4 |

**Q2, the 192 demand-supplied draws, sizes nine to twelve**

| Recorded verdict | Stalled | Bounded | Growing | Total |
| --- | ---: | ---: | ---: | ---: |
| Proved source | – | – | 5 / 0 | 5 |
| Proved not | – | 9 / 0 | 5 / 0 | 14 |
| Unresolved | – | 11 / 0 | 162 / 0 | 173 |

All 19 stalled starts are Q1 edits that stall at once: 16 loose deletions, the loose addition to the knot with no loose
distinction, and the additions 2–5 and 3–6. They pass, as settled by construction. Every one of the other 34 + 192 = 226
starts fails under each law. The three bounded Q1 starts are the additions 2–3, 4–5 and 4–6. Under parity they close; under
not-all-equal they continue with few births.

## Predictions

| # | Verdict | Evidence (identical under both laws) |
| --- | --- | --- |
| G | Passed | Table above |
| P1 | Held | 21 of 21 proved sources fail within the horizon (16 in Q1, 5 in Q2), every one at parent step 1. No candidate counterexample. |
| P2 | Held | Q1, growing kind. The 16 proved sources first fail at a median of 15 knots (ten at 15, six at 16). The 11 proved not first fail at a median of 17 knots (15, 15, 15, 15, 16, 17, 31, 31, 31, 53, 53). Without the three illegal shared deletions the median is 31 (8 starts). |
| P3 | Failed | 182 of 182 growing starts that are not proved sources fail within the horizon (Q1 15 of 15, Q2 167 of 167), against a bar of at most half. |

**Reading fixed in advance.** Among growing starts in Q1 and Q2 that are not proved sources, 182 of 182 (100%) fail, at or
above the 90% bar. **The test tracks growth, and no argument is attempted.** The 50% reading would also have needed
every proved source to fail, which they all do; only the first condition is missed. A sensitivity line reads three Q2
histories stopped within four steps as growing (ticket A's code calls them bounded). All three fail, giving 185 of 185.

## Knots at the first failing stage

| Group | Starts | Median | Range | First failing step |
| --- | ---: | ---: | --- | --- |
| Proved sources, Q1 | 16 | 15 | 15–16 | 1 (all) |
| Proved sources, Q2 | 5 | 33 | 24–35 | 1 (all) |
| Proved sources, both | 21 | 16 | 15–35 | 1 (all) |
| Growing, not proved sources, Q1 | 15 | 15 | 15–53 | 1 (10), 2 (3), 3 (2) |
| Growing, not proved sources, Q2 | 167 | 29 | 19–53 | 1 (163), 2 (4) |
| Growing, not proved sources, both | 182 | 28 | 15–53 | |

The five proved draws fail at 24 (draw 60, nine knots), 30 (draw 68, ten knots), 33 and 35 (draw 25 with two and with three
extra meetings, twelve knots) and 34 (draw 34, twelve knots). Within Q2 their median, 33, is above the 29 of the other
growing draws. P2 was stated for Q1 only, so this is reported and not judged. Q2 proved not of growing kind: 5 draws,
median 26 (23–38). Q2 unresolved of growing kind: 162 draws, median 29 (19–53).

## The birth that first makes the stage fail

From the last passing stage, that step's births were added one at a time in the engine's order. No stage failed at step 0.
Every breaking step had at most 27 births.

| Group (each law) | Breaking births | Number of parents | Fresh distinctions of that birth |
| --- | ---: | --- | --- |
| Proved sources, Q1 | 16 | 2 (all) | 3 (14), 4 (2) |
| Proved sources, Q2 | 5 | 2 (all) | 3, 5, 5, 6, 7 |
| Growing, not proved sources, Q1 | 15 | 2 (all) | 3 (10), 4 (5) |
| Growing, not proved sources, Q2 | 167 | 2 (129), 3 (21), 4 (15), 5 (2) | 1 (1), 2 (15), 3 (41), 4 (55), 5 (37), 6 (10), 7 (5), 8 (3) |
| Bounded, not proved sources, Q1 | 3 | 2 (all) | 2 (3) |
| Bounded, not proved sources, Q2 | 20 | 2 (16), 4 (4) | 2 (3), 3 (9), 4 (4), 5 (2), 6 (1), 8 (1) |

No breaking birth has fewer than two parents (0 of 226 under each law), as settled by construction. Every proved source
breaks at a birth with two parents.

## Q1: is the first failure inherited from the unedited source?

Knots are matched with the unedited source, grown under the same law, by parentage (deviations, item 5). The returned
sub-pattern is the routine's forbidden sub-pattern of the first failing stage. "Inherited knots alone fail" means some
forbidden sub-pattern uses only inherited knots. The unedited source itself first fails at step 1.

| Recorded verdict | First failures | Returned sub-pattern uses only inherited knots | Inherited knots alone fail | Returned sub-pattern holds the edit's distinction | Same first failing step as the unedited source |
| --- | ---: | ---: | ---: | ---: | ---: |
| Proved source | 16 | 14 | 14 | 7 | 16 |
| Proved not | 14 | 7 | 10 | 0 | 9 |
| Undecided | 4 | 0 | 2 | 0 | 4 |
| **All** | **34** | **21** | **26** | **7** | **29** |

The same numbers hold under both laws. **21 of the 34 Q1 first failures use only knots that the unedited source also has
at that step.** In 7 of those 21 the sub-pattern holds the edit's own added distinction: the loose additions at knots 5
and 6, and the shared additions 2–4, 2–6, 3–4, 3–5 and 5–6. Two proved sources do not inherit their failure: the
additions 1–2 and 1–3, the two proved by the later parent-map proof. Each first fails at 15 knots on a sub-pattern of the
K3,3 kind (K3,3 and K5 are the literature's two forbidden sub-patterns) with 7 of its 8 knots inherited, and their inherited knots alone pass. The other 14 proved sources
fail on a sub-pattern of the K5 kind with 10 knots, all inherited. The undecided additions 0–5, 0–6, 1–5 and 1–6 fail on
K5-kind sub-patterns with 9 of 10 knots inherited.

## Proved sources that pass at every stage

None, under either law.

## The two laws

Q1 was grown under both laws separately. Fifty of the 53 histories are identical. The three that differ (additions 2–3,
4–5 and 4–6) are exactly those whose parity history has a step with one birth: parity closes there, after 7, 5 and 5
steps, while not-all-equal continues to the horizon. Q2: 181 not-all-equal histories equal the parity history under the
engine's clause, and their first three steps were grown directly and agree (181 of 181). The 11 parity histories that
closed were regrown under not-all-equal. No start's test result differs between the laws. This confirms ticket A: the
laws' histories differ only after a step with exactly one birth, and here every start that fails has failed before any
such step.

## Limits

A 240 s limit per growth, fixed before any start was read, stopped 32 histories under each law: Q1-29 and Q1-30 after 10
steps, and 30 Q2 draws after 4 to 10 steps. All 32 had failed at step 1 before the stop, so their test results stand.
Outcomes in Q2 under parity: 87 stopped by the cap, 64 at the horizon, 30 on time, 11 closed. Two of the five proved draws
share one tree, so the independent sources number five by tree, not the six the note counts. The 16 edits count as one
family.

## What this is about

The populations, horizon, cap, time limit, the parentage matching of knots and the bars are supplied; each is a scaffold.
On these two populations the test does not separate proved sources from other starts: it separates starts that have any
birth from starts that stall at once. That matches ticket A's finding that stalled starts never fail. Ticket A's fresh
draws (four to eight knots, the original loose supply) passed at every stage in 247 of 280 funded starts per law. The
starts here differ from those in supply, size and meetings, and this study does not separate those factors. Knot counts at
first failure here are 15 to 53.

## Commands

From `/home/jscul/p-vs-np-contact-first`, with
`E=experiments/REVIEW-LEADS-20261123-001G/REVIEW-LEADS-20261123-001G-E001_release_and_test`,
`O=artifacts/REVIEW-LEADS-20261123-001G/REVIEW-LEADS-20261123-001G-E001_release_and_test` and
`P="timeout 600 prlimit --as=12884901888 .venv/bin/python -B"`:

```bash
$P $E/populations.py | tee $O/populations.log          # recover Q1, Q2 and verdicts; gate counts
$P $E/gates.py | tee $O/gates.log                      # gate G, first clause (exits non-zero on failure)
# Q1, both laws grown separately; four chunks in parallel, then the remainder of chunk 2 after its start deadline
for c in 0 1 2 3; do ($P $E/read_test.py --pop Q1 --start $((c*14)) --stop $((c*14+14)) --tag c$c > $O/read_Q1_c$c.log 2>&1) & done; wait
($P $E/read_test.py --pop Q1 --start 30 --stop 31 --tag c2b > $O/read_Q1_c2b.log 2>&1) &
($P $E/read_test.py --pop Q1 --start 31 --stop 36 --tag c2c > $O/read_Q1_c2c.log 2>&1) &
($P $E/read_test.py --pop Q1 --start 36 --stop 42 --tag c2d > $O/read_Q1_c2d.log 2>&1) & wait
# Q2, one start per run; batches 0-31 (-P 16), then 32-71, 72-111, 112-151, 152-191 (-P 20)
seq 0 31 | xargs -P 16 -I{} sh -c "/usr/bin/time -f 'maxrss_kb=%M wall=%e' $P $E/read_test.py --pop Q2 --start {} --stop \$(({}+1)) --tag q{} > $O/read_Q2_q{}.log 2>&1"
seq 32 71 | xargs -P 20 -I{} sh -c "/usr/bin/time -f 'maxrss_kb=%M wall=%e' $P $E/read_test.py --pop Q2 --start {} --stop \$(({}+1)) --tag q{} > $O/read_Q2_q{}.log 2>&1"
# (same for 72-111, 112-151, 152-191)
$P $E/analyze.py > $O/analyze.log                      # summary.json: tables, predictions, reading
```

The longest run took 240.3 s and the most memory any run used was 603 MB.
