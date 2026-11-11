# Parity of five held points

Epic `PARITY-FIVE-20261111-001` (backlog B149, G15 with G16; program learning), 2026-11-11, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md), frozen in commit `95e0c04c3` before any five-input search. Proof family:
`proofs/PARITY-FIVE-20261111-001A/`.

## The answer

**No lattice torus up to 24 points counts five held points, and composing two counting tori loses everything.**

- **Lattice tori (exact).** Of the 421 lattice tori with 3 to 24 points, every class, none has a set of six points whose parity is fixed
  with any five of them free. Only 16 of them count three held points, all with 8 to 18 points; none of the 196 tori with 19 to 24 points
  counts even three. Nothing was dropped.
- **Two tori composed (exact).** The knot sphere K_2 with the 8-point torus (2, 0, 4) grown at each of its two lines (30 points, genus 2)
  counts neither five held points nor three, in any of its 16 classes, though each torus alone counts three.
- **Why (computed after the run).** With one torus grown, six points of the host sphere are tied together in every class, a wire, and the
  torus forces that wire to the parity of its three inner points. With two, nothing is tied and no set of points has a fixed parity in any
  class: the second torus unties the wire the first used.
- **Larger tori (undecided).** The pre-registered extension to 25 to 32 points ran into its 60-minute cap and was dropped by rule.
- **Learning** was not run: it was to run only on a five-input parity space.

## What is known, and what is proved and computed

| Claim | Evidence class |
| --- | --- |
| Parity of an even number of held points never occurs (theorem D) | proved (`IN-OUT-20261110-001`) |
| A five-input parity space computes three-input parity, so genus 0 is excluded for it unless P = NP | proved by restriction, conditional on P ≠ NP (`PARITY-NEEDS-20261111-001`, after Moret 1988 and Lichtenstein 1982) |
| Five-input parity needs at least 32 floor states in its class | proved by counting |
| No lattice torus up to 24 points computes five-input parity; only tori of 8 to 18 points compute three-input parity | exhaustive computation |
| The composed genus-2 space computes no parity map at all | exhaustive computation |
| The second torus unties the host's wire | computed after the run (`after_run.py`) |
| No published bound on how many held points one handle can count, or construction past three, that I know of | literature as stated in the pre-registration; not a search result |

## Against the pre-registration

- I predicted a five-input parity torus at 12 to 16 points: wrong. I predicted the composed space would compute five-input parity: wrong,
  it computes nothing.
- Stage 1b was dropped at its cap. My 15-minute estimate came from one class with few checks, and the check writes each part's results
  only at the end, so the cap kept nothing. It is a fault of the check's design, not a result; it is recorded as B151.
- V1 to V3 held: the harness reproduced `LEARN-PARITY-20261111-001`'s first run exactly, and the three-input tori up to 20 points are
  exactly `PARITY-NEEDS-20261111-001`'s 16.

## What it changes

- **One handle counts three, and in the lattice range no more.** "Not found up to 24 points" is not a bound: it does not show that genus 1
  cannot count five, and it says nothing about non-lattice tori (B150).
- **Composition needs a wire that survives.** Growing a second counting torus is not enough to compose two; it unties the host's wire.
  Sub-goal B148 (composing learned parity) now has a concrete first step: find a host where two grown tori stay wired, that is, where a
  six-point set across both tori has fixed parity with five of its points free.

## Assumptions

None added or changed. Relied on: A20, A21, A46, A47, A49, A50, A52, A58.

## Corrections

None. The composition was pre-registered as expected, not claimed.

## In the owner's words

One ring of eight points counts three into a fourth, but no ring of up to 24 points counts five. Gluing two counting rings onto one sphere
doesn't help: the second ring loosens the wire the first one spoke through, and the whole thing goes quiet.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: parity of five held points (B149) | **Status:** Partially successful | exact: none on 421 lattice tori up to 24 points or on the composed space; the composition's obstacle found; 25 to 32 points undecided |
| Local direction: one torus counting more held points | Practically exhausted | lattice tori stop at three, and at 18 points; only non-lattice tori remain (B150) |
| Broader exploration: learning program | Known alternatives | composing through a wire that survives (B148), non-lattice tori, the probe as a theorem |
| Long-term goal: G15 Learning: a point in a learned knot space | Obstruction learned | counting more needs composition, and the obvious composition unties its wire |

The attempt reached its pre-registered stop (the exact statement that none exists in the range, and what the composed space shows); it
did not find a space that counts five, and it leaves open whether any genus-1 space does.

