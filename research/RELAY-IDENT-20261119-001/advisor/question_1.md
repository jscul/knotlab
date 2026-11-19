# Question for the advisor (RELAY-IDENT-20261119-001, before freezing the statement)

You have no tools. Answer only from this text; check the argument and say exactly where it fails.

**Background (you checked it).** CHAIN-IDENT: with the floor allowed, X⁺ = live knots' blocks, s = open − d pendant points per live
knot, R(open) = 0/1/2 rays per pendant point (open ≥ 3 / 2 / 1). Under (S3), (S4) and (S5⁺) every piece of X⁺ holding a live knot is
infinite, round t's junctions are the deck orbits of clusters of t + 1 points, parents = R*(C), loose = |∂C|. You noted that (S5⁺)
excludes the relay: a finite ray-free piece's top has ∂ = ∅ and is implied only if nothing else is live.

**Claimed theorem (relays).** Under (S3) and (S4) only (K connected, simple, ≥ 2 knots). Let the pieces of X⁺ holding a live knot be
Y_1, …, Y_q (pieces never interact: a junction's parents stay in its piece, so groups and candidates are within a piece; the only
global coupling is the implied test). Then:
- an infinite piece follows CHAIN-IDENT's clusters for all t;
- a finite ray-free piece Y (deck-trivial: its incidence graph is a tree) follows its clusters for t ≤ |Y| − 1, its top being the
  junction of Y itself at round r = |Y| − 1, with p = |R*(Y)| ≥ 2 parents and demand 0;
  - if q = 1, the top takes every loose distinction (implied), gets 0, and the growth closes;
  - if q ≥ 2, the top is not implied and gets max(0, 3 − p, 1) = 1 fresh distinction, and from then on Y's junctions are
    J(i, l), i + l = k − 1, at round r + k (k ≥ 1): J(0, 0) the relay (one parent: the top; fresh 2), J(i, 0) and J(0, l) chain ends
    (one parent; fresh 2), J(i, l) with i, l ≥ 1 groups with parents J(i − 1, l) and J(i, l − 1) (fresh 2). So Y makes k junctions
    in round r + k: the clusters of "Y plus a point z with two rays", where z enters only with all of Y.

**Proof plan.**
1. Pieces don't interact (parents within a piece; candidates need a common neighbour, a parent).
2. Before the top every cluster C ⊊ Y has ∂C ≠ ∅, so CHAIN-IDENT's count (fresh table) holds; the top is the first junction of Y with
   d = 0.
3. Implied at the top iff every loose distinction of the presentation lies in Y's round-(r − 1) junctions, i.e. iff no other piece
   holds a loose distinction then. If q ≥ 2: another piece is infinite (always loose bits), or finite and still growing, or finishing
   at the same round (its own parents hold bits), or finished earlier and (by induction on finishing order) relaying, whose
   J's always hold 2 loose distinctions. So not implied.
4. After the top, a direct induction: J(i,l) and J(i′,l′) of one round share a parent iff |i − i′| = 1 (adjacent); no three are
   pairwise candidates; so the groups are the adjacent pairs, giving J(i, l + 1); chain ends J(k−1, 0) have one candidate (d = 1), get
   2, leftover 1 → J(k, 0); the relay J(0,0) has no candidate (the top has one child), gets max(0, 2, 1) = 2 → J(1,0), J(0,1); groups
   J(i,l) (i, l ≥ 1) have two candidates, d = 2, get 2. None of the p = 1 ones is implied (their parent holds ≥ 2 loose bits, or for
   the relay, another piece holds bits by step 3).

**Checked so far (machine):** path of five ({B, D} relays from round 1: growth 5, 5, 6, 8, 10, … equals the cover count of {A, C, E}
with two chains plus the relay's k), the spider with three legs of two ({1, 3, 5} relays from round 2), two stars joined at their
centres (both pieces finish at round 1 and both relay), the star K_{1,3} (one finite piece, closes). A full comparison on every start
of 2 to 7 knots is running.

**Questions.**
1. Is each step sound? In particular step 3's case analysis (pieces finishing in the same round; a piece whose top forms while
   another piece's relay is already running), and step 4's claim that no three J's are pairwise candidates.
2. Is "the growth with relays equals the clusters of X⁺ with, for each finite ray-free piece, a point z with two rays attached to the
   whole piece" the right single statement? Does it make CLUSTER-ALL's "a relay feeds two chains" exact, including the dimension
   (Theorem 2 extended: a relay adds 2 to its piece's chain count, but the piece's own count is then only linear)?
3. Predict the dimension of the path of seven knots and of a spider with legs 2, 2, 2, 2, by this theorem.
