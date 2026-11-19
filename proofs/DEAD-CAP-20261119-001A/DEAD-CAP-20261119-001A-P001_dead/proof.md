# The map within five places, dead knots included

Status: Partial

Ticket `DEAD-CAP-20261119-001A`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-CORES-20261119-001#2`.

**What it builds on.**
- `CAP-CHAINS-20261119-001A-P001` (all-live cores) and `RING-CORES-20261119-001A-P001` (all-live rings).
- `DOUBLE-IDENT-20261119-001A-P001` and `RING-IDENT-20261119-001A-P001`, for the identification. Round t's junctions are the orbits of
  clusters of t + 1 points of the cover of the relayed map X⁺ that contain a knot. A finite piece, when there are two or more pieces,
  is relayed: it adds k junctions in round m − 1 + k, where m is its number of points, its spares included (a pilot before the
  freeze caught that the spares count; disclosed).
- `RELAY-IDENT-20261119-001A-P001`.

**How it was checked.**
- The advisor checked the statements before the freeze, and independently predicted the theta's counts at rounds 12 and 13 (8,910
  and 18,375), which the system gives. Its points are folded in:
  - blocks indexed by their knot;
  - the deck group's torsion-freeness in the pointing;
  - strong connectivity on the 2-core only;
  - periodic cores;
  - "rational series, algebraic rate".
- `deadlib.py`, `job.py` and `merge.py` are the machine check, a separate algorithm in the same task.

## Setting and words

As DOUBLE-IDENT, with every knot at most five places and dead knots allowed. A **dead** knot (open 0) is never a point of X⁺, but
its block N(w) ∩ live stays.
- A **block** is N(w) ∩ live for a knot w, live or dead, when it has at least two points.
- The **incidence graph** of a piece joins each point to the blocks that hold it. The piece's **rank** is that graph's cycle rank.
- **Pendants:** a live knot k carries s_k = open_k − d_k pendant points, each with R(open_k) rays (R = 2, 1, 0 for open = 1, 2, ≥ 3).
  A pendant with no ray is a **spare**.

## Lemma 1 (blocks within five places)

In the class within five places:
1. Distinct knots give distinct blocks, and two blocks share at most one point.
2. The round-1 groups are the candidate pairs, and d_k = Σ_{B ∋ k} (|B| − 1).
3. Every live knot k lies in blocks whose sizes sum to at most p_k − (deg_k − r_k) − (open_k − d_k) ≤ 5, where r_k is the number of
   blocks through k. So its profile, the multiset of the sizes of its blocks, is one of: none, {2}, {3}, {4}, {5}, {2, 2}, {2, 3}.
4. A block has at most five points.

*Proof.*
1. Two blocks sharing two points u, v give u and v two common neighbours, against (S4). The same holds for two knots giving the
   same block.
2. **Groups are pairs.**
   - Under (S4), a valid set of three or more contains a valid triple. If every triple of it had a common neighbour, two of those
     neighbours would be common to the same pair, so a single knot is common to all.
   - So (S3) forbids any valid set of three or more, and every candidate pair is a group.
   - k's partners are the other points of its blocks. They are distinct over blocks by item 1.
3. **The profile bound.** Each block through k comes from a distinct neighbour of k, so deg_k ≥ r_k. Then
   p_k = sh_k + open_k ≥ deg_k + d_k + (open_k − d_k) = (deg_k − r_k) + Σ_{B∋k} |B| + (open_k − d_k), and p_k ≤ 5.
4. **Block size.** A block's points are neighbours of its knot w, and deg_w ≤ sh_w ≤ p_w ≤ 5. ∎

## Lemma 2 (the skeleton of a piece)

1. **The skeleton Γ.** Contract each point of two blocks to an edge between them. Its properties:
   - 3-blocks have degree at most 3 in Γ;
   - 2-blocks have degree at most 2;
   - no edge joins two 3-blocks;
   - a 4- or 5-block is a whole piece (its points have profile {4} or {5}).
2. **The class boundary.** Under (S0) and (S6′), the class is exactly: no two blocks share two points (no cycle of two blocks) and
   no three blocks pairwise share three different points with no block holding all three (no cycle of three blocks). A cycle of
   three blocks is a valid triple, a round-1 group of three. This is where the class ends and the out-of-class eddies whose
   groups of three overlap begin.
