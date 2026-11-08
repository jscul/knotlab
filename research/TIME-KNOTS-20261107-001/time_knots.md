# Knots across time: a process read as its space-time law

Epic `TIME-KNOTS-20261107-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** It is backlog B7, the selected next step of `GROWTH-LAW-20261107-001`. That epic answered question 4
  of `docs/KNOT_INTUITION.md` for growth: a growth order adds a beginning, never a knot of the world. The coordinator relayed on
  2026-11-08 that the wrap-up request had ended, so the step started at once under the standing mandate.
- **The question.** Question 4's other half: "Are loops better modeled as processes whose outputs over time are the data, and does
  the static definition survive that change?" Here the states themselves change under a local dynamics. Written as its space-time
  law, whose allowed states are the trajectories, which knots join a cell's future to its past, and which processes remember their
  past only pairwise?
- **The owner's example.** On 2026-11-08 the owner suggested Conway's Life as the picture of emergence (knotlab's lesson 1.3).

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Knots across time are minimal decisive sets.** The knots made of a cell's value after T steps and cells of the first row are exactly the sets of past cells that, set suitably, decide the future value while no smaller set decides it, when they have two or more cells. A single deciding cell gives a tie. | proved; computed on 476 maps against the generic enumerator | A |
| 2 | **Pairwise memory of the first row is exactly the single ANDs and ORs.** A future value has no knot with the first row exactly when it is a single conjunction or disjunction of literals of it. Such a process can still knot two times through intermediate rows (corrected 2026-11-08; see the correction below). | proved; computed on every nonconstant function of up to four inputs | A |
| 3 | **Linear processes keep a fixed-size knot with their past at every power of two.** A linear rule with polynomial p has one two-time knot per lag: the support of p^T plus the cell. It has \|supp p\| + 1 places at every lag 2^k (Frobenius), and 2^popcount(T) + 1 for rule 60 (Lucas). Knots through intermediate cells are smaller, down to 2 + w(T) for Ledrappier's law, the space-time law of rule 102. | proved; computed | A |
| 4 | **Life binds a cell's future only to its neighbours.** In one step of Life the knots are the 70 sets of four neighbours (overcrowding). There are no ties, and the cell's own present value is in no knot. | proved by exhaustion | A |
| 5 | **A census of the 88 elementary automata to lag 6.** 15 are knot-free at every lag, so their memory of the first row is only pairwise; four of them still knot their later states (correction below). 8 keep exactly one knot per lag: the linear 60, 90, 105 and 150, and 42, 76, 138 and 200. 49 have knot counts growing at every lag, and 16 do otherwise. The traffic rule 184's knots at lag T are all C(2T + 1, T + 1) sets of T + 1 light-cone cells. Majority (232) keeps a three-place knot at every lag. Knots across time do not follow Wolfram's classes. | exploratory experiment | B |

## Answer

- **The static definition survives.** A process written as a law is a static law on its trajectories.
- **What its knots across time are.** They are the minimal sets of past cells that decide a future cell.
- **Pairwise memory.** A process knows its first row only pairwise, ties and no knot, exactly when each future value is a single
  AND or OR. This is the program's two/three boundary, read across time. Such a process is not knot-free across time: an AND
  process still knots its later states wherever its image forbids a pattern (correction below).
- **Knotted memory.**
  - **Linear processes** never forget: at every power of two they keep one knot of fixed size with their past.
  - **Traffic** binds its past most uniformly: every set of T + 1 of its 2T + 1 past cells is a knot.
  - **Life's step** binds a cell's future to four neighbours at a time, and never to the cell itself.

## Reading

**Interpretation, not a theorem.**
- **For question 4.** Loops can be modelled as processes without changing the knot test. The data over time are the trajectory,
  and K1–K3 reads knots across time directly. What a process adds over a static law of one moment is these knots, which join
  different times.
- **Emergence across time.** A future value that is a single AND or OR is fixed by one first-row cell at a time, so its memory of
  the first row is only pairwise. Every other future value needs several past cells together, constrained as a whole and free in
  every part. A second source of knots across time is the image: patterns a rule never produces knot its later states together.
- **Life.** The owner's example of emergence emerges, under K1–K3, from crowds: four neighbours at a time decide a cell, and
  its own present never enters a knot.
- **The light cone is too small.** In Ledrappier's law the least knot joining a cell to itself seven steps on has four places.
  It reaches outside the cell's past light cone, through a second cell at the later time (stress test). Knots across time are not
  confined to what can influence the future cell.

## Stress test

One size past each computed claim (`stress_test.py` here, with `stress_test_quick.json` and `stress_test_census7.json`). Each
reuses the tickets' own code.

| Claim | One size past | Result |
| --- | --- | --- |
| Theorem 1 on the 88 rules at T = 1, 2 (A) | T = 3 | pass: no mismatch with the generic enumerator |
| Theorem 2 on all functions of ≤ 4 inputs, terms and clauses of 5 (A) | All terms and clauses of 6 inputs; 300 random 6-input functions | pass: terms and clauses knot-free; all 300 random functions knotted |
| Rule 102's light cone: least knot 2 + w(T), T ≤ 6 (A) | T = 7, 8 | **the cone is too small at T = 7**: it gives 5, while a window reaching one cell further gives 4 = 2 + w(7). T = 8 passes. The claim, scoped to T ≤ 6, was corrected before publication to say so |
| The census classes at T ≤ 6 (B) | The census at T = 7 (88 rules, 15 cells) | pass for the knot-free and one-knot classes, and rule 184's knots are again all 6,435 sets of 8 cells; 46 of the 49 growing rules grew again, while rules 7, 33 and 156 levelled off or dropped (12 → 12, 26 → 24, 24 → 23), so "growing" describes lags 1 to 6 only |

## Correction (2026-11-08)

Logged in `docs/CORRECTIONS.md` as a narrowing, after publication. As first published, the answer read "A process knows its past
only pairwise, ties and no knot, exactly when each future value is a single AND or OR", and conclusion 5 said that the 15 knot-free
rules' "memory is only pairwise".
- **What is true.** That holds for the knots joining one future cell to the first row, which Theorem 2 proves and the census counts
  (A30). Through intermediate rows it fails.
  - **Rule 128.** Each cell becomes the AND of three, so no future value has a knot with the first row, at any lag. But its image
    never shows 1 0 1: two cells on at time 1, two apart, force the cell between them on. A cell on at time 2 forces its three cells
    at time 1 on, so x(1, 1) and x(2, 4) on force x(1, 2) on. That knot joins two times.
  - **The census's knot-free rules, read on their whole law** (`space_time_knots.py`, `space_time_knots.json`: cones of first-row
    windows of 7 to 11 cells, T ≤ 3). Rules 128, 136 and 160 have knots joining two times, and rule 32 has knots inside one later
    row. The other eleven, 0, 2, 4, 8, 10, 12, 15, 34, 51, 170 and 204, show no knot: none at all with a 7-cell window and T = 3,
    and none of up to five places in the larger windows.
  - **Windows.** A window's cone is a projection of the whole law, and a set's verdict depends only on the projection on it. So every
    knot found in a window is a knot of the law, while a window without one shows nothing beyond itself.
- **What stands.** Theorems 1 to 3, Life's step, every count of the census, and the stress test, which are all statements about the
  two-time law.

## Literature and provenance

- **Sources.**
  - **Implicants and certificates** of Boolean functions are classical (certificate complexity: Buhrman and de Wolf, 2002). Theorem
    2's terms and clauses are elementary.
  - **Linear automata.** Pascal's triangle mod 2 (Lucas), Frobenius over GF(2), and Ledrappier's shift (1978) with its Frobenius
    triangles (`LOGIC-AXIS-20261107-001B`) are known.
  - **The elementary automata** are Wolfram's (1983). Rule 184 is the traffic rule, and rule 232 is majority.
- **Classification.** Known-with-delta. The mathematics is classical. New as far as found are:
  - the reading under K1–K3 (knots across time are minimal decisive sets, and pairwise memory is exactly the single ANDs and
    ORs);
  - the census of the elementary automata by their knots across time;
  - the uniform knot family of the traffic rule.
- **Where the ideas came from.** The question is the owner's question 4. Life is the owner's example.

## Workspace assumptions

- **Relied on.** A3 (verdicts from allowed states) and A6 (erasure is forgetting).
- **Taken by default.** A process's memory is read from its two-time knots: one future cell with the first row (new entry A30).
  Knots through intermediate rows and with several future cells are counted only for the linear rules. The correction above shows
  that the two readings differ.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families changed conclusions: A (a proof) and B (an exploratory census). One stress-test pass also
  counts.
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — what knots a process has across time | **Status:** Successful | Minimal decisive sets; pairwise memory of the first row exactly the single ANDs and ORs |
| Local direction — one process's memory | Continue | Its knots are characterized; joining two processes is the open step |
| Broader exploration — G5 and G16 lines | Known alternatives | Knots between processes; learning a rule from its knots |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | The static definition survives processes, and K1–K3 reads their memory |

**Corrections:** none at closure; one narrowing the same day, after publication (above): pairwise memory is of the first row only.
**Goals:** a G5 checkpoint (capability gained); backlog B7 marked taken. **Assumptions:** A30 added (a process's memory is read
from its two-time knots).

- **What the attempt leaves open.** Knots through intermediate rows and with several future cells were counted only for linear
  rules, and Life only at one step.
- **The missing bridge to the program's first emergence.** A knot between two processes: two loops, each changing in time, joined
  by a contact.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Knots between processes (G5) | 2/3 — Substantial | 2/3 — Testable | Two rings coupled by one contact cell; the contact's knots across time over both pasts → which couplings bind both loops | Selected · started |
| 2 | Learning a rule from its knots (G16) | 2/3 — Substantial | 1/3 — Stated | Whether the knots across time and their settings determine an elementary rule → a reconstruction, or two rules with the same knots | Alternative · deferred |
| 3 | The traffic rule's uniform knots | 1/3 — Incremental | 3/3 — Ready | Prove that every T + 1 cells decide rule 184's cell → a theorem | Alternative · deferred |
| 4 | Life at two steps | 1/3 — Incremental | 2/3 — Testable | Minimal decisive sets on 25 cells by a prime-implicant search → the knot sizes | Alternative · deferred |

1. **Knots between processes.**
   - **Payoff 2.** The program's first emergence is a knot between two loops. With loops as processes, the question is which
     contacts bind two changing loops so that the contact's future needs both of their pasts.
   - **Concreteness 2.** Theorem 1 applies at once: the contact's future value has its minimal decisive sets over both rings'
     pasts.
   - **Uncertainty.** Whether binding persists or decays with time.
   - **Status.** Bound: one epic. Started in this thread under the standing mandate.
2. **Learning a rule from its knots.**
   - **Payoff 2.** It touches the owner's new goal G16, learning the rules behind a shape.
   - **Concreteness 1.** No method yet. The knots with their settings do determine F_T, but learning from trajectories is another
     question.
3. **The traffic rule.**
   - **Payoff 1.** A clean curiosity.
   - **Concreteness 3.** Computed to T = 7, and the ballot structure of rule 184 is known.
4. **Life at two steps.**
   - **Payoff 1.** It extends the owner's example.
   - **Concreteness 2.** It needs a prime-implicant search over 25 cells.

## Final report as sent

Sent to the owner on 2026-11-08 at 07:52 UTC and copied here verbatim.

Knots across time (B7) is closed and published. A process written as its space-time law is just a static law on its trajectories, so the knot test works unchanged. Its knots with its first row are exactly the smallest sets of past cells that decide a future cell. Memory of the first row is only pairwise exactly when each future cell is a single AND or OR. [Decision note](https://github.com/jscul/knotlab/blob/main/research/TIME-KNOTS-20261107-001/time_knots.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt | Successful | Minimal decisive sets; linear rules keep one knot per power of two; Life's step knots four neighbours, never the cell itself |
| Local direction | Continue | One process is characterized; joining two is open |
| G5 Dynamics (question 4) | Capability gained | The static definition survives processes |

**Next step:** Continue, with #1 started.

| # | Direction | Payoff | Concreteness | Status |
| --- | --- | --- | --- | --- |
| 1 | Knots between processes: two rings joined by a contact cell | 2/3 | 2/3 | Started |
| 2 | Learning a rule from its knots (G16) | 2/3 | 1/3 | Deferred |
| 3 | Prove the traffic rule's uniform knots | 1/3 | 3/3 | Deferred |
| 4 | Life at two steps | 1/3 | 2/3 | Deferred |

**Corrections:** one, a Narrowing, found right after publishing. I had said these processes remember their past "only pairwise". That holds only for knots with the first row. Rule 128 (each cell the AND of three) still forms a knot joining two later times, because it never produces the pattern 1 0 1 ([correction](https://github.com/jscul/knotlab/blob/main/research/TIME-KNOTS-20261107-001/time_knots.md#correction-2026-11-08)).
**Goals:** a G5 checkpoint; B7 marked taken; G1 marked active for the collar-law thread.
**Assumptions:** A30 added: a process's memory is read from its two-time knots, and its first test already shows the two readings differ.
