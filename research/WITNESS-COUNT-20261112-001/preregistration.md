# How many all-equal knots each dead depth needs: pre-registration

Epic `WITNESS-COUNT-20261112-001` (`LIMIT-STATE-20261112-001` direction 1; G17, with G7), 2026-11-12, at the coordinator's go-ahead.
Frozen before the registered run. The canonical K1–K3 test is unchanged. Families, words and the usual limit as in
`LIMIT-STATE-20261112-001` (A71, A79).

## The question

Every living state of the usual limit has, at each dead depth t, a **witness**: a call of depth t with its three ends all equal.
What is the least number w_t a living state needs, how does it grow with depth (a fixed share of the calls, so that the all-equal
state is itself a pattern inside the pattern; a constant; or between), can one state attain the least counts at every depth, and do
the witnesses at depth t+1 sit inside those at depth t or hop to other branches?

## In standard terms

For satisfiable infinite iterated hyperedge-replacement NAE instances whose capped finite members are unsatisfiable: the least
number of monochromatic replaced hyperedges at each derivation depth over satisfying assignments, against lower bounds from disjoint
unsatisfiable sub-derivations.

## Settled by construction (stated, not tested)

- **One witness per disjoint dead copy (proved).** A copy made by a call at depth s of definition i is dead on its own at depth t
  when i's relation at depth t − s is empty; the lemma applied to it needs a witness among its own depth-t calls, and disjoint copies
  cannot share. So w_t ≥ A_t, the number of disjoint dead copies.
- **Each dead copy needs its own least count (proved; the advisor's).** The limit's state restricted to a copy is a living state of
  that copy's limit, so in one-definition families (the definition holds itself and is the main one) w_t ≥ B_t, the sum over
  disjoint dead copies of w at their own depth; with regular branching b this gives w_{T+k} ≥ b^k w_T.
- **Consequences.** "Two or more witnesses at some depth", `LIMIT-STATE-20261112-001`'s headline, already follows wherever A ≥ 2
  (reported here as a correction to that record, with exact counts). The growth law is settled by the bound as a share at least
  b^−T of the calls, so it is reported, not predicted. When relations shrink with depth, every depth-t witness contains a depth-t+1
  witness; only the converse share (depth-t+1 witnesses inside depth-t ones) is informative.

## Design (frozen in `census.py`)

Genuine families, depths T, T+1, T+2 of the part to depth T+3 with the limit relation at its bottom; N_t calls, A_t, B_t (one-
definition families), w_t exact by SAT with an incremental totalizer (binary search from the bound; a state below the bound is a
**bound violation**, a gate); one SAT call for a state attaining all three least counts; in it the share of depth-t+1 witnesses made
inside a depth-t witness's copy. Caps: 60,000 knots, 20,000 calls per depth; the recurrent family is left out.

## Predictions (frozen)

The advisor model reviewed a draft cold (`advisor_review_answer.md`): it gave the sharper bound, showed the draft's P1 (w = A) refuted
at depth T+1 by it and its growth-law test settled, and proposed multiplicativity and simultaneity as the tests. Adopted.

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate: no bound violation. | any |
| P1 | **Copies are independent.** In at least 90% of one-definition families read, w_t = B_t at depths T+1 and T+2. | below 90% |
| P2 | **One state attains every least count together.** In at least 90% of the families read. | below 90% |
| — | Reported: w_T, the excess w/B, the growth law, the converse nesting share, multi-definition families (A against w), the families where one witness per depth suffices (described). | — |

## Plumbing (disclosed)

Plumbing runs on 1/80 and 1/160 of the families (scratch output) printed only counts, timing and the gate count. No outcome was
looked at.

## Stop rule and runtime

One run on 16 workers (about ten minutes; registered in `docs/LONG_RUNNING.md`), its summary, a hand-off to the referee thread,
report.

## Amendment (before any outcome was looked at)

2026-11-12, about 22:25 UTC. The first registered run (16 workers, 8 GB each) was killed for memory after 202 families: the
cardinality counter was built up to the number of calls at a depth (up to 20,000). The counter is now built only up to a bound grown
by doubling until some living state lies within it, which changes memory, not answers. Nothing in the 202 records was looked at; all
families are rerun with the amended code (12 workers, 10 GB each). The thread missed the failure for about an hour because its
waiting loop counted failed units as running.
