# The first filled knot is the first crossing

Status: Proved

Ticket `KNOT-SWITCH-20261118-001A`, 18 November 2026, by Claude. Epic `KNOT-SWITCH-20261118-001`. Written before the run.

## Words

As in `PICK-TWO-20261118-001A` and `MEET-ORDERS-20261118-001A` (KF3, bracketings, Lemma A, fills, subdivisions, splits and their
crossing).
- **The knot complex.** K: the distinctions; the pairs that share a knot; the knots, as unordered triples. Its homology is taken over
  GF(2), with Betti numbers b₀, b₁, b₂.
- **An even knot set.** A set of knots in which every pair lies in an even number of them (the literature's 2-cycle of K over
  GF(2)). b₂ counts the independent ones.
- **A filled knot.** A knot (a, c, b) together with the three knots of its fill F(a, c, b) = {B(a, r, b), B(c, a, r), B(c, b, r)}:
  four distinctions carrying four knots, one on each three of them, each the middle of exactly one. (*After the referee:* of the
  nine ways to give four distinctions four such knots, three are of this kind; the other six force two distinctions to be copies,
  so they never occur in a base without copies.) Any of
  the four knots can play (a, c, b), since the other three are its fill. Its four knots are an even knot set.
- **The rules.** KF3, NN and NN2 (`NEVER-NEST-20261118-001`), and SEEDK: `PICK-TWO-20261118-001`'s SEED with knots only on pairs
  that already share a knot. While b₂(K) = 0 it takes any fill; afterwards it takes the fills that copy or conserve as SEED does.
  Else it takes a subdivision.

## Statements

- **W1. A move attaches a cone.** A knot-local move adds the new distinction p and, for each of its knots, the triangle on p and
  that knot's old pair. Every old pair already lies in K. So K′ is K with a cone from p over the graph L of the old pairs used:
  - b₂(K′) = b₂(K) + dim ker(H₁(L) → H₁(K)), so b₂ never falls;
  - b₁(K′) = b₁(K) − rank(H₁(L) → H₁(K)) + (the number of components of L minus one).

  A fill whose knots use pairs that do not touch therefore makes a new loop. (My first version said that b₁ stays zero; the advisor
  and the gate checks showed otherwise.)
- **W2. A filled knot forces a crossing, whatever the presentation.** If a base's states satisfy the four knots of a filled knot on
  a, b, c, r, and no two of these four are copies, then two splits cross. The four knots allow, on a, b, c, r, only the two
  constants and the patterns ac | br and ar | cb with their complements. Distinctness forces both patterns to occur, and they
  cross.
- **W3. Along these rules, nothing crosses exactly until the first filled knot and the first even knot set.** (*Scope, after the
  referee:* this is an equivalence along these growths, where all four readings change at the first move. In general a filled knot
  forces a crossing (W2), but a crossing rarely brings one: of 2,776 random copy-free presentations with a crossing, 2,772 carry
  none.) From a bracketing
  each of KF3, NN, NN2 and SEEDK first takes a fill, and that fill is the fill of one of the presentation's knots (Lemma A). It
  makes, in the same step, the first crossing (`PICK-TWO-20261118-001A`, S6), the first filled knot, and b₂ = 1. Crossings,
  filled knots and b₂ never go away. So at every step:
  - no two splits cross;
  - no filled knot;
  - b₂(K) = 0;
  - no fill yet.

  These four are equivalent, and SEEDK's switch, read from the knots, is SEED's.
- **W4. The even-knot-set reading belongs to the grown presentation, the filled-knot reading to any.** The line of n presented by
  all its implied knots has b₂ = C(n − 1, 3) and nothing crosses, so b₂ does not read the states. But it has no filled knot, and by
  W2 no presentation with a filled knot lacks a crossing.

## Proofs

