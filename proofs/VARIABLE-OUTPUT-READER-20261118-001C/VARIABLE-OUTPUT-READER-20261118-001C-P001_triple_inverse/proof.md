# Reading a three-parent choice at variable fresh counts

**Standard statement.** Begin with three binary coordinates subject to even parity. Each new parity equation takes one old loose coordinate from each of one to three eligible equations and introduces two or three fresh coordinates. Give each pair of coordinates the least size minus one of an inclusion-minimal nonempty dual support through both, or infinity if none exists. Does every weight-preserving bijection of current coordinates preserve the eligible unordered triples for the next equation?

**Nearest known result.** The fixed-three-output theorem gives a uniform inverse under its stronger source law. With variable output counts, width eighteen already admits identical allowed states with different singleton and two-input permissions. At width nineteen, the three rows of a proposed triple together with the parity of the total number of distance-four pairs were sufficient for every triple. The present results test that feature at twenty, explain its failure at all sufficiently large widths and isolate a local alternative. External novelty is unassessed. [Fixed-three result](../../../research/BOND-NEXT-JOIN-20261117-001/next_joins.md) · [Width eighteen](../../../research/VARIABLE-OUTPUT-READER-20261118-001A/first_three.md) · [Width nineteen](../../../research/VARIABLE-OUTPUT-READER-20261118-001B/triples.md)

## Incidence and observations

A distinction is loose while it belongs to exactly one current junction. Two ordinary junctions are neighbors when they share a distinction. The three-parent law requires three loose inputs from three different parents. Each pair of parents must have a common ordinary neighbor. No one neighbor may serve all three. A permitted triple can introduce either allowed fresh count.

For a marked triple \(T\), keep its three mutual distances and the column of distances to all three marks for each other distinction. Forget the names of the exterior columns and consistently forget the names of the three marks. Call this observation the three rows. Write \(C_4\) for the number of unordered pairs in the full table at bond distance four. A full-table counterexample requires a *single* isometry taking a legal marked set to a forbidden marked set. Two different choices in a common unmarked table establish this only when a table symmetry actually exchanges their marks. [Prespecified protocol](../../../research/VARIABLE-OUTPUT-READER-20261118-001C/preregistration.md)

## How the surrounding rows reveal the shared neighbor at nineteen

In the published example the same renaming matches all 51 entries touching the three marks. On **each** side, taking a mark together with its closest partners in the scalar table recovers the support of its physical parent. Two unmarked distinctions, numbered 13 and 14 in the certificate, each have precisely four closest partners, all at distance four. Each of their rows recovers the same five-distinction support \(\{5,6,8,13,14\}\). Directly comparing this visible group with the three recovered parent supports gives the following intersections. Numbers in a row are local certificate names.

| Marked choice | First parent | Second parent | Third parent | Common ordinary neighbors for the three pairs |
| --- | --- | --- | --- | --- |
| Legal | {6} | empty | {8} | {0}, {5}, {3} |
| Forbidden | {5} | {6} | {8} | {0,5}, {5}, {3,5} |

The five-distinction junction is a neighbor of two marked parents on the legal side and all three on the forbidden side. This explains the obstruction without a growth history. The count changes from 32 to 33. Under the three-row matching, four unmarked pairs enter distance four and three leave. In each of those seven changes the shortest five-distinction bond is exactly that junction. One further pair retains distance four because the sum of junction equations 0, 1 and 2 supplies a second five-distinction bond. This reconstruction from closest partners is verified on these two examples. [Incidence, shortest supports and all seven changes](surroundings.json) · [Replay](check_surroundings.py)

## Exhaustive result at twenty

If there are \(a\) two-fresh and \(b\) three-fresh additions, \(2a+3b=17\). The resulting counts include one entry per incidence type up to renaming. The last column counts actual triples of distinctions in one representative of each type, before choosing how many fresh distinctions to add.

| Existing junctions | Two-fresh, three-fresh additions | Reachable arrangements | With a legal triple | Legal triples |
| ---: | ---: | ---: | ---: | ---: |
| 7 | 1, 5 | 1,216 | 49 | 501 |
| 8 | 4, 3 | 10,198 | 869 | 4,182 |
| 9 | 7, 1 | 8,000 | 667 | 1,675 |
| **All** | | **19,414** | **1,585** | **6,358** |

Forward enumeration grows all legal parent sets with both fresh counts, identifying presentations by the ordinary meetings and each parent's remaining loose count. These two data determine the actual incidence up to renaming because each meeting uses precisely one shared distinction and loose distinctions at a parent can be exchanged. Induction from the seed covers all reachable presentations. A separate reverse enumeration begins with candidate ordinary meetings and loose counts and tests all eligible last-junction removals down to the seed. The width-nineteen proof gives the coverage argument for the same family. Both enumerations yield the displayed counts. [Forward checks](check_parity.py) · [Reverse enumeration](check_reverse.py) · [Independent counts and orbits](reverse.json)

