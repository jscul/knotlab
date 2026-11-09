# The flip rule on the snub and elongated tilings and their duals: interpretation

Experiment `FLIP-RULE-20261109-001A-E001` (exploratory), run once on 2026-11-09 under the frozen contract (pre-registered in 65843d9d4),
in 1.5 s on 16 workers. Exact readings as in `PLANE-PLAIN-20261109-001A-E001`. Every row is in `result.json`.

## Primary observable

| Tiling | Tori read | Contacts that persist |
| --- | --- | --- |
| snub square 3.3.4.3.4 and its dual, the Cairo pentagonal tiling | 104 each | 1,870 of 9,350: one in five, the snub's contacts across the base edges |
| snub hexagonal 3.3.3.3.6 and its dual, the floret pentagonal tiling | 93 each | 2,574 of 12,870: one in five, likewise |
| elongated triangular 3.3.3.4.4 and its dual, the prismatic pentagonal tiling | 115 each | 3,036 of 5,060: the contacts of the square rows and along the rows |

- **H1 holds on every torus read:** a contact persists exactly when it has a flip.
- **H2 holds:** no torus of these six tilings keeps every contact persistent.

## Reading against the decision rule

Both hold. With `PLANE-PLAIN-20261109-001A-E001` the flip rule and the obstruction now cover all 11 Archimedean tilings and their 11 Laves
duals: only the square, triangular and honeycomb tilings keep every contact persistent. Ticket B searches small maps for persistence
without a flip.

## Nonclaims

- **Exploratory and finite:** the roster only; equally spaced rings; two-time knots only (A30).
