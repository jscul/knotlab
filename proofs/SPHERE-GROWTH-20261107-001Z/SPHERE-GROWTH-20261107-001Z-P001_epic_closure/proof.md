# Closure of round spheres from one hidden bit

Status: Proved

Ticket `SPHERE-GROWTH-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/SPHERE-GROWTH-20261107-001/sphere_growth.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Every closed sphere of the two-kind law has six digons, and with the local Kasteleyn sign rule its knot contradicts itself. | proved (Euler and the count identity) | A |
| 2 | A law of radius r without hidden states that allows K_m (m ≥ 2r + 1) allows every capped tube T(m, L, τ), whose contradiction resolution refutes in width O(m) at every length. | known-with-delta (local views); proved | A |
| 3 | The seam law (one hidden bit per incidence, two rules at co-lines) has exactly the octahedral knot spheres K_m as its spheres, each with one marking, so all its contradictions need width Θ(√n) and size 2^Θ(√n). | new as far as found; proved | A |
| 4 | A growth law without branching grows at most one closed surface. | proved | A |
| 5 | Random local growth closed 60 spheres in 711 tries; the only round ones were octahedra. | computed | A |

## Answer

A local law places the six digons itself only with hidden information. Without hidden states it cannot tell a round sphere from a long
tube, whose contradiction is easy. With one hidden bit per incidence its spheres are exactly the round knot spheres, so it lays out its
own sphere and the hard contradiction at every size.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue**, as a fresh epic awaiting the owner's go-ahead: grow K_m by a local process, ring by ring from a digon with the seams as
signals. Rated Payoff 2/3 (Substantial), Concreteness 2/3 (Testable). The table is in the decision note.
