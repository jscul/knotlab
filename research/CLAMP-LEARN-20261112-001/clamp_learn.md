# Let the examples shape the dissonance the learner feels

Epic `CLAMP-LEARN-20261112-001` (sub-goal B168, with the cheap part of B169; G15 with G16; program learning), 2026-11-12. Pre-registered in
[preregistration.md](preregistration.md), frozen in commit `498f903cc`; the design and predictions were put to the advisor model before
freezing. Proof family: `proofs/CLAMP-LEARN-20261112-001A/`. **Refereed: Confirmed** with one wording fix, Not a block, made below
([referee report](referee-R1/report.md), commit `b834df5f6`). Closed at the owner's pause of the learning line (2026-11-12): every frozen
part had already run to completion, so nothing is left unfinished.

## The answer

**No. A clamped phase does not let the examples steer the learner, and the walk's bias is its dynamics, not its start.**

- **Clamped and contrastive learners (computed, frozen).** With 64 laws at rest and random starts, the clamped phase found the count in 13
  of 100 runs and contrastive acceptance in 12, against 48 for the unchanged learner, each within the frozen five-minute cap per run;
  neither came within the restricted blind median (blind search among laws consistent with every positive example: 6 draws, about 1
  million steps), nor the uniform one. No steering shown.
  - **The cap, not the budget, stopped every run that did not find.** All 363 such runs stopped at 300 s, about 25 to 42 million steps;
    none reached the 2,000,000-step learning budget, so the rule setting unfound runs to the budget never applied (the summary counts them
    as never finished). The comparison with B is not one of speed: contrastive acceptance takes the most steps per second and finds the
    count least often.
- **The restriction alone is strong (exact).** Among the laws at rest, those consistent with every positive example hold the count 1 time in
  8 (against 1 in 32 among all), so any learner that merely filtered by the examples would already gain fourfold; the clamped learners did
  not reach even that. The chance weights each law at rest and each flip equally; it is not a uniform pick among the consistent laws first.
- **The walk's bias (B169's cheap part, computed).** Taught an impossible map, the unchanged walk rests at the count's law at 3.4% of probes
  on one copy (uniform: 12.5%) and at g's at 15.3% (uniform: 6.25%) from the fixed start, and 4.3% and 13.2% from random starts. The bias is
  the dynamics', not the start's.

## What is known, and what is proved and computed

| Claim | Evidence class |
| --- | --- |
| Blind medians uniform and restricted to consistent laws, in draws and steps | exact |
| No steering: C and CA pass on neither target | computed, frozen (600 runs; counts within the five-minute cap per run) |
| The walk's bias is the same from random starts as from the fixed start | computed, frozen (80 walks of 60 probes) |
| A clamped phase against a free or negative phase is Boltzmann machine learning, contrastive Hebbian learning, equilibrium propagation | known |

## Against the pre-registration

Predicted no steering: held. Predicted C and CA would beat the uniform blind median: wrong, they did not. Predicted the bias was mostly the
start: wrong, it is the dynamics.

## Assumptions

None added or changed. Relied on: A20, A21, A46, A47, A49, A50, A52, A58.

## Corrections

None at the close. One from the referee, Not a block, logged in `docs/CORRECTIONS.md`: the found counts are counts within the five-minute
cap, which stopped every run that did not find; the budget never did.

## In the owner's words

Holding each example in front of the learner while it wanders made it worse at finding the counting rule, not better. And its leaning toward
some rules is in how it wanders, wherever it starts.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: let the examples shape the dissonance (B168) | **Status:** Failed (refereed, Confirmed) | no steering; the clamped learners found the count less often than the unchanged one |
| Local direction: energy-based teaching of this learner | Retire for now | probe-time steering (B165) and the clamped phase (B168) both fail |
| Broader exploration: learning program | Known alternatives | the drift test under shuffled outputs (the advisor's), why the dynamics prefers some laws (B169), symmetric laws (B166), two histories (B159) |
| Long-term goal: G15 Learning: a point in a learned knot pattern | Obstruction learned | learning from examples is not shown by any of five learners |

**Next step:** Research directions — No next action selected (the owner paused the learning line on 2026-11-12)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why the dynamics prefers some laws (B169, the rest) | 2/3 — Substantial | 3/3 — Ready | the walk's exact stationary preference over the 4 laws on one copy, from its move rules → the bias explained, or not | Alternative · deferred |
| 2 | The drift test (B171) | 2/3 — Substantial | 2/3 — Testable | under each example's clamp, the expected sign-move direction toward the taught law against shuffled outputs, scaling with the clamp length → steering seen without search, or none | Alternative · deferred |
| 3 | Symmetric laws (B166) | 2/3 — Substantial | 3/3 — Ready | as recorded | Alternative · deferred |
| 4 | Two histories (B159) | 2/3 — Substantial | 2/3 — Testable | as recorded | Alternative · deferred |

- Nothing is selected: the owner paused the learning line to save tokens, and every direction waits for the line to resume.
- **#2** is the advisor model's cleaner test, recorded so the line can pick it up cold.

**Corrections:** none at the close; one wording fix from the referee (Not a block).
**Goals:** G15 checkpoint (obstruction learned, with G16); sub-goal B168 taken; B169's cheap part done; B171 added.
**Assumptions:** none new or changed.
**Basket:** B169, B171, B166, B159, B162, B157, B154, B155, B156, B150, B151, B130 (the line paused).

## Final report as sent

Posted in the thread on 2026-11-12 (17:42 UTC), as the pause report: the clamped phase found the counting rule less often than without the examples (13 and 12 of 100 runs against 48), beating neither blind search nor blind search among rules consistent with the examples; the walk's bias is its own dynamics (taught nothing it could satisfy, it settles at the counting rule about a third as often as chance and at the swap target about twice as often, from random starts as much as from the usual one); five learners tried, none beats blind search, keeping a found rule works and being taught by examples is not shown; the B165 referee verdict folded in (Confirmed, two wording fixes logged); everything committed, LONG_RUNNING updated, the basket holding B169 and B171; the line stopped, nothing new started.

## Referee (2026-11-12)

Confirmed by the referee thread from the records, without regeneration (`referee-R1/`, `ref_clamp.py`): the restricted blind chances and
medians recomputed and matching in all four cases; the tallies (B 48 and 73, C 13 and 36, CA 12 and 55 of 100 for the count and g); on every
run with a record, found equals the map at the stop being the target, and all steps equal learning plus wrong copy plus probe walk; the walk's
shares as stated. One wording fix, Not a block, made above and logged in `docs/CORRECTIONS.md`: the found counts are counts within the
five-minute cap, which stopped all 363 runs that did not find (about 25 to 42 million steps), and the budget currency for such runs never
applied. Its optional note, also made above: the restricted chance weights each law at rest and each flip equally.
