# Learning without a drawing

Epic `UNDRAWN-LEARN-20261111-001` (sub-goal B153, G15 with G16; program learning; the challenge of A66), 2026-11-11 to 2026-11-12, at the
coordinator's go-ahead. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `6be010d59` before any learning run.
Proof family: `proofs/UNDRAWN-LEARN-20261111-001A/`.

## The answer

**Without the drawing's faces the learner neither finds nor keeps a count: the faces did real work.**

- **The test.** The learning line's learner feels part of its dissonance at the faces of a drawing. Here it felt dissonance at knots alone
  (twice the number of violated knots), changed signs only at violated knots, and read distinctions where its credit rule read faces.
  Everything else was unchanged.
- **One copy (exact first).** On one copy of the drawn knot pattern (2, 0, 4), 4 of its 512 laws count three held distinctions. With faces
  the learner can rest only among 4 law classes, 1 of which counts; without faces it can rest at any of the 512.
- **One copy (computed, frozen): 0 of 10.** One run stopped at the count for all three targets and held none of them; nine reached the
  30-minute cap without stopping. With faces: 10 of 10, median 13,400 steps.
- **Two copies sharing a distinction: 0 of 10.** All ten runs reached the 120-minute cap. With faces: 10 of 10 (`SHARED-COUNT-20261111-001`).
- **A base no drawing fits: 0 of 10.** U, 6 distinctions and 8 knots with 2 to 6 knots at a distinction, counts three held distinctions
  in exactly 1 of its 2,048 laws (exact). Two runs stopped at the count; 1 of their 6 writes held; eight runs reached the cap.
- **Why the stops did not hold (computed, read from the runs).** After the disturbance, the repair re-signed knots as freely as it flipped
  distinctions, and the learned law drifted: on one copy the count `01101001` became `0x1uu0x1`. With faces, a sign change makes the faces
  beside it dissonant, so repairs flip distinctions and the law stays (a reading, not tested apart: B158).

## What is known, and what is proved and computed

| Claim | Evidence class |
| --- | --- |
| On one copy, 4 of the 512 laws count three held distinctions; with faces the learner rests among 4 law classes, 1 counting | exhaustive |
| U counts three held distinctions in exactly 1 of its 2,048 laws, at one set only | exhaustive |
| The drawing-free learner holds the count on none of the three bases (0 of 10 each) | computed, frozen |
| The faces narrow the laws the learner rests at and make a learned law cost something to change | reading of the runs; the two jobs not tested apart (B158) |
| A 6-distinction base counts three held distinctions, fewer distinctions than any drawn knot pattern found to count (8) | exhaustive for U; a search observation, not a minimum |

## Against the pre-registration

- V and R as computed before freezing.
- I predicted L1 would pass, more slowly. It failed, and so did L2 and L3 (L3 as predicted).
- By the frozen criterion (L1 or L2 failing), the faces did real work, and A66 is **Confirmed** for that reason: the counts learned with
  faces rested on reading each copy's drawn faces.

## What it changes

- **The line's memory lived partly in the drawing.** The learned law is a memory only because changing it costs dissonance, and on drawn
  knot patterns that cost is paid at faces. A base in the owner's sense, knots overlapping freely, has no faces, so a learner there needs
  another reason for its law to stay put, and another way to narrow the laws it searches.
- **Overlap still computes cheaply.** U counts three held distinctions with 6 distinctions, where no drawn knot pattern found so far does
  with fewer than 8. What fails on U is the learner, not the base.

## Assumptions

A66 **Confirmed** (the faces did real work on J1 and J2; kept for that reason). Relied on: A20, A21, A46, A47, A49, A50, A52, A58.

## Corrections

None.

## In the owner's words

Take away the drawing and the learner forgets as fast as it learns. When it is shaken, it mends itself by rewriting its own rules as
easily as by changing its state, so whatever it had learned washes out. On a drawing, rewriting a rule costs something, and that cost was
the memory.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a learner whose dissonance needs no drawing (B153) | **Status:** Failed | 0 of 10 held on each of three bases; the faces did real work |
| Local direction: the credit learner with dissonance at knots alone | Retire | it neither finds nor keeps a count without faces |
| Broader exploration: learning program | Known alternatives | separating the faces' two jobs and finding them natively (B158), the tie (B157), the count of seven (B154), the two-histories test (B159) |
| Long-term goal: G15 Learning: a point in a learned knot pattern | Obstruction learned | learned memory has so far needed a drawing's faces; bases with no drawing need another source of rigidity |

