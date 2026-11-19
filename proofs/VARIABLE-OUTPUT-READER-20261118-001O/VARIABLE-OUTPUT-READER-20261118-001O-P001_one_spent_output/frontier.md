# Legal triples after the fourth junction spends one output

The first live one-spent source has width 23. Its fourth three-output junction witnesses a pair of holders, and its spending child supplies a loose input. At width 25, a named triple using the fourth junction survives the spend. A nonshrinking two-move recurrence gives arbitrarily large live sources. The specific width-31 pair from N has empty one-spent menus along every allowed two-output continuation. [Frozen prediction](../../../research/VARIABLE-OUTPUT-READER-20261118-001O/preregistration.md)

## Earliest literal sources

In the following width-23 source, all names and site indices start at zero.

~~~text
(0,1,2)
(0,3,4,5)
(1,6,7,8)
(2,9,10,11)
(3,6,12,13)
(4,9,14,15)
(12,14,16,17)
(7,10,16,18,19,20)
(13,18,21,22)
~~~

The fourth three-output site is site 7. It supplies 18 to site 8, the spending child. Just before the spend there is no legal triple. Just afterward the menu is \(\{5,11,x\}\) for \(x\in\{21,22\}\). The holders are sites 1, 3 and 8, with respective witness sets \(\{0,5\}\), \(\{4\}\) and \(\{7\}\) for their three pairs. The child holds \(x\), and site 7 witnesses the last pair. The inherited formation predicate and a separate literal incidence test agree. Connected cuts and direct minimization in the parity span independently reproduce all 253 pair bond cardinalities of this source.

To obtain the earliest fourth-holder example, keep the first eight sites of this history and append \((5,8,21,22)\) and \((13,18,23,24)\). At width 25 the second of those is the spending child. Initially the menu is \(\{15\}\times\{18,19,20\}\times\{21,22\}\), viewed as unordered triples. Exactly four survive, replacing the middle set by \(\{19,20\}\). The mark \(\{15,19,21\}\) thus survives in its original names. The earliest survival of a named triple through the spend and at least one further move is at width 27. Its literal history in the certificate retains \(\{15,17,22\}\) from before the spend.

When the third and fourth three-output sites both take three parents, all immediately one-spent menus are empty. There are 34 positive later records, all without any shrinking join. The first has width 37 and marks \(\{27,31,35\}\). Its holders are sites 11, 13 and 15, with pair witnesses 10, 14 and 12 in that order. Site 11 is the fourth site, and site 14 is its spending child. The full menu is \(\{27,28\}\times\{31,32\}\times\{35,36\}\).

The spending child can also be the only shrinking join. Start from the width-25 fourth-holder example, keep all sites through \((5,8,21,22)\), and append \((15,21,18,23,24)\), \((11,23,25,26)\), and \((17,24,27,28)\). The first appended site is the child. The immediate menu is empty. By width 29 both of the child's outputs have been spent, and the menu is \(\{13,22,x\}\) for \(x\in\{27,28\}\), with the child a pair witness. The certificate also gives a width-27 reactivation in which neither distinguished site is adjacent to any of the legal holders.

## Exact formation quotient

