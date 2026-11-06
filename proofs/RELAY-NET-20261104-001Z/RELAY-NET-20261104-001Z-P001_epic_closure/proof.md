# Closure of the relay-network epic

Status: Proved

Ticket `RELAY-NET-20261104-001Z`, 2026-11-04.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/RELAY-NET-20261104-001/relay_net.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | After a frozen hop a relay is an arc signal: two ports fixed and disagreeing, the third free. | new | A, §1 |
| 2 | Arc lemma: an arc signal freezes exactly the lines with a corner on its arc. Sufficiency is proved; the converse is computed on generic pieces. | new | A, §1 |
| 3 | Repeaters: a station passes the signal on exactly when its out-line lies on the arc. Aligned chains keep the same live pins at every cut. | new; finite | A, §2 |
| 4 | Depth: aligned chains reach the final grid four cuts away, misaligned ones stop within two. At separated cuts, creation needs a live signal at every cut. | new; finite | A, §3 |
| 5 | Broadcast: hubs copy a relay into several receivers. | new; finite | B, §1 |
| 6 | Direction: no creation upstream of the handle's piece in any network tested. | new; finite | B, §2 |
| 7 | Bypasses: stations with adjacent cut vertices pass relays without loss. | new; finite | B, §3 |
| 8 | Exact: a broadcast, a three-cut chain and a two-cut relay, on small networks. | exact | B, §4 |

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): a native reading of genus.
- **The question.** Whether the creation map over all removals splits into one halo per Fano atom, so that it counts and locates a space's
  handles.
- **Alternatives.**
  - The display rule (1/3).
  - The claim rule's converse (2/3).

The table is in the decision note.
