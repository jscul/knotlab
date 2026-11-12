# The pinning theorem, and pins that vary

Epic `PIN-RULE-20261112-001` (`SUBST-NEST-20261112-001` directions 1 and 2; G17 with G8; program mathematics, group arithmetic),
2026-11-12, at the coordinator's go-ahead. Pre-registered in [preregistration.md](preregistration.md), with the proof and its check
frozen in commit `c768dcd09`. Proof family: `proofs/PIN-RULE-20261112-001A/`. **Referee pending** (the background referee thread).

## Words

As in the guide's glossary: block, distinction substitution, block triples, between-copy knots, spare distinction, part, tie class.
The block triples are the block's knots in every order.

## The question

`SUBST-NEST-20261112-001` found, exactly on 87 blocks and 300 past them, that nesting by substitution pins a block distinction across
the whole pattern exactly when the block cannot spare it. Prove it; then ask whether pins can vary from copy to copy, nearer to the
owner's "fold in immensely complex ways", and say plainly how much of it the definition builds in.

## The answer

**Proved: nesting pins exactly what the block cannot spare, by equality; and with native bindings pins never vary.**

- **The theorem (proved; checked).** If two copies joined by a knot disagree at a block distinction, the third copy's state shows the
  block can spare it. So every distinction the block cannot spare is equal in the three copies at every knot, hence constant on each
  connected component of the pattern; spare ones are tied to nothing. The advisor model checked the proof cold and found it correct;
  a frozen check on all 387 blocks found no exception.
- **Spare means "can flip unseen".** A distinction is spare exactly when some state of the block survives flipping it alone, the
  advisor's restatement. So nesting pins exactly the distinctions that can never flip unseen in the block, the notion that decided
  `EVEN-PERIOD-20261112-001`'s periods.
- **Harmonies pin everything (a corollary).** For odd n, a cyclic block makes a harmony exactly when nesting it pins every one of its
  distinctions: the odd harmonies of 61, 73 and 193 are blocks that, nested, pin everything. The two lines of the night meet here.
- **Pins never vary (proved).** With any block triples closed under reordering, a pin is symmetric in the copies and in the mirror,
  so it is equality: a pinned part takes one value on each component. No pattern of varying pins arises.
- **What a sceptic would call built in.** The between-copy knots are the block's own knots spread over three copies in every order,
  so equal copies always fit, nothing tells copies apart, and the reach across the pattern is connectivity chaining one equality per
  knot, like a wire. Not built in: no between-copy knot ever holds two copies of the same distinction, so the equality is forced, not
  stated, and which distinctions it reaches is a property of the block alone. The argument is short, and it needs "in every order":
  with the diagonal nothing is pinned.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Nesting with the block's knots pins exactly the distinctions the block cannot spare, by equality, on each component | proved by hand (with N6 of `SUBST-NEST-20261112-001`); checked cold by the advisor model; frozen check on 387 blocks |
