# Exactly what a positive-implication prefix must preserve

Status: Proved

## Standard statement

A prefix is a finite conjunction of Boolean implications $u\to v$, with a source $s$ fixed true and a sink $t$ fixed false. A unit $x$ can be written $s\to x$, and $\neg x$ as $x\to t$. Let $B$ consist of $w$ distinct labelled boundary variables, all distinct from $s,t$. A continuation may use those names, the two fixed constants and its own private variables. The prefix's private variables are forgotten. Two prefixes are continuation-equivalent when adjoining any allowed continuation gives the same SAT answer for both.

The exact invariant is the set of feasible assignments on $B$. It is either empty or uniquely specified by the forced-true names, the forced-false names and a preorder on the remaining neutral names. A preorder is reflexive and transitive, and can relate two distinct names in both directions. Every such invariant is realized. If $Q(n)$ counts preorders on $n$ labelled names, including $Q(0)=1$, the number of distinct continuation classes is

\[
N(w)=1+\sum_{n=0}^w \binom wn\,2^{w-n}Q(n).
\]

For $w\ge1$, the unique indispensable questions in the fixed menu of pin-only continuations with at most one true pin and at most one false pin are **all $2w$ single pins and all $w(w-1)$ ordered opposite-valued pins on distinct names**. Their $w(w+1)$ answers distinguish every class. Omitting any one loses a distinction even when every other elementary question, including the question with no pins, is available. At width zero the empty continuation alone separates the two classes.

| Boundary names $w$ | 0 | 1 | 2 | 3 | 4 | 5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Labelled preorders $Q(w)$ | 1 | 1 | 4 | 29 | 355 | 6,942 |
| Continuation classes $N(w)$ | 2 | 4 | 13 | 74 | 732 | 12,085 |
| Indispensable elementary questions | 1 | 2 | 6 | 12 | 20 | 30 |

## Nearest known result

