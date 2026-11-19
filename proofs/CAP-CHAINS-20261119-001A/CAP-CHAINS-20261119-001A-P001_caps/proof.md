# Chains under a cap on places

Status: Proved

Ticket `CAP-CHAINS-20261119-001A`, 19 November 2026, by Claude, on the coordinator's go-ahead for `WEIGHTINGS-20261119-001#2`.
It builds on `DOUBLE-IDENT-20261119-001A-P001` (the identification and dimension theorems for knot multigraphs, with dead knots as
blocks) and `RELAY-IDENT-20261119-001A-P001` (relays; a tree start's dimension is the most rays in one piece). The advisor checked
the statements before the freeze; its points are folded in:
- the 6-cycle step of Lemma 1;
- the relay's reading;
- the wording of the families;
- the headline, which is restricted to tree starts, since cyclic starts at cap 5 can grow exponentially.

`machine_check.py` is a separate algorithm in the same task.

## Setting

As DOUBLE-IDENT: a start is a connected set of knots with places p_k. Each distinction lies in one or two knots. K is the knot
multigraph and K̄ its simple underlying graph, and deg_k is k's degree in K̄. sh_k counts k's shared distinctions with multiplicity,
so sh_k ≥ deg_k. open_k = p_k − sh_k, and k is live when open_k ≥ 1.
- **The class.** (S0) no stall, open_k ≥ d_k; (S3) no round-1 group of three or more; (S4) no two live knots with two common
  neighbours, live or not; (S6′) at least two loose distinctions.
- **The relayed map X⁺.** Its points are the live knots. It has a block N(w) ∩ live for every knot w with at least two live
  neighbours. Each live knot k carries s_k = open_k − d_k pendant points with R(open_k) rays each, where R = 2, 1, 0 for open = 1, 2,
  ≥ 3. There is a relay point with two rays on every finite piece, when there are two or more pieces.
- **Pieces.** A piece is a component of X⁺. It is *finite* when it has no ray and no cycle of blocks. The rays of a piece are its
  pendant rays plus a relay's two.
- **The cap.** It is c when p_k ≤ c for every knot.
- **No dead knot** means every knot is live.

## Lemma 1 (what the class leaves when every knot is live)

In the class with every knot live, K̄ has no cycle of length 3, 4 or 6. The round-1 groups are exactly the candidate pairs (two live
knots with a common neighbour), and

d_k = Σ_{w ∈ N(k)} (deg_w − 1).

*Proof.*
- **A triangle a, b, c.** Each pair has the third as a common neighbour, so the three are pairwise candidates. If a fourth knot is
  adjacent to all three, a and b have two common neighbours, against (S4). Otherwise {a, b, c} is a valid set of three, which lies
  in a round-1 group of three or more, against (S3).
- **A 4-cycle** a, x, c, y. Then a and c have two common neighbours, x and y, against (S4).
- **A 6-cycle** a, x, b, y, c, z. With no shorter cycles it is induced. Then a, b and c are pairwise candidates through x, y and z.
  A common neighbour of all three would close a 4-cycle with x. So {a, b, c} is valid, against (S3).
- **The groups.** By (S3) no valid set of three exists, so every candidate pair is uncovered and is a group.
- **The count.** k's partners are the knots of N(w) − {k} for w ∈ N(k), all live.
  - They are distinct over w: a knot in two of them would be a second common neighbour (S4).
  - None is k's neighbour: that would close a triangle.
  - So d_k is the sum. ∎

## Lemma 2 (cap 5: one line or one ring of knots, with leaves)

In the class with every knot live and cap 5, every knot has at most two non-leaf neighbours. If there are three or more knots, the
non-leaf knots (the *core*) form one path or one cycle, and every other knot is a leaf hung on a core knot.

*Proof.*
1. Let m_k be the number of k's non-leaf neighbours. Each contributes at least 1 to d_k, so d_k ≥ m_k. Also deg_k ≥ m_k.
2. By (S0), 5 ≥ p_k = sh_k + open_k ≥ deg_k + d_k ≥ 2 m_k. So m_k ≤ 2.
3. With three or more knots, every leaf's neighbour is a non-leaf. So removing the leaves keeps K̄ connected.
4. A connected graph whose degrees are at most 2 is a path or a cycle. ∎

For a tree this makes K̄ a caterpillar, in the literature's word (Harary and Schwenk 1973).

## Theorem 1 (five places and no dead knot: at most two chains in a piece)

In the class with every knot live and cap 5, every piece of the relayed map carries at most two rays, a relay included.

*Proof.* A live knot k carries s_k · R(open_k) rays. This is positive only in two cases:
- open_k ∈ {1, 2} and d_k = 0, giving two rays;
- open_k = 2 and d_k = 1, giving one ray.

1. **d_k = 0.** By Lemma 1 every neighbour of k is a leaf, so K̄ is a star with k at its centre, or has at most two knots. No block
   holds k, since each neighbour's live neighbours are just k. So k is a piece by itself, with at most two rays.
2. **d_k = 1.** Exactly one neighbour of k has degree 2, and the others are leaves. So k is one of two kinds:
   - (a) a leaf whose neighbour has degree 2;
   - (b) a non-leaf with exactly one non-leaf neighbour, which has degree 2.
3. **A cycle core.** No knot is (a) or (b).
   - A core knot has two non-leaf neighbours.
   - A leaf's neighbour has two core neighbours besides it, so degree at least 3.
   - So no knot carries a ray.
   - Every piece holds a cycle of blocks. An odd core is one piece around it. An even core has length at least 8 by Lemma 1, and
     each parity class makes a cycle of at least four blocks.
   - So no piece is finite and no relay is added. Every piece has no rays.
4. **A star** (one core knot c).
   - Its centre is case 1.
   - Its leaves have d = deg_c − 1. They are (a) only when deg_c = 2: the path of three, whose two leaves form one piece with two
     rays.
5. **A path core** c_1, …, c_m with m ≥ 2.
   - An inner core knot has two non-leaf neighbours, so it is neither (a) nor (b).
   - A leaf hung on an inner knot, or on an end with two or more leaves, has its neighbour of degree at least 3, so it is not (a).
   - So the only candidates at the end c_1 are its single leaf, when c_1 has exactly one, and c_1 itself, when c_2 has degree 2.
     The same holds at c_m.
   - The two candidates at one end are adjacent, so they lie in opposite parity classes of the tree.
   - So each parity class holds at most one ray-bearing knot per end, each with one ray: at most two pendant rays.
6. **The pieces of a tree.** With every knot live, two knots at distance 2 share the block of their middle knot. A block joins only
   knots of one parity class. So the pieces are the parity classes, and each carries at most two pendant rays.
7. **The relay.** A relay is added only to a finite piece, which has no pendant ray, and it carries two. ∎

## Corollary 2 (the dimension of tree starts)

In the class, with every knot live, cap 5 and K̄ a tree, the growth closes, or is one- or two-dimensional. This follows from
Theorem 1 with RELAY-IDENT's Theorem 5, extended to multigraphs by DOUBLE-IDENT's Theorem 6: a tree start's dimension is the most
rays in one piece.

A start whose core is a cycle carries no rays at all. Its growth class is decided by its cycle. This reading is DOUBLE-IDENT
Corollary 7's computed rule, not proved here:
- a bare single cycle is one-dimensional;
- anything else is exponential.

For example, the ring of seven knots with one leaf is exponential at cap 5. So cap 5 bounds the dimension of tree starts. For other
starts it bounds only the chains.

## Theorem 3 (the cap is sharp, and dead knots lift it)

1. **Cap 6, every knot live.** For every R ≥ 3 there is a bare tree in the class with R rays in one piece, and so dimension R.
2. **Cap 5, with dead knots.** For every h ≥ 1 there is a tree in the class with 3 · 2^(h−1) rays in one piece, and so dimension
   3 · 2^(h−1).

*Proof of 1.*
- **The tree S_R.** Take a tree whose R − 2 branch knots have degree 3 and lie on a path, neighbouring branch knots joined through
  one connector knot. Each end branch knot carries two arms and each inner one carries one. Each arm is branch – a – leaf.
- **At bare sizes:**
  - a branch knot has d = 3 (its neighbours all have degree 2), so p = 6;
  - a connector has d = 4, so p = 6;
  - a has d = 2, so p = 4;
  - a leaf has d = 1, open 2 and p = 3, so it carries one ray.
- **The class.** It is a tree, so (S4) holds. Three knots pairwise at distance 2 in a tree share their median, so (S3) holds.
  Bare sizes do not stall.
- **The piece.** Every leaf lies at distance 2 from its branch knot. The branch knots lie at even distances from each other. So all
  R leaves are in one parity class, one piece with R rays.
- S_3 is the seven-knot spider with arms of two, the bare tree of WEIGHTINGS' W1.

*Proof of 2.*
- **The tree T_h.**
  - A dead hub H has three places, all shared with three live members M.
  - Each member is joined to a live connector X.
  - X's other neighbour is either an end K or, below depth h, a member of a new hub with two fresh members.
- **The values:**
  - M: d = 2 + 1 = 3 (two co-members through H, one partner through X), so p = 5 and open 3, with no pendant point.
  - X: d = 0, since H is dead and M's other neighbours are not live, so p = 3 and open 1. X is a piece by itself with two rays.
  - K: d = 1, open 2 and p = 3, so it carries one ray.
- **The class.** It is a tree. A hub's three members have the hub as a common neighbour, so they are not a valid set, and no knot
  stalls.
- **The piece.** The blocks N(H) and N(X) tie every member and end into one piece, with 3 · 2^(h−1) ends. The relay theorem holds
  with dead knots as blocks (DOUBLE-IDENT), so the dimension is the number of ends. ∎

## What the machine check must show (frozen before it runs)

| # | Check | Falsified by |
| --- | --- | --- |
| C1 | Every connected graph of up to 12 knots with no 3-, 4- or 6-cycle that meets deg_k + d_k ≤ 5 everywhere has a path, a cycle or a star as its core (Lemma 2) | one graph |
| C2 | On every such graph and every assignment open_k ∈ [max(1, d_k), 5 − deg_k], no piece has more than two pendant rays (Theorem 1) | one assignment |
| C3 | The program's reader (DOUBLE-IDENT's classify and dims.predict), on every simple start of those graphs with up to 9 knots, never reads an in-class start as three or more dimensions | one start |
| C4 | Every girth-5 start with a 6-cycle, every knot live, within cap 5 and up to 7 knots, is out of the class (Lemma 1) | one in the class |
| C5 | Every touch-census arrangement in the class with no dead knot has at most two rays in a piece | one arrangement |
| C6 | S_3 to S_6 and T_1, T_2 are in the class, with the largest knot 6 and 5 and the stated ray counts; dims.predict reads R; the growth agrees with the relayed cover per round to round 8 | any failing |
| C7 | (the advisor's prediction) the engine's per-round counts have degree R − 1: 2, 3, 4, 5 for S_3 to S_6, and 2 and 5 for T_1 and T_2. That is, the R-th differences vanish once the early rounds settle | a family whose last R-th differences are not zero, reported with the rounds reached |
| C8 | (the advisor's risky case) the ring of seven with one leaf is in the class and read exponential, and its growth agrees with the cover to round 8 | either failing |

## Validation

`machine_check.py` ran once after the freeze (output `machine_check.json`, summary `result.json`). All eight checks pass.

| # | What ran | Result |
| --- | --- | --- |
| C1 | 86 graphs of 1 to 12 knots (no 3-, 4- or 6-cycle, deg_k + d_k ≤ 5), enumerated one knot at a time up to isomorphism | every core a path (58), a cycle (22) or a star or less (6) |
| C2 | 200,597 open assignments on them, pieces and rays counted from the definitions | at most two pendant rays in any piece |
| C3 | 162,576 simple starts of up to 9 knots read by DOUBLE-IDENT's classify and dims.predict | 150,355 stall; in the class, 1,864 one-dimensional, 9,259 two-dimensional, 1,098 exponential (cycle cores), none three or more |
| C4 | 2,187 all-live starts of girth 5 with a 6-cycle, up to 7 knots | 1,377 out by (S3), 810 stall, none in the class |
| C5 | the touch census's 12,473 arrangements in the class | 963 have no dead knot, and none has more than two rays in a piece; 11,510 have a dead knot |
| C6 | S_3 to S_6 (7, 11, 15, 19 knots, largest 6 places) and T_1, T_2 (10 and 31 knots, largest 5 places, 1 and 4 dead hubs) | all in the class; rays in the main piece 3, 4, 5, 6 and 3, 6; read as that many dimensions; growth equals the relayed cover per round to round 8 |
| C7 | the engine's per-round counts, 24 rounds for S_3–S_5 and T_1, 18 for S_6, 16 for T_2 | R-th differences zero over the last four rounds or more and (R−1)-th constant, so degree R − 1 in every case |
| C8 | the ring of seven with one leaf (largest 5 places) | in the class, read exponential, equal to the cover to round 8; the engine's counts grow by about 9% a round to round 60 (8, 9, …, 1,096 at round 52, 2,086 at round 60) |

The advisor's predicted degrees (2, 3, 5 for S_3, S_4, S_6; 2 and 5 for T_1, T_2) held. It counted S_6 as 17 knots, but it has 19:
four branch knots, three connectors and twelve arm knots.
