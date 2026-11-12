# Locks across two shifts

Status: Proved (G1 and G2 by hand, checked with the advisor model) with an exact census and a linear control; **referee pending** (the
background referee thread). Ticket A of `research/SHIFT-LOCK-20261112-001/preregistration.md`, frozen with the code in commit
`4a511977a`.

Words as in the pre-registration: copy shifts e₁ = (1, 0), e₂ = (0, 1) of the n × m repeat; the harmony's own shift σ and flip κ,
G = ⟨σ, κ⟩; unmixed knots (x, x + e, x + 2e); the mixed knot (x, x + e₂, x + e₁); stepped states; a state invariant along a step v
(X(x + v) = g·X(x) at every copy, some g in G); short steps (both counts at most 2); locked.

## 1. Unmixed knots reduce to rings (G1; proved; 945 of 945)

The repeat with both unmixed knots locks exactly when the ring of n knots and the ring of m knots both lock. If both lock, each row is
a state of the ring of m and each column one of the ring of n, so all are constant, and the rows' constants are equal along each
column. If the ring of m has a non-constant state s, then X(r, c) = s(c) is a state: its row knots are the ring's, and its column knots
see (s_c, s_c, s_c), which R allows because R holds the diagonal. Likewise for n. ∎ So copies along two shifts with unmixed knots lock
at exactly the pairs of ring lengths that lock (the referee's rule for rings, `LOOP-LOCK-R1`): no collective lock, and no failure when
both lock. Checked on all 45 harmonies, n ≤ m in 3..8 (`result_one.json`), and my ring verdicts at 3..8 agree with the referee's on
270 of 270.

## 2. Stepped states (G2; proved; no exception)

G is abelian and keeps R (shifting every member, or flipping every value, keeps not-all-equal at every place). So the mixed knot at
(r, c) of X(r, c) = g^r h^c u is g^r h^c applied to (u, hu, gu), allowed when R(u, hu, gu); g^n u = u and h^m u = u make X well defined.
Every stepped state the census built was a state.

## 3. The mixed knot (exact on the range)

**Mixed repeats n, m = 2 to 9, all 45 harmonies (2,880 cells; `result_two.json`).**

| Outcome | Cells |
| --- | --- |
| locked | 323 |
| unlocked, and every non-constant state invariant along a short step | 1,303 |
| unlocked, with a state invariant along no short step (34 harmonies) | 878 |
| of these, no non-constant state invariant along a short step at all (H0 fails; 10 harmonies) | 78 |
| no-short-step search not settled within its bound | 376 |

- **H0 fails in 78 cells (frozen: "Yes, the discovery", in its weaker form).** In each, the repeat unlocks, yet no non-constant state
  is invariant along a short step: whether it is open is decided by states that are not a walk around one cycle. The cells:
  `0011 + 01`, `00001111 + 00011011 + 00100111 + 00101101 + 0011` and the seven-orbit harmony with `0011 + 01` at the same 14 sizes
  (3 × 5, 3 × 7, 5 × 3, 5 × 6, 5 × 7, 5 × 9, 6 × 5, 6 × 7, 7 × 3, 7 × 5, 7 × 6, 7 × 9, 9 × 5, 9 × 7), `00001111 + 0011` at 10 of
  them; `00001111 + 00101101 + 01` at 12; `0010011011` at 6 (7 × 6, 8 × 6, 8 × 7, 9 × 6, 9 × 7, 9 × 8); `0000011111` at 3;
  `00001111 + 01` and `000000111111 + 01` at 2 each; `000111` at 1 (7 × 5).
- **The squares do not show it.** On n × n, n = 2 to 16 (675 cells; `result_square.json`), H0 holds on every cell: each square that
  unlocks has a non-constant state invariant along a short step. So the strongest form frozen (such sizes recurring along the squares
  with a growing shortest step) did not appear.
- **No linear case.** No orbit of any of the 45 harmonies has increments holding a whole graph {(a, λa)} with λ not 0 or 1, so no
  Ledrappier-type linear automaton sits inside the census.

**The linear control (`result_control.json`).** Ledrappier's law on n × n has a non-zero state exactly at n = 3, 6, 7, 9, 12, 14, 15,
18, 21, 24, 27, 28, 30, 31 for n ≤ 32, as the advisor predicted from (1 + S)^n + 1 and S^n + 1 sharing a factor (32 of 32). At 7, 12,
14, 15, 21, 24, 28, 30 and 31 not every state is invariant along a short step, and at 31 none is (a space of dimension 30 with no
non-zero state invariant along any short step): the discriminator sees the linear case where it exists.

**Ring ties (`result_ringties.json`; the coordinator's "how much does one copy fix as n grows").** On rings of 6 to 60 knots: a locked
ring ties all n copies (85 of 85 cells); a ring unlocked only through components of period p > 1 ties exactly the copies at multiples
of L, the least common multiple of those periods, n / L in all (160 of 160); a ring unlocked through a component of period 1 ties copy 0
alone (158 of 160; `000111` and `000111 + 01` tie two copies at 6). So one copy fixes every L-th copy at every length: influence of
unbounded reach, by a walk around one cycle.

## 4. After the run (descriptive; labelled; not frozen)

- **The 78 states checked independently (`after_run_broad.py`).** Each found state satisfies every copy's own kinds and every mixed
  knot by direct evaluation of not-all-equal on its bits, without R, and none is invariant along any step at all (any length) up to the
  shifts and flip. For the 8 harmonies with at most 20 states (50 cells), every permutation of the states keeping R was found (6 to 32
  of them; 16 outside the shifts and flips for `00001111 + 0011`), and none gives a non-constant state invariant along a short step;
  not computed for the two largest (28 cells). In all 78 cells copy 0 is tied to no other copy.
- **Lock shapes to 16 × 16 (`after_run_wedge.py`, the 22 harmonies with a locked cell).** Locks that hold at every size of a family are
  of two kinds only: strips, where one count stays small (2 to 7), so the repeat is a ring of short rows with a finite transfer; and
  short-step arithmetic: `0011` locks exactly when 4 ∤ m and gcd(n, m) ≤ 3 (225 of 225, `after_run_tiling.py`). Otherwise locks are sporadic: 5 × 5 for
  `0011 + 01`; 6 × 6, 9 × 9, 9 × 11, 11 × 9 and 11 × 11 for `00001111 + 00101101 + 01`.
- **What the two-way states are, for `0011 + 01` (by hand, then checked).** On the orbit of 0011 the increments are
  A = {(0, 0), (1, 2), (1, 3), (2, 3)} modulo 4: the three members of a mixed knot are equal, or three distinct phases in increasing
  order. Lifting phases to whole numbers, a cell steps by +1 or +2 along e₂ and by −1 or −2 along e₁, of three types (1, −2),
  (1, −1), (2, −1), and no unit square can wind (its lifted sum lies in [−2, 2] and is a multiple of 4). So a state with no
  constant cell is a height function with three cell types, the kind that describes tilings (the literature's height functions; Thurston, 1990), whose average
  slopes (S_c / m, S_r / n), with S_c, S_r the windings, multiples of 4, must lie in the slope polygon x ≥ 1, |y| ≥ 1, x + |y| ≤ 3
  (counting the cells of each type), as for the dimer model (Kenyon, Okounkov and Sheffield, 2006). The repeat locks exactly when that
  polygon has no point: 225 of 225 cells to 16 × 16 (`after_run_tiling.py`). All 14 of its found states with no short step use only
  the orbit of 0011 and all three cell types. When the only points have slopes that are not whole numbers, every state mixes cell
  types and repeats along no step, as at 3 × 5. So the two-way states are mixed tilings, and their arithmetic is the polygon's.

## What this establishes

- Proved: two copy shifts with unmixed knots add nothing to the rings; stepped states are states.
- Exact on the range: under the mixed knot, states that repeat along no short step occur in 34 of 45 harmonies, and in 78 cells they
  are the only way the repeat unlocks; on squares to 16 they never are; no harmony's increments are linear.
- After the run: those states are verified, repeat along no step at all, tie nothing, and for one harmony are mixed tilings whose slope
  polygon decides every lock to 16 × 16. Locks at every size of a family come only from strips and short-step arithmetic.
- Not established: a rule for every size (the polygon rule is a check to 16, not a proof), the automorphism check for the two largest
  harmonies, and whether any law of the program puts a linear automaton inside its increments.