The family count is classical. It counts families of subsets of a labelled set closed under binary union and intersection, including the empty family. The nonempty cases are the sublattices of the Boolean lattice, in the literature's terminology. OEIS A306445 records the values and the equivalent topologies formula, with a reference to Stanley, *Enumerative Combinatorics*, vol. 1, exercise 3.46. The correspondence with preorders also occurs in Siggers's more general representation of sublattices of products of chains. [OEIS A306445](https://oeis.org/A306445/internal) · [Siggers](https://arxiv.org/abs/1412.0011)

The positive-implication decision uses classical directed reachability, a special case of Horn satisfiability. The preceding route result applies it to shared middle variables. Here we identify exactly which boundary assignments any continuation can distinguish and give a separate minimality witness for every question in the stated elementary menu. [Dowling and Gallier](https://doi.org/10.1016/0743-1066(84)90014-1) · [Joined-route synthesis](../../UNSIGNED-ROUTE-JOINS-20261115-001Z/UNSIGNED-ROUTE-JOINS-20261115-001Z-P001_synthesis/proof.md)

## Projection and continuation

Write $R_P$ for the feasible boundary assignments of prefix $P$. A prefix $P$ and continuation $C$ are jointly satisfiable exactly when $R_P\cap R_C$ contains an assignment. A joint model gives this assignment. Conversely, two model witnesses that agree there can be combined, since all other shared names have fixed values and the two private sets are disjoint. If two projected relations differ, choose one assignment in their symmetric difference and pin every boundary bit to it. The resulting continuation separates the prefixes. This proves both directions of continuation equivalence.

In the usual directed graph of the implications, $s$ reaching $t$ is exactly the case $R_P=\varnothing$. If $t$ is unreachable from $s$, setting just the names reachable from $s$ true satisfies the prefix. Define $T$ as the boundary names reachable from $s$, and $F$ as those from which $t$ is reachable. These sets are disjoint. Every other name is neutral. The assignment just constructed makes each neutral name false. For a given neutral $i$, setting exactly the names reachable from $\{s,i\}$ true also satisfies the prefix and makes $i$ true.

On the neutral names write $i\preceq j$ when $j$ is reachable from $i$, counting a path of length zero. If a model makes $i$ true it makes $j$ true. Conversely, if $j$ is unreachable from neutral $i$, the preceding assignment from $\{s,i\}$ makes $i$ true and $j$ false. Thus the relation on neutrals is recoverable from the projected assignments themselves.

The full projection consists of $T\cup U$ for every upward-closed set $U$ of neutral names, writing an assignment as the set of names given value one. To extend it, set true precisely the names reachable from $\{s\}\cup U$. This leaves $t$ and all $F$ false, since a chosen starting name reaching $t$ would be forced false. Any neutral name newly reached from $U$ already belongs to $U$. All implications hold. In particular, taking $U$ empty or full recovers exactly $T$ and $F$ as the forced values.

Every proposed triple $(T,F,\preceq)$ has an immediate realization. Add $s\to i$ for $i\in T$, add $j\to t$ for $j\in F$, and add $i\to j$ for each required neutral implication. A direct $s\to t$ realizes the empty relation. Distinct triples give different forced values or different possible ordered assignments $i=1,j=0$. Choosing $n$ neutral labels, the values of the other $w-n$ labels, and their neutral preorder proves the displayed count. Any deterministic prefix summary that must answer every allowed continuation consequently has at least $N(w)$ possible states, and indexing the classes attains that cardinality.

For the connection to the known enumeration, the displayed family of true-name sets is closed under binary union and intersection. Conversely, take a nonempty family with these closure properties. Its intersection is $T$ and the complement of its union is $F$. Remove $T$ from every member and keep the neutral names. This gives a family containing the empty and full neutral sets. For each neutral $i$ intersect all its members containing $i$ to get $D_i$. Define $i\preceq j$ by $j\in D_i$. These are exactly the pairs for which membership of $i$ implies membership of $j$, so this relation is a preorder. Every upward-closed $U$ equals $\bigcup_{i\in U} D_i$, hence belongs to the family, including $U=\varnothing$. This proves the equivalence without using the external sequence as a premise.

## Which pin questions are indispensable

Use $+i$ for pinning $i$ true and $-i$ for pinning it false. A question asks whether the prefix and those pins have a common assignment. At width at least one, any nonempty relation answers yes to at least one of $+i,-i$ at each name. Thus the single pins detect the empty relation, and for a feasible relation they recover all forced signs. On neutral names, $i\preceq j$ holds exactly when $(+i,-j)$ answers no. These answers reconstruct the whole relation. Opposite pins on the same name always answer no. The no-pin answer is the disjunction of the two single-pin answers at any one name.

Each indispensable question has two explicit feasible prefixes that agree on every other elementary question.

| Question removed | First prefix | Second prefix | Why the other questions agree |
| --- | --- | --- | --- |
| $+i$ | Force every other name true, leave $i$ free | Also force $i$ false | A mixed question with $+i$ must request a false value at some already-true name, or pin $i$ both ways. All questions omitting $+i$ can use $i=0$ whenever they are feasible. |
| $-i$ | Force every other name false, leave $i$ free | Also force $i$ true | Complementing all values in the preceding two prefixes exchanges the polarities. |
| $(+i,-j)$, $i\ne j$ | Leave every name free | Add exactly $i\to j$ | Only a consistent partial assignment requiring both $i=1$ and $j=0$ prevents extension. In the elementary menu only this ordered pair does so. Its reverse remains feasible. |

At $w=0$, there is one empty tuple. The empty prefix allows it, and $s\to t$ excludes it. With no boundary pins available the no-pin query is indispensable. These menu counts concern a fixed list of elementary pin questions with separately observable yes/no answers.

## Finite checks and scope

Run the checker from this directory. It uses the Python standard library and prints a JSON object with the calculated counts.

~~~sh
python3 -B check.py
~~~

Through width five the checker generates every conjunction of boundary pins and implications by intersecting their literal truth tables, retaining each distinct result. Independently it constructs every labelled preorder by adding a name to a smaller preorder, then enumerates its upward-closed sets and adjoins all possible forced pins. The resulting sets of projected truth tables agree exactly. Through width four it also inspects every Boolean relation, including all 65,536 candidates at width four, and selects those closed under both coordinatewise operations.

Every menu report and each single-question deletion is checked on all the resulting profiles through width five. Among the 732 width-four profiles, omitting any one single pin gives only 687 distinct reports. Omitting any ordered mixed pair gives 616. At width five the corresponding counts are 11,585 and 10,247 out of 12,085 distinct complete reports.

For every ordered pair of prefix and continuation classes through width four, the checker compares existence of a common literal assignment with direct reachability after conjoining their canonical realizations. This gives 541,489 comparisons, and 8,192 further sampled pairs at width five. It also directly projects the literal assignments of all 8,192 implication graphs on two boundary and one private name with possible positive and negative pins and the direct contradiction, omitting tautological implications. At five boundary and three private names it checks 240 further graphs. These latter finite checks exercise actual forgetting before the continuation arrives.

The assumption about the prefix class matters already at width two. The relation $x_1\lor x_2$ and the unconstrained relation give the same six elementary answers. Pinning both names false separates them. Width one realizes every Boolean relation. At width three, even parity agrees with the unconstrained relation on all 12 elementary questions and excludes the all-true assignment. The checker exercises both controls and every question-deletion witness. The counting and minimality theorems hold at every width by the constructions above. [Executable checker](check.py) · [Recomputed counts](checks.json)
