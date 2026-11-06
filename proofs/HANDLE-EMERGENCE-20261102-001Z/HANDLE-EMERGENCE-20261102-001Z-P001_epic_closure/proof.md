# Closure of the handle-emergence epic

Status: Proved

Ticket `HANDLE-EMERGENCE-20261102-001Z`, 2026-11-02.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/HANDLE-EMERGENCE-20261102-001/handle_emergence.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Planar removed sides create no new knot at an opened cut: 24 planar knot spaces beyond the census and the planar census, 2172 removals. Non-planar sides create 936 knots at 100 of 208 census removals, and no four-pattern interface creates. | new; finite | A |
| 2 | Every created knot has three points: the removed line's hub, a near point and a far point. The first two pin all three ports, and the third separates them. Necessary, not sufficient. In the Fano plane the hub sits on the port it pins as odd. | new; finite, with elementary lemmas | B |
| 3 | Odd-point model: solutions up to complement correspond to choices of one incidence per line with prescribed parities on every cycle. | elementary; new as stated | C, item 1 |
| 4 | Skip model: on a plane knot space with Kasteleyn signs the knot fails by counting faces (n + 2 against n lines). After a removal the solutions are the perfect matchings of the other lines to the faces off the removed line. Every failing signing of the planar census spaces is Kasteleyn. | new as stated; close to Kasteleyn and Moret | C, item 2 |
| 5 | A line meeting the removed line shares a face with it and has at most four port patterns on a plane space. | new | C, item 3 |
| 6 | Genus g removes 2g faces and adds 2g homology parities. On the Fano plane's torus embeddings, 14 face-odd assignments per removal leave 5 solutions. | new as stated | C, item 4 |
| 7 | Open: a proof that planar removed sides never create. | open | C, item 5 |

## Pending the owner

- **Still open.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): planar glue only composes.
- **The proof.** Prove planar non-creation from the skip model. The first discriminator is a single-port lemma for plane line–face
  matchings.
- **Then.** Test whether a handle's created knots are exactly what its homology parities add.

The table is in the decision note.
