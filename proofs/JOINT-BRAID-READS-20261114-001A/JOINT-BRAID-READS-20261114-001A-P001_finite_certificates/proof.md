# Which states have their own crossing tests?

Status: Proved

## Standard statement

A state of one pair of strands has labels $(a,a+d)$ in $\mathbb F_3$. A public test $(k,t)$ asks whether the first label equals $t$ after $k$ crossings. Among the nine states, **five** can simultaneously have a test that accepts only that state within the chosen set. Six states admit an order in which each has a test that rejects all later states. The incidence matrix has rank **six** over $\mathbb F_3$.

For $b$ pairs, a public test specifies one such test on every pair. The answer for an input table is yes if **one joint state** passes all of them. Eight pairs already have **459,270** states with distinct private tests, exceeding the **390,625** obtained by taking products of the one-pair maximum. Every subset of a privately tested set gives different answers, so at least 459,270 fixed message bits are required for arbitrary tables at eight pairs.

## Nearest known result

The preceding study classifies one-pair support, parity and exact-count readers. It provides the one-pair setting. Here the tests combine multiple pairs under a single existential quantifier. [Previous reader comparison](../../BRAID-COUNTS-20261114-001A/BRAID-COUNTS-20261114-001A-P001_reader_comparison/proof.md)

In the literature a privately tested set selects an induced matching in a bipartite graph and a triangular submatrix selects a half-induced matching. Groenland, Mannens, Nederlof, Piecyk and Rzążewski give these definitions, relate powers of the matrix to representative subsets, and show in Lemma 11 how balanced words in a triangular submatrix yield induced matchings in its powers. We use the specified crossing to obtain concrete matrices, finite maxima, product sizes and a counterexample to retaining separate tables. The arguments below verify them directly. [Groenland et al., ICALP 2024](https://doi.org/10.4230/LIPIcs.ICALP.2024.77)

## The one-pair certificates

The actual crossing sends $(u,v)$ to $(v,2v-u)$. It preserves $v-u=d$ and advances the first label by $d$. Thus

$$
M_{(k,t),(a,d)}=\mathbf1[a+kd=t].
$$

In the following array both rows $(k,t)$ and columns $(a,d)$ use the order $00,01,02,10,11,12,20,21,22$. Each column is a state and each row is a test.

~~~text
111000000
000111000
000000111
100001010
010100001
001010100
100010001
001100010
010001100
~~~

A private test accepts its chosen state and rejects all other chosen states. In the order below these five tests and five states give an identity submatrix.

| | First | Second | Third | Fourth | Fifth |
| --- | --- | --- | --- | --- | --- |
| State $(a,d)$ | 00 | 01 | 02 | 11 | 20 |
| Test $(k,t)$ | 10 | 11 | 21 | 01 | 02 |

**Five is maximal.** Suppose six states were chosen. Every row has three states, so a private row must contain two of the three omitted states. Any two distinct states agree on at most one test. Indeed, two distinct affine functions of $k$ can agree at most once, and at that power only their common label qualifies. Thus the three omitted pairs of states can supply at most three private rows. Six states need six distinct private rows. A larger privately tested set would retain privacy on every six-member subset. This proves the upper bound independently of the census.

The following six-state certificate gives two groups of three letters. Number them 0 through 5 in the indicated order. Within either group each matched test accepts exactly its matched state. Every test in the low group rejects all three high states.

| Letter | 0 | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- | --- |
| Group | Low | Low | Low | High | High | High |
| State $(a,d)$ | 10 | 22 | 11 | 00 | 12 | 01 |
| Test $(k,t)$ | 21 | 02 | 12 | 20 | 01 | 11 |

The literal submatrix in that order is

~~~text
100000
010000
001000
011100
101010
110001
~~~

This lower triangular matrix has determinant one. For the reverse bound over $\mathbb F_3$, the indicator of equality is $1-(a+kd-t)^2$. Expanding expresses every row as a linear combination of the six column functions $1,a,d,a^2,ad,d^2$. Thus the rank is exactly six and no seven-state triangular submatrix exists. Direct elimination gives rank seven over $\mathbb F_2$, which shows why the choice of field matters here.

| Chosen states | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7–9 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Privately tested subsets | 1 | 9 | 36 | 84 | 81 | 27 | 0 | 0 |
| Subsets admitting a triangular ordering | 1 | 9 | 36 | 84 | 126 | 126 | 72 | 0 |

The exhaustive count visits all 512 subsets. For a subset of columns, intersect each row with the subset. The private count requires every selected column to occur as a singleton intersection. The ordered count starts with the empty set. It records a subset whenever removing one singleton intersection leaves an already recorded subset. This recurrence is exhaustive because the first test in a triangular ordering has a singleton intersection, and any such test can precede an ordering of the remainder. Its row then has no entries in the remainder and cannot be reused later.

## Certificates for simultaneous tests

The matrix for $b$ pairs is the ordinary Kronecker product $M^{\otimes b}$ because one joint state passes exactly when each of its entries passes its own test. A matched query is specified by the same word of letter indices as the chosen state, using the matched tests in the certificate.

* Five-letter products give $5^b$ private states. Any unequal word differs on a coordinate where the one-pair identity matrix rejects it.
* Using the triangular list of six letters, take all words of one fixed total digit sum. An accepting query word can only match a state word whose digit at each coordinate is at most the corresponding query digit. Equality of their total sums forces the words to agree. The number of words of sum $s$ is the coefficient of $z^s$ in $(1+z+\cdots+z^5)^b$.
* Using the two groups of three, take all words with exactly $h$ high letters. If a test word accepts a state word, every high position of the state must be high in the test. With both counts equal the high positions agree. Within each group the identity test then forces the labels to agree in every coordinate. This gives $\binom bh3^b$ private words.

| Pairs | Five-letter product | Middle digit sum | Exactly $\lfloor b/2\rfloor$ high letters |
| ---: | ---: | ---: | ---: |
| 2 | 25 | 6 | 18 |
| 3 | 125 | 27 | 81 |
| 4 | 625 | 146 | 486 |
| 8 | 390,625 | 135,954 | **459,270** |

The checker runs every test word against every selected state word for the digit-sum and high-count examples at two, three and four pairs, applying the actual crossings at each coordinate. It separately verifies the entire five-letter products at two and three pairs. Binomial coefficients give the displayed high-count bound at eight pairs and show that eight is the first size where that construction beats $5^b$. Integer convolution places the first such success for the middle digit sum at 16 pairs, with 163,112,472,594 versus 152,587,890,625 states. These are bounds from specific constructions. At two pairs we certify $25\leq\text{private maximum}\leq36$, using the five-letter product below and rank $6^2$ above. Its exact maximum is open here.

A private set of $n$ states yields $2^n$ distinct Boolean reports. For two different subsets take a state in their symmetric difference and ask its private query. The reports differ, establishing the fixed-message lower bound in the statement. This bound concerns a sender given an arbitrary table of joint states and a later reader who chooses these simultaneous tests.

## Keeping the same joint witness

Let $p=(0,0)$ and $q=(0,1)$ in the $(a,d)$ representation. Compare the two joint tables

$$
T_{=}=\{(p,p),(q,q)\},\qquad T_{\ne}=\{(p,q),(q,p)\}.
$$

Both positions in both tables individually allow precisely $p$ and $q$, so even their full separate tables agree. Ask for first label zero after one crossing in **both** positions. On each individual position this accepts $p$ and rejects $q$. The joint answer is yes for $T_{=}$ and no for $T_{\ne}$. An independent choice of single-coordinate witnesses gives a false positive on $T_{\ne}$.

When the input really is a product $S_1\times\cdots\times S_b$, every set of individual witnesses combines to a joint witness. The joint yes set is the Cartesian product of the individual yes sets. There are 110 one-pair yes sets, of which exactly one is empty. Each nonempty product recovers every factor yes set by projection, and all products with an empty factor give the empty report. Hence there are exactly $1+109^b$ product-input reports. At $b=2$ this is 11,882, requiring 14 fixed bits. The checker constructs every such two-pair report and exercises the logical equivalence on all 1,296 choices of single factors from the two distinguished states and public queries. [Finite data and controls](certificates.json)

## Verification scope

The verifier derives the entire matrix by executing the crossing and compares it with the displayed affine formula. Its concrete rank factorization, elimination, subset enumeration and direct product queries use separate checks. In both the private and two-level certificates it changes one public test to a distinct test that still accepts the assigned state but now also accepts another selected state. Both changes fail the certificate. Adding a word from a second high-count level also produces a genuine collision. These are V1 checks within the task. The evidence is a finite-instance classification with explicit bounds for the named product constructions. No complexity bound for unrestricted 3-SAT decision follows. [Checker](check.py)