All \(19{,}414\binom{20}{3}=22{,}131{,}960\) proposed triples were graded. With 54 entries touching a triple, 15 forbidden triples in nine physical types share a three-row description with a legal one. Appending \(C_4\bmod2\) gives 1,702 legal descriptions and zero forbidden matches. The feature was fixed using width nineteen and the positive catalogue was formed for width twenty. Controls checked the canonical description against all six permutations of the marks on 6,572 candidates, reproduced the width-nineteen obstruction and tested an arbitrary relabeling. [Profiles and controls](parity.json)

The 190 entries in each full table give 19,414 exact unmarked isometry classes. Testing 88,255 generators and their lifts covers 1,420,288 self-isometries. Every isometry preserves the actual legal triples. The reverse calculation uses marked canonical forms and verifies that all 1,732 legal marked orbits are complete. A change in a singleton or two-input menu is a separate question. [Full-table checks](check_full.py) · [Isometry counts](full.json) · [Independent marked check](reverse.json)

## How one attachment changes a bond distance

Consider two binary parity presentations whose coordinates intersect at the single identity \(t\). Suppose no singleton is a parity constraint on either side and all bonds have size at least three, as on the attachments below. Each dual word of the joined presentation decomposes uniquely into a left word plus a right word. The two spans intersect trivially, since any common nonzero word would be supported only at \(t\).

The bonds of the union are exactly the old bonds on either side and the sums of a left and a right bond both containing \(t\). In a minimal mixed word, both summands must contain \(t\), which cancels. Otherwise a nonzero summand supported away from \(t\) is a proper subword. Each summand is minimal on its side. A proper nonzero subword omitting \(t\) fits in the mixed word, and a proper subword containing \(t\) can replace its summand to give a smaller mixed word. Conversely a smaller nonzero word inside the sum of two such bonds would restrict to a proper nonzero subword of one side, or decompose into two words containing \(t\) and each contained in its original bond. The latter must both equal the originals. A word supported on one side belongs to that side's span, so the unmixed bonds survive.

Old pair distances stay fixed. A new mixed bond containing an old pair has size at least one more than its constituent old bond. For \(x\) and \(y\) on opposite sides and different from \(t\), choosing the two shortest qualifying bonds independently gives

\[
D(x,y)=D(x,t)+D(t,y)-1 .
\]

If either contributing distance is infinite, there is no mixed bond through the pair. For finite values the equation explains precisely which entries a branch can change. [Direct check of the decomposition](check_gluing.py)

## Failure of global distance-four parity at every width from 27

Start from the two width-nineteen presentations above. Attach four more junctions on each side, beginning at an unmarked loose distinction. The two attachments have the same distribution of distances to that distinction, so the marked rows still match. They have different internal distance-four counts. At width 27 the full counts split as \(32+8+6=46\) and \(33+13+6=52\), where the last term counts crossing pairs. All 75 entries touching the marks agree and both counts are even. The old triple keeps its legality on each side. The full tables are nonisometric because their counts differ. Each literal history, both 4,096-word duals and the gluing identity were checked. [Explicit width-27 witness](gluing.json)

A second pair at width 28 matches all 78 marked entries and has exactly 50 distance-four pairs on **both** sides. Their full tables differ even as unmarked tables. They have 21 and 18 pairs at distance two. The two counterexamples were independently reconstructed from their allowed rows and minimal-support rank tests, with 32,768 allowed rows on each width-27 side and 65,536 on each width-28 side. No minimality in width is claimed. [Both histories, table comparisons and bijections](witness.json) · [Independent replay](check_witness.py)

**Propagation.** In both pairs, unmarked loose distinction 18 corresponds under the given three-row match and has \((r_2,r_3)=(0,3)\) on each side. Here \(r_i\) counts other distinctions at distance \(i\) from this tip. Attach a single junction to the tip \(t\) with the same \(k\in\{2,3\}\) fresh distinctions on each side. All distances within this new junction equal \(k\). From an old distinction \(x\ne t\) to any new distinction the distance is \(D(x,t)+k-1\). The three marked rows therefore keep their matching, and the old pair and triple permissions on these marks persist. The new junction meets only one old junction. The number of new pairs at distance four is exactly \(k r_{5-k}\). At a new tip the new \((r_2,r_3)\) equals \((2,r_2(t))\) for \(k=2\) and \((0,3)\) for \(k=3\). Hence corresponding tips keep these two counts equal and add the same amount to each full \(C_4\).

Every nonnegative integer other than one is a sum of twos and threes. The two initial examples therefore give opposite legalities with matching rows and matching global parity at **every width at least 27**. Equal exact \(C_4\) is possible at width 28 and every width at least 30. The full tables stay distinguishable in these families. The width-27 difference in \(C_4\) is preserved. A two-fresh unary join adds three distance-two pairs and a three-fresh unary join adds none, so the width-28 difference at distance two is preserved as well. [Induction bases and first extensions](extension.json) · [Full-dual controls](check_extension.py)

