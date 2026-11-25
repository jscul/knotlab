# Independent full-record check

The input is the frozen physical request list and its content-addressed stage
supports. A request keeps the exclusive places of each of two holders and one
shared distinction `c`. All other physical places are existentially removed.
An additional shared place is one hidden variable wherever it occurs. Bars
impose no values.

The checker protects the two holder rows and queues places with exactly one
remaining holder. It removes a row only when its queued place occurs nowhere
else in the remaining rows. Such a place falls outside the retained records
because the two holders stay present. Restore removed rows in reverse order
and choose each removed row's place to satisfy it. This proves preservation of
the projection. The implementation uses the incidence queue, which is
independent of birth order.

For parity, the checker eliminates hidden columns from the remaining rows.
Visible row relations determine the ranks for the two records, their separate
projections with `c`, and their joint projection. The ranks decide the product
and both proper attachments. For not-all-equal, reducing to the two holders
gives the closed-form relation from the full-record certificate. The fallback
first asks for a fixed hidden assignment satisfying every outside row for all
visible records. Its exact SAT fallback identifies private variables with the
same remaining row incidence. Each such group contributes only zeros, only
ones, or both to those rows, so its allowed record classes determine the exact
product and attachment tests. The actual panel reduces to the two holders
throughout.

The receipt bits are the conditional product, proper attachment on the first
arm, and proper attachment on the second arm in that order. Coherence, openness
of `c`, private widths, extra shared places, method and occurrence weights are
retained independently. `verify_population.py` regrows the independent earlier
stages and matches the frozen physical-key multiplicities exactly. The same
weights recover the earlier literal occurrence counts.

Use the workspace virtual environment from the repository root. The shared
runner job is `driver.py`. Pass `--param assay=1` for timing only. Omit it to
retain the actual classifications. The rehearsal covers the entire panel and
records the resource caps. After the shared-runner job finishes, run:

```sh
.venv/bin/python -B "$REFEREE/collect.py" "$RUN_DIR" "$OUTPUT_DIR"
```

The collector retains `records.jsonl.gz` in frozen request order and verifies
its raw row count and SHA-256 by reading it back. `summary.json` has the exact
weighted and unique counts and a source occurrence for each outcome.
Once both runs are complete, `compare.py PRIMARY_RESULTS INDEPENDENT_RESULTS
COMPARISON` checks the physical keys, outcome bits and occurrence weights. The
comparison digest uses those fields alone, in key order.