3. **Where rays start.** Rays come only from two kinds of point:
   - lone points (d = 0, in no block: a piece of their own, with at most two rays);
   - points whose only block is a 2-block, with open 2 (one ray each).

   A point of a 3-, 4- or 5-block has d ≥ 2, and a point of two blocks has d ≥ 2.

*Proof.*
1. Item 3 of Lemma 1 gives the degrees. A point between two 3-blocks would need the profile {3, 3}.
2. (S4) is item 1 of Lemma 1. Under (S4), a valid triple a, b, c has three different blocks for its three pairs and no block
   holding all three, which is a cycle of length 6 in the incidence graph. The converse is the same statement read back.
3. A ray needs s_k ≥ 1 and open_k ≤ 2, so d_k ≤ 1. ∎

## Theorem 3 (every count, from a branch system)

For each point–block incidence (p, B) of a piece, let the formal series b_{p,B}(z) satisfy

b_{p,B} = Π_{q ∈ B − p} (1 + z e_q Π_{B' ∋ q, B' ≠ B} b_{q,B'}),

where e_q is q's pendant factor:
- 1 + z for each spare;
- 1/(1 − z) for each one-ray pendant;
- 1 + z/(1 − z)² for a two-ray pendant.

These equations have a unique solution in formal series with b = 1 + O(z). Let

r_p = z e_p⁺ Π_{B ∋ p} b_{p,B},

where e_p⁺ counts the clusters through p with one point of p's own pendant structure marked. It is e_p plus, for each pendant,
the series with that pendant's marked points forced:
- z/(1 + z) times its factor, for a spare;
- z/(1 − z)², in place of 1/(1 − z), for a one-ray pendant;
- z(1 + z)/(1 − z)³, in place of 1 + z/(1 − z)², for a two-ray pendant.

Then the piece makes [z^{t+1}] (Σ_{p knot} r_p) / (t + 1) junctions in round t, plus k junctions at round m − 1 + k (k ≥ 1)
when it is a finite piece with m points, spares included, and there are two or more pieces.

*Proof.*
1. **The cover.** It is a tree of points and blocks. The branch of the cover seen from a lift of p through a lift of B depends
   only on (p, B), since the cover is universal. A connected set in that branch that contains p's lift is a choice, for each other
   point q of B, of nothing, or of q with its pendants and a connected set in each of q's other branches. That is the equation.
   Iterating from b = 1 fixes one more degree of z each time.
2. **Pointing.** Every cluster contains a knot, so it meets the structure hung on that knot. Summing over the base knots p, the
   series z e_p⁺ Π b counts pairs (a cluster through a lift of p, a marked point of the cluster lying in p's own pendant structure,
   p included).
3. **Each pair is one orbit's cluster with one of its points marked.** Every point of a cluster belongs to exactly one knot's
   structure, so each cluster with t + 1 points is counted t + 1 times. The deck group of the universal cover is free, so it is
   torsion-free. An element fixing a finite cluster would have a power fixing a point, so it is trivial. Each (cluster, marked
   point) class therefore meets the fixed lift of p exactly once.
4. **The relay term** is RELAY-IDENT Theorem 4. ∎

## Theorem 4 (the growth class is the rank)

In the class within five places, for each piece:
1. **Rank 0** (a tree, finite or with rays). The system terminates. The count is eventually a polynomial whose degree is one less
   than the piece's rays, with a relay counting two (RELAY-IDENT Theorem 5, which reads only the piece). A piece with no rays closes
   if it is alone.
2. **Rank 1.** Only the cycle's incidences are recursive, and their equations are linear in one another. So the count is rational,
   with denominator 1 − W(z), where W is the product round the cycle of:
   - z e_x for each cycle point;
   - 1 + g_q for the off-cycle point q of each 3-block on it.

   g_q is the rooted series of q's hanging tree, z e_q Π (b over q's other blocks). It is rational, with powers of 1 − z from rays.

   The piece is constant (n junctions a round) when W = z^n, and otherwise exponential at the root x > 1 of W(1/x) = 1, as in
   RING-CORES Theorem 4.
3. **Rank ≥ 2.** The equations on the 2-core form a positive polynomial system.
   - **It is strongly connected.** Its dependency graph is the non-backtracking walk on a connected incidence graph of minimum
     degree 2 that is not a cycle.
   - **The rest is not, harmlessly.** Incidences into hanging trees are polynomial or rational. Those from trees into the core
     depend on the core, but nothing on the core depends on them, so they inherit its singularity.
   - **It is nonlinear.** Some 3-block on the 2-core has Γ-degree 3, so the equation through it is a product of two core unknowns.
   - **So, by Drmota–Lalley–Woods,** the rooted series have a square-root singularity at their radius ρ < 1. Pendant factors
     1/(1 − z) make the system analytic rather than polynomial, which is fine since ρ < 1.
   - **The rate.** The count grows at rate 1/ρ, an algebraic number, with a factor t^{−5/2} for orbits. If the core is periodic,
     the growth is stated along residue classes.
   - **Exponential.** ρ < 1, because the piece contains a one-cycle part with something hung on it.
4. **The start's class** is the largest over its pieces: exponential if any piece of rank ≥ 1 is not a bare cycle. Otherwise it
   closes, is constant, or is polynomial with the most rays in a piece (a finite piece counting two).

## Corollary 5 (what occurs within five places)

In the proved class within five places:
- **Trees** of the map grow in any number of dimensions. Three or more need a dead knot (CAP-CHAINS).
- **One-cycle pieces** have rational count series. Their rates are algebraic numbers, the roots of W(1/x) = 1. With every knot live they are the decorated rings, and the rate is at most the golden
  ratio (RING-CORES).
- **Pieces of rank two or more** need a 3-block of Γ-degree 3 on their 2-core, and so a dead knot. They grow at algebraic rates.
  - The theta of two dead hubs, each with three five-place members joined pairwise through three connectors, has 11 knots and rank 2.
  - **Nothing of rank 2 is smaller** (the advisor's count). A branch of Γ is a 3-block of degree 3 and no Γ-edge joins two of them,
    so the smallest rank-2 skeleton is this theta: 5 blocks and 6 points. Each point has profile {2, 3}, so it touches exactly two
    knots and cannot itself be a block's knot. So the 5 blocks' knots are not among the 6 points.
  - Its system is a = (1 + zb)², b = 1 + za. Its singularity solves 4z³ + 4z² = 1, giving the rate 2.3830, above every all-live ring.

**Outside the class** the theorem says nothing:
- cycles of two or three blocks, where groups of three overlap and the explosive eddies begin;
- knots of six or more places;
- stalls.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` (`research/DEAD-CAP-20261119-001/advisor/`), before the freeze, staying within its
text.
- **It confirmed** the profile bound, the class boundary (S3 under S4 iff no cycle of three blocks, read by points), the pointing
  (with torsion-freeness) and the theta's equation.
- **It derived** the theta's rounds 12 and 13 from the equation by hand.
- **It argued** that rank 2 needs 11 knots and a dead knot.
- **It asked** to check, in order:
  - the round-0 count (dead knots are round-0 junctions, which `exact_counts` includes);
  - a dumbbell;
  - a theta with a hanging tree or rayed pendant;
  - a periodic core;
  - a live hub with a dead connector.

  The frozen sampler covers these.

## What the machine check must show (frozen before it runs)

| # | Check | Falsified by |
| --- | --- | --- |
| D1 | On every connected graph of 1 to 6 knots, every choice of dead knots and every open assignment open_k ∈ [max(1, d_k), 5 − deg_k] meeting (S0), (S3), (S4) and (S6′) (read on the data): Lemma 1's items 1 to 3, Lemma 2's skeleton and ray kinds, and Lemma 2.2's boundary ((S3) under (S4) iff no cycle of three blocks, also checked on the data failing (S3)) | one datum |
| D2 | On every touch-census arrangement in the class with a dead knot, and on 20,000 random in-class starts of 6 to 16 knots within five places with a dead knot (frozen sampler): the branch system's counts equal the program's engine on every round reached (to round 20, or 4,000 junctions) | one round of one start |
| D3 | On the same starts, DOUBLE-IDENT's dims.predict agrees with Theorem 4's reading (closes, dimension R, exponential) | one start |
| D4 | On every rank-1 piece of D2, the root of W(1/x) = 1 equals the branch system's radius, read numerically (within 10⁻⁶) | one piece |
| D5 | The theta, T_1, T_2 and T_3 are in the class. The theta's counts follow the system to round 13 and its radius gives 2.3830 | any failing |
| D6 | (risky, the advisor's or mine) no in-class start within five places sampled in D2 grows faster than the theta's 2.3830 | a start that does |

## Validation

To be filled from the run.
