# Does growth survive side branches? Pre-registration

Epic `TRUE-BOND-20261113-001` (`PROVED-RATE-20261113-001` direction 1; G17, with G1), 2026-11-13, at the coordinator's go-ahead.
Frozen before the code is written. Codex writes and validates the code from the frozen spec (`codex_spec.md`); the thread launches
the long run as its own job. The canonical K1–K3 test is unchanged.

## The question

Along one ray of copies the least bond provably grows linearly in 226 one-definition limit-only families. Bonds through side
branches were not allowed. Allowing them, does the law's reach from the top to depth s still grow?

## In standard terms

The least size of a minimal non-shattered set containing a root vertex and a vertex of the depth-s copy, over all vertices of an
infinite iterated hyperedge-replacement NAE instance, against the same restricted to one derivation ray.

## Settled by construction (stated, not tested)

- **L(s) ≤ L_ray(s)** (a ray bond is a bond), so the true rate is at most the ray rate.
- **No level skipping.** A side subtree meets the ray only at its three ports, in one ray copy; with no side member at a level, the
  transition is the ray DP's. Side members near the top or bottom can still change the boundary, so a bounded true bond is not
  excluded by construction.
- **The method is exact** (the advisor's check): non-fullness is monotone, so single deletions suffice; children's assignments are
  independent, so sets of masks suffice; the cost cap L_ray(s) − 2 is sound. The agreement with brute force at the same truncation is
  a code check, not a finding.
- **No rate is claimed.** The cost cap depends on s, so a minimum cycle mean over the capped table would not be sound; the study
  reads L(s) for s ≤ 12 and the deficit D(s) = L_ray(s) − L(s).

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate: the four validations of the spec pass (brute force by bond counts per size, a shortening case if one exists, the F-for-G mutant disagrees, the ray check). | any fails |
| P1 | **Side branches rarely shorten the reach.** L(s) < L_ray(s) for some s ≤ 12 in at most 20% of the 226. | more than 20% |
| P2 | **Where they do, by a boundary amount.** In those families the deficit does not grow: D(12) − D(6) ≤ 1 in at least 80%. | below 80% |
| P3 | **Growth survives within depth 12.** L(12) > L(6) in at least 90% of the 226. | below 90% |
| — | Reported: the deficits, the generic tables' sizes, families not reached. | — |

The advisor model reviewed the draft cold (`advisor_review_answer.md`): it confirmed the method's exactness, showed the Karp step
unsound with an s-dependent cap (dropped), gave the pruning rules, the validation design (bond counts by size, a shortening case, a
mutant) and the discriminating predictions P1 and P2.

## Prior work

Bonds as minimal non-shattered sets (Sauer–Shelah; Pajor); ∃∀ dynamic programming on bounded treewidth (Chen; Pan and Vardi); least
fixed points of superior functions (Knuth 1977). Not found: whether side branches shorten the law's reach in nested NAE patterns.

## Hand-off and stop rule

One spec to Codex (code and validation only; one memory-capped unit; writes only in `codex/`; never commits); the thread then runs
`run_true.py` on the 226 as its own background job (workers set from Codex's memory estimate), checks, interprets, commits, hands off
to the referee thread and reports.
