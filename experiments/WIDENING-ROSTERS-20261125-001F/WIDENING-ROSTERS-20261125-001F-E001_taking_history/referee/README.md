# Independent recount of first meetings under history-based takes

The run uses the frozen case order, both knot laws, seven attempted rounds,
and the 1500-knot bound. It calls the established B growth engine and reuses
the earlier referee's eligibility reader and first-meeting reader. The only
growth intervention is the taking rule. For the two rules based on earlier
extra takes, the selector reads a completed snapshot. A made holder must
have taken a distinction as an extra if the holder did not make it and none
of its parents holds it. A separate ledger of completed takes verifies that
reading. The other history rules read the maker and the maker's round. The
comparison with the most-held selector is calculated after a round completes.

The event digest uses compact JSON with sorted key names and one newline per
event, in separation round, meeting round and split membership order. An event
is strict when every linking knot was made after the start and every linking
distinction is free of start holders. The direct two-step-only take count uses
the actual taker and pre-round holder. The narrower count requires these to
descend exclusively from opposing sides with respect to this pair. A take
elsewhere in the same growth certifies only that a two-step-only take occurred.

The replay compares each new rule to each of the four preceding rules on the
same start, ration, treatment and knot law. It retains the observed results
and also compares the rounds that completed under both members of the pair.
For strict meetings, the stable split and meeting keys use the start IDs,
each birth's round, kind, parents and offshoot index, and distinction makers
and ordinals. The more detailed key includes the supports of the included
knots, meeting types, linking knots and distinctions, mixed witnesses and
pure meeting routes. The older ring sweep also preserves explicit IDs for
the sides at separation. The compact link archive preserves their sizes
and meeting rounds. Matching only those fields can leave several candidate
pairs for a row.

Use the repository virtual environment and shared runner. The retained
`timing.json` records the exact timing-only assay, source hashes, and
configuration used before the evidence run. Its assay emits times and sizes.
The evidence run's `job.json` and `state.json` bind the completed invocation.
From the repository root, set `F_REFEREE` to this directory and `F_OUTPUT` to
a fresh output directory. Rebuild the post-run tables from the sealed run as
follows.

```sh
.venv/bin/python -B "$F_REFEREE/summarize.py" "$F_RUN" "$F_OUTPUT"
```

`F_RUN` is the retained `referee/run` directory for this experiment. The
summary reports exact totals with the observed stops. `paired.jsonl.gz`
contains one record per new trajectory with all four comparisons.
`physical_matches.jsonl.gz` contains each strict meeting and its alignment
with the most-held control.
