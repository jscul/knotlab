# Replication and control evidence

The recount used the per-run archives and the frozen seed and comparison records. It recomputed multiset readings, horizons, partitions and cells without loading a reader from the study. All eight input digests in the contract matched. The archived run totals for replication, the held-out forms, the held-out chains and parity were respectively 13,680, 5,490, 5,670 and 5,490. [Recount and tables](replication_counts.json)

| Check | Result |
| --- | --- |
| PR1 | The exact set of names in each class and the last common round matched in all 270 studies. The run counts by round also matched. |
| PR2, PR3, PR5 | All 62 first-told-apart cells, 162 chain-depth cells and 158 wider-record, fate, profile and horizon cells matched. The fate count on the two probe families was 58 and 62 studies of 90. |
| PR4 | No start knot was a roster member after round 1 or in the prospective roster at the end of any of the 9,000 eligible runs. When short knots waited, later start membership occurred in 858 of 1,530 runs of the mixed family, 744 of 1,140 runs of the second probe family, and 1,506 of 1,830 runs of the held-out family. |
| S1, S2, S3 | The bare start had its own class in all 90 linked studies. There were at least two form classes in all 90. The one-knot and two-knot chains were told apart in all 20 eligible pairs under each of 18 laws. |
| PN6 | Three or more classes among the forms in 87 of 90 parity studies. All 90 own-descent partitions and common horizons matched exactly. The wider-record partitions differed in six studies. |
| G | All three written starts rebuilt. The raw gate cases match the seeded sample of 400 without replacement, 287 from the replication runs and 113 from the held-out runs. All 209 runs with no take matched exactly in 2,166 snapshots including their starts. All 191 taking runs recorded agreement in the taking checks for 85,436 births, 9,547 with a take. |
| C1, renumbering | All 900 recorded renumberings matched their corresponding baseline readings, rounds read and stops, including the wider record and second-only counts. All 900 were regenerated on the shared engine using independently written numbering and descent readings. |

PR4 follows from how release spends a member's usable loose distinctions. A short member either bars all of them when retiring or gives all of them to offshoots. A member that can pay its owing gives one to each kept join and releases the rest to offshoots. The resulting shared or barred distinctions cannot become usable loose distinctions again. An old knot with no usable loose distinction can still be a common knot of later members.

The 28 differences among 5,490 pairs under the parity swap concern the recorded fields. Six changed the own-descent reading, the wider record and the final knot count. Six changed the second-only counts and the final knot count. Sixteen changed the wider record and the final knot count. Through the common horizon only three own-descent readings changed, all for the bare start of first seed K under the ordinary count with no taking rule. Every linked form gave the same own-descent reading through its study's common horizon under both knot laws.

## Knot-test coverage and timing

The logs place the gate before the start of the replication runs. The deviations record says entries 1–27 were written before the gate. The freeze commit contains the specification, the seeds and the disclosed probe comparison. The deviations record was committed with the later results.

The first control launch retained 900 renumberings and 241 completed knot-test records. The cut was recorded about 14 minutes after that launch. It retained the first half of each of the two registered control samples and started 22 more jobs from that retained half. Two stopped control shards have no gzip trailer. Taking their complete lines gives 116 and 125 usable records respectively. The combined archive has 1,163 distinct job records.

| Knot law and part of sample | Completed | No completed verdict | Knot-round verdicts |
| --- | ---: | ---: | ---: |
| Not-all-equal, retained half | 99 | 1 | 113,640 |
| Parity, retained half | 50 | 0 | 62,347 |
| Not-all-equal, outside the half | 80 | 20 | 100,244 |
| Parity, outside the half | 34 | 16 | 49,208 |

The archive contains zero failures, disagreements and untested knots within the completed records. The original control ended after 263 of 300 jobs had completed. The text "Nineteen of twenty registered predictions hold" counts the partial knot test as a pass. The result, decision and guide could say "Eighteen checks passed and the fate prediction failed. The knot-test control ended early, with no failing knot in the 263 completed tests." The positive predictions were judged independently of the knot-test sample by the registered criteria. The late cut narrows the original control's coverage.

The gate's implementation could accept an invariant match when exact comparison failed. An invariant match on these fields can miss a structural difference and is compatible with a stop difference when the snapshot count stays equal. All 209 comparisons matched exactly, so the fallback made no difference to the observed gate. For a future use of the gate, require an exact comparison or a verified renaming and check the stopping and no-taking conditions independently.

## Later check of the 37 omitted jobs

All 37 omitted jobs were regenerated on the shared growth engine and matched their archived readings, final knot count, rounds read and stop conditions. A fresh allowed-state calculation passed the 21 not-all-equal jobs on 35,164 knot-round occurrences and the 16 parity jobs on 16,596. Both independent calculations rejected supplied relations with constrained proper projections. The original sample still ended at 263 completed jobs. The original routine was not rerun for the omitted 37. [Unfinished job in retained half](replication_unfinished_knot_test.json) · [Omitted jobs outside the half](replication_omitted_knot_tests.json)

For not-all-equal, each start knot was checked for exact equality of its allowed-state projection with its own rule. Each birth was checked by enumerating the assignments of its old inputs up to global complement, and asking whether each extends in the previous structure. Each new knot has an individually verified fresh distinction held by no other knot in that round. Those fresh distinctions allow any old state to extend, and allow every state satisfying the newborn's rule on its own places when its old inputs are free. Consequently the newborn's projected relation is exactly not-all-equal at birth and remains so in all later rounds read.

For parity, the rank of a projection is the dimension spanned by its distinction rows modulo the span of the parity equations. The independently implemented binary row reduction checked that rank for each start knot, and checked that every birth's old inputs were jointly free. The newborn can extend any old state by setting one of its private fresh distinctions, leaving exactly the parity relation on its own places. The omitted parity jobs had no implied births, and all knots in the 37 runs had at least three places.

## Reproduction

Commands are from the checkout root. Run one process at a time under the displayed memory cap. The recount took about 3 seconds, the 900 renumberings 33 seconds, the formerly unfinished job about 8 seconds and the other 36 about 4 seconds. A slice was timed first for each. The calculations printed JSON that is saved beside this note.

```sh
ulimit -v 2097152
dir=research/FOLLOWS-THE-FORM-20261125-001/referee-R1
.venv/bin/python -B "$dir/replication_counts.py"
.venv/bin/python -B "$dir/replication_control_replay.py" renumber
.venv/bin/python -B "$dir/replication_control_replay.py" unfinished
.venv/bin/python -B "$dir/replication_control_replay.py" omitted
PYTHONPATH=tools .venv/bin/python -B -m knotlab check --cnf 'd0 d1 d2 d5; ~d0 ~d1 ~d2 ~d5' --loops d0 d1 d2 --contact d5 --json
```

The last command checks the projected relation of the first start knot of job 941. It finds 14 allowed states and passes K1–K3 under forgetting. The projected relation was computed by the checks on the start as a whole. The variable labels given to the checker identify its argument places.
