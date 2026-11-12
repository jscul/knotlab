# Referee report NEST-READ-R1 (lean, as asked)

**Verdict: Confirmed, with two fixes (both Not a block).**
- **Everything recomputes from the records** with my own summary code: the code control, P2, P3 and P4, and the classification as
  described.
- **P3 is broad.** It is not carried by a few families.
- **The fixes.**
  - P4's distance control loses most deep pairs, because the uniform pattern seldom has a pair that far apart.
  - The 'hold' should be read with that in mind.

Referee: the background referee thread, 2026-11-12. `ref_nest.py` reads `runs_*.jsonl` only. There was no regeneration, as asked. The
advisor model was not consulted.

## 1. What reproduces

| Item | Census | Referee |
| --- | --- | --- |
| Families (480 constraining and 240 monotone per variant) | 1,440 | 1,440. Tied: 168 of the knot variant's 480 constraining, 2 of the direct variant's |
| Code control: Berge-acyclic pairs with L ≠ d + 2 | 0 | 0 |
| P2: monotone with a cycle, bonded within five at d ≤ 3 / d ≥ 4 | 0.932 / 0.113 | 0.932 (3,595 pairs) / 0.113 (1,600). Fails on the second bound |
| P3: tie-free shortcut share, constraining / monotone with a cycle | 0.2025 / 0.1024, difference 0.100 [0.066, 0.131] | 0.2025 / 0.1024, difference 0.100 [0.067, 0.132] |
| P4: constraining excess slope over level | −0.001 [−0.005, 0.003], hold | −0.001 [−0.005, 0.003], hold (852 families) |

**The classification is as described.**
- **Constraining.** Some SELF definition, with SELF read as its holding knot on the first three ports, allows on its ports less than
  that knot does.
- **Tied.** At most two complementary pairs remain on the first three ports.

**One note on the knot variant.** By the 16 complement-closed relations on three ports, an untied constraining definition acts on its
ports as a knot with one port flipped: a three-pair relation that does not contain the holding knot's. A tied one forces ties at every
level, which the tie-free measures exclude, as the pre-registration says.

## 2. Is P3 driven by a few families?

**No.**
- **Breadth.** 432 of the 960 constraining families have a tie-free shortcut, against 89 of the 395 monotone families with a cycle
  (45% against 23%).
- **Concentration.** Each stratum's top tenth of families holds a large share of its shortcuts: 53% for constraining and 77% for
  monotone with a cycle.
- **A symmetric trim.** Removing each stratum's top tenth, by shortcut share, leaves the difference at 0.084 [0.066, 0.102].
- **Splits.** It holds within both variants (knot 0.091, direct 0.090) and among untied (0.104) and tied (0.087) constraining families.

## 3. The uniform pair as a distance control (P4)

For each nested pair, the census draws up to 40 random starts in a living uniform pattern of the same n and m. It takes a pair at the
same steps apart when one exists, and otherwise records "not found". The pair is then left out of the excess.

| Steps apart | Uniform pair found | Not found |
| --- | --- | --- |
| d ≤ 3 | almost always | 34 pairs |
| d = 4 | 1,175 | 559 (32%) |
| d = 5 | 406 | 587 (59%) |
| d = 6 | 180 | 492 (73%) |
| d ≥ 7 | 205 | 1,226 (86%) |

**Why it matters.** Uniform patterns of the same size have small diameters. So the excess slope over level uses few deep, far pairs:
1,850 of the 15,894 constraining reachable pairs are left out, mostly the far deep ones. One random pair per nested pair adds noise,
not bias. But the pairs that survive at deep levels are those at the distances a uniform pattern has. So P4's "hold" (−0.001) says
the excess does not change with level where a uniform pattern can be compared. It does not speak for the far deep pairs, which is
where "dies with level" would show.

**The raw slope** (−0.013 [−0.017, −0.010]) does fall with level. The note reports it, which fits.

## 4. Scope and the language

**Selection.** Families with at most 60 distinctions at the largest depth up to 12 and with levels to at least 4 are mostly chain-like.
The note reports keep rates and scopes its claims to them, as frozen.

**What the language settles.** The pre-registration states the settled parts:
- the steps are set by the substitution;
- a pattern with no cycle has L = d + 2, the control;
- ties are forced under a tied port relation;
- monotone depths keep the top's relation.

Unlike SHORT-DESC, the tests here are not met by construction. P3 compares constraining with monotone families that have a cycle, and
the difference survives the symmetric trim and the splits. One case is near-trivial and correctly counted as a ruler, not a shortcut:
a top distinction passed down as an argument to every level is one step from every level (d = 1, L = 3).

**Known against new.** One-dimensional transfer is the known mechanism; that is the frame for "bonded within five" falling off with
steps in monotone families. The strata contrast and the level profiles are new data. Nothing is proved.

## Fixes (both Not a block)

1. **P4's control.** Say that the uniform pair is missing for 32% of pairs at d = 4, rising to 86% at d ≥ 7, so the excess slope rests
   on pairs at distances a uniform pattern has, and 1,850 deep constraining pairs are left out. 'Hold' is scoped to them.
2. **P3's breadth.** Add that 45% of constraining families against 23% of monotone families with a cycle have a shortcut, and that the
   difference survives a symmetric trim of each stratum's top tenth (0.084 [0.066, 0.102]).

## Files

`ref_nest.py` → `result_nest.json`.
