# While it doubles every lag, no ring hears another

Status: Proved by hand (the theorem). The finite claims are checked exactly in `check.py`; checks 2 and 3 are computations, not theorems.

Ticket `GROW-HORIZON-20261109-001A`, 2026-11-09. Pre-registered in `research/GROW-HORIZON-20261109-001/preregistration.md`.

## Standard statement

- **The doubling network.** A running network of rule-60 rings with law (12, 12) contacts, every corner holding an own cell, grown by the
  doubling law of `GROW-ALL-20261109-001`: at a doubling lag a band goes in at every cut, both ways, with the fresh split, so every ring
  keeps its own cells, every contact is cut and both halves are born, and the new rings are born. Doubling happens every P lags.
- **Hearing.** Ring Y **hears** ring X at a lag when one of Y's own cells depends on X's own first-row cells; a contact **needs** X when
  its value depends on them. Positions are in the original lattice's units, an original ring at an integer point, a ring born between
  two at the midpoint; the **reach** of X is the largest taxicab distance, on the original torus, from X to a contact that needs it.

**Theorem (doubling every lag isolates the rings).** With doubling at every lag, at every lag every own cell of a ring depends only on
that ring's own born cells and on cells born at contacts, and every contact depends only on the own cells of the rings it lies on. So no
ring ever hears another, a contact needs only the rings it lies on, and the reach of an original ring never exceeds half the current
spacing.

**Computed (doubling every P ≥ 2 lags).** From the 3 × 3 and 5 × 5 tubes at g = 2, doubling every P lags to at most 96 × 96 rings, the
reach of an original ring, read at every lag, stays below 51/64, 3/4, 93/64, 113/64 and 155/64 original spacings for P = 2, 3, 4, 6 and 8
(within 5/64 on the 5 × 5 tube, read one doubling fewer), and no original ring hears it for P = 2, 3 and 4; for P = 6 the four at distance 1 do, for P = 8
the eight at distances 1 and 2. Just before each doubling the reach grows by amounts that halve at each doubling (P = 4: 1/4, 7/8, 19/16,
43/32; P = 8: 1/4, 11/8, 31/16, 71/32), as a horizon would: the reach stops growing in the original units while the rings inside it
multiply: the contacts needing the ring grow four- to tenfold per doubling, approaching fourfold.

**Control.** Without growth the reach of ring (0, 0) covers the farthest contact of the 3 × 3 and 5 × 5 tori within 40 lags (5/2 and
9/2); on the 4 × 4 torus it stops at 5/2, as even square tori leave rings unreached (`LATTICE-NET-20261108-001A`).

## Nearest known result

- **Causal structure of expanding lattices.** Horizons in discrete models of uniform expansion, where the signal speed is fixed per step
  and the lattice is refined faster than signals cross it; the light cones of additive automata (Martin, Odlyzko and Wolfram 1984).
- **Classification.** Known-with-delta. The causal argument is elementary; the delta is that the program's own growth law, chosen by the
  dynamics, has this structure, and that at every-lag doubling it isolates every ring.

## Proof of the theorem

At law (12, 12) a contact reads only the left neighbour on each of its two rings, an own cell since every corner holds one; an own cell
reads itself and its left neighbour, an own cell or a contact. Consider a doubling lag t. Every contact holds, after the doubling, a
newborn value; during the step to t + 1 each own cell reads an own cell of its ring or one of these newborn values, and each contact reads
own cells of its two rings. At lag t + 1 the doubling cuts every contact again and gives both halves newborn values, so the values the
contacts computed at t + 1, the only cells that carried one ring's cells toward another, are never read. By induction on the lag, an own
cell's value depends on its ring's own born cells and on newborn contact values only, and a contact's value at the lag after its birth on
the own cells of its two rings. A contact lies at half the current spacing from each ring it touches. ∎

## Remarks

- **What the doubling law's "plane" is while it grows.** At every-lag doubling it is a plane of declared rings (A45) none of which hears
  another: the network reads no distance at all until growth stops. Slower doubling lets influence cross contacts between doublings, and
  then every ring is heard only inside a horizon set by P.
- **The horizon follows from the counts.** Influence crosses about one ring in 2g lags, so between doublings it advances a fixed number of
  rings; each doubling halves the spacing, so the advances in the original units halve too, and the reach converges.
- **Parity.** The reach read at single lags rises and falls with the parity filter of the plain first need (`DISTANCE-20261108-001B`,
  Theorem 4), which is why P = 3 reaches less than P = 2.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash, the pre-registration among them | pass |
| 1 | The theorem: doubling at every lag from 3 × 3, 4 × 4, 3 × 4 at g = 2 and 3 × 3 at g = 3, to 96 × 96 rings or fewer: no own cell hears another ring and every contact depends only on the rings it lies on, at every doubling lag and the lag after | pass |
| 2 | Computed: doubling every P lags, P = 2, 3, 4, 6, 8, from 3 × 3 and 5 × 5: the reach, read at every lag, and the original rings that ever hear ring (0, 0) | pass |
| 3 | Control: the static 3 × 3, 4 × 4 and 5 × 5 tori | pass |

## Nonclaims

- **The horizon is computed**, to four doublings from 3 × 3 and three from 5 × 5; that the reach stays bounded at every later lag is not
  proved.
- **Plain dependence, not freezing**: the reach is the plain first need's; the freeze lengths on a growing network are not read.
- **Square tubes at g = 2** for the horizon; two-time knots (A30); declared rings (A45).
