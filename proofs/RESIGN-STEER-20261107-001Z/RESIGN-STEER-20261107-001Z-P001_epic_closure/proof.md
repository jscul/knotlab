# Closure of steering by re-signing

Status: Proved

Ticket `RESIGN-STEER-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/RESIGN-STEER-20261107-001/resign_steer.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In every state and law of a Kasteleyn knot sphere, violated lines minus over-agreement plus half the number of even faces is 1; with four or more even faces every state over-agrees. | known-with-delta; proved | A |
| 2 | On every simplicial knot sphere every law with exactly two even faces is satisfiable, wherever they sit; so one sign change at the violated line moves the dissonance into the law, and every line is the violated line of a flat state. | known-with-delta; proved | A |
| 3 | Every line is the violated line of exactly 2 N(T) flat states, N(T)² = det(B Bᵀ) / (n0 n1 + n1 n2 + n2 n0); differently coloured even faces allow at least N(T) matchings. | no overlap found; proved | A |
| 4 | With the state fixed, sign changes made only at the dissonance carry it from any line to any line through configurations holding only the forced unit; a closed walk equals a block change of state. | known-with-delta; proved | A |
| 5 | A rule that sees only one even face's lines and the distance to the target, never stepping straight back, reached 2,399 of 2,400 targets on K_2–K_8 and K_10 within 40 m steps (300 of 300 on K_12 in the stress test). | computed (exploratory) | B |
| 6 | The count of consistent states is least when the two even faces touch, where theorem 3 makes it N(T), and grows with their separation like a power near 1/2: fitted slopes 0.46 on K_12, 0.49 on K_16 and 0.51 on K_20, as for two unit holes in lozenge tilings. From every source the maximum sits at a corner, and corners carry more states than other faces at the same distance. | computed (exploratory) | B |
| 7 | Moving one even face at a time to the neighbour with the most consistent states, all 144 runs on K_3–K_8, and six more on K_9 and K_10, stopped with both even faces on corners; 33 of the 144 reached the best pair, antipodal corners. | computed (exploratory) | B |

## Answer

Yes, on every count asked. One sign change at the forced dissonance always moves it out of the states and into the law, as two even faces that can sit anywhere, and the law with nothing learned puts the dissonance on every line equally often. Sign changes made only where dissonance is seen carry it to any line while the state holds still. On the sphere that is everything learning adds to behaviour, since a closed learning walk is a change of state. A rule that sees only one even face's lines and a target signal does it in practice. Left to keep the most states consistent, the two halves repel each other like equal charges and settle on the sphere's corners.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue, awaiting the owner's go-ahead:** learning in handles (backlog B6 of the goals doc): off the sphere a learning walk
around a handle changes the sign class, which no change of state does. The decision note gives the two tables.
