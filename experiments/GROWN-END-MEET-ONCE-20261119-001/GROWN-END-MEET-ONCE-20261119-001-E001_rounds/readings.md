# Which current readings separate the archived extensions?

The six-junction start with repeated meetings gives 48 automorphisms of the first grown pair table that fix every distinction in every live support. Exactly 16 extend through the second round. The same 16 work with exact old names, with loose distinctions re-paired inside their holders, and with new junctions matched through the round. They also carry the old equation span. The other 32 fail on already shared distinctions.

| Added observation on the current stage | Failures detected | Extenders rejected |
| --- | ---: | ---: |
| Unary and pair minimum bond sizes, including existence | 0 of 32 | 0 of 16 |
| One pair query on `0,1`, asking whether the names occur in exactly the same bonds | 32 of 32 | 0 of 16 |
| One pair query on `0,1`, asking whether more than one bond contains both | 32 of 32 | 0 of 16 |
| One triple query on `0,1,15`, asking for the least bond size | 32 of 32 | 0 of 16 |
| One triple query on `0,1,15`, asking whether any bond contains all three | 32 of 32 | 0 of 16 |
| All triple readings, by least size or by existence | 32 of 32 | 0 of 16 |

The entire current group allows arbitrary permutations of `0,1,2,3` and an independent exchange of `7,8`. Distances to the fixed live distinctions limit the group to these permutations, and exact comparison of the full table confirms all 48. Its extending subgroup preserves the partition `{{0,1},{2,3}}` and still permits the independent exchange. Each of the two same-side pairs occurs together in 21 bonds and has identical bond occurrence columns. Every mixed pair occurs together in one bond and has different columns. Thus either pair Boolean already tests the partition on every one of the 48 maps.

For the triple query, `(0,1,15)` is included in a bond of size four. Its image `(2,1,15)` under the originally exhibited exchange is in no bond. For all 48 maps, a query is compared with its image. The exact replay finds 34 individual triples that make the same classification, with either least size or existence. Any of the 15 names fixed by the whole group, `4,5,6,9–20`, also works as a common probe with all its pair completions. The full triple reading agrees with this classification.

The minimum number of extra queries is one for either pair Boolean and for either triple convention. The minimum *arity* is three within the convention that a reading gives the least size of a bond containing its named distinctions, or existence alone. When richer observations are allowed, the pair Boolean gives arity two. An equivariant unary observation of the current allowed states and growing end is constant on each orbit of the equation-span-preserving subgroup. Every one of the 48 maps moves names only inside these orbits, including the four middle names in one orbit. Hence such a unary observation cannot distinguish any of the failures. This arity argument and the query minima concern the archived example.

## Replay of the meet-once witness

The seven-junction start with four central junctions `A,B,C,D` grows through stages of 12 and 16 junctions. The replay checks that junctions meet at most once throughout and that every junction support is itself a support-minimal parity equation. It recomputes both rounds, all live supports, and the full connected-cut and support-minimal XOR tables. The two calculations agree on 120, 253 and 435 pair entries at the start, current stage and successor. Both full table hashes and both bond counts, 364 and 996, agree with the production record.

The exchange of `AC` and `BC` fixes every live distinction and preserves all 253 current entries. The ordered distances for `(AC,AD)` and `(BC,AD)` change from `(3,3)` to `(2,3)`. In the explicit indexing, `{0,2,23}` is a bond through `AC,AD`, and the least bond through `BC,AD` is `{0,1,2,3}`. The names are already shared and the unequal entries rule out every assignment of fresh names, including when loose old names are re-paired within live junctions.

```bash
python3 -B experiments/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/readings.py
python3 -B experiments/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/verify_once.py
```

[Archived input and prior proof](../../../proofs/GROWN-END-SWAP-20261119-001A/GROWN-END-SWAP-20261119-001A-P001_shared_distinctions/proof.md) · [All current maps and reading classifications](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/readings.json) · [Meet-once replay](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/verify_once.json)
