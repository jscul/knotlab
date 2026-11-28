# Abstract choice recount

The counting unit is a choice on labelled knots, with a fresh pair of values
for each failing pair and the names of those values suppressed. The class
count uses one vote per class under permutations of the knots.
[Counts and representatives](abstract_counts.json)

| Knots used | Labelled choices covered twice | Classes | Even non-orientable classes |
| --- | ---: | ---: | ---: |
| 4 | 1 | 1 | 0 |
| 5 | 61 | 4 | 0 |
| 6 | 8,547 | 28 | 4 |
| 7 through seven failing pairs | 614,232 | 176 | 19 |
| Total | 622,841 | 209 | 23 |

All 622,841 agree on the closing sign and same-order parity. All six
labelled choices of separated Euler count zero on five knots are orientable.
The five classes in P1 have 60, 360, 720, 180 and 210 labelled choices,
respectively, and every one has a doubled pair. This gives 630 labelled
six-pair choices in three classes. Among the 18 even non-orientable
seven-pair classes on seven knots, exactly three have every holding pair
single. Each has 2,520 labelled choices. The complete E class table contains
209 classes, of which 144 have seven knots and seven pairs.

## Completeness

Each four-knot subset has three cyclic orders up to rotation and reversal,
corresponding to the three assignments of the values' two holder pairs.
Each cycle contributes one binary column marking its four cross pairs.
For each size the search divides the sorted cycle indices into two fixed
lengths and matches halves with the same binary sum. The order condition
selects the unique split of each set of indices. The whole set has binary
sum zero, and rank one less than its size exactly when the whole set is its
only nonempty zero sum. Every cycle takes fresh values, so strictness holds
in the constructed representatives.

Two equal cycles by themselves form a minimal choice with even sign and
balanced orientation. A larger choice containing them has a proper
commuting subchoice. Thus the repeated-cycle case adds exactly three
labelled choices on four knots, all in one class, and E excludes those
three by definition. A single failing pair is never commuting. Coverage
two gives exactly twice as many cross pairs as failing pairs, so the
bound on distinct pairs of knots makes seven failing pairs exhaustive
at six knots. The same search also rejects choices using fewer knots than
the row declares.

## Separation and the coverage check

At coverage two the matching of occurrences is fixed. At each knot,
separation uses the components of its local cycle relation. Both occurrences
of a cross pair use the same component at each endpoint. Each resulting
cross pair therefore corresponds to exactly one original cross pair. Keep
the original reference direction on its copy and every reversal condition
and sign summand is preserved. The executable check used each way to
assign the names at every split, totaling 407 assignments for the 209
classes. Two-colourability changes in 57 classes, representing 177,195
labelled choices. Three of these classes are even non-orientable
seven-knot, seven-pair choices, representing 5,040 labelled choices.

The higher-coverage check is an additional test through seven failing pairs
at every size from four through seven knots. It yields 777,430 labelled
choices with higher coverage. Among its 15,580 labelled choices through
six failing pairs, every even choice is orientable. The 3,510 even
non-orientable higher-coverage choices all have six knots, seven failing
pairs and a maximum coverage of four. Every one has a doubled pair.

The cutoff on knots is sufficient for an arbitrary even-covered minimal
choice through six failing pairs. Pair the occurrences at each cross
pair and separate the knots using those pairings. A connected component
of the failing pairs joined by paired occurrences has even coverage on
the original knot pairs. Minimality forces one component. This is a
closed connected surface in the literature's construction, with the
paired occurrences as its edges and one vertex per separated knot. A
balanced orientation of the paired occurrences would balance the original
choice, so original non-orientability implies separated Euler count at
most one. For \(F\) failing pairs there are \(2F\) paired occurrences,
counted as groups of two, so the number of original knots is at most the
number of separated knots and hence at most \(F+1\). Together with the
finite recount, this extends the six-pair lower bound and the list of three
kinds at six to arbitrary even coverage under these minimality and holder
rules. Higher-coverage choices past seven failing pairs were outside the
recount.

The additional test includes a balanced minimal even choice on five knots
and five failing pairs with one cross pair covered four times. Its three
ways of pairing occurrences give separated Euler counts and orientability
\((0,\mathrm{no})\), \((0,\mathrm{yes})\) and \((2,\mathrm{yes})\).
Those are properties of the paired structures. The original choice has
a balanced orientation on all occurrences.

## Replay

From the repository root, run one command at a time. The native enumeration
took 1.52 seconds and used 40,384 KiB peak resident memory. The independent
class checks and archival comparison took 1.05 seconds and used 15,272 KiB.

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
referee=research/EVEN-ORIENT-20261127-001/referee-R1
c++ -std=c++20 -O3 -Wall -Wextra -Werror -pedantic "$referee/abstract_check.cpp" -o "$referee/abstract_check_native"
"$referee/abstract_check_native" > "$referee/abstract_check_raw.jsonl"
.venv/bin/python -B "$referee/abstract_check.py" "$referee/abstract_check_raw.jsonl" "$referee/abstract_counts.json"
```
