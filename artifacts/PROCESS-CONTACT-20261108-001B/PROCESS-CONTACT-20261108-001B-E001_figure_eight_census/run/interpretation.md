# Rings that share their contact cell: interpretation

Experiment `PROCESS-CONTACT-20261108-001B-E001` (exploratory), run 2026-11-08 under the frozen contract: 128,128 configurations in
7 s on 16 workers. Every verdict is exact at every lag: the joint dynamics was iterated until its T-step map repeated (at most 3,865
lags). Rows are in `rows.json`, totals in `result.json`.

## Controls

All three pass.
- **Linear algebra.** Linear and affine rules with a parity combiner give an affine system, and its verdict at every computed lag
  equals the linear-algebra one: the contact's row of M^T meets both rings.
- **One-sided combiners.** Constant and one-input combiners never bind.
- **Decisive sets.** On a sample, the lag-1 verdicts agree with the minimally decisive sets.

## Lag 1, by an elementary argument

Let n ≥ 3 and c(1) = g(P_A, P_B), with P_A = f_A(a_{m−1}, c(0), a_1) and P_B = f_B(b_{n−1}, c(0), b_1). A setting of ring A's own
cells and c(0) fixes P_A, while b_{n−1} and b_1 stay free.
- **When ring A's side decides.** Ring A's side decides c(1) exactly when some value P_A can take makes g constant on the values
  that f_B(·, c(0), ·) takes. Ring B's side is the mirror case.
- **The verdict.** The contact binds at lag 1 exactly when g is a parity and neither rule is *canalizing at its centre*, meaning
  that neither f(·, 0, ·) nor f(·, 1, ·) is constant.
- **The two failures.**
  - If g is canalizing in one input, that ring can take the canalizing value.
  - If a rule is canalizing at its centre, the contact's own first value fixes that ring's proposal, and then the other ring's side
    decides c(1).
- **In the census.** The census agrees on every configuration. 65 of the 88 rule classes are not canalizing at their centre.

So no combiner other than a parity binds at every lag, as the contract stated.

## Primary observable

Configurations by class. Rows marked "alike" have both rings on one rule at four sizes, 352 per combiner. Rows marked "mixed" pair
distinct rules at 3 + 4 cells, 7,656 per combiner.

| Combiner | Rings | Every lag | From some lag on | Recurring | Decays | Never |
| --- | --- | --- | --- | --- | --- | --- |
| XOR | alike | 16 | 8 | 57 | 184 | 87 |
| XNOR | alike | 16 | 7 | 54 | 185 | 90 |
| XOR | mixed | 7 | 23 | 1,004 | 3,194 | 3,428 |
| XNOR | mixed | 5 | 42 | 1,079 | 3,147 | 3,383 |
| the other 12 | both | 0 | 53 in all | in result.json | | most |

- **Binding at every lag.** 44 configurations, all with a parity combiner.
  - **Linear rules at particular sizes.** 60 at 3 + 4, 4 + 4 and 5 + 6; 90 at 5 + 6; 150 and 105 at 4 + 4 and 4 + 5.
  - **Nonlinear rules.** 22, 28, 54, 62, 73, 108 and 126 at 4 + 4, and 7, 23, 28, 94, 108, 154 and 156 at 5 + 6; only 28 and
    108 do so at two sizes.
  - **Mixed pairs.** 9 with 24, 15 with 134, 26 with 36, 156 with 105 and with 150, and 170 with 134; and 105 and 150 with 90.
  - **No rule at every size.** No rule binds at every lag at all four sizes.
- **Decay is the rule.** With a parity combiner and neither rule canalizing at its centre, 6,682 of 8,840 configurations bind and
  then stop, 5,150 of them after lag 1 alone. 2,052 bind at recurring lags only. Rule 30 at 5 + 6 binds for 38 lags and then stops.
  When binding fails, one ring's side, with the contact's own past, sets the contact's future.
- **H1 fails.** 53 configurations with a non-parity combiner bind from some lag on, first binding at lag 3 to 13. OR, NOR, NAND,
  AND and the four mixed implications all occur. Feedback lets a canalizing combiner bind, as memory did for the listening contact
  (ticket A, check 4).
- **H2 fails, overwhelmingly.** For parity combiners:

  | Listening counterpart | Shared contact binds at every lag | Fails |
  | --- | --- | --- |
  | Binds at every lag | 36 | 13,068 |
  | Fails | 8 | 2,904 |

  - **Sharing breaks binding.** Sharing the contact breaks almost every binding that a listening contact keeps forever.
  - **Sharing can also rescue it.** In 8 configurations a ring that would forget alone keeps binding when it shares the contact:
    rule 60 on 4 cells, nilpotent alone (ticket A's Theorem 5), binds at every lag at 3 + 4 and 4 + 4. So do 105 and 150 with a
    rule-90 ring of 4 cells.

## Reading against the decision rule

- **Shared identity costs persistence.** A contact that is a cell of both rings, as the contact gate's shared identity asks, feeds
  each ring the other's past and its own. Its own past then competes with both loops:
  - with a rule canalizing at its centre it settles its own future at once;
  - otherwise one ring usually learns to steer it within a few lags.
- **Persistence is rare and size-dependent.** In 44 of 128,128 configurations the contact binds both rings at every lag, and no rule
  does so at every size.
- **Against ticket A.** A listening contact binds forever whenever it is a parity and both rings remember. The difference is the
  feedback.

## Nonclaims

- **Declared sizes only.** The ring sizes are those declared, the stress test one size past included.
- **Two-time knots only.** Binding is read from the contact's knots with the first row (A30).
- **One combiner family.** The contact combines the two rings' proposals. Other shared-contact laws, such as a parity of its four
  ring neighbours that ignores its own value, are not covered.
