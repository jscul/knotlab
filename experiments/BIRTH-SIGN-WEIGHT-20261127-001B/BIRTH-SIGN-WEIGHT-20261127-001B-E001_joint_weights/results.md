# Joint weights from the current births

One round can give its siblings dependent positive weights. The example counts joint fresh assignments up to renamings of the current round that preserve the founder and its values. This choice of weighting is supplied. It preserves every allowed state. A different question has a negative answer on an archived example. A single first-round weighting cannot reproduce equal division among all completions at both of two stopping rounds.

## Why the previous weighting needs its stopping round

The archived ordinary not-all-equal start with census index 23 has rules on 014, 023 and 12356. Digits name distinctions. Its first round adds rules on 457 and 689. Its second adds rules on (7,8,10) and (9,11,12). On the archived assignment of the other distinctions, the table on old distinctions 4 and 6 has entries (1/12, 1/15, 1/27, 1/27) when each old state divides its unit of weight over all final completions. Its determinant is 1/1620. Dividing at each round gives (1/9, 1/9, 1/18, 1/18) and determinant zero. There are 68 allowed starting states, so normalizing the initial weighting multiplies each entry by 1/68. No listed rule holds these two distinctions together. The earlier referees explain why that screen and the whole structure's knot test must be kept distinct. [Original counting](../../../research/FACTOR-WEIGHTS-20261126-001/countings.py) · [Archived witness](../../../research/FACTOR-WEIGHTS-20261126-001/referee-R1/part_a_full.json) · [Referee's distinction](../../../research/FACTOR-WEIGHTS-20261126-001/referee-R2/report.md)

Fix the allowed old state 1010000, in order 0 through 6. The first birth forces distinction 7 to 1. The second birth permits three fresh patterns. At the next round the rule on (7,8,10) gives two choices if 7 and 8 differ, one if they agree. The rule on (9,11,12) always gives three.

| First fresh state on 7,8,9 | Weight when stopping here | Later completions | Weight when stopping one round later, then forgetting |
| --- | ---: | ---: | ---: |
| 101 | 1/3 | 6 | 1/2 |
| 110 | 1/3 | 3 | 1/4 |
| 111 | 1/3 | 3 | 1/4 |

The two distributions differ by total variation 1/6. A single first-round probability for 101 cannot take both values. If the finish is specified, weighting each prefix by its number of descendants does reproduce that finish. This uses exactly the horizon information excluded from the current-round rule. [Exact replay](../../../artifacts/BIRTH-SIGN-WEIGHT-20261127-001B/BIRTH-SIGN-WEIGHT-20261127-001B-E001_joint_weights/results.json)

## A weighting chosen at the birth

One ordinary not-all-equal founder has three distinctions (0,1,2). Its three births hold (0,3,4), (1,5,6) and (2,7,8). In state 001 the first two births both receive 0. Their fresh pair can be 11 (equal) or 01 or 10 (mixed). The third birth receives 1 and can have 00, 01 or 10. In every allowed founder state the two births receiving the same value are identified as an unordered pair.

For a finite extending round, partition the allowed fresh assignments under the renamings that preserve the current colored birth record, its roles and its old values. If there are M classes, give each assignment in class C weight 1/(M × |C|). This rule needs the current old state, the current birth proposals and their allowed completions. A fixed old state then retains its weight under every subsequent **extending** round. We evaluated the current rule on this founder. There is no computational or locality claim about finding the classes in arbitrary large structures.

Here the renamings exchange the two like-paid siblings along with their old distinctions, and may swap the fresh pair at each birth. They preserve the three distinct old identities as a set. For 001 the 27 allowed fresh assignments form six classes with sizes 1, 2, 4, 4, 8 and 8. For the two like-paid siblings the unordered joint patterns equal/equal, one of each, and mixed/mixed have weight 1/3 each. Either order of the mixed pair has weight 1/6. Each sibling's own pattern is equal with weight 1/2.

| Weighting | Equal/equal | Equal/mixed | Mixed/equal | Mixed/mixed | Determinant |
| --- | ---: | ---: | ---: | ---: | ---: |
| One share per joint class | 1/3 | 1/6 | 1/6 | 1/3 | 1/12 |
| Independent draws with those same marginals | 1/4 | 1/4 | 1/4 | 1/4 | 0 |
| One share per named simultaneous completion | 1/9 | 2/9 | 2/9 | 4/9 | 0 |
| Reinforce the class, starting with its number of named representatives | 1/6 | 1/6 | 1/6 | 1/2 | 1/18 |

Fixing every old distinction pointwise removes the exchange of the two siblings. Counting the resulting classes gives the second row. The last row starts with one equal token and two mixed tokens. Draw a class in proportion to its tokens, add a token of that class, and draw again. Within either class draw each named fresh assignment uniformly, separately for the two siblings. The result is unchanged by the order used to describe the draws. Each of 11, 01 and 10 has marginal 1/3. This preserves the original single-birth marginals while still coupling the births.

