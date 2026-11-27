# Exact costs for a pair and for a family sum

Consider a finite connected start with at least two families. Each distinction has one or two distinct holders, every knot has the even law, and a round uses the funded ordinary rule. Let \(d(A,B)\) count the fewest shared distinctions on a route between a live start knot of family \(A\) and one of family \(B\). At reached round \(t\), put \(D_t(A,B)=d(A,B)+2+2t\).

**The least change flipping exactly \(A\) and \(B\) costs the least sum of \(D_t\) over chains of families from \(A\) to \(B\).** A family that occurs between the two ends can be entered and left through different loose distinctions. Its fact then keeps its value.

**The least change flipping the parity of a proper nonempty set \(U\) of families costs \(\min_{A\in U,\ B\notin U}D_t(A,B)\).** The same minimum results when each \(D_t\) is replaced by the exact pair cost. At any scale \(k\), the dimension of the kept family sums is the number of single-linkage clusters at \(D_t\le k\), less one. This conclusion concerns which *sums* are kept at a scale. Selecting them as the places of further knots is another decision.

## Derivation

Each join at the start takes from members of one family by the common-witness rule. In subsequent rounds two eligible parents with a common witness are births with a common parent from the preceding round, so the two descend from one family. Single-parent births preserve this property. Every loose distinction is used once. In a connected presentation the only nonempty parity equation on loose distinctions alone is their total parity. In a sum of knot laws that cancels all shared distinctions, their two holders must have equal coefficients, and connectedness makes all coefficients equal. With at least two families present, each birth therefore has a fresh distinction, since it takes loose distinctions from only one family. Each live holder has at least one live child. Summing one family's birth laws equates its previous and current loose parities. This also follows from the earlier family argument. [Previous derivation](../../THIRD-LAYER-20261126-001/referee-R1/argument.md)

Among *actual knots*, a new round preserves the shortest holder-step count between any two old knots. Each passage through a new birth enters from one parent and leaves through another. Its two parents already have a common witness, giving an old route of length two. Retracing to the same parent can be removed. Births of the same round share no distinction with one another. Every new route between old knots thus gives an old route no longer than it, and all old routes are retained. A route from live family \(A\) to live family \(B\) in the new round takes a step from its first birth to a parent of \(A\) and a final step from a parent of \(B\). Both steps can be added to a shortest route from the preceding round because each live holder contributes to a live birth. By induction the least number of such holder steps at round \(t\) is \(d(A,B)+2t\).

For counting a change, give each family a separate bookkeeping holder on all its current loose distinctions. The family fact flips exactly when the change reaches its bookkeeping holder an odd number of times. All actual holders have even incidence. A change that flips just \(A\) and \(B\) contains a route between those two bookkeeping holders, and each simple route between them is itself a legal change of exactly those two facts. Break a route wherever it reaches a bookkeeping holder. Each leg between consecutive families costs at least \(D_t\), including two loose distinctions. Conversely concatenate least legs along a chain of families. Removing repeated passages gives a route of at most the concatenated length. This proves the pair formula. The direct prediction holds for every pair at that round exactly when \(d(A,B)-d(A,C)-d(C,B)\le 2+2t\) for all distinct families \(A,B,C\).

For a sum, use just two bookkeeping holders, on the loose distinctions in \(U\) and its complement. An allowed change flips the sum exactly when both of these holders have odd incidence. It contains a route between the two. A least such route uses one loose distinction on each side and has cost equal to the least crossing \(D_t\). This argument includes changes flipping four or more families. Every chain crossing the cut uses a crossing leg, so it also gives the same minimum over the exact pair costs. Equivalently, two or more disjoint open trails cannot undercut the cheapest crossing trail. The previous study already proved the increase of two per funded round for every nonconstant family sum. [Earlier result](../../THIRD-LAYER-20261126-001/referee-R1/argument.md)

The pair routes realize each two-family flip, hence every even family signature by addition. The total parity is the sole equation on the family facts. A set's parity survives scale \(k\) exactly when the set contains either both or neither of the two families in each pair with \(D_t\le k\). Its coefficients are constant on the resulting connected classes. One independent coefficient per class, modulo complement, gives the claimed dimension.

## Comparisons with the records