The failure answers B153's question (the faces were needed), so the attempt failed at its target but decided it.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | What does the faces' work on a base with no drawing (B158) | 3/3 — Major | 2/3 — Testable | on one copy, two learners frozen apart: faces only as a rule for where the learner may rest (no face dissonance), and no faces but repairs that flip only distinctions → which job learning needs; then a native source of that job on U → a learner that holds a count on a base no drawing fits, or which job has no native source | Selected · awaiting go-ahead |
| 2 | A tie in place of the shared distinction (B157) | 2/3 — Substantial | 3/3 — Ready | as recorded by the coordinator, with the copies' faces kept → the count of five learned through a tie, or a cost unrelated to identity | Alternative · deferred |
| 3 | The count of seven: where the time goes (B154) | 2/3 — Substantial | 3/3 — Ready | as recorded | Alternative · deferred |
| 4 | A learner that must end differently after two histories (B159) | 2/3 — Substantial | 2/3 — Testable | the six-distinction example's two legal 50-move histories ending in one state (Codex, unrefereed): referee them, then require a native learner to end in different laws → a G16 control, or none | Alternative · deferred |

- **#1:** payoff 3/3, because a learner on the owner's bases needs whatever the faces supplied, and the two jobs may need different
  sources; concreteness 2/3, both one-copy variants are small changes and J1 runs are fast with faces, but a native source on U is not yet
  defined. Resource bound: J1 runs at this epic's caps; U only after a variant holds on J1. Awaiting a go-ahead because it changes the
  learner's rules, which the coordinator should weigh against B157.
- **#2:** payoff 2/3, it would give B155 a native move; concreteness 3/3, the tie is checked and the code exists.
- **#3:** payoff 2/3; concreteness 3/3.
- **#4:** payoff 2/3, a crisp test that a learner's state records its history (G16); concreteness 2/3, the histories exist but are
  unrefereed.

**Corrections:** none.
**Goals:** G15 checkpoint (obstruction learned, with G16); sub-goal B153 taken; sub-goal B158 and backlog B159 added.
**Assumptions:** A66 Confirmed (the faces did real work).
**Basket:** B158 (selected, awaiting a go-ahead), B157, B154, B159, B155, B156, B150, B151, B130.

## Final report as sent

Posted in the thread on 2026-11-12 (02:03 UTC), exactly:

**B153 is closed: without the drawing's faces, the learner neither finds nor keeps a count.** With dissonance felt only at broken knots, the same learner held the count in 0 of 10 runs on each base: one copy, two copies sharing a distinction, and a 6-distinction base that no drawing fits. Reading the faces, it held 10 of 10 on the first two. By the frozen criterion the faces did real work, so A66 is Confirmed.

- **Why it fails (exact plus the runs).** The faces do two jobs. They narrow where the learner can rest: on one copy, 4 law classes instead of 512 laws, of which 4 count. And they make changing a sign cost something. Without them, a disturbed learner repairs itself by rewriting its rules as freely as its state, so the count washes out. Its few stops at the count were all lost but one. The two jobs weren't tested apart; that's the next step.
- **A side observation (exact):** the undrawn base counts three held distinctions with 6 distinctions, where no drawn pattern found so far does it with fewer than 8. Exactly 1 of its 2,048 laws counts, so what failed there is the learner, not the base.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a learner whose dissonance needs no drawing (B153) | **Status:** Failed | 0 of 10 held on each of three bases; the faces did real work |
| Local direction: the credit learner with dissonance at knots alone | Retire | it neither finds nor keeps a count without faces |
| Broader exploration: learning program | Known alternatives | separating the faces' two jobs (B158), the tie (B157), the count of seven (B154), the two-histories test (B159) |
| Long-term goal: G15, a point in a learned knot pattern | Obstruction learned | learned memory has so far needed a drawing; bases with no drawing need another source of rigidity |

**Next step:** Research directions, selected #1, awaiting a go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | What does the faces' work on a base with no drawing (B158) | 3/3 Major | 2/3 Testable | on one copy, the two jobs frozen apart (rest only where faces allow, no face dissonance; no faces, repairs flip only distinctions), then a native source of the needed job on the undrawn base | Selected, awaiting go-ahead |
| 2 | A tie in place of the shared distinction (B157) | 2/3 Substantial | 3/3 Ready | as recorded, copies' faces kept | Deferred |
| 3 | The count of seven: where the time goes (B154) | 2/3 Substantial | 3/3 Ready | as recorded | Deferred |
| 4 | A learner that must end differently after two histories (B159) | 2/3 Substantial | 2/3 Testable | referee the two histories, then require different laws at the end | Deferred |

**Corrections:** none.
**Goals:** G15 checkpoint (obstruction learned, with G16); sub-goal B153 taken; sub-goal B158 and backlog B159 added.
**Assumptions:** A66 Confirmed (the faces did real work on one and two copies).
**Basket:** B158 (selected), B157, B154, B159, B155, B156, B150, B151, B130.

The runs are registered in docs/LONG_RUNNING.md and folded in. I'm holding for a go-ahead on B158, since it changes the learner's rules and you may prefer the cheaper tie (B157) first.