| Spare is "survives a flip at that distinction alone" | proved (the advisor's restatement) |
| For odd n, a cyclic block makes a harmony exactly when nesting pins all its distinctions | proved by combining definitions with `ODD-SEARCH` lemma 5 and `ODD-FAMILY` |
| Pins under block triples closed under reordering are uniform | proved by hand (with the advisor's general form) |
| Varying pins under a binding twisted by a symmetry of the block | the advisor's sketch, checked locally only; not tested here |

## Against the pre-registration

The theorem and corollary held; the frozen check found no exception (387 of 387 blocks; the proof's step on 87 of 87), in 80 seconds.
The sceptic paragraph was revisited with the advisor's answer and kept, with its "not built in" part sharpened.

## Review

Referee pending: the background referee thread has the hand-off. The coordinator asked the referee to judge how much is built in; the
answer above is this epic's.

## What it changes

- **For the owner's "globally influential".** The influence that nesting by substitution creates is now understood completely: it is
  a wire of equalities, one per knot, carrying the value of every distinction the block cannot spare to every copy it is connected
  to. It is global in reach and local in cause, and it is uniform.
- **For the owner's harmonies.** A harmony is a block whose every distinction is pinned when it is nested: the repeating patterns of
  the arithmetic line are the blocks that lock completely.
- **For "fold in complex ways".** Not with native bindings: pins cannot vary. The nearest change that could make them vary, a binding
  twisted by a symmetry of the block, puts a twist on each knot, and the pinned relation then depends on the twists met around each
  cycle of the pattern. That is the next place to look.

## Assumptions

A75 unchanged (Assumed; the owner's answer on side by side or inside is awaited).

## Corrections

None. (The rule was reported as exact, not proved; proving it sharpens it.)

## In the owner's words

When each yes-or-no is replaced by a small block and the blocks are tied by their own rules, the positions that get locked
everywhere are exactly the positions the block can never flip on their own. That is now proved, and it is the same idea that decided
which lengths of repeating patterns exist: a repeating pattern of odd length is exactly a block that, nested, locks every position.
The locking travels like a wire, one tie at a time, and it is always the same value everywhere it reaches; to get locks that change
from place to place, the ties would need a twist.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — prove the pinning rule; pins that vary | **Status:** Successful, referee pending | the rule proved; pins shown uniform under native bindings |
| Local direction — nesting | Continue | twisted bindings are the one place pins could vary |
| Broader exploration — G17's census | Known alternatives | random patterns' jumps; folding among random periodic bases (knots alone) |
| Long-term goal — G17 Typical and rare meeting patterns | Capability gained | nesting's influence is characterised exactly, and joined to the harmonies |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Twisted pins | 2/3 — Substantial | 2/3 — Testable | bind one slot through a symmetry π of the block; on chains, cycles and drawn nestings, measure whether pins become twists that depend on the cycles met, and whether twisted cycles end the pattern → pins that vary, or a proof they reduce to uniform ones | Selected · awaiting go-ahead |
| 2 | Endless blocks | 2/3 — Substantial | 2/3 — Testable | substitute a harmony for each distinction, bound by its own kinds → pins along both shifts, or none | Alternative · deferred |
| 3 | Harmonies as nested blocks | 1/3 — Incremental | 3/3 — Ready | nest the 61, 73 and 193 harmonies' cyclic blocks into small patterns and read the six or more states left → a count | Alternative · deferred |

- **#1** is where the owner's "fold" could live: a twist per knot, read around cycles, is native folding of the pin.

**Corrections:** none. **Goals:** G17 checkpoint (capability gained, with G8; no goal change). **Assumptions:** A75 unchanged.
**Basket:** #1 to #3 recorded; SUBST-NEST #3 (endless blocks) carried as #2. **Advisor:** consulted once, cold, on the proof (correct;
it supplied the restatement of spare, the general uniformity argument and the twisted binding).

## Final report as sent

Sent to the owner in the project thread on 2026-11-12 at about 08:39 UTC, verbatim:

> Done. The pinning rule is now a theorem, and it ties back to the harmonies. The write-up is research/PIN-RULE-20261112-001/pin_rule.md. The referee is pending with the background referee thread.
>
> • **The proof is four lines.** Suppose two knotted copies disagree at some distinction of the block. Then the third copy's state shows the block could spare that distinction. So nesting pins exactly what the block can't spare, and it pins it by equality across every connected part of the pattern. The advisor checked it cold, and a frozen check on all 387 blocks found no exception.
> • **"Spare" means "can flip unseen."** A distinction is spare exactly when some state of the block survives flipping that distinction alone. That is the same idea that decided which periods harmonies can have. So for odd lengths, **a harmony is exactly a block that, nested, locks every position**: the 61, 73 and 193 harmonies are such blocks.
> • **Pins never vary.** If the binding treats all copies alike, a pin is always an equality: the same value everywhere it reaches. The reach works like a wire, one equality per knot chained along the pattern.
> • **What's built in, plainly.** The binding spreads the block's own knots across copies, so equal copies always fit and the reach is just connectivity. What isn't built in: no knot ever states the equality directly, and which positions get locked depends on the block alone.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt — prove the pinning rule; pins that vary | **Status:** Successful, referee pending | rule proved; pins shown uniform under native bindings |
> | Local direction — nesting | Continue | twisted bindings are the one place pins could vary |
> | Broader exploration — G17's census | Known alternatives | random patterns' jumps; folding among random bases (knots alone) |
> | Long-term goal — G17 Typical and rare meeting patterns | Capability gained | nesting's influence characterised exactly, and joined to the harmonies |
>
> **Next step:** Research directions — selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | Twisted pins | 2/3 — Substantial | 2/3 — Testable | bind one slot through a symmetry of the block; measure whether pins become twists that depend on the cycles they go around → pins that vary, or a proof they reduce to uniform ones | Selected · awaiting go-ahead |
> | 2 | Endless blocks | 2/3 — Substantial | 2/3 — Testable | substitute a harmony for each distinction, bound by its own kinds → pins along both shifts, or none | Alternative · deferred |
> | 3 | Harmonies as nested blocks | 1/3 — Incremental | 3/3 — Ready | nest the 61, 73 and 193 blocks into small patterns and count the states left → a count | Alternative · deferred |
>
> **Corrections:** none. **Goals:** G17 checkpoint (capability gained), no goal change. **Assumptions:** A75 unchanged (still waiting on your side-by-side or nested answer). **Basket:** #1 to #3 recorded. **Advisor:** consulted once, cold, on the proof. It found it correct and suggested the "flip alone" restatement and the twisted binding in #1.
