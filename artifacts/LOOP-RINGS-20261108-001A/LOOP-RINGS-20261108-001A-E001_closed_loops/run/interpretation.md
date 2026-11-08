# A census of closed loops of rings: interpretation

Experiment `LOOP-RINGS-20261108-001A-E001` (exploratory), run 2026-11-08 under the frozen contract: 295,056 loops in 1.4 s on 16
workers. Every verdict is exact by row sequences, and none was undecided. Totals are in `result.json`, and the persistent loops in
`loops.json`.

## Control

The contract's control, rechecking persistent loops on their full state spaces, was not built into `run.py`. It was run right after the
census in `research/LOOP-RINGS-20261108-001/characterise.py`, and it passes: all 31 persistent loops at size 4 agree.

## Primary observable

| Loops | Count |
| --- | --- |
| In the family | 295,056 |
| Every contact persistent | 2,707 (1,312 of three rings, 1,395 of four) |
| Not persistent | 292,349 |

- **H1 holds.** Closed loops of rings exist in which influence returns to its source and every contact still binds both of its rings
  at every lag. The smallest has three rings of four cells, each contact two cells from the next and reading its left neighbour on
  both of its rings.
- **How they work.** In the persistent loops each contact reads the chains that arrive from both of its neighbouring contacts, one
  on each ring. Under rule 60 every ring then carries a circuit through its two contacts.
- **How the rest fail.** A contact misses one of its rings at some lag; the commonest first misses are at lags 3, 6 and 10.

## Reading against the decision rule

H1 holds, so the next step is to verify, characterise and prove. The characterisation, in
`research/LOOP-RINGS-20261108-001/characterise.json`:
- **Across sizes.** 54 families of four-ring loops persist at every size from 4 to 16. All 54 mix the contacts' positions, half the
  rings with cell 2 and half with cell s − 2. No three-ring family persists at every size.
- **Round the loop.** In 2,659 of the 2,707 persistent loops, every contact needs the rings it does not touch at some lag of its
  cycle, and never at every lag.

## Nonclaims

- **These loops only:** rule 60 rings, the declared laws and sizes.
- **Two-time knots only** (A30); composition is read under A37.
