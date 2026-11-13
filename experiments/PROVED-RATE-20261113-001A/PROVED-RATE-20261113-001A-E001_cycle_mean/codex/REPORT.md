# Ray-bond DP calculation

Execution is in progress. All authored files and outputs are confined to this
`codex/` directory. The supplied specification is the computation contract;
no ticket, lifecycle, navigation, source-input, or Git changes are made.

The inputs contain 664 distinct family indices matching
`BD.families_one_def()`. Eleven unfinished input records have an empty `L`.

The implementation exposes the requested start, middle, and closing maps,
uses the original BD tables, and evaluates the same `advance` set images
with memoized finite maps. Nodes retain the original pair-of-frozensets type.
The complete run will use seven family workers and one parent process,
single-thread numerical libraries, a 2,000,000-node breadth-first cap, and
a 1,200-second wall-computation limit per family.

Validation: compare compiled maps with the literal copied `advance`; compare
refactored layers against BD on small real families; check Karp against an
independent small-graph cycle enumerator; check every available stored L(s).

## Ambiguities

- How should “constant over the last 8 computed depths” apply to an input
  with fewer than 8 computed depths? There are 135 nonempty such records.
  No class will be chosen for a record when its class depends on this answer;
  its graph calculations and gate still run.
- In a capped reachable graph, an empty-W trajectory can leave the retained
  nodes, so the specified eventual cycle cannot necessarily be followed.
  If no fully known qualifying cycle is found and a trajectory is missing,
  the affected `bounded_all` result will be left null rather than completing
  an unspecified trajectory. A known qualifying witness still gives true.

## Timings and deviations

Final timings, exact commands, validation, and any affected omissions will be
recorded when computation finishes. There is no interpretation of results.
