# A band inserted while the network runs keeps only the knots it has not reached

Status: Proved by hand. The finite claims are checked exactly in `check.py`; checks 3, 4 and 6 are computations, not theorems.

Ticket `GROW-RUN-20261109-001A`, 2026-11-09.

## Standard statement

- **Networks.** The n × m tube of equally spaced rule-60 rings with law (12, 12) contacts (`GROW-NET-20261108-001A`), rings (i, r) with i
  round the seed loop and r along the tube; each stage is balanced: every contact binds both of its rings at every lag
  (`GROW-NET-20261108-001A`, Theorem 1).
- **Growth while running.** The network runs from its first row at lag 0. At lag t0 a band of n new rings is inserted after row r: the
  contact v(i, r) now joins (i, r) to the new ring (i, r*), a new contact v(i, r*) joins (i, r*) to (i, next r), and the new rings and
  their contacts along the band are born, their cells new open distinctions from lag t0 (A44). The cut contact's value goes by one of
  four **splits**: lower (v(i, r) keeps it, v(i, r*) is born), upper (the reverse), fresh (both born) or copy (both keep it). From t0 on
  the network is the next stage.
- **The whole history as one law.** The run is read as one space-time law (`TIME-KNOTS-20261107-001A`): each cell's value is a sum mod 2
  of born cells. A contact **binds** ring X at a lag when its value depends on one of X's own born cells (A32), and it **persists**
  when it binds both of its rings at every lag. X's **footprint** at a lag is, for each of X's own born cells, the set of cells whose
  value depends on it.
- **Reached.** The insertion at t0 has **not reached** an old ring X when X's footprint at t0 in the run equals its footprint at t0 in
  the next stage run from lag 0 with the same first row.

**Theorem 1 (what the insertion has not reached is intact).** If the insertion has not reached the old ring X, then at every lag
T ≥ t0 X's footprint in the run equals its footprint in the next stage, so every contact binds X at every lag. This holds in
particular when X's first row has influenced none of the n contacts the band cuts, nor the cells across which they read, at any lag
up to t0: then no ring farther than t0 from them in time length is reached.

**Theorem 2 (the band is always bound).** Every contact binds the band's new rings at every lag after t0.

**Corollary.** An insertion at lag 0 is the next stage, and every contact persists. An insertion at a later lag keeps every contact
persistent exactly when every binding of a reached ring survives.

**Computed (every insertion lag).** On 13 tubes (n, m from 3 to 6, g from 2 to 4), reading every insertion lag through one period of
the run's state, an insertion keeps every contact persistent at lag 0 in every case and at 42 of 634 lags overall for the lower and
upper splits, 64 for fresh and 58 for copy. On three tubes and all lags below 32, 17,612 of 26,016 bindings of reached rings fail
(68%), and none of the 6,240 bindings of rings not reached, nor of the 5,120 of the band's rings. On the 3 × 8 tube the contacts that
lose a binding spread from the band one row every 4 lags each way, the time length of a row at g = 2. With a band every P lags (P = 4,
8, 16) on the 3 × 3 tube, after the fourth band only the newest band's rings keep every binding.

## Nearest known result

- **Linear cellular automata on changing graphs.** Additive automata over GF(2) and their light cones (Martin, Odlyzko and Wolfram
  1984); dynamics on time-varying networks and temporal graphs, where reachability is along time-respecting paths.
- **Classification.** Known-with-delta. Linearity and causality are classical; the delta is that the program's persistent knots across
  time survive a growth event exactly outside the event's reach, and mostly fail inside it.

## Proof of Theorem 1

From t0 on the run and the next stage evolve by the same linear map M (the next stage's), so a cell's dependence on one of X's born
cells at lag T ≥ t0 is the corresponding entry of M^(T − t0) applied to that cell's column at t0. Equal columns at t0 give equal columns
at every later lag. In the next stage, which is balanced, every contact binds X at every lag ≥ 1, hence at every lag ≥ t0; and before
t0 the run is the previous stage, also balanced. So every contact binds X at every lag.

For the sufficient condition, let y_t be the column of one of X's first-row cells at lag t under the previous stage's map M′, and y′_t
under M. The two maps differ only in the rows of the cells whose inputs change: each cut contact v(i, r), which read the cell before S
on (i, next r) and now reads the cell before S on (i, r*); the cell after S on (i, next r), which read v(i, r) and now reads v(i, r*);
and the band's cells, of which only the cell after S on (i, r*) reads an old cell, v(i, r) (lower and copy splits). If y_t vanishes on
v(i, r) and on the cell before S on (i, next r) for every t ≤ t0, then by induction y_t = y′_t for t ≤ t0 (the band's cells hold nothing
of X in either), and at t0 the split moves nothing of X. So the footprints agree. A cell's first dependence on X's first row comes no earlier
than X's time of flight to it (`DISTANCE-20261108-001B`, Theorem 2), so every ring farther than that is not reached. ∎

## Proof of Theorem 2

A cell born at t0 enters the run as a new distinction, and from t0 its column evolves by M from a unit vector, exactly as the matching
first-row cell of the next stage evolves from lag 0. So a contact's dependence on the band's own cells at lag t0 + k is the next stage's
at lag k, and in a balanced stage every contact binds both of its rings at every lag. ∎

## Remarks

- **The damage is causal.** An insertion rewires the cells the band cuts. Every ring whose first row has already flowed through them
  carries, into the new network, a mixture the new returns no longer cancel; rings whose influence has not arrived are untouched, and
  so is the band. The failing contacts fill the insertion's past light cone, read in time length.
- **Only the young are bound.** With bands arriving every P lags, each insertion reaches every ring older than it, so the persistent
  knots across time are the newest band's, until the next band reaches them.
- **The stage reading is load-bearing.** "Every stage balanced" (`GROW-NET-20261108-001`, `BAND-SURFACE-20261108-001`) is a statement
  about growth between runs (A42). Growth in time keeps persistence only at its first lags or at rare special ones.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Every stage persists, and inserting at lag 0 gives the stage, for each split | pass |
| 2 | Theorems 1 and 2: rings not reached and band rings keep every binding (3 × 8, 4 × 6, 3 × 5, lags 0 to 31, four splits) | pass: 0 of 11,360 fail; 17,612 of 26,016 reached bindings fail |
| 3 | Computed: every insertion lag of 13 tubes, four splits | pass: lag 0 always clean; 42 to 64 of 634 lags clean |
| 4 | Computed: the spread of failing contacts on the 3 × 8 tube | pass: one row every 4 lags each way |
| 5 | The dependence sets against actual bits, flipping one born cell at a time | pass: 89 flips |
| 6 | Computed: a band every P lags, P = 4, 8, 16 | pass: only the newest band keeps every binding |

## Nonclaims

- **Square tubes and the band law only**; equally spaced rings, two-time knots (A30).
- **The reached side is computed**: which reached bindings survive is read, not explained, and the clean lags beyond lag 0 are listed,
  not characterised.
- **Born cells are open** (A44); a band born with values copied from its neighbours is the copy split for the cut contacts only.
