# Independent audit of the finite interval

The generator's width and junction-count totals agree with the accepted censuses at widths 18, 19 and 20. The audit streamed every published population record to count its junctions and hash the source file. It independently rebuilt all 27 selected control presentations and 59 selected presentations at widths 21 through 26. The selection includes the first record at each feasible junction count, the last record, four indices set by SHA-256, and the first record with a legal triple. These checks validate the generation and measurement paths. The interval verdict uses the separate complete marked comparison. [Audit code](audit.py) · [Compact replay evidence](audit.json)

| Width | Published presentations | Independently measured samples | Samples with a legal triple |
|---:|---:|---:|---:|
| 18 | 3,495 | 9 | 1 |
| 19 | 8,191 | 9 | 3 |
| 20 | 19,414 | 9 | 2 |
| 21 | 46,449 | 10 | 1 |
| 22 | 112,335 | 9 | 1 |
| 23 | 273,842 | 10 | 3 |
| 24 | 672,424 | 10 | 3 |
| 25 | 1,661,752 | 10 | 2 |
| 26 | 4,131,343 | 10 | 3 |

## Coverage of the generator

The current ordinary incidence and loose counts specify all current extensions up to names. The forward generator starts with the ternary seed and chooses both output counts for each admissible parent set. Its pruning chooses the earliest required number of interchangeable holders of each kind. Each such class consists of junctions with equal loose counts whose transpositions preserve the complete ordinary incidence. Thus every eligible parent set is equivalent to one retained parent set. Reassigning the actual chosen distinction among the loose distinctions at a holder also preserves the isomorphism class of the resulting incidence.

The canonical calculation refines ordered color classes by their exact neighbor counts, then individualizes a smallest unresolved class and selects the minimum complete encoding. It omits a branch only when a transposition already preserves the colored incidence. The full lower adjacency array and loose counts fit in the encoding, so equality of keys certifies incidence isomorphism. The hash table stores the complete key and checks equality after a hash collision. Width layers therefore contain all reachable types by induction. The archived counts provide an independent check of this implementation for all possible junction counts at each control width. [Generator](population.cpp)

## Independent relation and menu checks

For each sampled record, reverse removal recovered a history back to one junction on three distinctions. The audit then replayed the actual input and fresh names at every join. It computed the menu directly over unordered triples of loose distinctions.

The table calculation used a basis of the allowed-state relation. Gaussian elimination expresses each named distinction as a binary linear form in free coordinates. A second elimination on these forms retains the original names and enumerates the kernel, which is the parity space. Each nonzero kernel support is tested for inclusion-minimality using projected rank. Because the sum of the forms on the support vanishes, independence after deleting one distinction forces the full support to be its unique nonzero dependence. The minimum cardinality of a retained support through each pair then gives the scalar entry. This primal-rank calculation agreed entry for entry with the earlier dual-space calculation on all 86 samples. Exact marked orbit checks found no opposing self-isometry on those records. [Independent checker](audit.py) · [Earlier exact interface](../../VARIABLE-OUTPUT-READER-20261118-001B/VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/check_reverse.py)

The compiled comparison also returned the same 20,345 individual pair entries and exactly the same named menus on those 86 samples. It measures bonds by enumerating ordinary shores connected on one side, then checking that every component of the complement connects to the wired exterior. That test characterizes an inclusion-minimal cut independently of the audit's projected-rank calculation. The optional `--grader` argument to the replay checks the compiled comparison on precisely the saved records. [Compiled comparison](compare.cpp)

The controls recover the 18 legal triples and 69 bonds of the named width-19 example after relabeling. A planted menu with the same 18 entries fails under the actual swap of 11 and 12. At width 22 an accepted legal and forbidden triple agree on all 60 entries involving a mark under the archived map. Ten other entries differ, and exact marked comparison rejects every full-table isometry between those marks. [Width-19 positive and mutation](../../VARIABLE-OUTPUT-READER-20261118-001B/VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/reverse.json) · [Width-22 negative](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/continuation.json)

## Cases requiring exact self comparison

The complete comparison's per-width population and pair totals agree with the independent scan. No two different records at the same width share the compiled rejection fingerprint. An exact isometry preserves the fingerprint because each hashing step uses only multisets of entries with their preceding row colors. This leaves no cross-record suspects.

The compiled comparison passed every triple-bearing record either by a mark profile that determines the menu on that record or by exact symmetry checks. The audit independently replayed all 311 records submitted to exact self comparison, with counts 0, 4, 12, 31, 67 and 197 from width 21 through 26. Every record matched its original population line and had a legal and a forbidden mark sharing the compiled profile. Each history replayed from the seed, each table was remeasured by projected rank, and every legal marked orbit was complete. The archived generator-check counts add up to the totals in the complete comparison. [Exact-case roster](residual_cases.jsonl) · [Independent verdicts and receipts](audit.json)

One deliberate mutation uses source line 16,537 at width 22. It replaces the legal triple `{13,14,20}` with the forbidden triple `{13,14,16}`, keeping the menu at 15 choices. The exact checker rejects the mutation because the actual scalar transposition of 19 and 20 maps the still-listed triple `{13,14,19}` to the deleted triple.

From the repository root, replay the compact evidence with the workspace Python:

```sh
family=proofs/VARIABLE-OUTPUT-READER-20261118-001F/VARIABLE-OUTPUT-READER-20261118-001F-P001_finite_interval
.venv/bin/python -B "$family/audit.py" --replay "$family/audit.json" | cmp "$family/audit.json" -
```
