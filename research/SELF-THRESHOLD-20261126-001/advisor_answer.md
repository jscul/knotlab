# The advisor's answer (26 November 2026)

To [the question](advisor_question.md), asked before the self-read thresholds were frozen.

**(1) Caps in disguise, by kind.** On these starts p takes only two values, so any function of p is a two-row table of constants. Assuming the ordinary floor is kept (f = min(ordinary, threshold); as written, D = 0 gives f = 0, which would be a second change):

| Law | Joins (p = 2) | Offshoots (p = 1) |
|---|---|---|
| Cap of three | at most 3 | at most 3 |
| PLACES | at most 3 | exactly 2 |
| DOUBLE | at most 4 | exactly 2 |

- **What they are:** PLACES is the cap of three on joins plus a cap of two on offshoots; DOUBLE is the cap of four on joins plus the same offshoot cap.
- **The control:** offshoots owed three or more are exactly where they differ from the caps. Count them per run. If there are none, PLACES and the cap of three are the same run, and you should report it as a replay.
- **The finding:** "the cap's number is the knot's own count of places" cannot be claimed here. With p fixed at 2 on joins, 3 = p + 1 is a coincidence until p varies. Only joins of three parents, or takes, can separate reading the number from a constant.
- **Isolating the offshoot cap:** run "cap of three on joins, offshoots ordinary" beside PLACES.

**(2) A threshold that is not a cap: HALF.** f = min(ordinary, ⌈D/2⌉ + 1).

- It binds exactly where D ≥ 4, the same binding set as the cap of three, on both kinds.
- f is unbounded, and the shortfall ⌊D/2⌋ − 1 grows with the owing.
- It separates the two readings of your result: whether late hearing depends on where the threshold binds, or on the fixed number 3.

PARENT also varies, through o, but it reads the parent, not the knot itself. With max(o, 2) it will mostly equal 2, so it will mostly coincide with PLACES. Log how often o ≥ 3.

**(3) Expectations (guesses, not evidence).**

- **PLACES:** late hearing if offshoots owed three or more are few. If they are common, the offshoot cap binds widely and I expect parting, as under the hold-back laws.
- **DOUBLE:** follows the cap of four, with the same offshoot caveat.
- **PARENT:** about the same as PLACES.
- **HALF:** the informative one. Late hearing supports your reading; parting, or hearing at a different round, means the mechanism is the number 3 and not the binding set.

Before freezing, record binding counts by kind (join or offshoot) for every law, and state the floor explicitly.
