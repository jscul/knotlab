# Referee hand-off: RING-IN-BALANCE-20261123-001

All three tickets are referee pending. Each pre-registration has its prior-work searches under "Prior work in the program";
run `python3 -B scripts/track.py objects-gate research/<TICKET>/preregistration.md`. The shared definitions are in
`research/RING-IN-BALANCE-20261123-001/definitions.md`. The next step of the line does not wait for the verdict.

| Record | Claims to check | Evidence class | Code and data |
| --- | --- | --- | --- |
| Ticket A | The return every two rounds with n two-member parts coming apart, odd rings of 5 to 15 knots (P1, P2); the roster in balance under the three added rules (P4); every knot passing the knot test under parity and not-all-equal (P6, P7); a returning ring for every cap from three to seven, with parts of 2, 5, 9, 14 and 20 knots (P11); the jam under HOLD (P10); the table of 70 swapped laws, including the failed P8 and the small parts that copy themselves | Exact computation. Two arguments to read: that under parity a new knot with a fresh distinction passes the knot test and keeps passing (pre-registration, settled statements), and that the return holds for every odd ring from five (result note, "The argument for every odd ring") | `experiments/RING-IN-BALANCE-20261123-001A/`, `artifacts/RING-IN-BALANCE-20261123-001A/` |
| Ticket B | The census counts: 86,032 starts, 316 set aside, 227 returning under the added rules, none under ordinary growth; the shares by number of dead knots; the 107 returning starts with four members; the matched pairs 70 / 42 / 0 / 30,278; that all 1,846 returns of a ring itself are made of knots that waited, and the two failures of P3; the round formula on 44,333 knots and its spread | Exhaustive census for the stated family; exact computation. Seven ordinary-law runs not completed, listed in the result note | `experiments/RING-IN-BALANCE-20261123-001B/`, `artifacts/RING-IN-BALANCE-20261123-001B/` (two files stored compressed, see `COMPRESSED.md`) |
| Ticket C | That parts taking their rounds one at a time build what complete rounds build (P2, 726 runs) and the argument for it; the births between returns under each order (P4 to P6); the jam of the birth-by-birth law on every cycle through dead knots and in every order on the cycle of four (P1) | Exact computation; one argument (pre-registration, settled statements; it rests on ticket A's "parts act alone") | `experiments/RING-IN-BALANCE-20261123-001C/`, `artifacts/RING-IN-BALANCE-20261123-001C/` |
| The thread's checks | The comparison of ticket A's engine with the pilot's two programs (83 of 84 comparisons equal; the one difference explained); the comparison of the two independent engines; the spot checks of the cap of four and five, the Fibonacci counts and two census starts | Exact computation by the designer of the studies, weaker than a fresh referee | `research/RING-IN-BALANCE-20261123-001/checks/` (the pilot's programs are private workspace files) |

Things a referee should know. The engines of tickets A and C were written by two helper agents from the frozen text alone and
never saw each other's code or the pilot's; ticket B uses ticket A's engine. Each helper recorded its readings of the frozen
text in `deviations.md` before its registered runs; four bear on verdicts (ticket A: which parts P3 follows, and that P8
counts a part of any size; ticket B: which returns P3 covers; ticket C: which n P5 means). The definition of "returns" counts
the ring's other phase, a part of 2n members made of new knots, as a return in its own right; two predictions were worded
without that in mind. The advisor reviewed the first design cold and found by hand that its birth-by-birth law jams; the
part-round law of the frozen design was not reviewed by anyone before the runs. Ticket C's contract has two stale descriptive
fields. Whether the line-graph operator's literature already contains a returning cycle with output under a blocking rule was
not searched beyond the phrases listed in ticket A's pre-registration.
