# When a shared contact binds at the first step

Status: Proved by hand. The finite claims are checked exhaustively on small rings (`check.py`).

Ticket `SHARED-CONTACT-20261108-001A`, 2026-11-08.

## Standard statement

- **The setting.** Two rings share one contact cell c: ring A is c, a_1, …, a_{m−1} and ring B is c, b_1, …, b_{n−1}, with
  m, n ≥ 3, each closed through c. Every non-contact cell updates by its ring's elementary rule, so both rings read c.
- **Binding.** As in `PROCESS-CONTACT-20261108-001A`: the contact binds both rings at lag T when every minimally decisive set of
  c(T) over the joint first row meets both rings' own cells. Equivalently, neither ring's first row with c(0) decides c(T)
  (Theorem 1 there, whose proof uses only that every value is a function of the first row).
- **Two contact families.**
  - **Proposals** (assumption A31): c(t + 1) = g(f_A(a_{m−1}, c, a_1), f_B(b_{n−1}, c, b_1)), g a two-input law.
  - **Self-blind:** c(t + 1) = h(a_{m−1}, a_1, b_{n−1}, b_1), h a four-input law that does not read c. Its *parities* are
    h = u(a_{m−1}, a_1) + v(b_{n−1}, b_1).
- **Canalizing at its centre.** A rule f is canalizing at its centre when f(·, 0, ·) or f(·, 1, ·) is constant: one value of the
  cell's own state fixes its next value.

The results:

1. **Theorem 1.** A proposal-combining contact binds both rings at lag 1 exactly when g is XOR or XNOR and neither rule is
   canalizing at its centre.
2. **Theorem 2.** A self-blind contact binds at lag 1 exactly when no setting of one ring's pair (a_{m−1}, a_1) or (b_{n−1}, b_1)
   makes h constant in the other's. Its parities bind at lag 1 exactly when u and v are nonconstant.
3. **Theorem 3.** Take linear or affine rules and an affine contact law (a parity combiner, or u and v affine). Then the shared
   system is affine, c(T) is the parity of the support of the contact's row of M^T plus a constant, and the contact binds at lag T
   exactly when that support meets both rings.

## Nearest known result

- **Canalizing functions** (Kauffman, 1969): every two-input function except XOR and XNOR is canalizing.
- **Boolean automata double-cycles.** Two cycles sharing one automaton have been studied by Demongeot, Noual, Sené and coauthors.
  The shared node's function there combines its two in-neighbours.
- **Classification.** Known-with-delta. The arguments are elementary. The delta is the reading of the contact gate across time:
  - at lag 1 a proposal-combining contact fails exactly when its own past fixes a ring's proposal;
  - a self-blind contact removes that failure.

## Theorem 1 (proposals at lag 1)

c(1) = g(P_A, P_B), where P_A = f_A(a_{m−1}(0), c(0), a_1(0)) and P_B = f_B(b_{n−1}(0), c(0), b_1(0)).
- **What a side fixes.** A setting of ring A's cells and c(0) fixes P_A and c(0). The two cells b_{n−1} and b_1 are distinct
  because n ≥ 3, and they stay free, so P_B ranges over V_B(c0), the set of values of f_B(·, c0, ·).
- **When it decides.** Ring A's side decides c(1) exactly when, for some c0 and some value p of f_A(·, c0, ·), g(p, ·) is constant
  on V_B(c0). Ring B's side is the mirror case.

*Proof.*
- **Parities.** If g is a parity, g(p, ·) is a bijection. It is constant on V_B(c0) exactly when V_B(c0) has one element, that is,
  when f_B is canalizing at its centre with value c0. So a parity binds exactly when neither rule is canalizing at its centre.
- **Other laws.** Every other g is canalizing in some input, say the first, with value v.
  - **Ring A can give v.** If f_A(·, c0, ·) takes the value v for some c0, that setting of ring A's side decides c(1).
  - **Ring A cannot.** Otherwise f_A(·, c0, ·) is constant and equal to the other value for both c0, so c(1) = g(1 − v, P_B)
    depends only on c(0) and ring B, and ring B's side decides it.
  - **The second input.** The case is symmetric. ∎

**Computed (check 1).**
- **Exhaustive.** All 7,744 ordered pairs of rule classes, all 16 combiners, rings of 3 + 3, 3 + 4 and 4 + 5 cells: 371,712 maps, no
  mismatch.
- **Which rules qualify.** 65 of the 88 classes are not canalizing at their centre.

## Theorem 2 (self-blind contacts at lag 1)

c(1) = h(x, y), with x = (a_{m−1}(0), a_1(0)) and y = (b_{n−1}(0), b_1(0)).

*Proof.*
- **What a side fixes.** A setting of ring A's cells and c(0) fixes x and leaves y free. So it decides c(1) exactly when h(x, ·) is
  constant on all four values of y. The mirror case holds for ring B.
- **The criterion.** So the contact binds exactly when h's 4 × 4 table has no constant row and no constant column.
- **Parities.** For h = u(x) + v(y), the row h(x, ·) = u(x) + v(·) is constant exactly when v is constant, and a column is constant
  exactly when u is. ∎

**Computed (check 2).**
- **All laws.** Of all 65,536 self-blind laws, exactly the 22,874 with no constant row or column bind at lag 1.
- **Parities.** Exactly 196 of the 256 parities bind, those with u and v nonconstant.
- **Ring rules.** The verdict does not depend on the ring rules, under 300 random pairs.

## Theorem 3 (the linear case)

*Proof.*
- **The system is affine.** With linear or affine rules and an affine contact law, every update is affine over GF(2). So the state
  map is s ↦ Ms + b, and c(T) is the parity of the support S_T of the contact's row of M^T, plus a constant.
- **Binding.** A parity of S_T is fixed by a setting exactly when the setting covers all of S_T. So ring A's side with c(0) decides
  c(T) exactly when S_T contains no cell of ring B, and the mirror case holds for ring A's cells. ∎

**Computed (check 3).**
- **The criterion.** The 16 linear and affine rules, with partners 150 and 90, both families with affine laws, rings of 3 + 4 and
  4 + 5 cells, and T = 1 to 12: 43,776 maps, no mismatch.
- **Affinity.** Every such system is affine.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream proofs Proved | pass |
| 1 | Theorem 1 on 371,712 maps | pass |
| 2 | Theorem 2 on all 65,536 self-blind laws; the parities; random ring rules | pass |
| 3 | Theorem 3 on 43,776 maps | pass |
| 4 | Two implementations of the self-blind dynamics agree; binding agrees with the minimally decisive sets (400 configurations) | pass |

## Reading

**Interpretation, not a theorem.** At lag 1 a proposal-combining contact fails for two reasons:
- its combiner canalizes, and the ring that gives the canalizing value decides alone;
- its own value enters a rule that is canalizing at its centre, and then its own past fixes a proposal.

A self-blind contact is still a cell of both rings, since both rings read it, but it keeps its own past out of its next value. Every
self-blind parity of nonconstant u and v binds at lag 1. Whether it keeps binding is ticket B's question.

## Nonclaims

- **Lag 1, and the linear case only.** Later lags of nonlinear systems are the census.
- **Two-time knots only** (A30).
- **No physics.** No physical time or dynamics is claimed.
