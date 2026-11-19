# Partnered starts grow without end, faster than any cluster reading

Status: Partial

Ticket `WALL-READ-20261119-001A`, 19 November 2026, by Claude, on the coordinator's go-ahead for `MERGE-BURST-20261119-001#1`.
- **What it builds on.** `REDUCE-BLOCKS-20261119-001A-P001` (Lemma R: the growth reads only the live roster, refereed in part) and
  `DOUBLE-IDENT-20261119-001` (the cluster reading inside the class).
- **What it proves.** An explicit start past the wall whose growth is read exactly, never ends, and outruns every cluster reading;
  and two bounds that read the next round of any stage from a part of it.
- **How it will be checked.** The advisor checked the sketch before the freeze; its four gaps are closed below. `rosterlib.py`
  (the roster engine and the partnered-set search) and `job.py` are the machine check, frozen with this file.
- **Prior work.** Neumann-Lara (1978) proved that the clique graph of the literature's cocktail-party graph O_n is O_{2^(n−1)}, the
  first clique-divergent graph. Theorem 1 is the same mechanism under the cheapest growth's rule, which drops the cliques a block
  holds; that drop is the "− N(t−1)" below. Lemma 2's injection of maximal cliques is folklore. Deciding clique-divergence of a
  finite graph is open (Cedillo and Pizaña, 2021, prove it undecidable for automatic graphs).

## Setting

A state is the live roster: live points with open counts and the maximal blocks (REDUCE-BLOCKS, Lemma R). Two points are
**candidates** when a block holds both. The **groups** are the maximal cliques of the candidate graph that no block holds and have
three or more members, plus the candidate pairs inside none of them. From round 1 on, two junctions are candidates exactly when
they share a parent, and the blocks are the sets {junctions with parent v} (Lemma R, item 3). N_t is the number of junctions made
in round t; N_0 is the number of live points of the start.

