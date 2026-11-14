# Independent certificate audit

- Scope: `LEVEL-REACH-20261114-001`; writes belong only to this directory.
- Question: do sampled retained bond certificates prove nonfullness and full
  projections on every maximal proper subset for the pattern rebuilt from the
  frozen address-map specification?
- Branch: code analysis; referee validation of an existing frozen study.
- Inputs: the permitted gzip result records, retained gzip CNF/LRAT pairs,
  design/specification text, and the earlier independent referee's
  `fresh_patterns.py` action routines and `check_rup.py` RUP checker, read only.
- Forbidden inputs: every Python or C source under the study's experiment
  directory, and the study's `summarize.py`.
- Mapping: rebuild term images from words and MSB-first automaton actions;
  form deduplicated NAE triples; compare CNF clause multisets; check every
  proof addition by hint-free unit propagation; directly evaluate recorded
  states and their projections.
- Sampling: deterministic hash selection, up to four numeric `(key,s)` cells
  in each of the chained, direct, other, and undecided profile strata, aiming
  to cover s=1..4 with distinct keys. All numeric bond claims nested in each
  selected cell are checked, including target-restricted and per-target
  claims. This purposive stratification is an audit, not a prevalence estimate.
- Outputs: selection, inventory, per-claim results with hashes and counts,
  controls, and a concise findings note.
- Controls: reject malformed LRAT, a mathematically wrong refutation of a
  satisfiable formula, a changed CNF clause, and a deliberately invalid state.
  Deliberate hint changes do not alter a hint-free proof check.
- Budget: one compute process, address-space cap 3 GiB, each invocation below
  20 minutes; no solver subprocess or network access.
- Stop: sampled claims checked, or an explicit resource/input obstruction.
- Nonclaims: a valid bond certificate establishes inclusion minimality of its
  displayed support. It does not establish globally least cardinality,
  exhaustion through size ten, a uniform theorem, or any claim beyond the
  finite pattern being checked.

## Assigned follow-up

The lead additionally assigned a read-only review of this task's fresh
`fresh_pattern.py` and `fresh_search.py`, truth-table controls using their
actual selectors, and a depth extension of the frozen `sample_plan.json`.
These new referee sources are permitted inputs; study Python/C remains
forbidden. Review outputs and depth outputs also belong only here.

The depth sample comprises all twelve chained descriptions (six with and six
without cycles in their N9 incidence representation), the first two direct3
descriptions, and the first two slow descriptions. It tests N=10,11 and s=3,4,
with cap ten, width limit eight and 45 seconds per compilation/query. Chained
descriptions were previously filtered by N9 elimination width at most eight;
the other strata were not. Invocations cover at most three descriptions so
each stays below the twenty-minute command ceiling. All source hashes are
bound to each output row. Timeout and width failures remain undecided, and no
performance tuning or automatic retry is authorized by this follow-up.

After the s=3,4 baseline finished, the lead assigned the same sixteen
descriptions at s=1,2 and both deeper cutoffs, to obtain complete four-value
profiles. This adds sixty-four cells without replacing or repeating the
original cells. The underlying construction and search modules stay fixed;
the wrapper gains only a span-selection argument.
