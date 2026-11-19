# Relays: the count when a finished piece goes on

Status: Proved

Ticket `RELAY-IDENT-20261119-001A`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-IDENT-20261119-001#1`. This
completes `CHAIN-IDENT-20261119-001A-P001` by dropping its (S5⁺). The advisor checked the statement before the freeze. Its fixes
are folded in: step 3's invariant over all pieces, the relay as the pendant rule applied to the top, and the small cases written
out.
`machine_check.py` is a separate algorithm in the same task. Referee pending.

## Setting

As in CHAIN-IDENT:
- the cheapest parity growth;
- the knot graph K, connected and simple, with at least two knots;
- the bare convention;
- the extended complex X⁺: the live knots' blocks, s = open − d pendant points per live knot, and R(open) = 0, 1 or 2 rays per
  pendant point.

The class is (S3) and (S4) only.
- A **piece** is a component of X⁺ holding a live knot; let q be their number.
- A piece is **infinite** when it holds a cycle of the incidence graph or a ray, and **finite** otherwise.
- A finite piece Y is a finite tree of blocks, so its cover is Y itself. Its **top** is the cluster of all its |Y| points.
- **Finite pieces occur only when K is a tree.** If K has a cycle, every component of X meets it (RING-IDENT's Lemma 0), so every
  piece is infinite.
- **A finite piece has |Y| ≥ 2.** A live knot with no X⁺-neighbour has d = 0, so its open distinctions are pendant points. If it
  has one or two of them, those points carry rays and the piece is infinite. So it has at least three leaf pendant points.

**The relayed complex.** For each finite piece Y, when q ≥ 2, treat the top as a knot with open 1 and demand 0, and apply the
pendant rule to it: one pendant point z_Y (the **relay point**), carrying R(1) = 2 rays. So a cluster holds z_Y only if it holds all
of Y. The clusters of Y are then those of Y, together with Y ∪ {z_Y} ∪ A ∪ B, where A and B are prefixes, possibly
empty, of z_Y's two rays.
- For such a cluster, R* is {z_Y} when A = B = ∅, and otherwise the tips of the nonempty prefixes.
- Its boundary is the next point of each ray. For the top Y itself it is {z_Y}.

## Theorem 4 (the identification with relays)

In the class, for every t ≥ 0, the junctions born in round t are in bijection with the orbits of clusters of t + 1 points of the
relayed complex holding a knot, together with the non-live knots at t = 0. As in RING-IDENT:
- parents correspond to R*;
- loose distinctions after birth correspond to the boundary.

In particular:
- **an infinite piece** follows CHAIN-IDENT's count in every round;
- **a finite piece Y** follows its own clusters up to its top, at round r_Y = |Y| − 1, and then:
  - if q ≥ 2, it makes k junctions in round r_Y + k, for every k ≥ 1;
  - if q = 1, the growth closes after the top.

## Theorem 5 (the dimension of a tree start)

Let K be a tree in the class, with q ≥ 2 pieces, and let D be the largest of:
- the ray counts R_Y of the infinite pieces;
- 2, if some piece is finite.

Then the number of junctions per round is eventually a polynomial of degree D − 1, with these leading coefficients:
- D ≥ 3: (Σ_{R_Y = D} N_Y)/(D − 1)!;
- D = 2: Σ_{R_Y = 2} N_Y plus the number of finite pieces;
- D = 1: Σ_{R_Y = 1} N_Y.

Here N_Y is CHAIN-IDENT's number of clusters of Y's core holding every ray base. If q = 1 and the piece is finite, the growth closes.

So a relay feeds exactly two chains, as `CLUSTER-ALL-20261119-001` read it, and a tree start's dimension is
max(largest number of chains in an infinite piece, 2 if any piece is finite).

## Proof of Theorem 4

**Step 1: pieces do not interact.** A junction's parents lie in its piece, by induction on its round: a round-1 junction comes from a
candidate pair of knots, adjacent in X⁺, or from a knot's offshoot. Candidates need a common neighbour, which for round t ≥ 1 is a
common parent. So groups, offshoots and demands are computed within each piece. The only coupling between pieces is the implied
test: "takes every loose distinction of the presentation".

**Step 2: infinite pieces, and finite ones before the top.** CHAIN-IDENT's proof applies piece by piece. Its only use of (S5⁺) was
∂C ≠ ∅, for the fresh count d ≥ 1. In an infinite piece this holds for every cluster. In a finite piece it holds for every cluster
except the top, so the induction runs through round r_Y − 1 and makes the top at round r_Y.
- The top has p = |R*(Y)| ≥ 2. If Y has two knots, both are non-cut points. If it has one knot w, then w has at least three leaf
  pendant points: d_w = 0 and open_w ≥ 3 would otherwise make Y infinite or not live. Every non-cut point is in R*.
- The top has demand 0, since its cluster has no extension.

**Step 3: implied junctions.** A new junction gets max(d, 3 − p, 1) fresh distinctions, or exactly d if it takes every loose
distinction of the presentation (the program's rule, `freelib.floored` of `FRESH-COUNT-20261118-001`: no floor at an implied
junction).
- **Where loose distinctions are.** They lie in the pieces: a non-live knot holds none, and the floor's distinctions sit on live
  knots. Every loose distinction of round t is taken in round t + 1, by a group or by an offshoot.
- **Invariant (q ≥ 2).** At every round, each piece's latest junctions hold at least one loose distinction. They are proper
  clusters (∂ ≠ ∅), a top (1 distinction, from this step) or relay junctions (2 each, step 4).
  - A junction's parents lie in its own piece, so it never takes another piece's distinctions.
  - So when q ≥ 2 no junction is ever implied. This covers two pieces finishing in the same round, a top forming while another
    piece's relay runs, and the relay point J(0, 0), which takes all of Y's loose distinctions.
- **Before the top, the implied rule changes nothing.** Every cluster there has d ≥ 1. Its only one-parent clusters are {w, o} with
  o a leaf pendant point (open_w ≥ 3), which have d = open_w − 1 ≥ 2. So max(d, 3 − p, 1) = d either way.
- **At the top.** The top takes one distinction from each parent, which are all of Y's round-(r_Y − 1) junctions.
  - If q = 1, these hold every loose distinction of the presentation, so the top is implied: it gets d = 0 and the growth closes.
  - If q ≥ 2, it is not implied, and gets max(0, 3 − p, 1) = 1 fresh distinction (p ≥ 2). Its boundary is {z_Y}, as the pendant
    rule with open 1 says.

**Step 4: after the top, if q ≥ 2.** Write J(i, l) for the junction of the cluster Y ∪ {z_Y} ∪ (a_1..a_i) ∪ (b_1..b_l). Claim: the
junctions of Y born in round r_Y + k are exactly the J(i, l) with i + l = k − 1, and each holds 2 loose distinctions. By induction on
k.
- **k = 1.** The top's single loose distinction has no candidate, since the top's only child would be this junction. So it becomes
  an offshoot, J(0, 0), with p = 1 and demand d = 0. It is not implied (step 3), so it gets max(0, 2, 1) = 2.
- **The step.** The junctions of round r_Y + k are J(i, l) with i + l = k − 1.
  - **Parents.** J(i, l) has parents J(i − 1, l) (if i ≥ 1) and J(i, l − 1) (if l ≥ 1); the J(i, 0) and J(0, l) have one.
  - **Candidates.** Two of them share a parent exactly when they are neighbours in i, so no three are pairwise candidates.
  - **Groups.** The groups are the neighbouring pairs {J(i, l), J(i − 1, l + 1)}, which become J(i, l + 1) with exactly those two
    parents.
  - **Offshoots.** A chain end J(k − 1, 0) has one candidate, so d = 1. It gets max(1, 2) = 2, gives one distinction to its group,
    and its leftover becomes the offshoot J(k, 0); likewise J(0, k − 1).
  - **Two-chain junctions.** A J(i, l) with i, l ≥ 1 has two candidates, d = 2, and gets max(2, 1, 1) = 2 with no leftover.
  - **Implied.** None is implied, by step 3's invariant.
  - So round r_Y + k + 1 holds exactly the J(i, l) with i + l = k.
- **The dictionary.** The relayed complex's clusters of |Y| + k points beyond Y are exactly the Y ∪ {z_Y} ∪ A ∪ B with |A| + |B| = k
  − 1. There are k of them, and they match the J(i, l) with the stated parents (R*) and loose distinctions (boundary). ∎

## Proof of Theorem 5

**The pieces.** For K a tree, Γ is trivial (CHAIN-IDENT, Theorem 2). An infinite piece is then a finite core with rays, and counts
as in CHAIN-IDENT's Theorem 2: eventually a polynomial of degree R_Y − 1 with leading coefficient N_Y/(R_Y − 1)!. A finite piece,
with q ≥ 2, makes k junctions in round r_Y + k: degree 1, leading coefficient 1.

**The sum.** c(t) is the sum over pieces, plus the non-live knots at t = 0. The largest degree is D − 1, and the coefficients at that
degree add. ∎

## Corollary 6 (tree starts in the census)

For a bare tree with at least four knots, the two pieces are K's two parity classes, so q ≤ 2. Each class has as many rays as it has
leaves hanging from a knot of degree 2 (CHAIN-IDENT, Corollary 3). So:
- **Dimension two** arises in three ways:
  - one class with two such leaves;
  - a class with none, which is finite and relays, while the other class has at most two;
  - the two smallest trees, K2 and the path of three knots.
- **Dimension one** needs both classes to have exactly one such leaf each, as in the path of four knots.
- **Three or more** needs three such leaves in one class, as in the spider with three legs of two (dimension 3).

Two is typical for small trees because a class without such leaves always relays. Every tree start with a ray-free class therefore
has dimension at least two, and more than two needs three such leaves in one class, which takes at least seven knots.
- **The census tally** (ticket B, `experiments/RELAY-IDENT-20261119-001B/`). On the touch census's simple trees that do not stall,
  this dimension equals the measured one in 307 of 307.
- **Tree-shaped growths.** Every growing tree-shaped arrangement of up to five knots has dimension 1 or 2, and 3,753 of 4,055 have
  two. A relay is part of the reason in 2,678 of them.

## Validation

**`machine_check.py`.** It runs every connected simple knot graph on 2 to 7 knots, at bare sizes and with one surplus distinction
at each knot in turn: 218 starts with (S3) and (S4). On each it compares, per round to t = 6, the multiset of (parents, fresh) from
the growth with the relayed complex's (|R*|, |∂|). All 218 agree:
- 81 with chains only;
- 115 with at least one relay;
- 22 that are a single finite piece and close.

The relayed model writes the top as (|R*(Y)|, 1), the relay point as (1, 2), the chain ends as (1, 2) and the two-chain junctions as
(2, 2).

**The advisor's predictions** were made from the statement before the larger cases were grown. Both hold:
- the path of seven knots grows 7, 7, 7, 8, 10, 12, …;
- the spider with four legs of two (nine knots, beyond the machine check) grows 9, 14, 18, 25, 40, 62, 91, …, which is
  C(t + 3, 3) + t + 1 from round 4 on: four chains in the centre's class, and a relay in the other.

**Named cases.** These are part of the run:
- the path of five knots (its class {B, D} relays from round 1);
- the spider with three legs of two (its class {1, 3, 5} relays from round 2);
- two stars joined at their centres (both pieces finish at round 1, and both relay);
- the star with three leaves (one finite piece, which closes).

**Aside.** CHAIN-IDENT's machine check counts a non-live knot twice. That is harmless there, since its class has none. This check
counts it once.
