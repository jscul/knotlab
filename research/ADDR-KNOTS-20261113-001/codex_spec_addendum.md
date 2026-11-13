# Codex specification addendum: the summary's units (ADDR-KNOTS-20261113-001A)

Written 2026-11-13 18:05 UTC by the thread, answering the eleven ambiguities in `codex/REPORT.md` after the first hand-off. The
full run (`codex/full/`, systemd unit ak-run) was launched unchanged at 18:00 UTC; no registered result had been read. The thread
had seen the 300-key smoke only (fates F0 123, F2 37, F3 140; one return). These answers change no computation of the run, only how
`summarize` groups its records.

You are computing, not designing. The rules of `codex_spec.md` hold. In addition: **do not modify `addr.py`, `run_census.py` or
anything under `codex/full/`** (the run is using them). Write a new `codex/summarize_v2.py` (copy `summarize.py` and change it), test
it on the smoke outputs only, and append a section "Addendum" to `codex/REPORT.md`. Do not run it on `codex/full/`.

## Answers

1. **E's bits.** As you did: null for E, with the components retained. E is unweighted.
2. **V-sat.** "All 2ⁿ assignments" was a slip for every assignment of the instance's 2ⁿ variables, as you did.
3. **Unit for anything split by class.** The unit is the pair (pattern hash, relative class). A pattern produced by descriptions of
   several relative classes counts once in each of those classes. Unsplit counts (overall fate shares by count) use the pattern
   hash alone.
4. **Cluster.** A unit's automaton class is that of its first description in sorted key order among the descriptions forming the
   unit.
5. **Settled.** A unit is settled when any description forming it is `single_placement` or `first_letter_settled` (each implies the
   pattern lives at every level). s = 1 descriptions have no knot and form F0 units only.
6. **Conditioning on s.** A unit's s is the least s among the descriptions forming it.
7. **Letter class (secondary).** That of the unit's first description in sorted key order.
8. **Verdicts across descriptions of one pattern.** They are the same instance. At each level, any decided verdict among the
   descriptions is the pattern's verdict; recompute the fate from the merged verdicts. Two decided verdicts that disagree are a bug:
   list them and stop.
9. **P1.** Applies to descriptions with a knot; F0 descriptions are excluded and counted (s = 1 included).
10. **W secondary.** Units as in 3, each weighted by the summed weight of the W draws forming it (draw frequency; rejected draws
    excluded). Eligibility counts units (at least 30 decided, at least 5 automaton classes, under 10% FU by count); death shares are
    by weight; the bootstrap resamples W draws within each arm (2,000, seed 20261115), as the spec says.
11. **Logistic.** Write two design matrices, FU as dead and FU as alive; the fit stays skipped without statsmodels.
