# Outcomes of random meeting patterns: stage 2, frozen before its run

Ticket `RANDOM-FATES-20261112-001C`, 2026-11-12, added while the stage-1 census of ticket A was still running (its results not
yet read). Words as in the stage-1 pre-registration (`preregistration.md`) and the guide's glossary. The canonical K1–K3 test is
unchanged.

## The question

Newest-four growth never ends (ticket B, T4(b)): every pattern it reaches allows a state, at every closing probability q. It is
the one process in the census that goes on for ever whatever its moves, so it is the natural place for the owner's third outcome,
patterns that "go on forever and create sets like the natural numbers". Does the law, reading its allowed states alone, count
along it? Three readings are possible: the law **cuts** the line (two far distinctions lie in no common bond), **counts** it (the
least bond containing two distinctions grows steadily with their distance along the line), or **folds** it (the least bond stays
bounded, as in the pattern of all knots within four consecutive distinctions, where two distinctions four apart are tied).

## The method (exact)

`bonddp.py` computes the least bond containing two distinctions i < j by a dynamic programme over positions. Its design came from
the advisor model (Fable 5.2), consulted under the owner's rule of 2026-11-12 that threads consult it on hard analysis and before
freezing a design. The state after position m records the family of reachable window-state sets over every pattern on the members
chosen so far, and the same family pooled over every one-member deletion; the empty set in the first family at the end means
"constrained", and its absence from the second family means "every proper part free". Members are chosen only in
[i − 8, j + 8] (the margin; the advisor doubts that a smallest bond always lies in a fixed window, so wider rechecks are frozen
below), and nothing else is cut: every knot of the base is applied. "Undefined" means no bond containing both with members in that
window. In exploration it matched exhaustive search on 276 small random newest-four patterns (and the frozen controls repeat this
on 300 new ones), gives L = 2 at g ≡ 0 mod 4 and 3 otherwise on the complete pattern, and L = steps + 2 on the chain
{2k, 2k + 1, 2k + 2}, a pattern with no cycle of knots.

## The design (frozen; `census.py` beside the code)

- **Bases.** Newest-four growth at q = 0, 0.1, 0.3, 0.5, 0.7, 0.9; ten bases each (fresh seeds), grown to 800 distinctions.
- **Pairs.** Per base, eight nested sequences: i uniform in [40, 200], and for each g in {4, 8, 16, 32, 64, 128, 256, 512},
  j = i + g + r with r uniform in {0, 1, 2, 3} (the advisor's point: L depends on g mod 4 near the complete pattern).
- **Per pair.** Steps apart d; the least bond L (or undefined, or a blow-up past 20,000 states, counted separately); its members;
  the number of **open windows** between them (positions m in [i + 3, j] whose four distinctions m − 3 .. m do not carry all four
  possible knots).
- **Rechecks.** Undefined pairs at g ≥ 64 (up to five per base) and four defined pairs per base again with margin 32. Every bond of
  at most ten members verified independently by a SAT solver (constrained, every member's removal free).
- **The unit is the base** (the advisor's point: at large g the nested pairs of one base share most of their stretch).

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| Q1 | **Rare closings cut the line, more closings lengthen the pieces.** Per base, g½ is the least g at which fewer than half of its eight pairs have a bond (infinite if none). The median g½ over the ten bases rises strictly over q = 0.1, 0.3, 0.5, and is at most 128 at q = 0.1. | either part |
| Q2 | **At q = 0.5 the law counts linearly.** Among bases with at least six of eight pairs defined at g = 32, 64 and 128, the ratio (L128 − L64)/(L64 − L32) of the base's median L lies in [1.5, 2.7] (linear growth gives 2) in at least 7 bases. | fewer than 7 eligible bases, or fewer than 7 inside the range |
| Q3 | **More closings, a shorter unit.** At g = 64, the median over bases of the base's median L (bases with at least four of eight defined) falls strictly over q = 0.3, 0.5, 0.7, 0.9. | any step not strictly lower |
| Q4a | **What the law counts is open windows.** At q = 0.7 and 0.9 and g = 256, over the defined pairs (at least 20), the Spearman correlation between L and the number of open windows between the pair exceeds 0.5. | either q below, or too few pairs |
| Q4b | **Near the complete pattern the count is slow, not a fold.** At q = 0.9, the base's median L at g = 512 exceeds that at g = 128 by at least 3 in at least 8 of the 10 bases. | fewer than 8 |
| Q5 | Reported only: pairs tied (L = 2) at g ≥ 32, per q. | — |

Controls (a failure is a bug): the complete pattern, the chain, and the programme against brute force on 300 small patterns; every
SAT-verified bond confirmed.

## Decision rules

- **Q1 holds:** when closings are rare the law reads the never-ending line as pieces it does not bind together, and the pieces
  lengthen with the closing rate.
- **Q2 and Q3 hold:** where the law binds far distinctions it counts linearly, in a unit that shrinks as closings fill the line in.
- **Q4a holds:** the count is of open windows, the places where not every knot is present, not of distinctions or steps.
- **Q4b holds:** the line near the complete pattern is counted slowly, not folded into a repetition; **fails:** a fold.

## Pilot (disclosed)

Exploration in the session's scratchpad (seeds 3, 7 and 11, one base per q, three pairs per gap) gave: q = 0.1, defined at g ≤ 16,
mostly undefined at g = 64, undefined at 128 and 256; q = 0.5, L about 6, 14 and 26 at g = 16, 64 and 128 (d about 6, 23, 45),
undefined at 256; q = 0.9, L about 3, 4, 5 and 10 at g = 16, 64, 128 and 256 (d about 6, 22, 43, 87); margin 16 agreed with
margin 8 wherever both were computed. One smoke-test base at q = 0.5 (the frozen code, seed of base 0) was read before freezing:
defined to g = 64 and undefined beyond on its first two sequences. The advisor model reviewed a draft of these predictions and
judged the first draft's Q2, Q4 and Q5 nearly settled by the pilot; they were replaced by the linearity ratio, the open-window
correlation and the slow-count test, and the base made the unit.

## Stop rule and runtime

One run, its summary, a referee pass on the method and the result. About ten minutes on six workers, under
`systemd-run --user -p MemoryMax=16G -p MemorySwapMax=0`.
