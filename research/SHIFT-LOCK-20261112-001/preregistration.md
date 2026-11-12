# Pre-registration: locks across two shifts

Epic `SHIFT-LOCK-20261112-001` (`LOOP-LOCK-20261112-001` direction 1, "why rings lock by arithmetic", taken to the arrangement of
copies along two shifts; G17 with G8; program mathematics, group arithmetic), written on 2026-11-12 before the census runs, at the
coordinator's go-ahead under the owner's standing mandate. Code frozen with this file in
`proofs/SHIFT-LOCK-20261112-001A/SHIFT-LOCK-20261112-001A-P001_two_shift_locks/` (`shift_lib.py`, `check.py`). The canonical K1–K3 test
is unchanged.

## What is already settled, and by whom

- **Rings lock by arithmetic, at every length: the referee's proof** (`LOOP-LOCK-R1`,
  [report](../LOOP-LOCK-20261112-001/referee-R1/report.md), `result_rings.json` with its certificates). A ring of n knots
  (j, j + 1, j + 2) is a closed walk of length n of the transfer on pairs of states; from the strongly connected components of that
  transfer and their periods, 4 of the 45 harmonies lock rings of every length, 21 every length outside a residue class (14 of them every
  odd length), 20 finitely many lengths. For 40 of 45 the off-diagonal pairs on cycles are shears (u, σ^c u); which shears a harmony
  admits is real content, and given them the arithmetic is the period. This epic credits that proof and does not prove it again; its
  ring lists are used as a cross-check, never as input to a verdict.
