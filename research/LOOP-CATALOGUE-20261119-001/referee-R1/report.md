# Referee report LOOP-CATALOGUE-001-R1 (own growth, tests and search)

**Verdict: confirmed, with one Narrowing. No Block.**
- **The round-weights are exact.** On all 122 catalogue, ring and interface starts, the referee regrew the counts and found them
  equal to the study's.
  - All 74 with a recorded W are annihilated exactly, after a short transient, by num(1 − W)(1 − y)², the denominator the
    transfer argument predicts.
  - The three even rings with a spare are annihilated by the two-loop denominator.
  - This is a stronger check of C2 and R1 than the rate comparison.
- **The listed rates and L values are internally consistent.** Every one is the root of x^(L+1) = x + 1 for its stated L. The ring
  of eight (1.1673) is faster than the ring of five (1.1347) because its knots join two apart, so it acts as two loops of four, as
  the coordinator supposed. The rings of 10 and 12 likewise act as five and six.
- **The three post hoc rescorings are right** (C2, I2, R1).
- **The catalogue entries are minimal.**
- **The 49 rule-eddies grow exponentially, and no sampled non-eddy does.**
- **Part U's starts with meeting groups of three grow as the study says.**
- **The Narrowing: the search treated one class of starts as "no eddy" without growing them, and one of them is an eddy.**
  - **The class.** The catalogue's verdict (`catalogue.rule_verdict`) counts a start outside the cluster rule's scope with no
    loop through distinct blocks as no eddy. Such starts were neither grown nor put in part U.
  - **The eddy.** The referee's exhaustive search to six knots found **two triangles of knots joined by one shared distinction,
    with one spare.** It is minimal and grows exponentially (6, 7, 9, … 1,646 at round 36, ratio about 1.16), yet is classed no
    eddy.
  - **Two more shapes of that class** (two triangles joined by two shared distinctions; a 3-regular six-knot graph, with spares)
    exceed the referee's engine within their first rounds. Their class is not known.
  - **What changes.** "Every minimal eddy up to eight knots that the rule can read is a ring with one extra choice" stands as
    worded, since these lie outside the rule's scope. But part U is not every start the rule could not decide. A minimal eddy
    outside both the catalogue and part U exists at six knots.

## 1. The transfer argument (argued)

The argument for one loop:
- **The unrolled piece is periodic.** It is a bi-infinite chain of copies of the loop's blocks, with finite trees and endless
  chains hanging from it.
- **Counting.** A cluster lies inside less than one period, or crosses k whole periods. The latter contributes W^k times its two
  ends, so the generating function is P(y) + Q(y)/(1 − W(y)); the hanging chains add powers of 1 − y to P and Q's denominators.
- **The rate.** With non-negative coefficients and W(0) = 0:
  - a single power of y gives a constant count per round;
  - otherwise W(1) ≥ 2 (or W has a pole at 1, for an endless chain), so W = 1 has a root y* in (0, 1). That root is the dominant
    singularity, and the rate is 1/y*.
  - A gcd above one among W's exponents would add a periodic oscillation without changing the rate.
- **This is the standard transfer argument**, correct as stated. The referee tested its exact content, the denominator, on
  every start with a recorded W (Section 2).

## 2. loopweight.py's W against growth (the owner's second point; `referee_loop_series.json`)

The method:
- **The growth.** The referee's own engine (complete rounds, the fewest counts, GF(2) implication) regrew every start to the
  study's horizon.
- **W made exact.** Each start's recorded W is a 16-term series. Where its last terms are equal and non-zero, it was read as
  poly + c y^m/(1 − y), the endless chain's form.
- **The test.** Do the referee's counts satisfy, from some round on and for at least 8 rounds, the recurrence of
  num(1 − W)(1 − y)²?

