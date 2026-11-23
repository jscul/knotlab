# Counting null for the five-founder clock under the rule

Written by hand before any value was computed, as the pre-registration's "Null"
asks (`research/REVIEW-LEADS-20261123-001F/preregistration.md`). Nothing below
comes from a run of this study's code.

## Notation

The clock has five live knots at every stage `t` (stage 0 is the five founders,
stage `t` is after `t` parent steps). Number them `K_t(0..4)` around the
five-cycle of the clock, so that at stage `t+1` the five newborns are the
children `K_{t+1}(p)` of the parent pairs `{K_t(p), K_t(p+1)}`, `p` mod 5. Each
live knot holds exactly two loose distinctions. Write `c_p(t)` for the number of
ones among the two loose distinctions of `K_t(p)`, so `c_p(t)` is 0, 1 or 2.
The carried count is `C(t) = sum_p c_p(t)`, between 0 and 10.

`K_t(p)` pays one loose distinction to each of its two children: value `a_p` to
`K_{t+1}(p)` and value `b_p` to `K_{t+1}(p-1)`, with `a_p + b_p = c_p(t)`.
The newborn `K_{t+1}(p)` therefore receives the two incoming values
`x_p = a_p` and `y_p = b_{p+1}`. It holds four distinctions: those two and its
two fresh ones. A word of four places that is both even and not all equal has
exactly two ones (the rule at three and four places). So under the rule

    c_p(t+1) = 2 - x_p - y_p = 2 - a_p - b_{p+1}.            (R)

The receiver is `K_t(0)` at each stage and its return is the birth of
`K_{5j}(0)` for `j = 1..6`. A return signals when its two incoming values differ.

## What counting alone gives (derived by hand)

H1. No removal. For every pair of incoming values `x, y` in {0,1}, the number
`2 - x - y` is 0, 1 or 2, and two fresh distinctions can carry exactly that many
ones. So every old word has a lawful completion at every birth, at every step,
under the rule. The same holds for parity alone (two fresh distinctions give
either 0 or 2 ones or exactly 1, whichever the parity needs) and for
not-all-equal alone (two free fresh distinctions can always avoid a constant
word). So on the clock every lawful valued start survives all 30 parent steps,
in every arm. Hand prediction for P1: it fails on the clock (every start
survives there), whatever happens on the other structures.

H2. A signal is a single. The two incoming values of a newborn differ exactly
when `x_p + y_p = 1`, which by (R) is exactly when `c_p(t+1) = 1`. So a return
signals exactly when the receiver holds exactly one one among its two loose
distinctions. Call a live knot with `c = 1` a single. A single is also the only
place where a free choice exists: it chooses which child receives its one,
`(a_p, b_p) = (1,0)` or `(0,1)`. Knots with `c` in {0,2} pay `(0,0)` or `(1,1)`
by counting alone.

H3. Carried count. Summing (R) over `p`:
`C(t+1) = 10 - sum_p (a_p + b_{p+1}) = 10 - sum_p (a_p + b_p) = 10 - C(t)`.
So on every history of every start under the rule, `C(t) = C(0)` at even `t` and
`C(t) = 10 - C(0)` at odd `t`. Write `C0 = C(0)`, the number of ones among the
ten loose distinctions of the founders.

H4. Parity of singles. The number `S(t)` of singles at stage `t` satisfies
`S(t) = C(t) mod 2`, so `S(t) = C0 mod 2` at every stage.

H5. Forced starts. If `C0 = 0` every founder pays `(0,0)`, every newborn receives
`(0,0)` and by (R) carries 2; then every knot pays `(1,1)`, every newborn
receives `(1,1)` and carries 0; and so on. If `C0 = 10` the same alternation
runs the other way round. In both cases every knot at every stage has `c` in
{0,2}, no choice ever arises, the history is unique, every return has equal
incoming values, and the signal fraction is 0. This start class is forced by
counting alone.

H6. Every other carried count leaves a choice. If `1 <= C0 <= 9`, then either
some founder is a single at stage 0 (a choice), or every `c_p(0)` is 0 or 2 and
not all equal, so some cyclically adjacent pair has `c_p = 0` and `c_{p+1} = 2`
or the reverse; then newborn `K_1(p)` receives `(0,1)` or `(1,0)`, is a single
at stage 1, and offers a choice there. Distinct choices give distinct values on
some (child, parent) edge, so they are different histories. So a start has
exactly one history if and only if `C0` is 0 or 10; every other start has at
least two (this uses only stages 0 and 1 of the 30).

H7. The case `C0 = 1` (and `C0 = 9`, by complementing every value, which the
rule allows because exactly two ones among four is also exactly two zeros).
Take one single at stage 0 and every other knot at 0. By (R) the next stage has
every other knot at 2 and one single at `p0` or `p0 - 1`; then the background is
0 and again one single, and so on: there is exactly one single at every stage,
it is the only choice, and at each stage it goes to one of two positions: stays
or moves back one place mod 5, each by exactly one choice. So there are exactly
`2^30 = 1,073,741,824` histories per start with `C0 = 1` or 9. Let `x_t` be the
position of the single at stage `t`; a return `j` signals exactly when
`x_{5j} = 0`. Over five steps the displacement `r` (mod 5) can be obtained in
2, 5, 10, 10, 5 ways for `r = 0,1,2,3,4` (from the number of subsets of five
steps whose size is congruent to `r`). From position 0 the next return is again
at 0 in 2 of the 32 five-step choice sequences and elsewhere in 30; from any
position every residue is reachable. So every sequence of six signal values is
realized and every signal count 0..6 occurs; the counts of histories at each
signal count follow from this transition table and are the number to check
against the run. The quiet start has `C0 = 0`.

## The null, stated for comparison

For the clock under the rule, with the carried count `C0` of the start:

| `C0` | histories (hand) | signal fractions (hand) |
| --- | --- | --- |
| 0 or 10 | 1 | {0}, forced |
| 1 or 9 | exactly 2^30 | all seven values 0, 1/6, ..., 1 |
| 2..8 | at least 2 (not derived) | predicted all seven values, not proved by hand |

So counting alone forces a fraction (the value 0, with a unique history) only
for the starts whose carried count is 0 or 10, and for no other carried count.
The hand prediction for the three clock predictions of the pre-registration is:

- P1 fails on the clock (H1): all lawful valued starts survive 30 parent steps.
- P2 fails for every start with `C0` between 1 and 9 that has more than one
  signal fraction; it holds for the starts with `C0` in {0, 10}. For `C0` in
  {1, 9} it fails by H7. For the others it fails if the predicted full range
  holds.
- P3 fails if two or more of the seven fractions occur among the starts, which
  H5 and H7 already give (0 and every other value).

Carried count by stage, under the rule, on every history: `C0, 10 - C0, C0, ...`
(H3). Number of singles by stage has the parity of `C0` (H4).

If a run disagrees with a statement above, the run is the finding and this file
stays as it was written.
