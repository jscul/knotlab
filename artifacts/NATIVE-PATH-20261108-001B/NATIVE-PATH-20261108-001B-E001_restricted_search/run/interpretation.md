# Restricted searches for native paths: interpretation

Experiment `NATIVE-PATH-20261108-001B-E001` (exploratory), run 2026-11-08 under the frozen contract: 996,840 paths of four rings and
three shared contacts in 565 s on 16 workers. Every verdict is exact by ticket A's reduction. The paths whose three contacts all
persist are in `paths.json`, and the totals are in `result.json`.

## Primary observable

| Family | Paths | All three contacts persist | Native (ends bound at the last contact from the light cone) |
| --- | --- | --- | --- |
| Rule 150 on all four rings, every law at each contact | 900,000 | 496 | 0 |
| The 430 carrying chains extended by one end ring | 96,840 | 266 | 0 |

- **H1 fails in both families.** No native path exists here. The control, verifying the smallest native paths, had nothing to
  verify.
- **No path binds its ends.** No path has its ends bound at both end contacts, and none has a last contact binding every ring.

## Why the persistent paths do not compose

The 762 paths with all three contacts persistent were replayed to their row cycles.
- **The first ring never reaches the last contact (578).** Its influence never reaches c3.
- **It reaches c3 at some cycle lags (184).** It does so at 30% to 70% of them, but not at all.
- **The middle contact.** It holds the first ring's influence at every cycle lag in 302 of the 762, at some lags in 220, and never in
  240. So the middle contact often carries the first ring persistently, and the loss happens on the way across the second middle
  ring.

## Reading against the decision rule

- **The absence is for these two families only.** Rule 150 everywhere, and the carriers extended with their old end rule as the
  second middle ring.
- **What the second middle ring lacks.** It does not carry c2's past to c3 without cancelling. A ring that carries without mixing,
  such as a shift, was not in either family as the second middle ring. The contract's follow-up is a broader search, which ticket C
  takes up with shifts as the second middle ring.

## Nonclaims

- **The two restricted families only.** No claim about other paths.
- **Two-time knots only** (A30).
