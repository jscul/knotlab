# What the joining policy builds when the fresh count is free

## Standard statement

The complete-round joining policy of `CUBIC-FROM-A-KNOT-20261117-001`, run on even-parity constraints with an arbitrary rule for
the number of fresh variables of each new constraint, builds the cover graph of a rank-truncated finite distributive lattice
(Birkhoff); the rule only chooses the poset of join-irreducibles. A constant rule survives exactly at the seed's arity and builds
ℕ^a; with groups capped at three only a = 3 survives; the least rule closes one seed into the Boolean lattice 2^[a] and conserves
the number of growing chains from any hand-over; bond balls of ℕ^a are Θ(r^a).

## Nearest known result

Birkhoff's representation theorem in its finitary form (Stanley, *Enumerative Combinatorics* I, Prop. 3.4.3), configurations of
conflict-free prime event structures (Nielsen, Plotkin and Winskel 1981), and the cube condition of median graphs (Barthélemy and
Constantin 1993; Chepoi 2000). In the program: the policy and the r³ theorem of
[`CUBIC-FROM-A-KNOT-20261117-001`](../../CUBIC-FROM-A-KNOT-20261117-001/CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth/proof.md),
its [referee's](../../../research/CUBIC-FROM-A-KNOT-20261117-001/referee-R1/report.md) two- and four-distinction variants, the
reader of [`BOND-NEXT-JOIN-20261117-001`](../../BOND-NEXT-JOIN-20261117-001/BOND-NEXT-JOIN-20261117-001-P001_distance_reader/proof.md),
and the r^D law of [`LOGIC-AXIS-20261107-001A`](../../LOGIC-AXIS-20261107-001A/LOGIC-AXIS-20261107-001A-P001_rulers_without_ends/proof.md).
[Design](../../../research/FRESH-COUNT-20261118-001/preregistration.md).

## 0. Setting

A **junction** is an even-parity constraint on binary distinctions (bits). A bit is **loose** while it lies in one junction and
**shared** once a second junction takes it; two junctions are **neighbours** when they share a bit. The **seed** is one junction on
a ≥ 3 loose bits (the program's smallest knot has three places). One **round** of the policy, on the current snapshot:

1. The **live** junctions hold loose bits. Two live junctions are **candidates** when they have a common neighbour.
2. A **valid set** is a set of at least three pairwise candidates with no neighbour common to all of them. The **groups** are the
   maximal valid sets (capped version: every valid triple) and every candidate pair contained in no valid set.
3. Each live junction gives one loose bit to each group containing it, and every remaining loose bit gets a junction of its own,
   an **offshoot** (the junction with one parent; the literature's join-irreducible). If some junction is in more groups than it
   has loose bits, the round is unavailable: a **stall**.

Each group and offshoot becomes a new junction on its chosen bits; a **count rule** then gives every new junction k fresh loose
bits. Old allowed states are all kept when k ≥ 1, and when k = 0 only if the new junction's parity is already implied (Lemma 0).
Every loose bit is used each round, so the live junctions of the next round are the new junctions with k ≥ 1. The **demand** of a
new junction is the number of groups of the next round containing it, computed on the snapshot after the round with every new
junction counted live; its **surplus** is k minus its demand. A junction's **parents** are the junctions it took bits from.

**Lemma 0 (implied parity).** A new junction's parity is implied by the old equations exactly when it takes every loose bit of the
snapshot. *Proof.* Over GF(2) the valid checks are the sums of junction equations, the cut of a set U of junctions (bits with one
end in U, a loose bit counting at its one junction). A cut made only of loose bits must contain no shared bit, so U is a union of
components of the junction graph; every junction descends from the seed, so the graph is connected and U is empty or everything.
The cut of everything is the set of all loose bits. ∎

## 1. The descent order decides the pattern (T1)

Order the offshoots by descent (q ≤ q′ when q′ descends from q through parents, or q = q′): the **descent order** Q. For a junction
v let I(v) be the offshoots v descends from or equals.

**Theorem 1.** Suppose no round up to t stalls. Then (a) v ↦ I(v) is a bijection from the junctions onto the ideals (down-sets) of Q
of size at most t, with |I(v)| the round of v; (b) u is a parent of v exactly when I(u) ⊂ I(v) with one element fewer, and then they
share exactly one bit; (c) the groups of round t + 1 are the sets of lower covers of the ideals of size t + 1, one group for each
such ideal; (d) the demand of a junction I of round t is |min(Q ∖ I)|, the number of minimal offshoots outside I; (e) each surplus
bit of I becomes an offshoot q with I(q) = I ∪ {q}; (f) a count below the demand makes the next round stall; (g) a junction's parity
is implied exactly when its demand is 0, exactly when it is the only live junction, which is then the top of a finite pattern.

The pattern is therefore the cover graph of the literature's distributive lattice of ideals of Q, truncated at size t, and a count
rule's whole freedom is the number of offshoots it places directly above each junction.

*Proof.* Induction on t, with the hypothesis H(t): (a), (b), every ideal of Q of size at most t a junction, and the round-t
junctions' bits other than their parents' all loose. H(0) holds with Q empty and the seed as the empty ideal.

*Candidates.* The live junctions are round-t ideals. Their neighbours are their parents only (their own bits are loose), which by
(b) are their lower covers, of size t − 1. If I and I′ have a common lower cover J then I ∩ I′ = J has t − 1 elements; conversely if
|I ∩ I′| = t − 1 then J = I ∩ I′ is an ideal (an intersection of ideals) of size t − 1, a junction by H(t), and a lower cover of both
by (b). So candidates are the pairs of round-t ideals meeting in t − 1 elements.

*Valid sets.* A family of at least three distinct t-sets pairwise meeting in t − 1 elements is a sunflower (all contain one
(t − 1)-set) or lies inside one (t + 1)-set. Take two members A = C ∪ {a}, B = C ∪ {b}; a third member D either contains C, or
misses some c ∈ C and then contains A ∖ {c} and B ∖ {c}, so D = (C ∖ {c}) ∪ {a, b} ⊆ A ∪ B; a member of the first kind and one of
the second meet in t − 2 elements, so the family is all of one kind. A sunflower's core is an ideal of size t − 1, a common
neighbour: not valid. A family inside the (t + 1)-set Y = A ∪ B has no common neighbour: three distinct t-subsets of Y meet in t − 2
elements, and the members have no neighbours of size t + 1 yet. So the valid sets are the families of at least three lower covers of
ideals Y of size t + 1 (Y is an ideal, a union of two), and the maximal ones are all the lower covers of such a Y, each of which is an
ideal of size t and so a junction. Each such lower cover is live: a junction with no fresh bit has implied parity, so by (g) it
is the only junction of its round, and then no Y with two or more maximal elements lies above it. A
candidate pair {I, I′} lies only in valid sets inside Y = I ∪ I′; it is a group of its own exactly when Y has two maximal elements.
Every ideal of size t + 1 of Q has at least two maximal elements, since a principal ideal I(q) has size equal to q's round, at most
t. This proves (c).

*Demand.* The ideals of size t + 1 containing I are I ∪ {m} for m minimal in Q ∖ I, so (d). A junction in more groups than its loose
bits stalls the round (f).

*The new round.* Each group for Y becomes a junction taking one bit from each lower cover of Y; I(new) = Y. Each surplus bit of a
live I becomes an offshoot q, and Q gains q with down-set I ∪ {q}; q is maximal and lies in no old ideal, so the old ideals stay
ideals. Every ideal of size t + 1 of the new order either contains a new offshoot q, and then equals I(q) (both have size t + 1), or
lies in the old order and is some Y. Ideals of size at most t contain no new offshoot. Parents are lower covers: a group junction's
parents are all the lower covers of Y, and an offshoot's one parent is the one lower cover of I(q) (its only maximal element is q).
Two junctions share at most one bit, since a new junction takes one bit from each parent. So H(t + 1) holds. (e) is the
construction.

*(g).* By Lemma 0 a new junction's parity is implied exactly when it takes every loose bit, i.e. it is the only new junction. Its
demand is then 0 (no candidates). Conversely demand 0 means Q ∖ I has no minimal element, i.e. I = Q, the top; Q's ideals of size |Q|
are just Q, so it is the only junction of its round. ∎

**Remark.** The policy's groups are the literature's cube condition: lower covers pairwise sharing a lower cover, with none shared by
all, are completed by their join. The demand needs no lookahead beyond the descent order: d(I) = |min(Q ∖ I)|.

## 2. One count for every join (T2)

**Theorem 2.** From a seed on a ≥ 3 bits, the uncapped policy with one count c at every new junction runs every round exactly when
c = a, and then Q is a disjoint chains, so the pattern is the literature's orthant ℕ^a (a junction at each v ∈ ℕ^a, its fresh bits
the steps v → v + e_i), with C(t + a − 1, a − 1) junctions in round t. Otherwise it stalls at round 2 if c ≤ a − 2, at round 4 if
c = a − 1, and at round 3 if c ≥ a + 1.

*Proof.* By Theorem 1 the rounds before a stall are ideals of Q, so compute demands with (d).
- Round 1: the seed has no groups; its a bits make offshoots μ_1, …, μ_a, an antichain. Each μ_i has demand a − 1 (the other μ's).
  If c < a − 1, round 2 stalls.
- Otherwise each μ_i has s = c − a + 1 surplus bits, making offshoots ν_{i,1..s} above μ_i. The round-2 junctions are the pairs
  {μ_i, μ_j}, with demand (a − 2) + 2s (the other μ's and the ν's above μ_i or μ_j), and the ν's, with demand (a − 1) + (s − 1). A pair
  needs a − 2 + 2s ≤ c = a − 1 + s, i.e. s ≤ 1. So c ≥ a + 1 stalls at round 3.
- If s = 0 (c = a − 1): no ν's; each pair has demand a − 2 and one surplus bit, giving offshoots π_{ij} above {μ_i, μ_j}. The round-3
  triples {μ_i, μ_j, μ_l} have demand (a − 3) + 3 = a (the other μ's and π_ij, π_il, π_jl) > c. Round 4 stalls.
- If s = 1 (c = a): every ν is the second element of a chain above μ_i. Inductively Q is a chains of length t, chain i being
  μ_i < q_i^2 < … < q_i^t. An ideal is a vector of heights (h_1, …, h_a) summing to t. If one height is t (a principal ideal, the top
  of chain i), the minimal elements outside it are the a − 1 other chain bottoms: demand a − 1, one surplus, the next element of
  chain i. Otherwise every chain's next element exists: demand a, no surplus. So Q stays a chains and J(a chains) = ℕ^a. ∎

## 3. The cap of three (T3)

**Theorem 3.** (a) On a snapshot satisfying Theorem 1, the capped and uncapped policies form the same groups exactly when no ideal of
size t + 1 has four or more maximal elements. (b) With groups of at most three and one count c, the policy from a seed on a ≥ 3 bits
runs every round exactly when c = a = 3. For a ≥ 4 and c = a it stalls at round 4.

*Proof.* (a) Valid sets are lower covers of a Y with at least three maximal elements; the capped policy takes every valid triple
instead of the maximal valid set, so the two agree exactly when every such Y has exactly three. (b) Rounds 1 to 3 only form groups
of at most three members (round-3 groups are the lower covers of ideals with at most three maximal elements), so Theorem 2's stalls
for c ≠ a occur unchanged (the capped demand is never smaller). For c = a ≥ 4, round 4 meets the ideal {μ_1, μ_2, μ_3, μ_4} with four
maximal elements: its four lower covers form four valid triples, each lower cover in three. The junction {μ_1, μ_2, μ_3} is in those
three, in three for each of the a − 4 other ideals {μ_1, μ_2, μ_3, μ_l}, and in one triple for each of the three ideals adding a
chain's second element: demand 3 + 3(a − 4) + 3 = 3a − 6 > a. For a = 3 no ideal of ℕ³ has four maximal elements, so the cap never
acts. ∎

So "the stall at four" picks three, but only together with the cap of three, a number the policy is told; without the cap every
a ≥ 3 runs (Theorem 2). The earlier study's four-distinction variant used a four-distinction seed, matching (b).

## 4. The fewest counts (T4)

The **fewest** rule gives k = 0 at a junction whose demand is 0 (its parity is implied, Theorem 1(g)), and otherwise
k = max(d, 3 − p, 1), where p is the number of parents (at least three bits per junction, the program's smallest knot).

**Theorem 4.** (a) From a seed on a ≥ 3 bits the fewest rule builds the 2^a pattern: Q stays the antichain of the a seed offshoots,
the junctions are all subsets of it, the round-j junctions have j parents and a − j fresh bits (every junction has exactly a bits),
the last junction (the whole set) takes the last a loose bits, its parity is implied, it gets no fresh bit, and growth stops after
round a. It has 2^a junctions, a·2^(a−1) bits, equations of rank 2^a − 1, and no distinction with one value in every allowed state.
(b) Under the fewest rule, an offshoot with demand 1 gets exactly one surplus bit, and its offshoot again has demand 1; no other
junction gets surplus. So from any snapshot the number of offshoots made per round is constant from the second fewest round on: the
number of offshoots of the first fewest round with demand 1. (c) For every a there is a start (the crossed start: one surplus bit at
each junction of round a − 1 of the 2^a pattern) from which the fewest rule keeps a chains growing forever.

*Proof.* (a) With Q the antichain of a, the ideal of size j has demand a − j (the other offshoots). For j = 1, a − 1 ≥ 2 = 3 − p, so
no floor surplus; for 2 ≤ j ≤ a − 1, a − j ≥ 1 ≥ 3 − j; for j = a the demand is 0 and the parity implied. So no surplus is ever
given, and Theorem 1 gives the Boolean pattern. Each junction before the last brings fresh bits, so its equation is independent of
the earlier ones; the last is implied: rank 2^a − 1. Every bit lies on a 4-cycle of the junction graph, which is the cover graph of
2^[a] (the literature's a-cube), so no bit is a bridge: every bit flips in some allowed state.

(b) The rule gives surplus only where max(d, 3 − p, 1) > d with d ≥ 1, i.e. at an offshoot (p = 1) with d = 1 (the floor 3 − p = 2);
a junction with p ≥ 2 and d ≥ 1 gets d, and one with d = 0 gets 0. Let q be an offshoot with demand 1: it gives one bit to its one
group G and one surplus bit to its offshoot S. S's only neighbour is q, whose live children are G and S, so S's only candidate is G,
and no valid set contains S (a third member would be another candidate of S): S has demand exactly 1. By induction the chain
continues forever, and offshoots arise nowhere else.

(c) Let μ_1, …, μ_a be the seed offshoots and c_i the offshoot above the round-(a − 1) junction {μ_j : j ≠ i}. Then Q ∖ I(c_i) has the
single minimal element μ_i (every other c_j lies above μ_i), so c_i has demand 1 and (b) applies to each of the a chains. The chains
C_i lie above every μ_j with j ≠ i, and an ideal is a choice of heights in the a chains together with the μ's it needs; the number of
ideals of size at most t grows like t^a. ∎

So the fewest counts add no direction by themselves: from one knot they close it, and from any hand-over they conserve the number of
chains they are handed, which can be any number.

## 5. Bond balls of the product (T5)

Take the infinite parity system on ℕ^a, a ≥ 3 (Theorem 2's limit: every bit shared; the junction at v holds the bits of the steps
into and out of v). Bond distance δ(e, f) is the least size minus one of a minimal dependency (a K1–K3 knot of at least three bits)
containing both. Let a(e) be the lower end of e.

**Theorem 5.** For r ≥ 2a − 1, with m = ⌊(r − 2a + 1)/(2a − 2)⌋, a·C(m + a, a) ≤ |B(e, r)| ≤ a(2r + 1)^a for every bit e.

*Proof.* The proof of `CUBIC-FROM-A-KNOT-20261117-001` §3 carries over with three replaced by a.
- *Finite constraint lemma.* Every finite valid check is a finite vertex cut: flipping an elementary square (four bits around v, v + e_i,
  v + e_j, v + e_i + e_j) keeps every parity, so a check meets every square evenly; its sums along monotone paths from 0 define a
  potential, constant outside a box (two exterior points connect through their coordinatewise maximum in the exterior), and the
  check is the cut of the finite set where the potential is 1.
- *Locality.* A minimal check splits into pieces meeting every square evenly only trivially, so it is connected through squares (the
  connectedness of minimal cuts when short cycles generate the cycle space: Babson and Benjamini 1999, Timár 2013). Two bits of one
  square have lower ends within sup-norm 1, so ‖a(e) − a(f)‖_∞ ≤ δ(e, f), and the ball holds at most a(2r + 1)^a bits.
- *Long bonds.* Let u, w be the closest ends of e and f, at graph distance d, and P a shortest path from u to w; it is monotone in every
  coordinate, and neither far end of e or f lies on it. Among a ≥ 3 coordinates two have the same sign of monotonicity along P
  (constant coordinates take either sign). From any vertex x off P the two positive rays along those coordinates cannot both meet P:
  the meeting points would differ in opposite directions in two coordinates that P orders the same way. So one ray leaves every box
  containing P, and the complement of P is connected. The cut of P is a bond containing e and f of at most 2a(d + 1) − 2d =
  (2a − 2)d + 2a bits, so δ(e, f) ≤ (2a − 2)d + 2a − 1.
- *Count.* For every t ∈ ℕ^a with Σt ≤ m, the a bits leaving a(e) + t have closest ends within graph distance m of e's lower end, so
  they lie within δ ≤ (2a − 2)m + 2a − 1 ≤ r. There are C(m + a, a) such t. ∎

Every bit flips around an elementary square at every allowed state, so every distinction is native in the source-aware reading. The
statement is for the infinite system; a finite round's frontier, with its loose bits wired to one outside vertex, has more cycles and
is not claimed. The exponent a is exact; the constants are far apart.

## 6. Reading the junctions from bond distances (T6)

**Theorem 6.** In every snapshot of the uniform-count growth with c = a ≥ 3, the threshold reader of `BOND-NEXT-JOIN-20261117-001`
(§3), run with thresholds 3, …, 2a, returns exactly the junctions.

*Proof.* That proof used three facts, which hold here: (i) the junction graph is bipartite with no triangles (it is the cover graph
of a graded order; Theorem 1) and two junctions share at most one bit; (ii) deleting at most two junctions leaves every other
junction joined to the outside, since each has a fresh bits and each later junction takes at most one of them, so at least
a − 2 ≥ 1 remain, and following fresh bits upward reaches loose bits; hence single stars and adjacent pairs' cuts are bonds; (iii)
every set U of at least three junctions has |cut(U)| ≥ 3a − 2 > 2a: its last three members in round order bring 3a fresh bits, of
which at most two are taken inside the three (no triangle) and none by an earlier member. Stars have between a and 2a bits and an
adjacent pair's cut |S| + |T| − 2 ≥ 2a − 2 bits, so every bond of at most 2a bits is a star or an adjacent pair's cut, the
two-star cuts at threshold k have both stars smaller than k, and the induction of that proof goes through at every threshold up
to 2a. ∎

Beyond the product the reader is not proved: in the 2^a pattern a row of three junctions cuts 3a − 4 ≤ 2a bits for a ≤ 4, and in the
round before the last the set of all loose bits is itself a bond of a bits (Lemma 0: their parity is implied), which the reader
returns as a junction one round early. The allowed states of that snapshot and of the closed pattern are the same, so a reader of
distances, or of states, sees the 2^a pattern closed one round before the policy closes it. Whether bond distances determine the
junctions when counts vary is `VARIABLE-OUTPUT-READER-20261118-001`'s question; its exploratory scout found the threshold reader
fails after three junctions and no collision of tables through six.

## 7. What this answers

- **The count rule chooses only the descent order** (Theorem 1). Every number of directions the pattern grows comes from where the
  rule puts offshoots; the policy adds none of its own.
- **One count for every join is forced to the first knot's size** (Theorem 2). A rule told only "use one count" and "never stall"
  has one choice, a, and grows a directions; the smallest knot gives three. The three is the first knot's, not the rule's.
- **The stall at four is the cap's** (Theorem 3). It singles out three only for the capped policy, which is told three.
- **The fewest counts close one knot into the 2^a pattern and stop, and otherwise conserve the chains they are handed** (Theorem 4).
  They never single out a number either.
- No criterion here reads a number from the distances that the start or the rule did not supply. The question of typical behaviour
  (blind and random counts) is computed in ticket B.

## Verification and evidence

Ticket B (`experiments/FRESH-COUNT-20261118-001B/FRESH-COUNT-20261118-001B-E001_free_count/`) replays Theorems 1 to 4 and 6 on its
census, with gates that check the policy against the predecessor's rounds, the implied-parity test against GF(2) elimination, the
ideal checker against mutants and the bond distances against the allowed states. The proofs were written by the thread before the
census and read by the advisor (Fable 5.2), which confirmed Theorems 1 to 3 and 4(a), refuted the first form of 4(b) and supplied
its replacement. There is no independent referee verdict yet and no proof-assistant certification.