The dependence survives reading the complete fresh pairs. In row and column order 01, 10, 11, eight cells have weight 1/12 and the 11/11 cell has weight 1/3. A minor using 01 and 11 has determinant 1/48. Reading just the first distinction of each pair gives (1/12, 1/6, 1/6, 7/12), also with determinant 1/48. The third child's whole pattern is independent of the others given 001. With equal weight on all six founder states, the **same two fixed children** have equal/mixed table (5/18, 2/9, 2/9, 5/18), with determinant 1/36. All six founder permutations and global reversal of values carry the conditional distributions to their renamed versions. [Exact distributions](../../../artifacts/BIRTH-SIGN-WEIGHT-20261127-001B/BIRTH-SIGN-WEIGHT-20261127-001B-E001_joint_weights/results.json)

The first row has an elementary classical realization. Choose an equal-pattern probability from 0, 1/2 and 1 with weights 1/6, 2/3 and 1/6, respectively, then draw independently conditional on it. The continuum version takes that probability uniformly on [0,1]. For m interchangeable siblings with two local types and the full sibling permutation group, each count k has weight 1/(m+1). A specified ordered assignment with k equal patterns has weight k!(m−k)!/(m+1)!, also the integral of p^k(1−p)^(m−k) from 0 to 1. Summing over one more sibling gives the same distribution on the preceding siblings. This identifies this special case with the literature's Pólya scheme. The token or common-probability description is a realization of the proposed weighting. The existing growth law does not choose that weighting. [Blackwell and MacQueen](https://people.eecs.berkeley.edu/~jordan/sail/readings/archive/blackwell-macqueen.pdf)

## Which readers are joined

At the fixed preparation 001, the positive support is the product of the three children's sets of three patterns. Any constraining projection across separate children retains a constrained proper part. Exactly zero of the 466 scopes of arity at least three pass K1–K3 on the 27 positive states.

Allowing all six founder words gives 162 positive states and 11 knots. Two meet both of the first two children's fresh pairs. One holds (2,3,4,5,6) and allows 30 of 32 patterns. If each fresh pair equals 11 then the two old inputs must both be 0, forcing the third old distinction to 1. Complementing every value gives the other forbidden pattern. Forgetting any of its five distinctions makes the rest free. The other knot holds (3,4,5,6,7,8) and allows 62 of 64 patterns. The procedure screened all 466 eligible scopes on each support and compared both of these projections and the founder projection with the canonical checker, using the original four rules and declaring every omitted distinction a witness. The conditioned and unrestricted separation claims refer to different supports. [Checker commands and verdicts](../../../artifacts/BIRTH-SIGN-WEIGHT-20261127-001B/BIRTH-SIGN-WEIGHT-20261127-001B-E001_joint_weights/results.json)

## What can be read

Ordinary binary functions of each child's own fresh values have a maximum CHSH score of 2. The code enumerates all functions of the two pattern classes and all functions of the three allowed fresh words, including constants and repeated settings. A single positive distribution gives every setting its value on the same sampled state.

Supply a coherent pure preparation with amplitudes equal to the positive square roots of the joint weights. In the equal/mixed basis the two-child amplitude matrix has diagonal entries √(1/3), off-diagonal entries √(1/6) and determinant 1/6. Its correlations XX, YY and ZZ are 1, −1/3 and 1/3, and the correlations on differing axes vanish. The optimum with arbitrary local two-valued reads is **2√10/3** (about 2.1082). The first reader uses X and Z. The second uses (3X+Z)/√10 and (3X−Z)/√10. Their four correlations attain the optimum. The squared two largest singular values of the correlation matrix are 1 and 1/9, giving the same upper bound. With independent classes and the same marginals, the coherent preparation is a product and the optimum is 2. [Horodecki, Horodecki and Horodecki](https://doi.org/10.1016/0375-9601(95)00214-N)

The calculation also checks each child's full pair of fresh distinctions. The equal pattern is the state |11⟩ and the mixed pattern is (|01⟩+|10⟩)/√2. Those two states are orthonormal. Their local embeddings reproduce the full coherent amplitudes exactly under each weighting, and the same reads extended by the identity on the unoccupied subspace attain the same score. The third child's amplitudes factor and tracing it out has no effect. Choosing a common phase between different allowed states and granting each reader those local operations are additional assumptions. The signed-change comparison is recorded separately in the epic review. [Exact symbolic checks](../../../artifacts/BIRTH-SIGN-WEIGHT-20261127-001B/BIRTH-SIGN-WEIGHT-20261127-001B-E001_joint_weights/results.json)

## Reproduction

From the repository root, run the following command twice, first with `--pilot` after the script path and then as printed.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 prlimit --as=1073741824 -- .venv/bin/python -B experiments/BIRTH-SIGN-WEIGHT-20261127-001B/BIRTH-SIGN-WEIGHT-20261127-001B-E001_joint_weights/joint_weights.py
```

The timed pilot took 0.33 seconds and 75,976 KiB. It exercised the old-state, orbit, five-place canonical and two-class coherent calculations. The full set was estimated below ten seconds from those four phases. It took 0.75 seconds and 77,120 KiB in the main process, under the 1 GiB cap inherited by each checker. The predictions and the prior witness were known at freeze. This is an exact enumeration of the declared examples in an exploratory study. [Pilot](../../../artifacts/BIRTH-SIGN-WEIGHT-20261127-001B/BIRTH-SIGN-WEIGHT-20261127-001B-E001_joint_weights/pilot.json) · [Script](joint_weights.py) · [Contract](contract.json)
