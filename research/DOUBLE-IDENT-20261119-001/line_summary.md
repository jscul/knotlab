# The identification line: the cheapest growth as clusters of an unrolled map

19 November 2026, by Claude, at the coordinator's request. This is one page for the owner. It adds no evidence: every figure comes
from the linked records.
- **All refereed and confirmed:** the four identification proofs, the reading past the census (SCALE-THEOREM), the weightings test
  (WEIGHTINGS) and the cap on places (CAP-CHAINS).
- **Also refereed and confirmed:** the rings within five places (RING-CORES), which joins this line to the eddy catalogue.

## First: two dimensions are typical of how starts are drawn, not of the growth

The census found that most growing starts are two-dimensional, and the proofs below explain how. That "two is typical" is a fact
about the starts sampled, not a law of the growth (a Narrowing, logged in docs/CORRECTIONS.md).
- **Knots of at most five places keep two.** The census, SCALE-SHARE's samples, random pairing of places and growth by attaching
  knots one at a time all keep knots at three to five places. Under the last three, two dimensions are 80% to 100% of the growing
  starts in the proved class, and none of those has three. On the census, 82% of all growing starts are two-dimensional.
- **The cause is the cap, not crowding** (WEIGHTINGS' referee). In all seven weightings, uncrowded trees included, none of the
  25,133 growing starts in the class whose knots all have at most five places reaches three. Within five places, growth can
  still be exponential (127 of them).
- **Uniform random trees do not.** Here every knot gets the places its joins need. Read by the same proved theorem, three or more
  dimensions is 12% of growing starts at twelve knots and 37% at twenty, up to six.
- **Random extra lines make exponential growth common:** 11% at six knots, and 41% at twenty.

**What knot size bounds.** Suppose no knot is dead, so every knot keeps at least one open distinction. Then five places allow at
most two chains in any piece of the map. A tree-shaped start of such knots therefore grows in at most two dimensions, at every
size. This is proved.
- **Five is the threshold.** At six places any number of chains fits.
- **A dead knot lifts it.** A dead knot's places are all shared, so it joins its neighbours without costing them a place. With dead
  knots, any number fits even at five places.
- **Rings are different.** A ring of knots carries no chain, but it can still grow exponentially.

So "dimension is bounded by knot size" holds for tree-shaped starts with no dead knot, with the bound two at five places, and only
there.

## In plain words

Start from a set of touching knots and grow them by the cheapest parity growth. Then draw a second picture, the **map of joins**:
- a point for each live knot;
- a block for the knots around each knot, which are the pairs that can join through it;
- a dead-end point for each leftover open distinction;
- an endless chain where the floor of three places tops a junction up.

Open every loop of that map out into its endless branching form. The theorem is that the junctions the growth makes in round t are
exactly the clusters of t + 1 points of this unrolled map, each counted once:
- a junction's parents are the points its cluster can lose and still hang together;
- its open distinctions are the points just outside the cluster;
- a finished piece that has no loop and no chain, while another piece still grows, goes on through a **relay**: one point carrying two
  endless chains.

So the growth is decided by the map of joins alone, and the same few pieces recur everywhere:
- dead ends;
- endless chains;
- relays;
- loops, which are the catalogue's eddies when they offer a choice.

From this the growth's dimension can be read off a tree-shaped start. It is the largest number of chains in one piece, and a finished
piece counts two. That is why two dimensions are typical on the census: a piece with no chain relays, and a start is one-dimensional
only if each of its two pieces holds exactly one chain. Three or more needs three chains in one piece. With no dead knot and at most
five places that cannot happen (CAP-CHAINS). Past five places, or with dead knots, it can, and under uniform random trees it is common
from twelve knots (WEIGHTINGS). That is the Narrowing above.

## The proofs, and the tests past the census

| Proof | What it proves | Condition it adds or drops | Referee |
| --- | --- | --- | --- |
| [RING-IDENT](../RING-IDENT-20261119-001/ring_ident.md) | Junctions are the clusters of the unrolled map, every round, with parents and open distinctions. It rests on one inequality: a cluster and a shifted copy fit only in a cluster at least four points larger, because no loop passes through fewer than four knots | RING-PAIR's four conditions, plus a loop in the knot graph. Without the loop the rule fails inside RING-PAIR's stated scope (two stars joined at their centres): a Narrowing of RING-PAIR | Confirmed line by line |
| [CHAIN-IDENT](../CHAIN-IDENT-20261119-001/chain_ident.md) | The floor's endless chains hang from the knots' own leftover points, so they belong to the map. For tree-shaped starts the count per round is eventually a polynomial whose degree is one less than the most chains in a piece | Drops the no-floor conditions; needs every live piece to be infinite | Confirmed line by line (its control count corrected, not a block) |
| [RELAY-IDENT](../RELAY-IDENT-20261119-001/relay_ident.md) | A finished piece's top is not implied while another piece grows, so it carries a relay: k junctions in the k-th round after the top. A lone finished piece closes | Drops the infinite-piece condition | Confirmed line by line (the tally's reach stated: its 93% counts double-touch trees, which rest on DOUBLE-IDENT; simple trees 91%) |
| [DOUBLE-IDENT](double_ident.md) | Knots touching twice or more change nothing but the open counts, so all of the above holds for every multiplicity. A start with a single loose distinction closes at round 1 | Drops simplicity. The two block conditions are read on live knots; no stall and at least two loose distinctions are needed | Confirmed (its classification of all 26,441 reproduced exactly) |
| [SCALE-THEOREM](../SCALE-THEOREM-20261119-001/scale_theorem.md) (frozen run) | Read by the theorem, SCALE-SHARE's samples of 5 to 20 knots are 73–83% in the class; in it two dimensions rise from 85% to 98% of growers, and three never occurs | Nothing new; it measures the class's reach under one weighting | Confirmed (every figure reproduced; two wording points folded in) |
| [WEIGHTINGS](../WEIGHTINGS-20261119-001/weightings.md) (frozen run) | Under seven weightings frozen before reading, two stays typical only where knots have at most five places, crowded or not. Under uniform random trees three or more is 12% at twelve knots and 37% at twenty; extra lines make exponential growth common. All 1,226 regrown samples agree with the theorem, 622 of them three- to six-dimensional or exponential | Nothing new; it narrows "two is typical" and overturns A106 as a reading of the growth | Confirmed (the samplers checked against their exact laws; every one of 6,271 hard in-class starts regrows as read; the cause credited to the cap, not crowding) |
| [CAP-CHAINS](../CAP-CHAINS-20261119-001/cap_chains.md) (proof) | With no dead knot and at most five places, the knots form one line or one ring with single knots hung on it, so a piece carries at most two chains, and a tree start grows in at most two dimensions. Six places, or dead knots at five, allow any number | Adds a cap on places and no dead knot | Confirmed line by line (rechecked to 13 knots; the ring with a leaf grows at the root of x⁸ = x + 1, about 10% a round) |
| [RING-CORES](../RING-CORES-20261119-001/ring_cores.md) (proof) | Within five places, with no dead knot, the eddies are exactly the rings carrying a hung knot or a spare. The count is rational with denominator 1 − W, where W is a product of three kinds of factor, and the rate is the root of W(1/x) = 1, at most the golden ratio for rings of live knots. 23,098 rings grow exactly as the formula says | Adds nothing; it reads the cap's ring cores | Confirmed (the golden-ratio ceiling is for rings of live knots: dead knots go faster, a Narrowing) |

