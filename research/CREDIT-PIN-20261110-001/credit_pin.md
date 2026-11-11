# Credit from pinned dissonance

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `CREDIT-PIN-20261110-001` (backlog B132, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md) in two stages, each before the runs it governs: stage 1 (commit `08681795e`) froze the defect fix,
ticket A's re-run and ticket B's targets and marks; stage 2 (commit `15f999a38`, erratum `8ed4bc96f`) froze the credit learner. Proof
families: `proofs/CREDIT-PIN-20261110-001A/` (the fixed learner) and `proofs/CREDIT-PIN-20261110-001B/` (the credit learner).

## The answer

*Corrected on 2026-11-10 (`STURDY-PROBE-20261110-001`).* The credit learner lost to the probe, not to its credit: with a
sturdier probe and both learners unchanged, it learned and held every write (16 of 16 composites on S3 and S4, 12 of 12 on S5) against the
fixed learner's 10 of 16 composites, with no inexact stop. Mark M stands as computed with the old probe. See `docs/CORRECTIONS.md`.

**The defect, not depth, was most of the composite failure; pinned dissonance is an exact signal but not a better learner.**

- **Ticket A: the stall fixed, the old test re-run exactly.** Leaves 55 of 56 learned and held (was 53), composites 10 of 16 (was 1),
  inexact stops 5 (was 6), the impossible `0001` never stopped. So `IN-OUT-20261110-001`'s "not through a composite" was mostly the
  learner's stall: corrected (Narrowing). Depth still costs: on S3 and S4 learned composite gates took about 30 times the steps of
  learned leaf gates (median 3,309,200 against 103,200).
- **Ticket B: credit from pinned dissonance.** Every one of the 4,473 lines the learner cooled lay in an atom acting at that moment, so
  the learner's own walk tells it exactly which inner atoms hold. Used as credit it turned composite gates on more often (5 of 8 against
  3 of 8) and faster (median 1,281,800 steps against 3,309,200), and one size past it learned all 12 composite writes of a six-atom
  space. But on S3 and S4 the total did not rise (40 learned and held against 41) and inexact stops rose (9 against 5): by the frozen
  mark, pinned dissonance misleads.
- **The probe is now the weak link (computed).** Its clamped walks missed a reachable wrong value in 5 of 90 writes in ticket A, 9 of 60 in
  ticket B on S3 and S4, and 5 of 45 on S5, and three times it accepted `0001`, which theorem D forbids. Every inexact stop is such a
  miss by construction (the probe certifies only that the asked value is reachable); its reliability stays computed, not proved.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| With the stall fixed: leaves 55 of 56, composites 10 of 16 (ticket A) | computed, frozen |
| Cooled lines all in acting atoms (4,473 of 4,473 on S3 and S4; all on S5) | computed, frozen |
| Credit learner: S3 and S4 composites 11 of 16, leaves 29 of 32, 9 inexact stops; S5 composites 12 of 12 | computed, frozen |
| The probe accepted the impossible `0001` 3 times in 21 runs | computed, frozen |

## Against the pre-registration

- Ticket A (marks of `IN-OUT-20261110-001` as frozen): L held (98%), C failed (62.5%), A held, R failed (5), K held.
- Ticket B: **C2 failed** (11 of 16; mark 15); **M held**, so pinned dissonance misleads by the frozen definition (40 against 41 learned
  and held, 9 against 5 inexact stops); **A failed** (one `0001` stop on S3 and S4); **S5's C2 held** (12 of 12). The stage-2 predictions
  that C2 holds, M does not and A holds were wrong.

## What it changes

- **Depth is a cost, not a wall.** With the stall fixed, a learner told nothing about inner atoms still forms composite gates, at about
  30 times the steps, because it must find both inner atoms by trial (lemma C).
- **The memory can see what it holds.** Dissonance that a state-only walk cannot clear marks acting atoms without error here (P1 one
  way; computed the other). That is a native readout of the stored address, usable anywhere.
- **Reliability, not reach, limits learning from examples.** The clamped probe is fooled once in about every 10 to 20 writes, most often
  through composites and Fano pieces, and that is what kept every mark of this epic below 90% at composites.

## Assumptions

None added. Relied on: A20, A21, A46, A47, A49, A50 (its temperature alternative), A52, A58.

## Corrections

One, logged in `docs/CORRECTIONS.md`: `IN-OUT-20261110-001`'s "not through a composite" was mostly the learner's stall defect
(**Narrowing**, worded beyond its evidence), with dated lines in its note, intuition entry, the goals doc and the learning note.

## In the owner's words

