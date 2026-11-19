# A growth that reads only the allowed states: pre-registration

Epic `STATES-GROWTH-20261119-001` (the coordinator's go-ahead on `NAE-GROWTH-20261119-001#1`, challenging A108; goals G17 and G1),
2026-11-19. Written after a pilot (disclosed) and the advisor's answer, before the frozen run. The canonical K1–K3 test is unchanged.

## The question

The cheapest growth reads which junction holds which distinction (A108). Is there a growth that reads only the allowed states? Is
it well defined? How does it compare with the cheapest growth? The stop rule: a states-only law well defined on all the test
stages, or the point where none can be.

## The states-only growth (the advisor's rank 1)

M(S) is the set of minimal not-all-equal constraints the allowed states satisfy: minimal sets on which no allowed state is
constant. It depends only on the states.
- **The growth.** At each stage, grow one round of the cheapest growth (under not-all-equal) on M(S) when M(S) is an admissible
  presentation: every member of three places or more, every distinction in at most two members. Otherwise it is undefined.
- **The verdicts.** A stage is saturated (M(S) is its presentation, counted with repeats), sharpened (M differs but is admissible),
  or undefined.
- **What is immediate.** Saturated stages with the same states are equal, so on them the cheapest growth already reads only the
  states.

**Under parity.** A presentation with each distinction in at most two junctions is a graph: junctions are points, distinctions are
lines. Add the implied junction that holds every loose distinction. The states fix only the cycle matroid of this completed system,
so which junction is "dropped", and hence which distinctions are loose, is a choice the states cannot see. By Whitney's
2-isomorphism theorem (1933), two completed systems with the same cycle matroid differ by twists at two-point cuts, and if they are
three-connected they are the same graph.

## Pilot (disclosed)

- **The advisor's example** (the literature's K4: the four "stars" and the four "triangles" as two presentations). It replays:
  - 18 states and 8 minimal constraints;
  - exactly 2 admissible, irredundant presentations;
  - the duplicate pair has 1 minimal constraint.
- **On 1,594 irredundant stages** of NAE-GROWTH's part B, M equals the junctions on 1,420 (89%).
  - Where it differs, a triangle of knots (three pairwise touching) or a double touch is present.
  - The advisor's local "forcing" test does not predict it (17 against 157).
- **Trajectories** on a few one- to three-knot starts:
  - The two growths agree while the stages stay saturated.
  - The duplicate pair is sharpened, and the states-only growth grows it where the cheapest growth closes.
  - A triangle of three-place knots becomes undefined after round 1.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| A1 | the K4 example: 18 states, 8 minimal constraints, 2 admissible irredundant presentations; the duplicate pair: 1 (a replay) | any differs |
| B1 | among the irredundant stages of NAE-GROWTH's part B (2,715 stages), the saturated share is in [0.85, 0.92] | outside |
| C1 | along trajectories from every census arrangement of one to four knots (up to 18 distinctions, 6 rounds), the two growths make the same counts at every round while every stage so far is saturated | any differs |
| C2 | every disagreement follows a stage that is not saturated | one follows a saturated stage |
| C3 | (risky) every trajectory that becomes undefined starts from an arrangement with a triangle of knots or two knots touching twice | one does not |
| D1 | (Whitney) every parity same-state pair whose completed systems are both three-connected has the same completed system up to renaming | one differs |
| D2 | at least half of parity's same-state pairs have the same completed system up to renaming: they differ only in which junction is dropped | fewer |

## Prior work in the program

`python3 -B scripts/track.py objects "growth that reads only the allowed states presentation minimal constraints" --until 2026-11-19 --exclude STATES-GROWTH-20261119-001`

- `NAE-GROWTH-20261119-001`: A108, and the stages and collisions used here.
- `STATE-RULES-20261117-001` and A99: an earlier states-only growth, of betweenness knots one distinction at a time; a different
  object with the same aim.
- `DISTANCE-INFO-20261117-001` and `DISTANCE-ORDER-20261117-001`: what the states' distances determine.
- `MEET-ORDERS-20261118-001`, `MEET-ADDED-20261118-001`, `KNOT-ORDER-20261117-001`: the states-only betweenness growth line
  (A99); related aim, different object. `HARMONY-ARITH-20261112-001`, `FAR-BOUND-20261112-001`: unrelated objects, the same words.

## Runs and stop rule

`job.py` through the shared runner (36 cases); `merge.py` scores. Stop at the read-out.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), at the design stage, before the freeze. This answer stays within its text.
- **What it gave.** The rank-1 definition and the three verdicts. The K4 example, so that NAE's irredundant presentation is not
  unique (A1). The parity reading through the completed system and Whitney's theorem (D1, D2). The test order.
- **Its guesses.** It guessed a saturated share of 85–95%; the pilot gives 89%, so B1 narrows the range. Its local forcing criterion
  was tested in the pilot and does not predict saturation.
