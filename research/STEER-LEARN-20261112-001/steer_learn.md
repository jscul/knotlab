# A learner whose examples steer its search

Epic `STEER-LEARN-20261112-001` (sub-goal B165, G15 with G16; program learning), 2026-11-12, at the coordinator's go-ahead.
Pre-registered in [preregistration.md](preregistration.md), frozen in commit `a2cd50751` before any frozen run; the rules and the test were
drafted with the advisor model. Proof family: `proofs/STEER-LEARN-20261112-001A/`. **Referee pending** (handed to the referee thread).

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
  disfavours the count's: a preference of the dynamics among the laws it can rest at.
- **Every check was charged,** as the coordinator asked: candidate laws checked against stored states count as probes. Two-sided acceptance
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
| This attempt: a learner whose examples steer (B165) | **Status:** Failed (referee pending) | no rule beats blind search on the count; the only fast target is one the walk itself favours |
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
