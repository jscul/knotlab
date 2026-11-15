# Exact messages for simultaneous ternary crossing tests

Status: Proved

## Standard statement

Fix an integer $b\ge 1$. One ternary pair has state $s=(a,d)\in\mathbb F_3^2$, with original strand values $a,a+d$. The crossing sends these to $a+d,a+2d$. Iteration leaves $d$ fixed and allows the one-strand test $a+kd=t$ for every $q=(k,t)\in\mathbb F_3^2$. With $b$ indexed pairs, the input is an arbitrary set $S\subseteq (\mathbb F_3^2)^b$. For every future $q=((k_1,t_1),\ldots,(k_b,t_b))$, the required answer is

$$
 h_S(q)=[\exists ((a_1,d_1),\ldots,(a_b,d_b))\in S\quad
              \forall i,\ a_i+k_i d_i=t_i].
$$

The sender knows $S$ and sends one fixed-length binary message before learning $q$. A deterministic receiver knows $q$ and must answer correctly for every $S,q$. Both sides may compute without a time or space restriction. Let $M_b$ be the minimum message length in bits. Then

$$
 \max\left\{5^b,\ 3^b\binom{b}{\lfloor b/2\rfloor}\right\}
 \ \le M_b \le
 \min\{9^b,\; 6^b\lceil\log_2(9^b+1)\rceil\},
 \qquad
 \lim_{b\to\infty} M_b^{1/b}=6.
$$

The bounds apply to all deterministic encodings, including encodings that send no state identifiers. With the additional promise $S=S_1\times\cdots\times S_b$, the exact optimum is $\lceil\log_2(1+109^b)\rceil$ bits.

## From states to distinct answer profiles

Write $A_{(k,t),(a,d)}=[a+kd=t]$ for the $9\times9$ incidence matrix. The row of $A^{\otimes b}$ for $q$ has a one at $s$ precisely when the same state $s$ passes all $b$ tests. The profile $h_S$ is the Boolean union of the columns indexed by $S$, with the empty union equal to zero. Let $N_b$ count the distinct profiles. Two different profiles disagree at some query and must have different messages. Conversely one can agree on an ordering of all profiles and send the index of $h_S$. Hence $M_b=\lceil\log_2 N_b\rceil$. This counting step transfers a lower bound on distinguishable profiles to every encoding in the stated model.

## Six independent evaluations and a short description of each profile

Over $\mathbb F_3$ the equality indicator is $1-(a+kd-t)^2$. As a function of $a,d$, every row therefore lies in the span of $1,a,d,a^2,ad,d^2$. Its rank is at most six. Tensoring the row spans gives $\operatorname{rank}_{\mathbb F_3}(A^{\otimes b})\le 6^b$.

For each $S$, select an inclusion-minimal subset $R\subseteq S$ that generates the same profile. For every $s\in R$ there is a private query accepting $s$ and no other member of $R$, since otherwise removing $s$ would preserve the profile. These queries are distinct and their evaluations on $R$ form an identity matrix. Thus $R$ has at most $6^b$ members. Nonuniqueness of $R$ poses no problem. The sender can choose the first eligible $R$ in a fixed order. A list of $6^b$ slots with state identifiers from $1$ to $9^b$ and zero for padding describes $R$. Alternatively, the sender can transmit the $9^b$ incidence bits of $S$. Taking the shorter option gives the displayed upper bound.

## Private queries in the simultaneous reader

Use the following six distinct states and six distinct queries in the listed order. Levels label the two groups used in the proof.

| Index | Level | State $(a,d)$ | Query $(k,t)$ |
| --- | --- | --- | --- |
| 1 | 0 | $(1,0)$ | $(2,1)$ |
| 2 | 0 | $(2,2)$ | $(0,2)$ |
| 3 | 0 | $(1,1)$ | $(1,2)$ |
| 4 | 1 | $(0,0)$ | $(2,0)$ |
| 5 | 1 | $(1,2)$ | $(0,1)$ |
| 6 | 1 | $(0,1)$ | $(1,1)$ |

Substitution in $a+kd=t$ gives the displayed $A$-submatrix with query rows and state columns.

    1 0 0  0 0 0
    0 1 0  0 0 0
    0 0 1  0 0 0
    0 1 1  1 0 0
    1 0 1  0 1 0
    1 1 0  0 0 1

It has ones on the diagonal and zeros above it, so the one-pair rank is exactly six. Its tensor power also contains a triangular minor of size $6^b$ and its rank is exactly $6^b$. Two additional properties give more private queries at finite $b$. An accepted state letter has level at most that of the query letter. At equal levels acceptance forces their indices to agree.

