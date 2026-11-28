# Holder patterns and the repetition encoding

Among the 252 grown closures with a strict split and no odd ring around a knot, all minimum strict splits at 198 have the same pattern of readers and holders. Each closure receives one vote. There are 1,586 labelled minimum words at these 198 starts. A pattern retains both holders of every reader distinction and which two distinctions form a reader. It forgets all outside distinctions and any knot left empty. Relabelling may permute the knots, the readers and each reader's two settings.

| Minimum strict readers | Knots holding reader settings | Archived choice | At least one minimum | Every minimum | Labelled minimum words |
| --- | --- | --- | --- | --- | --- |
| 4 | 5 | 198 | 198 | 198 | 1,586 |
| 5, two original readers encoded | 6 | 20 | 20 | 19 | 176 |
| 5, five knots holding settings | 5 | 16 | 18 | 16 | 216 |
| 5, a reader encoded again | 6 | 13 | 13 | 12 | 84 |
| 6, five distinct patterns | 6, 6, 7, 7, 7 | 1 each | 1 each | 1 each | 16, 8, 4, 4, 8 |

All 252 closures admit multiple minimum words. In two six-knot closures there are two different patterns among the ties. The closure grown in one round from census index 6181 has eight words of the 20-start pattern and eight of the 16-start pattern. The one grown from census index 6185 has eight words of the 13-start pattern and eight of the 16-start pattern. The remaining 250 closures each give a single pattern under the stated relabellings. [All nine patterns and witnesses](shapes.json)

The 198 whole holdings are pairwise different even after relabelling. In the selected four-reader words, the knot joining two halves has two reader settings at all 198, but holds exactly two distinctions at only 25. Its full sizes are three at 82, four at 71, five at 19 and six at one. At the eight-knot second-round closure grown from census index 794, every knot holds at least three distinctions. The reader word uses distinctions 6 and 8 of the knot holding 6, 8 and 12. In all 198, the doubled meeting has full multiplicity two, and the two ends of the passed meeting have no direct meeting. The [decision's phrase “198 of them in a single shape”](../decision.md#L23) needs the qualification “the reader settings in every minimum strict split at 198 have one pattern.”

## A realization on four reader bits

Take the four original knot checks in order. Each letter below acts on one reader, and omitted settings act as the identity. Duplicate the first reader's basis value by the isometry `|a b c⟩ → |a a b c⟩`.

| Knot | Original check | Encoded check |
| --- | --- | --- |
| A | ZXX | ZIXX |
| B | ZZZ | IZZZ |
| C | XXZ | XXXZ |
| D | XZX | XXZX |
| Added knot | III | ZZII |

On the image of the isometry, either copy's Z acts as the original Z, the product of the two X settings acts as the original X, and ZZII acts as the identity. The five checks commute and multiply to minus the identity. The supplied state `(|0000⟩ + |0011⟩ + |1110⟩ − |1101⟩)/2` gives signs `+, +, +, −, +` in the displayed order. The calculation checks these signs, all eight logical basis states for the isometry and all sixteen four-reader basis states for commutation and the product. Equality of the marked holders transports this realization to every minimum strict split at the 198 closures, with all outside distinctions fixed at +1. [Calculation and rerun](shape_audit.py)

Two applications of the same operation give the 20-start pattern by passing a setting of a second original reader. They give the 13-start pattern by passing one of the two copies made at the first doubling. Passing a half of the first passed meeting gives a third pattern, absent among the 252 selected words.

The five-reader pattern selected at 16 starts has only five knots holding reader settings. A ring with its common knot starts with one more such knot than readers, including the four-knot, three-reader case. Passing a setting through a new knot and doubling its mate adds exactly one knot holding settings and one reader. The difference of one is therefore invariant under any number of these operations. At the six-knot first-round closure grown from census index 6171, every minimum word has five readers on five knots and the sixth has no reader setting. Two of the six-reader singletons likewise use only six knots. These are explicit limits on the proposed family for this precise operation. [Proposed family](../decision.md#L30)

## Check

The search starts from the independently reconstructed lists of decidable pairs and holders. It rebuilds each parity and sign column and checks them against the earlier reconstruction. Any two readers with the same pair of holder lists can be removed together, preserving all checks, oddness and disjointness. A minimum cannot contain this repetition. The search therefore joins two ordered lists of distinct holder-pair types to find every choice having the target column sum, then counts every disjoint assignment of actual distinctions. It tests all smaller cardinalities and canonicalizes by all knot relabellings consistent with the counts. A second search directly chooses disjoint pairs of actual distinctions at four closures, including both ties. [Code and input paths](shape_audit.py)

From the repository root, run the following command in a shell with the indicated limit.

```bash
ulimit -v 700000
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -B research/READER-SPLIT-20261127-001/referee-R1/shape_audit.py
```
