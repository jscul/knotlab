# What existence, parity and exact counts preserve

Status: Proved

## Standard statement

A table is any subset of the nine ordered pairs of labels in $\mathbb F_3$. The crossing sends $(x,y)$ to $(y,2y-x)$. For an offered power $k$ and a label $a$, count the table entries for which the first label after $k$ crossings equals $a$. The four readers may ask whether this count is positive, whether it is odd, both questions, or the exact count. A reader may use any offered $k$ and any label. Two tables are in one answer class if every such answer agrees.

With all three powers, **existence, parity, their combination and exact counts give 110, 128, 399 and 490 classes**, respectively, among all 512 tables. Existence and parity each retain distinctions the other loses. Their combination has one four-table class, while exact counts have two three-table classes. Two extra Boolean tests of the difference between the original labels suffice to recover the table from exact counts, or from parity if the extra tests also read parity.

## Nearest known result

The preceding crossing-power census gives the existence classes, their sizes and the message-length argument. This proof computes them again alongside the other readers. In the literature, sums on all $q+1$ kinds of parallel lines on a prime-size array occur in the finite Radon transform of Matúš and Flusser. The power queries here omit the tests of the difference $d=y-x$. Our comparison concerns the exact binary-table classes, including those created by reducing counts to positivity or parity. External novelty of the numerical census is unassessed. [Earlier crossing-power census](../../BRAID-READOUT-20261114-001A/BRAID-READOUT-20261114-001A-P001_power_menu_census/proof.md) · [Matúš and Flusser, 1993](https://doi.org/10.1109/34.254058)

## Exact finite classification

Write each original pair as $(x,d)$ with $d=y-x$. After $k$ crossings its first label is $x+kd$. For a fixed menu $K$, write $N_{ka}(S)$ for the number of pairs in $S$ with $x+kd=a$. For each possible vector of counts $n$, the coefficient of $\prod_{k,a} z_{ka}^{n_{ka}}$ in

$$
\prod_{(x,d)\in\mathbb F_3^2}
  \left(1+\prod_{k\in K} z_{k,x+kd}\right)
$$

is the number of source tables with exactly that vector. Choosing the first or second term in a factor omits or includes that original pair. Taking the product counts each table exactly once. To obtain the size of an existence, parity or combined class, sum the coefficients of all count vectors that reduce to its Boolean answers. This gives a finite coefficient calculation for every class.

In the last column, $s\times h$ means that $h$ classes each contain $s$ tables. The fixed message length in bits is the ceiling of the base-two logarithm of the number of classes. The public menu is known before the sender commits a message. The particular question is revealed afterward. A class index suffices, and every two classes differ on an offered question.

| Offered powers | Reader | Classes | Bits | Class sizes and their frequencies |
| ---: | --- | ---: | ---: | --- |
| 1 | Existence | 8 | 3 | 1×1, 7×3, 49×3, 343×1 |
| 1 | Parity | 8 | 3 | 64×8 |
| 1 | Both | 27 | 5 | 1×1, 3×3, 4×3, 9×3, 12×6, 16×3, 27×1, 36×3, 48×3, 64×1 |
| 1 | Count | 64 | 6 | 1×8, 3×24, 9×24, 27×8 |
| 2 | Existence | 50 | 6 | 1×34, 7×9, 25×6, 265×1 |
| 2 | Parity | 32 | 5 | 16×32 |
| 2 | Both | 210 | 8 | 1×121, 2×45, 3×12, 6×7, 7×9, 9×6, 10×9, 16×1 |
| 2 | Count | 328 | 9 | 1×230, 2×54, 3×24, 5×18, 6×2 |
| 3 | Existence | 110 | 7 | 1×73, 3×27, 16×9, 214×1 |
| 3 | Parity | 128 | 7 | 4×128 |
| 3 | Both | 399 | 9 | 1×316, 2×54, 3×28, 4×1 |
| 3 | Count | 490 | 9 | 1×470, 2×18, 3×2 |

All seven nonempty menus are checked. Their profiles depend only on menu size. Relabeling $k$ by $ak+b$ for $a\ne0$ is absorbed into the pair labels by replacing $(x,d)$ with $(x+bd,ad)$, and such a relabeling takes any ordered pair of distinct powers to any other. Equal message lengths can conceal different partitions. In particular the combined and exact readers both require nine bits with three powers, although one can distinguish tables that the other merges.

## Which distinctions each reader loses

Exact counts determine both Boolean answers at each position. Having both answers determines either one. All these refinements are strict, and the two individual readers are incomparable, for each nonempty menu size. The table below gives witnesses for all three powers. Each two-digit entry gives $(x,d)$, so 12 denotes $(1,2)$. Minimality is measured by the **total** number of occupied entries across the two tables.

| Same answers | Distinguishing information | Example pair of tables in $(x,d)$ | Minimum total entries |
| --- | --- | --- | ---: |
| Existence | Parity | $\{00,01,10\}$ and $\{00,10,12\}$. At $k=0,a=0$ the counts are 2 and 1. | 6 |
| Parity | Existence | Empty table and the six entries with $d=0$ or $d=1$. Every count is 0 in the first and 2 in the second. | 6 |
| Both | Count | $\{00,01,02,11,20\}$ and $\{01,10,11,12,22\}$. At $k=0,a=0$ the counts are 3 and 1. | 10 |
| Count | Original table | All three entries with $d=0$ and all three entries with $d=1$. Every count in either is 1. | 6 |

For the five-entry examples, the counts at the three powers in the first table are $(3,1,1),(1,1,3),(2,1,2)$. In the second they are $(1,3,1),(1,3,1),(2,1,2)$. Positivity and parity agree in every position. Every smaller total was excluded by examining each unordered pair inside each relevant answer class. For one offered power, the four minima in the order above are 3, 2, 4 and 2. For two powers they are 5, 4, 8 and 4. The data retain a minimizing pair for each case. [Finite witnesses and full class profiles](comparison.json)

For all powers, the unique largest combined class has every answer positive and odd. It contains the entire nine-entry table and the three tables with any one difference $d$ held constant. The full table gives count 3 everywhere. Each constant-difference table gives count 1 everywhere. Exact counts still confuse the three constant-difference tables. Their complements form the other three-table exact class, with count 2 everywhere.

## Why the missing difference matters

Fix a table $S$. Write $n_d(S)$ for its number of entries with difference $d$. At a position $(x,d)$, summing the three count answers whose queried sets contain that position gives

$$
\sum_{k=0}^2 N_{k,x+kd}(S) = 3\,\mathbf 1_S(x,d) + |S|-n_d(S).
$$

An entry with a different difference contributes once, since the first labels of the two entries agree at exactly one crossing power. An entry with the same difference contributes at all three powers if it is the queried position and zero times otherwise. Also $\sum_a N_{ka}(S)=|S|$ for any $k$. Thus equal full-menu exact counts force the difference of the two membership indicators to be constant on each fixed-$d$ set. Every changed fixed-$d$ set switches entirely from full to empty or vice versa, and their total sizes balance. Conversely, switching a full set for an empty one preserves every count.

This gives a second check of the 490 exact classes. If $r$ of the three fixed-$d$ sets are full or empty, the remaining $3-r$ have six possible partial patterns each. Specify which $r$ they are and how many $t$ are full. For each choice of partial patterns, the class has size $\binom rt$. For $r=0,1,2,3$ this gives precisely 470 singleton classes, 18 doubletons and two triples. Reducing the displayed identity modulo two similarly forces the symmetric difference of two parity-equivalent tables to be a union of whole fixed-$d$ sets. The number of such sets must be even because every test meets each one once. Conversely, complementing an even number preserves every count parity. Each table therefore belongs to a parity class of size four.

A **difference query at label $a$** inspects the original pairs with $y-x=a$. Its answer can be positivity, count parity, both, or the exact number $n_a(S)$. The following are numbers of classes after adding fixed queries of the indicated kind. Every subset of the indicated size was checked.

| Reader on all crossing powers | Added difference answers | None | One | Two | Three |
| --- | --- | ---: | ---: | ---: | ---: |
| Parity | Parity | 128 | 256 | **512** | 512 |
| Both | Parity | 399 | 464 | **512** | 512 |
| Count | Existence | 490 | 504 | **512** | 512 |
| Both | Existence | 399 | 413 | 428 | 440 |
| Existence | Count | 110 | 149 | 206 | 285 |

Two difference-existence bits distinguish the exact-count alternatives because each changed fixed-$d$ set is full in one table and empty in the other, with at least two such sets. Two difference-parity bits distinguish the parity alternatives because toggling all three entries changes their count parity, and two queried differences meet every nonempty even collection of three differences. One difference query of any of these kinds leaves the other two constant-difference tables indistinguishable. The two five-entry examples above also show why testing existence at **all** differences does not complete the combined reader. Their difference counts are $(2,2,1)$ and $(1,2,2)$, all positive.

## Independent checks and five-label scope

The direct check repeatedly executes the permutation on original ordered pairs and adds their observed counts. The second calculation multiplies the generating polynomial on $(x,d)$ and aggregates its integer coefficient vectors after applying each reader. They agree on each possible report of every ternary menu. The two algorithms were written in the same task, giving V1 validation. The displayed identity separately derives the full-menu exact and parity class structures. The numerical control includes a dense table which defeats the apparent equality of two readers in the sparse five-label check. [Replay and controls](check.py)

With five labels we checked all 31 nonempty menus on all 68,406 tables with at most five pairs. The full-menu class counts in this sparse roster are 64,527 for existence, 67,152 for parity and 68,402 for both or exact counts. In the latter two partitions the five constant-difference tables form one class and every other sparse table is unique. The equality of those two partitions ends on dense input. The full 25-entry table reports 5 everywhere and a constant-difference table reports 1 everywhere. Both counts are positive and odd. As an independent algebraic control on every five-label table, binary row reduction gives ranks 21, 22, 23, 24, 25 and 25 after adding zero through five distinct difference-parity tests. Four such tests distinguish every table, while three leave the two untested constant-difference tables indistinguishable. [Five-label results and difference-query census](comparison.json)

This is a finite-instance classification for the supplied crossing and readers. Fixed message length counts the states a message must distinguish. The proof supplies no running-time bound for general SAT decision.
