# What a states-only growth gives up where the states allow several presentations

Epic `MANY-VALUED-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead (taking `STATES-GROWTH-20261119-001#2`).
Goals G1 and G17. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `0a6f2350e` at 11:35 UTC after a pilot (disclosed).
- The run went through the shared runner (`MANY-VALUED-B1`, `runs/many-valued`, 31 cases), all ok by 11:38 UTC.
- Code: [manylib.py, job.py, merge.py](../../experiments/MANY-VALUED-20261119-001B/MANY-VALUED-20261119-001B-E001_presentations/).
- Results: [results.json](../../artifacts/MANY-VALUED-20261119-001B/MANY-VALUED-20261119-001B-E001_presentations/results.json).

**Words.** As in `STATES-GROWTH-20261119-001`; M(S) is the set of minimal not-all-equal constraints of the allowed states S. A
**presentation** of S is a set of knots that is:
- admissible: three places or more, each distinction held once or twice;
- irredundant;
- allowing exactly S.

The **refined rule** grows the presentation drawn from M(S) when it is unique up to renaming.

## The answer

**In the owner's terms.**
- **The stop rule's answer: there was nothing to choose between.** At every one of the 146 points where the states-only growth had
  been undefined, the allowed states have exactly one presentation up to renaming, and it is the stage itself.
  - The rule had failed only because it used all the minimal constraints as the presentation, and some of them are consequences,
    not knots.
  - The one place with two presentations, four three-place knots pairwise touching (the K4 example), has two that are exchanged by a
    renaming, so they grow alike.
- **So the states fix the presentation almost everywhere small.** With the refined rule, a growth reading only the allowed states
  equals the cheapest growth at every round on 1,805 of the 1,806 census trajectories without a redundant knot, from starts of up to
  four knots.
- **The one exception is the real limit.** The start has knots (0, 1, 2), (3, 4, 5), (0, 3, 6) and (1, 2, 4, 5, 6), and the
  five-place knot's support is not minimal: NAE(1, 2, 4, 5) already holds.
  - The states cannot tell this knot from its four-place core.
  - Read with the five-place knot, every distinction is held twice and the growth closes at once.
  - Read with its core, distinction 6 is held once and the growth grows 1, 2, 3.
  - The advisor predicted exactly this shape before the run.
- **What a states-only growth gives up, then.** Two things, both invisible in the states:
  - a redundant knot (STATES-GROWTH);
  - a knot whose support is larger than the constraint it imposes.

  Everywhere else in this range, distance, read from the states, carries all the growth uses.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| M1 | on the 106 points not read in the pilot, ≥ 95% have exactly one presentation from M(S), and it is the stage | **held** | 106 of 106 (and all 146 in both pools) |
| M3 | on every trajectory with no redundant knot, the refined rule is defined and equals the cheapest growth | failed | 1,805 of 1,806; the exception is the non-minimal-support start above |
| (replay) | the advisor's pair: same states, one closes, one grows | as predicted | closes at once against 1, 2, 3 |

1 of 2 frozen predictions held. The failure is the mechanism the advisor named, found once in the census range.

## Known results, and what this adds

- **Known.** Minimal transversals, and implied constraints in constraint satisfaction. A redundant or non-minimal constraint is
  invisible to the solution set: this is standard.
- **What this adds.** The measurement for the cheapest growth. In the range checked, the allowed states fix the knots up to renaming
  at every point tested, apart from redundant knots and one non-minimal support, so the growth's presentation dependence (A108)
  comes only from those two.

## Limitations

- Brute force over the allowed states: stages of at most 18 distinctions, trajectories of at most 6 rounds, starts of up to four
  knots.
- Presentations are searched among M(S), and among M(S) with the stage's knots. The full pool of all implied constraints (the
  advisor's) was not enumerated.
- 36 trajectories with redundant knots ended where pool M had no admissible presentation. They are outside M3 and reported only.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. Its answer stayed within its text.
- **The non-minimal support.** It gave the mechanism and an example pair. The pair replays, and the census's one M3 failure is that
  shape.
- **Renaming.** It said to count presentations up to renaming; the K4 case is then unique.
- **The headline and the scoring.** It said the finding is uniqueness, and asked for M1 to be scored on the unread points, by start.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: presentations of the same states | **Status:** Partially successful (1 of 2 held; the failure is the predicted mechanism) | Unique up to renaming at all 146 points; the refined states-only growth equals the cheapest growth on 1,805 of 1,806 clean trajectories |
| Local direction: A108 | Confirmed, narrowed | The presentation dependence comes from two named things: redundant knots and non-minimal supports |
| Broader exploration: the growth and the canonical reading | Known alternatives | A states-only growth exists wherever neither occurs |
| Long-term goal: G1 | Capability gained | Distance (the states) carries the growth except at those two |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Parity over the dropped junction on the rings (`STATES-GROWTH-20261119-001#3`), as the coordinator set if BREAK-EDDIES' verdict is still out | 2/3 | 2/3 | as there | Selected · started |
| 2 | A transfer between kinds of junction (`JUNCTION-MAP-20261119-001#1`), after the BREAK-EDDIES verdict | 3/3 | 2/3 | as there | Alternative · deferred |
| 3 | How often non-minimal supports occur at scale, and what the states-only growth does after them | 2/3 | 3/3 | sample five- to eight-knot starts → stop at the rate and the growth classes | Alternative · deferred |
