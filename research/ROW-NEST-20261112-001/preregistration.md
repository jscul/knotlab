# Rows that grow by one: pre-registration

Epic `ROW-NEST-20261112-001` (`NEST-COUNT-20261112-001` direction 2; G17, with G1), 2026-11-12, at the coordinator's go-ahead.
Frozen before the registered run. The canonical K1–K3 test is unchanged. The law is NAE on three-place knots on distinct
distinctions.

## The question

`NEST-COUNT-20261112-001` proved that nested patterns whose self-holding knots meet their outside in three distinctions are
finite-state: their fate repeats with depth. The smallest escape passes one more distinction per depth. Does a pattern then count:
does its life at depth t, or what its first row allows, depend on t without a period? Or does it only make harmonies (a dependence
on t with a period)? And how common is each under a weighting by short descriptions?

## In standard terms

For NAE window-1 rules on a growing triangle (rows of length 3, 4, …, 3 + t, the last closed by consecutive triples): the
satisfiability of the depth-t triangle and the projection onto its first row, as sequences in t ≤ 40.

## The extension (frozen in `census.py`)

A definition's ends are a row of k distinctions; its body makes a new row of k + 1 and holds itself on it. Between the rows a fixed
rule: for each new position i, its knots among the relative positions old i − 1, old i, old i + 1, new i − 1, new i (a knot touching
a missing position at a row end is left out). The first row has 3 distinctions. At depth t the bottom row is closed by a knot on every
three consecutive distinctions, as a self-holding knot is closed by a knot at depth 1. Rules: the 1,024 subsets of the 10 possible
relative knots. Weight of a rule: 2^−(gamma(#knots + 1) + log2 C(10, #knots)) (short descriptions; A79's kind of code). **"Lives at
depth t"** is the depth-t triangle allowing a state; nothing is claimed about the infinite triangle.

## Settled by definition (stated, not tested)

- Without the closing bottom row the depth-t + 1 triangle would contain the depth-t one, so life would only fall and the first-row
  relation only shrink: no counting by construction (the advisor's). The closing row is what lets depth matter.
- The first-row relation is one of 16 sets (complement classes of three distinctions), so it can count only by when it changes.
- The empty rule lives at every depth (the closing row alone allows 0011… patterns). The weighting puts about half its weight on
  rules with at most one knot; weights are reported given at least one knot, and by number of knots.
- Prior work: space-time diagrams of cellular automata; the seeded domino problem (Wang 1961) shows counters need richer local rules
  in general; NAE window-1 rules are monotone and complement-symmetric, so they may be too weak (the advisor's).

## Classification (frozen)

For each of the sequences alive(t) and T_t (t = 1..40): **constant**; **eventually periodic**, the smallest period p ≤ 10 holding
from some depth a ≤ 20 to depth 40 (eventually constant when p = 1; a **harmony** when p ≥ 2); else **unexplained within 40**, a
candidate counter.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| Q2 | **NAE window-1 rows do not count.** No rule has an unexplained alive(t) or T_t within depth 40. | any rule does |
| Q3 | **They do make harmonies.** At least one rule's life at depth t depends on t with a period of 2 or more. | none |
| — | Reported: shares by class given at least one knot and by number of knots; the depth of the last change of T_t; rules dead at 40; the smallest harmonies. | — |

The advisor model reviewed a draft cold (`advisor_review_answer.md`): it showed the draft's observable monotone (so its counting test
vacuous), proposed the closing bottom row, and asked for weights given at least one knot. Adopted.

## Plumbing (disclosed)

A plumbing run on 8 rules printed only timing, sizes and the first line (the empty rule, alive at every depth, as settled).

## Stop rule and runtime

One run on 8 workers (about a minute), its summary, a hand-off to the referee thread, report.
