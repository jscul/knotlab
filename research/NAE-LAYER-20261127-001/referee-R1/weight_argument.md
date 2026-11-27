# What the equal weighting keeps

On a ring of four three-place not-all-equal knots, two parities carried on disjoint loose pairs take all four joint values. Their counts in the order 00, 01, 10, 11 are **26, 20, 20, 16**. Independence would require $26\cdot16=20\cdot20$. Every one of the 15 proper subsets of the four laws gives independent readings when each allowed state counts once and every distinction is retained. Their dependence persists through two ordinary growth rounds. The reading groups two loose distinctions by hand. The result concerns the weighting of allowed states. Every joint value still occurs. [Exact tables](weight_tables.json)

## A count for rings of every even size

Give each knot $i$ shared distinctions $x_i,x_{i+1}$ and a loose distinction $z_i$, with indices modulo $2k$, for $k\ge2$. Reader $j$ reports whether $z_{2j}$ and $z_{2j+1}$ differ. The readers use disjoint pairs. If precisely $t$ readers report a difference, the number of allowed states giving that particular word is

$$
5^{k-t}4^t+\mathbf1_{t=0}.
$$

For fixed loose value 0 or 1, the counts at a knot, with the incoming and outgoing shared values as row and column, are respectively

$$
L_0=\begin{pmatrix}0&1\\1&1\end{pmatrix},\qquad
L_1=\begin{pmatrix}1&1\\1&0\end{pmatrix}.
$$

Summing at the distinction shared within a reader's pair gives $L_0^2+L_1^2=\left(\begin{smallmatrix}3&2\\2&3\end{smallmatrix}\right)$ for equal loose values, and $L_0L_1+L_1L_0=\left(\begin{smallmatrix}2&2\\2&2\end{smallmatrix}\right)$ for different loose values. Their eigenvalues on the same two vectors are $(5,1)$ and $(4,0)$. Closing the ring takes the trace of the product, giving the formula and $9^k+1$ allowed states in total.

Removing a law replaces its two fixed-loose matrices by the all-ones matrix $J$. For a reader with one law removed, either value gives $J(L_0+L_1)=3J$, or its transpose. With both laws removed it gives $2J^2=4J$. Any such replacement vanishes on the second eigenvector. The remaining count factors into one function per reader, proving independence for **every proper subset of the source laws**. The complete truth tables verified all 63 proper subsets at six knots. At eight knots all 16 counts matched, totaling 6,562, and one law deletion gave independence. [Source counts and controls](weight_tables.json)

The extra completion at the all-zero reading gives a $k$-way interaction. Divide the product of the counts at even reader words by the product at odd words. Any positive weight that factors over proper subsets gives ratio 1, since every factor occurs equally often in both products. Here the ratio is $1+5^{-k}$. A marginal on $j$ readers has counts $9^{k-j}5^{j-t}4^t+\mathbf1_{t=0}$. Consequently lower-order dependence also occurs. For three readers the three-way ratio is 126/125 and each two-reader ratio is 226/225. Among the 4- and 6-knot sources, every one of the six possible local states at every knot admits both values of each reader. [Marginals and local reads](weight_tables.json)

## Growth and controls

| Ring and readers | Source counts | After one ordinary round | After two ordinary rounds |
| --- | --- | --- | --- |
| Four knots, two readers | 26, 20, 20, 16 | 62, 40, 40, 52 | 558, 360, 360, 468 |
| Six knots, three readers | 126, 100, 100, 80, 100, 80, 80, 64 | 396, 296, 296, 264, 296, 264, 264, 244 | Nine times the preceding column |

Each round-one birth takes the original loose distinctions at alternating knots and makes one fresh distinction. The counts for the two fresh distinctions together are 51, 46, 46, 51 on the four-knot start, and 588, 572, 572, 588 on the six-knot start. Round two adds two single-parent births, each with three completions per old state. On both starts, one fresh distinction from each round-two birth still shows dependence. Reading each birth's two fresh distinctions by their parity gives independence. A single law deletion in either grown stage retains dependence between the original readers. The every-proper-subset result applies to the source. [Growth stages](weight_tables.json) · [Independent growth definitions](growth_rule.py)

As a control with exactly independent proper reader marginals, take three separate three-place knots. From each use two distinct places, $a_i,b_i$, and read three parities on the disjoint pairs $(a_i,b_{i-1})$ around the three indices. Each pair of readers has counts 54, 54, 54, 54. Each even triple has 26 completions and each odd triple 28. All seven proper subsets of the three laws give independent readings. The carrier assignment spans separate knots. This control measures what a supplied grouping can produce even without a connected meeting pattern. [Control table](weight_tables.json)

## Claims in the consultation

- The ring-of-four parity has 50 even and 32 odd states on the four **shared** distinctions. Its four **loose** distinctions give 42 and 40. Removing one knot while retaining all distinctions gives 60 and 48 on the shared ones, and 54 and 54 on the loose ones. The original 50 alone therefore fails the law-removal test for a bias held by the whole.
- The statement that flip-invariant functions on disjoint sets of knots on a tree are independent needs connected carrier sets. In a four-knot chain with a loose sign $z_i$ at each knot, take $A=z_1z_3$, $B=z_2z_4$. Both have mean $-1/27$ and $AB$ has mean $1/81$, while independent readings predict $1/729$. The consecutive grouping $z_1z_2,z_3z_4$ gives independence. More generally, root a tree and fix one reference sign. At each knot the relative values of its other places to its incoming sign range freely over every pattern except all equal to that sign. Those choices count independently and flipping the entire system changes only the reference sign. A flip-invariant reading on a connected group uses only that group's relative choices. A flip-invariant reading spanning separated knots can use choices between them. Either value of any reference distinction distinguishes the two globally flipped representatives of a relative state.
- The normalized product means $-15/41,-33/95,-3/13$ in the earlier signed-count study reproduce. A simple-route reading needs a further term when a knot uses four selected places. For knots $(0,1,3,4),(1,2,5),(2,0,6)$, the product of the loose signs 3 and 4 has mean $-5/31$, from 26 equal and 36 different. The only simple route uses the first knot, contributing $-1/7$. Dividing this by the ring normalizer $62/63$ would give $-9/62$. Selecting all four places there and both ring places at each other knot adds $-1/63$ to the numerator. In general expand each knot over its even subsets, giving weight 1 to the empty choice and $-1/(2^{a-1}-1)$ to any nonempty even choice at a knot of $a$ places. Sum products for choices whose symmetric difference is exactly the measured pair and divide by the corresponding empty-difference sum. This counts any size of even choice at a knot once. [Direct counts and expansion](weight_tables.json) · [Earlier counts](../../SIGNED-COUNT-20261126-001/referee-R1/report.md)

## Reproduction and limits

From the repository root, the same single process and two-GiB address-space cap apply to both commands. The pilot timed the actual four- and six-knot configurations and a 1,024-assignment prefix per eight-knot roster. This put the full work below ten seconds. The recorded run finished in about 1.1 seconds at under 16 MiB peak resident memory. All reported counts use exact integers. [Pilot](weight_pilot.json) · [Counting script](weight_counts.py)

```sh
r=research/NAE-LAYER-20261127-001/referee-R1
ulimit -v 2097152
.venv/bin/python -B "$r/weight_counts.py" --pilot --output "$r/weight_pilot.json"
.venv/bin/python -B "$r/weight_counts.py" --output "$r/weight_tables.json"
```

Later growth rounds, growth from the eight-knot source, and a census of other weightings or carrier definitions were not run. No iteration of a new law follows from the counts.
