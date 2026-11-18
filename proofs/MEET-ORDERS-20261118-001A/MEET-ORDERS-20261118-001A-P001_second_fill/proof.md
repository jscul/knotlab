# How the knots' bracketing decides the second fill

Ticket `MEET-ORDERS-20261118-001A`, 18 November 2026, by Claude, with the advisor model (Fable 5.2) for the converse of Lemma 0,
the parity form and Lemma C. Words as in `research/MEET-ORDERS-20261118-001/preregistration.md` ("Words used here").

## Setting

- **The line of n.** Distinctions 0, …, m with m = n − 1. Its allowed states are all-0, all-1 and, for each step k = 1, …, m,
  the state P_k with distinctions 0, …, k − 1 at 1 and the rest at 0, with its complement: 2n states.
- **Betweenness.** B(x, y, z) rules out the states with x = z ≠ y. A **presentation** of the line is a set of betweenness knots
  whose allowed states are exactly the line's; a **fewest-knot** presentation has the fewest knots.
- **KF3** (`STATE-RULES-20261117-001`, `KNOT-CAP-20261117-001`). A new distinction r comes with an irredundant set of one to three
  betweenness knots, each holding r and two old distinctions that already share a knot (co-knotted); every old state extends; r
  is constrained and is no copy of an old distinction; the fewest resulting states are taken, uniformly over the knot sets. A
  knot set that adds no state is a **fill**. KF3 reads the knots only through the co-knotted pairs.
- **Parity form** (the advisor). While no new distinction has added a state, each state extends uniquely, so a new distinction is a
  function of the state. Its value on P_k changes, as k runs from 0 (all-0) to n (all-1), exactly at the positions of an odd set
  O of line distinctions, and it equals the parity of O in every state; O is its **odd set**. A line distinction i has odd set
  {i}; the fill F(a, c, b) = {B(a, r, b), B(c, a, r), B(c, b, r)} gives r the parity of {a, c, b}, which is 1 on the steps
  a + 1, …, c and b + 1, …, m of P_k (as a function of k) and 0 on the others.
