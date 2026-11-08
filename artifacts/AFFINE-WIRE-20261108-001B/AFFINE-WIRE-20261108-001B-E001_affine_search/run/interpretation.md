# Searching affine chains for persistent composition: interpretation

Experiment `AFFINE-WIRE-20261108-001B-E001` (exploratory), run 2026-11-08 under the frozen contract: 9,216,000 chains in 258 s on
16 workers. Every verdict is exact by ticket A's reduction. The chains in which both contacts persist are in `positives.json`
(45,406 rows), and the totals are in `result.json`.

## Control

It passes. The twelve smallest persistently composing chains give the same verdicts on their full state spaces.

A verification added after the run (`research/AFFINE-WIRE-20261108-001/verify_transport.py`) does the same for the twelve smallest
chains with the contacts at least two cells apart, and all agree.

## Primary observable

| Chains | Count |
| --- | --- |
| In the family | 9,216,000 |
| c1 persists (binds rings A and B at every lag) | 346,508 |
| Both contacts persist | 45,406 |
| c2 binds the end rings at every lag from d + 1 on | 60,508 |
| Both contacts persist and the chain composes | 2,376 |
| … and c1 also binds the end rings from d + 1 on | 380 |

- **H1 fails.** Gaps are not forced: 2,376 affine chains pass the contact-network gate's composition across time with both
  contacts persistent.
- **Adjacent contacts.** 1,946 of them have their contacts adjacent on the middle ring (d = 1), so c2 reads c1 directly. In 1,416
  the middle ring runs rule 204 and does not move at all.
- **The middle ring carries (430).** With the contacts two or three cells apart, the middle ring carries c1's past across its own
  cells.
  - **Middle rings.** Rule 150 (266 chains), 60 and 102 (60 each), 90 (28), and the shifts 170 and 240 (8 each).
  - **End rings.** Mostly 90 and 150.
  - **Both contacts compose** in 186 of them.
- **The smallest such chain.** Rule 150 on all three rings, 3/5/3 cells, contacts two apart. c1 reads one neighbour of ring A and
  both of its ring-B neighbours; c2 reads both of its ring-B neighbours and one neighbour of ring C. From lag 3 = d + 1 on, c2
  always holds the parity of one cell of A, three of B, one of C, and both contacts' own first values. The generic enumerator finds
  exactly that one knot through c2(T) at every lag, and `knotlab check` confirms the parity relation on that support is a knot
  (`canonical.json`).
- **What the laws share.** In 152 of the 430, each contact reads both of its middle-ring neighbours.
- **Contacts read one-sidedly.** In 208 of the 430, each contact reads only one of its two end-ring neighbours (u = x or u = y).

## Reading against the decision rule

- **The stop condition is not met.** The coordinator's condition was that arrival sets of affine chains always have gaps. They do
  not. So the process line does not close with forced gaps. It now has persistent native networks across time on affine
  substrates.
- **Why the earlier chains failed.** `PROCESS-CHAIN-20261108-001B` used one rule for all three rings and one law for both contacts.
  Here most persistently composing chains mix laws, a contact often reading its end ring on one side and the middle ring on both
  sides, and many mix rules, one for the middle ring and another for the ends. Rule 150 everywhere, with mixed laws, already
  composes.

## Nonclaims

- **The declared family only.** Linear rules, ring sizes to 5, 7 and 5, contact laws by their linear parts. The stress test
  checks one size past.
- **Two-time knots only** (A30).
- **No claim about nonlinear chains.** They are covered by `PROCESS-CHAIN-20261108-001B` and `INTERMITTENT-NET-20261108-001B`.