The learner was not blind to the knots inside a knot; it had stopped looking. Fixed, it finds them by trial, and it can feel which ones
hold: their tension never leaves. Keeping those did not make it better on the whole, because its way of checking an answer, holding
the inputs and wandering, sometimes misses the wrong answer and says yes too soon.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: credit from pinned dissonance (B132) | **Status:** Partial | the defect fixed (composites 1 → 10 of 16); credit exact as a signal but no better overall (M: misleads) |
| Local direction: learning maps through composites | Continue | reach is shown; the probe's false acceptances are the limiting error |
| Broader exploration: learning program | Known alternatives | a probe that is not fooled, three held inputs, the probe as a theorem |
| Long-term goal: G15 Learning: a point in a learned knot pattern | Capability gained | composite gates learned from examples natively, and the memory reads what it holds |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A probe that is not fooled (B134) | 2/3 — Substantial | 2/3 — Testable | the same frozen tests with longer or restarted clamped walks, and a check that a decided reading survives a walk from a fresh state → no inexact stop and no `0001` stop, or a reachable wrong value no walk finds | Selected · awaiting go-ahead |
| 2 | Three held inputs (B133) | 2/3 — Substantial | 2/3 — Testable | as recorded | Alternative · in the basket |
| 3 | A probe that is a theorem (B130) | 2/3 — Substantial | 1/3 — Exploratory | as recorded; the clamped probe's misses add cases | Alternative · deferred |
| 4 | Credit from pinned dissonance, settled (from this epic) | 1/3 — Incremental | 3/3 — Ready | rerun both learners with a sturdier probe on more seeds → credit helps composites, or not | Alternative · deferred |

**Corrections:** one, Narrowing (`IN-OUT-20261110-001`'s composite failure was mostly the stall). **Goals:** G15 checkpoint (capability
gained); B132 taken; B134 added. **Assumptions:** none new or changed.
**Basket:** B134 (a probe that is not fooled), B133 (three held inputs), B130 (a probe that is a theorem); taken: B134 as the selected
next step.

## Final report as sent

Posted in the thread on 2026-11-10:

**B132 is closed. Most of the earlier composite failure was the learner's stall, not depth. Pinned dissonance turns out to be an exact signal of what the memory holds, but using it as credit didn't make a better learner.**

**The stall fix first, re-run exactly on the same frozen test.** Leaves went from 53 of 56 to 55 of 56, and composites from 1 of 16 to 10 of 16. Inexact stops went from 6 to 5, and AND still never stopped. I corrected B120's reading "not through a composite" (Narrowing, logged in docs/CORRECTIONS.md with dated lines). Depth is a cost, not a wall: learned composite gates took about 30 times the steps of leaf gates.

**Credit from pinned dissonance (frozen in two stages).** Every one of the 4,473 lines the learner kept fixed, because their dissonance never walked away, sat in an atom that was acting at that moment. So the memory reads what it holds. As credit, it turned composite gates on more often (5 of 8 against 3 of 8) and in under half the steps, and one size past it learned all 12 composite writes. On S3 and S4 the total didn't rise, though: 40 learned and held against 41, with 9 inexact stops against 5. By the frozen mark, credit misleads, and that is the opposite of what I predicted.

**How often the probe is fooled (computed, not proved).** It was fooled in 5 of 90 writes with the fixed learner, 9 of 60 with credit on S3 and S4, and 5 of 45 on S5. Three of those were acceptances of AND, which self-duality forbids. Every inexact stop is the probe's walk missing a reachable wrong value, and that is now the limiting error.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: credit from pinned dissonance (B132) | **Status:** Partial | stall fixed (composites 1 → 10 of 16); credit is exact as a signal but no better overall |
| Local direction: learning maps through composites | Continue | reach is shown; the probe's false acceptances limit it |
| Broader exploration: learning program | Known alternatives | a probe that isn't fooled, three held inputs, the probe as a theorem |
| Long-term goal: G15, a point in a learned knot pattern | Capability gained | composite gates learned from examples natively; the memory reads what it holds |

**Next step:** Research directions, selected #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A probe that is not fooled (B134) | 2/3 Substantial | 2/3 Testable | the same frozen tests with longer or restarted clamped walks, re-checking each decided reading from a fresh state → no inexact or AND stop, or a reachable wrong value no walk finds | Selected, awaiting go-ahead |
| 2 | Three held inputs (B133) | 2/3 Substantial | 2/3 Testable | as recorded | In the basket |
| 3 | A probe that is a theorem (B130) | 2/3 Substantial | 1/3 Exploratory | as recorded | Deferred |
| 4 | Credit, settled on more seeds | 1/3 Incremental | 3/3 Ready | rerun both learners with a sturdier probe → credit helps composites, or not | Deferred |

**Corrections:** one, Narrowing: B120's composite failure was mostly the stall.
**Goals:** G15 checkpoint (capability gained); B132 taken; B134 added.
**Assumptions:** none new or changed.
**Basket:** B134 (a probe that is not fooled), B133 (three held inputs), B130; taken: B134 as the selected next step.

The learning note now has the line you asked for: B109's AND is over stored roles, which the law fixes, while self-duality concerns values the world holds. B134 waits for a go-ahead.
