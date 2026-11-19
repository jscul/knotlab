# Question for the advisor (CAP-CHAINS-20261119-001, before the freeze)

You have no tools. Answer only from this text, say where you are unsure, and keep it short.

**Setting.** A start is a connected set of knots, each with p_k places (here 3 <= p_k <= c for a cap c). Each shared distinction lies in exactly two knots; K is the knot multigraph and K̄ its simple underlying graph. sh_k = shared distinctions of k (with multiplicity, so sh_k >= deg_k in K̄), open_k = p_k - sh_k, and k is live when open_k >= 1. Round-1 groups: maximal sets of three or more live knots that are pairwise "candidates" (share a common neighbour in K̄, live or dead) but have no common neighbour, plus every candidate pair not inside such a set. d_k = number of groups containing k. The proved class: (S0) open_k >= d_k for every live k; (S3) no group of three or more; (S4) no two live knots with two common neighbours (live or not); (S6') at least two loose distinctions. In the class, the growth is the clusters of a cover of the relayed map X⁺: points are the live knots; a block N(w) ∩ live for every knot w (live or dead) with at least two live neighbours; s_k = open_k - d_k pendant points on each live k, each carrying R(open_k) rays, R = 2, 1, 0 for open = 1, 2, >= 3; a relay point with two rays on every finite piece when there are two or more pieces. A piece is a component of X⁺. Proved (refereed): for K̄ a tree, the dimension (per-round count is a polynomial of degree D - 1) is the largest number of rays in one piece. A piece with a cycle grows exponentially unless it is a bare single cycle (dimension 1; this part is a computed rule, checked on a census).

**Claim 1 (cap 5, no dead knot).** If every knot is live and p_k <= 5, every piece carries at most two rays.

Proof sketch.
1. All live: a triangle gives a valid triple (S3 fails) or two common neighbours (S4 fails); a 4-cycle gives two common neighbours. So K̄ has girth >= 5, groups are exactly the candidate pairs, and by S4 d_k = sum over w in N(k) of (deg(w) - 1).
2. 5 >= p_k = sh_k + open_k >= deg_k + d_k. Let m_k = number of non-leaf neighbours of k; d_k >= m_k and deg_k >= m_k, so m_k <= 2. Removing the leaves of a connected graph leaves it connected, so the non-leaves form one path or one cycle (the core), with leaves hung on it.
3. Rays: s_k R(open_k) > 0 needs (open 1 or 2, d_k = 0) or (open 2, d_k = 1). d_k = 0 means every neighbour is a leaf: K̄ is a star and k its centre, an isolated point of X⁺ with at most two rays. d_k = 1 means exactly one neighbour has degree 2 and the others are leaves: k is a leaf beside a core end of degree 2, or a core end whose core neighbour has degree 2. A cycle core has no such knot. A path core has at most two at each end, one in each parity class.
4. For a tree, the pieces are the two parity classes (with all knots live, two knots at distance 2 share a block), so each piece has at most two rays. A cycle core has no rays.

**Claim 2 (sharpness at cap 6, all live).** At cap 6 there are all-live trees in the class with any number R of rays in one piece. Take a tree whose branch knots have degree 3, are at mutual distance 2, and are adjacent only to degree-2 knots, and end every arm with a path branch - a - leaf. Branch knots: deg 3, d = 3, p = 6. A knot between two branch knots: deg 2, d = 4, p = 6. a: d = 2, p = 4. The leaf: d = 1, open 2, p = 3, one ray. All leaves lie in the branch knots' parity class, so one piece holds every ray.

**Claim 3 (dead knots, cap 5).** With dead knots allowed, cap 5 bounds nothing.
- A dead hub H has three places, all shared with three live members M.
- Each M is joined to a live connector X (sh 2). M has d = 2 + 1 = 3 (two co-members through H, one partner through X), so p = 5 and open 3.
- X's other neighbour is either an end K, with p = 3, sh 1, d = 1 and open 2, so one ray, or a member of a new hub.
- X has d = 0, because its neighbours have no other live neighbour (the hub is dead). So p = 3 and open 1: an isolated piece with two rays.
- A binary tree of hubs of depth h gives one piece with 3·2^(h-1) rays.

**Questions.**
1. Is Claim 1's proof right, in particular steps 1 and 3? Is there a case I miss, such as multiplicities, surplus, a dead knot appearing although every knot "is live", or n <= 3?
2. Are Claims 2 and 3's constructions in the class, with the d and p values stated? Do any S3 or S4 failures or stalls hide there?
3. Before I grow them, predict the per-round junction counts, or at least their degree, for: Claim 2 with R = 3 (the 7-knot spider with arms of two), R = 4, and R = 6; and Claim 3 at depth 1 (10 knots: H, 3 M, 3 X, 3 K) and depth 2.
4. Is "five is the largest cap that bounds the dimension of all-live starts, and the bound is two" the right headline? What would you check first to break it?
