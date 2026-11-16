# Growing interfaces: the addressed patterns' closing summary

2026-11-16. This is the addressed-pattern line, from knots placed by address maps (`ADDR-KNOTS-20261113-001`) to the no-skip test
(`MARK-RATE-20261116-001`). Every epic named here is refereed and folded in except `MARK-RATE-20261116-001`, whose referee is pending.
The owner and the coordinator wrapped the line up after that study (2026-11-16); the program's main line moves to the navigating-agent
study.

## The question

In the nested line (`TOP-INFO-20261114-001`'s [summary](../TOP-INFO-20261114-001/line_summary.md)) a copy meets the rest through a
fixed interface. Here the interface grows. Knots are placed by a small invertible automaton on binary addresses, so the number of
distinctions joining level n to level n + 1 can grow with n (assumption A82). Does the top level bind the deep levels with nothing
chosen? That is: does the least bond from level 3 to level 3 + s grow with s, stay bounded, or vanish, and what decides which?

## What is proved

| Result | Where |
| --- | --- |
| **Shared lists stay finite-state.** One placement on two letters always lives. | `ADDR-KNOTS-20261113-001` |
| **Two living halves at every level.** For two of the seven patterns that alternate with the level's parity, a finite machine reading the address gives a state at every level (parity; first letter XOR last). | `LEVEL-RETURN-20261113-001` |
| **Theorem A\*\*.** With no cycle of knots, the reach is the fewest knots on a path between the levels plus two, so s + 2 when a chain steps down level by level. **Theorem A:** one tree-type placement gives such a pattern at every depth. | `RULER-LEVEL-20261114-001` |
| **Theorem W (blocks of orbits).** Every knot placed at an orbit of the maps lies in that orbit's block (the orbit with its children), and blocks meet only parent to child. When orbits stay small, life, ties and three-member bonds inside two orbits are decided at every depth and every s by a finite computation. | `DIRECT-REACH-20261115-001` |
| **Theorem D (a block's descent).** A few addresses followed down one letter each, with the letters eventually periodic, carry ties (L = 2) or three-member bonds (L ≤ 3) to every depth, given a finite-reader state for life. | `DIRECT-REACH-20261115-001` |
| **Theorem F (forgetting along blocks).** If every run of r block steps composes to a product relation, L ≥ 1 + ⌈s/r⌉ at every depth (the nested line's splicing lemma). **Lemma U:** bonds within levels 9 − r₀ at depth 9 stay bonds at every depth. | `BLOCK-REACH-20261116-001` |
| **Theorem M (no single skip).** If every up and below signature over every marking meets the block step, no bond skips a level, so L ≥ s + 1 at every depth. | `MARK-RATE-20261116-001` (referee pending) |

## What is computed

The `LEVEL-REACH-20261114-001` census reads the reach from level 3 to level 3 + s, s = 1..4, at depth 9. Over the alive weight:
- **A ruler** (s + 2, one more member per level) in 43 to 52%;
- **no bond** in 37%;
- **constant** ("direct") in 5 to 11%.

No least bond needs a member below its target. The least bond is not monotone in depth, so these are depth-9 readings.

Of the census's alive descriptions, 786 have orbits of at most four addresses. For these the census values become every-depth results:
- **Bounded at every depth.** 54 of the 100 constant descriptions: 15 at two members, 39 at most three (32 at exactly three). Blocks
  prove 42 of them, descents 12 more.
- **Grow at every depth.** All 399 small-orbit rulers, all 43 half-rate ones and 6 of 8 undecided ones, by forgetting. The first
  levels are exact: three members at s = 1 and 2 for every half-rate description, and at s = 1 for every ruler. The ruler part was
  computed after the referee and not separately refereed.
- **One member per level at every depth.** Every acyclic ruler with a chain stepping down level by level, by the hypertree theorem,
  and 86 of the 152 cyclic small-orbit rulers with r₀ = 0, by forgetting over one level or the no-skip test.
- **Forgetting decides bounded or growing** in 782 of the 786. The 4 left never forget and are not known to be bounded.

Life at every depth is proved for 139 of the 146 constant or half-rate descriptions by finite-reader states. Where orbits grow past four addresses
(479 alive descriptions), only upper bounds are proved, by descents.

## What it means (interpretation)

The top binds every depth with a bounded bond exactly where a fixed relation between two orbits survives at every distance: a tie, or
a three-member bond held by two orbits. Where every short run of levels forgets what enters it, the bond has to pick up members as it
goes down, at a rate set by how many levels it takes to forget. Cycles of knots do not stop a pattern from counting depth, but they
slow how fast its levels forget, and that is why the hypertree theorem could not reach the cyclic rulers. This holds where the
interface stays small (orbits of at most four addresses). Where orbits grow, the program can carry the top down but not yet show
that it fades.

## What is open

| # | Open item | Payoff | Concreteness | Backlog |
| --- | --- | --- | --- | --- |
| 1 | Exact reach by least-mark costs over blocks: s + 2 for the cyclic rulers, exact L(s) for every s where orbits stay small | 2/3 | 2/3 | B186 (with B180) |
| 2 | Lower bounds at every depth when orbits grow: an infinite family of states, or a finite interface for bounded automata | 2/3 | 1/3 | B188, B175 |
| 3 | The four small-orbit descriptions that never forget and are not direct | 1/3 | 2/3 | B187 |
| 4 | Ties in nearly rigid patterns with growing orbits (19 constant-2), and rigidity at every level | 1/3 | 2/3 | B189 |
| 5 | The 88 undecided bounded-activity descriptions | 1/3 | 1/3 | B190 |

## Lessons

These are kept in `docs/CORRECTIONS.md`:
- A reading one level above the deepest level read is a boundary reading; check one depth further before calling it a change.
- Control both ends of a finite reading: the top level and the distance from the bottom.
- When freezing predictions after a gap, compare them with the last committed version and state every change.
- Apply every proved refinement before tallying how far a bound is from the truth.
- Name an interface by the distinctions both sides use.
- Finitely many finite-reader states cannot prove a lower bound when their values recur.
