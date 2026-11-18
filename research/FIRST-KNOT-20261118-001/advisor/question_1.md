You are a colleague reviewing a research design before it is frozen. Check the mathematics, attack the claims, propose sharper
predictions. Be concrete and terse; say plainly where a claim is false.

## Setting (from a finished study, FRESH-COUNT)

Parity growth. A junction is an even-parity constraint on binary distinctions (bits); a bit lies in one junction (loose) or two
(shared); junctions sharing a bit are neighbours. One round of the joining policy: live junctions hold loose bits; two live
junctions are candidates when they have a common neighbour; groups are the maximal sets of >= 3 pairwise candidates with no
neighbour common to all, plus candidate pairs in no such set; each live junction gives one loose bit to each of its groups; every
remaining loose bit gets a junction of its own (an offshoot, one parent); a junction in more groups than its loose bits stalls the
round. Each new junction gets k fresh bits from a count rule. Old allowed states are kept: k = 0 only if the junction's parity is
implied by the old equations. "Demand" = number of next-round groups containing a new junction.

Proved there, from ONE seed junction on a >= 3 bits: (T1) with no stall the pattern is the down-closed sets of the descent order of
the offshoots (Birkhoff), demand(I) = |min(Q \ I)|; (T2) one count c for every join survives iff c = a, giving N^a; else stalls at
round 2 (c <= a-2), 4 (c = a-1), 3 (c >= a+1); (T4) the fewest rule F: k = 0 if demand 0 and parity implied, else max(d, 3 - p, 1)
(p = parents; at least 3 bits per junction, the program's smallest knot), closes one seed into the Boolean 2^a pattern; under F an
offshoot with demand 1 starts an endless chain, and an offshoot with demand 0 whose parity is not implied gets 2 surplus bits whose
two offshoots then have demand 1. So with one count the dimension is the first knot's size, and three needs a three-place first knot.

## The new question (coordinator)

Is there a reason in the parity law or the joining rule why a growth begins with the smallest knot? First step: a three-place
against a four-place first knot under one count. Stop at a reason that prefers one, or a proof that nothing prefers either.

## Claims I intend to prove (attack them)

S1 (pieces). If the start is a set of junctions in which no two have a common neighbour (two knots apart, or two knots sharing one
bit), the growth splits into independent pieces, one per start junction J: the descendants of J grow exactly as a single seed with
l_J = (J's loose bits) bits would, because a junction's neighbours are its parents and children, which lie in its own piece or are
its start junction, and junctions of different pieces never share a neighbour. Only the implied-parity test is global.

S2 (one count, two first knots of sizes a, b >= 3). Apart: survives iff c = a = b (two copies of N^c). Sharing one bit: each has
a - 1 and b - 1 open bits; survives iff c = a - 1 = b - 1 (for c >= 2; T2 extends to a two-bit seed: c = 2 gives N^2, c >= 3
stalls at round 3), the pattern being two copies of N^c glued at the start. So first knots of different sizes never grow together
under one count, apart or touching; no size wins; touching lowers the dimension by one; two touching three-place knots grow
two-dimensionally.

S3 (fewest, two first knots). Apart: each closes into its 2^a pattern (the top takes every loose bit of its component: implied).
Sharing one bit h: a piece with 2 open bits (a = 3) has offshoots of demand 1, which never end: an N^2 piece. A piece with l >= 3
open bits grows the 2^l pattern, but its top's parity is not implied (the cut of the piece's junctions, start included, is the
top's bits plus h, and h is open, so no cut equals the top's bits alone; by the connectedness argument the only all-loose cuts are
empty or all loose bits), so F gives it one fresh bit; its lone offshoot has demand 0 and is not implied, so it gets two; their
offshoots have demand 1 and continue forever: an N^2 tail. Hence for every a, b >= 3 sharing one bit, the fewest counts grow two
copies of N^2 forever: two-dimensional, whatever the sizes.

S4 (cheapness). Each junction of a one-count growth multiplies the allowed states by 2^(c-1), least at the smallest admissible c.

Reading I intend to state: nothing in the law or the rule prefers the smallest first knot; the three of a lone knot is fixed by the
foundation's first emergence (two native recurrences joined by one contact: a three-variable relation); the parity law accepts every
size; touching knots under the fewest counts give two-dimensional growth for every pair of sizes, the number two coming from the
knot floor (three places, one shared).

## Pilot (my code, GF(2) implied test)

Two knots of sizes 3..5: apart, one count survives only at c = a = b; sharing one bit only at c = a-1 = b-1; mixed sizes: no count
survives (stall at rounds 2 to 4). Fewest: apart, both close; sharing one bit, alive at round 14 with 4 offshoots per round and
junctions per round rising by 2 (two N^2), for all nine pairs of sizes. Chains of three knots (3-3-3, 4-4-4) under fewest: 4
offshoots per round; chain 3-4-5: 3 per round; ring of three 3-knots and the star (a 3-knot with a 3-knot on each bit): close; ring
of four 3-knots: 4 per round.

## Questions

1. Are S1-S3 right? In S3, is the top's parity really never implied, and is the "lone offshoot gets two" step right when both pieces
   reach their tops in the same round? Any case where F stops instead?
2. Is there a reason in the law I am missing that prefers the three-place first knot? Candidates I considered: cheapness (restates
   the floor), atomicity (every a-place parity knot is a chain of a - 2 three-place knots through a - 3 hidden distinctions; the
   three-place one is the only one not composed of smaller knots), bits hidden (every parity knot hides exactly one bit; per
   distinction, the three-place one hides most). Does any of these act inside the growth? For instance: present a four-place first
   knot as two three-place knots sharing a hidden distinction; under one count that start (S2, sharing) grows two-dimensionally,
   while the single four-place junction grows N^4. Is "the dimension depends on the presentation, not the relation" a fair reading,
   given that the canonical knot test quantifies witnesses away?
3. Predictions to freeze (please sharpen): (Q1) S2 on every pair of sizes 3..6, apart and sharing, counts 2..8: survive exactly as
   stated, stall otherwise within 4 rounds; (Q2) S3 on the same pairs: apart closes (two 2^a), sharing grows exactly two N^2 pieces
   (offshoots per round constant at 4 from some round, junctions per round rising by 2), no forced bit; (Q3) the presented four-place
   knot (two 3-knots sharing a bit) under one count survives only at c = 2; (Q4) small starts of 3 or 4 knots (chains, rings, stars,
   sizes 3 and 4) under fewest: what do you expect? I see finite, linear and quadratic outcomes only.
4. Is S1-S3 known in some literature (growth of median graphs/cube complexes from several bases, distributive lattices glued)?
