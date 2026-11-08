# Composition at recurring lags across sizes (E001): interpretation

Experiment `RECUR-PATH-20261108-001A-E001` (exploratory), run 2026-11-08 under the frozen contract as the long-running unit
`recur-path-a1` (RECUR-PATH-A1 in `docs/LONG_RUNNING.md`), 226 s on 16 workers.

## Control

It fails. The every-lag reading should reproduce `PATH-GROWTH-20261108-001A`'s counts at the full levels (0, 0 and 8) and gives 200,
144 and 140. The cause is a bug in that reading: it checked the lags from the light cone to the end of the last contact's first cycle,
a range that is empty when the cycle ends before the light cone, so it counted every such persistent path as composing at every lag.
The ten small paths checked on their full state spaces agree, and they test only the recurring readings.

## What stands

The two recurring readings do not use the faulty check, so their counts stand. They were recomputed in
`RECUR-PATH-20261108-001A-E002`, which fixes the every-lag check and changes nothing else; its control passes and its recurring
counts are these.

## Nonclaims

- **Superseded by E002** for every count; kept as the record of the failed control.
