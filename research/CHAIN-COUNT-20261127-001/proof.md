# The chain counting on node cores: a proof on a class read off the start

> **Referee report R1, 27 November 2026: confirmed with fixes — no Block on the theorem under N1 to N3 (with a relay
> correction); Block on dropping N2, on Lemma D as stated (it needs N2), and on Lemma C's pair clause (repaired)**
> ([the report](referee-R1/report.md)). The referee rebuilt the node core and extended nodes independently and found all
> 100 in-class growth comparisons of a fresh sample and all 19 on built starts agree, and all out-of-class ones differ.
> - **N1 alone does not suffice.** A 13-knot start meets N1 and N3 but fails N2: the last core node's two parents both hold
>   both chain bases, and their two common parents hold one base each. Growth makes two three-parent joins where the
>   reading makes one four-parent join, and two births get three fresh distinctions where the reading gives two (round 9,
>   both laws). The cycle study's referee found the same with a nine-knot start. So failed lifts are a second
>   obstruction beside chained twins; whether N1 implies N3 is still open (the referee reduces N3 to a triple test).
> - **Repairs.** Lemma C's pair clause omitted a neighbour one chain total below (repaired: every family holding the pair
>   still has the pair's common parent); Lemma D needs N2; the class is connected, with a loose distinction, and two for
>   parity (a lone offshoot under parity closes); a relaying terminal birth gets f + 1 = 1 fresh distinction; N2 is for
>   distinct parents and nonempty B; 26 sample rows passed the cap, not 2. Read this record with these changes.

Status: **Proved on a class whose conditions are read off the start** (N1 to N3 below), refereed with fixes; N1 alone
does not imply N2 (referee R1), and whether it implies N3 is open. Referee pending. Epic `CHAIN-COUNT-20261127-001`, 27 November 2026, at the coordinator's sequenced pick after
`CYCLE-READ-20261127-001`. The advisor could not be consulted on the proof (its usage limit was reached); the
independent check is the machine check below and the referee.

The node reading (`GRADED-ORDER-20261126-001`, `CYCLE-READ-20261127-001`) was computed to read ordinary growth exactly on
every start without chained twins it was run on. Referee R2 of the graded-order study proved its core part (the core's
groups) and left the chain counting open. This note proves the chain counting, and with it the whole reading, on starts
that satisfy three conditions read off the start's node core without growing, and checks that all 793 sample starts
without chained twins satisfy them.

## Setting