- **Number of orders**, as the program reads it (`STATE-RULES-20261117-001`, Eppstein's formula for lattice dimension): each
  state pair {P_k, complement} is a split of the distinctions, and λ = (number of splits) − (a largest matching of the graph
  joining sides of different splits whose union is every distinction). A **chain** is a set of splits whose sides can be chosen
  nested. A matching is a cover by chains and back: a matched pair {X, Y} says comp(X) ⊂ Y, so following matched pairs runs up a
  chain comp(X) ⊂ Y ⊂ Z ⊂ … (no cycle, since distinct splits give strict inclusions), and a chain of L splits gives L − 1 matched
  pairs. So λ is the least number of chains covering the splits. Two crossing splits (all four combinations of sides occupied)
  never share a chain. Each chain gives one coordinate (how many of its 1-sides hold a distinction), which is the reading "the
  least number of lines whose product holds the distinctions". **Two orders** means λ = 2 with a bipartite crossing graph.

## Lemma 0 (presentations are bracketings)

Let K present the line of n.
1. Every knot B(x, y, z) of K has y strictly between x and z in the line. Otherwise y lies beyond both, and the line state that
   cuts between y and the other two has x = z ≠ y, which the knot rules out.
2. Every interior distinction c is the middle of a knot: the state with only c at 1 is not a line state, and only a knot with
   middle c rules it out. So |K| ≥ n − 2, and a fewest-knot presentation has exactly one knot κ_c = (a_c, c, b_c) with
   a_c < c < b_c for each interior c.
3. **Every bracketing presents the line.** A bracketing assigns each knot (a, c, b) its halves a..c and c..b, with the ends'
   knot (0, c, m) at the top and single steps at the bottom. Let x be allowed. By induction from the bottom, x is monotone (at
   most one change) on a..c and on c..b. If x_a = x_b the knot forces x_c = x_a, so x is constant on a..b; if x_a ≠ x_b, x_c
   equals one of them and the two monotone halves join into one change. At the ends' knot, x is monotone on 0..m: a line state.
4. **Every fewest-knot presentation is a bracketing** (the advisor's agreement form). State x is allowed iff every interior c has
   x_c ∈ {x_{a_c}, x_{b_c}}. Draw arrows c → a_c and c → b_c.
   - *No directed cycle among interior distinctions.* Given one, let X be the least set containing the cycle and every interior c
     with both a_c, b_c in X. The state 1 on X, 0 elsewhere, is allowed (members of the cycle agree with their successor; added
     members with both outer distinctions; any other interior c has an outer distinction outside X), has both ends at 0 and is
     not constant: not a line state.
   - So some interior c receives no arrow. Its value enters no other knot, so dropping it and κ_c leaves a presentation of the
     line on the other n − 1 distinctions (each of its allowed states extends by x_c = x_{a_c}).
   - κ_c = (c − 1, c, c + 1). If a_c ≤ c − 2, the smaller line's state with 1 on 0..a_c extends by x_c = 1 to an allowed state of
     K with 1 on {0..a_c} ∪ {c} and 0 at c − 1: not a line state. The same at b_c.
   - By induction the rest is a bracketing of the smaller line; κ_c brackets its step c − 1..c + 1 into two. So K is a bracketing.

So the fewest-knot presentations are exactly the bracketings (the literature's triangulations of the n-gon 0..m, the ends' pair
(0, m) its marked side), n − 2 knots each, Catalan(n − 2) per labelling: 5 for the line of five (300 labelled, as KNOT-CAP's
referee counted), 14 for six. In a bracketing every three pairwise co-knotted distinctions form a knot (a triangle of chords of
a triangulated polygon is one of its triangles).

**The five-starts.** Per labelling the line of five has two chains of the same way (the end placements: B(0,1,2), B(0,2,3),
B(0,3,4) and its mirror), two chains of the other way (next to an end: B(0,1,3), B(0,3,4), B(1,2,3) and its mirror), and one
bracketing whose ends' knot holds a knot in each half (the middle: B(0,1,2), B(0,2,4), B(2,3,4)). The shared distinction's
placement is a proxy for the bracketing: the three knots of a chain share the distinction where the chain's knots all meet,
which is an end for the same way and next to an end for the other way.

## Lemma A (the first new distinction)

From a fewest-knot presentation, KF3's options are exactly the fills of its n − 2 knots, one knot set each; each gives two orders.

*Proof.* Some fill is knot-local (any knot's), so KF3 takes fills. The fills of the line are exactly the C(n, 3) knot sets
F(a, c, b), a < c < b (`STATE-RULES-20261117-001`, S4). Uniqueness of the knot set: a knot on r and the pair (x, y), x < y,
pins r on a run of steps (B(x, r, y): steps up to x and after y, and the all-0 and all-1 states; B(x, y, r) or B(y, x, r): the
steps x + 1..y). The parity of {a, c, b} has four runs of steps (1..a, a + 1..c, c + 1..b, b + 1..m, the first and last possibly
empty), and only B(x, r, y) knots pin the all-0 and all-1 states. Covering the two middle runs needs one knot on (a, c) and one on
(c, b) pinning exactly those runs, and then B(a, r, b) for the rest; any other choice pins a step against the parity or leaves one
unpinned. Knot-locality needs (a, c), (c, b) and (a, b) co-knotted, so (a, c, b) is a knot of the presentation (Lemma 0). Two
orders: Lemma C with one fill. ∎

## Lemma C (the two-order criterion; the advisor's statement)

Let a base be the line with new distinctions whose odd sets are triples {u, v, w}, u < v < w (fills of triples), no state added.
Call v the fill's **middle** and u, w its **ends**. The base has one order if there is no fill; two if there is one and no
fill's middle lies strictly between the ends of another fill without being its middle; three or more otherwise.

*Proof.* On P_k, a line distinction i takes 1 iff i < k; a fill (u, v, w) takes 1 iff k ∈ (u, v] ∪ (w, m]. For steps k < l, the
line distinctions show the value pairs (1, 1), (0, 1) and (0, 0) on (P_k, P_l) (i < k, k ≤ i < l, i ≥ l); the missing pair
(1, 0) comes only from a fill with k ∈ (u, v] and l ∈ (v, w]. So steps k and l cross exactly when some fill holds them in different
halves.
- *Three or more.* Suppose fill g = (u′, v′, w′) has u < v′ < w and v′ ≠ v for a fill f = (u, v, w). Then steps v′ and v′ + 1 lie
  in one half of f, and cross each other (they lie in different halves of g); both cross every step of f's other half. Three
  pairwise crossing steps need three chains, and they make the crossing graph non-bipartite.
- *Two.* Colour step k by the parity of the number of fill middles below k. Under the condition, each fill's halves are
  single-coloured, with different colours. On one colour class every distinction's value is monotone in k: a line distinction
  by definition; a fill (u, v, w) takes 0 below u + 1 and 1 from there on, on the class of its first half (that class has no steps
  in (v, w]), and 0 up to w and 1 after, on the other. So each class is a chain: λ ≤ 2. A crossing exists, so λ = 2, and
  crossing steps lie in different halves of a fill, hence have different colours: the crossing graph is bipartite. ∎

## Lemma B (the second new distinction)

Let κ = (a, c, b) be filled first, with new distinction q (odd set {a, c, b}). KF3's options for the next distinction r are exactly:
- **(F)** for each knot τ ≠ κ, the fill of τ: one knot set, r with odd set τ;
- **(E)** for each knot ν sharing a pair {s, t} with κ, with x the distinction of κ outside it and y that of ν: two knot sets,
  with odd sets {x, y, s} and {x, y, t}, each using the two pairs of ν other than {s, t} and one pair holding q.

Both kinds add no state, so they are KF3's options. Through the knot κ lies directly within (ν = (a, b, y)), the two are the
re-bracketings {a, c, y} and {c, b, y} (the advisor: the rotation of κ with ν); through a knot directly within κ (ν = (a, y, c),
say), they are {y, c, b} and {a, y, b}.

*Proof: compression and a finite check.*
1. *Segments.* Let P be the positions 0, m, a, c, b and the line distinctions of the at most three old pairs a knot set uses
   (|P| ≤ 11). Each constraint pins r to one value, or leaves it free, on all steps between two consecutive positions of P: the
   pins of a knot on the pair (x, y) depend on where the two take different values, and line distinctions in P and q (whose
   changes are at a, c, b) change only at positions of P.
2. *Compression.* Merge the steps of each segment. Compatibility, covering (every state pinned), irredundancy and "adds no
   state" are statements about the pins segment by segment, so they hold before iff after. "Not a copy" also: r is constant on
   segments, so r equals a line distinction i only if i ∈ P, and equals q iff it does after (a, c, b ∈ P).
3. *Pull-back.* The pairs a knot set uses, with κ's pairs, are co-knotted in the bracketing, so as chords of the polygon they do
   not cross; after compression they still do not, and complete to a bracketing T′ of the compressed line (at most 11
   distinctions) that contains κ′ and the set's pairs. So every option of the big presentation is an option of a small one, and
   conversely for a set whose positions are all in P. A set of kind F or E in T′ uses all three pairs of a knot of T′ (F) or, with
   κ's shared pair, all three pairs of a knot sharing a pair with κ (E); those pairs are co-knotted in T, so the knot exists in T
   (Lemma 0). This is the advisor's point: the check records that the E sets use the two pairs of ν other than the shared one.
4. *Finite check* (ticket B, M1): every bracketing with n0 = 4 to 11 distinctions and every first knot: the options are exactly
   the sets above, one per other knot and two per knot sharing a pair, with the stated odd sets. With 1 to 3, this proves the
   lemma for every n. ∎

**Verdicts, by Lemma C.**
- (F) τ step-disjoint from κ: neither middle lies strictly between the other's ends: two orders. τ within a half of κ (or κ
  within a half of τ): its middle lies strictly between κ's ends and differs from c: three or more orders.
- (E) through the knot κ lies within, ν = (a, b, y): {a, c, y} has middle c, κ's middle; {c, b, y} has middle b, an end of κ, and c is an end
  of it: two orders, both. The mirror case ν = (y, a, b) is the same.
- (E) through a knot within κ, ν = (a, y, c): {y, c, b} has middle c: two orders; {a, y, b} has middle y, strictly between κ's ends
  and not c: three or more. One of two. The same for a knot within κ's other half.

## Theorem 1

Under KF3 from a fewest-knot presentation of the line of n (n ≥ 4), the chance of two orders after the second new distinction is

  (1 / (n − 2)) Σ_κ [ s(κ) + 2 p(κ) + c(κ) ] / [ (n − 3) + 2 (p(κ) + c(κ)) ],

where the sum is over the knots, s(κ) counts the knots step-disjoint from κ, p(κ) is 1 when κ lies directly within a knot (0 for the
ends' knot), and c(κ) counts the knots directly within κ.

*Proof.* Lemma A: κ is uniform. Lemma B: the options number (n − 3) + 2 (p + c), uniform. The verdicts: s + 2p + c keep two
orders. ∎

**It depends only on the bare bracketing**, since s, p and c ignore which half a knot lies in.

**Corollaries.**
- Line of five: the chains (end, next to an end) give (1/2 + 1/2 + 1/4)/3 = 5/12; the middle bracketing gives
  (3/4 + 1/3 + 3/4)/3 = 11/18.
- Line of six: chains 51/140 (both six-starts are chains), the ends' knot holding a knot in each half 79/140, and a step and a
  knot holding a knot in each half 83/180.
- A chain of n − 2 knots: 3 [1/(n − 1) + (n − 4)/(n + 1)] / (n − 2), about 3/n.

**Why nesting costs orders.** A fill makes every step of one half of its knot cross every step of the other: two groups, two
orders. A second fill in a knot within one half splits that half into two groups that cross each other and the other half: a
third order. A second fill in a step-disjoint knot crosses steps the first does not touch, and the two can share two orders. The more
the knots lie within one another, the fewer second fills are step-disjoint, and the sooner a third order comes.

## What this does not prove

- The third and later new distinctions. That the number of orders at n0 + 3 depends only on the bare bracketing, and that same
  way against other way enters at n0 + 4, are computed (ticket B), not proved.
- Presentations with more than n − 2 knots, other knot kinds, and other weightings.
- That the chain is the least for every n (ticket B computes it to n = 13; the advisor suggests a route through path lengths).

## Known mathematics, labelled

Triangulations, bracketings and binary trees (Catalan); lattice dimension and chains of splits (Eppstein 2005); rotations
(Sleator, Tarjan and Thurston). Local: Lemma 0's characterization of betweenness presentations, Lemmas A to C for KF3, and the
formula.
