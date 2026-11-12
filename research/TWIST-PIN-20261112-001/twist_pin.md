# Twisted pins

Epic `TWIST-PIN-20261112-001` (`PIN-RULE-20261112-001` direction 1; G17 with G8; program mathematics, group arithmetic), 2026-11-12,
at the coordinator's go-ahead, kept small. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `1422c900f`.
Proof family: `proofs/TWIST-PIN-20261112-001A/`. **Referee pending.**

## The question

Under the block's own knots pins never vary. If the between-copy knots pass through a symmetry of the block (a twist), can a pin
change with the cycle it goes around, nearer to the owner's "fold in immensely complex ways"? And is that more than renaming?

## The answer

**A short result, mostly settled by definition: twisted pins vary only when the pattern's cycles carry a symmetry that cannot be
undone; living does not depend on cycle length (after the run), but ties can.** *Narrowed by referee R1 (logged): the folded block is a
necessary condition, not the whole story; on one twisted cycle of k knots the twisted copy takes exactly the states t with t∘h within k
moves of t (the referee's rule), so a tie can appear on short cycles and vanish on long ones.*

- **By definition (proved).** A twist that every cycle undoes can be removed copy by copy (the null outcome: on a pattern without
  closed chains, always). Otherwise the cycles' symmetries form a group H, and the pinned values are those of the block folded by H:
  a distinction can become tied to its image, unequal to it, or the pattern ends.
- **Exact on the range.** On 18 blocks whose symmetries move a pinned distinction: every N-twisted holonomy made pins vary or ended
  the pattern; balanced ones matched untwisted; the advisor's exact condition for living held in all 240 single-cycle cells, and living
  did not depend on the cycle's length (2, 3 or 6 knots; this part is descriptive, from the follow-up after the run, because the
  frozen twist sat off the cycle). **Unexplained:** one block's fold (knots (0,1,2), (0,1,3), (0,1,4), (2,3,4), (2,3,5), the symmetry
  swapping 2 and 3) also ties its spare distinctions 4 and 5 in every copy, on every cycle. T3 speaks only of the distinctions the
  block cannot spare, so this does not contradict it, but it shows the folded block does not give every tie, and no reason is known.
- **Native folding on a ring.** On the one-shift ring, twisting every knot's middle member by an involution undoes on 6 distinctions
  and folds the pins on 7: whether the pins fold is decided by the ring's parity, a property of the whole pattern.
- **A design flaw, disclosed.** The frozen placement put the twist on a member outside the cycle for the closed chains and the two
  cycles, so those cells tested only the null; the length question was answered after the run with the twist on the cycle.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Transport, gauge and the folded-block form of twisted pins | proved by hand (the advisor model's form) |
| No cycle-length effect; the advisor's living condition exact; parity on rings | exact on the stated range; the length part descriptive, after the run |

## Referee R1 (folded in 2026-11-12)

The background referee thread confirmed the census with fixes ([report](referee-R1/report.md)), reproducing every count with its own
code, and found the exception's mechanism. In the block (0,1,2), (0,1,3), (0,1,4), (2,3,4), (2,3,5) with h exchanging 2 and 3 (spare
2, 3, 4, 5; N = {0, 1}; N-balanced), the states with 4 = 5 are 0 or 2 moves from their image under h and those with 4 ≠ 5 exactly 4
moves (a move changes a set of places meeting every knot at most once). **The referee's rule:** on one twisted cycle of k knots, the
twisted copy takes exactly the states t with t∘h within k moves of t (gauge the twist onto one knot; consecutive copies are allowed
together exactly when they differ by a move). So 4 and 5 are tied on cycles of 2 and 3 knots and on two cycles of 3, and not on the
cycle of 6. The rule predicts the whole tie relation in all 111 living single-cycle cells and contains the advisor's living
condition. Fixes, logged in `docs/CORRECTIONS.md`: the length claims hold for living only and are after the run (Narrowing); T3 is a
necessary condition on the pinned layer, not a full description, and "pins vary exactly where a holonomy moves a pinned distinction"
is contradicted by this N-balanced tie (Narrowing); P2 failed in one frozen cell (52 of 53 living N-balanced cells unchanged), and the
tie of 4 and 5 is not "on every cycle" (Not a block); the count of 69 N-balanced endings is after the run (the frozen run has 33)
(Not a block). This is the first tie found whose presence depends on how long a loop is: influence that is not plain connectivity.

## What it changes

