# Referee report PLUS-ONE-001-R1 (fresh code, no Codex)

**Verdict: confirmed, with one Narrowing. No Block.**
- **The hit counts reproduce exactly** with the referee's own growth, births, classes, links and dimension reading. On the census the
  rule makes 11,649 matches, 9 misses and no overshoot. On the six-knot sample it makes 148 matches in 149, with no overshoot.
- **Not all ten misses share one shape.** The nine census misses all have the stated shape: two round-1 births from two start knots
  that share a distinction. **The six-knot miss**, the one P1 failed on, **does not**: its two round-1 births come from start knots
  that share no distinction.

## 1. Method

`referee_plus.py` (lighter check, as asked):
- **Growth:** the referee's FIRST-KNOT-R1 engine under the fewest rule.
- **Births, classes, links and the rule,** written from the study's stated definitions:
  - a birth is a new one-parent junction of demand 1 whose parent is not itself one;
  - its partner is the other new junction on the same parent;
  - births sharing a partner form a class, and sibling births are one class of two;
  - two classes are linked when their partners share a neighbour or are neighbours. Neighbourhoods are taken at round 15, as the
    study's code does;
  - the rule takes the largest linked-component sum over the first 15 rounds.
- **Dimension:** the referee's TOUCH-CENSUS-R1 reader (45 rounds, the last 12 read).
- **The study's code** (linked.py, job.py, its census library) was not imported. The six-knot sampler was rewritten from the procedure
  job.py states, with its seeds 50000 to 50399.

## 2. The hit counts

| Part | Referee | Study |
| --- | --- | --- |
| Census, arrangements with a birth and a settled dimension | 11,689 in the current run file: the study's 11,658 plus the 31 of shard 0244, recorded ok after two timeouts | 11,658 |
| Referee dimension equals the census's | **11,689 of 11,689** | |
| Rule matches | **11,680** (11,649 on the study's 11,658; the 31 later ones all match) | 11,649 |
| Overshoots | **0** | 0 |
| Misses, all unlinked with dimension = largest class + 1 | **9** | 9 |
| Linked components | 222 of sizes 1 + 1 (218 without shard 0244) and 4 of sizes 1 + 2, all cliques | 218 and 4 |
| Births with two or more siblings (an ambiguous partner) | 0 | |
| Six knots: outcomes | stall 237; closed 14; dimension 1: 15; dimension 2: 132; dimension 3: 2 | the same |
| Six knots: settled with a birth | **149** | 149 |
| Six knots: rule matches, overshoots | **148, 0** | 148, 0 |

## 3. The shapes of the ten misses

**All nine census misses** (`referee_plus_census.json`) have exactly two births, both in round 1. Their parent start knots share a
distinction (knots 1 and 2, or 2 and 3), as the decision note says.

**The six-knot miss** is seed 50025 (`referee_plus_six.json`): knot sizes 5, 3, 5, 3, 4, 4, with shared distinctions 0–1, 0–3, 0–4,
2–3 (two), 2–5 and 4–5.
- **The births.** It also has exactly two births, both in round 1. Their parents are start knot 1 (three places) and start knot 5
  (four places).
- **The parents share no distinction.** They are three steps apart, 1–0–4–5.
- **The partners cross over.** Each birth's partner sits on a start knot next to the other birth's parent. Junction 8 is on knots 1
  and 4, and 4 touches 5. Junction 7 is on knots 0 and 5, and 0 touches 1.
- **The two partners share no neighbour** at round 15, so the classes are unlinked, as the study finds.
- **A consequence.** The naive repair (link births whose parents are neighbours) would not link this miss at all. That bears on
  direction #1, "the second link": the shape to explain is wider than the one stated.

## Correction for the owner (listed, not folded in)

1. **"All ten have the same shape: two births in round 1 from two start knots that share a distinction"** (decision note, answer
   and final report). True for the nine census misses. The six-knot miss has its two round-1 births at start knots that share no
   distinction (three steps apart), with crossing partners. **Verdict: Narrowing.** The rule's hit counts and P1's failure are
   unaffected. **Not a block.**

## How the work was split

- **The referee** read `plus_one.md`, the pre-registration and the study's code for its definitions, and wrote `referee_plus.py`.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Reproduction

Run from this folder. The census part takes about 1 minute with 20 workers; the six-knot part about 2 seconds.

```sh
../../../.venv/bin/python -B referee_plus.py census > referee_plus_census.json
../../../.venv/bin/python -B referee_plus.py six > referee_plus_six.json
```
