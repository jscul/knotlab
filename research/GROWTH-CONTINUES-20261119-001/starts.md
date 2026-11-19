# Which of the sixteen archived starts can be read to the end?

**Starts 03 and 14 continue indefinitely. Starts 00 and 04 close. The screen leaves twelve unresolved.** All sixteen initial rounds are funded under the roster law. Fourteen starts pass the earlier canonical parity gate. The two outside that gate, 08 and 15, are among the twelve unresolved rows. [Complete per-stage records](../../artifacts/GROWTH-CONTINUES-20261119-001/GROWTH-CONTINUES-20261119-001-E001_checks/starts_screen.json) · [Canonical parity audit](../PARTNER-SEVEN-20261119-001/screen.md)

## The two continuing starts

In both starts one holder has two loose distinctions and belongs to exactly one required group. The complete round spends one distinction on that group and one on an offshoot. These are the holder's only two children. The offshoot has one parent and exactly one candidate, its sibling. It then belongs to one required pair. The fresh-count law gives it two loose distinctions, so the same parent and sibling pattern recurs. There are at least two births in every such round, which excludes a single implied terminal birth. The proof applies from the initial holder onward, and the recorded ages 1–8 verify the resulting chain. [Local continuation proof](../../proofs/GROWTH-CONTINUES-20261119-001/GROWTH-CONTINUES-20261119-001-P001_continuation/proof.md)

| Start | Original holder | Its only group in round one | Age-one offshoot and only candidate |
|---|---:|---|---|
| 03 | 4 | {2, 3, 4} | 8 and 2 |
| 14 | 5 | {2, 3, 5} | 8 and 1 |

The first two columns use the original physical junction order, and age-one labels in the last column are zero-based names within that age's live roster. In the age-zero roster, which omits exhausted junctions, the two witnessing holders are both at position 4. The checker independently traces the initial holder into the age-one sole-parent child and follows that child's identity as the next offshoot's sole parent at each archived transition. At age eight the final recorded pairs are (28,064, 28,063) for 03 and (162,335, 162,334) for 14, with the offshoot first in each pair. The literal parity replay supplies the first two rounds in original physical labels. [Independent replay](../../experiments/GROWTH-CONTINUES-20261119-001/GROWTH-CONTINUES-20261119-001-E001_checks/offshoot_literal.py) · [Literal allowed-state audit](../../artifacts/GROWTH-CONTINUES-20261119-001/GROWTH-CONTINUES-20261119-001-E001_checks/offshoot_literal.json)

For a reached junction with one parent, all its candidates share that parent. Every compatible set containing the junction is therefore held, so it belongs to exactly one pair per candidate. A one-parent junction with at most one candidate has two loose distinctions and supplies the same continuation witness. An isolated junction with at least two parents has one loose distinction. If another birth coexists, its unary child is live and isolated. That child has two loose distinctions and hence makes two siblings in the following round. The sole-junction, sole-distinction case instead permits an implied closing birth.

## Closing and the exact scope of the screen

The screen covers the original starts and all 140 positive ages in WALL-READ's retained count series. It checks 155 nonempty live rosters. For 04, the full block at age eight makes one child for every pair of its 781 junctions. That gives exactly 304,590 children, each with 1,558 candidates. Other recorded incidences use the verified HUB exports or replay from the literal start. All ten pairs of equal live size within one history occur in 00. In each pair the block sizes or candidate degrees distinguish the full rosters. The complete partnered test on the 155 open rosters rejects 78 by size, 8 by a block exceeding the possible transversal size, and 69 by candidate degree. The available exact invariants decide every test in this prefix. [Input provenance](../HUB-GUIDED-SAMPLE-20261119-001/inputs.md) · [Earlier full-roster screen](../PARTNER-SEVEN-20261119-001/screen.md)

Every archived start has one candidate component. In a funded round, each old candidate pair occurs in a born group, either as a residual pair or inside an admitted larger group. These births connect all children of each old candidate component through shared parents. A birth uses parents from one component, so distinct components remain separate. Thus a connected growing end remains connected until it closes, which excludes a proper isolated partnered component throughout these histories. The screen also tests the whole connected end for a funded free or complement-closed partnered roster.

A reached whole growing end of size \(m\ge3\) with a full block has demand \(m-1\) everywhere, exactly its available loose supply. Its subsequent births follow the finite subset count, starting with \(\binom m2\). If all pairs are candidates and the full set is unheld, the whole set is the unique group. A reached junction with one parent would force a full block, so every loose supply is one and the whole group is an implied terminal birth. This gives the second complete-end closing case. For two live junctions the single pair closes only when it consumes all the loose distinctions. For one live junction with one loose distinction the implied single birth closes. Starts 00 and 04 enter the full-block case at ages 14 and 8. Their last births occur at ages 22 and 788, with zero births in rounds 23 and 789. [Accepted one-block reduction](../../proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/proof.md) · [Merge and burst archive](../MERGE-BURST-20261119-001/merge_burst.md)

