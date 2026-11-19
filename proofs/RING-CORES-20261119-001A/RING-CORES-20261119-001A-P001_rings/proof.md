# Rings within five places: the eddies and their rates

Status: Proved

Ticket `RING-CORES-20261119-001A`, 19 November 2026, by Claude, on the coordinator's go-ahead, which joins the identification line
to the eddy line. It builds on:
- `CAP-CHAINS-20261119-001A-P001`, for Lemmas 1 and 2 (in the class with every knot live and at most five places, the core is a
  path, a ring or a star) and for Corollary 2 (tree starts close or grow in at most two dimensions);
- `DOUBLE-IDENT-20261119-001A-P001` and `RING-IDENT-20261119-001A-P001`, for the identification: round t's junctions are the
  orbits of clusters of t + 1 points of the cover of the relayed map that contain a knot.

The advisor checked the statement before the freeze. Its points are folded in:
- the round-1 groups at a hung knot's block;
- which piece a hung knot or a spare joins when L is even;
- the wording of the headline.

`ringlib.py` and `job.py` are the machine check, a separate algorithm in the same task.

## Setting and words

As CAP-CHAINS. Every knot is live and has at most five places, and the start is in the class. A **ring start** is one whose core is
a cycle c_0, …, c_{L−1}. It has the following parts:
- **Leaves**, also called hung knots: knots of degree 1.
- **Spares**: pendant points of X⁺ with no ray (s_k = open_k − d_k of them on a knot whose open count is 3 or more).
- **Line points** of a piece: the core knots in it, in the order of the walk c_0, c_2, c_4, … (indices mod L).
- **Bare**: a piece with no leaf and no spare.

## Lemma 1 (the shape of a ring start)

A ring start has the following shape.
1. L = 5 or L ≥ 7.
2. Each core knot carries at most one leaf, and in any three consecutive core knots at most one carries a leaf.
3. The open counts are:
   - **a leafed core knot:** d = 2, open 2;
   - **a core neighbour of a leafed knot:** d = 3, open 3, no spare;
   - **any other ("plain") core knot:** d = 2, open 2 or 3, so a ∈ {0, 1} spares;
   - **a leaf:** d = 2, open 2, 3 or 4, so b ∈ {0, 1, 2} spares.
4. Conversely, every such shape with every such choice of open counts is a start in the class: a simple start realizes it.

*Proof.*
1. **The length.** By CAP-CHAINS Lemma 1 there is no cycle of length 3, 4 or 6, and the ring is the only cycle.
2. **The leaves.**
   - A core knot c has deg_c = 2 + ℓ_c.
   - By Lemma 1 there, d_c = Σ_{w∈N(c)} (deg_w − 1) = (1 + ℓ_{c−1}) + (1 + ℓ_{c+1}).
   - By (S0) and sh ≥ deg, 5 ≥ p_c ≥ deg_c + d_c = 4 + ℓ_{c−1} + ℓ_c + ℓ_{c+1}.
3. **The open counts.** open_k ≥ d_k by (S0), and open_k = p_k − sh_k ≤ 5 − deg_k. This gives the ranges stated.
   - A leaf's d is deg_c − 1 = 2.
   - A leaf's sh is 1. A double touch with its core knot would give that knot six places, since p_c = deg_c + d_c = 5 already.
4. **The converse.** Take each core knot at its bare size max(3, deg + d), plus one for a plain knot's spare, and each leaf at 3 + b
   places. Then:
   - (S0) holds by construction.
   - (S4) holds, since there is no 4-cycle.
   - (S3) holds. Three pairwise candidates with three different common neighbours close a cycle of length 6, which a ring of length
     5 or at least 7 with leaves does not have. Three pairwise candidates with one common neighbour w are not a valid set, since a
     valid set has no common neighbour; they give three candidate pairs. This is the case at a leafed knot, whose block holds
     c_{i−1}, c_{i+1} and the leaf.
   - (S6′) holds, since every knot keeps an open distinction.

   By Lemma M (DOUBLE-IDENT), multiplicities change only open counts, so the simple starts realize every case. ∎

## Lemma 2 (the map of a ring start)

1. **Blocks.** The blocks of X⁺ are N(c_i) ∩ live = {c_{i−1}, c_{i+1}}, together with the leaf of c_i when c_i has one. A leaf w has
   N(w) = {c_i}, which is no block. So each piece is a ring of blocks along the walk c_0, c_2, c_4, …:
   - for L odd, one piece with n = L line points;
   - for L even, two pieces, the even and the odd core knots, with n = L/2 each.
2. **Leaves and spares.**
   - A leaf of c_i is a third point in the block joining the consecutive line points c_{i−1} and c_{i+1}. So it joins the piece of
     the parity opposite to i.
   - A spare of c_j hangs on c_j and joins c_j's own piece.
   - A leaf's spares hang on the leaf.
