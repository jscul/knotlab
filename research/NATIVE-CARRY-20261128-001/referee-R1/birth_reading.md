# What the closed pattern and the birth rule select

The 1,177 census starts where some birth choice closes odd give the following counts. Each start gets one vote. A minimum is taken over **all nonempty commuting whole-choice sets**, including the even ones. An odd whole-choice set can have only even minima.

| All cells of the entire closure | Some odd minimal set | Only even minima inside odd sets | No odd whole-choice set | Total |
| --- | ---: | ---: | ---: | ---: |
| Commute and close odd | 39 | 14 | 0 | 53 |
| Do not commute or close even | 113 | 25 | 986 | 1,124 |
| Total | 152 | 39 | 986 | 1,177 |

All 191 positive closures have at least one odd whole-choice set whose cells are all eligible at birth. At 138 a proper set of knots must be chosen to obtain such a witness. At the remaining 986, no choice of a set of knots alone gives an odd sign under the all-internal-cells declaration. The archived 1,025 is the exact complement for **odd minimal** sets alone. Fourteen of these 1,025 already close odd under the rule that takes every eligible pair in the entire closure.

A four-knot start at census index 643 closes in round one. Its final five knots hold `{0,1,2,7}`, `{0,3,4,5,6,8}`, `{1,3,4,9}`, `{2,5,6,10}` and `{7,8,9,10}`. All 18 candidate cells are eligible at birth. All 18 together commute, with seven interleavings in the listed knot order. Its only minimal sets of knot indices are `{0,1,2,3}` and `{1,2,3,4}`. Each has four cells, two interleavings and even sign. This counterexample uses the whole closure and no choice of a proper set of knots. [Counts and certificate](birth.json)

## Later births

For a set of knots S, write W(S) for every finished candidate pair with its four holders in S. Write E(S) for those pairs already eligible at the later distinction's birth. The commutation-at-birth study's plural “whole choices” ranges over all selections among finished candidates. Its natural rule takes every eligible pair in the entire closure. This study tests the single choice W(S) for each S.

| Closing round | Closures | Finished candidates | Birth candidates | Any odd birth choice | Full natural choice commutes (odd) | Odd minimal sets, eligible / all | All odd W(S), eligible / all |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1,713 | 39,126 | 39,126 | 1,091 | 145 (53) | 180 / 180 | 512 / 512 |
| 2 | 105 | 5,581 | 5,086 | 85 | 0 (0) | 14 / 14 | 57 / 65 |
| 3 | 1 | 110 | 97 | 1 | 0 (0) | 0 / 0 | 0 / 0 |

Each candidate occurrence and each knot subset receives one vote within its own closure. The candidate lists differ at all 106 later closures. The 508 excluded candidate occurrences had two loose distinctions when decided. All 14 odd minima at the 11 qualifying later closures consist entirely of birth-eligible cells. Eight nonminimal odd sets contain birth-forbidden cells. Taking E(S) in place of W(S) gives 66 odd knot subsets in round two, including the 57 whose original whole choice was eligible. These alternate counts are a separate reading. [All later choices, holdings and decision rounds](birth_later.jsonl)

In the two samples, 15 of 16 and 48 of 48 recorded odd minima pass the birth rule. A six-knot start, draw 203 of the first sample, closes on nine knots in round two. The set `{0,4,6,7,8}` needs `(10,15)` and `(11,14)`. Each pair was decided in round zero while both distinctions were loose, one at knot 0 and the other at knot 4. Two other odd minima in that same closure pass the rule. Across the three grown populations 257 of the 258 reported odd minima are birth choices. All 770 odd minima in the separate census of finished types have finished-pattern status only. The 149 positive types have four knots at one type, five at two, six at 13 and seven at 133. [Sample and type counts](birth_other.json)

An internally commuting W(S) extends to a commuting finished choice on the entire closure by letting every other pair commute. All four holders of every selected cell lie in S, so every pair involving an outside knot has zero coverage. The outside knots can be ordered after S without changing the sign. This extension is a birth choice exactly when all its failing pairs lie in E(S). At earlier stages each pair of then-existing knot checks already has the same commutation count as in the closure, since neither knot acquires new distinctions. This constructs an admissible choice for that history. A growth rule selecting S or supplying those decisions uniformly across starts would be a separate result.

## Separated readers

A commuting choice with odd product is the definition used in the whole-choice study. A split into separated readers additionally requires that all failing pairs lie within readers, and that a reader supply at most one distinction in any knot. For four mutually meeting knots the three cells are disjoint pairs of distinctions, hence three readers. For two knots A and B meeting the same three others, let their shared distinctions with the others be `a_i` and `b_i`. The six failing pairs are `(a_i,b_j)` with `i != j`. They join all six distinctions in one group. Assigning this group to one reader would ask that reader for three distinctions at A.

Among the 194 census odd minima, 153 split into three readers and 41 have no split. Of the 152 positive closures, 119 have a splitting minimum and 33 have only nonsplitting minima. At 23 of those 33 another birth choice splits, while at ten no birth choice splits. The latter comparison uses the already refereed separated-reader existence verdicts in the same start order. “Odd product of commuting checks” gives the conclusion common to both kinds. [Reader split definition](../../READER-SPLIT-20261127-001/README.md) · [Refereed split counts](../../READER-SPLIT-20261127-001/referee-R1/report.md)

In fact a commuting W(S) with a reader split always gives the three-reader game. Consider the distinctions whose **two** holders are in S. Each group connected by failing pairs must belong to one reader. Within a group every two distinctions must have disjoint holders for the reader to supply at most one value per knot. Since W(S) takes every such pair, all pairs inside the group fail. If a group has at least three distinctions, every distinction outside it must meet each of three pairwise disjoint holder pairs to avoid joining that group. Its two holders cannot do this. That leaves just one group with pairwise disjoint holders. A pair of knots holding two different distinctions then has exactly one cross pair occurrence, which rules out commutation.

Every nontrivial group therefore has exactly two distinctions. Fix one such pair with holders `{a,b}` and `{c,d}`. Every other internal distinction meets both, so its holders are among the same four knots. The three possible ways to divide these four into pairs give at most one failing pair each. Duplicate distinctions at an active meeting would put two co-held values in one reader. At any given knot pair the coverage is the sum of the indicators of the other two divisions. The indicators must therefore all agree, and the nonempty choice forces all three. These are precisely the three cells of four mutually meeting knots. Any extra knot in S is unused. On the census-start closures the direct split test examined all 12,419 nonempty commuting W(S). Exactly 166 split, on 119 closures, all with the six distinctions of those four knots. Of these, 153 are minimal sets of knots. [Full census test](birth.json)

## Reproduction

`birth.py` uses the archived start roster and the original growth wrapper to rebuild the 1,819 known positive-round closure histories. It makes all pair decisions from the holdings available at that stage, compares every census row to the earlier birth study, and checks all knot subsets without pruning. `birth_other.py` rechecks each reported odd minimum in the other populations for sign, minimality, birth eligibility and reader split. The census types have no birth history and allow all finished candidates.

```sh
ulimit -v 1500000
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
r=research/NATIVE-CARRY-20261128-001/referee-R1
.venv/bin/python -B "$r/birth.py"
.venv/bin/python -B "$r/birth_other.py"
```
