# Canonical qualification of the jumping starts

**Fourteen of the sixteen jumping starts pass the canonical parity test.** Starts 08 and 15 each have a proper subset of one declared knot that already carries a parity equation. The full screen identifies 690 canonical starts in the original 1,000 cap-seven draws. Fourteen of those 690, or 2.03%, have the recorded jump classification. [Complete source audit and literal supports](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/sources_audit.json)

## The two exclusions

Each recorded meeting occurrence gets its own distinction. Labels start at zero and follow the order of the archived meetings, then the loose distinctions by junction. We enumerate the GF(2) span of the literal parity rows. For a support \(S\), the equations that survive projection onto \(S\) are precisely the span words contained in \(S\). The declared row constrains its whole support, and the zero assignment satisfies all rows. A nonzero span word on a proper subset violates K2.

| Start | Original frame and zero-based draw | Junction failing K2 | Its literal support | Smaller supported equation | Allowed assignments on the declared support |
|---|---|---:|---|---|---|
| 08 | cap-7-07, 107 | 3 | {0, 2, 3, 4, 7} | Rows 1 and 3 XOR to {0, 7} | 8 of the 16 single-parity assignments |
| 15 | cap-7-09, 111 | 4 | {0, 5, 6, 7, 8, 9} | Rows 4 and 7 XOR to {0, 5, 9} | 16 of the 32 single-parity assignments |

The three-place supports of junction 1 in 08 and junction 7 in 15 already lie wholly inside the respective failed supports. In each case the span restricts to rank two there. Every individual distinction can still take either value. That singleton check would miss both failures. The original count records give jumps from 52 to 158 and from 90 to 324. Their starting relations fail the canonical gate despite satisfying the original funding and common-holder screens. [Exact support checker](../../experiments/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/sources_span.py) · [Earlier archive and parity gate](../PARTNER-SEVEN-20261119-001/screen.md)

## The original weighting and corrected counts

EXPLOSIVE drew 200 accepted labelled sources at each starting size from six through ten. Its generator draws a uniform labelled tree and adds a uniform subset of non-tree meetings conditional on their number. That number comes from a Poisson draw with its mean chosen uniformly from 1, 2, and 3, capped by availability. Each junction is marked exhausted with probability 0.2, with repeat meetings added when needed to reach three places. The original arity, funding, common-holder, and valid-triple filters condition the accepted draws. The cap-five frame uses its own arity ceiling and the cycle-five frame also requires a positive filled cycle rank. The census and the chosen references retain their original selection rules. This audit reapplies K1–K3 to every accepted draw in each fixed frame. It independently reproduces the filled reading, both overlap flags, the initial filled cycle ranks, and the class at the frozen stopping horizon on all 3,200 archived rows. [Original design](../EXPLOSIVE-20261119-001/preregistration.md) · [Exact original record](../../artifacts/EXPLOSIVE-20261119-001B/EXPLOSIVE-20261119-001B-E001_filled/results.json)

| Starting junctions | Original cap-seven draws | Original jump class | Canonical draws | Canonical jump class |
|---|---:|---:|---:|---:|
| 6 | 200 | 8 | 159 | 8 |
| 7 | 200 | 6 | 144 | 5 |
| 8 | 200 | 1 | 135 | 1 |
| 9 | 200 | 1 | 123 | 0 |
| 10 | 200 | 0 | 129 | 0 |
| **Total** | **1,000** | **16** | **690** | **14** |

The fixed original frame contains 14 qualified jumping draws out of 1,000. Deleting only 08 and 15 gives 14 of 998 and leaves 308 additional draws outside the canonical gate. The fully screened conditional share is 14 of 690. It gives equal weight to each retained draw, so different starting sizes contribute in proportion to their retained counts. Each figure describes the fixed archived weighting and stopping rule. The jump classification records a tripling at or after round four when the earlier frozen classes do not apply.

| Readout | Original | Only 08 and 15 deleted | Full canonical gate |
|---|---:|---:|---:|
| Cap-seven X1 agreement on decided zero-rank cases | 835 / 864 | 835 / 862 | 545 / 571 |
| Cap-seven X1 based on non-overlapping decided zero-rank cases | 775 / 776 | 775 / 776 | 493 / 494 |
| Cap-seven X1b failures on decided positive-rank cases | 0 / 99 | 0 / 99 | 0 / 87 |
| Jump class among seven-place starts with both overlap flags | 16 / 117 | 14 / 115 | 14 / 102 |
| Undecided in that same overlap stratum | 35 | 35 | 30 |
| Within-five jump class, fresh draws plus census | 0 / 2,191 | 0 / 2,191 | 0 / 1,661 |
| Within-five X1b failures, fresh draws | 2 / 12 | 2 / 12 | 1 / 7 |

