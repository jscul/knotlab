# Proved true rates with side branches: pre-registration

Epic `TRUE-RATE-20261113-001` (`TRUE-BOND-20261113-001` direction 1; G17, with G1), 2026-11-13, at the coordinator's go-ahead. Frozen
before the code is written. Code by Codex from `codex_spec.md`; the run launched by the thread. The canonical K1–K3 test is
unchanged.

## The question

Side branches shorten the law's least bond in at least 62 of the 226 families whose ray bond grows, yet it still grows wherever it
was read deep enough. Can a true growth rate be proved, for every family whose computation closes?

## What is to be proved, and the general lemma

- **The general lemma is false as stated** (the advisor's, reasoned): "a side subtree can be replaced by its three ports at cost at
  most 3" fails because a side subtree can realise a three-port relation (such as equality) that no three own members express; and
  "every level needs a member" fails because arguments passed through let a level transmit at no cost. No per-level constant is
  claimed in general.
- **What is proved instead, per family.** The least-cost table of side summaries is a least fixed point over a finite universe
  (Knuth 1977), so, once computed without a cap, the step from one ray copy to the next is the same at every depth. On the trimmed
  graph of ray summaries (n nodes), every walk of length s is cycles plus a simple path, so L(s) ≥ λ_true (s − n + 1), with λ_true the
  minimum cycle mean (Karp 1978): the liminf of L(s)/s. Weights are integers, so λ_true > 0 iff the trimmed graph has no zero-weight
  cycle, and then λ_true ≥ 1/n.
- **Settled.** λ_true ≤ λ_ray; λ_true is rational with denominator at most n; the gate is a code check (the earlier cap lost nothing
  at any s).
- **What would refute growth:** a family whose trimmed graph has a zero-weight cycle while its ray bond grows — side branches making
  the true bond bounded along a progression of depths. That would itself be the result.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate: L(s) from the graph equals TRUE-BOND's exact values at every reached depth. | any mismatch |
| P1 | **The tables close.** At least half of the 226 families have a closed table and a complete graph. | below half |
| P2 | **Growth survives.** No complete family has a zero-weight trimmed cycle (λ_true > 0 in all). | any zero cycle |
| P3 | **Side branches lower the rate only in the deficit-growing families.** In the 4 whose deficit grows to 3 by depth 7, λ_ray − λ_true = 1/2; in at least 80% of the other complete families λ_true = λ_ray. | otherwise |
| — | Reported: λ_true's distribution, closed and complete counts, upper bounds where not closed, acyclic families. | — |

The advisor model reviewed the plan cold (`advisor_review_answer.md`): Plan A sound under three conditions (written into the spec),
the lemma false as stated, the reduction of growth to a zero-cycle test, and the predictions P2 and P3.

## Prior work

Least fixed points of superior functions (Knuth 1977); minimum cycle means (Karp 1978); min-plus eventual periodicity (Cohen,
Dubois, Quadrat and Viot). Not found: proved true growth rates of least bonds in nested NAE patterns.

## Hand-off and stop rule

Codex: code and validation only (one memory-capped unit). The thread: the run on the 226 at three workers and 16 GB (another job
shares the machine), check, interpretation, commit, a hand-off to the referee thread, report.
