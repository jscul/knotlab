# Closure of the planar-theorem epic

Status: Proved

Ticket `PLANAR-THEOREM-20261102-001Z`, 2026-11-02.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/PLANAR-THEOREM-20261102-001/planar_theorem.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On a plane knot space minus a line, line–face matchings carry integer potentials, one per matching. They form an L-natural convex set, and their parities are the values relative to the hub. | new; classical heights and convexity | A, §1 |
| 2 | The staircase at a gluing line: the non-odd difference takes neighbouring values on and off each state, and a hub-tied port puts its state in the middle of a chain. | new | A, §2 |
| 3 | The access lemma is a theorem (rounded midpoints). Hence every pinned three-point knot through the hub is generated on a plane near side, for any far side. | new | A, §3 |
| 4 | A crossing knot that one port separates is a 2-sum through that port, or is tie-equivalent to a one-sided circuit, on any splice (33,556 checked). | new; matroid 2-sum analogue | B |
| 5 | Re-centring the potentials at any point gives the access lemma for every pinning. So every crossing knot pinned by two near points and separated by one far point is generated on a plane near side, for any far side (167,704 plane pinnings; 3,438 knots). | new | C, §§1–3 |
| 6 | On the Fano plane and census 58, no pinning by two non-port points has access (1,536). Split at a point, no two points pin, while plane spaces split at a point give every pinning access (552). | new; finite | C, §5 |
| 7 | One-sided knots and near-pinned three-point knots generate all 58,875 crossing knots on the splices. All 564 new knots are hub-pinned three-point knots on non-planar near sides. The 12,102 residual knots have no proof. | new; finite | C, §4 |
| 8 | Scout: in 16-point spaces with one handle, access is decided by the gluing line's position. In the plane part: 6,056 of 6,056 pinnings have it. In the Fano part: 11,376 of 12,368 do not. | new; finite; not a claim | decision note |
| 9 | Correction: PLANAR-COMPOSE's plane pinning total of 8020 is 9020. | correction | A; decision note |
| 10 | Open: the reduction of the residual knots, four-pattern removals, and the locality of access. | open | C |

## Pending the owner

- **Still open.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): handles seen from a gluing line.
- **First.** Prove that access at a gluing line depends only on a planar neighbourhood of that line.
- **Then.** Test whether creation localizes at gluing lines on handles, on spaces with one and two Fano atoms.
- **Alternatives.** Finish the reduction lemma (1/3). Selection as a dimer model (2/3).

The table is in the decision note.