All fourteen qualifying jump rows contain a seven-place junction and have both overlap flags. Their initial filled ranks \(b_1,b_2\) are zero. Thirteen ended at the original resource limit. The smallest, 00, was still open at the original horizon and closed at round 23 on replay. Among the fresh within-five samples, 1,281 of 1,712 cap-five draws and 2 of 5 selected cycle-five draws qualify. The fixed within-five census contributes 378 of 474. The zero jump counts apply at the study's limits. X1 and X1b still fail and X2 and X3 still hold under the frozen rules.

The same three horizon reconciliations reported by the referee survive the full gate. They are cap-7-06 draw 91, cap-7-10 draw 176, and cap-7-07 draw 126. The non-overlap horizon check is the second of these and resolves the single remaining frozen disagreement in that stratum, giving 494 of 494 after that check. The separate control of 346 decided nonjump draws preserved its class on every replay, and 249 of those draws pass the gate. All nine deliberately chosen reference starts qualify, including their five jump-class cases. The reference and replay controls retain their own weightings. [EXPLOSIVE referee report](../EXPLOSIVE-20261119-001/referee-R1/report.md)

## What changes in the later studies

| Follow-up readout | Original archive | Canonical starts |
|---|---:|---:|
| MERGE-BURST named starts | 16 | 14 |
| MERGE-BURST positive rounds before the separate reading checks | 116 | 101 |
| MERGE-BURST finite readings | 2 | 2 |
| MERGE-BURST non-control starts reaching a reading | 1 / 15 | 1 / 13 |
| Unresolved at the MERGE-BURST boundary | 14 | 12 |
| Unresolved MERGE-BURST ends by memory or time | 10 memory, 4 time | 8 memory, 4 time |
| Unresolved with an earlier cycle-of-three-blocks obstruction in the referee replay | 9 | 7 |
| WALL-READ positive birth ages | 140 | 123 |
| WALL-READ stage records including age zero | 156 | 137 |
| WALL-READ B3 comparisons agreeing with the lower bound | 140 / 140 | 123 / 123 |
| WALL-READ B5 next bound better than last built count | 0 / 13 | 0 / 11 |
| WALL-READ B6 unread starts reaching a single block | 0 / 14 | 0 / 12 |

The two excluded starts account for 8 and 7 of the positive MERGE-BURST rounds. They account for 9 and 8 WALL-READ positive ages. Each stopped by memory in both follow-ups. Every retained unresolved MERGE-BURST history still has overlapping maximal blocks at the archive boundary. Start 00's block of 9 and start 04's block of 781 retain their closing readings. Start 04 still supplies the exact 304,590-birth successor. Both named closing controls qualify, and the referee's checks pass at their original coverage. [MERGE-BURST results](../../artifacts/MERGE-BURST-20261119-001B/MERGE-BURST-20261119-001B-E001_stages/results.json) · [MERGE-BURST referee](../MERGE-BURST-20261119-001/referee-R1/report.md)

The WALL-READ predictions retain their reported verdicts. The independent B1 panels give 26,441 census agreements, 995 random agreements with five resource stops, and two read-start agreements under their original selection rules. The start-03 post hoc B2 check verifies 993,164 incoming incidences and 28,065 births at age eight, completing the unfinished double count in the frozen output. The start-03 threshold in B4 still fails at the frozen budget. The WALL-READ proof's mixed machine-check panel has 6,021 M3 stages and 1,955 M4 checks after deleting the two archive cases, with 60 nonempty M4 constructions. The original counts were 6,033, 1,963, and 61. Its random stratum and the independent M1 and M2 controls retain their original scope. [WALL-READ frozen results](../../artifacts/WALL-READ-20261119-001B/WALL-READ-20261119-001B-E001_past/results.json) · [Completed B2 check](../WALL-READ-20261119-001/posthoc/double_count.json) · [Proof controls](../../proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/machine_check.json)

The latest incidence records for 02, 05, and 08 remain exactly relabeled. The literal beginnings of 02 and 05 qualify and still provide canonical witnesses for that later incidence. The difference in the starting gate matters when counting source histories. [Exact incidence maps](../HUB-GUIDED-SAMPLE-20261119-001/inputs.md)

## Replay

The machine audit carries the original frame and draw identifiers, all gate verdicts, the sixteen literal supports and their spans, and the original and filtered study counts. The retained input bundle preserves the raw parsed frames and follow-up records with the original runner hashes. The gate controls include a failed support with one forced distinction and a failed support with a smaller parity equation and every distinction individually free. [Machine audit](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/sources_audit.json) · [Retained raw inputs](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/sources_inputs.json.gz)

```sh
family=experiments/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks
.venv/bin/python -B "$family/sources_audit.py" --use-retained
```

The scoring run completed all 21 original sampling batches. The retained-input replay recomputed every gate and comparison and reproduced the audit byte for byte under a different Python hash seed.

The canonical `knotlab check` command with forgetting erasure also evaluated all seven distinct projected truth tables among the 107 original junctions of the sixteen named starts. It returned precisely the two failed junctions listed above. [Truth-table replay](../../experiments/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/canonical_controls.py) · [Results](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/canonical_controls.json)
