# Persistence as the rings grow: interpretation

Experiment `SHARED-CONTACT-20261108-001C-E001` (exploratory), run 2026-11-08 under the frozen contract: 8,448 configurations in
214 s on 16 workers. The largest rings, 8 + 9 cells, have 65,536 joint states. A decided verdict is exact at every lag: maps were
told apart by digests, and each repeat was confirmed by recomputing the earlier map. The longest repeat came at lag 4,020. Rows are
in `rows.json`, totals in `result.json`.

## Controls

Both pass.
- **Earlier censuses.** The configurations shared with `PROCESS-CONTACT-20261108-001B` and `SHARED-CONTACT-20261108-001B` get the
  same classes.
- **Lag 1.** Every self-blind configuration binds at lag 1, as ticket A's Theorem 2 says.

## Primary observable

The fraction of configurations that bind both rings at every lag, with both rings on one rule (88 classes). Proposals use the two
parity combiners. Self-blind contacts use u(a_{m−1}, a_1) + u(b_{n−1}, b_1) with the same nonconstant u on both sides, 14 laws.

| Rings | Proposals | Self-blind | Proposals without 51 and 204 | Self-blind without 51 and 204 | Undecided (proposals, self-blind) |
| --- | --- | --- | --- | --- | --- |
| 3 + 4 | 1.1% (1 rule) | 3.6% (6 rules) | 1.2% | 1.3% | 0, 0 |
| 4 + 5 | 2.3% (2) | 5.7% (14) | 2.3% | 3.5% | 0, 2 |
| 5 + 6 | 7.4% (9) | 11.9% (28) | 7.6% | 9.8% | 0, 8 |
| 6 + 7 | 11.9% (17) | 20.1% (38) | 12.2% | 18.3% | 5, 10 |
| 7 + 8 | 19.3% (24) | 24.4% (46) | 19.8% | 22.6% | 5, 34 |
| 8 + 9 | 20.5% (28) | 26.0% (49) | 20.9% | 24.3% | 5, 62 |

- **Persistence grows with the rings in both families.** From 3 + 4 to 8 + 9 the proposal parities go from 1.1% to 20.5% and the
  self-blind parities from 3.6% to 26.0%. The growth slows between 7 + 8 and 8 + 9.
- **Rings that never read the contact do not drive it.** Without rules 51 and 204 the curves keep their shape.
- **The proposal family's ceiling.** Its 23 rule classes canalizing at their centre never bind at lag 1, so at most 130 of its 176
  configurations can persist. Of the 130 that can, 36 persist at 8 + 9, which is 28%.
- **Which self-blind laws.** At 8 + 9, u = XOR and u = XNOR persist for 36 of the 88 rules each.
- **Persistent at every size.** Self-blind contacts on rules 12, 51, 60, 140, 200 and 204 persist at all six sizes. No rule does so
  under a proposal parity.
- **Undecided.** The undecided counts grow with size, to 62 of 1,232 self-blind configurations at 8 + 9. If all of them were
  persistent, the fraction there would be 31%.

## Reading against the decision rule

- **H1.** It asked for a rising fraction in each family, reaching at least 0.25 at 8 + 9. It holds for the self-blind family (0.260)
  and fails narrowly for the proposals (0.205), although both rise about as predicted.
- **The rarity is largely a small-ring effect.** `PROCESS-CONTACT-20261108-001B` found persistence rare at sizes to 5 + 6. On rings
  of 8 and 9 cells a fifth to a quarter of parity contacts shared by identity bind both rings at every lag. Shared identity and
  persistence are compatible.
- **Removing the self-read adds a few points.** The self-blind family is ahead at every size, by 2 to 8 points.
- **Saturation is open.** Whether the fraction keeps rising, or levels near a quarter, is not settled by these sizes.

## Nonclaims

- **Sizes to 8 + 9 only.** Both rings alike.
- **Undecided configurations are counted apart.**
- **Two-time knots only** (A30).
