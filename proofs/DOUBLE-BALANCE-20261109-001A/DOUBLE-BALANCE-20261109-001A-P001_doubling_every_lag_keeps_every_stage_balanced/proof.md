# Doubling every lag keeps every stage balanced; slower doubling does not

Status: Proved by hand (the lemma and the theorem). The finite claims are checked exactly in `check.py`; check 3 is a computation, not a
theorem.

Ticket `DOUBLE-BALANCE-20261109-001A`, 2026-11-09.

## Standard statement

- **Networks.** Running networks of rule-60 rings with law (12, 12) contacts, every corner holding an own cell, read as one space-time law
  (`TIME-KNOTS-20261107-001A`): every cell's value is a sum mod 2 of born cells. A contact **binds** ring X at a lag when its value
  depends on one of X's own born cells (A32). A **stage** is the network fixed from a lag on; it is **balanced** when, read from that lag
  with the history as it stands, every contact binds both of its rings at every later lag. The **static stage** is the same network run
  from an open first row; it is balanced when its returns cancel (`LOOP-NET-20261108-001A`), as every square torus with both sides at
  least 3 is (`GROW-NET-20261108-001A`, Theorem 1).
- **The doubling law.** At a doubling lag every ring splits into a 2 × 2 block: a band at every cut both ways, every contact cut and both
  halves born, the new rings born (`GROW-ALL-20261109-001`). Doubling every P lags repeats it.
- **X's part.** For a ring X, the X-part of a cell is the part of its value over X's own born cells.

**Lemma (transfer).** Suppose that at a lag t, for a ring X of the network, every cell other than X's own cells has zero X-part, and the
X-parts of X's own cells are linearly independent. Then for every contact c and every k ≥ 1, c binds X at lag t + k in the network fixed
from t exactly when c's value at lag k in the static stage depends on X's own first-row cells.

**Theorem (doubling every lag).** Under the doubling law at every lag, from any square tube with both sides at least 3, the lemma's
hypothesis holds for every ring at every lag. Hence every stage is balanced at every lag: whenever growth stops, every contact binds
both of its rings at every later lag.

**Computed (doubling every P lags).** From the 3 × 3 tube at g = 2, up to 48 × 48: with P = 3 the hypothesis holds at every doubling lag
and every stage is balanced; with P = 2, 4, 6 and 8 own cells hear other rings from the second doubling on and a stage is unbalanced
by 24 × 24 at the latest. See check 3 for the lags.

## Proof of the lemma

From lag t the network is fixed, with one-step map M, and a cell's value at t + k is the sum, over cells b, of (M^k)_(c b) times b's value
at t. Its X-part is therefore Σ_b (M^k)_(c b) · (X-part of b at t). By hypothesis only X's own cells contribute, and their X-parts are
independent vectors, so the sum is zero exactly when (M^k)_(c b) = 0 for every own cell b of X. That is exactly when c's value at lag k
in the static stage, where X's own cells start as independent open distinctions, does not depend on them. ∎

## Proof of the theorem

By `GROW-HORIZON-20261109-001A`, Theorem, under doubling at every lag no cell outside X's own cells ever holds a part of X's own born
cells at a doubling lag: contacts are newborn, and other rings' own cells never hear X. For the independence, follow X's own cells: at
every lag the contacts are newborn before the step, so an own cell reads itself and its left neighbour, an own cell or a contact with
zero X-part. In each corner of X, with own cells a_1, …, a_l after a contact, the X-parts evolve by a_1 ← a_1 and a_j ← a_j + a_(j − 1),
a unipotent map; a doubling keeps X's own cells. So the X-parts of X's own cells at any lag are the image of X's born cells under an
invertible map, independent. The lemma applies at every lag t, and c binds X at every lag after t in the stage fixed from t exactly when
it does in the static stage, a square torus with both sides at least 6 (at least 3 before the first doubling), which is balanced. The
same holds for c's other ring. ∎

## Remarks

- **Balance by isolation.** The doubling law keeps its contacts' knots across growth because it isolates its rings: every ring hears only
  itself, so each stage starts, ring by ring, from what is in effect an open first row. Slower doubling lets rings hear each other, and
  then the old mixtures break the cancellation that keeps contacts persistent. In the schedules read, balance and hearing exclude each
  other: P = 3 at g = 2 keeps both isolation and balance, by a cancellation particular to corners of one cell.
- **Single cuts.** The theorem is about the doubling law, every ring split at once. That each single cut is allowed, which is how
  `GROW-ALL-20261109-001`'s order-free rule arrives at the doubling, is read there to lag 2 and is not proved here; its lag-3 readings
  remain an unconfirmed census.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | The hypothesis at every doubling lag of doubling every lag: 3 × 3 to 48 × 48 and 3 × 4 to 24 × 32 at g = 2, 3 × 3 to 24 × 24 at g = 3 | pass |
| 2 | Every one of those stages balanced, read through a full cycle | pass |
| 3 | Computed: doubling every P = 2, 3, 4, 6, 8 lags from 3 × 3 at g = 2, to 48 × 48: the hypothesis and balance at each doubling lag | pass |

## Nonclaims

- **Square tubes, the band law's doubling**; two-time knots (A30); declared rings (A45).
- **The slower schedules are computed** to 48 × 48 at g = 2; that every non-isolating schedule loses balance is not proved.