3. **No rays, no relay.** Every pendant point sits on a knot with open ≥ 3, so it carries no ray. Every piece holds a ring of blocks,
   so none is finite, and there is no relay. ∎

## Theorem 3 (the count of a ring start)

Take a piece with line points x_0, …, x_{n−1}, where x_k has a_k spares, and the edge (x_k, x_{k+1}) carries a leaf with b_k spares or
none. Write:
- λ_k = 1 + z(1 + z)^{b_k} if the edge carries a leaf, and λ_k = 1 otherwise;
- v_k = z(1 + z)^{a_k} λ_k;
- W(z) = Π_{k=0}^{n−1} v_k = z^n (1 + z)^A Π_leaves (1 + z(1 + z)^b), where A = Σ a_k.

The piece's junctions in round t are [z^{t+1}] of

F(z) = Σ_{i=0}^{n−1} λ_{i−1} (Σ_{m=0}^{n−1} Π_{k=i}^{i+m} v_k) / (1 − W(z)) + Σ_leaves z(1 + z)^b,

with indices mod n. The start's count is the sum over its pieces.

*Proof.*
1. **The cover.** The incidence graph of a piece has exactly one cycle, its ring of blocks. So its universal cover is the bi-infinite
   periodic unrolling:
   - line points x_k for k ∈ ℤ, consecutive ones sharing a block;
   - a leaf in the block of (x_k, x_{k+1}) when the periodic pattern puts one there;
   - spares on the points that carry them.
   - The deck group ℤ shifts by n.
2. **Clusters.** A cluster is a connected set of points that contains a knot. Its line points form an interval, since the line
   points are connected only along the line. Two cases:
   - **The interval is empty.** The cluster holds no line point, so it is one leaf (a knot) with some of its spares. A spare alone
     is not a knot.
   - **The interval [i, j] is not empty.** The cluster is that interval with any subset of the spares of its points. It also has
     any subset of the leaves in blocks meeting it, those on the edges (x_{i−1}, x_i), …, (x_j, x_{j+1}), j − i + 2 of them. Each
     included leaf brings any subset of its spares. A leaf lies in exactly one block, so it can join through no other.

   Such a cluster has generating weight λ_{i−1} Π_{k=i}^{j} v_k.
3. **Orbits.** Clusters are finite, so the shift acts freely on them. Each orbit holding a line point has exactly one member whose
   leftmost line point lies in {0, …, n − 1}. Summing over i and over j = i + m + qn gives the geometric series in W. ∎

## Theorem 4 (which ring starts are eddies, and their rates)

1. **A bare piece** contributes exactly n junctions in every round: there F = nz/(1 − z).
2. **Any other piece** grows exponentially at the rate x > 1 with W(1/x) = 1. Equivalently,

   x^n = (1 + 1/x)^A Π_leaves (1 + (1 + x)^b / x^{b+1}).

   The count is asymptotic to C x^t with C > 0.
3. **The start** grows exponentially exactly when some piece is not bare, at the largest of its pieces' rates. Otherwise it makes L
   junctions every round.

*Proof.*
1. **W has a unique root in (0, 1).** W has non-negative coefficients, W(0) = 0, W is increasing on [0, 1], and W(1) =
   2^A Π (1 + 2^b) > 1 unless the piece is bare. So 1 − W has exactly one root ρ in (0, 1), and it is simple since W′(ρ) > 0.
2. **ρ is the only root of least modulus.** If the piece is not bare, W has a term of degree n and one of degree n + 1. On |z| = ρ,
   |W(z)| ≤ W(ρ) = 1, with equality only when z^n and z^{n+1} point the same way, so only at z = ρ (Pringsheim, with aperiodicity).
3. **The numerator does not cancel it.** It is a non-zero polynomial with non-negative coefficients, so it is positive at ρ.
4. **So** [z^{t+1}] F ~ C ρ^{−t} with C > 0, and x = 1/ρ.
5. **The bare case.** Every v_k = z and λ = 1, and F collapses to nz/(1 − z). ∎

## Corollary 5 (the eddies within five places)

In the class, with every knot live and at most five places, a start grows exponentially exactly when its core is a ring that
carries a hung knot or a spare.
- Path and star cores close or grow in at most two dimensions (CAP-CHAINS Corollary 2).
- A bare ring makes L junctions every round.

Each piece's round-weight is a product of three kinds of factor:
- y for each line point;
- 1 + y for each spare;
- 1 + y(1 + y)^b for each hung knot with b spares.

The rate depends only on n, A and the b's of the piece, not on where they sit. These are the catalogue's ring family and its
interfaces (`LOOP-CATALOGUE-20261119-001`), now proved complete within the cap.

