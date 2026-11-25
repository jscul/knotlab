# The roster at one round of the mutually sharing start

## Standard statement

Let $m\ge3$ knots each hold two loose distinctions and share one further distinction with each of the other $m-1$ knots, a different distinction for each pair. Under the ordinary complete-round law, the roster after round $t\ge1$ consists of the ordered sums of $t-1$ in $m$ nonnegative terms and $m$ additional offshoots. Two sums are one witnessed step apart precisely when one unit moves between two terms. Offshoot $i$ is one step from just the sum with all units in term $i$. At $t=1$ all these sums name the same member.

The greatest count within $r$ witnessed steps agrees with the unrestricted count exactly when $mr\le t-1$. A sum whose terms differ by at most one attains the greatest count at every $r$, including after this range. The same roster arises from thirteen of the twenty-three starts specified by the earlier probe. A cap of $c$ fresh distinctions keeps this roster for all rounds exactly when $c\ge m$ among the laws considered below.

## Nearest known result

The proof of the fewest-count law identifies the knots through a round with down-closed sets in the descent order of the offshoots. Its crossed start has $m$ continuing chains. The proof for mutually sharing starts identifies the same continuation and gives degree $m$ for the count through round $t$. Here we identify the members at a single round, exhibit the witness for each step, prove when its finite counts equal the unrestricted ones, and determine the effect of short supply. The exploratory probe supplied the proposed roster and the selected starts. [Fresh-count theorem, §§1 and 4](../../FRESH-COUNT-20261118-001A/FRESH-COUNT-20261118-001A-P001_free_count/proof.md) · [Mutually sharing start, Proposition 4](../../FIRST-KNOT-20261118-001A/FIRST-KNOT-20261118-001A-P001_two_knots/proof.md) · [Exploratory roster probe](../../../research/KNOTS-WITHIN-REACH-20261125-001/checks/roster_probe/README.md)

The unrestricted step counts are classical. They are the coordination sequences of the literature's root lattices of type $A_{m-1}$. The proof below derives them from transfers. The finite-stage equality condition, the additional members, the start certificates and the capped growth all use the growth law. [Baake and Grimm, 1997](https://arxiv.org/abs/cond-mat/9706122)

## 1. The law and the starting condition

A member holds a usable loose distinction. A **witnessed step** between distinct members $u,v$ requires a knot $w$ that shares a distinction with each. A knot does not meet itself. The witness can be a knot that has spent all its loose distinctions.

A group of at least three is a maximal set of pairwise one-step members for which no one knot witnesses the whole set. Each one-step pair in no such group is also a group. A join takes one loose distinction from each member of its group. Each remaining usable distinction of a member makes a separate one-parent birth, an offshoot. A birth with $p$ inputs and demand $d$ receives $\max(d,3-p,1)$ fresh distinctions under the ordinary law. Demand counts the next groups containing that birth after all the births have received their inputs. A fresh cap $c$ replaces this number by its minimum with $c$. A parity rule implied by the old rules supplies no fresh distinction. In this proof every birth has fresh distinctions under either not-all-equal or parity, as shown in §5. The six laws compared here use release on cancelled groups, no fillers and no extra takes. [Definitions of the laws and roster](../../../research/KNOTS-WITHIN-REACH-20261125-001/claim.md) · [Rule implementation, including demand and closing](../../../experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/pm.py)

The following more general starting condition describes the thirteen census starts as well. Write $L$ for the start knots with at least one loose distinction, and $\ell_i$ for the loose count of knot $i$. Suppose that

1. $|L|\ge3$, every two members of $L$ meet a common start knot, and no start knot meets all of $L$.
2. Each live start knot has one or two loose distinctions. Exactly $m\ge3$ have two.
3. Each shared start distinction has two holders, and all start knots belong to one connected component of meetings.

Then $L$ itself is the only first group. It makes a knot $P_0$ taking one distinction from each live start knot. For each of the $m$ start knots $R_i$ with two loose distinctions there is also one offshoot $E_i$, taking its other distinction. A start knot with one loose distinction has only $P_0$ as a child. A start knot with none contributes no child. No start knot stays live. The only witnessed steps at this stage are $P_0,E_i$, with witness $R_i$. Indeed, the only older knot meeting $E_i$ is $R_i$, and its live children are precisely these two. The first-round demand of $P_0$ is $m$. Each $E_i$ has demand one and receives two fresh distinctions.

