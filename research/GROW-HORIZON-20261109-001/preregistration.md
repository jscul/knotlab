# Pre-registration: distance and balls in the doubling network

Epic `GROW-HORIZON-20261109-001` (backlog B49), written on 2026-11-09 before any reading of the doubling network's reach, at the
coordinator's request.

## The network

The running square tube of equally spaced rule-60 rings with law (12, 12) contacts (g = 2), grown by the doubling law of
`GROW-ALL-20261109-001`: at a doubling lag a band goes in at every cut, both ways, with the fresh split, so every ring keeps its own cells,
every contact is cut and both halves are born, and every ring gains three new neighbours. Doubling happens every P lags, P = 1, 2, 3, 4,
6 and 8, from the 3 × 3 and 4 × 4 tubes; the static tubes are the control. Each ring has a position in the original lattice's units
(an original ring at an integer point, a ring born between two at the midpoint), and the reach of an original ring X by lag T is the
largest taxicab distance, on the original torus, from X to a contact whose value at T depends on X's own first-row cells.

## Expectations, frozen

- **E1 (doubling every lag).** No cell ever depends on another ring's first row through a contact: a contact born at a doubling holds its
  two rings' cells one lag later and is cut and reborn before any cell reads it. So a contact needs only the rings it touches, no ring
  hears another, and the reach of every original ring stays at the distance of its own contacts (1/2) at every lag. Expected to be
  proved, and checked.
- **E2 (every P ≥ 2 lags).** Influence crosses contacts between doublings, about one ring per 2g = 4 lags, while the rings between two
  original rings double every P lags, so the reach stops growing: a horizon whose radius grows with P and stays of the order of P/g
  original spacings. Expected to be computed.
- **E3 (control).** Without growth the reach covers the whole torus within its diameter's time of flight.

## What would count against them

A cell that depends on another ring's first row under doubling every lag (against E1); a reach that keeps growing to the size limit for
some P ≥ 2, or does not grow with P (against E2); a static tube whose reach stops short (against E3, which `LATTICE-NET-20261108-001`
and `DISTANCE-20261108-001` would then contradict).
