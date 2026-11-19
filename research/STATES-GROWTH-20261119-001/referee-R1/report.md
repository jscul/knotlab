# Referee report STATES-GROWTH-001-R1 (own states, own minimal constraints, own growth)

Code shared with MANY-VALUED-001-R1 and DROPPED-JUNCTION-001-R1: `job_states.py` (under `scripts/longrun.py`),
`states_readout.py`, `referee_states.json`.

**Verdict: Block on the not-all-equal headline reading; the parity part is confirmed; A108's "Confirmed" stands for its
statement, but its reach line needs new numbers.**
- **The cut decides the 93%.** `statelib.nae_core` searches minimal constraints only up to one place above the largest knot. Over
  every size, the referee's own computation shows minimal constraints above the cut on 406 of the 2,715 stages.
  - **The saturated share of irredundant stages becomes 79.8% (1,992 of 2,497), not 92.95%.** 329 stages called saturated are not:
    their states satisfy a minimal constraint that is no knot.
  - **The simplest case.** One three-place knot after one round, with knots (0, 1, 2), (0, 3, 4), (1, 5, 6), (2, 7, 8). NAE(3, …, 8)
    is a minimal constraint of its 162 states: if 3 to 8 are all equal, 0, 1 and 2 are forced to the other value, against the
    first knot. Brute force over every subset confirms that it holds and is minimal.
- **So the states-only growth was not states-only.** The cut is read from the presentation, its largest knot. With every minimal
  constraint, M(S) at that simplest stage is admissible: five members, every distinction held twice. The states-only growth would
  then close at once, while the cheapest growth goes on.
  - **C1** ("no disagreement while saturated") is true but empty. At a saturated stage both growths are handed the same
    presentation.
  - **C3** ("undefined only from a triangle or a double touch", 146 of 146) fails with every constraint. 556 trajectories reach an
    undefined stage, and 15 of them start without a triangle or a double touch, the single three-place knot among them.
- **At the study's cut, everything reproduces exactly.** All 2,715 verdicts and redundancy counts equal the study's. The redundant
  stages are never saturated.
- **"Saturated stages cannot collide" holds only for two saturated stages.** The note's own duplicate pair has the states of a lone
  knot, which is saturated. So a saturated stage can share its states with an unsaturated presentation. With every minimal
  constraint, M is a function of the states, and no two saturated stages collide (argued, Section 3).
