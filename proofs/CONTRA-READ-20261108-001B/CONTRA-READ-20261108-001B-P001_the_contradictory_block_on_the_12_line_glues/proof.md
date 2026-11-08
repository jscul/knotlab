# The contradictory class's block on the five 12-line glues

Status: Proved (exhaustive computation on five glues with exact pruning)

Ticket `CONTRA-READ-20261108-001B`, 2026-11-08.

## Question

- **Where it came from.** On the 8- and 10-line trisum glues every single row of creation between glue lines singles out the
  contradictory class (ticket A). Does its whole block stay its own one size past?
- **The test.** TRISUM-READ's five 12-line glues (seeds 1, 192, 240, 246 and 300): 12 lines, 12 points, cycle rank 13, 8,192
  switching classes each. Follow, line by line, only the classes whose row equals the contradictory class's, computing each row once
  per class of the glue without its line.

## Dependencies

- **`CONTRA-READ-20261108-001A`.** The method (`contra_lib.py`) and the result on the smaller glues.
- **`SWITCH-PROOF-20261108-001A`.** The theorem behind reading a row from the class on the glue without its line.
- **`TRISUM-READ-20261107-001A`.** The glues and the engine.

## Results

1. **One contradictory class (check 1).** On each of the five glues exactly one class has no solution, the class of the generator's
   Pfaffian signing.
2. **Its block is its own (check 2).** On each glue, no other class survives the pruning: no other class has the contradictory class's
   glue block.
3. **One row nearly does it (check 2).** After the first line only the four classes over the contradictory class's restriction to the
   glue without that line remain, so the first row already singles out that restriction; the second row picks the class among the four.

## Reading

- **Creation recognizes the contradiction one size past.** On all seven glues of 8 to 12 lines, the class that makes the space
  contradictory is told apart from every other class by creation between glue lines.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Classes without solutions on the five glues | one each, the Pfaffian class |
| 2 | Pruning by rows | only the contradictory class survives; four classes left after the first line on every glue |

## What this does not establish

- **Every row.** Only the first row is computed in full here. Whether each single row singles the class out on these glues, as on the
  smaller ones, is the epic's stress test.
- **Larger glues.** The 14- to 18-line glues are not computed.

## Novelty

- **New here.** The computation.
