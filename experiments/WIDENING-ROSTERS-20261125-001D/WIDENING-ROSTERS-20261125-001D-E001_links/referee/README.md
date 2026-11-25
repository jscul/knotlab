# Independent check of further-reaching meetings

`referee.py` grows each frozen case with the unchanged B round mechanics and
an independently written selector for the four registered rules. Every offer is
read from the same structure at the start of its round. A take is further
reaching when its chosen distinction is offered within two holder steps and is
absent from the one-step offers. The output keeps both offer sets for each
actual take. The guard discards an incomplete round and the knot bound retains
the first completed round that crosses it.

The meeting reader recovers the live and demand rosters from holder incidences
and reconstructs the groups using the earlier local-round implementation. It
recomputes which split parts are wholly apart, how every later knot descends
from those parts, and the first actual group, demand group, or take that links
each pair. Within a meeting it records the actual pure endpoints of each
witness, the arms, and the shared distinctions. For a cross take it keeps the
newborn and the previous holder, as well as which side took the distinction.
It records mixed witnesses and events with no pure pair. A witness may be
an ancestor of one endpoint, both endpoints, or neither.

`project.py` keeps the exact eight-state table on each literal triple. It
computes parity with elimination followed by expressions in the free
distinctions. Under not-all-equal it first constructs possible satisfying
extensions in parallel. Only assignments left unaccounted for go to an
incremental SAT solver. Complementation certifies the opposite assignment
under the same law. Every source of allowed states acts on the whole stage.
Bars contribute to the roster metadata and impose no Boolean value. The
pre-meeting projection keeps the two side distinctions when both already exist.

`collect.py` checks the exact row count for the Cartesian product of the two
exclusive place lists and the shared candidates. It verifies each distinct
table with the canonical knotlab CLI and retains its three binary shadows.
The full table, the two-informative-arm factorization, the one-arm
factorization, and the K1–K3 knot verdict each have their specified meaning in
the frozen contract. Native recurrence and its persistence require their own
evidence.

Use the existing workspace virtual environment from the repository root. The
shared-runner job is `referee.py`. Its timing-only mode takes `--param assay=1`.
The evidence run uses the same cases with that parameter omitted. The retained
rehearsal and summary record the process and case caps. To assemble checked
artifacts from an evidence run:

```sh
.venv/bin/python -B "$REFEREE/collect.py" "$RUN_DIR" "$OUTPUT_DIR"
```

The retained outputs are one case receipt per configuration, compressed
streams of first meetings and actual takes, the compressed exact MOST literal
rows, canonical receipts for their distinct tables, and a summary by rule,
knot law and archive source. Each MOST case receipt hashes that case's compact,
sorted literal rows with their newlines included. Alternate rules have exact
meeting and take counts. The literal projection requirement applies to MOST.