| Starts | Counts equal the study's | With a recorded W | Annihilated exactly | Needing the endless-chain reading |
| --- | --- | --- | --- | --- |
| 5 catalogue entries, 12 rings, 105 interfaces | **122 of 122** | 74 | **74 of 74** | 18 |
| Even rings with one spare (two loops, no W recorded) | (included above) | — | **3 of 3**, by (1 − y^L − y^(L+1))(1 − y^L)(1 − y)², L = n/2 | — |

## 3. The three post hoc rescorings (the owner's third point)

- **C2** (W truncated at 30 terms). The endless chain's series needs its exact tail. With it, every W, the 12 rescored included, is
  exact (Section 2). **Confirmed, and stronger than "agree to 10⁻⁵ at 120 terms".**
- **I2** (`i2_rescore.py`, `referee_loop_i2.json`). Each interface's W was divided by its entry's, as exact power series.
  - **At true loop knots, 56 of 56 factors match the frozen table:** 1 + y, 1 + y, 1 + y + y² and (1 + y)/(1 − y).
  - **The other 8 are hung side knots** that the study's `on_loop` flag marks as loop knots. Their factors are the nested ones,
    for example (1 + y + y²)/(1 + y) for a spare on a hung knot, as the note says. **Confirmed.**
- **R1** (even rings). Their counts satisfy the two-loop recurrence exactly, so their rates are the predicted roots. **Confirmed.**

## 4. The listed rates and L values (the coordinator's question; `referee_loop_roots.json` in the series run)

| Ring with one spare | L | Root of x^(L+1) = x + 1 | Listed |
| --- | --- | --- | --- |
| 8 | 4 (two loops of four) | 1.167304 | 1.1673 |
| 5 | 5 | 1.134724 | 1.1347 |
| 7 | 7 | 1.096982 | 1.0970 |
| 9 | 9 | 1.075766 | 1.0758 |
| 10 | 5 | 1.134724 | 1.1347 |
| 11 | 11 | 1.062169 | 1.0622 |
| 12 | 6 | 1.112776 | 1.1128 |
| 13 | 13 | 1.052711 | 1.0527 |

- **Consistent throughout.** An even ring of 2m knots joins its knots two apart, so its candidate map is two loops of m, and its
  rate is that of L = m. That is why the ring of eight outruns the ring of five, and why the ring of ten equals it.
- **For John's "core libraries" list,** the rate depends on the loop length L, not on the number of knots. Rings of four and six
  feed nothing: four knots make a pair with two common neighbours, and six make two triangles, each joined in one go.

## 5. Minimality and the search (the owner's fourth point)

**The entries' reductions** (`referee_loop_minimal.json`). For each of the five entries, every start one spare place or one knot
smaller was built, with bare sizes plus the remaining spares, and grown 36 rounds. **All 37 reductions are quasi-polynomial; all
five entries are exponential.**

**An exhaustive search to six knots** (`job_search6.py` under `scripts/longrun.py`, `search6_readout.py`,
`referee_loop_search6.json`, `referee_loop_newshapes.json`):
- **The search space.** Every connected simple knot graph on 2 to 6 knots, at bare sizes plus no spare, one spare or two spares:
  3,693 starts, each grown by the referee's engine.
- **Classes:** 1,605 close, 1,913 quasi-polynomial, 13 exponential, 62 explosive; 88 hit the 2 GB case limit and 12 the time
  limit.
- **The sizes are the study's own:** on every minimal fast start the referee's bare sizes equal `catalogue.start`'s.
- **40 minimal fast starts** (counted with their spare placements):

| Shape | Catalogue | Part U (undecided) | The rule (`eddy.eddy`) | The catalogue's verdict | The referee's growth |
| --- | --- | --- | --- | --- | --- |
| ring of five, one spare | yes | — | eddy | eddy | exponential |
| ring of five, a lone knot hung | yes | — | eddy | eddy | exponential |
| the theta (ring of five, a knot on two of its knots) | — | **yes** | unreliable | grow | past the case limit (study: exponential) |
| **two triangles joined by one shared distinction, one spare** | — | — | **outside its scope** | **no eddy (not grown)** | **exponential**: 6, 7, 9, 10, 12, 13, 16, 19, 22, 25, 29, 35, 41, 47, …, 1,219, 1,418, 1,646 at round 36; ratio 1.16 |
| two triangles joined by two shared distinctions, one or two spares | — | — | outside | no eddy (not grown) | past the 2 GB and 3 GB limits in its first rounds: **class unknown** |
| the 3-regular six-knot graph (9 lines), with spares | — | — | outside | no eddy (not grown) | past the limits: **class unknown** |

