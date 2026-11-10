# A probe that is not fooled

Epic `STURDY-PROBE-20261110-001` (backlog B134, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md), frozen with the code in commit `fb162b543` before any run on a test space. Proof family:
`proofs/STURDY-PROBE-20261110-001A/`.

## The answer

**Yes: a sturdier check removes every false acceptance, and with it the credit learner learns every write.** Each negative check of the
probe became four 25,000-step walks, one from the current state and three from fresh states, with nothing else changed. Across 156 writes
and 39 runs of the impossible `0001`, no stop was inexact and no `0001` run stopped (mark Z). The probe then cost 2.5 times the old one's
walk steps on the same run, about three probe steps per learner step.

- **The fixed learner:** leaves 56 of 56 (was 55), composites 10 of 16 (unchanged; the four writes that had stopped on a false reading now
  ran out their budget instead).
- **The credit learner:** every one of its 84 writes learned and held: 32 of 32 leaves and 16 of 16 composites on S3 and S4, 24 of 24 and
  12 of 12 on S5. Against the fixed learner it doubled the composite gates turned on (8 of 8 against 4 of 8). So pinned dissonance does
  help as credit; `CREDIT-PIN-20261110-001`'s "did not make a better learner" was the old probe's doing, corrected (Narrowing).

## Which earlier figures survive

| Figure | Scored by | With the sturdier probe |
| --- | --- | --- |
| 100 of 100 native writes (`NATIVE-WRITE-20261110-001`) | SAT on roles; its own probe, an unclamped 20,000-step walk, never fooled | untouched: not this probe |
| 55 of 56 leaves, fixed learner (`CREDIT-PIN-20261110-001A`) | SAT on maps | 56 of 56 |
| 10 of 16 composites, fixed learner | SAT on maps | 10 of 16 |
| 11 of 16 composites, credit learner (`CREDIT-PIN-20261110-001B`) | SAT on maps | 16 of 16 |
| S5: 21 of 24 leaves, 12 of 12 composites, credit learner | SAT on maps | 24 of 24, 12 of 12 |

Every figure since B119 was scored by SAT on the law at each stop, so a fooled probe never inflated one; it stopped a run early and the
write was counted as an inexact stop. The sturdier probe can only let such runs continue, and every figure stays or rises.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Every inexact stop is a reachable wrong value the negative check missed (the positive check certifies its value) | by construction |
| With the sturdier probe: no inexact stop, no `0001` stop (156 writes, 39 runs) | computed, frozen |
| Fixed learner 56 of 56 and 10 of 16; credit learner 84 of 84 | computed, frozen |
| Cost: 2.5 times the old probe's walk steps on the same run | computed, frozen |

## Against the pre-registration

Z held; the counts stayed or rose, as predicted; the cost was 2.5 times, as "several times" predicted. The probe's reliability is still
computed, not proved (backlog B130).

## What it changes

- **Learning from examples now works through composites, natively and exactly here.** With the credit from pinned dissonance and a check
  that does not accept too soon, a learner that sees only its own dissonance under the world's clamps learned every gate target at every
  leaf and composite of three spaces, up to six atoms at genus 6, with no outside map.
- **The two readings of `CREDIT-PIN-20261110-001` reverse.** Its mark M ("credit misleads") stands as computed, but it measured the old
  probe, not the credit.

## Assumptions

None added or changed. Relied on: A20, A21, A46, A47, A49, A50, A52, A58.

## Corrections

One, logged in `docs/CORRECTIONS.md`: `CREDIT-PIN-20261110-001`'s "as credit it did not make a better learner" (**Narrowing**, worded beyond
its evidence), with dated lines in its note, intuition entry, the goals doc and the learning note.

## In the owner's words

The learner was saying yes too soon. Asked to check an answer, it now looks four times, three of them from somewhere new, before it
believes no other answer fits. With that, it learned every gate it was asked for, inside patterns of patterns too, by keeping the parts
whose tension it cannot walk away.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a probe that is not fooled (B134) | **Status:** Successful | mark Z met at 2.5 times the probe's cost; every figure stays or rises |
| Local direction: learning gates of held inputs | Exhausted for this phase | every gate target learned at every leaf and composite tested |
| Broader exploration: learning program | Known alternatives | three held inputs, deeper memories, the probe as a theorem |
| Long-term goal: G15 Learning: a point in a learned knot space | Capability gained | gates through composites learned from examples natively, without false stops |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Three held inputs (B133) | 2/3 — Substantial | 2/3 — Testable | census of maps with three held points (theorem D allows majority and parity), then learn parity with the credit learner and the sturdier probe → a learned map that is not unate, or a proof that none exists | Selected · awaiting go-ahead |
| 2 | Deeper memories from examples (B135) | 2/3 — Substantial | 2/3 — Testable | composites of three atoms and composites within composites, the same learner and probe → gates learned at every depth tested, or the depth where the budget runs out | Alternative · deferred |
| 3 | A probe that is a theorem (B130) | 2/3 — Substantial | 1/3 — Exploratory | as recorded; now for both probes | Alternative · deferred |
| 4 | A cheaper sturdy probe (from this epic) | 1/3 — Incremental | 2/3 — Testable | fewer or shorter negative walks with the same mark → the cheapest probe with no false stop | Alternative · deferred |

**Corrections:** one, Narrowing (`CREDIT-PIN-20261110-001`'s credit reading). **Goals:** G15 checkpoint (capability gained); B134 taken;
B135 added. **Assumptions:** none new or changed.
**Basket:** B133 (three held inputs), B135 (deeper memories from examples), B130 (a probe that is a theorem); taken: B133 as the selected
next step.
