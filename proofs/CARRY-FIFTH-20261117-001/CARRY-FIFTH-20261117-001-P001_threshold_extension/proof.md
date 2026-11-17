# What four distinctions remember when a fifth joins

With a common meaning for the two values, the two original knots can identify a reference for outward growth. In one construction a single distinction is outer in both knots. The mirror construction marks the opposite end the same way. Both allow exactly the same eight states. Those states alone identify the ends as a pair. If each distinction's two value names can be swapped independently, neither the states nor the two constituent knots select a single old distinction. Once a successful fifth distinction joins, one old distinction belongs to all three knots. That mark survives every allowed renaming.

## What the test supplies

Write T₄ for the eight binary words that change value at most once in the displayed order `abcd`. They are `0000`, `0001`, `0011`, `0111` and their complements. The five-distinction target T₅ consists of the ten words obeying the same rule in a proposed order. The letters serve only to show witnesses. The test declares the fifth distinction fresh and supplies no position in the order. Its primary input is the joint set of four-distinction states. A second reading also retains the unordered constituent knots as local allowed-state relations. Neither reading receives a formation history.

A permitted step conjoins one ternary knot on two distinct old distinctions and the fresh one, with no hidden variables. The knot must pass K1–K3. Its allowed states are nonempty, exclude at least one triple, and allow all four outcomes on each pair. Write `B(x,y,z)` for the knot that excludes `010` and `101` in this order. In words, if the two outer values agree, the middle one must agree with them. The old relation is the threshold example in [DISTANCE-ORDER, statement 5](../../DISTANCE-ORDER-20261117-001A/DISTANCE-ORDER-20261117-001A-P001_betweenness/proof.md).

## What the joint states determine

In a common reading of the values, two positions `s` places apart disagree in `2s` old states. There are two states changing at each gap between them. The pair `ad` alone disagrees six times. Reversing `abcd` to `dcba` preserves the eight states and exchanges the two ends. It also exchanges the two interior distinctions. An individual choice based entirely on the joint states would have to be fixed by this reversal. No old distinction is fixed.

If the fifth distinction must go beyond `d`, its unique knot is `B(a,d,e)`. On each nonconstant old state, `a` differs from `d` and the new value must equal `d`. On the two constant states either new value is permitted. This yields exactly the ten target words. An attempted carry from `b` in `B(b,d,e)` allows twelve states, and a carry from `c` allows fourteen. For example, the latter admits `00110`, with two changes. Reversal gives the equally valid extension beyond `a`, using `B(d,a,e)`.

| Placement of the fifth distinction | Single knot | Distinct placements |
| --- | --- | ---: |
| Beyond either end | `B(d,a,e)` or `B(a,d,e)` | 2 |
| In an interior gap | `B(a,e,b)`, `B(b,e,c)` or `B(c,e,d)` | 3 |

Each of these choices yields the full target in its displayed order. The middle gap is invariant under reversal, so inserting the fifth between `b` and `c` is a deterministic way to preserve order using only the old states and a common value convention. It inserts into the order without designating an old end. For outward growth the two alternatives are distinct as allowed-state sets on fixed distinctions. For example `00011` is allowed on extending past `d`, while `00010` is allowed on extending past `a`. Their intersection has four states. Pool their allowed states in one relation and all sixteen combinations of an old state with a free fifth value survive.

## What changes when each distinction can swap its two value names

The map `(a,b,c,d) ↦ (1−d,a,b,c)` preserves all eight states. On a nonconstant word, the new first bit agrees with the old first bit. On a constant word it introduces just one change. This bijection cycles through all four distinctions, so the displayed pair of ends moves. All four pairs `ab`, `bc`, `cd` and `da` can serve as ends in some reading. Even after specifying `d` and preserving its value, `(a,b,c,d) ↦ (1−c,1−b,1−a,d)` preserves the states and exchanges its two possible partners `a` and `c`.

| Renamings allowed on the old relation | Symmetries | Old distinctions exchangeable under them |
| --- | ---: | --- |
| Distinction names only | 2 | `{a,d}`, `{b,c}` |
| Distinction names and a simultaneous value swap | 4 | `{a,d}`, `{b,c}` |
| Distinction names and independent value swaps | 16 | `{a,b,c,d}` |

