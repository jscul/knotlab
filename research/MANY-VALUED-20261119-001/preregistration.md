# What a states-only growth gives up where the states allow several presentations: pre-registration

Epic `MANY-VALUED-20261119-001` (the coordinator's go-ahead on `STATES-GROWTH-20261119-001#2`; goals G1 and G17), 2026-11-19.
Written after a pilot (disclosed) and the advisor's answer, before the frozen run. The canonical K1–K3 test is unchanged.

## The question and the stop rule

STATES-GROWTH's states-only growth (the cheapest growth on M(S), the minimal not-all-equal constraints) was undefined at 146
trajectory points. At each, list every admissible irredundant presentation of the same allowed states, grow each, and stop at
whether their counts agree.

**Presentations.** Sets of junction supports that are:
- admissible: every member of three places or more, every distinction in one or two members;
- irredundant;
- allowing exactly the stage's states.

They are drawn from one of two pools:
- **pool M:** M(S) alone, which is states-only;
- **pool stage:** M(S) together with the stage's own junctions, which reads the stage (the advisor's point: a junction's support
  need not be minimal).

Presentations are grouped up to renaming of distinctions. Two in one group grow alike, since a renaming that carries one onto the
other carries the states onto themselves.

**The refined rule.** Grow the presentation from pool M when it is unique up to renaming.

## Pilot (disclosed)

- **On the first 40 of the 146 points,** both pools give exactly one presentation up to renaming, and it is the stage itself.
- **One of the 40,** four three-place knots pairwise touching once (the K4 example in knot form), has two presentations. They are
  exchanged by a renaming and grow alike.
- **The advisor's pair** (smoke run, a replay, not a prediction). NAE(a, b, p), NAE(c, d, q), NAE(p, q, r), NAE(a, b, c, d, r)
  against the same with NAE(a, b, c, d) as the last member. They allow the same states. The first holds every distinction twice and
  closes at once; the second grows 1, 2, 3. Pool M sees only the second.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| M1 | on the 106 points not read in the pilot, at least 95% have exactly one presentation from pool M up to renaming, and it is the stage | fewer |
| M3 | on every census trajectory of one to four knots with no redundant knot, the refined rule is defined at every stage within reach (at most 18 distinctions, 6 rounds) and equals the cheapest growth | one is undefined or differs |

**Readouts.**
- Each pool's counts of presentation classes over all 146 points, and by start.
- Where pool M gives several classes, whether their counts agree.
- The advisor's pair.

## Prior work in the program

`python3 -B scripts/track.py objects "presentations of the same allowed states admissible irredundant not-all-equal" --until 2026-11-19 --exclude MANY-VALUED-20261119-001`

- `STATES-GROWTH-20261119-001` (the rule, its undefined points and the K4 example) and `NAE-GROWTH-20261119-001` (A108's
  collisions): the same object.
- `DISTANCE-INFO-20261117-001`: what the states' distances determine (related). `RULER-FLAT-20261111-001`: an unrelated object, the
  same words.

## Runs and stop rule

`job.py` through the shared runner (31 cases); `merge.py` scores. Stop at the read-out.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. The answer stayed within its text. It gave:
- **The non-minimal support,** a junction implied by a proper subset of it. That makes "M(S) and the stage's junctions" a pool that
  reads the stage, so the states-only rule uses pool M alone. Its example pair replays.
- **Renaming.** Presentations exchanged by a renaming grow alike (a theorem), so uniqueness is counted up to renaming.
- **The headline.** M3 is mostly a uniqueness claim. The finding to state is "the allowed states fix their admissible irredundant
  presentation, up to renaming, within the range checked".
- **The scoring.** Freeze M1 on the points not read in the pilot, and report it by start.