| Check | Result |
| --- | --- |
| Frozen pair costs | 6,839 on 3,489 stages. The direct formula failed for 3 of 1,875 pairs at round zero. All 4,964 positive-round pairs agreed. All 6,839 matched the formula allowing intervening families. The largest exact cost was 17. |
| Frozen family sums and clusters | All 6,871 complementary set pairs in the announced range agreed. The largest set cost was 15. Both frozen scales agreed on all 3,465 stages in that range. A further 3,048 complementary pairs on the 24 frozen stages with eight families also agreed. |
| Changes flipping four or more families | On 228 frozen stages admitting such changes, all 3,080 such family signatures were costed. Of the 9,919 complementary set pairs over all family counts, 4,783 could be flipped by at least one such signature. In those comparisons the best such change cost at least three distinctions more than the cheapest crossing pair. |
| Independent growth and literal controls | 8,601 births matched archived parent lists, input counts, fresh counts and implication flags across 1,866 round logs, including stopping records. Direct enumeration of 234,368 allowed states on 37 stages matched all 122 attainable family signatures and their exact costs, including four signatures with at least four flips. |
| Later and larger cases | 1,888 extra stages on the original starts and 81 on 148 larger starts. The enlarged sample supplied three further round-zero exceptions. All 58 eligible larger sampled starts stalled at round one. The four larger ring constructions reached 23 stages, with up to twelve families. All 4,445 extra pair comparisons and all 16,337 extra set comparisons agreed with the formulas above. |
| Constructed shortcuts | Regrowth from the supplied starting distinctions matched every one of the 20 independent chain-certificate stages, including knot counts, distinction counts, exact pair minima and the concrete minimum change. The nine-knot start costs 10 versus 12 direct at round one. The seventeen-knot start costs 26 versus 28 direct at round five. [Certificate](pair_shortcut.json) |

The study's set-cost judge compares the measured set cost to the minimum of **predicted direct** crossing costs. The independent check compared the two actual minima as well. The archive logs exceptions for pairs and sets, with individual successful values implicit. At the held-out eight-knot start with live families on holders \(\{1,2,3\}\), \(\{4\}\) and \(\{5\}\), the direct and two-leg costs for the latter two families are \(8,6\) at round zero, \(10,10\) at round one and \(12,14\) at round two. Both twelve-knot starts with round-zero exceptions stalled before round one. One funded round increases every direct leg by two distinctions. [Source judge](../tree.py) · [Reconstruction and counts](cost_check.json)

## What the shortest changes retain

For each distinction, the check retained the family parities of **all** tied shortest changes through it. For every family sum it tested whether all these changes preserved it. It compared the resulting actual coefficient masks, modulo complement, to those for every integer threshold, including the trivial full and zero spaces. The table covers positive rounds and the originally announced range of up to six families.

| Starts | No nonconstant sum | Every nonconstant sum | Proper nonzero space equal to a threshold level | Proper nonzero space equal to no threshold level |
| --- | ---: | ---: | ---: | ---: |
| Census sample | 823 | 101 | 4 | 0 |
| Held-out sample | 1,023 | 145 | 32 | 68 |
| Larger archived sample | 147 | 41 | 12 | 16 |
| Built | 0 | 86 | 0 | 0 |
| Total | 1,993 | 373 | 48 | 84 |

The 16 additional positive stages with eight families all retained the full space. In round one of the held-out six-knot sample with one family on each of holders 0, 1, 4 and 5, the shortest changes flip only the first and third, or the first and fourth, together. Only the second family's fact survives, up to complement. The sole proper threshold level keeps the sum of the first and fourth families. Both readings retain one independent bit, with different values on allowed states. [Masks and all threshold levels](cost_check.json)

## Rerun and limits

The script imports only the standard library. It reconstructs the frozen labelled samples with their seeds, takes the specified sample of the archived small-start catalogue, and builds the ring starts from their definitions. The cutoff for the enlarged check was round seven and 512 distinctions. Among 1,037 eligible original and new starts, 619 finished round seven, 397 stalled before funding round one, and 21 crossed the distinction limit. Their subsequent stages and rounds after seven were not run. All-even-signature comparisons to each unrestricted set minimum were run through eight families. Literal enumeration was limited to the documented small stages. No unrestricted census above five knots was run. The script begins with a pilot using the same implementation and bounds, and records timings and memory. [Rerun source](cost_check.py) · [Counts and weighting](cost_check.json)

```sh
.venv/bin/python -B research/SELECTED-KNOTS-20261127-001/referee-R1/cost_check.py
```
