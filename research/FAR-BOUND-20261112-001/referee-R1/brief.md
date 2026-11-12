# Referee job FAR-BOUND-R1: the brief

The coordinator handed this job over on 2026-11-12 (13:52 UTC). It comes from the knots-alone thread: `FAR-BOUND-20261112-001`,
closed and published in commit e9cefdef3. The pre-registration was frozen in a0d2ee806.

## Ticket A: the census

The code is `census.py`; its outputs are `control.json`, `recheck.jsonl`, `far.jsonl` and `rings.jsonl`. The claims:
- **The Eventual certificate is sound.** The control certifies base 16's values 4, 5, 5, 6, 6. TRAVEL-READ-R1 already judged this
  certificate.
- **F1.** 34 of 66 bases are bounded on certified bonds. F1 failed, and the narrowing is already logged.
- **F2.** Of the 26 decided bases:
  - 16 stay within near + 1 out to 23 across;
  - 5 rise by 2;
  - 5 lack certificates.

  8 of the 34 were dropped at the cap. F2 failed, and so did its validity bound.
- **F3.** 77 of 102 bases hold, at window level.

## Ticket B: the proof

On COMMON-FOLD's sample 24 at r = 3, bond distance is at most 3 on two quadrants of the frame. The proof rests on four checks:
- **C1:** travel along t′ and along 4u;
- **C2:** T_0 is free;
- **C3:** 1,620 representative cases, certified by Eventual2;
- **C4:** a mutation, removing one kind.

The owning thread asks for a close check of two things: the soundness of Eventual2 (tails in both directions, and the corners), and
the representative argument.

## The coordinator's questions

- **(i)** How much of the exploratory pattern ("a second direction means bounded, 11 of 12; one direction grows in about half, 4 of
  9") survives the referee's wider second-direction search?
- **(ii)** Do the 8 dropped and 5 uncertified bases bias the 16 / 5 split?
- **(iii)** Is "rise by 2 out to 23" evidence of unbounded growth, or compatible with a higher bound?
