# Heights on weave patches: pre-registration

Epic `WEAVE-HEIGHTS-20261118-001` (the coordinator's go-ahead on `DOUBLE-MEET-20261118-001`'s direction 2; G1; tests A39 and A97),
18 November 2026. The proofs (ticket A) were written before this freeze and refereed once by the advisor; ticket B checks each step
mechanically. The canonical K1–K3 test is unchanged.

## The question

`DOUBLE-MEET-20261118-001` rests on two of the advisor's sketches: the height-function criterion for constrained sets on weave patches
without holes, and the bound b ≥ steps apart + 1. Write them as full, refereeable proofs, and check every step on every disc patch one
size past the earlier census.

## In standard terms

Not-all-equal on the weave is the triangular Ising antiferromagnet at zero temperature; states are height functions (Blöte and
Hilhorst 1982; Nienhuis, Hilhorst and Blöte 1984); heights are integer difference constraints (as in Thurston 1990), feasible exactly
when no cycle is negative. The pair graph of a disc patch is a bridged graph (Chepoi 2000; Januszkiewicz and Świątkowski 2006), with
convex balls (Soltan and Chepoi 1983; Farber and Jamison 1987) and the triangle condition (Chalopin, Chepoi, Hirai and Osajda 2020).

## Prior work in the program

`python3 -B scripts/track.py objects "height function weave criterion constrained sets lower bound" --until 2026-11-18 --exclude WEAVE-HEIGHTS-20261118-001`
`python3 -B scripts/track.py objects "weave patches bond distance steps apart not-all-equal" --until 2026-11-18 --exclude WEAVE-HEIGHTS-20261118-001`

- `DOUBLE-MEET-20261118-001` — same objects: the sketches and their computed checks (criterion to seven knots, D + D = 3·steps and
  b ≥ steps + 1 to eleven).
- `RULER-20261111-001`, `RULER-FLAT-20261111-001` — relatives: height functions and difference constraints on the endless and closed
  weaves.
- `FREE-READ-20261118-001`, `CUMULANT-DIST-20261118-001` — relatives on bond distance (trees, rings; parity bases), matched on words.

## Settled by construction (ticket A)

Lemma 0 (disc patches are topological discs, simply connected, flag), Lemma 1 (states are height functions up to adding 6),
Lemma 2 (heights as difference constraints; extension), Proposition 3 (a set is constrained exactly when m ≥ 3 of its members have a
cyclic order of D-sum at most 3(m − 2)), Corollary 4, Lemma 5 (no level knot, through the bridged-graph theorems), Lemma 6
(D(x, y) + D(y, x) = 3·steps), Theorem 7 (every bond holding x ≠ y has at least steps + 2 members) and Lemma 8 (lone distinctions).

## Exploration disclosed

`DOUBLE-MEET-20261118-001`'s census checked the criterion set by set to seven knots, D + D = 3·steps and b ≥ steps + 1 to eleven. Here,
three shards of the frozen job (eight, eleven and twelve knots) were timed reading only their keys.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates (`checks.py`): the forward orientation; every check clean on the two-knot disc (10 states = 2 × 5 choices); the 3 × 3 parallelogram; the disc test | any fails |
| Q1 | Lemma 1: on every disc to eight knots, the number of states is twice the number of ways to pick one falling pair per knot, consistently on shared pairs | any disc differs |
| Q2 | Proposition 3: on every disc to eight knots (one past seven), the cyclic criterion gives exactly the constrained sets | any set differs |
| Q3 | Lemma 0: on every disc to twelve knots, every three pairwise co-knotted distinctions form a knot of the patch | any exception |
| Q4 | The bridged-graph facts used in Lemma 5: on every disc to twelve knots, every ball is convex and the triangle condition holds | any exception |
| Q5 | Lemma 5: on every disc to twelve knots, no knot is level from any distinction | any level knot |
| Q6 | Lemmas 6 and 8: on every disc to twelve knots, D(x, y) + D(y, x) = 3·steps, and the lone-distinction identities hold | any exception |
| Q7 | Theorem 7: on every disc of twelve knots (one past eleven), no bonded pair has b below steps + 1 | any pair below |

## Runs and stop rule

`scripts/longrun.py` with `job.py`: 45 cases (discs of one to twelve knots, twelve shards from ten knots); `merge.py` scores. Registered
as WEAVE-HEIGHTS-B1 (about half an hour on 8 workers). One run; no change after seeing results. Stop at the read-out, the referee
hand-off and the report.

Advisor. `claude -p --model claude-fable-5-2 --tools ""` refereed the written proofs before the freeze ([question](advisor/question_1.md),
[answer](advisor/answer_1_fable.md); `modelUsage` names claude-fable-5-2): no wrong step in the chain from Lemma 0 to Theorem 7 or in Lemma
8; it asked for the definitions of lone distinctions and of b, s(x, x) = 0, G connected where D is used, the three hypothesis checks
before invoking the bridged-graph characterisation, the 2020 reference for the triangle condition in place of 1989, a sentence on
subsets of free sets in Corollary 4, the reduction sentence in Proposition 3, Theorem 7 strengthened to every bond, and the remark after
Lemma 8 weakened. All are folded in. It could not supply a self-contained proof of Lemma 5; Q4 and Q5 check its ingredients and
conclusion.
