# Why six starting knots can close with two added meetings

**Two is the minimum number of simple meetings beyond a tree that can give a whole closure on six founding knots under the stated private-opening cap.** Trees and single added meetings are excluded at every age by the previous results. For sufficiency the six-knot source below reaches its closure after four ordinary parity cuts. [Tree obstruction](../IDLE-PHASE-AND-TREE-CLOSURE-20261121-001/tree_proof.md) · [One-added-meeting obstruction](../KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B/one_meeting.md) · [Named receipt](../../artifacts/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A-E001_meetings/matched_and_signed.json.gz)

## Source eligibility

Each meeting is one name held by exactly its two endpoints. Each private distinction has one founder. For a holder of final degree \(d\) the supplied private count is \(\max(0,3-d)+b\) with \(b\in\{0,1\}\). Thus local arity is at least three. The two rules respectively require even parity and both binary values to occur (not-all-equal). Their local allowed sets meet K1–K3. The checker confirmed every source arity present and the arity of the actual even closure. [Canonical local reports](../../artifacts/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A-E001_meetings/local_knot_checks.json)

The private names suffice for the full global projection onto each founder. Fix all distinctions of one holder \(H\). Each component \(D\) after its deletion contains a holder having a private name. To see this write \(s\) for the number of holders in \(D\), \(e\) for its internal meetings and \(t\ge1\) for its distinct meetings with \(H\). The connected subdiagram \(D\cup\{H\}\) has at most the two extra meetings of the whole, hence \(e+t-s\le2\). If every holder of \(D\) had original degree at least three, then \(3s\le 2e+t\le2s+4-t\). Thus \(s\le3\). When \(s\le2\), simplicity makes every such degree at most two. When \(s=3\) the inequality requires \(t=1\), so \(2e+t\le7<9\). This contradiction gives the required holder of degree at most two and its private name.

Root a spanning tree of each \(D\) at that holder. Keep one private distinction at its root and one meeting to its parent at each other holder. Set unused distinctions freely and fill the tree from the leaves inward. Each holder has a remaining name on which its even or not-all-equal condition can be satisfied. This extends every allowed word at \(H\), and after erasing its rule it extends forbidden \(H\) words as well. This argument applies to every size under these two simple additions. Only the six-knot growth census is enumerated here. All 19 unlabelled meeting patterns also passed the component calculation directly. Every funded decorated type passed literal full projections and erasure checks under both laws. [Native and projection audit](../../artifacts/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A-E001_meetings/physical_audit.json)

## The positive named founder and its receipts

Use the meeting pairs \(01,02,03,12,14,34,35\), with knots 4 and 5 given the optional extra. The names are assigned first to these pairs, in that order, and then to private openings in holder order.

| Knot | Founder distinctions | Initially loose |
| ---: | --- | --- |
| 0 | 0, 1, 2 | None |
| 1 | 0, 3, 4 | None |
| 2 | 1, 3, 7 | 7 |
| 3 | 2, 5, 6 | None |
| 4 | 4, 5, 8, 9 | 8, 9 |
| 5 | 6, 10, 11, 12 | 10, 11, 12 |

There are 128 founding even words and 1,918 not-all-equal words. The three live knots form the witnessed sequence \(2,4,5\), where pairs \(2,4\) and \(4,5\) each make one call. Their private supplies are 1, 2 and 3. The two remaining names at knot 5 each make a separate unary birth. The two laws give the following first three paid cohorts. Entries in each list correspond from left to right.

| Cut | Child knots | Old parents | Grants of new names | Total old names spent |
| ---: | --- | --- | --- | ---: |
| 1 | 6, 7, 8, 9 | (2,4), (4,5), (5), (5) | 1, 3, 2, 2 | 6 |
| 2 | 10, 11, 12, 13 | (6,7), (7,8), (7,9), (8,9) | 2, 2, 2, 1 | 8 |
| 3 | 14, 15, 16 | (11,12,13), (10,11), (10,12) | 1, 1, 1 | 7 |
| 4 | 17 | (14,15,16) | 0 at parity, 1 at not-all-equal | 3 |

At cut three the related live knots 11, 12 and 13 have pairwise witnesses and no one witness holding them together. At the next end each of 14, 15 and 16 has one loose name, respectively 28, 29 and 30. Every pair is witnessed, and no older knot witnesses all three. Their only multi-parent proposal consumes all three openings. Every old shared name occurs twice in the sum of the 17 preceding even equations. The sum therefore has exactly the three loose names as support. Adding this implied even equation leaves all 16,384 preceding words intact on 31 names. The new whole has 18 knots, every name held twice, and no other birth in its closing cut. Changing only the parity of row 17 makes the augmented rank 18, one more than the coefficient rank 17, leaving zero scalar words. The corresponding unsigned fourth child receives private name 31 and the holding remains open. [Every input, new name, grant and row](../../artifacts/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A-E001_meetings/matched_and_signed.json.gz)