The twelve unresolved rows all have zero offshoots at their last retained open stage. This excludes the earlier presence of the persistent offshoot, which would have produced another one. It also excludes a future first offshoot along their connected growth. Their next children all have at least two parents. At every further open stage each live junction has a candidate and belongs to at least one required group, so it receives exactly the loose supply that its groups need. Their overall continuation still requires another certificate.

## Archive coverage

The complete block incidences extend through the ages shown. The retained data include exact accumulated junction counts and lower bounds on accumulated distinctions wherever the last loose supply is unknown.

| Start | Last archived age | Live junctions there | Later count or lower bound | Verdict here |
|---|---:|---:|---|---|
| 00 | 22 | 0 | Round 23 has zero | Closes |
| 01 | 10 | 21,516 | Round 11 has 249,882 | Unresolved |
| 02 | 9 | 102,871 | Round 10 has 1,061,953 | Unresolved |
| 03 | 8 | 28,065 | Round 9 has at least 2,174,695,764,693,287 | Continues |
| 04 | 9 | 304,590 | Round 789 has zero | Closes |
| 05 | 9 | 102,871 | Round 10 has 1,061,953 | Unresolved |
| 06 | 7 | 12,004 | Round 8 has at least 7,899 | Unresolved |
| 07 | 7 | 31,735 | — | Unresolved |
| 08 | 9 | 102,871 | Round 10 has 1,061,953 | Unresolved, outside the canonical gate |
| 09 | 6 | 4,652 | Round 7 has 6,210,264 | Unresolved |
| 10 | 7 | 4,157 | Round 8 has 761,879 | Unresolved |
| 11 | 7 | 3,493 | Round 8 has 58,894 | Unresolved |
| 12 | 7 | 36,394 | — | Unresolved |
| 13 | 7 | 35,408 | — | Unresolved |
| 14 | 8 | 162,336 | — | Continues |
| 15 | 8 | 38,001 | Round 9 has at least 2,201 | Unresolved, outside the canonical gate |

The older WALL-READ follow-up completed 00, stopped by time on 09, 10, and 11, and otherwise stopped by memory. It used a ceiling of 7 GiB and 1,200 seconds per start, at up to 40 rounds. MERGE-BURST used 6 GB and 900 seconds at up to 60 rounds. The original EXPLOSIVE cap-seven draw used 2.5 GB and 30 seconds per start, at up to 20 rounds or the first stage exceeding 6,000 accumulated junctions. The present replay stops at the archived roster boundary. [WALL-READ archive](../WALL-READ-20261119-001/wall_read.md) · [Exact later counts](../HUB-GUIDED-SAMPLE-20261119-001/applications.md) · [Deterministic round-nine lower bound for 03](../HUB-GUIDED-SAMPLE-20261119-001/structure.md)

## Which starts were weighted

These are all sixteen rows classified as explosive by the original cap-seven archive. The source takes 200 accepted labelled starts for each initial junction count from six through ten, with a separate seed per count. It draws a uniform Prüfer tree, then adds distinct non-tree meetings uniformly conditional on their count. That count is a Poisson draw with mean uniformly chosen from 1, 2 and 3 and capped by available meetings. Each junction is independently picked as exhausted with probability 0.2 and receives repeat meetings with its existing neighbors when needed to reach three places. Other loose supplies use the source's pair-demand estimate with its recorded random adjustments. Rejection enforces three to seven places, distinct labelled descriptions, sufficient first-round funding, the source's no-double-common-neighbor condition, and at least one valid triple. The historical class also requires a measured round-over-round jump of at least three from round four and no earlier applicable class in the original decision rule. The result keeps each selected archive row once. Starts 02, 05, and 08 have exactly relabeled latest incidences. The sixteen outcomes apply to the fixed jump-selected cohort, whose distribution on complete arrangements is induced by the source procedure. [Original selection and limits](../EXPLOSIVE-20261119-001/preregistration.md#populations) · [Sampler implementation](../../experiments/EXPLOSIVE-20261119-001B/EXPLOSIVE-20261119-001B-E001_filled/job.py) · [Exact relabelings](../HUB-GUIDED-SAMPLE-20261119-001/inputs.md)

## Replay

Run these commands from the repository root with the earlier HUB stage export available. [Input manifest and export commands](../HUB-GUIDED-SAMPLE-20261119-001/inputs.md)

```sh
family=experiments/GROWTH-CONTINUES-20261119-001/GROWTH-CONTINUES-20261119-001-E001_checks
.venv/bin/python -B "$family/starts_check.py" controls
.venv/bin/python -B "$family/starts_check.py" all
```

The controls include the exact four-junction repeat, a funded free partnered case of order three, changes of a held word or loose supply, and the distinction between two coexisting isolated births and one implied terminal birth. The full replay took 4.58 seconds and 521 MiB peak resident memory on this host.
