# Referee report BREAK-EDDIES-001-R1 (own growth, own recurrences)

**Verdict: the family claim is confirmed; Block on one reading, the short loops; one Narrowing on the explosive kind.**
- **The counts and the rates are right.** The referee regrew all 131 starts (122 + the referee's 9) with its own engine.
  - **Counts and groups.** On every round both runs reached (129 starts), the counts and the largest groups equal the study's.
  - **Recurrences.** Its own exact Berlekamp–Massey finds 118 rational starts (116 of the 122, and 2 of the 9). Their dominant
    factors are the study's in all 118.
  - **The family.** Every one of the 118 rates is a rate of the catalogue's family.
- **The cancelled factor (the owner's first point) is right in substance.**
  - **The identity holds:** x⁷ − (1 + x)² = (x² + x + 1)(x⁵ − x⁴ + x² − x − 1).
  - **The reading is unique:** y⁵(1 + y)² is the only family member with that dominant factor.
  - **But "a factor the counts cancel" fits only 6 of the 23.** In the other 17, x² + x + 1 is in the counts' minimal recurrence. The
    frozen reader dropped it because it kept only the irreducible factor with the largest root.
- **Growth from a stage is growth of that stage taken as a start (the second point).** This holds exactly in the referee's engine,
  by its structure and on all 369 tests (123 starts × s = 1, 2, 3; 8 rounds each). The same check serves JUNCTION-MAP's gate G.
- **Block on one reading: the short loops.** "Loops of two and three steps are the commonest", and "70 of 70", do not hold.
  - **The rate cannot fix W.** Eight family members share the plastic number's factor (y²(1 + y), y⁴(1 + y)², y⁵(1 + y)(1 + y + y²),
    y⁵/(1 − y), …). Two share that of y³(1 + y) (it and y⁶(1 + y)²). The post hoc match takes the smallest, but the counts can tell
    them apart.
  - **The counts exclude L ≤ 3 on 30 of the 42 starts.** By their full minimal recurrences:
    - 15 are y⁴(1 + y)² and 8 are y⁵(1 + y)(1 + y + y²);
    - 1 is y⁵/(1 − y) and 4 are y⁶(1 + y)²;
    - 2 hold two loops.
  - **Only 12 starts are consistent with a loop of three steps or fewer.** All 12 hold a first-round group of three, but the counts
    allow a short loop there without showing one.
  - **B6's 70 also counts 28 starts whose loop has five steps** even in the note's own table (the 23 misread starts and the 5 with an
    endless chain).
  - **Section 2 gives the corrected table.**
- **B7 holds on the corrected reading.** "More open places never lengthen the loop" holds on all 86 pairs. Its 15 failures came
  from the misread W.
- **Narrowing: the explosive kind.** "Their largest group grows without bound" rests on the last one or two rounds reached before
  memory ran out (13 → 60; 33 → 178). In F-04 and F-05 the study's own records show the largest group falling from 66 to 2, 3, 4, 5,
  while the counts leap (465, 4,495, 31,465, 169,911). The referee's engine reproduces the explosive shapes only to rounds 5 to 7,
  with the study's counts and groups there, so this check is lighter.

## 1. Regrowth (`job_break.py` under `scripts/longrun.py`; `break_readout.py`; `referee_break.json`)

How each start was grown:
- **The engine.** The referee's own: complete rounds, the fewest counts, GF(2) implication (FRESH-COUNT-R1 / FIRST-KNOT-R1). Starts
  were built by its TOUCH-CENSUS-R1 convention.
- **The limits.** Each start grew in a child process with a 3.5 GB address-space limit, to 60 rounds or 30,000 junctions. The study
  went to 300,000.
- **What was recorded each round:** the counts and the largest group (most parents of one new junction).

| Check | Result |
| --- | --- |
| Starts | 131 (122 of `population.json`, 9 of `population_ref.json`) |
| Counts equal to the study's on every round both reached | **129 of 129** (G-000, the theta, and G-009 have no study counts: over the study's cap) |
| Largest group equal on every common round | **129 of 129** |
| Rational (the referee's exact Berlekamp–Massey, from t0 ≤ 13, holding on every later term with 2L + 4 to spare; 21 to 50 rounds) | **118** (116 + F-00, F-01) |
| Dominant factor equal to the study's | **118 of 118** |
| Rate a member of the catalogue's family (posthoc.py's range) | **118 of 118** |