The supplied odd sign admits the previously specified operator reading. In the physical knot incidence there are three-against-three meetings after contraction, with one group \(10,12,17\) and the other \(14,15,16\). Seven of the nine connections are direct. The remaining two run through \(10,6,4,3,5,9,13,14\) and \(12,7,11,15\). Their internal knots are distinct and exclude the six designated ones, certifying the sign obstruction's positive side. Independently, binary operators assigned to all 31 named distinctions square to the identity. Their within-holder operators commute. Their product is \(+I\) at each of the 17 older knots and \(-I\) at the actual closing knot. These are two checks of a supplied signed reading after the ordinary growth event. [Certificate and named assignments](../../artifacts/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A-E001_meetings/matched_and_signed.json.gz) · [Signed criterion](../FOUR-READINGS-20261120-001A/derivations.md)

A positive-grant comparison uses the same founder. At the first cut child 6 spends the marks of 2 and 4 and receives private name 13. Flipping name 13 reverses only this newborn row, leaving siblings and all founders unchanged. Each supplied sign has 2,048 extended words and all 128 original words can be extended at either sign. In contrast, the actual cut-four input already satisfies the even equation throughout the old allowed set and has no fresh name to change.

## Seven still-connected parity survivors at the frozen stop

All eight initially funded, connected decorated types use the same seven original meetings shown above. The digits in the table give each founder's six optional flags in holder order \(0,\ldots,5\). Each type realizes 720 labelled holdings and has 11 possible original trees. The fourth-cut signs on the type marked as the measured closure are the only terminal signs actually tested in the primary population.

| Flags | Paid births at cuts 1–4 | Grants summed by cut | What the four observed cuts establish for ordinary parity |
| --- | --- | --- | --- |
| 000010 | 3, 3, 3, 3 | 5, 5, 5, 5 | The initial live end returns after one cut and repeats. |
| 000011 | 4, 4, 3, 1 | 8, 7, 3, 0 | Measured ternary whole closure at cut four. |
| 001010 | 4, 5, 6, 7 | 8, 10, 12, 14 | A path of two-opening knots gains one knot per cut indefinitely. |
| 001011 | 5, 6, 6, 6 | 11, 12, 12, 12 | The cut-two live end returns at cut three. |
| 001110 | 4, 4, 4, 4 | 7, 7, 7, 7 | The initial live end returns after one cut. |
| 001111 | 5, 5, 4, 3 | 10, 9, 7, 3 | At cut four its end equals the known closer's cut-three end up to relabelling. |
| 011010 | 4, 4, 4, 4 | 7, 7, 7, 7 | The initial live end returns after one cut. |
| 011011 | 5, 5, 4, 3 | 10, 9, 7, 3 | At cut four it also equals the known closer's cut-three end up to relabelling. |

The end read here records the opening count at every live knot and maximal subsets of live knots with a common old physical witness. Smaller contained subsets and repeated identical witnesses add no new pair or held whole. An isomorphism preserving those data preserves every proposed parent group and its demand. It preserves the remaining unary counts and which children have a common old parent, hence their lookahead prices. In a single connected physical holding it also preserves the sole-birth test for even implication. It therefore induces isomorphisms at successive ends under a specified ordinary law. The complete past physical holding need not repeat, and the operator reading of a later closure would require its full twice-held incidence. [Earlier end law](../ORDINARY-DYNAMICS-20261120-001/end_operator.md) · [Actual named end bijections](../../artifacts/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A-E001_meetings/connected_survivors.json.gz)

For the growing path, let \(m\ge3\) live knots have two openings each, and let the witnessed subsets be its \(m-1\) consecutive pairs only. Every interior knot owes its two neighbours and each endpoint owes one. Thus the new cohort consists of the \(m-1\) pair children and one unary child at each endpoint. Two children have a common parent precisely when consecutive in this \(m+1\) knot sequence. Each paired child is interior with following demand two. The endpoint unary's arity floor requires two. Every child is therefore given two openings. This proves induction.

Each of the two final rows matching the measured closer has cut-four knots \(20,21,22\) with one opening apiece. The recorded bijection \(20\mapsto14,\ 21\mapsto15,\ 22\mapsto16\) preserves every witnessed pair and the lack of a whole common witness. The next ordinary update is forced by the already measured transition of that equivalent end. Thus both sources must close by a ternary at cut five under parity. This is an inference from their actual fourth cuts. No six-knot founder was run to a fifth cut, and the two predicted closures have no measured operator verdict. Under not-all-equal all eight sources in the table remain open at cut four. Every paid NAE birth needs at least one fresh distinction. All 83 other funded source types already have two or three separate live groups initially, and all retain them through the observation. Connected physical holdings and persistence of distinct live groups exclude ordinary parity closure at any finite age for those 83. The 660 initial funding stops are permanent. [Named ledger for every class](../../artifacts/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A-E001_meetings/all_funding_and_components.json.gz)

Whole closure at six knots is thus decided for every covered start and every age by a four-cut census and structural deductions. Its exact frequency still depends on the source weighting. Independent scientific referee pending.
