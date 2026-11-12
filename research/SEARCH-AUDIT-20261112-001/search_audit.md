# Learning against blind search

Epic `SEARCH-AUDIT-20261112-001` (G15 with G16; program learning), 2026-11-12, at the coordinator's request. Pre-registered in
[preregistration.md](preregistration.md), frozen in commit `06d0f2a5f` before any comparison. Proof family:
`proofs/SEARCH-AUDIT-20261112-001A/`.

## The answer

**No. In none of the line's learned results did the examples speed the finding: the learner finds its target no faster than drawing laws
at rest at random, and usually slower.**

- **The comparison.** For each of 91 cases (every learned result in the learning note's cold-start section), the exact chance that one
  uniform draw among the signings the learner may rest at gives the target, against the learner's recorded probes to find it.
- **By the frozen rule:** 67 cases slower than blind search, 22 search, 2 learning. The 2 are single writes (one run each), found about
  as fast as blind search itself does a quarter of the time.
- **Pooled (after the run):** of 215 runs that found their target, 10.2% found it within the blind median, where blind search would do so
  half the time; the mean chance that blind search would have been as fast is 0.825 instead of 0.5. Gates and deeper memories are the
  slowest (2.2% within the blind median).
- **Headline cases:** parity on the 8-distinction pattern, blind median 6 probes, learner median 27; inside a memory, 6 and 16.5; the
  count of five through a shared distinction, 22 and 281.
- **Why slower:** the learner probes at rest every 200 steps and its law changes slowly, so it tests the same law many times; blind draws
  are independent. That accounts for slowness, not for a lack of steering: a learner the examples steered would beat blind draws anyway.

## What is known, and what is proved and computed

| Claim | Evidence class |
| --- | --- |
| The chance per draw, the blind median and mean, for every case | exact (classes at rest enumerated; interface flips counted) |
| 67 of 91 cases slower than blind search, 22 search, 2 learning (single writes) | computed from recorded runs, frozen criterion |
| 10.2% of 215 found runs within the blind median (blind search: 50%) | computed after the run (`pooled.py`) |
| Random search with a stopping test is a learner only in a weak sense; parity is hard for statistical learners | known (Kearns 1998 on statistical queries) |

## Against the pre-registration

As predicted: no case is learning beyond chance. The frozen rule names 2 single-write cases learning; the report reads them as chance,
and says so. The first full run hit its cap with nothing written; the rerun changed only speed and per-family writing.

## What it changes

- **The word "learned" is corrected (Narrowing).** What the record calls learned is a map found by a search over the laws the learner may
  rest at, stopped by the examples, and then held. The results stand (each map was found, every stop was exact, and held where reported);
  their reading as learning guided by examples does not. Judged against G15 (a point in a learned knot pattern) and G16 (learning the
  rules behind what a system allows): the capability gained is native storing and keeping of a found map, not learning from examples. The
  correction is logged in `docs/CORRECTIONS.md`; the goals doc, the notebook and the learning note say "found by search and held" from here
  on, and earlier entries keep their text with this correction pointed to.
- **The rest set decides the cost.** Since the search is blind, its cost is the number of laws at rest per target law. That makes B161
  (which cyclic sequences to fix, to shrink the rest set natively) the direct lever, and a learner whose examples steer the search (B165)
  the open question that would make "learning" earn its name.
- **A smaller fix.** The NATIVE-GRADE report gave 16 expected draws on one copy; with the target's constant fixed it is 32 (median 22).
  The comparison's direction stands (244.5 probes). Logged with the correction above.

## Assumptions

None added or changed. Relied on: A20, A21, A46, A47, A49, A50, A52, A58.

## Corrections

Two, logged together: the word "learned" across the learning line (Narrowing: found by search and held, not guided by the examples);
NATIVE-GRADE's blind expectation 16 should be 32 (Not a block).

## In the owner's words

The learner has never been taught by its examples. It wanders among the rules it may settle on, tries each against the examples, and
stops when one fits; it would have done as well drawing rules at random. What it does well is keep a rule once found.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: has the learner ever beaten blind search | **Status:** Successful | decided: no case beyond chance, 91 cases, 215 found runs |
| Local direction: the credit learner as a learner from examples | Retire | its examples stop the search but do not steer it |
| Broader exploration: learning program | Known alternatives | shrink the rest set natively (B161), a learner whose examples steer (B165), two histories (B159) |
| Long-term goal: G15 Learning: a point in a learned knot pattern | Obstruction learned | what was gained is native storing and keeping of found maps; learning from examples is not shown |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which cyclic sequences to fix (B161), redesigned with the advisor's points | 3/3 — Major | 3/3 — Ready | the counting laws' sums by cycle kind and by symmetry orbit, a null with random target laws, a dozen or more bases → a native rule that raises the counting density beyond chance, or a structural reason none can | Selected · started |
| 2 | A learner whose examples steer its search (B165) | 3/3 — Major | 1/3 — Exploratory | a learner that changes the signs nearest the failing examples first, frozen, against blind search on the same rest sets → probes below the blind median, or none | Alternative · deferred |
| 3 | Two histories (B159) | 2/3 — Substantial | 2/3 — Testable | as recorded | Alternative · deferred |

- **#1:** payoff 3/3, since with blind search the rest set is the cost; concreteness 3/3, the census is exact linear algebra on the laws'
  sums. Started at the coordinator's go-ahead; the advisor model's view is folded into its design.
- **#2:** payoff 3/3, it would make learning from examples real; concreteness 1/3, no steering rule is defined yet.

**Corrections:** two (the word "learned", Narrowing; one expected count, Not a block).
**Goals:** G15 checkpoint (obstruction learned, with G16); B165 added as a sub-goal.
**Assumptions:** none new or changed.
**Basket:** B161 (started), B165, B159, B162, B157, B154, B155, B156, B150, B151, B130.

## Final report as sent

Posted in the thread on 2026-11-12 (05:26 UTC), exactly:

**The audit is closed, and it's a real finding: the learner has never been taught by its examples.** I covered all 91 cases the line called learned: parity, the count of five, gates, deeper memories, written addresses, and the rest-set learners. In each, I compared the learner's recorded probes with blind search, meaning uniform random draws among the laws it may rest at, computed exactly.

- **By the frozen rule:** 67 cases slower than blind search, 22 at search speed, and 2 "learning". Those 2 are single writes and consistent with chance.
- **Pooled:** only 10% of 215 successful runs found the target within the blind median, where blind search would manage 50%. Parity, for example: blind median 6 probes, learner median 27. The count of five: 22 against 281.
- **What it means:** the examples decide when the learner stops; they don't steer where it goes. So I've logged a correction (Narrowing): every "learned" in the line now means *found by a search the examples stop, then held*. Each map found, each exact stop and each hold stands. Learning from examples is not shown, and is now open as sub-goal B165. I also fixed one number: the blind expectation in the B160 report was 32, not 16.
- **Consequence:** with a blind search, the cost is simply how many rules the learner may settle on per right one. That makes B161 (shrinking that set natively) the direct lever. I'm starting it now, as asked, with the advisor model's design points folded in. Its main point: tabulate the counting laws' sums by symmetry orbit first, and add a null test plus many more bases.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: has the learner ever beaten blind search | **Status:** Successful | decided: no, in 91 cases |
| Local direction: the credit learner as a learner from examples | Retire | examples stop, don't steer |
| Broader exploration: learning program | Known alternatives | shrink the rest set (B161), a steered learner (B165), two histories (B159) |
| Long-term goal: G15 | Obstruction learned | gained: storing and keeping found maps; learning from examples not shown |

**Next step:** Research directions, selected #1, started.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which cyclic sequences to fix (B161) | 3/3 Major | 3/3 Ready | counting laws' sums by kind and symmetry orbit, a null, a dozen or more bases → a native rule that raises counting density beyond chance, or a reason none can | Selected, started |
| 2 | A learner whose examples steer (B165) | 3/3 Major | 1/3 Exploratory | change first the signs nearest failing examples → beat the blind median, or not | Deferred (sub-goal) |
| 3 | Two histories (B159) | 2/3 Substantial | 2/3 Testable | as recorded | Deferred |

**Corrections:** two. "Learned" narrowed (Narrowing); the blind expectation in B160's report fixed from 16 to 32 (Not a block).
**Goals:** G15 checkpoint (obstruction learned, with G16); sub-goal B165 added.
**Assumptions:** none new or changed.
**Basket:** B161 (started), B165, B159, B162, B157, B154, B155, B156, B150, B151, B130.

The audit run is registered in docs/LONG_RUNNING.md and folded in.
