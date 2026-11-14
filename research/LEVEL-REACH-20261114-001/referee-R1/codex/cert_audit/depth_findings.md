# Fresh depth extension

The baseline finished **128 distinct queries on sixteen descriptions** at
N=10,11 and s=1,2,3,4. All **119 exact numeric results equal their N9 values**;
nine chained queries ended at projection deadlines. No completed baseline
query found a smaller or larger least-bond size.

| Stratum | Queries | Exact, unchanged | Undecided |
| --- | --- | --- | --- |
| Chained, twelve descriptions | 96 | 87 | 9 |
| Direct3, two descriptions | 16 | 16 | 0 |
| Slow `[3,3,4,4]`, two descriptions | 16 | 16 | 0 |
| Total | 128 | 119 | 9 |

The chained sample has six descriptions with and six without cycles in its
N9 incidence representation, each with N9 elimination width at most eight.
The other strata are separate controls from the frozen sample plan. This is
a purposive referee panel, not a prevalence estimate. Five chained
descriptions and all four controls have complete unchanged baseline profiles
at both deeper cutoffs. The incomplete chained profiles retain their
timeouts explicitly.

**Lead's merged result:** the lead reports that five separate retries of the
forest deadlines all returned exact reach six. Merging those parent-owned
retries gives **124 exact unchanged cells out of 128**, with complete
unchanged profiles at both deeper cutoffs for ten chained descriptions, two
direct3 controls and two slow controls. Four cyclic queries remain
unresolved: `67fdb8d7` at s=4 and both cutoffs, and `db28d1ad` at N=11 and
s=3,4. The retries are in `../depth_retries.jsonl`; this lane did not rerun or
independently recheck them. `parent_merge_note.json` records this authority
boundary. `depth_summary.json` and `depth_results.jsonl` retain the original
baseline without overwriting failures.

All baseline rows bind one unchanged version of the parent-owned fresh
builder and search, with hashes matching the versions reviewed here:

- `fresh_pattern.py`: `4afdb51de764d8cd7b3248c166661775cb8a069ba8235cf4e9e789d77a638497`
- `fresh_search.py`: `7e1e36a6fb73540a9b786415d4b5647bed0a8fe64a4aff8bdb686a9a110b8e62`
- `sample_plan.json`: `442664f5148d89fe6bb4cfa0f55b5f57945d92d1b345e501a248d9dcbc2289c8`
- Baseline output: `5c4d2c570f6c25f263de9470556b18f5cf0b69a367f5af0c206a0e1ce2134886`

Review controls passed 61,568 complete actual dual-rail selector assignments
on fifty tiny formulas, 712 independent brute-relation/search comparisons
across sixty formulas, 128 builder comparisons, and rejection of flipped
output and gate-literal mutations. See `search_review.md` and
`search_review_controls.json` for the argument, hashes and exact controls.

Runs used one compute process, a 3 GiB address-space cap, width limit eight,
cap ten and 45 seconds per compilation/query. Each invocation covered at
most three descriptions and finished below twenty minutes. Baseline query
time totaled 1,003.19 seconds; peak recorded RSS was 136.8 MiB. No source
change occurred while any baseline row was being recorded. Additional s=1,2
queries were appended only after the original s=3,4 panel completed, using
the same descriptions, builder, compiler and search; no cell was repeated.

The exact baseline results are independent finite SAT-based recomputation,
conditional on the SAT solver's answers. This depth lane does not export new
LRAT proofs for every refutation or exhausted master query. Timeout cells
establish neither persistence nor change, and no conclusion beyond the two
tested deeper cutoffs follows. The separate retained-certificate audit in
`findings.md` checks displayed bond certificates, rather than the search's
exhaustion mechanism.