**W1.**
- *The cone.* Each new triangle is {p, x, y} with {x, y} an old pair, so K′ = K ∪ cone(L), with cone(L) ∩ K = L.
- *The sequence.* cone(L) is contractible. The Mayer–Vietoris sequence of reduced homology gives
  0 → H₂(K) → H₂(K′) → H₁(L) → H₁(K) → H₁(K′) → H̃₀(L) → H̃₀(K) ⊕ 0.
- *Reading it off.* The kernel of H₁(L) → H₁(K) adds to b₂. Its cokernel, and the kernel of H̃₀(L) → H̃₀(K), make up H₁(K′). K is
  connected (it starts as a triangulated polygon and every move attaches to it), so the last kernel has dimension (components of
  L) − 1. ∎

**W2.**
- *The allowed patterns.* Write a pattern on (a, b, c, r) as the four values. The knots exclude, in turn:
  - a = b ≠ c (from B(a, c, b));
  - a = b ≠ r (from B(a, r, b));
  - c = r ≠ a (from B(c, a, r));
  - c = r ≠ b (from B(c, b, r)).

  The single-1 and single-0 patterns each break one of these. So does ab | cr, where a = b ≠ c. What remains is 0000, 1111,
  ac | br and ar | cb, each with its complement (checked over all sixteen patterns in the gate checks).
- *Both occur.* a and c differ only on ar | cb, and a and r only on ac | br. So if neither pair is a copy, both patterns occur in
  some state, on two splits s and s′.
- *They cross.* On the four, s has sides {a, c}, {b, r} and s′ has sides {a, r}, {c, b}. All four intersections, {a}, {c}, {r} and
  {b}, are non-empty, so s and s′ cross. ∎

**W3.**
- *Fills come first.* A line of three or more distinctions has fills (Lemma A), and each rule takes a fill when one keeps its
  condition:
  - KF3 because fills are cheapest;
  - NN and NN2 because the first fill keeps two orders (S6);
  - SEEDK because b₂ = 0 there.

  The first move is therefore a fill of a presentation knot (a, c, b).
- *Its knots.* They are F(a, c, b), so together with (a, c, b) they form a filled knot, and L is the triangle a-c-b. That triangle
  bounds in the triangulated polygon, so H₁(L) → H₁(K) is zero and b₂ becomes 1 (W1). The fill makes the first crossing (S6).
- *Nothing goes away.* Knots are never removed, so filled knots stay; b₂ never falls (W1); and crossings never go away
  (`PICK-TWO-20261118-001A`, S1).
- *Before it.* The presentation is the bracketing, with no crossing, no filled knot, and b₂ = 0. There is no filled knot because a
  filled knot needs four distinctions that pairwise share knots, and a triangulated polygon has no such four (its pair graph is
  outerplanar). ∎

**W4.**
- *The saturated line.* With every implied knot, K is the full 2-skeleton on n vertices, which has b₂ = C(n − 1, 3).
- *No filled knot there.* For a < b < c < d the implied knots on {a, b, c, d} have middles b, b, c, c (computed for n ≤ 8 in the
  gate checks; the middles are the inner two).
- *The other direction.* W2 holds for any presentation. ∎

## What this leaves to the computation

- W3 at every step of every run (a check), and how b₁ grows (the loops of W1).
- Whether SEEDK, with knots only on co-knotted pairs, is strong: two orders at every step after the first fill, with full two-way
  grids recurring, from every bracketing.
- Whether the filled knots also count anything more, for instance the number of orders (the advisor's suggestion, untested).

## Provenance

Local; builds on `PICK-TWO-20261118-001A` (S1, S6), `MEET-ORDERS-20261118-001A` (Lemma A) and `NEVER-NEST-20261118-001`. The
Mayer–Vietoris sequence is classical. The advisor, consulted before the freeze, corrected W1's b₁ term, separated the readings
that depend on the presentation from those that do not, proposed the filled knot (its "fill type" four-set) and the word "even
knot set".