The classical rank-two alternating arrangement has this same family of sign patterns. The local question here is which distinction the allowed states or the constituent knots select under each kind of renaming. The argument uses the eight words directly. [Kemper and Lawrence, §3](https://arxiv.org/pdf/1610.05039)

## Why the single-knot list is exhaustive

The projection of T₄ onto any two old distinctions contains all four pair values. Consequently the extended relation projects onto exactly the added knot on its three variables. If the extension is a copy of T₅, even after independent value swaps, it is closed under simultaneous complementation. Thus the added knot and its forbidden triples are closed under complementation too.

K1 requires a forbidden triple. K2 prevents two forbidden triples from differing in exactly one position. Among three bits, two distinct complementary pairs always contain two triples differing in exactly one position. Hence the knot forbids exactly one complementary pair. For old positions `s` places apart, each equal pair value occurs in `4 − s` old states and each unequal pair value occurs in `s`. Forbidding a complementary pair of triples therefore removes either `2(4 − s)` or `2s` of the sixteen old-state/fresh-bit combinations. The ten-state target requires removing six. This leaves adjacent old positions with equal forbidden values, or the two ends with unequal forbidden values.

Each of those four old pairs admits two choices for which fresh value is forbidden on one old pattern. For an adjacent pair, one choice inserts the fresh distinction between the two and the other reverses just its value. For the old ends, the two choices extend beyond opposite ends. All eight pass when independent flips are allowed. With common values the old disagreement counts determine its reading up to reversal, so every possible place for the new distinction is one of the five in the table. This proves the count independently of the enumeration.

The checker tried all 256 ternary truth relations. Exactly 34 passed K1–K3, giving 204 attachments to the six old pairs. All project back to the eight old states. Of the 32 attachments with ten joint states, only five agree exactly with the common-value target in any order, and eight agree in some independently recoded order. A ten-state counterexample is the knot on `abe` forbidding `000` and `110`. It admits `00001` and excludes its complement `11110`. Every recoding of a threshold relation contains the complement of each allowed word.

## What survives when the constituent knots are still present

This additional control was specified after the first census. It retains each old knot as a relation and erases the order in which the knots were made. Consider these two presentations of the same eight old states.

| Unordered old knots | Distinction outer in both knots | Other end |
| --- | --- | --- |
| `B(a,b,c)` and `B(a,c,d)` | `a` | `d` |
| `B(d,c,b)` and `B(d,b,a)` | `d` | `a` |

In the first row, `a` and `c` occur in both knots. Only `a` is outer in both. The outer roles are readable from the two local state sets with common binary values. Under that convention, every distinction has a different combination of incidence count and middle/outer role. Thus the first row singles out `a` and the second singles out `d`, without the reader knowing how either pair of knots was formed. Reusing this distinguished end as the reference in `B(reference,other end,new)` is one history-free outward-growth rule on these presentations. Extending at the other end still preserves the order.

These are all the two-knot presentations on the four visible distinctions. A ternary constraint containing every old threshold in projection may exclude only the two non-threshold patterns on that ordered triple. On four bits, each excluded triple removes two words. To exclude all eight non-threshold words with two knots, both must therefore exclude both patterns and their excluded sets must be disjoint. Among the four resulting betweenness knots, disjointness holds for precisely the two pairs in the table. The independent computation checked all 136 individual knots and all 9,180 unordered pairs. Zero singletons and these two pairs give the eight target states.

Under independent value swaps, even a retained presentation fixes no single old distinction. In the first row, `(a,b,c,d) ↦ (c,b,a,1−d)` exchanges `a` and `c` while preserving each of its two knots. Also `(a,b,c,d) ↦ (a,1−d,1−c,1−b)` exchanges the two knots and the two singly occurring distinctions. The two possible pairs of exchangeable distinctions are `{a,c}` and `{b,d}`. The second presentation has the same two pairs, with the roles of singly and doubly occurring distinctions interchanged. The checker found eight symmetries of each unordered presentation under the independent-value convention. Recovering the reference therefore requires knowing which knots are present and being able to compare the values across distinctions.

## What the fifth distinction makes visible

Before the fifth joins, the two old knots share two distinctions. After any successful step, exactly one distinction belongs to all three knots. This is a property of the finished, unordered family. It survives forgetting which distinction arrived last, the order of the three knots, every distinction name and all binary value names.

To see this for the first presentation, the old shared pair is `{a,c}`. Every successful attachment in the exhaustive list uses one of the old pairs `ab`, `bc`, `cd`, `da`. Each meets `{a,c}` in exactly one member. For the mirror presentation the shared pair is `{b,d}`, and the same calculation applies. This covers all sixteen combinations of a two-knot presentation and a successful attachment under independent value swaps.

The marked distinction can be a reference for further outward growth, subject to its position in the order. In the first presentation, both choices of outward extension use the three places `a,d,e`, so in both finished families only `a` belongs to all three knots. If the resulting order is `abcde`, then `a` is still an end. If it is `eabcd`, then `a` is interior. Across the two presentations and five common-value placements, the common distinction is an end in four cases and interior in six. Membership in all three knots cannot by itself certify which distinction will serve as an end in a subsequent step. The same example also distinguishes a mark produced by a step from a choice forced before the step.

## Evidence and reproduction

The finite obstruction concerns four distinctions, one fresh distinction and one added ternary knot. The companion growth study treats arbitrary length with a common reading of the values. Its rule can use a choice of end. The test here asks for a single reference recoverable from the older structure and checks how the answer changes when the constituents remain visible. [Program growth study](../../../research/KNOT-ORDER-20261117-001/knot_order.md)

The enumeration directly checks equality of sets of words. The independent argument above uses the forbidden patterns and explicit symmetries. The symbolic audit and the checker had separate authors within this task. Replaying the checker from another working directory and under another hash seed gave identical results. The controls retaining the old knots and examining the family after the fifth joins were added after the primary census. The command-line advisor suggested separating recoding symmetry from recovery of a reference and using a count-matched negative control. Its client printed a model-recognition warning, so the named advisor model could not be verified. Its suggestions have no proof authority.

Run from the repository root. The first command reproduces the complete [finite certificate](result.json). The second checks the added knot after forgetting the old interior distinctions in the actual outward extension.

```sh
python3 -B proofs/CARRY-FIFTH-20261117-001/CARRY-FIFTH-20261117-001-P001_threshold_extension/check.py
PYTHONPATH=tools python3 -B -m knotlab check --cnf 'a ~b c; ~a b ~c; a ~c d; ~a c ~d; a ~d e; ~a d ~e' --loops a d --contact e --witnesses b c --json
```
