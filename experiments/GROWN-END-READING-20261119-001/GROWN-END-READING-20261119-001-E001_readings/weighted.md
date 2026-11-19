# Doubling the original shared distinctions

The marked pair-and-triple reading preserves the full equation span in every one of the 256 multiplicity assignments, at both marked ages. Adding the pair-flip reading leaves the same maps. Every surviving renaming therefore extends to the next pair table with the fresh names fixed.

| Marked stage | Junctions | Distinctions across the 256 cases | Representatives checked | Full pair-and-triple maps | Also keep every flip bit | Carry the equation span |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| After round one | 12 | 23–31 | 448 | 12,636 | 12,636 | 12,636 |
| After round two | 16 | 30–38 | 448 | 12,636 | 12,636 | 12,636 |

The counts of full maps sum across labelled multiplicity assignments. At either age, 128 assignments have one representative, 96 have two, and 32 have four. The full group sizes range from 2 to 1,024, with the same size for each assignment at both ages. This is exhaustive for one-or-two multiplicity choices on the original shared distinctions of this one start. It samples the wider setting with repeated meetings.

## Why the same rounds and bonds can be reused

The seven-junction start has eight ordinary shared distinctions, numbered `0` through `7`. For each one, independently keep a single copy or add one extra copy with the same two holders. Every loose distinction and its holder stay fixed. Candidate pairs and maximal joining groups read which junctions meet, so a parallel copy of an already shared distinction cannot alter them. Each parent still contributes the same old loose names. Lookahead reads the new parent sets, and the implied-parity test in the connected arrangement depends on whether the group consumes all loose names. Fresh counts and the subsequent rounds therefore agree, up to naming, across the whole family. The verifier also replays all three literal rounds for each assignment. [Source start and first two rounds](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/two_histories.json) · [Complete-round reading](../../../research/EXTEND-ROUND-20261119-001/extend_round.md)

In the literature's holder graph, a bond has two connected shores. Adding parallel distinctions leaves the connected shores unchanged. A bond contains a duplicate exactly when it contains the original distinction, with one extra unit in its size. The program checks the 364 first-round and 996 second-round bond supports independently by connected shores and support-minimal XORs. It then computes each weighted pair and triple minimum from those supports, including absence of a common bond.

## Complete map comparison

The enumeration fixes every distinction belonging to a live junction. It preserves the full pair and triple tables before testing the extra flip reading. A permutation of parallel columns among the free old labels preserves the equation span and every current reading. Within each class of such columns, requiring the source names to have increasing images gives one representative per coset of these permutations. This still permits the image of a source class to split across different target classes. It therefore gives the complete pair-and-triple group even when the pair-flip reading is omitted. The identity on fresh names extends every equation-preserving representative because the old map fixes all loose inputs to every new junction. The same reasoning applies to each parallel-column permutation, so it also applies to all maps counted through the cosets. An exact constrained successor-table search is available for any survivor that changes the equation span. The run found zero such survivors.

For masks `0`, `1`, and `255` at both ages, direct XOR enumeration on the expanded supports checks every weighted pair and triple minimum. Full enumeration without the parallel-column quotient independently verifies the group counts, including when the flip filter is omitted. The complete run took 15.14 seconds and 65,748 KiB peak RSS.

```bash
.venv/bin/python -B experiments/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/weighted.py
```

[All 256 assignments and both ages](../../../artifacts/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/weighted.json)
