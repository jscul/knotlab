# Question for the advisor (DEAD-CAP-20261119-001, before the freeze)

You have no tools. Answer only from this text, say where you are unsure, and keep it short.

**Setting.** This is as in the cap and ring studies you checked, but dead knots are now allowed: knots with open 0, all of whose
places are shared. A dead knot is never a point of X⁺, but its block N(w) ∩ live stays. The class is:
- (S0) open_k ≥ d_k for live k;
- (S3) no valid set of three or more live knots (pairwise candidates with no common neighbour);
- (S4) no two live knots with two common neighbours, live or dead;
- (S6′).

Every knot has at most five places. Round t's junctions are the deck orbits of clusters of t + 1 points of the cover of the relayed
X⁺ that contain a knot point, with relays on finite pieces (a finite piece with m points, when there are two or more pieces, adds k
junctions at round m − 1 + k).

**Claims.**
1. **Blocks.**
   - Two blocks share at most one point (S4).
   - The groups are the candidate pairs (S3), so d_k = Σ_{B∋k} (|B| − 1).
   - Since deg_k is at least the number of blocks through k, p_k ≥ deg_k + d_k ≥ Σ_{B∋k} |B|. So each live knot lies in blocks whose
     sizes sum to at most 5: none, {2}, {3}, {4}, {5}, {2,2} or {2,3}.
   - Blocks have 2 to 5 points, and a dead knot gives a block of at most deg ≤ 5.
   - So a piece is a graph Γ on blocks, with points of two blocks as its edges. 3-blocks have Γ-degree ≤ 3, 2-blocks Γ-degree ≤ 2,
     and no Γ-edge joins two 3-blocks. 4- and 5-blocks are whole pieces.
2. **Rays.** These sit only on lone points (d = 0, at most two rays) and on points whose only block is a 2-block with open 2 (one
   ray each). Points of a 3-, 4- or 5-block have d ≥ 2.
3. **The class boundary in Γ.**
   - (S4) holds iff no two blocks share two points, i.e. no cycle of two blocks.
   - Under (S4), (S3) holds iff there is no cycle of three blocks (three points pairwise in different blocks).
   - So the class is (S0), (S6′) and no cycle of 2 or 3 blocks. I would call the cycle of three blocks the entry point of the
     out-of-class "explosive" eddies, whose groups of three overlap.
4. **The count of any piece** (the branch system). For each point–block incidence (p, B) of the base piece, let

   b_{p,B}(z) = Π_{q∈B−p} (1 + z e_q Π_{B'∋q, B'≠B} b_{q,B'}).

   Here e_q is q's pendant factor: (1 + z) per spare, 1/(1 − z) per one-ray pendant, and 1 + z/(1 − z)² per two-ray pendant. The
   rooted series r_p = z e_p Π_{B∋p} b_{p,B} counts the clusters containing a fixed lift of p. Since the deck group acts freely,
   Σ_p (clusters through p̃, by knots) equals Σ (cluster orbits × their number of knots). So the orbit counts follow:
   - exactly, as (1/(t+1)) [z^{t+1}] Σ_p r_p when no knot of the piece has a pendant;
   - in general, with a second variable marking knots.

   By rank of the piece:
   - **Rank 0 (a tree):** the system terminates. The count is polynomial, of dimension = rays, with a relay counting 2.
   - **Rank 1:** the system is linear along the cycle. The count is rational with denominator 1 − W, where W is the product round
     the cycle of z e_x over cycle points, and of 1 + g_q over the off-cycle point q of each 3-block on it. g_q is the hanging tree's
     rooted series. The rate is the root of W(1/x) = 1, and a bare cycle (W = z^n) is constant.
   - **Rank ≥ 2:** the system is polynomial and nonlinear, so (Drmota–Lalley–Woods) the count is algebraic with a square-root
     singularity at ρ. It grows like ρ^{−t} times a power of t, at rate 1/ρ, where ρ is the least z at which the least solution
     stops existing.
5. **Examples (pilot, disclosed).**
   - The ring of seven with a leaf (all live) gives the rank-1 recurrence exactly. A ring of four dead hubs is bare: four junctions
     every round.
   - **The theta.** It has two dead hubs (3 places), each with three live members (5 places), joined pairwise through three live
     connectors (3 places): 11 knots, rank 2, in the class. Its engine counts are 11, 12, 20, 33, 54, 92, 162, 297, 562, 1,092,
     2,166, 4,365 (rounds 0–11), with ratios still rising past 2.0.
   - My system for it is a = (1 + zb)², b = 1 + za. Its discriminant gives 1 − 4z² − 4z³ = 0, so ρ ≈ 0.4196 and a rate ≈ 2.383,
     above the golden ratio, which bounds every all-live ring.

**Questions.**
1. Is each claim right, in particular:
   - the profile bound (could a dead knot let deg_k exceed the number of blocks through k in a way that breaks it?);
   - the claim that S3 ⟺ no cycle of three blocks under S4;
   - the pointing argument for orbit counts?
2. Is the rank ≥ 2 statement safe? Is the system always strongly connected, so that DLW applies? Is the theta's equation right?
   Predict the theta's counts at rounds 12 and 13 from it, or at least whether 2.383 is its limit.
3. Is a start of rank ≥ 2 within five places possible with fewer than 11 knots, and does rank ≥ 2 need dead knots (all-live cap-5
   cores are paths, cycles or stars)?
4. Headline: "Within five places, in the class, the growth class is read off the rank of the map's pieces: trees are polynomial
   with dimension equal to their chain ends, one cycle is constant or exponential with a rational rate, and two or more cycles are
   exponential with an algebraic rate; a branch system gives every count exactly." Is that right, and what would you check first to
   break it?
