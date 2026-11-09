# Closure of knots read from the last growth event

Status: Proved

Ticket `REBASE-KNOTS-20261109-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/REBASE-KNOTS-20261109-001/rebase_knots.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Every cell of a rule-60 network with law (12, 12) contacts is read by exactly two cells, so every row after the first has even parity and is not open. | known-with-delta; proved | A (lemma) |
| 2 | Read as if the insertion row were open, every contact persists: the stage reading. | known-with-delta; proved | A (theorem) |
| 3 | Read natively from any later row of a tube that never grows, every contact fails to bind each of its rings at some lag. | new as far as found; computed | A (check 3), stress test |

## Answer

Knots cannot be read from the last growth event natively: the breakage under growth while running is not a reading artefact.

## Recommendation

**Research directions**; growth chosen by the dynamics (B23) continues as ordered. The table is in the decision note.
