# Exact reading refinements on the four named stages

The simultaneous pair-flip reading leaves all four failing permutations in each of the three minimum meet-once arrangements. Minimum common bond size on triples, including absence of a common bond, removes every failure in all four named arrangements. In each case the maps that preserve the full triple reading are exactly the maps that extend to the next pair table and exactly the maps that preserve the current equation span.

Each count is written as **maps extending / all maps admitted**. A map fixes every distinction in every live support and must extend with its complete old permutation. Allowing re-pairing within live junctions gives the same counts. All successful maps also extend by fixing the fresh names individually.

| Current arrangement | Pair table | Also every pair-flip bit | Also every triple minimum | Both refinements | Equation-span preservers |
| --- | ---: | ---: | ---: | ---: | ---: |
| Meet-once allocation 0, seven-junction start | 4 / 8 | 4 / 8 | 4 / 4 | 4 / 4 | 4 |
| Meet-once allocation 1, eight-junction start | 4 / 8 | 4 / 8 | 4 / 4 | 4 / 4 | 4 |
| Meet-once allocation 2, eight-junction start | 4 / 8 | 4 / 8 | 4 / 4 | 4 / 4 | 4 |
| Archived meet-twice six-junction start | 16 / 48 | 16 / 16 | 16 / 16 | 16 / 16 | 16 |

Two distinctions can flip together with every other distinction held fixed exactly when their parity columns are equal. In the declared parity presentations a column is the set of holders. If junctions meet at most once, the only distinct names with the same holders are loose distinctions in a common live junction. All such names are already fixed under the pointwise condition. Thus this pair-flip reading adds no restriction in the meet-once setting. In each of the three named meet-once stages, its only true pairs are `{19,20}` and `{21,22}`. In the meet-twice control, `{0,1}` can flip together and its image `{1,2}` under the published swap cannot.

The table gives the first lexicographic triple-existence mismatch under each archived failing map. The available bonds displayed below attain the least cardinalities. The distances in the last column are successor bond sizes minus one. Every marked pair there consists of already shared names, so fresh assignments and loose re-pairing cannot change the comparison.

| Arrangement | Current triple and proposed image | Minimum common bonds | Successor pair and image with distances |
| --- | --- | --- | --- |
| Meet-once allocation 0 | `{0,1,6}` → `{0,2,6}` | None → `{0,2,6,14,15}` | `{1,6}` at 2 → `{2,6}` at 3 |
| Meet-once allocation 1 | `{0,1,8}` → `{0,2,8}` | None → `{0,2,8,14,15}` | `{1,8}` at 2 → `{2,8}` at 3 |
| Meet-once allocation 2 | `{0,1,8}` → `{0,2,8}` | None → `{0,2,5,7,8}` | `{1,8}` at 2 → `{2,8}` at 3 |
| Archived meet-twice start | `{0,1,4}` → `{1,2,4}` | `{0,1,4,5}` → none | `{0,1}` at 2 → `{1,2}` at 3 |

In each case even the single yes/no question of whether a bond contains the source triple rejects exactly the failing maps when compared with its image. These four-stage observations give a counterexample to sufficiency of the pair-flip refinement and an exact test of the triple refinements on the named stages. A general sufficiency claim for triples remains open.

## Literal replay

The verifier reads the three distinct presentations and the original six-start witness from the preceding records. It checks both complete rounds against the archived law replay, then compares the entire bond family by two calculations, connected shores and support-minimal XORs. The three meet-once cases each give 253 current pair entries, 1,771 current triple entries and 435 successor pair entries. The meet-twice case gives 210, 1,330 and 378. A full permutation search fixes the live distinctions and tests every current pair entry. The refinements filter the resulting list of complete permutations, including products, before classifying each extension. Exact constrained matching assesses new-name choices. A comparison of the whole equation span is a separate check.

The identity succeeds in all four cases. Each case also records a rejected transposition that fixes the live distinctions but changes a current pair entry. The result includes the explicit supports, archive digests, each enumerated map, and least successor bond certificates for every old-pair obstruction.

```bash
python3 -B experiments/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/named.py
```

[Complete literal results](../../../artifacts/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/named.json) · [Threshold arrangements](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/reach_bound_threshold.json) · [Meet-twice control](../../../artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct_6.json)
