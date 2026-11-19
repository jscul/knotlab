# Which current readings carry the next pair table?

Every current pair-table symmetry that also preserves the full triple reading extends in this census. The pair flip reading leaves both failures of the pair table alone. The census covers all **33,430 admissible connected meet-once starts through 15 distinctions** and all **30,189 open positive-age stages through 16 current junctions**. It reaches age six with no independent age limit. Every comparison fixes each distinction in every live support individually.

| Added current reading | Passing stages | Failing stages | Unresolved stages |
|---|---:|---:|---:|
| Pair flip | 30,187 | 2 | 0 |
| Full triple minimum | 30,189 | 0 | 0 |
| Both | 30,189 | 0 | 0 |

An extending map preserves the specified current permutation on all old distinctions and has at least one bijection of the fresh distinctions that preserves the full successor pair table. The pair reading is the least common bond cardinality minus one. The triple reading is the least common bond cardinality. An absent bond has a separate reading, recorded as `null`.

## The complete groups on both exceptions

Both exceptions have six starting junctions and occur at age two. An order is the number of distinct old permutations, including identity.

| Starting width | Current width | Next width | Pair-table group order | Extender order | Pair with flip group order | Pair with triple group order | Pair with both group order |
|---|---:|---:|---:|---:|---:|---:|---:|
| 14 | 29 | 33 | 8 | 4 | 8 | 4 | 4 |
| 15 | 30 | 34 | 16 | 8 | 16 | 4 | 4 |

Each triple survivor preserves the current parity equation span and has two possible fresh bijections preserving the next pairs, next flips, next triples and next equation span. At starting width 14 the triple stabilizer contains exactly the pair-extenders. At width 15 there are four additional pair-extenders. For example, exchanging 3 and 4 preserves the current pairs and flips and has two fresh bijections preserving the next pairs. It takes the triple `(0,1,3)`, with no common bond, to `(0,1,4)`, with a minimum bond of size six. It changes the current equation span, and neither fresh bijection carries the next triple reading.

The width-14 failing permutation exchanges 1 and 2. It takes `(0,1,3)`, with no common bond, to `(0,2,3)`, with a minimum bond of size five. The successor pair readings on `(1,3)` and `(2,3)` are two and three, respectively. The width-15 failing permutation `(5 6)(9 10)` takes `(0,5,7)` with minimum bond size six to `(0,6,7)` with minimum bond size seven. Its successor pair readings on `(5,10)` and `(6,9)` are five and four. These changed successor pairs use only already shared distinctions, so no fresh bijection can repair either comparison.

A secondary check keeps only whether each triple has any common bond. This gives the same four maps as full triple minima on each exceptional stage, so it also passes the bounded next-pair census. The artifact records a finite-versus-absent triple mismatch for each rejected map.

## Coverage and validation

The previous full census certifies that every pair-table symmetry fixing the live supports extends on 30,187 open stages. Every refined symmetry group is a subgroup of that pair-table group, so these positive certificates apply to each arm. Replaying the original 402 census shards produced the archived summary byte for byte. On each of its two other stages the checker builds the full group of old pair-table symmetries, then measures each permutation against every extra reading and tests all compatible fresh bijections. It records all permutations and verifies closure of each restricted group and extension subgroup.

The pair flip reading follows directly from the parity equations. Flipping two distinctions with all others held fixed adds the vector supported on that pair. Every equation remains true exactly when its two columns coincide. For a meet-once arrangement any two distinct equal columns belong to loose distinctions of one live junction. Every such distinction is fixed by the old permutation, so the added flip reading leaves the group unchanged at every stage. The program also checks this reading directly on the allowed states of a two-junction control that meets twice.

For the triple measurements the checker enumerates every cut with both shores connected, orders the bonds by cardinality, and intersects bond occurrences of the three named distinctions. It visits 65,535 possible shores on each exceptional current stage and 524,287 on each successor. The resulting pair tables agree with the earlier exact C++ measurements on every current and next pair entry. The two histories replay under the original growth law. On the small repeated-meeting control, independently taking the inclusion-minimal nonzero parity words gives the same bonds and tuple readings, including the absent triple reading.

The conclusions concern extension to the next ordinary pair table within the stated starting-width and current-size bounds. Equation and next-triple transport were checked on the two exceptional stages as separate stronger outcomes.

## Reproduction

Use the reproduction commands of the previous census through its `collect` step. Run the comparison on the resulting `results.json` and the compiled previous census binary. The baseline replay took about 11 seconds with ten workers. The comparison took about two seconds and reproduced its JSON byte for byte.

```bash
family=experiments/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings
python3 -B "$family/census.py" "$scratch/results.json" "$scratch/census"
```

[Previous census and reproduction](../../GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/census.md) · [Exact census results and all exceptional permutations](../../../artifacts/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/census_results.json)
