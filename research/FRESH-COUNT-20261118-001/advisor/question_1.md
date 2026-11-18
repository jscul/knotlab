You are a colleague reviewing a research design before it is frozen. Please check the mathematics, attack the claims, propose
predictions, and answer the word questions at the end. Be concrete and terse. Say plainly where a claim is false.

## Setting (parity growth, from an earlier study)

A junction is an even-parity constraint on binary variables ("bits", the program's "distinctions"). A bit lies in one junction
(loose) or two (shared). Two junctions are neighbours when they share a bit. Growth starts from one junction on a loose bits (the
seed; a >= 3, since the program's smallest knot has three places). One round of the joining policy (from CUBIC-FROM-A-KNOT):
live junctions hold loose bits; two live junctions are candidates when they have a common neighbour; a valid set is a set of >= 3
pairwise candidates with no neighbour common to all of them; the groups are the maximal valid sets (the original policy instead
caps groups at three: every valid triple) plus every candidate pair contained in no valid set; each junction gives one loose bit to
each group containing it; every remaining loose bit gets its own one-parent junction (a "singleton"). If a junction is in more
groups than it has loose bits, the round is unavailable (a stall). Each group/singleton becomes a new junction on its chosen bits
plus k fresh bits; old allowed states are all kept as long as k >= 1, or k = 0 when the new junction's parity is already implied.
Every loose bit is consumed every round, so the live junctions after a round are the new ones. With k = 3 for every junction, the
original study showed the rounds build the incidence of the orthant N^3 (junction at v, its fresh bits are v -> v + e_i), with bond
balls Theta(r^3). Its referee noted the three was put in by the law: k = 2 gives N^2, k = 4 with groups capped at three stalls at
round 4. Bond distance: least size minus one of a minimal dependency (bond = minimal cut of the junction graph with loose bits wired
to one outside vertex) containing both bits. A later study showed bond distances up to five determine the junctions when k = 3.

## The question (coordinator's)

Let a rule choose k for each new junction, reading only bond distances (no names, no history). Can it settle its own dimension
(bond-ball growth exponent) without being told a number? What growth is typical, rare or forced? Does the stall at four single out a
number?

## What I believe I can prove (please attack)

T1 (Birkhoff structure). Suppose every new junction gets k >= d, where d = the number of multi-parent groups containing it in the
next round (computable by lookahead from the current incidence). Then after round t the junction graph, directed old -> new, is
the cover graph of the elements of rank <= t of J(Q), the distributive lattice of order ideals of the poset Q whose elements are the
one-parent junctions (join-irreducibles), ordered by descent; junction v <-> the ideal of one-parent junctions it descends from (or
equals); rank = round. The groups of round t+1 are exactly the lower-cover sets of the non-principal ideals of size t+1; d(I) = number
of non-principal upper covers of I; the k - d surplus fresh bits of I become new join-irreducibles whose down-set minus themselves is
I. A count k < d stalls the next round. Proof idea: induction; the candidate graph on rank-t ideals is "intersect in t-1 elements";
a family of >= 3 t-sets pairwise meeting in t-1 elements is a sunflower with a (t-1)-core (whose core is a present common lower
cover, so invalid) or lies inside a (t+1)-set (co-star; no common neighbour, valid; maximal = all lower covers of the union, all of
which are ideals of size t hence present). Every ideal of size t+1 is either principal on a new join-irreducible or has >= 2 maximal
elements and is built by a group.

T2 (one count for every join). From an a-seed, the policy with groups of any size and one count c for every new junction runs
forever iff c = a, and then builds N^a = J(a disjoint chains). Otherwise: c <= a-2 stalls at round 2 (each child of the seed is in
a-1 pairs); c = a+m with m >= 1... precisely c >= a+1 stalls at round 3 (pair junction P_ij is in a-2 triangles plus 2(c-a+1) pairs
with surplus singletons of c_i and c_j, needs a-2+2m' <= c = a-1+m' with m' = c-a+1, i.e. m' <= 1); c = a-1 stalls at round 4 (the
triangle junction T_ijl is in a-3 four-set groups and 3 pairs with the surplus singletons of the three pair junctions: demand a > a-1).

T3 (the cap of three). With groups capped at three and one count c: runs forever iff c = a <= 3. For a >= 4 and c = a, round 4
stalls: a level-3 junction e_i+e_j+e_l has demand 3 + 3(a-3) > a (each support-4 child's four parents form four valid triples). So
from one knot (a >= 3) with the cap and one count, exactly three. The three is the cap's (and the knot floor rules out two).

T4 (fewest counts). Rule F: k = max(d, 3 - p) (p = old bits taken; the knot floor: every junction has >= 3 bits), raised to 1 if it
would be 0 and the junction's parity is not implied. From an a-seed, F builds the Boolean lattice 2^[a] (Q = the a seed bits as an
antichain): level j junctions have j parents and a - j fresh bits, all junctions have a bits; the top's group is all remaining loose
bits so its parity is implied and it gets k = 0; growth stops after round a; 2^a junctions, a 2^(a-1) bits, rank 2^a - 1. In the
lattice picture F adds a surplus only at a one-parent junction with d <= 1 (floor) or at a d = 0 junction whose parity is not
implied. A one-parent junction at the end of a chain of join-irreducibles has d = number of minimal elements of Q outside its down-set;
so a chain continues under F iff at most one other minimal element is open. Hence N^a for a >= 3 does not continue under F (axis
d = a - 1 >= 2), its truncations close into boxes; N^2 (two chains) continues forever; one chain beside a finite set continues.
Conjecture (computed, not proved): under F, from any presentation, eventually at most two join-irreducibles are created per round,
so growth is finite, linear or quadratic.

T5. Bond balls of N^a are Theta(r^a) for every a >= 3 (generalising the earlier N^3 proof: squares generate the checks, sup-norm
<= delta, the cut around a monotone path is a bond since among a >= 3 axes two share a monotonicity sign; delta <= (2a-2)d + 2a - 1).

T6. For one count a >= 3, the earlier threshold reader (thresholds 3..2a; remove cross pairs of adjacent recovered stars whose
joint cut is short; read maximal cliques) recovers every junction from bond distances, because any >= 3 junctions have a cut of
>= 3a - 2 > 2a bits (last three junctions in a serial order bring 3a fresh bits, at most 2 used among themselves, no triangles).
At the round before the 2^a pattern closes, the a loose bits already form a bond (their parity is implied), so a distance reader
reads the closed pattern one round early; the states are identical.

## Pilot (disclosed; my code)

Uniform counts: exactly as T2/T3 for a = 3..6, c = 1..a+2 (stall rounds 2, 4, 3 as stated). Rules from one knot: F closes into
2^a (a = 3, 4, 5); "axis" (k = d plus one surplus at one-parent junctions) and "inherit" (k = max or min of the parents' counts) give
N^a; "balance" (k = p) stalls. Lookahead random surplus (each new junction gets one surplus bit with probability q): never stalls; the
Birkhoff check (T1) passed on 30 runs with no missing ideal. F applied after 1-4 random-surplus rounds (60 runs): 45 closed (some
after 14 rounds), 10 alive at 25 rounds with constant or linearly growing per-round counts, 5 exceeded 3000 junctions but with no
surplus being added (big finite lattices J(Q), |Q| around 29). Exact bond distances + reader on small presentations: exact except
the pre-closure stage reads the top junction early.

## Proposed answer

No distance-only criterion here picks a number of its own. Every rule's only freedom is where to put join-irreducibles (T1); the
dimension is then a property of Q. One count for every join must equal the first knot's size (T2), so the dimension is the first
knot's size; with the original cap of three it is exactly three (T3), the cap's number. The fewest counts close the knot into 2^a
and stop (T4); they sustain at most two directions, and only where the knot floor forces surplus bits: a junction that takes one
bit needs two fresh to be a knot. Random surplus gives no fixed exponent.

## Questions

1. Are T1-T6 correct? Any gap, especially T1's induction (is the candidate relation exactly "common lower cover"?) and T2's stall
   rounds? Is "the policy is upward closure of a distributive lattice" known (Birkhoff 1937; cover graphs of distributive lattices
   are median graphs; order dimension of J(Q) = width of Q, Dilworth 1950)? Anything closer?
2. Is there a natural distance-only count criterion I am missing that WOULD single out a number without being told one?
3. Is the T4 conjecture (eventually at most two new join-irreducibles per round under F) true? Proof idea or counterexample?
4. For bond-ball growth on J(Q) beyond N^a: is volume growth (ideals of size <= t) the right proxy, and what is known (e.g. width
   w with infinite chains gives t^w; Young's lattice J(N x N) grows like partitions, superpolynomial)?
5. Predictions I propose to freeze; please sharpen or replace: (P1) uniform counts survive 10 rounds iff c = a, with stall rounds
   2/4/3 as T2, for a = 3..7; (P2) cap three: survive iff c = a = 3; (P3) F gives 2^a for a = 3..6, axis and inherit give N^a,
   balance stalls for every a; (P4) T1's check passes on every non-stalling run of the census; (P5) blind counts uniform on {1..K}
   (floored): fraction alive at round 10 below 10% for every K in 2..6 and a in {3,4}; (P6) random surplus q in {0.05,0.1,0.2,0.4}:
   never stalls; among runs alive at round 10, the number of join-irreducibles created in round 10 is >= 3 in most runs and grows
   with q; (P7) F after random surplus: in every run, after at most 6 F-rounds, at most two join-irreducibles are created per
   round; (P8) the reader recovers every junction on every presentation with <= 16 junctions in the census, except that it also
   reads the set of all loose bits as a junction whenever that set is a bond no larger than the largest junction.
6. Words (the program bans spatial words such as lattice, edge, face for its own objects, and wants one word per meaning). I need
   program words for: (a) a junction with exactly one parent (the literature's join-irreducible); (b) the fresh bits of a junction
   that no join of the next round asks for (I propose "surplus distinctions"; "spare distinction" is taken); (c) the number of
   multi-parent joins of the next round that take a bit from a junction (I propose "asked count" or "demand"); (d) the poset of (a)
   ordered by descent and its width (I propose "the one-parent order" and "its spread"?). The classical names (distributive lattice
   of ideals, join-irreducible, width, cover graph) would be given once as the literature's. Suggest better words if these are poor.