A connected start of the late-views class (`LATE-VIEWS-20261126-001`, `late.py`: no shortage, distinctions held at most
twice) with at least one loose distinction, and two under parity *(added after R1)*,
grown by ordinary growth (the look-alike study's growth; Lemma R of `REDUCE-BLOCKS-20261119-001A`). Each piece is read
apart; pieces are those whose node core finishes.

- **The node core.** Rank 0: the live knots. Rank 1: the round-1 groups (sets of live knots) and one offshoot
  O_q = {w, q} for each pendant point q of a live knot w (its loose distinctions left after its groups). Rank r + 1: one
  node for each group (a maximal family of three or more rank-r nodes that pairwise share a parent and share none in
  common) and each uncovered pair (two rank-r nodes sharing a parent, inside no group), its parents that family. A
  node's points are the union of its parents' points. The core finishes when a rank has no node after it.
- **Chains.** A pendant point q of w carries R(open_w) endless chains: 0 if open_w ≥ 3, 1 if 2, 2 if 1
  (`CHAIN-IDENT-20261119-001A`). Its base is q.
- **Extended nodes.** x = (C, a): C a core node of rank ≥ 1 and a a vector of lengths a_e ≥ 1 on a set E(a) of chains
  whose bases are points of C (B(a) is the set of those bases). Its round is |x| = rank(C) + Σ a_e. It is **pure** when
  E(a) is empty (a core node).
- **Its parents** P(x): the **shortenings** x − e for e in E(a) (a_e lowered by one, the chain dropped at length 1), and
  the **lifts** (T, a) for each core parent T of C whose points hold B(a) (for rank(C) = 1 and a = 0 the parents are
  knots).
- **The reading.** x holds f(x) = (number of core children of C) + (number of chains based at points of C) fresh
  distinctions. A finished piece without chains has one last node, holding the whole piece, which relays as in
  `RELAY-IDENT-20261119-001A` (proved for this reading by referee R2).

**The conditions.**
- **(N1) No chained twins:** no two core nodes of one rank share two parents C and D with a chain base in the points of a
  common parent of C and D.
- **(N2) Lifts meet:** any two distinct core parents T, T′ of one core node that both hold a nonempty set B of chain
  bases share a core parent holding B.
- **(N3) Base-holding families close:** every maximal family of three or more core nodes of one rank that hold a set B of
  chain bases and pairwise share a core parent holding B has a common core parent holding B, or a common core child.

## Theorem

On a start of the class whose node core satisfies N1 to N3, for every round t ≥ 1 there is a bijection from ordinary
growth's births of round t to the extended nodes of round t under which each birth's parents are P(x) and its fresh
count is f(x), except that a terminal birth that relays gets f(x) + 1 = 1 *(corrected after R1)*, together with the
relay births of finished pieces without chains. So `late.py`'s binomial terms on the
node core give every round's births by kind, both readings, both knot laws.

## Lemma A (how two extended nodes of one round share a parent)

Two distinct extended nodes x = (C, a), x′ = (C′, a′) of round t share a parent exactly in one of three ways:
- **(S1)** C = C′ and a′ = a − δ_e + δ_e′ for chains e ≠ e′; the shared parent is (C, a − δ_e).
- **(S2)** C is a core parent of C′, a′ = a − δ_e, and C holds B(a); the shared parent is (C, a − δ_e).
- **(S3)** a = a′ and C, C′ share a core parent U holding B(a); the shared parent is (U, a).

*Proof.* A parent of x is x shortened (same core, a − δ_e) or lifted (a core parent of C, same a). Match the two kinds
in the four combinations; the vector and the core determine the rest. ∎

So in a family that pairwise shares, the chain totals Σ a_e take at most two consecutive values, and within one total
the family lies in one core (S1 throughout) or in one vector (S3 throughout): if x, x′ share a core and x′, x″ share a
vector, x and x″ differ in both and share nothing.

## Lemma B (the pure part; referee R2's argument on extended nodes)

Under N1, no group of round-t extended nodes holds two pure members and a non-pure one. Hence the groups and uncovered
pairs made only of pure nodes are those of the node core.

*Proof.* A non-pure node has at most one pure parent: C itself, when x = (C, e at length 1). Let a group hold pure A and
B and a non-pure member. A non-pure member shares a parent with A, and A's parents are pure, so its one pure parent is a parent of A and of B.
If every non-pure member had the same pure parent C, every member would have C as a parent (a pure member shares a parent
with a non-pure one only through that one's pure parent), and the group would have a common parent. So two non-pure
members (C, e:1) and (D, e′:1) have distinct pure parents C, D, both parents of A and B, and they share a non-pure parent.
The non-pure parents of (C, e:1) are (F, e:1) with F a core parent of C holding base(e), so the shared one is (F, e:1)
with e = e′ and F a common core parent of C and D holding a chain base: chained twins, against N1. A pure group therefore
stays a maximal family without a common parent (a non-pure node that shared with all its members would make a group, or
a family with a common parent, holding two pure members), and a pure uncovered pair stays uncovered. ∎

## Lemma C (each P(y) is a group or an uncovered pair)

Let y = (D, b) be non-pure with |P(y)| ≥ 2. Then P(y) pairwise shares, has no common parent when it has three members or
more, is a maximal family that pairwise shares, and, when it has two members, lies in no group.

*Proof.*
1. **It pairwise shares.** Two shortenings y − e, y − e′ share y − e − e′. A shortening y − e and a lift (T, b) share
   (T, b − δ_e). Two lifts (T, b), (T′, b) share exactly when T and T′ share a core parent holding B(b), which is N2.
2. **No common parent** (three members or more). Two shortenings have only y − e − e′ in common, which no third
   shortening and no lift has as a parent. A shortening and a lift (T, b) have only (T, b − δ_e) in common, which depends
   on T. So with |E(b)| ≥ 3, with |E(b)| = 2 and a lift, or with |E(b)| = 1 and two lifts, nothing is common.
3. **Maximal.** Let w share with every member and not be one. By Lemma A, w has the chain total of the shortenings or of
   the lifts.
   - *With the shortenings' total.* If w has core D, sharing with a lift forces w = (D, b − δ_f), a shortening. With no
     lift and |E(b)| ≥ 3, sharing with three shortenings forces the same. With no lift and |E(b)| = 2, w = (D, c + δ_g)
     with c = b − δ_e − δ_e′, and every such w has the common parent (D, c). If w has another core D′, it has a shortening's
     vector b − δ_e, so |E(b)| = 1; sharing with every lift (T, b) makes D′ a core child of each T. With two lifts, D and D′
     share the two parents T, T′, which by N2 share a parent holding B(b), a chain base: chained twins, against N1. With
     one lift T, both members and every such w have the parent (T, b − δ_e).
   - *With the lifts' total.* w = (T′, v) with T′ a core parent of D and v = b − δ_e + δ_f for each shortening y − e. With
     |E(b)| ≥ 2 this forces v = b, so w is a lift. With |E(b)| = 1 and two lifts, w would share a core with both: none.
     With one lift T, w = (T, b − δ_e + δ_f), which has the common parent (T, b − δ_e) with the pair.
   So with three members or more P(y) is maximal; with two, every family holding it has a common parent, so no group
   holds it. ∎

   *[Repaired after R1.]* The case list above omits a neighbour one chain total below the shortenings, (D′, v) with D′ a
   core child of D: it exists only when |E(b)| = 2, with v = b − δ_e − δ_h, and it has the pair's common parent (D, v).
   With several extra members, every family holding the pair lies on one side of its unique shared parent and unique
   proposed child (N1 excludes the one crossing), so it keeps the pair's common parent; the referee's report gives the
   case table.

## Lemma D (every group or uncovered pair with a non-pure member is some P(y))

Under N1 to N3 *(corrected after R1: N2 is needed, through Lemma C)*, every group of round-t extended nodes with a non-pure member, and every uncovered pair with one, is
P(y) for exactly one y of round t + 1.

*Proof.* Let Q be the family. By Lemma A its chain totals are one value k or two, k and k + 1.

**Two totals.** Call the members with k + 1 the upper ones (cores of rank t − k − 1) and those with k the lower ones.
Each upper (T, a) and lower (D, a′) share by S2: D is a core child of T and a′ = a − δ_e.
- If two upper members had different vectors, all upper members would share one core C (Lemma A). A lower member shares
  with two of them, (C, c + δ_e) and (C, c + δ_e′), only if it is (D, c) with D a core child of C, which leaves no room
  for a third upper member under one upper vector; so every upper member is (C, c + δ_g), every lower one is (D, c), and
  (C, c) is a common parent of Q. So the upper members share one vector a and have distinct cores T_i.
- If the lower members have two cores D_1 ≠ D_2, they share one vector a − δ_e and both are children of every T_i. With
  one upper member, (T_1, a − δ_e) is a common parent of Q. With two, D_1 and D_2 share the parents T_1, T_2, and (T_1, a)
  and (T_2, a) share (S3) a core parent holding B(a), a chain base: chained twins, against N1.
- So the lower members share one core D, with vectors a − δ_e, and Q lies in P(y) for y = (D, a): its lower members are
  shortenings, its upper ones lifts (T_i is a parent of D holding B(a)). By Lemma C, P(y) pairwise shares and is
  maximal, so a group Q equals P(y); a pair Q is P(y), or lies in the group P(y) and is not uncovered.

**One total k ≥ 1.**
- *One core C.* The vectors pairwise differ by a unit move, so they are c + δ_e over one lower vector c, with the
  common parent (C, c), or c − δ_e under one upper vector c, the shortenings of y = (C, c). In the second case Q lies in
  P(y) and the end of the two-totals case applies. A pair is both, and lies in P(y).
- *One vector a, cores C_i.* If the C_i have a common core child D, then (D, a − δ_e) shares with every member (S2), so a
  group Q is not maximal and a pair lies in P((D, a)). A pair C_1, C_2 always has a common child, since two core nodes that
  share a parent lie in a group or are an uncovered pair. With three or more and no common child, N3 gives a common core
  parent U holding B(a), and (U, a) is a common parent of Q.

**Pure members.** A pure member is a core node A at total 0, so Q has two totals; the argument above applies.

**Exactly one.** y is read off P(y): two shortenings give b as the larger vector; a shortening and a lift give D and b.
So distinct y give distinct P(y). ∎

## Lemma X (the order lemma for extended nodes)

Under N1 to N3, for every t ≥ 1, Lemma R's round rule applied to the extended nodes of round t returns exactly the parent
sets P(y) of the extended nodes y of round t + 1 with two parents or more.

*Proof.* The groups and uncovered pairs made only of pure nodes are the node core's (Lemma B), which are the P(y) of the
pure y by the core's construction. Those with a non-pure member are the P(y) of the non-pure y (Lemma D), and each such
P(y) is one (Lemma C). ∎

## Lemma F (the one-parent nodes and the fresh counts)

1. **The extended nodes with one parent** are the offshoots O_q (parent the knot w) and the chain nodes (O_q, e at length
   n). A pure node of rank ≥ 2, or a round-1 group, has a group or a pair as its parents. A non-pure (C, a) with two
   chains has two shortenings. With one chain e, based at q: if C has rank ≥ 2, its points are its parents' points, so
   some core parent holds q and gives a lift; if C has rank 1, it holds q, so C = O_q (round-1 groups are sets of live
   knots), whose only core parent is a knot.
2. **Demand.** For x = (C, a), the extended nodes having x as a parent are (C, a + δ_e) for each chain e based at points
   of C, and (C′, a) for each core child C′ of C (C′ holds C's points, so B(a)). So f(x) = d(x) + r(x), where d counts
   those with two parents or more (x's groups next round, by Lemma X) and r those with one.
3. **The fresh table.** Growth gives a new birth with p parents and demand d max(d, 3 − p, 1) fresh distinctions, or d
   when it is implied (`FRESH-COUNT-20261118-001`); the excess becomes offshoots, one each.
   - p ≥ 2: r = 0, since the only nodes with a one-parent child are O_q and the chain nodes, which have p = 1. And
     d ≥ 1, except at the last node of a finished piece without chains, which is the relay: a non-pure node has the child
     (C, a + δ_e), with two parents; a pure node with no core child is alone in its rank (while a rank of a connected
     piece has two nodes or more, its groups and pairs cover every node: referee R2's coverage argument), so it holds the
     whole piece, and in a piece with chains it has a child (C, e at 1) with two parents. So max(d, 3 − p, 1) = d = f.
   - O_q: its only parent is the knot w, so every family holding O_q shares w; its children are the uncovered pairs with
     the other rank-1 nodes at w, open_w − 1 of them (round-1 groups at w plus w's other offshoots), even with group cells.
     So d = open_w − 1, r = R(open_w), and max(d, 2) = d + r in each case open_w ≥ 3, 2, 1.
   - (O_q, e at n): d = (open_w − 1) + (R(open_w) − 1) = 1 for open_w = 1 or 2 (the core children of O_q with the chain,
     and the other chain at q), r = 1, and max(1, 2) = 2 = d + r.
   - Implied births: as in `CHAIN-IDENT-20261119-001A` (proof of Theorem 1, item 4): a chain node takes one of its
     parent's two or more loose distinctions, and an offshoot one of the start's two or more, so neither is implied.

## Proof of the theorem

By induction on t, carrying the bijection, the parents P and the fresh counts f, as in `CHAIN-IDENT-20261119-001A`.
- **Round 1.** By Lemma R item 1 the births are the round-1 groups and one offshoot for each pendant point: the rank-1
  nodes. Their fresh counts are given by Lemma F.
- **Step.** By Lemma R items 3 and 4, round t + 1's births are the groups and uncovered pairs of round t's births, with
  sharing read through the parents, and one offshoot for each fresh distinction beyond a birth's demand. Through the
  bijection at round t these are the round rule on the extended nodes of round t, which by Lemma X gives the P(y) with
  two parents or more, and by Lemma F the one-parent nodes, one for each excess distinction. Their fresh counts are f by
  Lemma F. The relay of a finished piece without chains is `RELAY-IDENT`'s and referee R2's. ∎

## The machine check

`ext.py` (structure only, no growth) builds every extended node through round 10 and checks Lemma X directly (the round
rule on all extended nodes of each round against the P(y) of the next), and N2 and N3, on every sample start of the
graded-order and cycle studies whose cores finish ([tree pieces](ext_samples.txt), [pieces with a cycle](ext_cycles.txt)):

| Starts | Without chained twins | Lemma X, N2 and N3 hold | With chained twins | Lemma X fails | N2 fails | N3 fails |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tree pieces (graded-order samples, both twin samples) | 678 | 678 | 56 | 56 | 32 | 4 |
| pieces with a cycle whose core finishes | 115 | 115 | 11 | 11 | 0 | 0 |

So N2 and N3 hold on every sample start without chained twins, and the theorem covers all 793 of them; there it agrees
with the 1,586 start-and-law growth comparisons already recorded. N2 failed only on starts with chained twins, always at
a node of rank at least their least rank (`convex.py` checks the single-base form). Two starts' cores passed the cap and
were not checked *(26 capped rows in all across both outputs, after R1)*.

## What is open

1. **Does N1 imply N2 and N3?** *(Answered for N2 after R1: no.)* A 13-knot start meets N1 and N3 and fails N2, and so
   does the cycle study's referee's nine-knot start. Whether N1 implies N3 is open; the referee reduces N3, under N1 and
   single-base N2, to a test on triples.
2. **Chained twins.** Lemma D's failure is exactly the family {(T_1, a), (T_2, a), (D_1, a − δ_e), (D_2, a − δ_e)}, the
   group the graded-order study found in its two misses: reading it means adding that family to the round rule.
3. **Cores that do not finish.** Chains there need the unrolled map's copies (`CYCLE-READ-20261127-001`).

## Known results, and what this adds

The extended nodes are `CHAIN-IDENT-20261119-001A`'s clusters of the extended map with its connected core sets replaced by
the node core's births, and the proof follows its Lemmas 4 and 5 and its proof of Theorem 1; the pure part is referee R2's
argument. What is new is that the counting survives group cells (sets of births that are not connected sets), on a class
read off the start, and that the obstructions are two families read off the start: chained twins, and lifts that do not
meet *(corrected after R1: "the obstruction is one family")*.
