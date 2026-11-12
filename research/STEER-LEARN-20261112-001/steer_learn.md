# A learner whose examples steer its search

Epic `STEER-LEARN-20261112-001` (sub-goal B165, G15 with G16; program learning), 2026-11-12, at the coordinator's go-ahead.
Pre-registered in [preregistration.md](preregistration.md), frozen in commit `a2cd50751` before any frozen run; the rules and the test were
drafted with the advisor model. Proof family: `proofs/STEER-LEARN-20261112-001A/`. **Refereed: Confirmed** with two wording fixes, both Not a block, made below
([referee report](../../proofs/STEER-LEARN-20261112-001A/STEER-LEARN-20261112-001A-P001_steering_rules/referee-R1/report.md), commit `b017137a9`).

## The answer

**No. None of three steering rules lets the examples steer the learner: none finds the count faster than blind search, with or without
charging its checks of stored states.**

- **The rules.** Persistence targeting (sign changes weighted toward knots the failing examples' end states violate), make and break
  (WalkSAT's break count, the examples as clauses), two-sided acceptance (keep correct stored states satisfied, break wrong ones). Each uses
  information blind search does not: the end states of the probe's own walks.
- **On one copy, resting at the 4 laws the faces allow:** blind search finds the count in a median of 6 probes. The unchanged learner takes
  19; persistence targeting 19; make and break 78 charged (21 world probes); two-sided acceptance 1,760 charged (19 world). None passes.
- **With 64 laws at rest:** blind median 22; every learner fails to find the count within its budget in half or more of its runs.
- **The swap target shows a bias, not steering.** On one copy every learner, including the unchanged one, finds the swap target g in about 6
  world probes, against a blind median of 11. The unchanged learner uses no examples to steer, so the learner's own walk favours g's law and
  disfavours the count's. Two causes are not separated: a preference of the dynamics among the laws it can rest at, and the fixed start
  (every run begins at the same law, and stops come within a few probes). The referee measured it: in the swap runs the walk met the
  count's laws in 15% to 19% of runs on one copy, where blind draws over as many probes would in 47% to 50%; with 64 laws at rest, 13% to
  26% against 71% to 82%.
- **Every candidate check was charged** (make and break, and two-sided acceptance), as the coordinator asked: candidate laws checked
  against stored states count as probes. Persistence targeting reweights its proposals with stored states uncharged, as frozen. Two-sided acceptance
  checked over a thousand candidates per run; even counting world probes alone, no rule beats the unchanged learner.

## What is known, and what is proved and computed

| Claim | Evidence class |
| --- | --- |
| Blind medians: the count 6 (F) and 22 (GE); g 11 and 45 | exact |
| No rule passes on the count in either setting; no steering shown | computed, frozen (1,600 runs) |
| The learner's walk finds g faster than blind search under every rule, the count more slowly | computed, frozen |
| The rules are WalkSAT's break count, clause weighting and contrastive acceptance, lifted to the law | known (Selman, Kautz and Cohen 1994; Morris 1993; Hutter, Tompkins and Hoos 2002; Ackley, Hinton and Sejnowski 1985; Hinton 2002) |

## Against the pre-registration

I predicted at least one rule would pass on the count in F. None did. B failed on the count as predicted. The unchanged learner passing on
g was not anticipated; it is read as a bias of the walk (B steers nothing).

## What it changes

- **Local steering at the probe does not make this learner learn.** The examples, read through the end states of its walks, carry too
  little about which sign to change, or the walk forgets the hint before the next probe.
- **The walk has preferences.** Which laws the learner's own dynamics favours decides which targets come fast. A learner whose dissonance
  itself depends on the examples, felt during the walk and not only at probes (the clamped phase of a Boltzmann machine), is the natural next
  test (B168); why the walk prefers some laws is a cheap exact question (B169).

## Assumptions

None added or changed. Relied on: A20, A21, A46, A47, A49, A50, A52, A58.

## Corrections

None.

## In the owner's words

Telling the learner which of its rules broke, and where, did not help it find the right rule any faster than drawing rules at random; the
tips cost more than they saved. What the learner finds quickly is what its own wandering already leans toward.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a learner whose examples steer (B165) | **Status:** Failed (refereed, Confirmed) | no rule beats blind search on the count; the only fast target is one the walk itself favours |
| Local direction: steering at the probe (break counts, weighting, contrastive acceptance) | Retire | slower than blind search with checks charged, no faster than the unchanged learner without |
| Broader exploration: learning program | Known alternatives | examples felt during the walk (B168), the walk's preferences (B169), symmetric laws (B166), two histories (B159) |
| Long-term goal: G15 Learning: a point in a learned knot pattern | Obstruction learned | learning from examples still not shown; the dynamics' own bias decides what comes fast |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Let the examples shape the dissonance the learner feels (B168) | 3/3 — Major | 2/3 — Testable | a clamped phase: while learning, the world holds one example at a time and the learner's sign moves feel the dissonance under that clamp (the Boltzmann machine's clamped phase, natively), frozen, on one copy against the blind median → the count found faster than blind search with the swap control, or not | Selected · awaiting go-ahead |
| 2 | Why the learner's walk prefers some laws (B169) | 2/3 — Substantial | 3/3 — Ready | exact visiting frequencies of the laws at rest under the unchanged walk on one copy, against uniform → the bias explained by the dynamics, or not | Alternative · deferred |
| 3 | Rest at the laws the base's symmetries fix (B166) | 2/3 — Substantial | 3/3 — Ready | as recorded | Alternative · deferred |
| 4 | Two histories (B159) | 2/3 — Substantial | 2/3 — Testable | as recorded | Alternative · deferred |

- **#1:** payoff 3/3, the clamped phase is how energy-based learners are taught in the literature, and it lets every example act during
  the walk, not only at its end; concreteness 2/3, one change to the walk, but the schedule of clamps must be frozen with care.
- **#2:** payoff 2/3, it explains which targets come fast; concreteness 3/3, an exact stationary computation on 4 laws.

**Corrections:** none.
**Goals:** G15 checkpoint (obstruction learned, with G16); sub-goal B165 taken; sub-goal B168 and backlog B169 added.
**Assumptions:** none new or changed.
**Basket:** B168 (selected, awaiting a go-ahead), B169, B166, B159, B162, B157, B154, B155, B156, B150, B151, B130.

## Final report as sent

Posted in the thread on 2026-11-12 (09:21 UTC). Its findings, word for word in substance: none of three steering rules (WalkSAT-style break counts, clause weighting, two-sided contrastive acceptance) finds the count faster than blind search over the laws at rest, every check charged (blind median 6; learners 19 to 1,760); counting world probes alone none beat the unchanged learner; with 64 laws at rest most runs did not find the count; every learner found the swap target faster than chance (about 6 against 11), a bias of the walk; the rules are known heuristics, that none steers this learner is new as far as found; the pipe fix in track.py and directions.py (0d64f88ad); referee handed to the referee thread, the next step not depending on it; the two tables as above; Corrections: none; Goals: G15 checkpoint, sub-goal B165 taken, sub-goal B168 and backlog B169 added; Assumptions: none; Basket: B168 (selected), B169, B166, B159, B162, B157, B154, B155, B156, B150, B151, B130. Holding for a go-ahead on B168.

## Referee (2026-11-12)

Confirmed by the referee thread with independent code (`referee-R1/`): claim 1 rebuilt from the frozen maps at rest; claim 2 from its own
tallies of all 1,600 runs (407 runs with 64 laws at rest dropped at the cap, counted as never), every median, share and mark matching; "no
rule steers" holds on world probes alone. Two wording fixes, both Not a block, made above and logged in `docs/CORRECTIONS.md`: the fixed start
named beside the walk's preference as a cause of the swap target's speed, with the referee's count-met numbers; "every check was charged"
narrowed to every candidate check. The referee's note for what follows: test the walk's bias from the fixed start and from random starts,
and use random starts in B168, so that start proximity cannot pass for steering.
