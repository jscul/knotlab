# Advisor question 1 (LOOP-CATALOGUE-20261119-001, before the freeze)

Analysis please, which I will check. The context is the cheapest parity growth of touching knots (FRESH-COUNT's complete-round
policy, fewest counts). Within a rule's scope, the junctions of round t are the clusters of t + 1 points of the unrolled candidate
map, where every cycle is opened out (the literature's universal cover). Its blocks are as follows.
- **Simplices.** For each knot w, the live knots sharing a distinction with w form a simplex.
- **Merged blocks.** Simplices sharing two knots merge into one block.
- **Hyperedges.** A first-round group of three or more (a hyperedge) is its own block, taken all or nothing.

The block graph has knots and blocks as points, joined by incidence. The owner's idea is that loops of logic are "like eddies in
a river that are shared across the universe ... 'core-libs' kind of processing". The coordinator asks:
1. which cycles of knots feed themselves (exponential growth), and why large growers' many cycles do not;
2. a catalogue of distinct self-feeding loops up to a stated size, each with its ratio as a root of its equation, whether it is
   the same under not-all-equal, and its interface (what a chain, a spare or another loop joined to it does to the ratio);
3. whether the catalogue is finite, a few families or unbounded, and whether a small generating set composes it.

## Pilot (disclosed)

**The eddy rule (v2).** A start feeds itself exactly when some piece of the block graph has a cycle and is not bare.
- **Bare** means one cycle; ordinary blocks that are pairs; no spares, a spare being an offshoot beyond the first-round demand;
  and knots off the cycle only as the third knot of a hyperedge.
- **Excluded** is any piece where two hyperedges meet at a knot. These are the cluster rule's known false rings (the referee's
  second break).

**On the census** (26,441 starts, five knots or fewer), it picks exactly the 13 rings, all rings of five with spares. The 3 bare
rings grow by 5 a round.

**On about a million random arrangements of 6 to 12 knots** (sizes 3 to 5, random touches, connected), I grew every start with a
cycle of blocks plus a control sample:
- 64 rule-eddies, all exponential;
- 0 exponential among about 13,000 grown non-eddies;
- 46 pieces with two hyperedges meeting at a knot, none exponential (they grow by dimension 1 or 2, or close);
- cycles through a single hyperedge are real eddies, and the rule's series equals the growth.

**Why growers' cycles don't feed.** Only 16 to 27% of a grower's knots are live, that is, still hold an open distinction. A loop
needs live knots at its candidates; its middles, the common neighbours, may be full. Growers average 3.9 to 19.5 chordless cycles
of knots, but only 0.5 to 1.4% of those are all-live. All-live ones of length 5 or at least 7 occur about 0.0002 per grower. A
cycle of 3 knots is a hyperedge, of 4 a pair with two common neighbours, of 6 two hyperedges, so none of those make loops. Loops
with a cycle of blocks run 2 to 6 per 20,000 growers.

**Minimal eddies.** These are starts that feed themselves, where removing any spare or any knot stops them. The search covered
simple knot graphs from networkx's atlas, sizes bare (shared plus first-round demand, at least 3) plus at most two spares, and
patterns up to renaming. It found:
- 5 knots: the ring of five with one spare: y^5 (1 + y) = 1, rate 1.1347.
- 6 knots:
  - the ring of five with a hanging knot: the same equation, 1.1347;
  - a theta (the ring 0-1-2-3-4, plus knot 5 touching 0 and 3), bare: y^5 (1 + 2y) = 1, rate 1.2298. It is rational, not
    algebraic: the two cycles share a merged block.
- 7 knots: the ring of seven with one spare: y^7 (1 + y) = 1.

Eight knots are running, all connected simple graphs (11,117) by augmentation. The rings of five, with or without a hanging knot,
were confirmed by growth to 23 rounds, equal to the rule.

**The product law I expect.** For a one-loop piece, y^L Π_e (1 + U_e(y)) = 1. L is the loop length in the candidate map (odd rings
of n knots give L = n; even rings of n ≥ 8 give two loops of n/2; rings of 3, 4 and 6 give none). The U_e are the side entries: a
spare gives U = y, a hanging knot with s spares gives y(1 + y)^s (JOIN-GROWTH's F_s), and an endless chain gives y/(1 − y). With
two independent loops the count is algebraic (RING-PAIR: U = y Π(1 + U), C λ^t t^(−5/2)).

## Planned freeze

- **E1–E3.** On fresh random samples at 6 to 14 knots, and on SCALE-SHARE's 64 regenerated chains:
  - every rule-eddy grows exponentially, its counts equal to the cluster rule's series;
  - every in-scope non-eddy grows polynomially or closes;
  - every piece with two hyperedges meeting at a knot is not exponential.
- **E4.** Growers' live share stays below 0.3 at n ≥ 6, and all-live chordless cycles are under 2% of a grower's cycles.
- **C1.** Every catalogue entry (minimal eddies to 8 knots) grows equal to its rule series to 40 rounds or 30,000 junctions, its
  counts satisfy its stated recurrence, and it is identical under not-all-equal for 14 rounds, by NAE-GROWTH's theorem, since
  eddies never close.
- **C2.** Interfaces, on each entry:
  - a spare at a loop knot multiplies the product by (1 + y);
  - a hanging lone knot by (1 + y);
  - a hanging knot with a spare by 1 + y(1 + y);
  - a pendant chain by 1/(1 − y);
  - a second loop joined at a knot turns the equation algebraic, with a rate above both.

  Each ratio is computed and the growth confirmed.
- **C3.** Rings of L = 9, 11, 13 knots with one spare, y^L (1 + y) = 1; rings of 8, 10, 12 with one spare, y^(n/2) (1 + y) = 1.
- **F.** The answer: unbounded in number, few in kind, generated by {a loop of length L ≥ 4, the spare, the hanging knot, the
  chain, the joint}.

## Questions

1. Is the eddy rule right, in particular "bare" with hyperedges? And can you explain why two hyperedges meeting at a knot kill the
   unrolling? My guess: both triples take a distinction of the shared knot in round 1, so they join in round 2 as candidates through
   it, and the cycle closes on itself in the real growth instead of unrolling.
2. Is the product law y^L Π(1 + U_e) = 1 right for every one-loop piece, including side entries inside merged blocks (the theta's
   1 + 2y)? Give the general statement for a loop through a block of k points, of which the loop uses two.
3. Is "minimal eddy" the right unit for "distinct self-feeding loops", or should the catalogue count loops (cycles of the candidate
   map with their entry multisets) rather than starts? What size bound is honest?
4. Which predictions are weakest, and what falsifier would you add? In particular, can any one-loop eddy have an equation outside
   y^L Π(1 + U_e) = 1, or a two-loop shape be rational, like the theta?
5. How would you state "finite, few families or unbounded" sharply? Is "the set of ratios is the set of roots generated by these
   pieces" a theorem I could prove from the cover model?
