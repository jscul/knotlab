# The advisor's answer (26 November 2026)

To [the question](advisor_question.md), asked before the hold-back laws were frozen.

**The main problem first.** Without takes, a join has p = 2 (floor 1) and an offshoot has p = 1 (floor 2). At the usual join (p = 2, D = 2) any law can give only 2 (the ordinary count) or 1 (three-places). So on your starts, forms differ only at that one binary choice and at births with D ≥ 3 or with takes. Several "new" forms are therefore old laws under another name. I assume a birth is short when f < D.

**1. Forms**

| Form | Formula | Why a knot would hold back so | What it is on the starts |
|---|---|---|---|
| A. Inheritance | max(min(D, p), 3 − p, 1) | passes on no more than it was given | cap 2 exactly, unless takes occur |
| B. One per parent | max(min(D, parents), 3 − p, 1) | each parent vouches for one | identical to A without takes |
| C. Net owing | max(D − p + 1, 3 − p, 1) | what it was given already pays part of what it is owed | three-places when D ≤ 2; offshoots ordinary |
| E. Keeps one | max(D − 1, 3 − p, 1) | retains one distinction of its own | equals C at joins; differs at offshoots with D ≥ 3 |

A fifth, debt passed down (offshoot gets max(D − o, 2), joins ordinary), cannot start a shortage. With joins ordinary, o is always 0 by your theorem, so it is the ordinary count. Use it only as a modifier on another form.

**2. Short in the joined starts?**

- **A and B:** not short at p = 2, D = 2, where they are the ordinary count. They are short only at D ≥ 3, by D − 2.
- **C and E:** every join with D ≥ 2 is short by exactly one. Offshoots are never short under C, and under E only at D ≥ 3.

So there are two real classes:
- **Cap-like (A, B):** the shortfall grows with D and is absent at small D.
- **Constant shortfall (C, E):** short by one at every join.

Freeze A and C. B and E are spares that matter only if the starts contain takes or offshoots with D ≥ 3.

**3. Survival, and controls**

*Survives* means the same receiver kind hears the far change under one form from each class, at a round growing with d; the constant may differ from 2d + 1.

*Belongs to one form* means hearing occurs only where the form coincides, birth for birth, with the cap or three-places.

Controls:
- **Difference census.** For each start, list the births on the way from the change to the receiver where the two forms give different f. If there are none, the "change of form" is empty and the start does not count.
- **Paired run.** Run the same start with and without the far change; hearing is a difference in the receiver's record only.
- **Jam check.** Under C nearly every join waits, so require growth to continue past the hearing round in both runs of the pair. Your earlier correction was exactly a jam read as hearing.
- **Negative control.** The ordinary count, which must show no difference.
- **Positive control.** Cap 3 at its known receiver.
- **Law of the knots.** State that this is not-all-equal only; your parity census found no shortage to work with.