**What it shows.**
- **The catalogue and part U, between them, miss at least one minimal eddy at six knots.** The catalogue's verdict counts "outside
  the scope with no loop through distinct blocks" as no eddy without growing. The first new shape is such a start, and it feeds
  itself at about 1.16.
- **The two others are open:** the referee's engine cannot grow them within the limits, because its group enumeration explodes
  in their first rounds.
- **The study's wording:** "every minimal eddy up to eight knots that the rule can read" is true as worded. The "undecided" set
  (part U) should include the out-of-scope starts the rule cannot read, and the catalogue's completeness is narrowed
  accordingly.

## 6. The 49 rule-eddies and the non-eddies (`job_eddies.py` under `scripts/longrun.py`, `referee_loop_eddies.json`)

- **All 49 rule-eddies** (parts E and S) regrow to the study's counts. All are exponential: 23 by the quasi-polynomial test, 26
  fast enough to reach the 30,000-junction cap with every recent ratio at least 1.2.
- **Every 8th grown non-eddy** (184): all regrow to the study's counts; 80 close and 104 are quasi-polynomial; **none
  exponential.**

## 7. Part U's starts with meeting groups of three (the owner's fifth point; `job_partu.py` under `scripts/longrun.py`, `referee_loop_partu.json`)

- **What was regrown.** The 34 starts part U's main run records as exponential with a meeting group of three, or with six knots:
  - **32 regrow in full to the study's counts:** 6 exponential and 26 explosive.
  - **The other two** exceed the referee's engine (6 GB) in a round. Grown round by round under a 4 GB limit, they equal the
    study's counts to the last round reached: the six-knot theta to round 18 (… 920, 1,352, 2,258), and an eight-knot start with
    a meeting group of three to round 7, just before the study's jump to 489 and 2,359.
- **So the 33 exponential starts with meeting groups of three are confirmed** as far as the referee's engine reaches. The 1,080
  still pending in the study's own part U rerun were not checked.
- **A note on method.** The referee's first, in-process run of this part held too much memory and was stopped. Every growth since
  has run through `scripts/longrun.py` under the 16 GB cap.

## Corrections for the owner (listed, not folded in)

1. **The catalogue's completeness.** The search treats out-of-scope starts with no loop through distinct blocks as "no eddy"
   without growing them. One is an eddy: two triangles of knots joined by one shared distinction, with one spare, ratio about
   1.16 at round 36. Two further six-knot shapes of that class are of unknown class. Part U is therefore not the whole set of
   starts the rule could not decide. **Narrowing; not a block.**

## How the work was split

- **The referee:**
  - read `loop_catalogue.md`, the pre-registration, `eddy.py`, `loopweight.py` and `catalogue.py`;
  - wrote `referee_loop.py` (series, roots, minimal), `i2_rescore.py`, `job_partu.py`, `early_rounds.py`, `partu_readout.py`,
    `job_eddies.py`, `eddies_readout.py`, `job_search6.py`, `search6_readout.py` and `job_newshapes.py`, on its FRESH-COUNT-R1,
    FIRST-KNOT-R1 and TOUCH-CENSUS-R1 code.
- **Read-only, as the objects under test:** the study's rule (`eddy.eddy`), its catalogue verdict and start sizes
  (`catalogue.rule_verdict`, `catalogue.start`), and its recorded W.
- **Read as data:** the study's starts and counts (`runs/loop-catalogue`).
- **No growth code of the study was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
