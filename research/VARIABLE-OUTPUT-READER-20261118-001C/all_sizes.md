# Can bond distances tell which triples may join at every size?

**The full table determines every permitted triple at width twenty. The answer for every finite width remains open.** The proposed distance-four parity bit passes its first new width, then fails at every width from 27 onward. The failures point to a smaller part of the table that still distinguishes the shared neighbor. [Proof and scope](../../proofs/VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/proof.md)

## What the distances show at nineteen

The same renaming makes the three candidate rows agree on all 51 entries in the two earlier examples. Each marked distinction and its closest partners identify its parent junction on these examples. Two unmarked distinctions each have the same group of five, consisting of themselves and their four closest partners. That group meets two of the candidate's parents in the legal arrangement and all three in the forbidden one. On the legal side the three pairs of parents have three different witnesses. On the forbidden side the five-distinction junction witnesses all three pairs. Four unmarked pairs move into distance four and three move out, accounting for the totals of 32 and 33. [Worked example](../../proofs/VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/surroundings.json)

## How far the count works

| Width | Observation | Outcome |
| --- | --- | --- |
| 20, all 19,414 arrangements | Three marked rows | 15 forbidden choices match legal ones |
| 20, same census | Three marked rows and global distance-four parity | All 22,131,960 candidate triples classified correctly, including 6,358 legal choices |
| 27, two reachable histories | Three marked rows and global distance-four parity | All 75 marked entries agree, with even totals of 46 and 52. Only one triple is legal |
| 28, two reachable histories | Three marked rows and exact global distance-four count | All 78 entries agree and both totals are 50. Only one triple is legal |

At twenty, all 1,420,288 distance-preserving permutations preserve actual triple eligibility. The larger examples have different full tables. At width 28 they even have different totals at distance two, 21 and 18. Attaching the same new junction to corresponding loose tips propagates the failure of global parity to every width from 27 on. We also get failures of the exact count at 28 and every width from 30 on. [Full-table census](../../proofs/VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/full.json) · [Larger witnesses](../../proofs/VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/witness.json) · [Propagation](../../proofs/VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/proof.md#failure-of-global-distance-four-parity-at-every-width-from-27)

## A rule to try at any size

Use the full table to remove branches attached through one distinction. Across such a distinction \(t\), the distances obey \(D(x,y)=D(x,t)+D(t,y)-1\). This gives a test for which distinctions stay together. Then use the candidate's three rows and the distance-four parity **only in the part that contains it**, keeping the boundary distinctions.

The table found every actual single-distinction separation at widths 19 and 20. In the combined census, all 8,739 legal triples survived. The rule using the retained rows and parity separated them from every forbidden choice. On the two larger witness pairs this operation removes the added branches and restores the original counts of 32 and 33. These same sixteen distinctions and their counts survive every further unary attachment in the constructed families. [Complete local comparison](../../proofs/VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/core.json)

Two facts would prove the rule at any size. First, show that every separation reported by the distance equation is a genuine break in the physical meetings. Second, within a retained part, show that changing triple eligibility while preserving the three marked rows must flip the local parity. The latter is where the distinction between three separate pair witnesses and one common neighbor must survive. One class of possible full-table counterexamples can already be ruled out. If two different joins to the same starting arrangement use the same fresh distinctions and produce identical allowed states on the same names, neither result has a legal next triple. [Precise proof obligations](../../proofs/VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/proof.md#a-size-independent-candidate-from-the-complete-table) · [Common-prefix theorem](../../proofs/VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/complementary.md)

## Prior work in the program

The two searches below passed at the prespecified comparison's freeze. A same-day record entered the index during the calculation. This closing addendum records its different scope and preserves the original protocol.

`python3 -B scripts/track.py objects "variable number fresh outputs distance four parity triple legality table common neighbor" --until 2026-11-19 --exclude VARIABLE-OUTPUT-READER-20261118-001C --limit 3`

`python3 -B scripts/track.py objects "three marked rows scalar parity same permitted three parent joins" --until 2026-11-19 --exclude VARIABLE-OUTPUT-READER-20261118-001C --limit 3`

The [frozen protocol](preregistration.md) records the overlap checks for `SIGNED-KNOT-OVERLAP-20261114-001`, `CHEAP-COUNT-20261112-001`, `BOND-BALLS-20261111-001`, `TERNARY-REPORT-JOINS-20261115-001`, `ROW-ARRANGE-20261118-001` and `TWO-RELAY-PADDING-20261115-001`. The later `FRESH-COUNT-20261118-001` concerns choosing how many fresh distinctions to introduce under its own growth policy. This comparison considers both counts and asks which triples of old distinctions are eligible. [Fresh-count study](../FRESH-COUNT-20261118-001/fresh_count.md)
