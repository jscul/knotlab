# A growth that reads only the allowed states

Epic `STATES-GROWTH-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead (taking `NAE-GROWTH-20261119-001#1`),
challenging A108. Goals G17 and G1. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `86e8ac334` at 11:24 UTC after a pilot (disclosed).
- The run went through the shared runner (`STATES-GROWTH-B1`, `runs/states-growth`, 36 cases), all ok by 11:27 UTC.
- Code: [statelib.py, job.py, merge.py](../../experiments/STATES-GROWTH-20261119-001B/STATES-GROWTH-20261119-001B-E001_states/).
- Results: [results.json](../../artifacts/STATES-GROWTH-20261119-001B/STATES-GROWTH-20261119-001B-E001_states/results.json).

**Words.**
- M(S) is the set of minimal not-all-equal constraints the allowed states satisfy: the minimal sets of distinctions on which no
  allowed state is constant. It depends only on the states.
- The **states-only growth** grows one round of the cheapest growth on M(S) whenever M(S) is an admissible presentation, and is
  undefined otherwise.
- A stage is **saturated** when M(S) is its presentation exactly, counted with repeats; **sharpened** when M(S) differs but is
  admissible; **undefined** otherwise.

## The answer

**In the owner's terms.**
- **Under not-all-equal: yes, almost everywhere small.**
  - On 93% of small stages without a redundant knot (2,321 of 2,497), the allowed states fix the presentation: the minimal
    constraints they satisfy are exactly the knots.
  - There the cheapest growth already reads only the states. Along every trajectory from every census arrangement of up to four
    knots (1,939), the states-only growth and the cheapest growth agree at every round while the stages stay saturated.
- **Where they part, and why.** In exactly two places, both things the allowed states cannot see:
  - **A redundant knot,** one whose constraint the others already imply: all 218 such stages. The duplicate pair (two knots on the
    same three distinctions) has the same states as one lone knot. The cheapest growth closes it and the states-only growth grows it.
  - **Several presentations for the same states.** The advisor's example has four "stars" and four "triangles" (the literature's
    K4), with 18 states, 8 minimal constraints and two irredundant presentations. There the states-only growth is undefined: it
    would have to choose.
  - Every one of the 146 trajectories that reached that point started from an arrangement with a triangle of knots (three pairwise
    touching) or two knots touching twice.
- **Under parity: "loose" cannot be read from the states at all.** Add to a presentation the implied junction that holds every loose
  distinction, giving the completed system. The states fix only that system's cycle matroid, so which junction is "dropped", and
  hence which distinctions are loose, is a choice the states cannot see.
  - **Whitney's theorem holds.** Every one of parity's 145 same-state pairs whose completed systems are three-connected has the same
    completed system, with a different junction dropped (Whitney 1933).
  - **Most pairs are twists.** Overall only 42% of the 2,802 pairs are the same completed system. The rest also differ by twists at
    two-point cuts.
- **For the owner's premise that distance is the only information.** Distances are read from the allowed states. So wherever the
  states fix the presentation (93% of small not-all-equal stages), the growth reads nothing but what distance can carry. Under
  parity it always reads a choice beyond the states.
- **A108 is confirmed, and its reach is measured.** The cheapest growth does read the presentation. Under not-all-equal that matters
  only at redundant knots and at triangles or double touches; under parity it matters everywhere.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| A1 | the K4 example and the duplicate pair replay | **held** | 18 states, 8 minimal constraints, 2 presentations; 1 |
| B1 | saturated share of irredundant stages in [0.85, 0.92] | failed (narrowly) | 0.9295 (2,321 of 2,497); every redundant stage unsaturated (209 sharpened, 9 undefined) |
| C1 | the two growths agree while every stage so far is saturated | **held** | 0 disagreements in 1,939 trajectories |
| C2 | every disagreement follows an unsaturated stage | failed as worded | 17 disagreements follow a saturated states-only stage, each after the trajectories had already parted at an unsaturated one; the first disagreement always follows an unsaturated stage (C1) |
| C3 | (risky) undefined only from a triangle of knots or a double touch | **held** | 146 of 146 |
| D1 | (Whitney) three-connected same-state pairs are the same completed system | **held** | 145 of 145 |
| D2 | at least half of parity's same-state pairs are the same completed system | failed | 42% (1,168 of 2,802) |

4 of 7 held.

## Why it holds

- **Saturated stages never collide.** If M(S) is the presentation, then the same states give the same M(S), hence the same
  presentation. So on saturated stages the cheapest growth is a function of the states, and C1 follows. It is checked, not only
  argued.
- **A redundant knot is invisible.** Its constraint holds on the states of the others, so M(S) cannot contain it, or contains it once
  where the presentation has it twice.
- **Parity (the advisor's statement).** A presentation in which every distinction sits in at most two junctions is a graph. Its
  allowed states are the cycle space of the completed system, which fixes the cycle matroid and nothing more. Whitney's
  2-isomorphism theorem then says that two such graphs differ by twists at two-point cuts, and are the same graph when
  three-connected.

## Known results, and what this adds

- **Known, cited once.** Whitney's 2-isomorphism theorem (Whitney, *Amer. J. Math.* 55, 1933); cycle spaces and cycle matroids.
- **What this adds.** A states-only version of the cheapest growth under not-all-equal. The measurement of where it agrees: 93% of
  small irredundant stages. The two exact places where it cannot: redundant knots, and triangles or double touches. And the parity
  case, where looseness is a choice beyond the states.

## Limitations

- M(S) is computed by brute force over the allowed states, so stages have at most 15 to 18 distinctions, and trajectories run at
  most 6 rounds from starts of up to four knots.
- Constraints are searched up to one place more than the largest knot.
- Where the states-only growth is undefined, no choice rule was tried. The many-valued growth, all outcomes over all presentations,
  is the advisor's rank 2 and is left as a direction.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), at the design stage, before the freeze. This answer stayed within its text.
- **What held.** The rank-1 definition, the K4 example (A1, exact), the parity reading through Whitney (D1, exact), and its guess of
  an 85–95% saturated share (0.93).
- **What failed.** Its local forcing criterion (pilot). D2's "at least half re-choices" was my own reading of its account, and twists
  are the majority.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a growth that reads only the allowed states | **Status:** Partially successful (4 of 7 held) | Under not-all-equal it exists and agrees wherever the states fix the presentation (93% of small irredundant stages); it parts exactly at redundant knots and at triangles or double touches; under parity looseness is a choice beyond the states (Whitney) |
| Local direction: A108 | Confirmed, reach measured | The growth reads the presentation, and this matters at two named configurations under not-all-equal and everywhere under parity |
| Broader exploration: the growth and the canonical reading | Known alternatives | States-only where the presentation is fixed; a choice, or many-valued growth, elsewhere |
| Long-term goal: G1 | Capability gained | Where distance (read from states) is enough for the growth, measured |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A transfer between kinds of junction for the break shapes (`JUNCTION-MAP-20261119-001#1`), after BREAK-EDDIES' referee verdict | 3/3 | 2/3 | as there | Selected · awaiting go-ahead and the verdict |
| 2 | The many-valued states-only growth where it is undefined: all outcomes over all presentations of the same states | 2/3 — what a states-only growth must give up | 3/3 — the presentations are enumerable on small stages | enumerate the presentations at the 146 undefined points → stop at whether their outcomes agree in count | Alternative · deferred |
| 3 | Parity's states-only growth over the dropped junction: does any dropped-junction choice reproduce the catalogue's eddies? | 2/3 | 2/3 | on the rings, try every dropped junction → stop at the set of rates | Alternative · deferred |