For the mutually sharing start, any pair has a third start knot as witness, and no start knot meets itself. This proves all three conditions. At **round zero** the witnessed relation on the $m$ start knots is complete. More generally it is complete on $L$ in every start satisfying condition 1. The formula using $t-1$ starts at round one. The lower bound $m=3$ is needed for the specified mutually sharing start. With $m=2$, its two three-place start knots meet each other but have no common witness. Their four first offshoots form two separate pairs. Each pair grows by the chain induction of §5 and has $t+1$ members at $t\ge1$. Thus even the first post-start round differs from the proposed $m=2$ roster, which would have three members in one part. At $m=1$ the specification would give a two-place rule, below the three-place minimum for a starting knot.

## 2. Which knots witness the steps

Write $s=t-1$ and let $e_i$ have one unit in term $i$ and zero elsewhere. We prove by induction that the roster at $t$ has one member $P_x$ for each $x\in\mathbb N^m$ with $\sum_i x_i=s$, and one newest offshoot $E_i$ in each of the $m$ chains. At successive rounds the names $E_i$ denote successive, distinct knots. The parent lists for a new sum $y$ of $s+1$ are

* all $P_{y-e_i}$ with $y_i>0$ when at least two terms are positive,
* $P_{s e_i}$ and the current $E_i$ when $y=(s+1)e_i$.

The next $E_i$ has the current $E_i$ as its only parent. The first description in §1 is the induction start at $s=0$.

Under these parent lists, two distinct sums at level $s\ge1$ have a common parent precisely when one transfers one unit to obtain the other. Such sums have the common parent indexed by their termwise minimum, whose terms sum to $s-1$. Each offshoot meets only its parent from the previous round. That parent has only two current children, the offshoot and $P_{s e_i}$. This gives the claimed extra witnessed step and all its witnesses. Every new knot takes only previously loose distinctions from its parents and all its other distinctions are fresh. Hence any knot witnessing a pair of new members must be one of their parents. This proves necessity of the listed steps.

We verify that the law produces exactly these parent lists on the next round. Represent $x$ by the size-$s$ set $I_x$ consisting of the first $x_i$ entries of chain $i$ for each $i$. A transfer pair of sums has size-$(s-1)$ intersection and size-$(s+1)$ union. Fix one such pair $A=C\cup\{a\}$, $B=C\cup\{b\}$. A third size-$s$ set one step from both either contains $C$, or equals $(C\setminus\{c\})\cup\{a,b\}$ for some $c\in C$. A further set of the first kind distinct from $A,B$ meets a set of the second kind in only $s-2$ entries. Thus a pairwise one-step set of at least three either has common predecessor $C$, which witnesses all of it, or is contained in the single union $A\cup B$.

The union is itself down-closed on the chains, so it indexes a sum $y$. Its size-$s$ predecessors are exactly the $I_{y-e_i}$ with $y_i>0$. Three distinct such predecessors have intersection of size $s-2$, hence have no common preceding sum. An earlier offshoot meets at most one current sum, so it cannot supply the missing witness. These predecessors therefore form exactly one group if their number is at least three. If there are two, their pair belongs to no group of three or more, since its union is fixed and has only two predecessors. It forms its own group. Each $E_i$ has only one member within a step, hence forms a group with $P_{s e_i}$ alone. At $s=0$ the groups are precisely the $m$ pairs proved in §1.

Every $P_x$ belongs to exactly $m$ groups, one for each $y=x+e_i$. It receives exactly $m$ fresh distinctions under the ordinary law, one per group. Each $E_i$ receives two because it has one parent and demand one. It uses one distinction for its group and one for its next offshoot. This proves both supply and the next parent lists. The argument determines demand from the new parent lists before using the fresh counts, as the law requires.

In terms of the crossed down-closed sets of the two earlier proofs, a round $t$ corresponds to size $m+s$. A member containing all $m$ original entries can take an independent initial segment of each continuing chain, with $s$ further entries in total. If it omits the original entry $i$, only chain $i$ can contribute further entries since every other chain requires that original entry. If it omits two original entries, no chain can contribute and its size is less than $m$. At size $m+s$ the single-omission case gives exactly one member per $i$, the newest $E_i$. Discarding these $m$ members would already give a wrong count in round one.

## 3. What one round contains

There is one part. Transfers take any ordered sum to any other, and each offshoot has its witnessed step to a sum. The number of members at $t\ge1$ is

$$
\binom{t+m-2}{m-1}+m .
$$

Every birth is a member in its birth round and spends its loose distinctions in the next. Therefore the number of knots made in rounds $1$ through $t$ is $\binom{t+m-1}{m}+mt$. Adding the start knots gives the count through all those rounds. This explains why the two counts have degrees $m-1$ and $m$.

For $s>0$, a sum with $k$ positive terms has $k(m-1)$ distinct transfer neighbours. It has one more neighbour if $k=1$. Every offshoot has one neighbour. The greatest number of other members one step away reaches $m(m-1)$ exactly when $s\ge m$. In particular, for $m=3$ and $t\ge2$ the three offshoots have one neighbour, the three single-term sums have three, the $3(t-2)$ two-term sums have four, and all three-term sums have six. At $t=1$ the single sum has $m$ neighbours and each of its $m$ offshoots has one.

