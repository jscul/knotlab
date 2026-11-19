# The eddies in the cluster rule's break shapes: pre-registration

Epic `BREAK-EDDIES-20261119-001` (the coordinator's go-ahead on `LOOP-CATALOGUE-20261119-001#1`; goal G17), 2026-11-19. Written
after a pilot (disclosed) and the advisor's answer, before the frozen run. The canonical K1–K3 test is unchanged.

## The question

LOOP-CATALOGUE found self-feeding starts where the cluster rule breaks:
- a merged block with a missing pair (the overlapping sunflowers);
- first-round groups of three that overlap another block in two knots, or meet at a knot.

1. Do those starts still grow by a finite model, a fixed round-weight W with rate the root of W = 1?
2. What loops do they hold?
3. Does one extended rule cover them, or do they need a different kind of object?

## Pilot (disclosed)

- **Long growth.** The 30 provisional minimal starts were grown to 40 rounds or 300,000 junctions, each in its own 6 GB child
  process. 25 of the 30 give exact recurrences whose round-weights belong to the catalogue's family, at loop lengths no ring
  makes:
  - W = y^2 (1 + y), the plastic number 1.3247 (3 starts);
  - W = y^3 (1 + y), rate 1.2207 (6);
  - W = y^4 (1 + y) (3);
  - W = y^5 (1 + y) (4);
  - W = y^5 (1 + y)^3 (9);
  - W = y^5 + y^6 + 2y^7 + y^8 (1).

  The theta (#0) and three others (#4, #5, #6) were not settled: they grow explosively or hit the limits.
- **Restarting the rule at a later stage.** The growth continued from its stage after s rounds is the growth of that stage taken
  as a start, so the rule can be applied at any stage (stagelib). The stages after 0 to 4 rounds stay outside the rule's scope, or
  hold a known break, in all 30. The break shapes reproduce themselves round after round.
- **Unmerging incomplete blocks** (breaklib, keeping two simplices apart unless their union is complete) made the theta worse: it
  differs from round 1.
- **Smoke run** of job.py on one start (W = y^3 (1 + y)): the recurrence held to round 44, but the largest group grew to 14 and the
  most fresh distinctions to 18. So groups are not bounded even where the count is rational.

## Method

Every one of the 122 exponential starts of LOOP-CATALOGUE's part U (main run; population.json) is grown in its own child process
(6 GB, 1,500 s) to 60 rounds or 300,000 junctions. After every round the child records:
- the counts;
- the largest group (most parents of one new junction);
- the most fresh distinctions one junction took.

Berlekamp–Massey reads the least recurrence, and W is read from the factor with the largest root. Part S asks the cluster rule
about the stages after 0 to 3 rounds. Outside kills (a negative exit status) are regrown.

## Prior work in the program

`python3 -B scripts/track.py objects "self-feeding starts in the cluster rule's break shapes overlapping groups of three recurrences" --until 2026-11-19 --exclude BREAK-EDDIES-20261119-001`

- `LOOP-CATALOGUE-20261119-001` found these starts and set the round-weight frame. `CLUSTER-ALL-20261119-001` gives the rule and
  its two breaks. `RING-PAIR-20261119-001` gives the cover model, and `JOIN-GROWTH-20261118-001` the recurrence reading.
- `SCALE-SHARE-20261119-001` (rings rare at scale; the false seven-knot ring was a break shape) and `ROUND-FREE-20261119-001`
  (the closure law fails at the same breaks): the same population and the same breaks. `STEER-LEARN-20261112-001`: unrelated object,
  the same words.

## Predictions (frozen; the advisor's P1–P7 where marked)

| # | Prediction | Fails when |
| --- | --- | --- |
| B1 | (advisor P5) every start rational in the pilot keeps its recurrence to the new horizon | one breaks |
| B2 | every rational start's W has nonnegative integer coefficients and W(1) ≥ 2 (a round-weight with at least two ways round) | one has not |
| B3 | readout, not a prediction: how the largest group grows in rational starts. The advisor's P1 (bounded) is already false in the smoke run, disclosed: a W = y^3 (1 + y) start reaches groups of 14 by round 44 | — |
| B4 | (after the advisor's P2, risky) in each explosive start (the theta, #4, #5, #6) the largest group exceeds that of every rational start at the same round, from some round on | one never does |
| B5 | (advisor P4) no recurrence of order 8 or less fits the theta's counts | one fits |
| B6 | every rational start whose W has a loop length L ≤ 3 (lowest power of y) holds a first-round group of three | one does not |
| B7 | (advisor P7) raising one knot's open places never lengthens the loop: for two rational starts on the same touches whose sizes differ by one at one knot, the larger has L no greater | one pair breaks it |
| B8 | no stage after 0 to 3 rounds of any of the 122 is inside the rule's scope and free of known breaks | one is |

## Runs and stop rule

`job.py` through the shared runner (122 cases, 3 workers, 6.5 GB each; registered). `merge.py` scores. Stop at the read-out, which
answers the three questions.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. Its points, checked:
- **Its environment.** It reported unreliable tool results in its own session. It had no tools, and its numbers were checked here.
- **Open places set the loop length.** It noted this (#17 and #20 share their touches and groups but differ in loop length), and
  that no graph on the round-1 groups alone can give the weights.
- **The loops appear in round 1.** In #23 and #25 the block graph of the start is a tree, and the rings run through first-round
  junctions. Part S tests the consequence, that restarting the rule later does not recover them (B8).
- **The theta and the explosive starts.** It read them as explosive with a long fuse, from groups that grow by merging (B4).
- **Its predictions.** P2, P4, P5 and P7 become B4 (restated), B5, B1 and B7. P1 (groups stay bounded in rational starts) failed in
  the smoke run, so B3 is a readout. Its P3 (the theta's round-19 ratio above 2) is left out
  as untestable within memory. Its P6 (the order of valid sets in a round does not matter) is left out, as the policy has no order
  within a round.
- **Two of its points did not hold.** Its claim that the theta's groups are not maximal: knots 1, 4 and 5 meet at knot 0, so they
  are pairs by the policy's own rule (a set of three needs no common neighbour). Its claim that the round-1 counts do not match the
  groups: round 1 also makes offshoots.