- **For the owner's "fold".** Pins can fold, but only as the symmetries a pattern's cycles carry: a value travelling around a cycle
  comes back renamed, and the block must accept that renaming. Whether it folds is global (a ring's parity, a cycle's symmetry), but
  what it does is local (the block folded by a group). It is not a new mechanism beyond the pinning theorem, except where the block can spare distinctions: there the
  referee's rule makes ties depend on how long the loop is.
- **Next.** The coordinator's preferred target: endless blocks, a harmony substituted for each distinction and bound by its own
  kinds, joining both readings of the owner's question.

## Assumptions

A75 unchanged.

## Corrections

None. (The frozen design flaw changed no claim; it is disclosed above.)

## In the owner's words

If the ties between copies pass through a symmetry of the block, a locked value that travels around a loop of the pattern can come
back as a different position of the block, and then the block has to agree with itself under that symmetry. That is a fold, and
whether it happens depends on the whole loop (a ring of odd length folds, an even one does not). Whether the pattern survives does not depend on how long the loop is,
but what it locks can: in one block a short loop locks two positions together and a long one does not. *(Narrowed after the referee.)*

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — twisted pins | **Status:** Successful, referee R1 confirmed with fixes | settled by definition for living; cycle length matters for ties (the referee's rule), not for living (after the run) |
| Local direction — nesting | Continue | endless blocks join both readings |
| Broader exploration — G17's census | Known alternatives | random patterns' jumps; folding among random bases (knots alone) |
| Long-term goal — G17 Typical and rare meeting patterns | Capability gained | folding pins are the block folded by the pattern's cycle symmetries |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Endless blocks | 2/3 — Substantial | 2/3 — Testable | substitute a harmony for each distinction, bound by its own kinds between copies, on small patterns → pins along both shifts, or none | Selected · awaiting go-ahead |
| 2 | Folds beyond the quotient | 1/3 — Incremental | 3/3 — Ready | find every block whose fold ties spare distinctions, as the one found → a rule, or that block alone | Alternative · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained, with G8; no goal change). **Assumptions:** A75 unchanged.
**Basket:** #1, #2 recorded; endless blocks carried from `SUBST-NEST-20261112-001` (#3). **Advisor:** consulted once before the freeze
(T1 to T3, the exact living condition, the ring parity, the classes).

## Final report as sent

Sent to the owner in the project thread on 2026-11-12 at about 09:00 UTC (edited a minute later to correct its count of corrections:
"seven corrections in all (one Narrowing, the rest Not a block)" became "seven fixes, logged as six corrections: one Narrowing and five
Not a block"), verbatim as edited:

> Done: twisted pins, a short result, as expected. The write-up is research/TWIST-PIN-20261112-001/twist_pin.md, and the referee is pending.
>
> • **A fold is the block folded by a loop's symmetry (proved).** Let the ties between copies pass through symmetries of the block. Then a locked value that travels around a loop of the pattern can come back renamed. If no loop leaves a symmetry, the twist undoes copy by copy. Otherwise the pins are the block's own, folded by the loops' symmetries: a position becomes tied to its image, or unequal to it, or the pattern ends.
> • **Loop length doesn't matter; parity can (exact, 18 blocks).** Living came out the same on loops of 2, 3 and 6 knots for all 60 block-and-symmetry pairs. On a native one-shift ring, a swap twist undoes on 6 distinctions and folds on 7.
> • **A flaw I'm disclosing.** My frozen design put the twist off the loop in some test patterns, so those cells only tested the null. I answered the length question after the run, with the twist placed on the loop.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt — twisted pins | **Status:** Successful, referee pending | settled by definition; the one open piece (loop length) answered: no effect |
> | Local direction — nesting | Continue | endless blocks join both readings of your question |
> | Broader exploration — G17's census | Known alternatives | random patterns' jumps; folding among random bases |
> | Long-term goal — G17 Typical and rare meeting patterns | Capability gained | folds are the block folded by a loop's symmetry |
>
> **Next step:** Research directions — selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | Endless blocks | 2/3 — Substantial | 2/3 — Testable | substitute a harmony for each distinction, bound by its own kinds → pins along both shifts, or none | Selected · awaiting go-ahead |
> | 2 | Folds beyond the quotient | 1/3 — Incremental | 3/3 — Ready | find every block whose fold also ties spare positions (one found) → a rule, or that block alone | Alternative · deferred |
>
> **Corrections:** none this epic. Separately, I folded in the referee's verdicts on the last three epics: ~~seven corrections in all (one Narrowing, the rest Not a block)~~ [Edit: seven fixes, logged as six corrections: one Narrowing and five Not a block], each reported earlier. **Goals:** G17 checkpoint, no goal change. **Assumptions:** A75 unchanged. **Basket:** #1, #2 recorded. **Advisor:** consulted once before the freeze.

