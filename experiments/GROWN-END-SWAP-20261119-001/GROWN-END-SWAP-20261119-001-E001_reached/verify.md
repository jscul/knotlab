# Exact replay of the complete-round obstruction

The proposed seven-junction start and the six-junction variant both give a reached stage whose full bond-distance table admits the exchange of distinctions `0` and `2`. It preserves the loose distinctions, the full support of every live junction, and both the whole family of sets met by one junction and its maximal members. At the next stage the distance for `(0,1)` is `2` and that for `(1,2)` is `3`. All three distinctions were already shared at the reached stage. Every extension of the exchange would still have to carry `(0,1)` to `(1,2)`, including after any re-pairing of loose distinctions within a live junction. The successor still has its identity isometry.

Both starts are connected, have at least three distinctions per junction, and have no forced distinction or non-outside cut holder. Both use pairs of junctions that share more than one distinction. The experiment assesses the marked extension claim in this setting. The six-junction witness is the smaller of the two checked constructions.

| Case | Junctions from start through successor | Current entries checked | Successor entries checked | Current and successor bond-distance values through `(0,1)` and `(1,2)` |
| --- | --- | ---: | ---: | --- |
| Frozen seven-junction start | 7 → 11 → 15 | 231 | 406 | `(3,3)` → `(2,3)` |
| Six-junction start | 6 → 10 → 14 | 210 | 378 | `(3,3)` → `(2,3)` |

## A short check of the six-junction witness

Call the three starting junctions attached by the four marked distinctions `A`, `M`, and `B`. Junctions `A` and `M` share `0,1`, and `M` and `B` share `2,3`. Use the literature's holder graph for the bond calculation, with the outside holder supplying the second holder of each loose distinction.

For a bond containing one marked distinction and any other distinction outside the four, consider the shores of its cut. If `A` and `B` lie on opposite shores, move `M` to the other shore. Before the move `M` has exactly one distinct neighbour on its own shore, and afterward it has exactly one on the other. Both shores stay connected, the two central pairs trade places, and the remaining cut is unchanged. If `A` and `B` lie on the same shore, a bond containing a central distinction must have `{M}` as its other shore. This places all four central distinctions in the cut. These facts give the same distances from `0` and `2` to every distinction outside the four. They also show that the least bond containing one distinction from each central pair has size four.

In the first grown stage there are two edge-disjoint paths from `A` to `B` avoiding `M`. The two routes from `A` to the outside have distinction sequences `(4,9,15)` and `(5,7,12,16)`. The two routes from `B` are `(13,17)` and `(14,19)`. A cut with `A` and `B` on different shores therefore has at least two more distinctions besides its central pair. The least bond containing either central pair has size four, as witnessed by `{M}`.

In the successor, the shore consisting of `A`, `S`, `D`, `E`, the two first-round pair junctions on that side, and their second-round junction has cut `{0,1,21}`. It and its complement are connected. Junctions `A` and `B` still have a route avoiding `M`, so there is no cut consisting of just `0,1`. The least bond through them now has size three. The least bond through `1,2` still has size four by the singleton argument.

## Replay

`verify.py` uses only the Python standard library. Given explicit supports, it checks each preceding round and the successor. It derives candidates from common neighbours, enumerates maximal groups, and assigns leftover loose distinctions to offshoots. It recomputes lookahead on the new junctions and tests implied parity by GF(2) elimination before applying the fresh-count rule. The table calculation scans all shores up to complements and uses cuts with two connected shores. The companion `verify_controls.py` independently enumerates support-minimal XORs and compares every table entry from both methods. The code calls neither the search implementation nor the predecessor growth and table programs. The replay is an in-task check of the explicit constructions.

Static Proposition X detects a failing extension and has no reached history in the replay. The reached identity extends, the closing round takes only the implied parity and has zero fresh distinctions, and exchanging `15` and `16` in the six-junction witness fails both the current-table and full live-support checks.

```bash
python3 -B experiments/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/verify_controls.py
python3 -B experiments/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/verify.py CASE.json --unrestricted
```

The case JSON contains `a` and optionally `b`, each with `start`, `current`, `next` and an optional ordered `intermediate` list. Omit `b` for a self-matching. Distinction names are nonnegative integers and `permutation` lists `[old name, image]` pairs. Optional `certificates` provide a `stage`, `pair`, exact `distance`, and optional zero-based `shore` indices. The checker recomputes all entries, including any supplied minimum. The saved replay contains the complete inputs, round demands and counts, verified certificates, and control outcomes. [Replay JSON](../../../artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/verify_controls.json) · [Formation rule](../../../proofs/FRESH-COUNT-20261118-001A/FRESH-COUNT-20261118-001A-P001_free_count/proof.md) · [Extension referee](../../../research/EXTEND-ROUND-20261119-001/referee-R1/report.md)
