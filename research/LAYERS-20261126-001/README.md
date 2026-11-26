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

## Reconciled before the freeze ([`multi_class.py`](multi_class.py), [`multi_class.json`](multi_class.json))

At the coordinator's request: the census starts that keep several independent classes (under parity, 24 with four and
2 with eight at the start, 8 with four after one round, in the two-class study's census) are where a rule binding
several facts could live. In every one, each class label can be read knot by knot (the labels single knots read span the
whole label space; in most, one knot reads all of it). So their facts are local, not held by the whole.

## Frozen

Committed before the runs below; the advisor proposed the rule (its second answer, in the hivemind) and its two
counterexamples (a tree; one more loose distinction) were run before the freeze.

**The rule (the advisor's reduction).** Under parity and the ordinary count, after one round, if (C1) the start grows,
(C2) no old knot keeps a loose distinction and (C3) no three knots pairwise share a distinction, then the start has
2^p classes, p its connected pieces that hold a shared distinction (so 2 for a connected start), and the parity of all
the old shared distinctions of each piece is a label.

**Sets** ([`frozen.py`](frozen.py)): every census start of three to five knots (7,075), and a held-out sample of 300
starts each of 6, 7 and 8 knots from the extension's weighting (`forbid.sampled`) with the fresh seed 20261206 + n.
Moves: every shortest change through each distinction, with no tie cap; loose distinctions free.

**Predictions.**
- **P1.** Every start meeting C1 to C3 has exactly the predicted classes and each piece's parity is a label.
- **P2 (reported).** The class counts of the starts outside C2 or C3.
- **P3.** Every held-out start with four or more classes after the round has its labels read knot by knot.

**Stop.** One start meeting C1 to C3 that breaks P1; or a held-out start with two or more classes not read knot by
knot, which would be a candidate first step of a tower (a discovery, not a failure); or none.

**What a pass would and would not show.** A pass makes it a computed rule that, under this reading of a small change,
the growth keeps one whole-held fact per connected piece: repetition, not a tower. It would not show that no other
reading of a small change, no other knot law or no larger start makes a tower, and nothing here bears on recursion.

## What was found

The frozen runs ([`frozen_census.jsonl`](frozen_census.jsonl), [`frozen_heldout.jsonl`](frozen_heldout.jsonl)), scored by
[`score.py`](score.py) ([`score.json`](score.json)):

| set | grow one round | in the conditions | P1 holds | P1 breaks | four or more classes | of those, labels read knot by knot |
|---|---|---|---|---|---|---|
| census, 3 to 5 knots | 5,111 of 7,075 | 978 | 130 | 848 | 8 | 8 |
| held out, 6 to 8 knots | 417 of 900 | 157 | 28 | 129 | 8 | 7 |

**The stop is met: the rule breaks.** In 848 of the 978 census starts that meet the conditions (and 129 of 157 held
out), the start keeps one class after the round, not two, and its pieces' parities are no label; in a few (31 and 27) it
keeps two with another label, and in four it keeps four. So the advisor's reduction, as stated, is wrong: its conditions
leave out what removes the class in most starts (the record's double meetings, two knots sharing two distinctions, are
the first suspect, not checked).

**What the tower's first step needed, and what was found.** A tower needs a connected start that keeps two or more
independent whole-held facts, so that a rule can bind them. Only starts with four or more classes could show that: 8 in
the census and 8 held out. In 15 of the 16 every label is read knot by knot (no whole-held fact at all among them), and
in the sixteenth (held out, seven knots) the two-dimensional label space holds one label that single knots read and one
that none does. So **no start read keeps more than one whole-held fact**, at the start or after one round, under this
reading of a small change. The first step of a tower is not found, on sampled starts, not only on built ones; but only
16 of 7,975 starts could have shown it, and rounds past the first were read only on the built rings.

**Repetition, not a tower.** The record shows the same kind of fact, held by the whole and by no part, twice: in a knot,
and in a grown start (one per connected piece, at most, in every start read). It does not show a step from one to the
next, and nothing here bears on recursion.