## On what share of the census

The touch census has 26,441 arrangements of up to five knots. 15,431 do not stall at once. The figures below rest on DOUBLE-IDENT
(confirmed), since most census arrangements have knots touching twice. On simple knot graphs alone (RING-IDENT to
RELAY-IDENT, all confirmed), the growing trees are two-dimensional in 266 of 292.
- **The class** (no first-round group of three, no two live knots with two common neighbours, at least two loose distinctions)
  holds 11,512 arrangements. All of them agree with the theorem round by round, in each junction's parents and fresh count.
- **Two more groups behave exactly as stated:** 727 with one loose distinction close at round 1, and 234 have none. With them, 12,473
  arrangements, 81% of those that run, follow the theorem.
- **The growth class** read off the map (closes, one or two dimensions, or exponential) equals the measured one on all 12,473.
- **Of the census's 9,564 two-dimensional growths,** 8,108 (85%) are in the class:
  - two chains in one piece: 3,525;
  - a relay: 1,801;
  - both: 2,782.

## Known mathematics, and what our reading adds

- **Known, cited once.**
  - Lattice animals (connected clusters) on tree-like covers: the Bethe lattice and Husimi trees (Fisher and Essam 1961; Harary and
    Uhlenbeck 1953).
  - Hyperbolic automorphisms of trees and their axes (Serre, *Trees*, 1980).
  - Block graphs and their non-cut points (Harary 1963).
  - "Remove a non-cut point" as reverse search over connected induced subgraphs (Avis and Fukuda 1996).
  - The algebraic and rational counts of animals on such covers (Drmota, Lalley, Woods; Flajolet and Sedgewick).
  - Caterpillars, the trees whose non-leaves form a path (Harary and Schwenk 1973). Leaves and degrees of uniform random labelled
    trees (Rényi 1959; Moon 1970). Configuration models (Bollobás 1980).
- **What our reading adds.**
  - The cheapest parity growth is exactly this animal count on its own map of joins. That holds for every round, with parents and
    open distinctions, and with the floor's chains and the relays included.
  - So the growth's typical shapes become theorems with named mechanisms: dead ends, chains, relays and loops. Two dimensions are
    typical on the census because finished pieces relay, and because five places with no dead knot allow at most two chains in a
    piece.

## The open 15%

1,456 two-dimensional growths, and 2,958 arrangements in all, have a first-round group of three knots, or two live knots with two
common neighbours. Both of CLUSTER-ALL's known breaks sit there. The unrolled map of blocks is the wrong object for them: a group of
three that closes a loop makes a cycle of three blocks, and the key inequality then gives only three new points, not four. A different
complex is needed. It stays in the basket as the cycles direction (`RING-IDENT-20261119-001#3`).