The inherited frontier retains the loose counts and ordinary incidences of live holders, together with the distinct projected neighborhoods of retired sites having at least two live neighbors. Pair-witness existence and exclusion by a witness of all three use only those rows. A retired site cannot gain a neighbor. Projecting its row as other sites retire therefore preserves every future witness test. Multiple copies of a retired neighborhood have the same existence test. [Predecessor frontier](../../VARIABLE-OUTPUT-READER-20261118-001N/VARIABLE-OUTPUT-READER-20261118-001N-P001_fourth_at_the_parents/frontier.md#reachable-frontiers-before-the-fourth-birth)

Close the predecessor through the third three-output birth for each possible parent count. Try every lawful three-parent fourth birth. Tag the fourth site, which keeps three loose bits before spending and two afterward. The first move using it also tags the newborn child and records the spending arity. Each later move avoids the fourth holder. The child retains its tag when live. If the child retires, retain its particular projected neighborhood as well as the ordinary undistinguished witness rows. This preserves its role as a witness after its last output is used. The canonical holder permutations preserve loose multiplicities, adjacencies, witness rows and tags.

Loose siblings at one site have the same formation tests. For a lawful holder group the named choices multiply the loose counts of its holders. A projected transition can thus name one suitable loose bit per holder and replay the inherited rule without restricting its future shapes. For the first-spending comparison, every old witness of a previously legal group still exists. The newborn forbids that group if it meets all three holders. Otherwise the named members that remain loose give precisely the surviving triples. After one further move the same test characterizes continued survival. An input used in an ordinary join cannot become loose again, and a common ordinary witness persists. Hence a previously legal named triple that survives arbitrarily far must already survive the first additional move.

The first two births are unary and leave seven loose bits. A third three-output birth with \(p\) parents raises that count by \(3-p\), and the fourth birth leaves it unchanged. Thus there are at most \(10-p\) live distinctions, regardless of depth. Any deficit from \(10-p\) equals the total number of shrinking joins so far. The search seeds its shortest-depth layers at each fourth birth and advances one site per move. A completed history with \(s\) sites has width \(2s+5\). Consequently shortest-depth representatives certify the width minima, including those that require intervening moves or a later continuation.

The closure contains **47,640** records and **168,929** projected transitions. Counts below separate projected first-spending actions from later records. A later record is reachable with at least one move after the spend and can also have an immediate realization. The last column counts records supporting any legal triple. The certificate includes counts for the fourth and child separately as holders, pair witnesses, and neither, with ordinary adjacency also checked.

| Third parents | Spending parents | First-spend actions | Positive just before | Positive just after | Same named triple | Later records | Later positive |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 9,514 | 3,329 | 2,071 | 1,726 | 24,833 | 5,135 |
| 1 | 3 | 1,088 | 1,088 | 181 | 103 | 2,602 | 371 |
| 2 | 2 | 4,471 | 1,434 | 966 | 761 | 5,965 | 1,378 |
| 2 | 3 | 503 | 503 | 86 | 57 | 442 | 56 |
| 3 | 2 | 170 | 0 | 0 | 0 | 402 | 34 |
| 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |

Deduplicating immediate and later positive records gives 8,334. Of these, 6,094 have no shrinking join and 486 have the spending child as the sole shrinking join. The other 1,754 have at least one shrinking join outside the spend. Every positive record has at most two shrinking joins. The certificate gives the immediate count, later count, intersection and union for each combination of third parent count, spending arity and total shrinks.

| Third parents | Spending parents | First live width just before | First live width just after | First later live width |
|---:|---:|---:|---:|---:|
| 1 | 2 | 23 | 23 | 25 |
| 1 | 3 | 23 | 27 | 27 |
| 2 | 2 | 25 | 25 | 27 |
| 2 | 3 | 25 | 27 | 31 |
| 3 | 2 | — | — | 37 |
| 3 | 3 | — | — | — |

Each shortest example is replayed with literal identities and checked at all three times. The tables above concern formation and ordinary roles. The scalar data in this certificate are confined to the named width-23 control.

## The width-31 pair and an unbounded live family

In the width-31 pair from N, the transposition of 26 and 27 identifies the physical histories. Close binary and ternary two-output moves after the fourth birth while allowing its first spend and keeping its other two outputs loose. Individually there are 18 records, 15 of them one-spent. They contain zero one-spent legal triples. In a shared named suffix the disputed spare at old site 11 must be reserved, since each of its two candidate distinctions is shared on one side. The marked closure for a common suffix has five records. Its three one-spent records have empty menus and offer no further permitted move retaining two fourth outputs. [Named pair](../../VARIABLE-OUTPUT-READER-20261118-001N/VARIABLE-OUTPUT-READER-20261118-001N-P001_fourth_at_the_parents/frontier.md#the-literal-width-31-pair)

The width-25 fourth-holder example has a different continuation. Append \((11,23,25,26)\), \((17,24,27,28)\), \((25,27,29,30)\), and \((26,28,31,32)\). At width 33 the mark \(\{15,19,21\}\) remains legal. There are two live sites holding \((29,30)\) and \((31,32)\). They have no live ordinary neighbors, and the only projected retired neighborhood meeting either of them contains exactly those two. These two sites can supply a binary join twice, each time giving one bit. The second join exhausts both old holders. The two newborn holders have the same two loose bits per holder, no live ordinary neighbors, and a common retired witness. Their projected witness rows are again confined to that pair. All other projected rows and the three named mark holders persist. The two moves therefore return to the same tagged frontier, increase the width by four, and retain the legal mark at every repeat. The certificate checks the first two repetitions on literal identities.

~~~sh
.venv/bin/python -B proofs/VARIABLE-OUTPUT-READER-20261118-001O/VARIABLE-OUTPUT-READER-20261118-001O-P001_one_spent_output/frontier.py
~~~

[Replay](frontier.py) · [Exact counts, histories and short scalar control](frontier.json)
