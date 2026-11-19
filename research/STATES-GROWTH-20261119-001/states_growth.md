# A growth that reads only the allowed states

Epic `STATES-GROWTH-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead (taking `NAE-GROWTH-20261119-001#1`),
challenging A108. Goals G17 and G1. **Refereed:** report [R1](referee-R1/report.md), a **Block** on the not-all-equal headline
reading (the 93% and the rank-1 rule), the parity part confirmed, three corrections that are not blocks; folded in on 19 November
(see Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `86e8ac334` at 11:24 UTC after a pilot (disclosed).
- The run went through the shared runner (`STATES-GROWTH-B1`, `runs/states-growth`, 36 cases), all ok by 11:27 UTC.
- Code: [statelib.py, job.py, merge.py](../../experiments/STATES-GROWTH-20261119-001B/STATES-GROWTH-20261119-001B-E001_states/).
- Results: [results.json](../../artifacts/STATES-GROWTH-20261119-001B/STATES-GROWTH-20261119-001B-E001_states/results.json).

**Words.**
- M(S) is the set of minimal not-all-equal constraints the allowed states satisfy: the minimal sets of distinctions on which no
  allowed state is constant. It depends only on the states.
- The **states-only growth** grows one round of the cheapest growth on M(S) whenever M(S) is an admissible presentation, and is
  undefined otherwise.
- A stage is **saturated** when M(S) is its presentation exactly, counted with repeats; **sharpened** when M(S) differs but is
  admissible; **undefined** otherwise.

## The answer

**In the owner's terms.**
- **Under not-all-equal: on four small stages in five (corrected after referee R1, a Block on the first reading).**
  - With every minimal constraint, of every size, the allowed states fix the presentation on 79.8% of small stages without a
    redundant knot (1,992 of 2,497): the minimal constraints they satisfy are exactly the knots.
  - The first version said 93% (2,321). Its search stopped one place above the largest knot, a cut read from the presentation, so
    the reading was not states-only. 329 stages it called saturated are not. The simplest is one knot after one round: knots
    (0, 1, 2), (0, 3, 4), (1, 5, 6), (2, 7, 8), whose 162 states satisfy the minimal constraint NAE(3, …, 8). If 3 to 8 were all
    equal, 0, 1 and 2 would all be forced to the other value.
  - Where a stage is saturated, the cheapest growth reads only the states. "The two growths agree while the stages stay saturated"
    (C1) is true by construction, since both are handed the same presentation; it is not evidence.
  - The rank-1 rule, growing M(S) itself, fails wherever M(S) holds a constraint that is no knot. At the one-knot stage above it
    would close at once while the cheapest growth goes on. The states-only growth that survives is `MANY-VALUED-20261119-001`'s:
    grow the presentation drawn from M(S), unique up to renaming at every point tested.
- **Where they part, and why.** At the cut, in two places, both things the allowed states cannot see (with every minimal
  constraint there is a third: a minimal constraint that is no knot, as above):
  - **A redundant knot,** one whose constraint the others already imply: all 218 such stages. The duplicate pair (two knots on the
    same three distinctions) has the same states as one lone knot. The cheapest growth closes it and the states-only growth grows it.
  - **Several presentations for the same states.** The advisor's example has four "stars" and four "triangles" (the literature's
    K4), with 18 states, 8 minimal constraints and two irredundant presentations. There the states-only growth is undefined: it
    would have to choose.
  - At the cut, every one of the 146 trajectories that reached that point started from an arrangement with a triangle of knots
    (three pairwise touching) or two knots touching twice. With every minimal constraint this fails (C3): 556 trajectories reach an
    undefined stage, and 15 of them start with neither, the single three-place knot among them.