**The theta (G-000), regrown.** The referee reached round 17 (… 643, 920, 1,352), equal to the study's 10 GB regrowth, with the
largest group 5, 5, 5, 5, 8.

**G-009 (the study's pending start).** The referee's readout reaches round 23:
- **Counts:** 8, 10, 12, 15, 19, 23, 28, 35, 44, 57, 75, 98, 128, 166, 214, 278, 365, 483, 644, 861, 1,148, 1,527, 2,028, 2,726.
- **Largest group:** 2 in round 1, rising to 5 by round 17 and 8 at round 23.
- **Recurrence:** none found within 23 rounds.

## 2. Which W? The rate against the full recurrence

**Why the rate is not enough.** Under the transfer argument, the counts' generating function is P(y) + Q(y)/(1 − W(y)). P and Q
have only powers of 1 − y in their denominators. So every factor of the counts' minimal recurrence other than x − 1 must divide
1 − W, and Q may cancel factors but cannot add them.

**The plastic number's factor x³ − x − 1 divides 1 − W for eight family members.** posthoc.py takes the first of them, y²(1 + y).

**The full recurrences tell them apart.** For example, G-040 (knots 7, 5, 5, 5, 5, 5, 5, 5):
- its counts satisfy c(t) = c(t − 4) + 2c(t − 5) + c(t − 6), the recurrence of W = y⁴(1 + y)², with zero residual on every round;
- c(t) − c(t − 2) − c(t − 3) oscillates and grows (…, 54, 9, −73, −63, 64, 136, −1, −200);
- so W = y²(1 + y) is excluded for it.

| W by the dominant factor (the note's table) | Starts | W by every factor of the minimal recurrence (the smallest family member holding all of them) |
| --- | ---: | --- |
| y²(1 + y) | 36 | **y²(1 + y): 10**; y⁴(1 + y)²: 15; y⁵(1 + y)(1 + y + y²): 8; y⁵/(1 − y): 1; two loops (no single member): 2 |
| y³(1 + y) | 6 | **y³(1 + y): 2**; y⁶(1 + y)²: 4 |
| y⁴(1 + y) | 8 | y⁴(1 + y): 8 |
| y⁵(1 + y) | 9 | y⁵(1 + y): 9 |
| y⁵(1 + y)² | 23 | y⁵(1 + y)²: 23 (x² + x + 1 present in 17, cancelled in 6) |
| y⁵(1 + y)³ | 29 | y⁵(1 + y)³: 29 |
| y⁵(1 + y)/(1 − y) | 5 | the same: 5 |
| y⁵(1 + y + y²) | 1 | the same: 1 |
| y⁵(1 + y(1 + y)²) | 1 | the same: 1 |

**What this does to the note's claims:**
- **"Loops of two and three steps are the commonest" is false.** Only 12 of the 118 starts are consistent with a loop of three
  steps or fewer, and even for those the counts do not show one. A loop of four with two spares (or a cancelled factor) fits them
  too.
- **B6.** All 12 hold a first-round group of three, so B6 holds there. But "70 of 70" counts 28 starts with five-step loops (the 23
  misread starts and the 5 with an endless chain), and 30 that the counts exclude.
- **B7** holds on all 86 comparable pairs under the every-factor reading.
- **"The same pieces."** The new members, y⁴(1 + y)², y⁵(1 + y)(1 + y + y²) and y⁶(1 + y)², are built from the catalogue's
  pieces. So the family claim stands, with the corrected table. The 2 two-loop starts have rates in the family but no single W.

## 3. Growth from a stage (`job_break.py`, the stage test)

**The argument.** The referee's engine reads only the present presentation:
- the junctions' distinctions and who holds them;
- adjacency, meaning that two junctions share a distinction (common neighbours count old junctions too);
- the live junctions, those holding a loose distinction, which in complete rounds are exactly the last round's junctions with fresh
  distinctions, since every loose distinction is taken in the next round;
- the GF(2) span of all junction equations.

A stage taken as a start, with its junction stars and nothing else, has the same state. So the claim follows.

**The test.** For s = 1, 2, 3, the stage was taken as a start and grown 8 rounds beside the continued growth:

| | Result |
| --- | --- |
| Starts with all three tests run | 123 |
| Equal for 8 rounds | **369 of 369** |
| The other 8 | the explosive shapes, whose stage test ran out of time or memory |

## 4. The explosive readouts (the owner's third point)

| Start | Rounds equal (referee / study) | Study's later largest groups | Study's later counts |
| --- | --- | --- | --- |
| F-02, F-03 (two triangles joined twice) | 7 / 9 | 13, 60 | 38, 127, 720 |
| F-04, F-05 (the same, other spares) | 6 / 13 | 13, 66, **24, 2, 3, 4, 5** | 80, 32, 31, 465, 4,495, 31,465, 169,911 |
| F-06, F-07, F-08 (the 3-regular graph) | 7, 5, 7 / 8 | 10; 178; 19 | 44; 225; 128 |
| G-121 (main population, eight knots) | 6 / 9 | 36, 382 | 94, 489, 2,359 |

- **What the referee could check.** Its engine enumerates groups as cliques and cannot pass groups of about 60. So it confirms
  these shapes only to rounds 5 to 7, where counts and groups equal the study's.
- **What the study's own later rounds show.** Leaps in the counts are real, but "the largest group grows without bound" is not what
  F-04 and F-05 show: their groups fall back to 2 to 5 while the counts leap. "Groups merge without bound" is a reading of the last
  round or two before memory, not a finding.
- **G-121 is explosive too** (group 382 at round 9; it entered B4). The answer's list of explosive starts does not name it.

## 5. Not rechecked

- B8, the cluster rule read at stages 0 to 3, was not rerun (the rule is the study's).
- The three fast eight-knot starts (G-118 to G-120) agree with the study's counts and groups to rounds 13 to 15. No recurrence was
  found there either.

## Corrections for the owner (listed, not folded in)

1. **The short loops (Block on that reading).** The table of W and "loops of two and three steps are the commonest" read W from
   the rate alone, which eight family members share for the plastic number and two for y³(1 + y).
   - **The corrected reading.** By the counts' full minimal recurrences, the 36 "y²(1 + y)" starts are 10 y²(1 + y), 15 y⁴(1 + y)²,
     8 y⁵(1 + y)(1 + y + y²), 1 y⁵/(1 − y) and 2 with two loops. The 6 "y³(1 + y)" starts are 2 y³(1 + y) and 4 y⁶(1 + y)².
   - **What it leaves.** Loops of three steps or fewer are consistent with at most 12 starts and are shown for none. "70 of 70"
     becomes "12 of 12 consistent starts hold a group of three". The family claim stands, with the corrected table.
2. **B7 holds** (86 of 86) once W is read from the full recurrence; its 15 failures were the misread W's. **Not a block.**
3. **"Drops a factor the counts cancel"** (B2's reading) holds for 6 of the 23. In 17 the factor is in the counts' recurrence, and
   the frozen reader dropped it. **Not a block.**
4. **The explosive kind (Narrowing).**
   - Say "counts leap and groups jump in the last rounds reached", not "groups grow without bound". F-04 and F-05's groups fall
     back to 2 to 5 while the counts leap.
   - Name G-121 among the explosive starts.
5. **"118 of 122"** (final report) is 116 of the 122, plus 2 of the referee's 9. **Not a block.**

## How the work was split

- **The referee:**
  - read `break_eddies.md`, the pre-registration, `job.py`, `job_ref.py`, `merge.py`, `posthoc.py`, `stagelib.py`, `breaklib.py`
    and the pilot's theta file;
  - wrote `job_break.py` and `break_readout.py`, the latter with its own exact Berlekamp–Massey, sympy factoring over Q, and the
    family listed by exact divisibility, on its FRESH-COUNT-R1, FIRST-KNOT-R1 and TOUCH-CENSUS-R1 code.
- **Read as data:** the starts (`population.json`, `population_ref.json`) and the study's run records (`runs/break-eddies`,
  `runs/break-eddies-ref`).
- **No study code was run.**
- **Where it ran.** Every growth ran under `scripts/longrun.py` within the 16 GB cap, 3 workers, each child limited to 3.5 GB (peak
  9.5 GB). A first launch capped at 150,000 junctions was stopped after 8 cases as too slow; those 8 were regrown at 30,000.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
