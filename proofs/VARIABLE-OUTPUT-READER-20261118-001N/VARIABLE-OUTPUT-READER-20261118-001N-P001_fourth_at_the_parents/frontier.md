# A moved fourth junction that holds a legal input

An exact width-31 pair-bond table admits a correspondence that moves the actual support of the fourth three-output junction. That junction itself supplies one of the three loose inputs of a legal next join. The two named allowed-state relations differ. Both permit precisely the same next triples in this correspondence. [Frozen prediction](../../../research/VARIABLE-OUTPUT-READER-20261118-001N/preregistration.md)

## The literal width-31 pair

Both presentations begin with the following ordinary supports, in formation order and with names starting at zero.

~~~text
(0,1,2)
(0,3,4,5)
(3,6,7,8)
(1,6,9,10,11)
(4,9,12,13)
(7,12,14,15)
(14,10,16,17)
(2,16,18,19)
(5,18,20,21)
(8,20,22,23)
(19,11,22,24,25)
(13,21,24,26,27)
~~~

The two initial three-output additions are unary. The third is binary. The fourth legally consumes either \(\{15,23,26\}\) or \(\{15,23,27\}\), on the same three distinct holders, and makes fresh \(\{28,29,30\}\). The twelve-site prefix is connected and its exterior is the other shore of the bond \(\{15,17,23,25,26,27\}\). The two final ordinary graphs each remain connected after deletion of any one site.

The full table match fixes every distinction. All 465 entries of \(K\), the minimum pair bond cardinality, agree. The measured pair-bond distance is \(K-1\). The connected-cut enumerator and independent minimization of all XORs of literal supports give the same entries in both presentations. The assignment with one bits \(\{24,25,27\}\) satisfies every left equation and violates the right fourth equation. The transposition of 26 and 27 relates the two ordinary incidences. The full table allows the identity correspondence as well.

The common menu consists of \(\{17,25,x\}\) for \(x\in\{28,29,30\}\). Their holders are sites 6, 10 and 12. For those three holder pairs in order, the existing ordinary witness sets are \(\{3,7\}\), \(\{5\}\) and \(\{9,11\}\). Their intersection is empty, and the fourth junction is the holder of \(x\). The checker recomputes the literal menu with the inherited formation predicate and separately checks loose multiplicities, distinct holders, the three pair-witness conditions and the exclusion of a common witness.

One extra joint reading suffices to distinguish these two named relations. For the marked query \(\{15,26,28\}\), the minimum cardinality of a bond containing the triple is 6 on the left and 9 on the right. For the legal mark \(\{17,25,28\}\), it is 6 in both. Across all 4,495 named triples, 144 joint entries differ. The sufficiency claim is for the exhibited pair and correspondence.

## Reachable frontiers before the fourth birth