**Outside the class, or outside the cap,** the theorem says nothing. Those starts are:
- knots of six or more places, which the catalogue's hanging path (1 + y)/(1 − y) needs;
- dead knots;
- first-round groups of three, or two live knots with two common neighbours, where the break-shape and explosive eddies live
  (`BREAK-EDDIES-20261119-001`);
- stalls.

## What the machine check must show (frozen before it runs)

| # | Check | Falsified by |
| --- | --- | --- |
| K1 | Every decorated ring word of L = 5, 7, …, 14 knots, up to rotation and reflection, realized as a simple start, is in the class with every knot live, at most five places, and the forced open counts and demands of Lemma 1 | one word |
| K2 | DOUBLE-IDENT's dims.predict reads each such start as one-dimensional exactly when it is bare, and exponential otherwise | one word |
| K3 | The program's engine (joinlib.grow) gives per-round counts equal to Theorem 3's coefficients on every round reached, to round 40 or 4,000 junctions | one round of one word |
| K4 | Theorem 3's closed form equals the direct sum over intervals to round 40 | one word |
| K5 | (the advisor's predictions) C5 with two spares 1.2628; C7 with a leaf of b = 1 and a spare 1.2377; C9 with three leaves 1.2207 (x^4 = x + 1); C14 with one spare 1.0970 | reported, not a check of the theorem |
| K6 | On every simple start of 2 to 9 knots on the cap study's graphs (every knot live, at most five places), an in-class start is read exponential exactly when its core is a ring with a hung knot or a spare | one start |

## Validation

The machine check ran once after the freeze, through the shared runner (`RING-CORES-A1`, `runs/ring-cores`, 52 cases, all ok,
16:18 to 16:28 UTC). `merge.py` was written while it ran and before its output was read. Output: `machine_check.json`, summary
`result.json`. Every check passed.

| # | What ran | Result |
| --- | --- | --- |
| K1 | 23,098 decorated ring words of L = 5, 7, …, 14 knots (17, 60, 129, 248, 543, 1,128, 2,551, 5,588, 12,834), each realized as a simple start | every one in the class, every knot live, largest knot 5, open counts and demands as Lemma 1 forces |
| K2 | DOUBLE-IDENT's dims.predict on each | the bare ring one-dimensional and every other word exponential, at every L |
| K3 | the program's engine on each, to round 40 or 4,000 junctions (10 to 40 rounds, median 14) | per-round counts equal Theorem 3's coefficients on every round of every word |
| K4 | the closed form against the direct sum over intervals, to round 40 | equal for every word |
| K5 | the advisor's four predicted rates | all four as predicted: 1.2628, 1.2377, 1.2207, 1.0970 |
| K6 | 162,576 simple starts of 2 to 9 knots on the cap study's graphs | 150,355 stall; in the class, 1,098 exponential starts, every one a ring with a hung knot or a spare; 4 bare rings one-dimensional; path and star cores 1,860 one-dimensional and 9,259 two-dimensional; no exception |

**The rates found.**
- **Slowest.** A single spare on the largest piece is the slowest grower: x^(n+1) = x + 1. That gives 1.0527 for the ring of 13,
  the catalogue's ring family.
- **Fastest.** A piece whose every line point carries a spare is the fastest: W = (z(1 + z))^n, so x = 1 + 1/x. That is the golden
  ratio 1.6180, at every length.
- **The golden ratio is the most** (Proposition 6 below, added after the run). It is the run's maximum at every L from 5 to 14.

## Proposition 6 (post hoc: no ring within five places beats the golden ratio)

Every ring start within the cap grows at a rate of at most φ = 1.6180. A piece reaches φ exactly when each of its line points
carries a spare or flanks a hung knot with two spares. The second option exists only for even L.

*Proof.* Let z_0 = 1/φ, so z_0(1 + z_0) = 1. W(z_0) is a product of factors, each at most 1:
- **Line points.** A line point with a spare gives z_0(1 + z_0) = 1. One without gives z_0 < 1.
- **Hung knots.** A hung knot on the edge (x_k, x_{k+1}) has two flanking line points, which are its core knot's neighbours and
  carry no spare. Together they give z_0²(1 + z_0(1 + z_0)^b) ≤ z_0²(2 + z_0) = 1, with equality only for b = 2.
- **The flanking pairs are disjoint,** since hung knots lie at least three apart.

So W(z_0) ≤ 1, which gives ρ ≥ z_0 and x ≤ φ.
- **Equality** needs every factor equal to 1: every line point spared, or flanking a hung knot with b = 2.
- **For L odd** the hung knot's own core knot is a line point of the same piece without a spare, so equality fails whenever there
  is a hung knot. ∎