- **The parity part (D1, D2) is confirmed, more strictly than tested.** The study tested a plain isomorphism; the referee tested
  Whitney's own statement.
  - **The pairs:** 2,802 same-state pairs (the referee's exact renaming search).
  - **Three-connectivity:** 145 have both completed systems three-connected. The referee's own test (no cut of at most two points)
    agrees with networkx on all 2,802.
  - **Whitney:** in all 145 there is an isomorphism of the completed systems that induces the renaming carrying the states.
  - **Overall:** 1,168 of 2,802 (41.7%) are isomorphic as completed systems.

## 1. Minimal constraints, at the cut and in full (parts B; `minimal_nae` in `job_states.py`)

**The method, independent of the study's code:**
- **Invalid sets.** A set is invalid when it lies inside a state or inside its complement. All invalid sets are found by a
  down-closure over all 2ⁿ sets.
- **M(S).** The minimal valid sets of two or more distinctions, of every size.
- **The cut.** "At the cut" keeps those of at most one place above the largest knot, which is what `nae_core` finds, since
  minimality does not depend on larger sets.

| Verdict (irredundant / redundant) | At the study's cut | Every minimal constraint |
| --- | ---: | ---: |
| saturated | 2,321 / 0 | **1,992** / 0 |
| sharpened | 1 / 209 | 12 / 198 |
| undefined | 175 / 9 | **493** / 20 |
| Saturated share of irredundant stages | 0.9295 | **0.7978** |

- **The study's verdicts and redundancy** are reproduced at its cut on 2,715 of 2,715 stages.
- **Stages with a minimal constraint above the cut:** 406.
- **Saturated at the cut but not in full:** 329.

## 2. The trajectories (part T; the referee's NAE engine: complete rounds, fewest counts, implication by SAT)

- **The census.** All 1,939 arrangements of one to four knots, grown 6 rounds while at most 18 distinctions.
- **With every minimal constraint:**
  - 1,674 trajectories start saturated;
  - 699 meet an unsaturated stage;
  - 556 meet an undefined one, 15 of them from starts with no triangle or double touch.
- **The rank-1 rule fails at the cut's blind spots.** It grows M(S) itself, so it departs wherever M(S) holds a constraint that is
  no knot. The single-knot stage above is one such point.
- **MANY-VALUED's refined rule** grows the unique presentation drawn from M(S). It still equals the cheapest growth on 1,805 of 1,806
  trajectories without a redundant knot (MANY-VALUED-001-R1).

## 3. Saturated stages and collisions (the owner's second point)

- **Argued.** If M(S), with every constraint and so a function of the states, is the presentation, then a renaming carrying the
  states carries M onto M. So two saturated stages with the same states are the same presentation.
- **What it does not give.** A saturated stage and an unsaturated one can share states: a lone knot and the duplicate pair.
- **Wording.** "Saturated stages never collide" should be "no two saturated stages collide".
- **At the cut.** M also depends on the largest knot. The argument then needs both stages to have the same largest knot, or neither
  to hold a minimal constraint between the two cuts.

## 4. Parity: completed systems and Whitney (part D; the owner's third point)

| | Count |
| --- | ---: |
| Distinct presentations; table collisions (the referee's brute-force tables, exact isometry) | 2,644; 2,902 |
| Same-state pairs (exact renaming search, which returns the renaming) | **2,802** |
| Both completed systems three-connected (the referee's test: at least four points, no cut of one or two points) | **145** (networkx agrees on all 2,802) |
| … an isomorphism of the completed systems inducing the renaming of the lines (Whitney's statement) | **145 of 145** |
| Plain isomorphism of the completed systems, all pairs (the study's test) | 1,168 (41.7%) |

- **How the completed system is built.** Junctions and 'out' are the points, and each distinction is a line; a loose distinction is
  a line to 'out'. This is right: 'out''s equation is the sum of the others, so the junction equations span the completed system's
  cut space, and the parity states are its cycle space.
- **"Never visible".** "Which distinctions are loose is never visible in the states" holds wherever another point can be dropped to
  give an admissible presentation. A single knot has only one presentation.

## 5. On A108's grading

- **Its statement is existential:** two presentations with the same allowed states can grow differently. The duplicate pair, the
  parity pairs and MANY-VALUED's non-minimal support show it. So "Confirmed" is right for the statement.
- **Its reach line needs new numbers.** The line reads: "93% of small irredundant stages … they part only at redundant knots and
  where a triangle or a double touch admits two presentations". With every minimal constraint, the knots are the minimal
  constraints on 79.8%, and undefined points also arise from a single knot.
- **What survives** is MANY-VALUED's form: drawn from M(S), the presentation is unique up to renaming at every point tested, and the
  dependence comes from redundant knots and non-minimal supports.

## Corrections for the owner (listed, not folded in)

1. **The 93% and the states-only growth (Block on that reading).**
   - **The figure.** The saturated share counts minimal constraints only up to one place above the largest knot, a cut read from
     the presentation. With every minimal constraint, a function of the states, it is 79.8% (1,992 of 2,497). 329 stages are not
     saturated, beginning with one knot after one round.
   - **C3** fails with every constraint (15 of 556 undefined trajectories start without a triangle or a double touch).
   - **The rule.** The rank-1 states-only growth is defined with the cut. The refined rule of MANY-VALUED is the states-only growth
     that survives.
2. **"Saturated stages never collide"** should be "no two saturated stages collide". The duplicate pair shares its states with a
   saturated lone knot. **Not a block.**
3. **C1 is true by construction**, since both growths are handed the same presentation. It is not evidence. **Not a block.**
4. **A108's reach line:** 93% → 79.8% with every constraint, and the undefined points are not only triangles and double touches.
   The status stays Confirmed. **Not a block.**

## How the work was split

- **The referee:**
  - read `states_growth.md`, the pre-registration, `statelib.py`, `job.py` and `merge.py`;
  - wrote `job_states.py` (minimal constraints by down-closure, verdicts, its own presentation search, renaming search,
    three-connectivity, the Whitney test) and `states_readout.py`, on its NAE-GROWTH-R1, FIRST-KNOT-R1 and TOUCH-CENSUS-R1 code.
- **Read as data:** NAE-GROWTH's part-B stages, and the study's records (`runs/states-growth`).
- **No study code was run.**
- **Where it ran.** Everything ran under `scripts/longrun.py` within the 16 GB cap, 3 workers (peak 4.1 GB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