A set of 2k points with a pairing is **partnered** when its candidates are exactly the pairs that are not partners (the
literature's cocktail-party graph O_k). A **transversal** holds one point of each partner pair. The transversals of a partnered set
are its maximal cliques, and two transversals share a point unless they are complements.

The **partnered start of order n** (n ≥ 2) has 2n live points in n partner pairs, one block for each non-partner pair, and open
count 2^(n−1) at every point. Its hub realization (REDUCE-BLOCKS, Corollary 1) is a start of the program: live knots of
2(n − 1) + 2^(n−1) places, one dead hub for each non-partner pair, and dead connectors. For n = 3 that is 30 knots, the largest of
8 places.

## Theorem 1 (partnered starts)

For n ≥ 3, write m_t = N_t / 2. The partnered start of order n grows with

  N_0 = 2n, N_1 = 2^n, N_(t+1) = 2^(m_t) − N_(t−1) (t ≥ 1),

so 6, 8, 10, 24, 4,086, 2^2043 − 24, … for n = 3. Every stage t ≥ 1 is partnered, with each junction's partner its complement. A
round-t junction has m_(t−1) parents (n in round 1) and open count 2^(m_t − 1) − m_(t−1). The growth makes no offshoot, never stalls
and never closes, and log₂ N_(t+1) ≥ m_t − 1: each count is about two to the power of half the one before (**runaway growth**, the
literature's iterated exponential). For n = 2 (a ring of four) every round has 4 junctions.

*Proof.* The **inductive form** at stage t ≥ 1 is:
- (F1) the N_t points are partnered, with partner the complement, and candidates exactly the non-partner pairs;
- (F2) the maximal blocks are N_(t−1) distinct transversals, closed under complement;
- (F3) each point lies in m_(t−1) blocks (its parents);
- (F4) m_t ≥ 4 and m_t > m_(t−1).

1. **Round 1.** The blocks are pairs, so every clique of three or more points is valid. The maximal cliques of O_n are its 2^n
   transversals, of n ≥ 3 points. Every non-partner pair lies in one, so no candidate pair is left over. Each point lies in 2^(n−1)
   transversals, its open count, so nothing stalls and no offshoot is made. So N_1 = 2^n junctions, each with n parents.
2. **Stage 1 has the form.**
   - Two transversals share a point unless they are complements, which gives (F1).
   - The block of a round-0 point x is B_x = {T : x ∈ T}, with 2^(n−1) members. It holds exactly one of T and T̄, so it is a
     transversal of the new pairing, and B_x̄ is its complement.
   - Two blocks B_x ≠ B_y differ, since some transversal holds x and not y. All have the same size, so all 2n are maximal, which
     gives (F2). (F3) holds with n parents, and (F4) holds since m_1 = 2^(n−1) ≥ 4 > n.
3. **The step.** Let stage t ≥ 1 have the form.
   - **The groups.** The maximal cliques are the 2^(m_t) transversals. A block holding a transversal equals it, since both are
     transversals. So the valid ones are the 2^(m_t) − N_(t−1) transversals that are not blocks.
   - **No pair is left over.** A non-partner pair {u, v} lies in 2^(m_t − 2) transversals but in only |u ∩ v| ≤ m_(t−1) − 1
     blocks, its common parents. By (F4), 2^(m_t − 2) ≥ m_t > m_(t−1) − 1. So every candidate pair is covered.
   - **No offshoot, no stall, no close.** A point lies in 2^(m_t − 1) transversals and in m_(t−1) blocks, so its demand is
     d = 2^(m_t − 1) − m_(t−1) ≥ 1. With p = m_(t−1) ≥ 3 its open count is max(d, 3 − p, 1) = d, so it uses all its loose
     distinctions and makes no offshoot. A stall needs a point in more groups than its open count, which is d. Closing needs one
     junction holding every loose distinction, and every round here makes N_(t+1) ≥ 2 junctions.
   - **N_(t+1)** = 2^(m_t) − N_(t−1).
4. **Stage t + 1 has the form.**
   - (F1): two valid transversals share a point unless they are complements, and the complement of a non-block is a non-block,
     since (F2) closes the blocks under complement.
   - (F2): the block of a point v is B_v = {valid U : v ∈ U}. It holds one of each complementary pair, so it is a transversal of
     the new pairing, and B_v̄ is its complement.
   - **Distinct blocks.** For v ≠ ū, the transversals holding v and ū number 2^(m_t − 2), and at most m_(t−1) − 1 of them are
     blocks, so some valid one holds v and not u. For v = ū, any valid U holding v works. Being equal in size, the N_t blocks are
     all maximal.
   - (F3): a valid transversal has m_t points, its parents.
   - (F4): m_(t+1) = 2^(m_t − 1) − m_(t−1) ≥ 2^(m_t − 1) − m_t + 1 > m_t, since 2^(m − 1) > 2m − 1 for m ≥ 4.
5. **n = 2.** O_2 is a ring of four points. Its maximal cliques are its four candidate pairs, each a block, so no clique is valid.
   The groups are the four pairs, each point in two, its open count. The ring of four junctions repeats with the same form. ∎

**Past the wall.** At stage 1, B_x ∩ B_y for non-partners x, y holds 2^(n−2) ≥ 2 junctions: two maximal blocks share two points
from round 1 on, the case DOUBLE-IDENT excludes.

## Lemma 2 (reading the next round from a part)

Let a stage have candidate graph G, maximal blocks ℬ and ℓ lone points (live points with no candidate), and let W be any set of
its live points. Then the next round has at least mc(G[W]) − |ℬ| − ℓ groups, where mc counts maximal cliques. In particular, a
partnered set of order k ≥ 2 gives at least 2^k − |ℬ|.

*Proof.*
1. Extend each maximal clique C of G[W] to a maximal clique Ĉ of G. If Ĉ₁ = Ĉ₂, then C₁ ∪ C₂ is a clique of G[W], so C₁ = C₂. The
   map is injective.
2. A maximal clique of G held by no block is a group: a candidate pair is held by a block, so it has three or more members, unless
   it is a lone point. A block is a clique, so a maximal clique held by a block equals it. So at most |ℬ| + ℓ maximal cliques are
   not groups.
3. A transversal of a partnered set of order k ≥ 2 has two or more points, so no extension of one is a lone point. ∎

*Found by the smoke test before the freeze.* The first statement left out ℓ: a lone point is a maximal clique held by no block,
but it is no group. The machine check's smoke run (125 random starts of six knots) showed 15 stages where the bound with k = 1
exceeded the groups. Lemma 3 needs k ≥ 2 for the same reason.

## Lemma 3 (a partnered set with no outside common candidate reads two rounds)

Let a stage t have a partnered set W of order k ≥ 2 such that no live point outside W is a candidate of every point of W. (For
k = 2 every transversal is a candidate pair, held by a block, so the lemma bites from k = 3.) Then stage
t + 1 has a partnered set of order at least 2^(k−1) − |ℬ_t|. So N_(t+1) ≥ 2^k − |ℬ_t| and N_(t+2) ≥ 2^(2^(k−1) − |ℬ_t|) − N_t.

*Proof.*
1. **One group per transversal.** A block holds at most one transversal of W, since its members are pairwise candidates. For
   each transversal T held by no block, every maximal clique holding T is held by no block and has k ≥ 2 members, so it is a
   group (Lemma 2, item 2). Choose one, Q(T).
2. **The groups meet W in their transversal.** A point of W outside T is the partner of a point of T, so Q(T) ∩ W = T.
3. **Complements are disjoint.** A point outside W in Q(T) ∩ Q(T̄) is a candidate of every point of T ∪ T̄ = W, and there is
   none. So Q(T) ∩ Q(T̄) = ∅, and Q(T), Q(T̄) share no parent: they are not candidates at stage t + 1.
4. **The rest are candidates.** For T′ ∉ {T, T̄}, T ∩ T′ ≠ ∅, so Q(T) and Q(T′) share a parent.
5. **Count.** Drop each complementary pair with a member held by a block: at most |ℬ_t| pairs of the 2^(k−1). The rest form a
   partnered set of stage t + 1. Lemma 2 at stage t + 1, with |ℬ_(t+1)| ≤ N_t blocks, gives the second bound. ∎

## Corollary 4 (no cluster reading follows a partnered start)

Suppose a reading sends the junctions of round t injectively to deck orbits of connected sets of at most s(t) members of an unrolled
map (the literature's regular cover) of a finite map with b members, each with at most Δ neighbours. A graph with degrees at most Δ
has at most (eΔ)^(k−1) connected k-sets through a given member, and every orbit has a member over one of the b. So
N_t ≤ b · (eΔ)^(s(t)), and log N_t = O(s(t)). For a partnered start, log₂ N_t ≥ N_(t−1)/2 − 1, so the clusters must have
s(t) ≥ c · N_(t−1) members: about as many as the round before has junctions.
- **The cluster reading of DOUBLE-IDENT** has s(t) = t + 1, so it cannot follow a partnered start.
- **No reading of that kind** follows it either, for any polynomial s(t).
- **Scope.** This holds for partnered starts and any start whose counts grow faster than every exponential. It is not proved for
  every start past the wall.

## What the machine check must show (frozen before it runs)

| # | Check | Falsified by |
| --- | --- | --- |
| M1 | Partnered starts n = 3, 4, 5, grown by the program's engine (hub realization) and by the roster engine: round-1 multisets (n parents, open 2^(m_1 − 1) − n) × 2^n; for n = 3 also rounds 2 and 3 ((4, 12) × 10, (5, 2043) × 24, disclosed: seen in exploration); the next count from the open counts (Σ open / parents of the next round) equal to the recurrence (n = 3: 4,086; n = 4: 248; n = 5: 65,526) | any multiset or count |
| M2 | Controls, n = 3 and 4: open count 2^(n−1) − 1 stalls in round 1; 2^(n−1) + 1 makes exactly 2n offshoots in round 1; n = 2 has 4 junctions in each of 10 rounds | any one |
| M3 | Lemma 2 on every stage (rounds 0–5) of 1,000 random starts within seven places (seed `wall-read-A-<case>`) and of the 16 explosive starts of EXPLOSIVE, wherever the next round is listed within the child's limits (3 GB, 120 s): the greedy partnered sets give 2^k − \|ℬ\| ≤ groups (minus ℓ when k < 2), and a seeded random W of 12 points gives mc(G[W]) − \|ℬ\| − ℓ ≤ groups | one stage |
| M4 | Lemma 3 on the same stages: for every partnered set found with no outside common candidate and 2 ≤ k ≤ 10, the construction on the actual next round (Q(T) the least group holding T) yields groups meeting W in T, complements sharing no parent, all others sharing one, and a partnered set of order ≥ 2^(k−1) − \|ℬ\| | one stage |

The smoke run before the freeze (disclosed) ran part-3, part-4, the controls for n = 3 and the ring, the random cases of six and
nine knots and the first explosive start; with the ℓ fix all passed.

## Validation

To be filled from the run.
