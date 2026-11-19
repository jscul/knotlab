# Question for the advisor (JUNCTION-KINDS-20261119-001, before the freeze)

You have no tools. Do not describe files or runs: answer only from this text, and say where you are unsure.

**Setting.** A parity growth in complete rounds. A junction is an even-parity constraint on its distinctions (bits); a bit is loose
while it lies in one junction. Each round: live junctions (those born last round with fresh bits) form groups (maximal sets of at
least three pairwise "candidates" with no common neighbour, plus remaining candidate pairs; two live junctions are candidates when
they share a neighbour). Each live junction gives one loose bit to each group containing it; leftover loose bits get one-parent
junctions (offshoots). Each new junction gets fresh bits = max(d, 3 − p, 1), where p = its parents and d = its demand (the number of
next-round groups containing it). Counts per round are c(t).

Where a "cluster rule" applies (the catalogue's eddies), round t's junctions are the deck orbits of connected sets of t + 1 points in
the universal cover of a finite "candidate complex", and the count is P(y) + Q(y)/(1 − W(y)) by a transfer argument along the
unrolled loop (W = the loop's round-weight). In the rule's break shapes (groups of three overlapping another block in two knots) the
cover model is wrong from round s + 2 on, yet the counts are still rational with family round-weights. Ten such starts (eight knots
each) have W = y²(1 + y): their counts satisfy c(t) = c(t − 2) + c(t − 3) exactly (e.g. 11, 15, 19, 26, 34, 45, 60, 79, 105, ...).

The planned direction was "a transfer between kinds of junction": classify junctions by local pattern (parents, fresh, demand,
neighbours' kinds, refined) and look for a finite set of kinds whose counts follow a fixed matrix (a junction with p parents shared
1/p to each).

**Pilot facts (mine, checked).**
1. Local labels never settle, even on the catalogue's own eddies (the ring of five with a spare, etc.), where the finite cover
   transfer is exact: a round's largest parent count and largest fresh count grow roughly linearly (catalogue: max parents 2 → 6,
   max fresh 3 → 7 over 24 rounds; the ten break-shape starts: max parents 3 → 10, max fresh 4 → 15). Distinct (parents, fresh)
   labels per round grow (catalogue 3 → 11; break shapes 4 → 52).
2. Refining by neighbours' kinds (depth 1 to 3) makes it worse: kinds per round grow at about the count's rate.
3. Forward kinds (kind_h(j) = multiset of (kind_{h−1}(child), 1/p(child))): the partition stabilises in depth (depth 4 equals depth
   5 on the window) but kinds per round still grow, slowly in the catalogue (9 → 13), fast in the break shapes (79 → 183 per round,
   about ×1.17 a round).

**My reading.** A junction is a cluster whose parents count its removable points, which grow with its size; so no finite set of
*junction* kinds can carry the counts, in any eddy. The cover's finite transfer is over positions along the loop (the ends of a
cluster), not over kinds of junction.

**Questions.**
1. Is that reading right? Is there an argument that a nonnegative finite transfer on junction kinds (a partition of each round's
   junctions with N(t+1) = M N(t)) is impossible when local degrees grow without bound, or can a coarse partition still work (for
   instance one class per residue of the loop, with M carrying the shares)? Give the strongest version you can.
2. What finite object, read natively from the growth (no cover drawn by the observer), should replace "kinds of junction" for the
   break shapes? Candidates I see: (a) ends of junctions, if a junction's two ends can be read from its parents; (b) kinds of loose
   bit, (child, removable point) pairs; (c) a "spine": for c(t) = c(t − 2) + c(t − 3), a native map sending each round-t junction to
   one junction of round t − 2 or t − 3, bijectively. Which is most promising, and how would you define it so it is checkable?
3. Propose a frozen test (three to five falsifiable predictions, at least one risky) for the ten starts with controls (the five
   catalogue eddies; starts whose corrected W is y⁴(1 + y)² and so share the rate but not W). Name the cheapest discriminator.
