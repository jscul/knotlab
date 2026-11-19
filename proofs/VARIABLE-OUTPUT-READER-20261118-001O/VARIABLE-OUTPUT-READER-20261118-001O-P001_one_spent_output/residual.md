# A two-shrink source with both child outputs used

Width 31 is the first live source in this subfamily where a later junction uses an output of the binary spending child. At that width both child outputs can already be used and a remaining output of the fourth junction can belong to a legal triple. On the example below, bond distances through five determine the entire physical presentation against every reachable rival.

## Minimum width and formation

Filter the complete one-spent quotient to unary or binary third births, a binary spending child and at least two shrinking joins. The total shrink count is \(10-p-F\), where \(p\) is the third birth's parent count and \(F\) the number of loose bits. The child starts with two outputs. Its current loose count, zero when it retires, determines how many were used. A legal triple uses a remaining fourth output exactly when that site is one of its holders. All these tests respect the quotient, and the stored shortest paths give the width minima. [Formation quotient](frontier.md#exact-formation-quotient)

All 96 positive records in the filter have a unary third birth and exactly two shrinks. No record with a binary third birth qualifies.

| Child outputs used | Fourth junction holds a legal input | Other positive records |
|---:|---:|---:|
| 0 | 21 | 7 |
| 1 | 21 | 6 |
| 2 | 39 | 2 |

Use these supports in order.

~~~text
(0,1,2)
(0,3,4,5)
(1,6,7,8)
(2,9,10,11)
(3,6,12,13)
(4,9,14,15)
(12,14,16,17)
(7,16,18,19)
(15,18,20,21)
(8,10,20,22,23,24)
(13,22,25,26)
(5,21,25,27,28)
(11,17,26,29,30)
~~~

The fourth three-output junction is site 9, and its child at site 10 spends output 22. The next two sites are the shrinking joins and spend 25 and 26, respectively. The present menu is \(\{19\}\times\{23,24,27,28\}\times\{29,30\}\), viewed as unordered triples. For \(\{19,23,29\}\), the holders are sites \(7,9,12\), with pair-witness sets \(\{2,8\},\{6\},\{3,10\}\). Site 9 holds 23. The child still witnesses the last pair after both its outputs have been used.

## The exact through-five inverse on this example

The two remaining fourth outputs are 23 and 24. The least bond size through either is six. For \(x=23\) the closed set \(S=\{x\}\cup\{z:K(x,z)=6\}\) is \(\{8,10,20,22,23,24\}\), of size six. The lower bound for a spent image in a through-five correspondence is eleven. [Sibling row test](holders.md#holder-and-permission-consequences)

Connected cuts and direct parity minimization agree on all 465 named pair entries. Through distance four the short-equation procedure forces rank 12. At distance five it forces rank 13, attaining the unrestricted rival rank bound. The physical checker finds 27 candidate short supports. Five candidates reach full width before remeasurement. The source is the sole support family that agrees through five, and it agrees on the complete table. A simultaneous permutation of all coordinates yields precisely the transported support family and menu. This certificate concerns the displayed source. [Rival rank bound](../../VARIABLE-OUTPUT-READER-20261118-001N/VARIABLE-OUTPUT-READER-20261118-001N-P001_fourth_at_the_parents/rank.md#the-rank-bound-from-distance-four) · [Physical inverse checker](census.py)

~~~sh
.venv/bin/python -B proofs/VARIABLE-OUTPUT-READER-20261118-001O/VARIABLE-OUTPUT-READER-20261118-001O-P001_one_spent_output/residual.py
~~~

[Replay](residual.py) · [Exact counts, histories and inverse](residual.json)