- **The classical mechanism.** Rings are periodic points of a one-dimensional shift of finite type whose symbols are the harmony's
  states (Lind and Marcus, cyclic structure and periods, chapter 4 and section 6). In two dimensions the picture changes: the sets of
  periods of two-dimensional shifts of finite type can be as complex as any NE set (Jeandel and Vanier), and for **Ledrappier's law**
  x(r, c) + x(r, c + 1) + x(r + 1, c) = 0 over two values (Ledrappier, 1978; periodic points of algebraic actions of ℤ², Kitchens and
  Schmidt, Lind, Schmidt and Ward, Schmidt's book) the square repeats that have a non-zero state follow polynomial arithmetic over F₂,
  and that set is provably not eventually periodic (every 2^i − 1 has one, every 2^k has none). Shifts given by a row relation and a
  column relation are Markley and Paul's matrix subshifts (1981); axial powers are Louidor, Marcus and Pavlov's. So the question here is
  not whether two-dimensional patterns can be arithmetic beyond cycles (they can, classically), but whether **the program's own
  stitched harmonies** do.

## Words

As in `LOOP-LOCK-20261112-001` and the glossary: harmony, one-order stitch (the one-knot relation R ⊆ W³ on the harmony's states W),
finite repeat, locked (every copy equal to every other, place by place, in every state). New, plain (checked with the advisor model):

- **The copy shifts.** Copies sit at (r, c) in the n × m finite repeat of an arrangement with two shifts e₁ = (1, 0), e₂ = (0, 1).
  "Shift" here always means a copy shift; the harmony's own shift inside a copy is written σ, and κ flips every value. G = ⟨σ, κ⟩
  acts on W, is abelian, and keeps R.
- **Unmixed knots:** (x, x + e, x + 2e) for one copy shift e. **The mixed knot:** (x, x + e₂, x + e₁), the literature's three-dot
  shape of Ledrappier's law.
- **Stepped state:** X(r, c) = g^r h^c u with g, h in G and R(u, hu, gu): each step along a copy shift applies one fixed symmetry of
  the harmony (the twist of `TWIST-PIN-20261112-001` held the same on every step; the literature's constant voltage).
- **A state invariant along a step v** (up to a symmetry): X(x + v) = g·X(x) at every copy x, for some g in G. A **short step** has
  both counts at most 2 (12 steps up to sign, those not zero on the repeat). A state invariant along a short step is a walk around one
  cycle of a finite transfer (the one-shift quotient along v, with the symmetry g carried as a twist); a state invariant along no short
  step is not, and is called below a **state with no short step**.
- **Increments** on one orbit of period p: A_u = {(a, b) mod p : R(u, σ^a u, σ^b u)}. A state on that orbit is a function
  φ: Z_n × Z_m → Z_p with (φ(r, c + 1) − φ(r, c), φ(r + 1, c) − φ(r, c)) in A_u at every copy (the advisor's reduction).

## Settled by hand (before the run; checked with the advisor model)

- **G1 (unmixed knots reduce to rings).** The repeat with both unmixed knots locks exactly when the ring of n knots and the ring of m
  knots both lock. If both lock, every row and every column is constant, so everything is. If the ring of m has a non-constant state s,
  X(r, c) = s(c) is a state, since the column knots see (s_c, s_c, s_c), which R allows; likewise for n. So two copy shifts with
  unmixed knots add nothing to the rings: no collective lock and no failure when both lock.
- **G2 (stepped states are states).** G is abelian and keeps R, so the knot at (r, c) is g^r h^c applied to (u, hu, gu); and g^n u = u,
  h^m u = u make X well defined on the repeat. Every ring state read through 2r + c (X(r, c) = s(2r + c mod k), k dividing m and 2n)
  is also a state; it is invariant along the short step (1, −2).
- **The linear case (the advisor's).** If A_u holds a whole graph {(a, λa)} with λ not 0 or 1 modulo p, the orbit's states include a
  linear cellular automaton φ(r + 1, c) = (1 − λ)φ(r, c) + λφ(r, c + 1) over Z_p, whose repeats follow polynomial arithmetic of
  Ledrappier's kind. **The triple test (the advisor's, sufficient):** if the only triples (e, e′, e″) in A_u³ with
  e₁ − e′₁ = e₂ − e″₂ are e = e′ = e″, every state on that orbit is stepped.

## The census (frozen)

- **one.** All 45 harmonies, unmixed repeats n ≤ m in 3..8: locked against "both rings lock" (G1); my ring verdicts at 3..8 against the
  referee's lists.
- **two.** All 45 harmonies, mixed repeats n, m in 2..9: locked or not; whether some non-constant state is invariant along a short step
  (H0); a non-constant state with no short step, found by refining the solver against every short invariance a found state has (H0',
  up to 400 rounds), with its shortest invariant step; stepped states checked to be states (G2); each orbit's increments, graph
  subgroups and triple test. Every solver call in the short and no-short-step searches is bounded by 20,000 conflicts; a cell past
  the bound is "not settled" and reported as such, never counted for or against a claim.
- **square.** n × n mixed repeats, n = 2 to 16, all 45: H0; H0' to 12.
- **control.** Ledrappier's law on n × n, n = 1 to 32, by rank over F₂ ("locked" there means only the zero state, since the law does
  not allow the constant 1); for each short step, the dimension of its states invariant along it.
- **ringties.** Rings of n in {6, 8, 12, 16, 24, 30, 36, 48, 60} knots, all 45: the copies tied to copy 0 (the coordinator's "how much
  of the ring does one copy's state fix, and does that hold as n grows").
- **Cap.** 1 hour and 16 GB per part (systemd); each harmony's rows are saved as they finish, and a part stopped at its cap is
  reported with the harmonies it reached.

## What counts (frozen)

The coordinator's question: **is there a pattern family whose influence is unbounded in size and is not a walk around one cycle?**

- **Yes (the discovery).** H0 fails: a mixed repeat that unlocks although no non-constant state is invariant along a short step, so
  that whether it locks is decided by states with no short step; strongest if, along the squares, such sizes keep appearing and the
  states' shortest invariant step grows, as in Ledrappier's law.
- **Partly.** H0' fails but H0 holds: states with no short step exist, but every unlocking is also made by a short-step state, so
  locking is still decided by walks around one cycle.
- **No (the obstruction).** H0 and H0' hold on the range: every state of every mixed repeat is a walk around one cycle with a symmetry
  carried along, and two copy shifts add nothing beyond the rings' arithmetic. Recorded as an obstruction on the range, not a theorem.
- **Controls.** G1 on every cell (a theorem; a failure is a correction of this file); G2: no stepped state that is not a state;
  Ledrappier's law unlocks exactly at the advisor's sizes.

## Predictions (frozen; the advisor's unless marked)

- G1 on every cell; G2 everywhere (theorems).
- H0′ fails widely: harmonies whose R(x, x, y), R(x, y, x) or R(x, y, y) has a non-diagonal pair, and free harmonies (domain walls
  between readings) have states with no short step (90%).
- H0 holds wherever no orbit's increments hold a graph subgroup with λ not 0 or 1 (mine, 70%); H0 fails somewhere in the census (mine,
  35%).
- Some of the 4 harmonies whose rings always lock unlock a mixed repeat, through R(u, hu, gu) with g ≠ h² (mine, 60%).
- Single-orbit harmonies passing the triple test show no state with no short step (a theorem's consequence, 99%).
- Ledrappier's law, n ≤ 32: unlocks exactly at 3, 6, 7, 9, 12, 14, 15, 18, 21, 24, 27, 28, 30, 31 (90%); at some unlocking size not
  every state is invariant along a short step (mine, 75%).
- Ring ties: a locked ring ties all n copies; a ring unlocked only through components of period p ties the n/p copies at multiples of
  p; a ring unlocked through a component touching the diagonal ties copy 0 alone (80%).

## Seen before the freeze (disclosed)

Smoke tests of the code, before this file: the alternation 01 at the mixed repeats 2 × 2 to 3 × 3 and 0011 at the same sizes, with an
earlier, narrower family (stepped states and rings read through 2r + c). The alternation's R is {(u, u, w)} (the first two members
equal, the third free), so its mixed repeats have every row constant and the rows free: at 3 × 2 it unlocks with no stepped state and
no ring read through 2r + c. That is why the frozen family is "invariant along a short step" (here the step (0, 1)), as the advisor also
advised. The linear control's kernel dimensions for n ≤ 11 (2 at 3, 4 at 6, 6 at 7, 2 at 9, else 0). Timing of the largest harmony
(128 states) at 9 × 9, 12 × 12 and 16 × 16, which set the conflict bound (only the times and solver rounds read).

**Referee.** The background referee thread (referee pending). Assumptions in force: A70, A75 (Assumed). Nothing here bears on P versus
NP.