## A size-independent candidate from the complete table

First separate components of finite bond distance, if any different components occur. In each one, for every proposed separating distinction \(t\), join two of its other distinctions \(x,y\) for this test whenever \(D(x,y)\ne D(x,t)+D(t,y)-1\). Take connected components of these links. If more than one component remains, the table presents a possible separation at \(t\). A genuine attachment through just one distinction always obeys the equality across its two sides, by the gluing result. The converse requires proof.

Reject a candidate that includes a separating distinction or that lies on different sides of one. For a surviving triple keep, for each separation, the side that contains all three marks together with its boundary distinction. Intersect these retained sets and restrict the table to them. An actual legal triple's three parents and their three pair witnesses form a six-junction cycle. The three witnesses are distinct because a common witness for two parent pairs would witness all three. Consequently no physical single shared distinction separates these parents from one another, and each of the three marked inputs is loose. The rejection step is valid provided the table has identified the physical separations correctly.

Use the three marked rows and \(C_4\bmod2\) **inside the retained part** as the candidate observation. One finite procedure at any supplied width is to enumerate all reachable presentations up through that width, form the set of retained observations of their legal triples, and accept a surviving triple when its observation occurs there. It uses the growth law and current distances. Labels and the actual history of the input never enter the decision.

| Complete test | Width 19 | Width 20 |
| --- | ---: | ---: |
| Single distinctions removed in the comparison | 155,629 | 388,280 |
| Genuine one-distinction separations | 16,027 | 38,617 |
| Disagreements between table and physical partitions | 0 | 0 |
| Candidate triples surviving the cuts | 3,416,901 | 9,671,289 |
| Legal triples surviving | 2,381 | 6,358 |

Across the two complete populations, 13,088,190 candidate occurrences survive. The retained three rows give five ambiguous descriptions and 36 forbidden matches. Appending the retained distance-four parity gives 1,404 legal descriptions, zero missed legal triples and zero forbidden matches in the pooled test. In both larger witness pairs the retained part is precisely the same sixteen distinctions from the original example. Its distance-four counts are still 32 and 33. These are exploratory results. [Cut and profile computation](check_core.py) · [Counts, partitions and deliberate faulty-table controls](core.json)

For the unary extensions of the width-27 and width-28 witnesses, this repair persists by induction. Suppose the new junction attaches at \(a\) outside the retained part and \(z\) is fresh. At any old test point \(s\ne a\), the pair \(a,z\) fails the equality through \(s\), since the value through \(s\) exceeds \(D(a,z)\) by \(2D(a,s)-2>0\). For any other old point \(x\), the equality for \(x,z\) through \(s\) holds exactly when it did for \(x,a\) through \(s\), by cancellation of \(k-1\). New vertices thus join the component of \(a\) without changing an old partition. When testing \(a\) itself, all old-to-new pairs across it obey the equality, and relations within the old side are unchanged. When testing a fresh \(s\), every old point and each other fresh point is linked to \(a\) by a failure of the equality. Thus the new test at a fresh point makes no cut. In these witnesses the marks keep exactly their sixteen original distinctions, including the same boundaries, through arbitrarily many such additions.

Two exact steps would prove this proposed reader for arbitrary reachable presentations.

1. **Recover the physical cuts.** For each removed \(t\), show that any two distinctions remaining in the same connected part of the physical incidence can be linked by a chain of pairs for which the displayed equality fails. A sufficient local lemma is that all surviving distinctions incident to each one junction lie in the same component of this test graph. The one-distinction formula already proves that such a chain cannot cross an actual cut.
2. **Distinguish the remaining marked triples.** Prove that when a legal and a forbidden triple in retained parts have identical three marked rows, the two local distance-four counts have opposite parity. This includes failures of looseness, distinct parents, or pair eligibility, as well as the common-neighbor obstruction. A witness against the reduced observation would still allow a richer reader on the full retained table. A witness against the full-table claim must transport the marks by an isometry of the entire table.

Two more checks narrow the possible full-table obstruction. Gluing the two original nineteen-distinction examples directly together gives 25 reachable choices of loose anchors among 81 tested. Of these, 12 retain the two original triples' opposite legality. All 194,250 candidate occurrences across the 25 constructions had consistent three-row answers *within their own presentation*. Separately, an all-size proof excludes distinct one-step successors of the same physical prefix, with the same fresh identities and identical allowed states on the same names. In this case both resulting three-parent menus are empty. This proof does not assume that equality of scalar distances implies equality of allowed states. Arbitrary larger histories and full-table isometries are the outstanding case. [Direct gluing test](same.json) · [Single-step theorem](complementary.md)

**Evidence.** The width-twenty result is an exhaustive computer-assisted finite classification, checked by separate forward and reverse algorithms within the task (V1). The extension and single-step results are mathematical statements on their stated families. The local reader beyond the tested widths and the uniform full-table inverse remain open.