- **Under parity: "loose" cannot be read from the states** (wherever another point can be dropped to give an admissible
  presentation; a single knot has only one). Add to a presentation the implied junction that holds every loose
  distinction, giving the completed system. The states fix only that system's cycle matroid, so which junction is "dropped", and
  hence which distinctions are loose, is a choice the states cannot see.
  - **Whitney's theorem holds.** Every one of parity's 145 same-state pairs whose completed systems are three-connected has the same
    completed system, with a different junction dropped (Whitney 1933). The referee confirmed it in Whitney's stricter form: an
    isomorphism of the completed systems inducing the renaming of the lines, 145 of 145.
  - **Most pairs are twists.** Overall only 42% of the 2,802 pairs are the same completed system. The rest also differ by twists at
    two-point cuts.
- **For the owner's premise that distance is the only information.** Distances are read from the allowed states. So wherever the
  states fix the presentation (79.8% of small not-all-equal stages, with every minimal constraint), the growth reads nothing but
  what distance can carry. Under parity it reads a choice beyond the states wherever another dropped junction is admissible.
- **A108 is confirmed, and its reach is measured.** The cheapest growth does read the presentation. Under not-all-equal, with every
  minimal constraint, the knots are the minimal constraints on 79.8% of small irredundant stages, and the dependence comes from
  redundant knots and non-minimal supports (`MANY-VALUED-20261119-001`'s form, which survives the referee). Under parity it
  matters wherever another junction can be dropped.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| A1 | the K4 example and the duplicate pair replay | **held** | 18 states, 8 minimal constraints, 2 presentations; 1 |
| B1 | saturated share of irredundant stages in [0.85, 0.92] | failed | at the cut 0.9295 (2,321 of 2,497); with every minimal constraint 0.7978 (1,992), further outside (referee R1); every redundant stage unsaturated |
| C1 | the two growths agree while every stage so far is saturated | **held**, by construction | 0 disagreements in 1,939 trajectories; both growths are handed the same presentation there, so this is not evidence (referee R1) |
| C2 | every disagreement follows an unsaturated stage | failed as worded | 17 disagreements follow a saturated states-only stage, each after the trajectories had already parted at an unsaturated one; the first disagreement always follows an unsaturated stage (C1) |
| C3 | (risky) undefined only from a triangle of knots or a double touch | held as scored at the cut; **fails** with every minimal constraint | 146 of 146 at the cut; with every constraint 541 of 556, the 15 others from starts with neither, the single knot among them (referee R1) |
| D1 | (Whitney) three-connected same-state pairs are the same completed system | **held** | 145 of 145, also in Whitney's stricter form (referee R1) |
| D2 | at least half of parity's same-state pairs are the same completed system | failed | 42% (1,168 of 2,802) |

4 of 7 held as scored. With every minimal constraint C3 fails, and C1 holds by construction (referee R1).

## Why it holds

- **No two saturated stages collide** (corrected wording; the first version said "saturated stages never collide"). If M(S),
  computed with every constraint and so a function of the states, is the presentation, then the same states give the same M(S),
  hence the same presentation. A saturated stage can still share its states with an unsaturated one: the duplicate pair has the
  states of a lone knot. At the cut the argument also needs the two stages to have the same largest knot. C1 follows by
  construction.
- **A redundant knot is invisible.** Its constraint holds on the states of the others, so M(S) cannot contain it, or contains it once
  where the presentation has it twice.
- **Parity (the advisor's statement).** A presentation in which every distinction sits in at most two junctions is a graph. Its
  allowed states are the cycle space of the completed system, which fixes the cycle matroid and nothing more. Whitney's
  2-isomorphism theorem then says that two such graphs differ by twists at two-point cuts, and are the same graph when
  three-connected.

## Known results, and what this adds

- **Known, cited once.** Whitney's 2-isomorphism theorem (Whitney, *Amer. J. Math.* 55, 1933); cycle spaces and cycle matroids.
- **What this adds.** A states-only version of the cheapest growth under not-all-equal, and the measurement of where the knots
  are the states' minimal constraints: 79.8% of small irredundant stages with every constraint (the first version's 93% was at a
  cut read from the presentation). The surviving states-only rule is `MANY-VALUED-20261119-001`'s. And the parity case, where
  looseness is a choice beyond the states.

## Limitations

- M(S) is computed by brute force over the allowed states, so stages have at most 15 to 18 distinctions, and trajectories run at
  most 6 rounds from starts of up to four knots.
- Constraints were searched up to one place more than the largest knot. That cut decided the headline figure: with every
  constraint the saturated share is 79.8%, not 93% (referee R1).
- Where the states-only growth is undefined, no choice rule was tried. The many-valued growth, all outcomes over all presentations,
  is the advisor's rank 2 and is left as a direction.

## Referee

Report [R1](referee-R1/report.md), 19 November 2026, by the coordinator's background referee thread, with its own states, its own
minimal constraints by down-closure over every subset, and its own growth. No study code was run.
- **Confirmed.** At the study's cut, all 2,715 verdicts and redundancy counts. The parity part: 2,802 same-state pairs, 145 with
  both completed systems three-connected, all 145 in Whitney's stricter form, 1,168 plain-isomorphic. The completed system's
  construction.
- **Folded in the same day**, logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`. I checked the simplest counterexample by
  brute force before folding: 162 states, and NAE(3, …, 8) is a minimal constraint with every proper subset failing.
  - **Block, on the not-all-equal headline reading.** The 93% and the rank-1 states-only growth rest on a search cut read from the
    presentation. With every minimal constraint the saturated share is 79.8% (1,992 of 2,497); 329 stages called saturated are not;
    C3 fails (15 of 556 undefined trajectories from starts with neither a triangle nor a double touch); the rank-1 rule departs
    wherever M(S) holds a constraint that is no knot. What survives is `MANY-VALUED-20261119-001`'s refined rule.
  - **Not blocks.** "Saturated stages never collide" is "no two saturated stages collide". C1 is true by construction and is not
    evidence. A108's reach line now reads 79.8% with every constraint, and undefined points also come from a single knot; its
    status stays Confirmed.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), at the design stage, before the freeze. This answer stayed within its text.
- **What held.** The rank-1 definition, the K4 example (A1, exact), the parity reading through Whitney (D1, exact), and its guess of
  an 85–95% saturated share (0.93 at the cut; 0.80 with every minimal constraint, outside its range too).
- **What failed.** Its local forcing criterion (pilot). D2's "at least half re-choices" was my own reading of its account, and twists
  are the majority.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a growth that reads only the allowed states | **Status:** Partially successful (4 of 7 held as scored; corrected after referee R1, a Block on the not-all-equal headline) | Under not-all-equal the states fix the presentation on 79.8% of small irredundant stages with every minimal constraint (93% at the first version's cut); the rank-1 rule fails where a minimal constraint is no knot, and MANY-VALUED's refined rule survives; under parity looseness is a choice beyond the states (Whitney, confirmed) |
| Local direction: A108 | Confirmed, reach measured (corrected) | The growth reads the presentation; under not-all-equal through redundant knots and non-minimal supports, under parity wherever another junction can be dropped |
| Broader exploration: the growth and the canonical reading | Known alternatives | States-only where the presentation is fixed; a choice, or many-valued growth, elsewhere |
| Long-term goal: G1 | Capability gained | Where distance (read from states) is enough for the growth, measured |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A transfer between kinds of junction for the break shapes (`JUNCTION-MAP-20261119-001#1`), after BREAK-EDDIES' referee verdict | 3/3 | 2/3 | as there | Selected · awaiting go-ahead and the verdict |
| 2 | The many-valued states-only growth where it is undefined: all outcomes over all presentations of the same states | 2/3 — what a states-only growth must give up | 3/3 — the presentations are enumerable on small stages | enumerate the presentations at the 146 undefined points → stop at whether their outcomes agree in count | Alternative · deferred |
| 3 | Parity's states-only growth over the dropped junction: does any dropped-junction choice reproduce the catalogue's eddies? | 2/3 | 2/3 | on the rings, try every dropped junction → stop at the set of rates | Alternative · deferred |

## Final report as sent (2026-11-19 11:30 UTC)

**Outcome:** Under not-all-equal, a growth that reads only the allowed states exists almost everywhere small, and wherever it exists it is the cheapest growth. On 93% of small stages without a redundant knot, the minimal constraints the states satisfy are exactly the knots. Along every trajectory from every arrangement of up to four knots (1,939), the two growths agree at every round while that holds. Under parity, which distinctions are "loose" is never visible in the states: it is a choice of which junction to drop, as Whitney's theorem says. A108 is confirmed, with its reach measured. 4 of 7 frozen predictions held. Closed, referee pending.

- **Where the two growths part, exactly two things the states can't see:**
  - **a redundant knot,** one already implied by the others (all 218 such stages). Two knots on the same three distinctions have the states of one knot, so the cheapest growth closes them and the states-only growth grows them;
  - **several presentations for the same states.** The advisor's example (four "stars" and four "triangles" of the literature's K4) has 18 states and two presentations. There a states-only growth would have to choose. All 146 trajectories that hit this started from a triangle of knots or a double touch.