Take all length-$b$ words in the six indices with exactly $j=\lfloor b/2\rfloor$ level-one positions. Each word $w$ determines a state $s_w$ and a query $q_w$. Both maps are injective coordinate by coordinate. If $q_w$ accepts $s_v$, the level-one positions of $v$ are a subset of those of $w$. Both sets have size $j$, so they coincide. The equal-level rule now gives $v=w$, and the diagonal verifies that $q_w$ accepts $s_w$. The resulting identity minor has $L_b=\binom bj3^b$ entries on its diagonal. Every subset of these $L_b$ states gives a different answer profile, as $q_w$ reads the membership bit of $s_w$. Thus $N_b\ge 2^{L_b}$ and $M_b\ge L_b$.

The central binomial coefficient is largest and at least $2^b/(b+1)$. The bounds on $M_b$ now give base six by taking $b$th roots. More precisely Stirling's formula gives $L_b\sim 6^b\sqrt{2/(\pi b)}$.

Direct enumeration of the 512 one-pair tables gives at most five states with simultaneous private queries in one pair. For example, $(0,0),(0,1),(0,2),(1,0),(2,1)$ have respective private queries $(2,0),(2,2),(1,2),(0,1),(0,2)$. Repeating the five choices in each coordinate gives an identity minor of size $5^b$. Each of its $2^{5^b}$ subsets is an allowed input under the arbitrary-table assumption. At $b=8$, the two-level construction gives 459,270 private states, exceeding the 390,625 from independent repetition. The exact optimum $M_b$ at general finite $b$ remains open here.

## Product tables, input size, and query order

For $S=\prod_i S_i$, let $U_i=\{q_i:h_{S_i}(q_i)=1\}$. Now one may take any independently chosen witnesses $s_i\in S_i$ together, so the accepted query tuples form $\prod_i U_i$. The table with no states gives one zero profile. Every nonempty product determines each $U_i$ by projection. In one pair the checker exhausts all $2^9=512$ tables and finds $110$ distinct profiles, $109$ nonempty. This finite count can be reproduced by starting with the singleton collection containing the empty query set and, for each of the nine states, adjoining the union of its three accepted queries with every set currently in the collection. Consequently exactly $1+109^b$ profiles occur on product tables.

For a matched control put $u=(0,0)$, $v=(1,0)$. The joint tables $\{(u,u),(v,v)\}$ and $\{(u,v),(v,u)\}$ have the same two projections. The simultaneous query $((0,0),(0,0))$ accepts the first table and rejects the second. Replacing each table with the product of its projections would lose this answer.

An explicit bit table has $n=9^b$ input bits, which is also an immediate message ceiling. In these units the result reads $M_b=n^{\log_9 6+o(1)}$. If the receiver may first send the query, it costs $\lceil\log_2(9^b)\rceil$ bits to name it and one bit for the sender to return its answer. With eight pairs this is 27 communicated bits. On an explicit table with indexed membership, the sender can enumerate the $3^b$ difference tuples and use $a_i=t_i-k_i d_i$ to test the compatible states. These comparisons separate the cost of storing answers to *every future query* from the time to answer a specified query. The theorem gives no lower bound on the running time of arbitrary solvers for formula-only SAT.

## Nearest known result

Bui-Xuan, Telle and Vatshelle define the Boolean cut value as the base-two logarithm of the number of distinct unions of neighborhoods across a given bipartition. Applied to the states and queries, this is $\log_2 N_b$. Rabinovich, Telle and Vatshelle relate this value to the largest induced matching. With $n$ state columns and largest identity-minor size $m$, the elementary counting bounds are $2^m\le N\le\sum_{j=0}^m\binom nj$. The lower bound uses all subsets of the minor, and the upper bound counts minimal representatives. [Bui-Xuan, Telle and Vatshelle, Definition 5](https://arxiv.org/pdf/0903.4796) · [Rabinovich, Telle and Vatshelle, IPEC 2013, Lemma 1](https://www.ii.uib.no/~martinv/Papers/RTV13.pdf)

Groenland, Mannens, Nederlof, Piecyk and Rzążewski identify private queries of minimal representatives with permutation submatrices and prove that a triangular matching of size $r$ gives asymptotic induced-matching base at least $r$ in tensor powers. Their paper uses the terms *induced matching* and *half-induced matching* for these two certificates. With the rank bound, their results already supply the general mechanism behind the base. The local calculation here identifies six for this particular crossing reader, gives its two-level finite certificate and distinguishes arbitrary joint inputs from product inputs. The argument above is self-contained and makes no external priority claim for the matrix value or certificate. [Groenland et al., ICALP 2024, Theorem 6 and Lemma 11](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2024.77)

The companion [checker](check.py) verifies the finite certificates and controls directly against ternary crossing evaluations.