For $r\ge0$ let $M_{m,s}(r)$ count the members within $r$ steps from a maximizing member, including that member. Define

$$
U_m(r)=\sum_{j=0}^{m-1}
 \binom{m-1}{j}\binom{m-1+j}{j}\binom{r}{j} .
$$

Then $M_{m,s}(r)=U_m(r)$ exactly when $mr\le s$, and $M_{m,s}(r)<U_m(r)$ when $mr>s$. In particular, $U_3(r)=3r^2+3r+1$ and $U_4(r)=(2r+1)(5r^2+5r+3)/3$. For every $r$ a sum with all terms differing by at most one attains the finite maximum. At $r=s-\lfloor s/m\rfloor+1$ it reaches the entire part for the first time. From any offshoot the count is $1+\binom{r+m-2}{m-1}$ for $0\le r\le t$, with the usual zero convention for too-small upper arguments. The other $m-1$ offshoots are first reached at $r=t+1$. The exact finite counts for every $m,t,r$, including the proof that balancing maximizes them even near the offshoots, are in the [count derivation](best_member_count.md).

## 4. A certificate for the census starts

The table is a direct transcription of the input distinctions. Name the original knots $A,B,C,D,E$ in their listed order, using only as many letters as the start has knots. Every pair of knots shares one distinct place except the pairs listed in the third column. Each group of digits gives the loose counts $\ell_A,\ell_B,\ldots$ in this order. The numbers before the parentheses identify rows in the original start file, indexed from zero. [Census input](../../../research/KNOTS-WITHIN-REACH-20261125-001A/census_starts.json) · [Selected starts](../../../research/KNOTS-WITHIN-REACH-20261125-001/checks/roster_probe/fast_starts.json)

| Original meeting pattern number | Knots | Pairs without a shared distinction | Census rows and loose counts |
| --- | ---: | --- | --- |
| 7 | 3 | None | 19 (222) |
| 17 | 4 | BD | 164 (1222), 172 (2122), 177 (2222), 178 (2223), 179 (2232) |
| 18 | 4 | None | 214 (1222), 218 (2222), 219 (2223) |
| 42 | 5 | AC, AD, BC, BD | 1350 (12221), 1382 (22231) |
| 46 | 5 | AB, AC, BC | 1964 (22233) |
| 47 | 5 | AC, AD, CE | 2086 (12122), 2216 (22201), 2218 (22203), 2231 (22312), 2236 (22323) |
| 49 | 5 | AC, BC | 2694 (02322), 2772 (12212) |
| 50 | 5 | AC, BD | 3075 (12221), 3077 (12223) |
| 51 | 5 | AC | 3195 (02222), 3288 (21222) |

In each of the nine meeting patterns, for every pair of knots $i,j$ there is a different knot meeting both. This is checked by deleting $i,j$ from the list of letters and the missing partners of either member from the remainder. For example, in pattern 42 any two of $A,B,C,D$ have witness $E$. Each pair involving $E$ has as witness the partner in $AB$ or $CD$. No live knot meets the entire live set because it misses itself. When there is a dead knot, it misses a live one too. In pattern 47 the dead $D$ misses $A$. In patterns 49 and 51 the dead $A$ misses $C$. Hence all 23 starts have one first group containing every live start knot. All their original meeting patterns are connected.

For a start with this single first group, each live knot makes exactly $\ell_i-1$ offshoots. They all have a witnessed step to $P_0$. Two of them have a step between themselves exactly when they come from the same start knot. Thus at round one the condition “$m$ offshoots each with only $P_0$ one step away” is equivalent to their positive counts per original knot being $m$ copies of one. This gives the following necessary and sufficient distinction **within the selected 23 starts**.

| Positive offshoot counts per start knot | Census rows | Consequence |
| --- | --- | --- |
| 1, 1, 1 | 19, 164, 172, 214, 1350, 2086, 2216, 2772, 3075 | The $m=3$ roster of §2 |
| 1, 1, 1, 1 | 177, 218, 3195, 3288 | The $m=4$ roster of §2 |
| 2, 1, 1, 1 | 178, 179, 219, 1382, 2218, 2231, 2694, 3077 | One original knot witnesses a pair of offshoots as well as their steps to $P_0$ |
| 2, 2, 1, 1, 1 | 1964, 2236 | Two original knots each witness such a pair |

The last two rows already differ at round one. Necessity here addresses the initial roster in this cohort. A different starting condition could give the same roster at some later round.

