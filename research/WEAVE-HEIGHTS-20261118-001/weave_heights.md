# Heights on weave patches: the criterion and the lower bound

Epic `WEAVE-HEIGHTS-20261118-001`, 18 November 2026, by Claude. The coordinator's go-ahead on `DOUBLE-MEET-20261118-001`'s direction 2:
write the height-function criterion for constrained sets and the bound b ≥ steps apart + 1 on weave patches without holes (the
advisor's sketches H and L) as full, refereeable proofs. Goal G1; tests A39 and A97. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `fa778afc8` at 11:51 UTC; the checks ran from 11:51 to
  12:27 UTC through the shared runner (`WEAVE-HEIGHTS-B1`, 45 cases, none failed).
- Proofs: [proof.md](../../proofs/WEAVE-HEIGHTS-20261118-001A/WEAVE-HEIGHTS-20261118-001A-P001_heights/proof.md).
- Code: [job.py, merge.py, checks.py](../../experiments/WEAVE-HEIGHTS-20261118-001B/WEAVE-HEIGHTS-20261118-001B-E001_checks/).
- Results: [results.json](../../artifacts/WEAVE-HEIGHTS-20261118-001B/WEAVE-HEIGHTS-20261118-001B-E001_checks/results.json).

## The answer

**In the owner's terms.**
- **Both are now proved.** On a patch of the weave without holes, every allowed state is a height: a whole number at each distinction
  that steps up by 1 or down by 2 along each pair in a fixed direction, the value being its parity (proved). Asking whether some values on
  a set extend to a state becomes asking whether a few inequalities between whole numbers can hold together, and that fails exactly
  around a cycle of the set whose length, counted in those steps, is too short: **a set is constrained exactly when m ≥ 3 of its
  distinctions can be visited in a cycle of length at most 3(m − 2)** (proved, with the parity bookkeeping done exactly).
- **The lower bound.** Going from one distinction to another and back always costs exactly three times the steps apart (proved; this
  needs that no knot of a patch without holes is level as seen from any distinction, which rests on cited theorems about bridged graphs).
  A bond's cycle must cost at most 3(m − 2) and contains such a round trip, so **every bond holding two distinctions has at least steps
  apart + 2 members: bond distance is at least steps apart + 1** (proved).
- **Checked one size past.** Every step was checked mechanically on every patch without holes to twelve knots (59,564), with no
  exception: the criterion set by set to eight knots (833,536 sets), the lower bound on all 3,365,574 bonded pairs at twelve knots.
- **What it does not give.** The upper side: at the rim, bond distance exceeds steps apart + 1 (by 2 from ten knots, by 3 from twelve,
  where a lone pair of opposite classes facing each other can break the triangle inequality while bonded). The height function turns the
  question into a shortest-cycle problem, but no closed form for the excess was found.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 4 gates | held | all pass |
| Q1 | Lemma 1's count (states = 2 × falling-pair choices), discs to eight knots | held | 1,080 discs |
| Q2 | Proposition 3 set by set, discs to eight knots | held | 833,536 sets |
| Q3 | flagness, discs to twelve knots | held | 59,564 discs |
| Q4 | convex balls and the triangle condition, to twelve knots | held | no exception |
| Q5 | no level knot, to twelve knots | held | none |
| Q6 | D + D = 3·steps and the lone-distinction identities, to twelve knots | held | no exception |
| Q7 | Theorem 7 on discs of twelve knots | held | 0 of 3,365,574 bonded pairs below steps + 1 |

7 of 7 held.

## What it means for A97, A39 and B200

The weave result of `DOUBLE-MEET-20261118-001` now stands on proofs where it is a theorem (the criterion and the lower bound) and on
computation where it is not (the rim obstruction and the upper side). For A39 and A97, under not-all-equal on the weave, bond distance
never undercuts the steps apart: whatever breaks it at the rim makes distinctions look farther apart, never nearer.

## Known results, and what this adds

Known, cited once: the triangular antiferromagnet's height function (Blöte and Hilhorst 1982; Nienhuis, Hilhorst and Blöte 1984); heights
as integer difference constraints (Thurston 1990); bridged graphs and their convex balls and triangle condition (Soltan and Chepoi 1983;
Farber and Jamison 1987; Chepoi 2000; Januszkiewicz and Świątkowski 2006; Chalopin, Chepoi, Hirai and Osajda 2020). What this adds: the
exact criterion for constrained sets (minimal non-shattered sets of the state family) on patches without holes, the round-trip
identity, and the lower bound on bond distance, with mechanical checks; the advisor knew no statement of them; no literature search was
run.

## Limitations

- Lemma 5 rests on cited theorems whose numbers were not checked against the sources; its ingredients and conclusion were checked on
  every disc to twelve knots.
- Patches with holes are not covered (heights there can wind).
- The upper side is open.

## Reproduce

```sh
d=experiments/WEAVE-HEIGHTS-20261118-001B/WEAVE-HEIGHTS-20261118-001B-E001_checks
.venv/bin/python -B $d/checks.py
.venv/bin/python -B scripts/longrun.py launch $d/job.py --out runs/weave-heights --workers 8 --case-mem 1800M
.venv/bin/python -B $d/merge.py runs/weave-heights
```

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md); `modelUsage`
names claude-fable-5-2) refereed the written proofs before the freeze: no wrong step from Lemma 0 to Theorem 7 or in Lemma 8; its
fixes (definitions, the hypotheses of the cited characterisation, the 2020 reference, Corollary 4's subset step, Theorem 7 for every
bond, a remark weakened) are folded in. The statements and outline of Proposition 3 and Lemma 6 are its, from `DOUBLE-MEET-20261118-001`.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: prove the criterion and the lower bound | **Status:** Successful (referee pending) | Both proved; every step checked on every disc to twelve knots; 7 of 7 held |
| Local direction: one distance for both laws (B200) | Promising | On the weave bond distance never undercuts steps apart; its rim excess is the open part |
| Broader exploration: heights and tilings | Known alternatives | The height function and difference constraints are classical; the criterion for constrained sets is the program's |
| Long-term goal: G1 | G1 capability gained | The weave's distance is bounded below by the steps apart, proved |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which facing lone pairs are bonded, and how far: use the cyclic criterion to compute the least tight cycle through a facing pair in closed form | 2/3 | 2/3 | the least tight cycle through the two acute lone distinctions of parallelograms and their one-knot extensions → stop at a formula that predicts every case to twelve knots, or a counterexample | Alternative |
| 2 | Patches with holes: heights that wind, and whether a hole acts like a rim | 1/3 | 2/3 | annuli of the weave with the criterion adapted to a winding height → stop at the first failure or a pattern | Alternative |
| 3 | Lemma 5 without citations: a direct proof that no knot of a lattice disc is level | 1/3 | 2/3 | an argument by the boundary curve's turning → stop at a proof or a gap | Alternative |

**Corrections:** none for this study (DOUBLE-MEET's referee Block, folded in today in `b3afe07ca`, bears on the upper side, which this
study leaves open).

**Goals:** G1 checkpoint (capability gained: the weave's height criterion and the lower bound b ≥ steps apart + 1, proved); no goal
changed.

**Assumptions:** A39 gains the proof of the lower bound; no status changed, no new entry.
