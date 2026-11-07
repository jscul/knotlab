# Closure of the logical-axis epic

Status: Proved

Ticket `LOGIC-AXIS-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new
  claim.
- **The decision note** is `research/LOGIC-AXIS-20261107-001/logic_axis.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A subshift that splits at range D (finite sets more than D apart are independent) has only D-chained minimal constraints, so the least minimal constraint through two coordinates grows at least linearly with their separation. Group shifts whose finitely supported points are dense split. | known overlap (strong irreducibility; Lind–Schmidt); proved | A |
| 2 | On Tseitin systems of Z^D and the cycle space of Z^2, this bond distance is comparable to graph distance (2d+1 to 2d+7 on the plane), so its balls grow like r^D. | elementary; proved | A |
| 3 | On the chain of Horn clauses w(t−1) ∧ L(t) → w(t), the bond distance between w_s and w_t is exactly t − s + 1. | new as far as found; proved | A |
| 4 | Group shifts over F_2 with one coordinate per site are full or have no finitely supported points. | classical; proved | A |
| 5 | A law can have every coordinate flipped by finite changes and still have minimal constraints joining points arbitrarily far apart (Ledrappier plus a free field); the per-variable source-aware reading does not give a ruler. | program-specific; proved; correction request filed | A |
| 6 | Conservative extensions never increase bond distance. | elementary; proved | A |
| 7 | In Ledrappier's shift, the three-point minimal relations are exactly the Frobenius triangles, and along each lattice line the least minimal relation through points n apart has at most 2 + w(n) points (w the non-adjacent-form weight), 3 exactly at powers of two. | known overlap (Ledrappier; Masser); delta new as far as found; proved | B |
| 8 | Conjecture: equality, 2 + w(n), and 2 + \|v\|_D in the plane. | conjecture; checked in windows | B |
| 9 | Parity substitution towers with nothing drawn: gadgets adding no open ends keep the old knot (bond distance 2 at every level). Gadgets adding open ends stretch by fixed factors (3^k + 1; 3·4^(k−1) + 1), with dimension estimates 1.26, 1.63 and 1.29. | exploratory experiment | C |
| 10 | A hub-free substitution keeps the replaced constraint exactly when its gadget adds no open end, and then is conservative; on tree-shaped knot graphs, bond distance = path knots + 1. | folklore-level mathematics; reading new; proved | D |

## Answer

- **When logic measures its own axis.** Logic measures its own axis faithfully exactly when nothing is
  opened by infinity: the thread counts loops, and lattice laws without ends read their dimension off
  their allowed states.
- **A frozen law.** It measures by signed binary digits, and its bond balls are infinite.
- **Growth.**
  - Growth that keeps old allowed states never stretches.
  - Refinement stretches only through open ends, with a dimension fixed by the chosen gadget.

## Pending the owner

- **New.** Whether a native knot must also be natively bound (`canonical_correction_request.md`).
- **Carried from earlier epics.**
  - Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Counted length as a native magnitude.

## Recommendation

**Continue** (2/3), as a fresh epic: growth at open ends.
- **The rule.** A uniform rule acts only where the relation shows an open end, with no chosen gadget
  shape.
- **The measurement.** The growth exponent of bond balls.
- **Alternatives.** The signed-binary lower bound (1/3) and the logical Cartesian product of two
  threads (1/3).

The table is in the decision note.
