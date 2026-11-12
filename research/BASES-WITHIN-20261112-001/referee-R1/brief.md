# Referee job BASES-WITHIN-R1: the brief

Handed over by the coordinator on 2026-11-12 (08:03 UTC), epic `BASES-WITHIN-20261112-001` (B164), closed "referee pending" in commit
0e3853b51 (documents 26d4e2659). The thread's next step does not depend on the verdict. The referee rechecks without trusting the
thread's reasoning: the hand proofs are re-derived, the computations rebuilt with code written for this job, and nothing imports the
author's `nest_lib.py` or `check.py` (the author's result files are read only to compare).

## Setting

Not-all-equal (NAE) law. An inner harmony I is a one-shift base all of whose states repeat (A70), with state set W. O[I] makes each
distinction X_j of an outer base O a copy of I, and each outer knot (a, b, c) the knot NAE(x_(a,i+s), x_(b,i+t), x_(c,i+u)) at every
i: an unlagged stitch when s = t = u (the record's "stitch at one place"), else a lagged stitch with lags (s, t, u).

## Claims to check

- **Proved by hand:** L1 an unlagged stitch holds iff the pairwise disagreement counts sum to 2L; L2 harmonies of harmonies are
  harmonies; L3 only W = {0101..., 1010...} has a one-bit reading; L4 the mirror lift x_(j,i) = s_j xor w(i), so O[I] lives iff O lives
  and each column realises exactly O's states, at every level; L5 the alternation gives O[I] = O; L6 levels never end; L7 ties of
  levels are products of the seed's; L8 lags on outer patterns with no closed chain are absorbed; L9 for the alternation, lags are
  signs.
- **Computed, exact on frozen ranges:** E3 five seeds, levels 1 to 4; E4 the three-copy nesting, levels 0 to 7; E2 45 harmonies x 33
  outer patterns, unlagged and lagged (60 sampled lag assignments per pair, every assignment for the alternation); the exactly-one
  control.
- **Descriptive, after the run:** the E1 follow-up (level-2 counts of all 45 harmonies capped at 20,000; level 3 of 0011).

## The coordinator's questions

Whether L4 gives "lives iff O lives" at every level or only one direction; whether "Fano revived" makes the sampled/exhaustive split
plain; whether any lemma is true by definition and so says less than it sounds.
