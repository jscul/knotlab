You are a colleague; I need a proof idea, concretely. Be terse; say plainly if my reading is wrong.

Setting. Parity growth by a complete-round joining rule. Junctions are even-parity constraints on bits; a bit lies in one junction
(loose) or two (shared); junctions sharing a bit are neighbours. Each round: live junctions (with loose bits) are candidates when
they share a neighbour; groups = maximal sets of >= 3 pairwise candidates with no common neighbour, plus candidate pairs in none;
each live junction gives one loose bit to each group; leftover loose bits become one-parent junctions; each group/leftover becomes a
new junction on those bits plus k fresh bits, k = the number of groups of the next round containing it (its demand), at least
3 - (parents), at least 1 unless its parity is implied. So with no surplus the growth is pure "cube completion": the new junctions'
candidate pairs and cliques are joined, round by round.

The start: a ring of five knots R0..R4, R_i sharing one bit with R_{i+1} (indices mod 5). Each R_i has 2 loose bits except R4, which
has 3 (a five-place knot). With all five of four places the growth is a cylinder: round t has 5 junctions J_i^t with parents
J_{i-1}^{t-1}, J_{i+1}^{t-1} (pairs two apart along the ring share a neighbour), forever, one-dimensional.

With R4 of five places, its extra bit becomes one offshoot o in round 1 (demand 2: it pairs with the two round-1 junctions that took
bits from R4); no other offshoot is ever made. The junction counts per round are (round 0 = the five knots)
5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 21, 24, 28, 32, 36, 40, 45, 52, 60, 68, 76, 85, 97, 112, 128, 144, 161, 182, 209, 240, 272,
305, 343, 391, 449, 512, 577, 648, 734, 840,
and Berlekamp-Massey finds c(t) = c(t-5) + c(t-6) exactly on all 41 terms (order 6). Parents and demands of junctions grow without
bound (by round 22 junctions with 6 parents and demand 7 exist).

My reading: completing squares (and cubes) around a pentagon is the literature's right-angled pentagon tiling of the hyperbolic
plane ({5,4}); the all-four-place ring is held to a cylinder because each knot has only two loose bits, and the five-place knot's
extra bit puts one point of "excess" in, after which the completion grows like a hyperbolic tiling: exponentially, with the
recurrence coming from the tiling's layers.

Questions:
1. Is this reading right? If not, what is the structure? (Note parents grow without bound, so it is not a two-dimensional tiling's
   vertex set of bounded degree.)
2. Give a proof strategy for c(t) = c(t-5) + c(t-6), or at least for exponential growth (a lower bound like c(t) >= 2 c(t-6) or a
   substructure that doubles). What invariant or decomposition should I compute to make it a proof (for example, a finite set of
   local types with a substitution, or an identification of the round-t junctions with words/compositions of t into 5s and 6s)?
3. What would you predict for rings of n knots with one five-place knot (n = 4, 6, 7, 8), and for two or three five-place knots?
4. Plain words: what does the ring do that a chain cannot? (The owner asks about "folded, overlapping structure" and "a logic based
   fractal".)
