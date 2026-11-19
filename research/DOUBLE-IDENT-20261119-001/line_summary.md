# The identification line: the cheapest growth as clusters of an unrolled map

19 November 2026, by Claude, at the coordinator's request. This is one page for the owner. It covers four proofs and adds no
evidence: every figure comes from the linked records.

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
piece counts two. That is why two dimensions are typical: a piece with no chain relays, and a start is one-dimensional only if each of
its two pieces holds exactly one chain.

## The four proofs

| Proof | What it proves | Condition it adds or drops | Referee |
| --- | --- | --- | --- |
| [RING-IDENT](../RING-IDENT-20261119-001/ring_ident.md) | Junctions are the clusters of the unrolled map, every round, with parents and open distinctions. It rests on one inequality: a cluster and a shifted copy fit only in a cluster at least four points larger, because no loop passes through fewer than four knots | RING-PAIR's four conditions, plus a loop in the knot graph. Without the loop the rule fails inside RING-PAIR's stated scope (two stars joined at their centres): a Narrowing of RING-PAIR | Confirmed line by line |
| [CHAIN-IDENT](../CHAIN-IDENT-20261119-001/chain_ident.md) | The floor's endless chains hang from the knots' own leftover points, so they belong to the map. For tree-shaped starts the count per round is eventually a polynomial whose degree is one less than the most chains in a piece | Drops the no-floor conditions; needs every live piece to be infinite | Confirmed line by line (its control count corrected, not a block) |
| [RELAY-IDENT](../RELAY-IDENT-20261119-001/relay_ident.md) | A finished piece's top is not implied while another piece grows, so it carries a relay: k junctions in the k-th round after the top. A lone finished piece closes | Drops the infinite-piece condition | **Referee pending** |
| [DOUBLE-IDENT](double_ident.md) | Knots touching twice or more change nothing but the open counts, so all of the above holds for every multiplicity. A start with a single loose distinction closes at round 1 | Drops simplicity. The two block conditions are read on live knots, and at least two loose distinctions are needed | **Referee pending** |

## On what share of the census

The touch census has 26,441 arrangements of up to five knots. 15,431 do not stall at once.
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
- **What our reading adds.**
  - The cheapest parity growth is exactly this animal count on its own map of joins. That holds for every round, with parents and
    open distinctions, and with the floor's chains and the relays included.
  - So the growth's typical shapes become theorems with named mechanisms: dead ends, chains, relays and loops. Two dimensions are
    typical because finished pieces relay.

## The open 15%

1,456 two-dimensional growths, and 2,958 arrangements in all, have a first-round group of three knots, or two live knots with two
common neighbours. Both of CLUSTER-ALL's known breaks sit there. The unrolled map of blocks is the wrong object for them: a group of
three that closes a loop makes a cycle of three blocks, and the key inequality then gives only three new points, not four. A different
complex is needed. It stays in the basket as the cycles direction (`RING-IDENT-20261119-001#3`).