- **For your distance premise.** Distances are read from the states. So on 93% of small not-all-equal stages the growth reads nothing distance can't carry. Under parity it always reads a choice beyond them.
- **Parity in numbers.** Whitney holds on all 145 three-connected same-state pairs (same completed system, a different junction dropped). Overall only 42% of the 2,802 pairs are that simple; the rest also differ by twists at two-point cuts.
- **Failures:**
  - the saturated share was 0.93 against a predicted ceiling of 0.92;
  - my "every disagreement follows an unsaturated stage" was worded too broadly. The first one always does, and 17 later ones come after the paths had already parted;
  - pure re-choices are 42%, not a majority.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a growth that reads only the allowed states | **Status:** Partially successful (4 of 7 held) | Exists and agrees wherever the states fix the presentation (93%); parts exactly at redundant knots and at triangles or double touches; parity's looseness is beyond the states |
| Local direction: A108 | Confirmed, reach measured | The growth reads the presentation; under not-all-equal that matters at two named configurations, under parity everywhere |
| Broader exploration: the growth and the canonical reading | Known alternatives | States-only where the presentation is fixed; a choice, or a many-valued growth, elsewhere |
| Long-term goal: G1 | Capability gained | Where distance (read from the states) is enough for the growth, measured |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A transfer between kinds of junction for the break shapes, after BREAK-EDDIES' referee verdict | 3/3 | 2/3 | as in JUNCTION-MAP | Selected · awaiting go-ahead and the verdict |
| 2 | The many-valued states-only growth where it is undefined (all presentations' outcomes) | 2/3 — what a states-only growth must give up | 3/3 | enumerate the presentations at the 146 undefined points → stop at whether their counts agree | Alternative · deferred |
| 3 | Parity over the dropped junction: does any choice reproduce the catalogue's eddies? | 2/3 | 2/3 | on the rings, try every dropped junction → stop at the set of rates | Alternative · deferred |

**Corrections:** none. **Goals:** G1 and G17 checkpoint (capability gained). **Assumptions:** A108 moved to Confirmed (reopenable), with a history line on its measured reach. **Basket:** `NAE-GROWTH-20261119-001#1` taken. **Advisor:** Fable 5.2, at the design stage. This time its answer stayed within its text. It gave the states-only rule, the K4 example (replayed exactly) and the parity reading through Whitney (held on all 145), and guessed the saturated share at 85–95% (it was 93%). Its local "forcing" test didn't predict saturation.

**Referee hand-off.** The decision note is `research/STATES-GROWTH-20261119-001/states_growth.md`; the prior-work line is in the pre-registration (objects-gate passes). Please check:
- `statelib.nae_core` (the search cap is one place above the largest knot);
- that saturated stages can't collide;
- the completed-system graphs and the three-connectivity test behind D1.
