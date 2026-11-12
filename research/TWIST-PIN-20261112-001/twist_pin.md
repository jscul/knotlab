# Twisted pins

Epic `TWIST-PIN-20261112-001` (`PIN-RULE-20261112-001` direction 1; G17 with G8; program mathematics, group arithmetic), 2026-11-12,
at the coordinator's go-ahead, kept small. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `1422c900f`.
Proof family: `proofs/TWIST-PIN-20261112-001A/`. **Referee pending.**

## The question

Under the block's own knots pins never vary. If the between-copy knots pass through a symmetry of the block (a twist), can a pin
change with the cycle it goes around, nearer to the owner's "fold in immensely complex ways"? And is that more than renaming?

## The answer

**A short result, mostly settled by definition: twisted pins vary exactly when the pattern's cycles carry a symmetry that cannot be
undone, and then they are ordinary pins of the block folded by that symmetry; cycle length does not matter.**

- **By definition (proved).** A twist that every cycle undoes can be removed copy by copy (the null outcome: on a pattern without
  closed chains, always). Otherwise the cycles' symmetries form a group H, and the pinned values are those of the block folded by H:
  a distinction can become tied to its image, unequal to it, or the pattern ends.
- **Exact on the range.** On 18 blocks whose symmetries move a pinned distinction: every N-twisted holonomy made pins vary or ended
  the pattern; balanced ones matched untwisted; the advisor's exact condition for living held in all 240 single-cycle cells, and living
  did not depend on the cycle's length (2, 3 or 6 knots). One block's fold also tied two spare distinctions, a case the folded pins
  do not predict.
- **Native folding on a ring.** On the one-shift ring, twisting every knot's middle member by an involution undoes on 6 distinctions
  and folds the pins on 7: whether the pins fold is decided by the ring's parity, a property of the whole pattern.
- **A design flaw, disclosed.** The frozen placement put the twist on a member outside the cycle for the closed chains and the two
  cycles, so those cells tested only the null; the length question was answered after the run with the twist on the cycle.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Transport, gauge and the folded-block form of twisted pins | proved by hand (the advisor model's form) |
| No cycle-length effect; the advisor's living condition exact; parity on rings | exact on the stated range; the length part descriptive, after the run |

## What it changes

- **For the owner's "fold".** Pins can fold, but only as the symmetries a pattern's cycles carry: a value travelling around a cycle
  comes back renamed, and the block must accept that renaming. Whether it folds is global (a ring's parity, a cycle's symmetry), but
  what it does is local (the block folded by a group). It is not a new mechanism beyond the pinning theorem.
- **Next.** The coordinator's preferred target: endless blocks, a harmony substituted for each distinction and bound by its own
  kinds, joining both readings of the owner's question.

## Assumptions

A75 unchanged.

## Corrections

None. (The frozen design flaw changed no claim; it is disclosed above.)

## In the owner's words

If the ties between copies pass through a symmetry of the block, a locked value that travels around a loop of the pattern can come
back as a different position of the block, and then the block has to agree with itself under that symmetry. That is a fold, and
whether it happens depends on the whole loop (a ring of odd length folds, an even one does not), but it never depends on how long the
loop is, and what it locks is just the block folded onto itself.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — twisted pins | **Status:** Successful, referee pending | settled by definition, with the one open piece (cycle length) answered: no effect |
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
