# Counting through a shared distinction

Epic `SHARED-COUNT-20261111-001` (sub-goal B148, re-posed for overlapping bases; G15 with G16; program learning), 2026-11-11, at the
coordinator's go-ahead after the owner restarted the learning line with a new direction: bases where knots overlap freely. Pre-registered
in [preregistration.md](preregistration.md), frozen in commit `6c391343f` before any run. Proof family: `proofs/SHARED-COUNT-20261111-001A/`.

## The answer

**Through one shared distinction, the learner learns to count five held distinctions; with two shared distinctions, seven was out of
reach in the time allowed.**

- **The bases.** A copy is the drawn knot pattern (2, 0, 4) (the literature's torus, drawn): 8 distinctions, 8 not-all-equal knots,
  whose tightest class forces distinction 5 to the sum mod 2 of distinctions 0, 1 and 4. J2 makes copy 1's read distinction the same
  distinction as an input of copy 2; J3 chains three copies the same way. The shared distinctions are hidden: never held, never read.
- **They count, by definition (exact).** J2 forces its read distinction to the sum mod 2 of five held distinctions, and J3 of seven,
  in exactly one class combination of 16 and of 64: every copy in its tightest class. That follows from the definition (the two sums
  add through the shared distinction); the check confirms it.
- **The count of five is learned (computed, frozen).** The unchanged learner learned and held it in 10 of 10 runs on J2, and all 30
  writes (the count, its negation, the count again) held after a disturbance, with no false stop. The first count took a median of
  199,200 steps, about fifteen times the 13,400 that one copy alone took (`LEARN-PARITY-20261111-001`).
- **The count of seven was not learned in time.** All ten J3 runs reached their 120-minute cap before their first stop and were
  dropped by rule, so P7 failed as frozen. Whether more time would have been enough is not known.
- **Against flat composition.** The same two copies grown together on a drawn knot pattern (the literature's genus-2 surface, drawn)
  compute no map of held distinctions at all, because the second copy unties the six distinctions the first one's count was tied to
  (`PARITY-FIVE-20261111-001`, exact). Sharing the read distinction by identity leaves nothing to untie.

## What the construction drops

The learning line's earlier bases are drawn knot patterns: every knot holds three distinctions, every distinction lies in three knots,
and the whole is one drawing, a two-coloured triangulation. J2 and J3 keep the not-all-equal knots, three distinctions in each knot, and
each copy's co-knotted pairs as they were. They drop two things: each shared distinction lies in six knots, three from each copy, and
there is no single drawing, only one per copy (drawn, the two surfaces share the one triangle that stands for the shared distinction,
so their union is not a surface). The learner still reads each copy's dissonance with that copy's own faces (A66); a base with no
drawing at all is the next step (B153).

## What is known, and what is proved and computed

| Claim | Evidence class |
| --- | --- |
| On finite bases with hidden distinctions, the maps of held distinctions are exactly the self-dual maps | known (Post's lattice: not-all-equal is a base of the complement-closed co-clone; Böhler, Reith, Schnoor and Vollmer 2005), with theorem D of `IN-OUT-20261110-001` |
| J2 and J3 count five and seven held distinctions, exactly where every copy is in its tightest class | settled by definition; confirmed exhaustively |
| The joined harness with one copy replays `LEARN-PARITY-20261111-001`'s first run exactly | computed, exact replay |
| The count of five is learned and held on J2 in 10 of 10 runs, 30 of 30 writes | computed, frozen |
| The count of seven is not learned on J3 within 120 minutes per run (0 of 10) | computed, frozen |
| No prior work found on a learner of this kind learning parity of five or seven inputs | prior-work check, recorded in the pre-registration |

## Against the pre-registration

- V1, R and P5 held as predicted, R in exactly the predicted class combinations.
- P7 failed: every run hit the cap. I called P7 uncertain. The runs saved their outcomes only, not their progress, so where each run
  stood at the cap is not known (B154).
- A word in the pre-registration and in A66 was wrong: they called each copy a two-fold weave. A copy is a drawn knot pattern; a
  two-fold weave has every co-knotted pair in two knots, the knots-alone line's object. The claims are unchanged, and A66's statement
  now says drawn knot patterns (logged in `docs/CORRECTIONS.md`).

## What it changes

- **An overlap does what flat composition could not.** Two counting copies grown together on one drawing count nothing; the same two
  copies sharing a distinction count five held distinctions, and the learner learns it. That is the first answer to the question put to
  this line: here, an overlapping base both computes and learns what the drawn composition does not. It does not show that no drawn
  knot pattern counts five; none of the lattice ones up to 24 distinctions does (`PARITY-FIVE-20261111-001`), and the rest are open
  (B150).
- **The cost grows fast with copies.** One copy: 13,400 steps. Two: 199,200. Three: more than two hours a run.
- **Sub-goal B148, composing learned parity.** The count of five came from learning the composite whole, not from wiring two separately
  learned copies; B148 stays open for that.

## Assumptions

A66 added (a base made of copies keeps each copy's own faces in the dissonance); its statement corrected to drawn knot patterns. Relied
on: A20, A21, A46, A47, A49, A50, A52, A58.

## Corrections

One, Not a block: the pre-registration and A66 called each copy a two-fold weave; it is a drawn knot pattern.

## In the owner's words

Two of the counting rings, glued flat, go quiet. Let them share one distinction instead, the answer of the first ring becoming a
question of the second, and the pair counts five, and the learner, feeling only its own tension, finds that out from examples, ten
times of ten. A third ring made the count of seven too slow to find in two hours.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: counting through a shared distinction (B148, re-posed) | **Status:** Partially successful | five learned and held 10 of 10; seven not learned within the cap |
| Local direction: learning counts on bases with shared distinctions | Continue | the overlap works where flat composition failed; the cost per copy is the obstacle |
| Broader exploration: learning program | Known alternatives | a dissonance needing no drawing, where the time goes at seven, learning what to share, endless chains |
| Long-term goal: G15 Learning: a point in a learned knot pattern | Capability gained | the first learned map on a base that is not a drawn knot pattern |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A learner whose dissonance needs no drawing (B153; challenges A66) | 3/3 — Major | 2/3 — Testable | the credit learner with dissonance from violated knots alone, frozen, run on J1 and J2 against this epic's results, then on a base with no drawing → learning that needs no faces, or what the faces were doing | Selected · started |
| 2 | The count of seven: where the time goes (B154) | 2/3 — Substantial | 3/3 — Ready | J3 with progress saved per probe and a longer cap, and the copies learned one at a time → the count of seven learned, or which copy stalls | Alternative · deferred |
| 3 | Learning which distinction to share (B155) | 3/3 — Major | 1/3 — Exploratory | copies unshared, with a learner move that makes two distinctions one → a learned overlap, or no move that does it natively | Alternative · deferred |
| 4 | An endless chain of counting copies (B156) | 2/3 — Substantial | 1/3 — Exploratory | an endless chain of copies sharing distinctions, the owner's infinite bases, read on finite windows → what an endless chain counts, or no native reading | Alternative · deferred |
| 5 | Five-input parity on drawn knot patterns that are not lattice ones (B150) | 2/3 — Substantial | 2/3 — Testable | as recorded | Alternative · deferred |

- **#1:** payoff 3/3 because the owner's bases have no drawing, and every learner so far reads its dissonance through faces; without
  this step learning cannot run on them. Concreteness 2/3: the change is one term of the dissonance, but the credit learner's cooling also
  reads faces, so it is a new frozen learner; the main uncertainty is whether the faces did essential work. Resource bound: the J1 and J2
  runs of this epic at the same caps; the bases with no drawing are chosen and frozen before any run.
- **#2:** payoff 2/3, it decides whether the cost or the learner stops the count of seven; concreteness 3/3, the code exists.
- **#3:** payoff 3/3, an overlap the learner makes itself would be native; concreteness 1/3, no such move is defined yet.
- **#4:** payoff 2/3, it touches the owner's infinite bases; concreteness 1/3, no reading of an endless chain is defined.
- **#5:** as recorded at `PARITY-FIVE-20261111-001`.

**Corrections:** one, Not a block (the copies called two-fold weaves; they are drawn knot patterns).
**Goals:** G15 checkpoint (capability gained, with G16); sub-goal B148 taken in part (the count of five through a shared distinction;
wiring separately learned copies stays open); B153 and B155 added as sub-goals, B154 and B156 to the backlog.
**Assumptions:** A66 added; its statement corrected to drawn knot patterns.
**Basket:** B153 (selected, started), B154, B155, B156, B150, B151, B130.

## Final report as sent

Posted in the thread on 2026-11-11 (23:10 UTC), exactly:

**SHARED-COUNT is closed: an overlap computes, and is learned, where the drawing failed.** I made two copies of the 8-distinction counting pattern (2, 0, 4) share one distinction, so the distinction the first copy reads is an input of the second. The pair then counts five held distinctions. That holds by definition, and an exact check confirms it: only when both copies sit in their tightest class. The unchanged learner learned and held that count in 10 of 10 runs. All 30 writes (count, negation, count) held after a disturbance, with no false stop. It took about 15 times the steps of one copy. The same two copies grown together on one drawing count nothing (PARITY-FIVE).

- **What the construction drops** (the coordinator asked me to state this exactly): the earlier bases are drawn knot patterns, with every distinction in three knots and one drawing. The shared distinction lies in six knots, and the pair has no single drawing, only one per copy. The knots and each copy's co-knotted pairs are unchanged. The learner still reads each copy's own drawn faces (assumption A66, new).
- **Seven failed as frozen.** On three copies (seven held distinctions), all ten runs reached the 2-hour cap before a first stop. That shows the count isn't learned within two hours, not that it can't be.
- **Known results:** that some base computes every self-dual map is classical (Post's lattice), and the composite counting follows by definition. The learning was the open part. I found no prior work on this kind of learner learning wider parity.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: counting through a shared distinction (B148, re-posed) | **Status:** Partially successful | five learned and held 10 of 10; seven not within the cap |
| Local direction: learning counts on bases with shared distinctions | Continue | the overlap works where flat composition failed; the cost per copy is the obstacle |
| Broader exploration: learning program | Known alternatives | dissonance needing no drawing, seven's cost, learning what to share, endless chains |
| Long-term goal: G15, a point in a learned knot pattern | Capability gained | the first learned map on a base that is not one drawn knot pattern |

**Next step:** Research directions, selected #1, started.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A learner whose dissonance needs no drawing (B153; challenges A66) | 3/3 Major | 2/3 Testable | dissonance from violated knots alone, frozen, on one and two copies against this epic, then on a base with no drawing → learning without faces, or what the faces did | Selected, started |
| 2 | The count of seven: where the time goes (B154) | 2/3 Substantial | 3/3 Ready | J3 with progress saved and a longer cap, or copies learned one at a time | Deferred |
| 3 | Learning which distinction to share (B155) | 3/3 Major | 1/3 Exploratory | a learner move that makes two distinctions one → a learned overlap, or none native | Deferred (sub-goal) |
| 4 | An endless chain of counting copies (B156) | 2/3 Substantial | 1/3 Exploratory | read an endless chain on finite windows → what it counts | Deferred |
| 5 | Five-input parity on non-lattice drawn knot patterns (B150) | 2/3 Substantial | 2/3 Testable | as recorded | Deferred |

**Corrections:** one, Not a block. My pre-registration and A66 called each copy a two-fold weave; it's a drawn knot pattern. Logged, and A66 is reworded.
**Goals:** G15 checkpoint (capability gained, with G16); B148 taken in part (wiring separately learned copies stays open); sub-goals B153 and B155, backlog B154 and B156 added.
**Assumptions:** A66 added (each copy keeps its own drawn faces in the dissonance), status Assumed; B153 challenges it.
**Basket:** B153 (started), B154, B155, B156, B150, B151, B130.

The run is registered in docs/LONG_RUNNING.md and folded in. Starting B153 now.
