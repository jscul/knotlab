# Do the forbidding cuts bind facts held by the whole? And not-all-equal carriers

Epic `CUT-BINDING-20261126-001`, at the coordinator's go-ahead after [`BINDING-20261126-001`](../BINDING-20261126-001/decision.md).
A check by the thread, not a registered study; computed. The section "Frozen" was committed before the runs it names.

## Why the cuts

Ordinary growth under parity adds no check on old distinctions, so it cannot force new relations among facts carried by
old structure; the binding study found none at all among facts no single knot reads. The two recorded forbidding cuts of
the fresh count (`FORBIDDING-JOIN-20261120-001B`: one fewer, and the arity floor) are the one recorded law that adds
checks: a birth can get no fresh distinction of its own, its law then restricts old values, and the recursion study's
referee found they can fix a loose value. The cuts are a named law (G18); their two forms are scaffolds, so both are run.

## Frozen

**The test** ([`cuts.py`](cuts.py)): the binding study's, unchanged (`judge.judge_all`): on every stage, B = (sums of
the knots' laws) ∩ (allowed changes) ∩ (empty on loose distinctions), and every nonzero element of B (up to 2^10) split
into distinction-disjoint cycles in every way (up to 5,000 per element); a binding is a split into three or more cycles
each a class label (even on every shortest change) not read by one knot. Also read: whether the old distinctions'
allowed changes are kept.

**Sets and arms.** Every census start of three to five knots and the 900 fresh starts of six to eight knots, rounds 0 to
2, and the layers referee's witnesses to round 3; under one_fewer and under arity_floor.

**Prediction.** None is made either way: the cuts add checks, so a binding is possible. **Stop:** the first binding
found, which would be a second-layer knot made by the law, to be followed by a frozen confirmation on fresh starts; or
none under both forms, after which the not-all-equal carriers are tested (below, frozen separately).

**Seen before the freeze:** the witnesses under arity_floor stall at round 2, keep the old allowed changes at round 1,
and show no binding.

## What was found

**Under the forbidding cuts (frozen): no binding.** [`cuts_*.jsonl`](.) (six runs):

| set | form | stages read | stages with forced relations | old states removed by the cut | bindings |
|---|---|---|---|---|---|
| census, 3 to 5 knots | one fewer | 15,128 | 6,973 | 280 stages | 0 |
| census, 3 to 5 knots | arity floor | 15,176 | 7,005 | 376 stages | 0 |
| held out, 6 to 8 knots | one fewer | 1,620 | 886 | 42 stages | 0 |
| held out, 6 to 8 knots | arity floor | 1,630 | 893 | 62 stages | 0 |
| witnesses | either | 10 | 4 | none | 0 (they stall at round 2) |

The cuts do add checks (old states are removed on several hundred stages), and forced relations split into three to six
disjoint cycles on thousands of stages, but on none are all the parts facts that no single knot reads.

**Not-all-equal (computed, not frozen beforehand)** ([`nae_carriers.py`](nae_carriers.py),
[`nae_carriers.jsonl`](nae_carriers.jsonl)). The record finds no fact kept by small changes under not-all-equal (one
class wherever read, `TWO-CLASS-SIGN-20261126-001`). The solver test asks the nearest thing: on the witnesses built from
two, three and four rings of four knots, grown 0 to 2 rounds under not-all-equal, do the rings' own parities (each
carried by its own ring, disjoint, unchanged by flipping every value) take every tuple of values? They do, at every round
(4 of 4, 8 of 8, 16 of 16 tuples): no rule binds them.

**[Withdrawn as a statement about the laws (Block): the sets read stop at eight knots, and the binding referee's built
30-knot start binds under ordinary growth and, modified, under both cuts.] So, for the recorded laws, the tower is closed
in what was read.** Ordinary growth under parity, the two forbidding
cuts, and not-all-equal all leave the facts that no single knot reads unbound. On the owner's rungs: repetition is shown;
a tower is not; recursion is not.

**Not shown.** Larger starts, later rounds, other readings of a small change, and laws beyond the recorded ones; and
under not-all-equal only the ring parities of three built witnesses were read.