## 5. Which laws preserve the count

| Growth law in the probe | When the unit-transfer roster persists through every round |
| --- | --- |
| Ordinary law with a stall on short supply (L0), ordinary law with retiring (L9) | Every $m\ge3$ |
| Cap of four with retiring (L11) | $m=3,4$ |
| Cap of three with waiting (L1), retiring (L6), or making offshoots (L7) | $m=3$ |

The demands and ordinary fresh supplies in §2 are $m,m$ at each sum and $1,2$ at each newest offshoot. Thus any listed cap at least $m$ never changes a birth, and no member runs short. In particular the nine starts keep their roster under all six laws, and the four keep it under the two ordinary laws and the cap of four. The first-round roster itself also exists when the cap is lower.

When $c<m$, the first-round $P_0$ holds $c$ fresh distinctions and owes $m$ groups. It first runs short in **round two**. Every group then contains $P_0$ and one $E_i$, so all $m$ are cancelled. Each $E_i$ can pay its original demand. Under release, both of its loose distinctions make separate offshoots. These two new members share witness $E_i$, and no other parent witnesses one of them. This starts $m$ separate parts.

In each such part the roster at $t=2$ consists of two consecutive members. Suppose a part has $n\ge2$ members in a chain. Its only groups are the $n-1$ consecutive pairs. The two end members are single-parent offshoots with demand one and fresh supply two. Every member between them has two parents, demand two and fresh supply two. The next roster contains the $n-1$ pair joins and one offshoot at each end. Two new members have a witness exactly when they are consecutive in this new chain of $n+1$ members, each old member witnessing its two children. This proves the induction, including the fresh supplies, with $n=t$ at round $t\ge2$. Its greatest count within $r$ steps is $\min(2r+1,t)$.

Retiring bars all the loose distinctions of $P_0$. This gives exactly the $m$ parts just described, for a cap of three or four below $m$. Under the two remaining laws with cap three, $P_0$ contributes one further part as follows.

| Treatment of $P_0$ | Members of the extra part after round $t\ge2$ |
| --- | --- |
| Make offshoots | Three pairwise one-step members at $t=2,3$. One member at $t=4,5$. A chain of $t-4$ members for $t\ge6$. |
| Wait | $P_0$ alone at $t=2$. Three pairwise one-step members at $t=3,4$. One member at $t=5,6$. A chain of $t-5$ members for $t\ge7$. |

Indeed, making offshoots spends the three distinctions on three siblings. They have a common parent, so their groups are the three pairs. The resulting three pair joins each meet the other two through different parents. They make one join with three inputs. Its demand is zero and it receives one fresh distinction. The resulting single offshoot has demand zero, receives two fresh distinctions and makes two siblings, beginning the chain just proved. With waiting, $P_0$ keeps all three distinctions at $t=2$. Its neighbours are still its start parents. Each member in one of the other parts meets only its own $E_i$, so $P_0$ is now isolated on the roster. It pays no groups in round three and makes three offshoots, delaying the same sequence by one round. Once only new members are live, every witness between them must be a parent of both. Members born from disjoint parts have disjoint parents, so the parts stay separate thereafter.

For each extra part as well, the best count is $\min(2r+1,\text{number of members in the part})$. The two transient groups of three members are pairwise one step apart. Their count starts $1,3,3,\ldots$ even though those three members do not yet form a chain. This distinguishes the count from the full witnessed relation. For the four census starts with $m=4$, retiring gives four parts and waiting or making offshoots gives five, from round two on. The untruncated $2r+1$ applies exactly while $2r+1$ fits in the part.

Finally, for even parity, a sum of older equations contains a shared distinction precisely when it uses one of the two holders and omits the other. A sum containing only loose distinctions must therefore use whole connected components of knot meetings. In the connected component that grows here its only such nonempty sum contains **all** its loose distinctions. This counts barred loose distinctions as well. Every birth in the descriptions above takes a nonempty proper subset of that component's loose distinctions at the start of its round. Other births use other loose distinctions, including births in the $m$ continuing parts after a split. None of these parity rules is implied. This proves that parity and not-all-equal give the same rosters throughout all the cases claimed. The argument proves the roster incidence under the stated laws. The allowed-state knot test on particular stages is a separate check in the epic.

## Evidence and scope

This is an inherited consequence and a uniform-family theorem for the specified growth law, with a finite input classification for the 23 selected rows. The cap supplies an explicit alternative law. The initial sample, complete rounds, treatment and witnessed-step reading are supplied choices. The unrestricted count is classical. The new inference connects a finite round of this growth to that count with an exact cutoff. The symbolic derivation uses no fitted counts. Numerical reproduction and allowed-state evidence have their own records. No physical or bond-distance conclusion is used.
