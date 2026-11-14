# Conditional-product computation

This implements preregistration census check 3 only. The frozen
`research/READ-RULE-20261114-001/preregistration.md` and
`advisor_review_answer.md` were read before implementation. No new theorem,
proof, lifecycle, population, or CARRY verdict authority is introduced.

## Interface

`conditional_from_calls(calls, checkpoint=lambda: None, *, max_r=8,
max_stored_products=250000, max_levels=100000)` consumes dictionaries with
`relation` (an unsigned 64-bit integer) and `arguments` (the three SELF-call
arguments after the authorized inlining). A caller can combine CARRY's
recorded `R_i` with its `SyntaxPreparation.flat(S)` arguments, in SELF-call
order, without a new allowed-state computation. The caller must first check
that the lists have equal lengths and correspond to the same family and
SELF-call order.

`conditional(prep, calls=None, checkpoint=lambda: None, **limits)` is the
convenience interface; omitting `calls` uses authorized `relations.per_call`.
All relation operations are loaded through CARRY's `inputs.py`:
FREE-TARGET's `relations.compose` and `relations.rectangular` are reused.
Population, weights, scope, CARRY verdict, runner, source freeze, and file
output remain the parent's responsibility. This module writes no files.

## Exact state and test

Each stored product is `(Boolean relation, identity carry map)`. The carry
map is represented from end positions to start positions: entry `j` is the
start position `0`, `1`, or `2` still held by identity at end position `j`,
or `-1` when no start identity remains. The returned records also spell out
the equivalent start-to-end position lists. A repeated argument is retained;
one start position may occur at several end positions. No tie inferred from
allowed values becomes an identity.

For left followed by right, the Boolean product is exactly the authorized
`compose(left, right)`. The new map at an end position is the left map at
the parent position named by the right map, or `-1` if that identity has
already been lost. Products with equal Boolean tables and different maps
remain distinct. Products equal in both components can be merged because
the requested conditional test depends only on these two components. The
least lexicographic representative SELF-call word is retained for failures.

For every assignment of the distinct carried start positions, fix those
start positions and every corresponding end position to equal values.
Intersect the product with this assignment mask, then apply authorized
`rectangular`. Every assignment is tested, including after a failed one.
The fixed positions can remain in the 8-by-8 table because the extra rows
and columns are zero. The empty slice is rectangular, matching the
authorized predicate. With nothing carried, the single slice is the whole
product, so the test reduces to plain rectangularity.

Every complete length set is tested for `r = 1..8`; successful lengths do
not imply later successful lengths. If a complete set of relation/map pairs
repeats, its exact recurrence determines the remaining lengths, which are
marked `derived_from_r`. A repeated trace's failure word explicitly names
the earlier length at which that representative word was produced. This is
set recurrence, not a conditional-persistence assumption.

## Caps and unresolved cap convention

The numeric defaults and checks follow `relations.semigroup`: 250,000
cumulative stored product states, construction checked against stored plus
the next set, and 100,000 distinct stored length sets. The study horizon is
eight. Detection of an exact repeated set precedes charging another stored
length, just as in the authorized semigroup. The 250,000 operational bound
here counts the required **relation/map pairs**. Cumulative per-length
distinct Boolean-table counts are returned separately as
`stored_boolean_products` and `boolean_length_set_sizes`.

Exact question if this distinction affects a case: **Does the inherited
250,000-product cap count relation/map pairs, or only distinct Boolean
products when a product has several carry maps?** The frozen text does not
specify the new state accounting. A pair-cap hit is therefore returned as
`capped`, with no primary `r`, and that affected family is undecided rather
than evaluated under a silently increased cap. The partial construction
counts show whether the Boolean-only count would already have hit the cap.
The parent can report this question without changing the study.

A cap from the supplied cooperative checkpoint or a `MemoryError` likewise
returns `capped`, preserving the completed trace. This follows semigroup's
no-conclusion-on-cap rule even if a successful earlier length appears in
the partial trace; that fact is retained as `least_r_in_partial_trace`.
Malformed or unsupported call data raises `ValueError`, for the caller to
record and skip rather than reinterpret.

## Returned evidence and controls

The result returns `r`/`least_r`, the three verdicts
`conditionally_rectangular`, `none_through_8`, or `capped`, and per-length
counts of relation/map pairs, distinct Boolean products, maps, represented
words, passing products, slice tests, failed slices, and empty slices. The
first failing product, map, word, value assignment, and sliced table are
retained at each length. Actual distinct pair checks and composition
attempts are separate from counts reused after recurrence.

`controls()` and `--controls` offer seven hand-specified controls: a full
relation; identity carried everywhere; identity with no carry; two equal
relations with different carries; one start position carried to two end
positions; a relation whose first rectangular product has length two; and
a storage cap that must stay undecided. A separate map-composition check
tests a start identity that changes end position. These controls write only
to the invoking process's stdout when the CLI is used.

At a full 250,000-state bound, each distinct pair has at most eight slices
of an 8-by-8 table; product construction has one small Boolean composition
per unique generator and stored pair.

The parent granted one scheduled Python-process slot for controls and a
feasibility assay. One `.venv/bin/python -B` process parsed the implementation
with `ast.parse`, passed all seven controls, and consumed only the first 20
rows of `source_index.json`. Each row's recorded `R_i` was paired with the
authorized `SyntaxPreparation` argument lists after checking their lengths.
There was no new allowed-state computation. Complete horizon-2, horizon-4,
and horizon-8 computations on those same 20 families took respectively
0.003007, 0.007605, and 0.068893 seconds in total. Process peak RSS was
89,184 KiB. The slot was released immediately after that process ended.

Raw controls, the source-index digest, all 60 feasibility outputs, per-case
metrics, and the timing summary are retained in `conditional_controls.json`.
The horizon-8 mean extrapolates to approximately 20.5 seconds for 5,964
families for this computation alone. This is a feasibility estimate from
the first 20 input rows, excludes full-run I/O, and gives no guarantee about
the remaining cases' costs. No full-census computation was run by this
worker.
