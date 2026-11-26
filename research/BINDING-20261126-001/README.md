# Does growth bind facts held by the whole into a knot of the next layer?

Epic `BINDING-20261126-001`, at the coordinator's go-ahead on the layers referee's top direction. A check by the thread,
not a registered study; computed, with an argument; refereed (R1: **refuted, two Blocks**; folded in below). The census B
computations finished before the freeze commit, whose outputs the thread reports unopened; the split prediction was
committed before the final judge and its results ([question](advisor/question.md), [answer](advisor/answer.md)).

> **Referee R1: refuted (two Blocks), narrowings** ([report](referee-R1/report.md)). The frozen prediction holds on every
> recorded stage, but the conclusion that growth leaves whole-held facts unbound is false. **Block:** a 30-knot start built
> for the review gains, at round 2 of ordinary growth, three disjoint cycles of distinctions born in round 1 whose
> parities take exactly 000, 011, 101 and 110, each read by no single knot; removing any one round-1 law frees all eight
> ([certificate](referee-R1/construct_born.json)). **Block:** on the sampled ten-knot start, three disjoint path parities
> bind at round 3; removing one round-3 law frees them ([paths](referee-R1/path_certificate.json)). **Narrowings:** the
> counts below were an unfinished prefix (finished: 7,961 stages with B nonzero, 2,931 with a split into three or more
> cycles; still no qualifying split; the finished [`judge.jsonl`](judge.jsonl) is now committed); a qualifying split is a
> candidate needing its own joint-state and origin check; under changes of at most five distinctions the built witnesses
> regain two, three and four facts at rounds 2 and 3. Reproduced independently in `BUILT-BINDING-20261126-001`.

## The question, sharpened

The layers referee found connected starts that keep two, three or four facts no single knot reads (under parity, with
the shortest changes as the small changes). A tower's next step would be the growth binding such facts by a knot rule.
The coordinator's correction: a layer-one parity knot is itself "one distinction is the sum of the others", so a parity
rule among the facts is not trivial in itself. What does not count is a third fact we define as the sum. What would
count: three or more such facts, each carried on its own account (each the parity of its own cycle of the structure, not
read by one knot), whose parity the growth forces.

## What it rests on, and the argument

1. **Old carriers get no new relations** (refereed in `LAYERS-20261126-001`): ordinary growth under parity leaves the
   allowed states' projection onto the old distinctions unchanged, so the joint values of facts carried by old
   distinctions are fixed at the start. At round 1 every fresh distinction has one holder, so every cycle is made of old
   distinctions; the first relations new in values can only appear from round 2 (the advisor).
2. **Every forced relation among cycle parities lies in one space.** Over two values a relation c1 + ... + cm = const
   holds on the allowed states exactly when c1 + ... + cm is a sum of knots' laws. With loose values free, such a sum that
   is also a sum of cycles is the cut of a set of knots holding no loose distinction that is at once a cycle: the space B
   = (sums of laws) ∩ (allowed changes) ∩ (empty on loose distinctions), the literature's bicycle space over two values.
   If B = 0 no relation among cycle parities is forced, whatever carriers are chosen.
3. **The criterion for a binding** (the advisor's, adopted): an element of B whose support splits into three or more
   distinction-disjoint cycles, each a class label (even on every shortest change) and not read by one knot. Choosing a
   different representative of a label cannot make or unmake it, since the criterion is about how one element of B
   splits.
4. **Not-all-equal.** The record read no classes under it; carriers there would be functions of pairwise agreements,
   and the space need not be linear. Not computed here.

## Seen before the freeze ([`binding.py`](binding.py), [`forced.py`](forced.py), [`split.py`](split.py))

- On the referee's built witnesses (two, three and four facts) B = 0 at rounds 0 to 3: no forced relation at all.
- On its sampled ten-knot start, B has dimension 1 at every round, from a relation already present at the start.
- On the seven-knot held-out start 7-239, B grows from 1 to 2 to 3 at rounds 1 to 3, and its new elements are sums of
  laws that include knots born after the start; [R1:] across rounds 0 to 3 a forced sum splits into at most two, two, three and four cycles
  respectively, and none of its cycle parts is an unread label.
- Under the second reading of a small change (every change of up to five distinctions), the built witnesses keep no
  facts at rounds 0 and 1 [R1: they regain two, three and four at rounds 2 and 3].

## Frozen

**Sets.** Every census start of three to five knots and the 900 fresh starts of six to eight knots, at rounds 0, 1 and 2
of ordinary growth under parity ([`forced.py`](forced.py), running when this was committed), and the five witnesses to
round 3.

**Prediction.** No stage read has an element of B (every nonzero element of its span, up to 2^10 of them) whose support
splits into three or more distinction-disjoint cycles that are each a class label not read by one knot.

**Stop.** One such element: a second-layer knot made by the knots' laws, to be frozen and tested in its own right [R1:
a positive split is a candidate: check that every proper subset is free and when the equation first holds on these
supports]; or
none, which with the argument above says that under parity, with the shortest changes, growth leaves whole-held facts
unbound.

**What it would not show.** Not-all-equal; other readings of a small change; rounds past 2 on sampled starts; that no
other law binds such facts.

## What was found

The space B was computed on every census and held-out stage of rounds 0 to 2 and the witnesses to round 3
([`forced_census.jsonl`](forced_census.jsonl), [`forced_heldout.jsonl`](forced_heldout.jsonl); these runs finished
just before the freeze was committed and were not opened before it), and [`judge.py`](judge.py) split every nonzero
element of B on every stage where B ≠ 0 ([`judge.jsonl`](judge.jsonl)): 7,713 stages.

**The stop is "none".** No stage has an element of B that splits into three or more distinction-disjoint cycles each a
class label not read by one knot. Forced relations are common (7,961 distinct start-and-round entries with nonzero B, of which 2,931 have a
split into at least three cycles; the 7,713 and 2,805 first given were an unfinished prefix), but on none are all the parts facts held by the whole: some part is no
class label, or one knot reads it.

**[Refuted by R1 as a statement about the growth:] no recorded stage passed the disjoint-cycle test; on the sampled
ten-knot start, three disjoint path parities bind at round 3.** With the argument:
facts carried by old distinctions keep the relations of the start (none for the witnesses), every relation the knots'
laws force among cycle parities lies in B, and no element of B binds three or more such facts on any stage read. The
built witnesses with two, three and four facts have B = 0 at rounds 0 to 3: their facts stay free. Under the second reading of
a small change the built witnesses have one class at rounds 0 and 1, and two, three and four independent facts
beyond all single-knot reads at rounds 2 and 3 (R1).

**On the owner's rungs.** Repetition is shown (a knot; a grown start keeping one or several facts no knot reads). A
tower is not: the facts exist, and the growth does not bind them, under this law and reading, on the stages read.
Recursion is not shown (the recursion study).

**Not run.** Not-all-equal (the record reads no classes under it; its carriers would be functions of pairwise
agreements, and its space need not be linear); rounds past 2 on sampled starts; other readings of a small change on the
census; the forbidding cuts, which can fix loose values and so could force new relations.
