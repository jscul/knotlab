# The pinning theorem

Status: Proved (by hand; checked by the advisor model cold and by a frozen check on 387 blocks); **referee pending** (the background
referee thread). Ticket A of `research/PIN-RULE-20261112-001/preregistration.md`, frozen with its check in commit `c768dcd09`.

Words, as in the guide's glossary: block, distinction substitution σ, between-copy knots, spare distinction, part, tie class.
Throughout, the block triples are the block's knots in every order.

## 1. The theorem

Let B be a block on [m] (not-all-equal knots on triples of distinct distinctions) and P a pattern whose knots hold three distinct
distinctions. In every state of σ(P), for every knot (x, y, z) of P and every distinction p of B that is not spare,
x_p = y_p = z_p. So within each state p's part is constant on each connected component of P (its value may differ between components
and between states), and p's part is tied by equality across each component.

Together with lemma N6 of `SUBST-NEST-20261112-001` (a spare distinction's part takes every assignment while the rest of σ(P) is
held at a spare witness, so no tie involves it), **the tied parts of σ(P) are exactly those of the distinctions B cannot spare.** An
equivalent form of spare (the advisor's): p is spare exactly when some state of B stays a state when p alone is flipped. So the
distinctions that nesting pins are exactly those that can never flip unseen in the block, the same notion as the flippable residues
of `EVEN-PERIOD-20261112-001`.

## 2. Proof

Let a, b, c be the states of copies x, y, z (each a state of B). Suppose a_p ≠ b_p; flipping every value keeps σ(P)'s states and
does not change which distinctions are spare, so take a_p = 0, b_p = 1. Let e = {p, u, w} be any knot of B containing p.

- The between-copy knots include NAE(a_p, b_u, c_w) and NAE(a_p, b_w, c_u) (orderings with p in x's slot). If c_u = c_w = 0, they force
  b_u = b_w = 1, so b is constant on e, which no state of B is.
- They include NAE(a_u, b_p, c_w) and NAE(a_w, b_p, c_u) (p in y's slot). If c_u = c_w = 1, they force a_u = a_w = 0, so a is constant
  on e.

So c_u ≠ c_w for every knot through p, and c, a state of B, holds both values on every knot avoiding p: c with p left out is a spare
witness, and p is spare. Hence a_p = b_p. The binding is closed under reordering, so the same argument with p in the z slot gives
a_p = c_p and b_p = c_p. The argument uses one knot of P; other knots only remove states. ∎

## 3. Pins never vary (the corollary; with the advisor's general form)

Under block triples closed under reordering (the block's knots in every order, every distinct triple, the diagonal), a forced
relation between two copies' values at p is symmetric in the copies and in the mirror, so it is equality, inequality, or nothing;
inequality on all three pairs of a knot is impossible with two values, so a pin is equality. A forced relation between x_p and y_q
gives the same between x_p and z_q and between y_p and z_q, hence x_p = y_p: any pin across parts is equality of parts composed with
a relation the block already forces inside one copy. So the whole vector of pinned values is the same in every copy of a component:
**with native block triples, pins are uniform, never a relation that changes from copy to copy.**

## 4. What a sceptic would call built in

- **Built in by the definition.** The between-copy knots are the block's own knots with their three members drawn from three copies,
  in every order. So three equal copies always satisfy them (σ(P) lives exactly when B does), nothing tells the copies apart, and a pin
  can only be uniform (section 3). The reach across the whole pattern is the pattern's connectivity: each knot of P forces equality on
  its three copies, and equalities chain along P like a wire. There is no influence at a distance beyond that chain.
- **Not built in.** No between-copy knot ever holds (x, p) and (y, p) together (each holds three different distinctions of the block),
  so the equality is never stated; it is forced. Whether it is forced is decided exactly by a property of the block alone, spareness,
  which the definition does not mention and which is independent of the pattern.
- **Where the sceptic is right.** The argument is shallow (four between-copy knots per knot of the block) and depends on "in every
  order": with the diagonal alone nothing is pinned (`SUBST-NEST-20261112-001`, S1).

## 5. A corollary for harmonies (proved by putting definitions together)

Take as block the cyclic base of steps S at an odd n (a distinction per residue, the knots {x, x + s, x + 2s}). A distinction r is
spare exactly when some compatible word stays compatible with r flipped, that is, has r flippable (`ODD-SEARCH-20261112-001`,
lemma 5). So such a block has no spare distinction exactly when no compatible word has a flippable residue, which, when compatible
words exist, is exactly "S makes a harmony at n" (`ODD-FAMILY-20261112-001`). **For odd n, a cyclic block makes a harmony exactly when
nesting it by substitution pins every one of its distinctions**: the harmonies of periods 61, 73 and 193 are blocks that, nested,
pin everything.

## 6. The check (frozen; descriptive support; `check.py`, 80 seconds)

On all 387 blocks (the 87 of `SUBST-NEST-20261112-001`'s census and the 300 of its stress test), one knot of P, three copies: each
distinction was forced equal in the three copies exactly when it is not spare, never forced unequal, and each spare one was tied to
nothing; and on the 87, for every pair of states differing at p and every compatible third state, the third was a spare witness for
p. No exception. The advisor model, given the proof cold, found it correct (it noted that all six orderings are used once every pair
of copies is covered, which section 2 now says).

## What this establishes

- Proved: with the block's knots in every order, nesting by substitution pins exactly the distinctions the block cannot spare, by
  equality, uniformly across each component of the pattern; with any block triples closed under reordering, pins are uniform.
- The census rule of `SUBST-NEST-20261112-001` is now a theorem; its descriptive checks (4,850 roots, 300 blocks past the range)
  are instances.
- Not established: pins that vary. The advisor's smallest change (twist one slot of the binding by a symmetry π of the block, so that
  x_p = y_π(p)) makes the pinned relation carry a twist around cycles of P; checked locally only, by the advisor.