The first two additions are unary because there is no available pair of old holders with a common ordinary witness. Close from both possible starts. Keep the loose count at each live holder, their ordinary incidences, and the set of projected exhausted-site neighborhoods containing at least two live holders. An exhausted site can gain no later ordinary neighbor. For a set of live holders, the projected rows test the existence of a witness for each pair and the possible exclusion by a witness of all three. A step uses one loose bit per chosen holder, adds the corresponding ordinary incidences to the newborn site, and projects away exhausted holders. The holder canonicalization retains all these data. [Predecessor quotient](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/family.md#all-histories-have-at-most-two-shrinking-joins)

Record whether the third three-output birth has occurred and its parent count when it has. Two-output births use two or three parents, so the loose count starts at seven and cannot increase except at the third birth. A third birth with \(p\) parents leaves at most \(10-p\) loose bits. The four branches, before the third birth and after each of its respective arities, close to 1,118, 65,304, 24,781 and 2,215 records. Their projected transition counts are 15,933, 434,184, 161,971 and 10,227, assigning each step to its starting branch. These are finite regardless of history length.

At six or seven loose, the checker tries each allowed parent arity for the fourth three-output birth and every loose-bit choice within a parent group. It reads each resulting named menu and the fourth site's possible roles. These are the results when the fourth birth has three parents.

| Third parents | Old loose | Old records permitting birth | Input sets | With a live menu | With fourth as holder | With fourth as pair witness |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 6 | 57 | 134 | 0 | 0 | 0 |
| 2 | 6 | 96 | 244 | 2 | 2 | 0 |
| 3 | 6 | 26 | 68 | 0 | 0 | 0 |
| 1 | 7 | 1,053 | 2,399 | 181 | 83 | 36 |
| 2 | 7 | 1,533 | 4,104 | 568 | 183 | 204 |
| 3 | 7 | 314 | 677 | 0 | 0 | 0 |

The two positive six-loose choices come from one frontier with five holders of loose counts \(1,1,1,1,2\). They exchange the two loose bits at the last holder. Breadth-first depth and the fixed width at a given depth place the first direct role for a ternary fourth birth from six loose at width 31. From seven loose, a ternary fourth can already have a direct role at width 27. For a ternary fourth birth from six loose, alternatives on any common frontier have equal named menus. The seven-loose alternatives include cases with distinct named menus before measurement.

There are four unordered complementary input pairs in each third-parent branch. The complementary choices use the same three holders, each with two loose bits. Both resulting menus are empty. In any literal realization of such a prefix the complementary final equations differ by the XOR of all prefix rows, so the two allowed-state relations agree on their named distinctions.

## Exact comparisons on literal prefixes

The scalar comparison uses one shortest literal realization of each qualifying tagged frontier of at most twelve old sites, which is old width at most 28. It tests all named three-parent choices for the fourth junction on that realization. Every retained old history is replayed through the inherited formation rule. The complete pair tables are compared using a single isometry for each match, together with the generators of the source table automorphisms. The generators suffice for checking preservation of an entire menu. For support movement, the checker follows the orbit of the fourth support and tests each transported image against the actual target supports.

The scope contains 790 old realizations, 2,264 final choices and 4,126 unordered cross-pairs on common prefixes. It contains 2,264 self cases. Of the cross-pairs, 2,014 match exactly. Twelve matched pairs have nonisomorphic ordinary incidences. Their menus are all empty. No tested table isometry changes a triple permission. Three comparison cases move the fourth support while it holds a legal input or witnesses a pair. These exact comparisons concern the chosen literal representatives. The all-depth frontier data concern formation and roles.

## Following the two exchanged bits

There are ten common two-output choices immediately after the named width-31 pair. Every resulting menu is empty. One choice, taking \(\{17,25\}\), preserves all named pair entries. The six choices taking two inputs including a fourth output change four entries. The three choices taking three inputs including a fourth output change eight. The twelve two-step paths all take a fourth output and change eight entries. Every table along these finite checks still matches across the physical transposition of 26 and 27.

A continued common named history can consume neither 26 nor 27, since each is already shared on one side. The sole remaining loose distinction at old site 11 is 27 on the left and 26 on the right. Mark site 11 in the initial frontier and disallow its selection in a suffix move. At each frontier still allow it in the permission query. The marked quotient closes over arbitrarily long binary and ternary two-output suffixes with 46 six-loose states, one five-loose state, 95 binary transitions and one ternary transition. The two literal histories replay every projected transition. No reached menu uses the marked holder. Since the physical transposition fixes all other names, every named triple permission along such a common suffix agrees across the pair, including when named pair readings change.

~~~sh
.venv/bin/python -B proofs/VARIABLE-OUTPUT-READER-20261118-001N/VARIABLE-OUTPUT-READER-20261118-001N-P001_fourth_at_the_parents/frontier.py
~~~

[Replay checker](frontier.py) · [Exact measurement helper](table_tools.py) · [Histories, table and closure records](frontier.json)
