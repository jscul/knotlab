# Closure of the strip-relay epic

Status: Proved

Ticket `STRIP-RELAY-20261103-001Z`, 2026-11-03.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/STRIP-RELAY-20261103-001/strip_relay.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Heights lemma: the port class fixes the ports' heights, so a port pattern freezes exactly the points whose height difference to the ports cannot vary. | new | A, §1 |
| 2 | Reduction lemma: across a 3-edge cut, an untouched side can be collapsed to the vertex it lost without changing the transfer or creation (253,536 pipeline cases, 1,080 exact). | new; uses the interface lemma | A, §2 |
| 3 | In the collapsed space the halo lies on the faces around the attachment point, which explains the FACE-CLAIM C junction. | new | A, §2 |
| 4 | Ring law: from the middle point of a pendant ring's removed line, the halo runs along the ring's whole far face, k − 3 lines for every ring length. | new; given the ladder law | B |
| 5 | Rigid strips relay: a handle in the strip or the far grid creates in the first grid near its cut, from every distance and at the same lines for every length. This is exact on small dumbbells. | new; finite | C, §§1, 4 |
| 6 | Liquid grid connectors screen relays within three steps; thick tubes relay part of the way. | new; finite | C, §2 |
| 7 | Orientation: relays enter only a side split at a point at that cut, and a handle leaves its grid only where the grid lost a line. | new; finite | C, §3 |

## Pending the owner

- **New.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`. The law of the faces around the point
  holds after collapsing untouched sides; D003's refutation applies to the uncollapsed space.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): relay networks.
- **The test.** Branch and chain rigid strips through small pieces and test whether one handle's halo reaches several grids.
- **The questions.** How relays from two handles combine where channels meet, and whether directed channels compose into native paths.
- **Alternatives.**
  - Proofs of the relay's length independence and of the composite-handle reading (1/3).
  - The converse of the claim rule (2/3).

The table is in the decision note.
