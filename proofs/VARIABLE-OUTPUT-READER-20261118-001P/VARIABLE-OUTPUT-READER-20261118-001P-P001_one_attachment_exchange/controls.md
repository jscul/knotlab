# One-attachment exchanges at width 31

Every live width-31 one-spent source separates from every candidate obtained by exchanging one attachment of its sole six-place junction. Bond distances through five already separate them. The width-31 result covers arbitrary simultaneous renamings and arbitrary lawful orders for the rival. [Frozen comparison](../../../research/VARIABLE-OUTPUT-READER-20261118-001P/preregistration.md)

## Complete width-31 sweep

The tagged generator gives 8,621 physical one-spent sources, including 2,394 with a legal triple. All 2,394 have one six-place junction. The generator also reproduces O’s width-29 counts of 2,854 total and 895 live. The inherited inverse fixes the physically small junctions and the two remaining loose outputs on supplied names. Call the fixed small incidence \(X\), the two outputs \(F\), and the old four attachments \(A\). This makes the candidate search finite without imposing a birth order on the rival. [O’s inverse](../../VARIABLE-OUTPUT-READER-20261118-001O/VARIABLE-OUTPUT-READER-20261118-001O-P001_one_spent_output/live_low_span.md#the-possible-four-attachments)

The sweep deletes each member of \(A\) and substitutes each available outside name that has one holder in \(X\). The following tests are cumulative. Write \(K=D+1\) for the least bond size containing a pair.

| Candidates remaining | Same low holder | Different low holder |
| --- | ---: | ---: |
| One named attachment exchanged | 4,921 | 54,419 |
| Four distinct low holders | 4,921 | 39,656 |
| Four low holders of one color in \(X\) | 4,921 | 12,392 |
| Added name reads \(K=6\) to both members of \(F\) | 16 | 16 |
| Added name reads \(K\le6\) to all three retained attachments | 0 | 0 |

The last two conditions are necessary because every pair in the proposed six-place support belongs to its size-six bond in a lawful rival. In fact every candidate surviving the sibling test fails on **all three** retained names. The three sizes are \((7,7,7)\) for all 16 different-holder candidates, and \((7,7,7)\) or \((8,8,8)\) for 4 and 12 same-holder candidates, respectively. This excludes even a distance-five match before any restriction on the rival's birth order.

The 32 close exchanges come from eight sources with a binary third three-output birth and two shrinks. They have 20 distinct pairs of source and added name. In every such pair the only six-shore containing the six-place junction and the added name’s holder is the whole source. Its boundary is the six currently loose distinctions and contains zero original attachments. Exact pair tables were recomputed for all 32 candidates. The fixed-support reachability check finds all 16 same-holder candidates lawful and 12 of those with a changed named menu. Four of the 16 different-holder candidates are lawful and all four change the menu. Each has a different table through distance five.

For all 4,921 same-holder exchanges, the swap of the two names gives a lawful relabeling that fixes every support in \(X\). The test compares the complete two affected matrix rows to check equality of the pair tables on the original names. All preserve the table through distance four, and 2,547 change at least one legal triple on those names. None preserves the entries through five. [Per-stage counts, six-shores, reachability and matrix differences](controls.json)

## A lawful different-holder exchange

Take the following chronological supports.

```text
(0,1,2)
(0,3,4,5)
(3,6,7,8)
(1,6,9,10,11)
(4,9,12,13)
(7,12,14,15)
(10,14,16,25)
(2,16,17,18)
(5,17,19,20)
(8,19,21,22)
(11,18,21,23,26)
(13,20,23,24,27,28)
(15,22,24,29,30)
```

Replace 23 with 25 at the six-place site. The same order is lawful after the replacement. The source permits exactly {25,26,29} and {25,26,30}. The rival spends 25 and has an empty menu. The surviving outputs 27 and 28 both read \(K=6\) to 25, while the three retained names 13, 20 and 24 each read \(K=7\) to 25 in the source. All 465 entries through distance four agree. Eleven entries differ through distance five and 47 differ in the full table. Two independent methods give those exact pair entries.

On the same source, replacing 23 with 26 is a same-holder exchange. It takes away both old triples and makes the two corresponding ones using 23 legal. All entries through distance four agree, with 12 changes through distance five and 20 in the full table.

## Predecessor controls

* At width 23, O’s exchange of 10 and 16 preserves distance four and reverses the verdict on {14,16,21}. It changes ten entries through distance five and 16 in the whole table.
* At width 25, O’s example retains a named legal triple using a surviving fourth output. None of its one-for-one candidates reaches the sibling test. The two live width-31 two-shrink controls from O, with one or both of the spending child’s outputs used, likewise separate from every candidate. The report includes the complete source menus and examples from both holder classes when available.
* N’s distinct width-31 terminal histories exchange 26 and 27 at one earlier holder while all three fresh outputs remain loose. They agree on all 465 exact entries and have the same three legal triples. The state with ones exactly at {24,25,27} satisfies only the left presentation. Appending {17,28,31,32} to both gives two lawful one-spent histories with empty menus. They agree through distance four and differ in exactly four entries through distance five and in the full table.

Run `python3 -B controls.py` with a C++20 compiler. It uses the inherited connected-cut engine and checks the explicit pairs by direct minimization in the parity span. The reachability search uses only the set of junctions already present. A join’s tests depend on their current incidence, so all legal birth orders are covered without retaining the order of an already reached subset. Any returned order is replayed with literal distinction names. [Checker](controls.py) · [Exact evidence](controls.json)
