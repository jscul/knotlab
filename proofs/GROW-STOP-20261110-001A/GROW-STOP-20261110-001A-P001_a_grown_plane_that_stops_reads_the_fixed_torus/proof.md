# A grown plane that stops reads the fixed torus's distances, scaled by the growth

Status: Proved by hand. The finite claims are checked exactly in `check.py`; check 3 is a computation, not a theorem.

Ticket `GROW-STOP-20261110-001A`, 2026-11-10.

## Standard statement

- **Growth that stops.** A running 3 × 3 (or n × m) tube of rule-60 rings with law (12, 12) contacts grows by the doubling law of
  `GROW-ALL-20261109-001` at every lag for k lags (open births), then stops: from lag k on the network is the square torus of sides
  n·2^k and m·2^k, fixed. The whole history is read as one space-time law; a contact **needs** ring X at a lag when its value depends on
  X's own born cells. The **fixed torus** is the same final network run from an open first row.
- **Readings.** The lags at which a contact needs a ring, with or without contacts frozen from the stop on (A38); hence the cut length,
  the time length and the plain first need of `DISTANCE-20261108-001B`.

**Theorem (stopping).** For every ring X of the final torus, every contact c and every lag T ≥ 1 after the stop, c needs X at lag k + T in
the stopped run exactly when c needs X at lag T in the fixed torus, and the same holds with any set of contacts frozen from the stop on.
So, read from the stop, the grown plane reads every distance between its rings that the fixed (n·2^k × m·2^k)-torus reads: the cut length
is the ring-graph distance, the time length is g·δ + 1, and the plain first need is that torus's; two original rings x and y lie 2^k·D
ring steps apart, D their original ring distance.

**Computed (slower schedules).** With doubling every P lags for two doublings and then a stop, the stopped run's needs equal the fixed
torus's for P = 3 at g = 2, which isolates its rings, and differ for 2,160 to 2,592 of 2,592 contact-ring pairs for P = 2 and 4 at g = 2 and
for P = 2 and 4 at g = 3, whose rings hear each other.

## Proof

By `DOUBLE-BALANCE-20261109-001A`, Theorem, at every doubling lag, the stop included, every ring X satisfies the transfer lemma's
hypothesis: no cell outside X's own cells has an X-part, and the X-parts of X's own cells are independent. From the stop the network is
fixed, with one-step map M (or the map with the chosen contacts frozen, which reads only itself at a frozen contact). By the lemma's proof,
c's X-part at lag k + T is Σ over X's own cells b of (M^T)_(c b) times b's X-part at the stop, and since those X-parts are independent this
is zero exactly when (M^T)_(c b) = 0 for every own cell b of X, which is exactly when c's value at lag T in the fixed torus run by the same
map does not depend on X's own first-row cells. The readings of `DISTANCE-20261108-001B` are built from these needs, so they agree. The
original ring at x sits at x·2^k in the final torus, and the ring graph of the torus gives the distance. ∎

## Remarks

- **The grown plane is useful once it stops.** While it doubles every lag no ring hears another (`GROW-HORIZON-20261109-001`); once it
  stops it is, for every reading of its rings, the fixed torus, with its original rings spread 2^k ring steps apart per original step.
  Distance across the grown plane is read after growth, never during it, in every schedule read (`CROSS-BORDER-20261110-001`).
- **Hearing spoils the stop.** Where rings heard each other before the stop, the stopped network's needs are not the fixed torus's: the
  history's mixtures stay in the cells, and the stopped plane is a different reader.
- **Its plain reading.** The final torus has both sides at least 6, so its plain first need is late (`GROWN-DISTANCE-20261109-001A`,
  Theorem 3): distance is read through freezes.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | The theorem at the cell level: k = 1, 2, 3 from 3 × 3 and k = 2 from 3 × 4 at g = 2, k = 1, 2 at g = 3; every contact and original ring, 60 lags after the stop | pass: 0 of 21,456 pairs differ |
| 2 | The same with one contact frozen from the stop on, three cases | pass: 0 of 7,776 pairs differ |
| 3 | Computed: slower schedules, two doublings then a stop | P = 3 at g = 2: none differ; P = 2, 4 at g = 2 and 3: most differ |

## Nonclaims

- **Doubling at every lag** (or any schedule that isolates its rings at the stop); open births (A44); declared rings (A45).
- **The readings after the stop**, not during growth.
