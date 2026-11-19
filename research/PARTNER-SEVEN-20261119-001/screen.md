# The touch census and explosive archive contain no complete free partnered stage in the screened prefixes

All 26,441 touch-census arrangements were screened at their first reached age and through age six, stopping at actual stall or closure. The 16 selected explosive starts contributed all 140 positive ages retained by WALL-READ. The screen found no complete free partnered stage of order at least three and no stage in WALL-READ's complement-closed continuation form. These are finite archive results. [Case data and inputs](../../artifacts/PARTNER-SEVEN-20261119-001/PARTNER-SEVEN-20261119-001-E001_seek/archive_screen.json)

## What was checked

The test uses the full live roster and actual blocks. The entire noncandidate graph must pair every live junction with exactly one partner. A transversal takes one junction from each pair. It is held when a block contains it. A complete free stage has every transversal free and each junction has exactly the open supply needed for all its groups. The canonical free start has only pair blocks. For the complement-closed continuation the maximal blocks are held transversals paired with their complements, only free transversals are groups, each open supply equals its demand, and the number of held complementary pairs is at least three and less than the current order. For a named induced partnered set the report also gives the outside common candidates, both-held and both-free complement counts, and exact supplies and demands on its junctions. These induced examples grade only the displayed sets. [Definitions and growth theorem](../../proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/proof.md#setting)

The roster replay uses the admitted complete-round law. It requires one distinction per parent in every group, spends every other loose distinction in a one-parent addition, and uses the exact next group demand to compute fresh counts. The first step of all 26,457 starts was cross-checked with the literal parity engine by comparing every parent set and fresh count, or the same stall or closure. The initial parity gate checks that each support is a bond in the augmented holder graph and that no distinction is forced. Starts that fail the gate are retained as archive rows and excluded from the canonical totals. [Replay implementation](../../experiments/PARTNER-SEVEN-20261119-001/PARTNER-SEVEN-20261119-001-E001_seek/archive_screen.py)

## Touch census

The archive counts each connected arrangement of up to five initial junctions of three to five places once. Its separate labelled multiplicities count 2,626,697 descriptions. The canonical parity gate admits 22,805 arrangements, including 181 already closed, with labelled multiplicity 2,299,861. Across the whole archive 11,010 starts stall before the first birth and 234 start closed. No replay hit a computational cap through age six. [Touch census and weighting](../TOUCH-CENSUS-20261118-001/touch_census.md)

| Age | Reached stages | From canonical starts | Complete paired candidate graphs |
|---:|---:|---:|---:|
| 1 | 15,197 | 11,735 | 6 |
| 2 | 13,588 | 11,013 | 214 |
| 3 | 13,345 | 10,774 | 123 |
| 4 | 12,470 | 10,242 | 32 |
| 5 | 12,098 | 9,972 | 3 |
| 6 | 11,886 | 9,800 | 0 |

The 378 complete paired candidate graphs all have six live junctions, exactly four held transversals, and no free complementary pair. All six first-age examples come from canonical starts. Of the 78,584 reached stages, 63,536 come from canonical starts, including 241 of the complete paired candidate graphs. The finite six-junction binomial control from a single four-place start has the same obstruction. At that stage every open supply is two, and each of the four complementary pairs has exactly one held word. The eight-place WALL-READ control has four free complementary pairs at the start and satisfies the held continuation test through its first three reaches. Reducing or increasing its starting supply by one fails the exact-open test.

There is also a first-age counting check. Five connected junctions of at most five places leave at most 17 loose distinctions, so a first-age partnered order \(k\) is at most eight. All first-age blocks come from the at most five old parent junctions. If every transversal is free, each block has at most \(k-1\) members. Such blocks cover at most \(5\binom{k-1}{2}\) candidate pairs, fewer than the \(2k(k-1)\) required for every \(3\le k\le8\).

## Explosive archive

The 16 starts were selected by the observed jump criterion from EXPLOSIVE's cap-seven random-tree-plus-extra-meetings population. Each has maximum initial arity seven. The canonical gate admits 14 of them, accounting for 123 of the 140 stored stages. These selected starts carry no uniform arrangement or labelled-description weighting. [Source weighting and stopping criteria](../EXPLOSIVE-20261119-001/preregistration.md#populations)

The screen rebuilt 115 stages with exact open counts and complete projected blocks, and rejected eight more from exact projected blocks before a lookahead cap. It rejected the remaining 17 archived stages using necessary incidence counts preserved by WALL-READ. The methods use live count, a held block larger than half the live roster, or the total candidate pair count. For `start-04` at age nine, the 304,590 junctions are all the two-parent groups of one 781-junction block. Every candidate degree is 1,558, since two such junctions are candidates exactly when they share a parent. For `start-14` at age eight, the 162,336 births include one one-parent offshoot, whose candidate degree is at most 70,420 by the largest block. Both degree bounds preclude a complete partnering. [Archived counts](../../artifacts/WALL-READ-20261119-001B/WALL-READ-20261119-001B-E001_past/results.json)

The smallest start has its zero-fresh closing birth at age 22. The other 15 literal roster replays stop explicitly at a birth-size, candidate-pair, or group-enumeration limit. Archived counts still decide the complete partnered predicate through the last retained age of all 16 starts. There is no continuation claim for unarchived ages. The 89 displayed greedy induced examples include 68 with no outside common candidate. In those 68 every complementary pair contains a held word. The artifact retains the exhibited pairing, held complementary words, and open supply alongside exact group demand. No search over all induced subsets or retractions was carried out.

## Replay

The two local closed-run archives and the MERGE-BURST link between their literal starts are identified by path and SHA-256 in the result. WALL-READ's archived summaries are bound in the same way. The group and point limits are recorded in the result. From the repository root, replay with the retained archives as follows.

```bash
family=experiments/PARTNER-SEVEN-20261119-001/PARTNER-SEVEN-20261119-001-E001_seek
run_dir=$(mktemp -d)
.venv/bin/python -B "$family/archive_screen.py" controls
.venv/bin/python -B scripts/longrun.py launch "$family/archive_screen.py" --out "$run_dir" --unit partnered-archive-replay --workers 6 --case-timeout 150 --case-mem 384M --mem-max 4G --prepare-only
.venv/bin/python -B scripts/longrun.py run --out "$run_dir" --foreground --limit 20
.venv/bin/python -B scripts/longrun.py run --out "$run_dir" --foreground
.venv/bin/python -B "$family/archive_screen.py" collect "$run_dir"
```
