# Round nine of the start with 28,065 growing junctions

How many junctions does round nine of EXPLOSIVE start-03 make?

Retain exact counts of every deterministic component found. Use unbiased random descent through an exhaustive branching decomposition or a probability sample of disjoint summands, calibrated on round seven to eight where applicable. Means use independent replicates; report their dispersion, precision, checks for heavy tails and whether uncertainty is design-based, empirical or rigorous. A proved multiplicative bracket on the count can replace sampling uncertainty if a decomposition makes that possible. State all adaptive changes. Include the actual start and one-stage weighting only.

**Decision.** Estimate round nine with a reported spread under a factor of ten, or exhibit a reason the spread cannot shrink with the chosen observations.

## Prior work in the program

`python3 -B scripts/track.py objects "start-03 28065 sampling round nine" --until 2026-11-19 --exclude NINTH-ROUND-SAMPLE-20261119-001 --limit 3`

`python3 -B scripts/track.py objects "random descent enumeration maximal cliques growth" --until 2026-11-19 --exclude NINTH-ROUND-SAMPLE-20261119-001 --limit 3`

`python3 -B scripts/track.py objects "maximal blocks stage eight 993164 parent" --until 2026-11-19 --exclude NINTH-ROUND-SAMPLE-20261119-001 --limit 3`

WALL-READ constructs the round-eight stage, proves 16,019 for its next round and finds uniformly sampled small induced parts give weak lower bounds. It suggests random descent; the study must handle duplicate joins and nonuniform importance.

Other retrieved records, included with their scope given by the objects index, are `FRESH-COUNT-20261118-001`, `MERGE-BURST-20261119-001`, `REDUCE-BLOCKS-20261119-001`, `SCALE-THEOREM-20261119-001`, `SEQUENTIAL-WALL-20261116-001`, `WALL-READ-20261119-001`.
