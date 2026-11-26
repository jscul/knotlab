# Whole-held facts as the distinctions of a next layer

Epic `LAYERS-20261126-001`, at the coordinator's go-ahead on the owner's emergence principle (register entry A293) and
his question whether recursion can be shown. A check by the thread, not a registered study; exploration so far,
nothing frozen. The advisor was consulted twice from inside the repository ([first question](advisor/question.md);
both answers are entries in `docs/ADVISOR_HIVEMIND.md`).

## Three rungs, kept apart

The owner: "So that's repetition, but we don't have recursion yet." Each result here says which rung it reaches.

1. **Repetition**: the same kind of fact held by the whole and by no part, at two layers.
2. **A tower**: a step that carries any layer to the next. Stated for this study: *if a layer holds whole-held
   two-valued facts, the growth makes them the distinctions of a next layer, bound by a knot rule (K1 to K3 on their
   values), and that next layer again holds a whole-held fact.*
3. **Recursion**: a pattern that grows back into itself, or whose product is fed back as its own start.

## Prior work searched first

`BASES-WITHIN-20261112-001` (nesting by hand: each distinction of an outer pattern made a pattern below; the pattern
above allows exactly the outer states, refereed), `LIMIT-ONLY-20261112-001` and `NEST-COUNT-20261112-001` (nested
families, finite-state, live in the limit only), `NEVER-NEST-20261118-001` (an unrelated bracketing rule), the
generators of lesson 8.7 and the self-copying parts (`COPYING-PARTS-20261123-001`), the two-class sign
(`TWO-CLASS-SIGN-20261126-001`, refereed) and the two distances of a class (`BOTH-LONG-20261126-001`). The objects index
holds nothing on classes of classes or on a tower of whole-held facts.

## The argument so far (the thread's, with the advisor's corrections)

- **(A) Growth adds no check on old distinctions** under parity and the ordinary count: every new knot has a fresh
  distinction of its own, or its law is implied by the present ones (read by the advisor in the engine's code; checked
  here on every structure explored: the allowed changes of the old distinctions are the same after each round). Under
  the forbidding arms a birth can get no fresh distinction, the one recorded place where growth adds a check.
- **What growth does change is which parities are classes** (the moves change each round). So a next layer, if any,
  would come from the moves, not from new checks.
- **The knot test on class values cannot tell a layer from bookkeeping by itself**: any two independent classes and
  their sum pass K1 to K3, since three nonzero values of a two-dimensional space always sum to nothing.

## What the exploration found (computed, not frozen) — [`layers.py`](layers.py)

Parity, the ordinary count, loose distinctions free, each knot funded with max(2, its round-1 demand) loose
distinctions, one and two rounds:

| start | classes after growth | which sums of ring parities are labels |
|---|---|---|
| one ring of 4 to 7 knots | 2 | the ring's own parity (as recorded) |
| a ring of 3 | 1 | none |
| rings kept apart, in separate pieces | 2^k | every sum |
| two or three rings joined by a shared knot | 2 | only the sum of all of them |
| rings joined by a shared distinction, or a chain of knots | 2 | none (the label needs the connecting distinctions) |
| a tree of ten knots, no cycle (the advisor's case) | 2, labelled by the sum of all nine shared distinctions | — |

**So the first step of a tower fails as computed.** Joined rings do not keep a fact each: they keep one between them,
and a start with no ring keeps one too. The advisor's reading, which these rows reproduce: after one round, when no old
knot keeps a loose distinction and no three knots pairwise share one, every shortest change through an old shared
distinction holds two old distinctions that share a knot, so the classes number one per connected piece of the start
and the label is the sum of the piece's old shared distinctions. If that holds, it fails for the law under this reading
of a small change, not only for the built starts; the frozen test below is to check it on the census.

**Not a fact of the loop.** The ring's class, read in Chapter 12 as a whole-loop fact, is a fact of the whole connected
start (logged as a narrowing in `docs/CORRECTIONS.md`). Emergence is shown twice, repetition; a tower and recursion are
not shown.

**The one lead for recursion (rung 3), not tested here.** The second-check study's exchange of knots and distinctions,
with loose values pinned (a choice of ours), gives the start ring back from the grown ring at most sizes
(`SECOND-CHECK-20261126-001`); and the parts that copy themselves (lesson 8.7) make copies of themselves. Neither is a
step of a tower, and neither is claimed as recursion.

## Next (planned, not frozen)

A frozen test of the reduced reading on every census start of three to five knots that grows: predicted from the start
alone, the number of classes after one round is two to the number of connected pieces wherever no old knot keeps a
loose distinction and no three knots pairwise share one; with the tie cap lifted, and two swaps of the reading (the
moves as every change of up to five distinctions; one more loose distinction at each knot).
