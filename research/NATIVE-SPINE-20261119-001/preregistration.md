# Pre-registration: can the growth pick its own spine?

Epic `NATIVE-SPINE-20261119-001`, ticket `NATIVE-SPINE-20261119-001B`, 19 November 2026, by Claude, on the coordinator's go-ahead
for `JUNCTION-KINDS-20261119-001#1`, bounded to three rules. Goal G17.

## The question

In the ten break-shape eddies with W = y²(1 + y), each round's junctions pair one to one with ancestors two or three rounds back
(a perfect matching of the spine relation, `JUNCTION-KINDS-20261119-001`). That matching was found by Hopcroft–Karp. Does a rule
read from the growth pick it?

## Pilot (disclosed)

On population index 28 (rounds 4 to 13) and index 44 (to round 11): N never keeps a single partner; M keeps one for 25–42% of a
round, with collisions; F for under 12%; the full relation's matching is never unique, and on index 44 no partner is forced.

## The rules (`rulelib.py`)

For a junction j of round t, its candidates are its ancestors at exact depths 2 and 3, each with m(a, j) parent chains.
- **N, the newest ancestor:** its depth-2 ancestors. It cannot reach round t − 3, so it fails by count (c(t) > c(t − 2)) before any
  data are read. It is recorded as refuted by count, not counted as a tested rule (the advisor's point).
- **N\*, the advisor's native reading of "newest":** take a partner where it is forced, propagating forced choices. Its ceiling is
  the set of pairs that lie in every perfect matching, so it picks the spine exactly when the matching is unique. The **forced
  share** of a round is the share of its junctions whose partner is the same in every perfect matching.
- **M, most chains:** its candidates of largest m(a, j), at either depth.
- **F, fewest chains:** those of smallest m(a, j).

A rule picks the spine at round t when what it keeps is a perfect matching of round t with rounds t − 2 and t − 3 together.

## Population and runs

The ten (BREAK-EDDIES population indices 28, 44, 52, 55, 56, 58, 61, 65, 66, 68), 24 rounds, every recurrent round (c(t) =
c(t − 2) + c(t − 3)). One frozen run through the shared runner (`NATIVE-SPINE-B1`, `runs/native-spine`). Stop at the verdicts.

## Predictions (frozen; scored by `merge.py`)

| # | Prediction | Falsified by |
| --- | --- | --- |
| S1 | (a check, by count) N picks the spine at no recurrent round, in all ten | any round where it does |
| S2 | M picks the spine at no recurrent round, in all ten | any round where it does |
| S3 | F picks the spine at no recurrent round, in all ten | any round where it does |
| S4 | N\* fails: the forced share is below 1 at every recurrent round from 6 on, in all ten | a round where the matching is unique |
| S5 | (risky, the advisor's) by round 13, M's single picks collide (two junctions keep the same single ancestor) in at least 8 of the ten | collisions in fewer than 8 |

Readouts: the forced share per round; for M and F, ties, the depth split of what they keep, single picks and collisions; at rounds
10, 15 and 20, whether a degree-preserving shuffle of the relation still has a perfect matching (the advisor's null).

## What would follow

S2 to S4 holding: none of the three rules picks the spine, and no pair is forced in a way that would let propagation do it. The
spine is then a choice the ancestry leaves open. The rule-free test (an automorphism of the start moving every perfect matching) is
the direction that could prove no native rule exists.

## Prior work in the program

`python3 -B scripts/track.py objects "spine ancestor perfect matching substitution Padovan rule forced unique" --until 2026-11-19 --exclude NATIVE-SPINE-20261119-001`

- `JUNCTION-KINDS-20261119-001`: the spine relation and its perfect matchings, the object under test.
- `WEAVE-MIX-20261117-001`, `RIGID-WORLDS-20261110-001`, `PICK-TWO-20261118-001`, `PIN-RULE-20261112-001` and
  `THREE-WAY-20261119-001`: the same words, other objects.

**Known, cited once.** Hopcroft–Karp; a perfect matching's pairs that lie in every perfect matching are those not on an alternating
cycle (strongly connected components of the alternating digraph); degree-preserving switchings.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before this freeze. Adopted: N as refuted by count; N\* and the forced share; ties, the
depth split and collisions for M and F; the shuffle null; its risky prediction S5; the automorphism test as a direction.
