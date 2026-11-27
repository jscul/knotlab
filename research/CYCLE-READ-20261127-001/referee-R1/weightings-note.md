# Part 3 weighting audit

The replay rebuilt all 47,000 samples and all ten admitted denominators directly from the recorded seeds. It also rebuilt the 192 retained W1 starts and their twin classifications. A replay with the same count guards and no timer found two discrepancies beyond the reported timeout allowances. The deterministic counts measure how often a core crossed a guard. Among those cores, two sampled cores finish at ranks 26 and 32, and another continues with a repeating birth count of 7, 7, 6. [Replay evidence](weightings.json) · [Study table](../README.md#part-3-how-often-a-core-is-unending-1)

## Counts and admission

Each entry gives the count with repeats, then the distinct count. The 120-second timeouts were part of the historical admitted denominators. The deterministic columns replay both count guards and omit the timer. The 1,000 column applies 1,000 wherever the 5,000 column applies 5,000, with the parent-pair incidence guard fixed at 250,000.

| Weighting and knot count | Seed | Admitted | Recorded guard hits | Recorded timeouts | Replayed at 5,000 | Replayed at 1,000 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `grow`, 7 | 31 | 234 / 231 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `grow`, 8 | 31 | 157 / 156 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `grow`, 9 | 31 | 149 / 149 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `tree+`, 7 | 31 | 2,278 / 144 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `tree+`, 8 | 31 | 2,162 / 253 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `tree+`, 9 | 31 | 2,077 / 417 | 9 / 5 | 1 / 1 | 10 / 6 | 12 / 8 |
| `tree+`, 9, W1 | 20261130 | 13,562 / 890 | 55 / 22 | 1 / 1 | 56 / 23 | 70 / 28 |
| `tree+`, 10 | 31 | 1,969 / 583 | 35 / 30 | 4 / 3 | 40 / 34 | 40 / 34 |
| `tree+s50`, 7 | 31 | 2,281 / 1,513 | 25 / 24 | 2 / 2 | 28 / 27 | 34 / 32 |
| `tree+s50`, 8 | 31 | 2,161 / 1,924 | 74 / 74 | 3 / 3 | 77 / 77 | 160 / 159 |

- The first five rows agree in every stored admission and classification category. For both nine-knot `tree+` rows and the eight-knot scaffold, all changes to categories are accounted for in aggregate by replacing recorded timeouts with deterministic guard hits. For ten-knot `tree+` and seven-knot `tree+s50`, the replay has one extra guard hit and one fewer unchained-twin start without chains in each row after that aggregate substitution. Each difference is one sample and one distinct start. The recorded categories for individual timeout cases are unavailable. [Recorded tallies](../part3/) · [Replay evidence](weightings.json)
- The round-map admission check uses not-all-equal and rejects starts with any piece with a cycle by the study's incidence count. The seed-31 standard `grow` results run through nine knots. The design lists ten knots as well, which has no result row. All other seed-31 rows use 3,000 samples. The additional W1 row uses 20,000 samples. [Design and results](../README.md) · [Draw code](../../GRADED-ORDER-20261126-001/graded.py#L125)
- Distinct counts use the study's Weisfeiler–Lehman key, encoding knot places and shared-distinction multiplicities. Exact isomorphism checks on all 20,712 same-key comparisons in the replay found each same-key pair equivalent under renaming. The code excludes earlier keys from the new-distinct count and retained starts, and keeps their full multiplicity in the repeated-sample count. W1 has 890 distinct keys before any earlier-file exclusions and gives exactly the 192 retained starts and classifications, so earlier exclusions need remove no W1 key to obtain its published denominators and sample list. The archive gives no command listing the prior files. [Draw code](../../GRADED-ORDER-20261126-001/graded.py#L61) · [Replay evidence](weightings.json)

## What reaches a count guard

Let `S_r` be the number of nodes already built in one piece through rank `r`. It includes the live start knots at rank 1 and the initial groups and offshoots at rank 2. For each parent `p`, let `d_p` be its number of children at rank `r`. With the final source settings, the study checks the following in order.

1. Stop if the sum of `d_p(d_p − 1)/2` over parents exceeds 250,000. Two children sharing two parents contribute twice.
2. Stop if the number of maximal pairwise-candidate sets exceeds `5,000 − S_r`. The count includes singleton sets and maximal sets sharing a parent, which the round rule discards as groups.
3. Stop if the next births would bring the number of built nodes above 5,000. The check is per piece. The tree-piece draw has no rank-25 limit.

A separate alarm can interrupt a classification and the code caches that timeout by the same key. The study writer emits only retained starts and aggregated categories. [Round rule](../../GRADED-ORDER-20261126-001/order.py#L24) · [Core count](../../GRADED-ORDER-20261126-001/order.py#L75) · [Twin draw](../../GRADED-ORDER-20261126-001/graded.py#L125)

Removing only the parent-pair guard finds one finite start with unchained twins and no chains in each of the two cells with an extra discrepancy. At seed 31, the ten-knot `tree+` sample at index 1547 crosses 332,906 parent-pair incidences before finishing at rank 11 with 1,049 nodes. The seven-knot `tree+s50` sample at index 658 crosses 722,644 incidences before finishing at rank 23 with 1,072 nodes. They each occur once and both pass both 5,000 limits when the parent-pair guard is removed. These two switches would account for the aggregate discrepancies beyond the original timeouts. The historical labels of the two starts are unavailable. [Removal controls](weightings.json)

## Exact continuations past the guards

Two distinct nine-knot `tree+` starts from W1, sampled at indices 4490 and 16615 under seed 20261130, each have one piece. All 26 births at rank 7 for the first share a parent, and all 16 births at rank 11 for the second share a parent. When a full rank of `m` births shares a parent, the next rank has one birth for each pair. From then on, the births of a rank can be indexed by the `k`-subsets of those `m` births. Two share a parent exactly when they share `k − 1` members. For `2 ≤ k < m`, any maximal pairwise set without a common parent consists of the `k`-subsets of one `(k + 1)`-subset. Take two distinct members with intersection `D` and union `U`. A further `k`-subset sharing `k − 1` members with each must either contain `D` or lie in `U`. A set containing `D` and extending outside `U` shares fewer than `k − 1` members with a subset of `U` omitting a member of `D`. The family of all `k`-subsets of `U` has no common parent, and every candidate pair lies in such a family. This gives every subsequent rank and proves termination. [Lemma R](../../../proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/proof.md#lemma-r-what-the-growth-reads) · [Sample parent lists](weightings.json)

The first piece finishes at rank 32 with 67,108,985 nodes including live start knots. The second finishes at rank 26 with 65,735 nodes. Under the relaxed explicit build of 16,000 non-start births, rank 64 and 2,000,000 group-search work units, the first still hits the birth limit and the second builds another 4,368 births before the group-search limit. The exact endings follow from the subset recurrence. A two-knot control with three shared distinctions and 13 loose distinctions on one knot can be enumerated through its ending. With the same relaxed limits the control finishes at rank 14 with 8,191 births after the one live start knot. [Relaxed builds](weightings.json)

A third nine-knot `tree+` start from W1, sampled at index 8915 under seed 20261130, has matching parent incidence at ranks 6 and 9 under a recorded renaming of both adjacent ranks. The deterministic rule depends only on that incidence, so the core continues with 7, 7, 6 births per period. Its replay reaches the maximal-candidate guard at rank 748 after building 4,997 nodes and having 15 parent-pair incidences at that rank. Its deterministic classification took 0.038 CPU seconds. That cost and the bounded size of every rank support inferring that it was a historical guard hit, although the aggregate record cannot distinguish its historical category from the single W1 timeout. The replay establishes a periodic, bounded-per-rank guard hit on the study's own sampled population. [Incidence renaming and guard trace](weightings.json)

## Replay

```sh
.venv/bin/python -B research/CYCLE-READ-20261127-001/referee-R1/weightings.py \
  --verify-keys --compare-birth-budget 1000 --certify --relax 16000 \
  --sample-indices 8915 4490 16615

.venv/bin/python -B research/CYCLE-READ-20261127-001/referee-R1/weightings.py \
  --read-replay research/CYCLE-READ-20261127-001/referee-R1/weightings.json \
  --files tree+_10.json tree+s50_7.json --drop-pair-cap --relax-prefix 12
```

The full run took 45.8 CPU seconds and peaked at 76,216 KiB. The two pair-guard checks took 1.13 CPU seconds in total and stopped after the first matching start for each cell. The replay rebuilt the weighting generators, admission, count guards and classification using the independent round construction. It used the declared key for comparison and checked same-key pairs independently for exact equivalence. A separate comparison against direct pair enumeration and maximal-clique enumeration agreed on pair incidences, groups and guard classifications in 400 small rounds. The producer's historical timer and per-start labels behind its aggregate tallies were unverified. [Replay program](weightings.py) · [Independent construction](core.py)