**Next step:** Research directions — selected: #1 (holding: the owner paused new work after this epic)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A host where two counting tori stay wired (sub-goal B148, first step) | 3/3 — Major | 2/3 — Testable | exact search over hosts (knot spheres K_m) and pairs of lines at which to grow two (2, 0, 4) tori, for a six-point set across both with fixed parity and five points free → a wired composite, then learn it; or no host in the range | Selected · awaiting go-ahead |
| 2 | Five-input parity on genus-1 spaces that are not lattice tori (B150) | 2/3 — Substantial | 2/3 — Testable | the exact method over a frozen sample of steered random tori of 12 to 20 points → a genus-1 space that counts five, or none in the sample | Alternative · deferred |
| 3 | Lattice tori of 25 to 32 points, with results kept per space (B151) | 1/3 — Incremental | 3/3 — Ready | the same method writing each torus as it finishes → every torus decided or named as dropped | Alternative · deferred |
| 4 | A probe that is a theorem (B130) | 2/3 — Substantial | 1/3 — Exploratory | as recorded | Alternative · deferred |

- **#1:** payoff 3/3 because a wired composite of parity gates is the step from one learned gate to larger learned functions (G15 with G16,
  sub-goal B148); concreteness rises to 2/3 because the exact method, the atoms and the hosts exist and the obstacle is named; the main
  uncertainty is whether any host keeps a wire between two grown tori. Resource bound: an exact search with caps set in advance and
  results written per space. Nothing of it was done in this epic beyond finding the obstacle.
- **#2:** payoff 2/3, it decides whether one handle can count five; concreteness 2/3, the steered generator and the method exist.
- **#3:** payoff 1/3, it completes this epic's range; concreteness 3/3, the code exists and only the writing changes.
- **#4:** as recorded at `LEARN-PARITY-20261111-001`.

**Corrections:** none.
**Goals:** G15 checkpoint (obstruction learned, with G16); B149 taken; sub-goal B148's first step sharpened and its concreteness raised to
2/3; B150 and B151 added.
**Assumptions:** none new or changed.
**Basket:** B148 (a host where two counting tori stay wired, selected, awaiting a go-ahead), B150, B151, B130.

## Final report as sent

Posted in the thread on 2026-11-11:

**B149 is closed: one torus counts three held points, and among lattice tori no more.** No lattice torus with up to 24 points computes the parity of five held points (421 tori, every class, exact, nothing dropped). Only 16 of them, with 8 to 18 points, count even three. That's the range searched, not a bound on what one handle can do.

- **Two tori composed count nothing.** I grew the 8-point counting torus at both lines of the knot sphere K_2 (genus 2). The result computes no parity map in any of its 16 classes, though each torus alone counts three. After the run I found why: one torus ties six of the sphere's points into a wire that carries its count, and the second torus unties it. Composition needs a wire that survives.
- **Known results, stated before the search:** proved, only odd counts are possible (self-duality); proved, a five-input space also counts three, so genus 0 is out unless P = NP; proved by counting, at least 32 floor states are needed. I know of no published bound on how many points one handle can count. Composition at genus 2 was marked as expected, not proved, and it failed here.
- **Tori of 25 to 32 points are undecided.** That stage ran into its 60-minute cap and was dropped by rule, because the check saved results only at the end. I estimated 15 minutes from one easy class. It's recorded as B151, a rerun that saves each torus as it finishes.
- **Learning wasn't run.** It was frozen to run only on a five-input space, and none was found. The harness reproduced last epic's learner run exactly.
- **My predictions were wrong:** I expected a five-input torus at 12 to 16 points, and the composed space to count five.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: parity of five held points (B149) | **Status:** Partially successful | exact: none on 421 lattice tori up to 24 points or on the composed space; why composition fails is found; 25 to 32 points undecided |
| Local direction: one torus counting more held points | Practically exhausted | lattice tori stop at three, and at 18 points; non-lattice tori remain (B150) |
| Broader exploration: learning program | Known alternatives | composing through a wire that survives (B148), non-lattice tori, the probe as a theorem |
| Long-term goal: G15, a point in a learned knot space | Obstruction learned | counting more needs composition, and the obvious composition unties its wire |

**Next step:** Research directions, selected #1, holding until you resume.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A host where two counting tori stay wired (sub-goal B148, first step) | 3/3 Major | 2/3 Testable | exact search over hosts K_m and pairs of lines for a six-point parity set across both tori, then learn it → a wired composite, or no host in range | Selected, awaiting go-ahead |
| 2 | Five-input parity on non-lattice genus-1 spaces (B150) | 2/3 Substantial | 2/3 Testable | the exact method over a frozen sample of steered random tori → one that counts five, or none in the sample | Deferred |
| 3 | Lattice tori of 25 to 32 points, saved per space (B151) | 1/3 Incremental | 3/3 Ready | rerun writing each torus → every torus decided or named as dropped | Deferred |
| 4 | A probe that is a theorem (B130) | 2/3 Substantial | 1/3 Exploratory | as recorded | Deferred |

**Corrections:** none.
**Goals:** G15 checkpoint (obstruction learned, with G16); B149 taken; sub-goal B148's first step sharpened and its concreteness raised from 1/3 to 2/3; B150 and B151 added.
**Assumptions:** none new or changed.
**Basket:** B148 (selected, awaiting a go-ahead), B150, B151, B130.

Both runs are registered in docs/LONG_RUNNING.md and folded in, the second as dropped. Pausing now, as you asked.
