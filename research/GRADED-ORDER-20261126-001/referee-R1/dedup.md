# Deduplication and source replay

The two frozen samples reproduce in full, with no hash merges of distinct starts in either sampled stream. One start was retained under both weightings. The 176 retained rows represent 175 starts up to renaming.

| Weighting | Source draws | Draws eligible for a bucket | Eligible starts up to renaming | Retained starts up to renaming |
| --- | ---: | ---: | ---: | ---: |
| `tree+` | 40,000 | 11,852 | 214 | 83 |
| `grow` | 200,000 | 1,413 | 724 | 93 |

The eligible draws contain 935 starts up to renaming when pooled, three of which appeared under both weightings. The retained samples have one pooled repeat. In the order of knot labels 0 through 6, the renaming from the [`tree+` row at source draw 267](../fresh7_treeplus.jsonl#L80) to the [`grow` row at source draw 96352](../fresh7_grow.jsonl#L78) is `[2, 5, 6, 0, 4, 3, 1]`. It preserves all place counts and pairs carrying shared distinctions. Both copies have neither exception flag, and the stored comparisons agree under both laws. Parity reads three rounds before closing at round 4 and not-all-equal reads to round 24 in both copies. [`tree+` parity](../scored_fresh7_treeplus_parity.jsonl#L80), [`tree+` not-all-equal](../scored_fresh7_treeplus_nae.jsonl#L80), [`grow` parity](../scored_fresh7_grow_parity.jsonl#L78), [`grow` not-all-equal](../scored_fresh7_grow_nae.jsonl#L78).

## Corrections

- **Not a block.** “Population (fresh, drawn by structure before any growth; every count below is up to renaming)” applies within each weighting. The pooled “127 starts of two weightings, 254 start-and-law cases” counts 127 retained rows and 254 comparisons covering 126 distinct starts and 252 distinct start-and-law cases. Of those distinct cases, 211 read through round 24 and 41 closed early. All 49 flag-bearing retained rows represent distinct starts. [Design](../README.md#L62), [results](../README.md#L120), [decision](../decision.md#L12).
- **Not a block.** “39 with a split pair, 3 with cells sharing two knots (one also a split pair)” counts the 39 `tree+` starts with a split pair alone. The sample has 40 with a split pair in total, including one whose cells share two knots. The “39 `tree+`” results row with first differences at round 2 applies to the split-pair-only cases. The case with both flags is in the round-1 row. [Design](../README.md#L65), [results](../README.md#L121), [frozen sample](../fresh7_treeplus.jsonl).

## How it was checked

The replay used the declared seed, source sample function, seven knots, and per-bucket limits. A draw could enter a bucket only after the study's static filters, and the first listed stratum and the route-cycle flag determined its bucket. The same selection was run with the original hash and with an exact comparison up to renaming. For the latter, the checker minimized the list of all pair multiplicities over permutations within groups of knots with equal size and equal multisets of shared partners' sizes and multiplicities. Equal canonical lists and correspondingly ordered knot sizes therefore give a renaming, and every renaming preserves the groups and lists being minimized. The exact check also pooled the frozen samples. The [source replay](dedup.py) verified all saved rows' places, pairs, distinctions, static flags, and order. Every distinct eligible start within a weighting had its own hash, including draws after quotas filled, and using the exact check retained the same 83 and 93 rows.

In the bucket for a block meeting a group cell in two knots with no route cycle, the caps excluded 131 eligible `tree+` starts and 631 eligible `grow` starts up to renaming. The buckets retain the first representatives within their quotas, so retained counts describe the frozen samples. The eligible draw counts describe the realized streams. Neither count is a census of the weightings' support.

The 1,000-draw prefix per weighting took 0.52 s and peaked at 38,096 KiB. The full replay took 33.00 s and peaked at 39,012 KiB, one process under a 2 GiB cap. Growth and scoring were read from the existing score records for the shared start. Additional growth, other seeds, and enumeration of either weighting's full support were outside this check. [Prefix data](dedup_pilot.jsonl), [prefix timing](dedup_pilot.time), [full data](dedup_full.jsonl), [full timing](dedup_full.time).
