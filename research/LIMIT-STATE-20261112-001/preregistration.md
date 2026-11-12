# What a living state of the bottomless pattern looks like: pre-registration

Epic `LIMIT-STATE-20261112-001` (`LIMIT-ONLY-20261112-001` direction 2; G17, with G7), 2026-11-12, at the owner's go-ahead ("iterate
on it for a bit") and the coordinator's steer. Frozen before the registered run. The canonical K1–K3 test is unchanged. The law is
NAE on three-place knots; the families are `LIMIT-ONLY-20261112-001`'s, drawn by SHORT-DESC's code (A71, A79).

## The question

The genuine families of `LIMIT-ONLY-20261112-001` (after its referee) die at every finite depth from some depth T on, with knots
at the bottom, while their usual limit lives. Every living state of the limit must set the three ends of some self-holding call all
equal at each dead depth. First: does the limit live only because everything comes loose? Then: must those all-equal ends spread
over many calls as depth grows, or can one call per depth carry them, and can those calls lie on one ray, each inside the one before
(a regular, self-similar arrangement)?

## In standard terms

For satisfiable infinite iterated hyperedge-replacement NAE instances whose capped finite members are unsatisfiable: in their
satisfying assignments, the sets of replaced hyperedges that are monochromatic at each depth; whether a singleton per depth, and a
singleton chain along the derivation tree, is achievable.

## Settled by definition or known (stated, not tested)

- **The usual limit** keeps knots present at all but finitely many depths: a self-holding definition with a SELF call on its own
  three ends keeps the knot on its ends, which is added (LIMIT-ONLY-R1). It lives iff the main relation is non-empty at the greatest
  fixed point G (compactness). The finite part to depth D with G on its bottom SELF calls has exactly the restrictions of the
  limit's living states (fixed-point property).
- **The restriction lemma** (LIMIT-ONLY-R1): at each dead depth t, every living state sets the ends of some call of depth t (a SELF
  call made from a copy at level t − 1) all equal. A **code check** (gate), not a result. So the interior is never unconstrained:
  "loose" (every self-holding definition's limit relation and the main relation free) tests only that the bottom imposes nothing,
  and is reported, not predicted (the census's 94% free relations nearly settle it).
- With one call per depth (chains), one witness per depth on one ray holds by the lemma: chains are reported apart.
- Per-call marginals (can be, must be all equal) are eventually periodic along call paths by construction, so they are not used.

## Design (frozen in `census.py`)

Families: the 1,341 records of `LIMIT-ONLY-20261112-001` alive only in the bottomless pattern; genuine ones kept (validation:
894, the referee's count). Excluded: the recurrent family and patterns over 60,000 knots. For depths T, T+1, T+2 of the finite part
to depth T+3 with G at the bottom, two exact SAT queries: **single**, a living state with exactly one call of all-equal ends at each
depth; **single ray**, moreover each made inside the copy of the one before. Gate: imposing not-all-equal on every call of a dead
depth leaves no state.

## Predictions (frozen)

The advisor model reviewed a draft cold (`advisor_review_answer.md`): it showed the draft's per-call marginals periodic by
construction, its loose test settled, its regularity test a one-step property, and proposed the joint queries (single witness,
single ray). Adopted.

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate: the lemma's check passes at every dead depth read, and every finite part read is alive; the genuine count is 894. | any |
| P1 | **One witness per depth suffices.** In at least 80% of branching genuine families (two or more calls at some depth read), some living state has exactly one all-equal call at each of depths T to T+2. | below 80% |
| P2 | **And it can be a single ray.** In at least half of branching genuine families, those single witnesses can lie on one ray. | below half |
| — | Reported: the loose share, chains, loose against non-loose branching families, calls per depth. | — |

## Prior work

Compactness; Knaster–Tarski; satisfiability on tree-structured (bounded-width) instances by message passing; hyperedge-replacement
grammars (Courcelle; Habel, Kreowski and Vogler). Not found: the arrangement of the all-equal state in limit-only NAE patterns.

## Plumbing (disclosed)

A plumbing run on 1/40 of the families (scratch output) printed only counts and timing. No outcome was looked at.

## Stop rule and runtime

One run on 16 workers (about a minute), its summary, a hand-off to the referee thread, report.
