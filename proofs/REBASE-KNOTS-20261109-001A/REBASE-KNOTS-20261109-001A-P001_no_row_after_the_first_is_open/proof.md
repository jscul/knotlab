# No row after the first is open, so knots cannot be read from the last growth event

Status: Proved by hand (the lemma and the reading as if open). The finite claims are checked exactly in `check.py`; check 3 is a
computation, not a theorem.

Ticket `REBASE-KNOTS-20261109-001A`, 2026-11-09.

## Standard statement

- **Networks.** Rule-60 rings joined by law (12, 12) contacts, every corner holding at least one own cell (`LOOP-NET-20261108-001A`): an
  own cell reads itself and its left neighbour; a contact reads the left neighbour on each of its two rings and not itself.
- **Two readings from a later row.** Let a network run from its first row, perhaps with a band inserted at lag t0
  (`GROW-RUN-20261109-001A`). Every cell's value at a lag is a sum mod 2 of born cells (the first row and the band's cells). A contact c
  **binds ring X from row t0 as if open** at lag T > t0 when c's value at T, written through the network fixed from t0 as a sum of
  row-t0 values, uses one of X's own cells. It **binds X from row t0 natively** when c's value at T is not equal, on every row t0 the
  history allows, to a function of the cells of row t0 that are not X's own: when the vector of c at T over the born cells is not in the
  span of the vectors of row t0's other cells.
- **Open.** A row is open when every assignment of its cells occurs, as the first row's do.

**Lemma (every later row has even parity).** In every such network every cell is read by exactly two cells, so the sum of all cells'
values is 0 at every lag ≥ 1. Hence no row after the first is open: each of its cells is the sum of all the others.

**Theorem (as if open, every stage persists).** Read as if row t0 were open, every contact of a balanced network binds both of its rings
at every lag after t0, whether or not a band was inserted at t0 and however its cut contact was split.

**Computed (natively).** Read natively, every contact binds both of its rings from the first row (t0 = 0) at every lag, and from any
later row t0 = 1 to 7 of the 3 × 3, 3 × 4 and 4 × 3 tubes at g = 2 and the 3 × 3 tube at g = 3, with no band inserted, every contact fails
to bind each of its rings at some lag. With a band inserted at t0 the native reading fails for most pairs too (check 3's detail).

So the breakage found by `GROW-RUN-20261109-001A` is not an artefact of reading from the first row. Reading from the last growth event
restores persistence only by treating as open a row that is not, and the native reading from a later row fails even in a network that
never grows.

## Nearest known result

- **Linear cellular automata.** Rule 60 on a ring is x ↦ (1 + s)x, which is singular over GF(2): its image is the even-weight subspace.
  Garden-of-Eden configurations of additive automata (Martin, Odlyzko and Wolfram 1984).
- **Classification.** Known-with-delta. The parity count is classical; the delta is that it rules out reading the program's knots across
  time from any row but the first.

## Proof of the lemma

An own cell i is read by itself and by the cell after it on its ring (as that cell's left neighbour), and by no other cell: a contact
reads only the left neighbours of its own position, and the cell after i is either an own cell or a contact that reads i as its left
neighbour on that ring. A contact d is read by the cell after it on each of its two rings, an own cell since every corner holds one, and
not by itself. So every cell is read exactly twice, and adding all new values counts every old value twice: the sum is 0. A row whose
cells sum to 0 is not open, and any one of its cells is the sum of the others. ∎

## Proof of the theorem

Read as if open, row t0 plays the part of a first row for the network fixed from t0, which is a balanced stage
(`GROW-NET-20261108-001A`, Theorem 1, for tubes; `LOOP-NET-20261108-001A`, Theorem 3, for every balanced network); so every contact binds
both of its rings at every later lag. ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | The lemma on 16 networks at g = 2, 3 and 5: every cell read exactly twice, the new values summing to 0 | pass: 48 |
| 1b | Ranks of rows 1 to 8 on six tubes: below the number of cells, every row of even parity | pass |
| 2 | The theorem: as if open, every contact binds at every lag after t0 (t0 = 0 to 7, four tubes, with and without a band, four splits) | pass: 160 cases |
| 3 | Computed: natively, binding from row 0 holds; from rows 1 to 7 of a network that does not grow, every contact fails at some lag | pass |

## Nonclaims

- **Linear substrates with law (12, 12)** only; a self-reading contact law or an invertible rule would need its own count.
- **The native failure is computed**, on four tubes and rows 1 to 7; which lag fails first is read, not explained.
- **Two-time knots only** (A30).
