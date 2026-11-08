# Knots across time are minimal decisive sets

Status: Proved by hand. The finite claims (the 88 elementary rules, all Boolean functions of up to four inputs, the linear rules,
the light cone of rule 102, Life's step) are checked by computation with controls (`check.py`).

Ticket `TIME-KNOTS-20261107-001A`, 2026-11-08.

## Standard statement

- **The setting.** A deterministic cellular automaton is written as one system of constraints. There is one Boolean variable per
  cell and time step, the first row is free, and every later cell equals the update rule applied to the cells below it. The
  allowed states are the trajectories. Let y be one cell's value after T steps, and F_T the Boolean function of the first row
  that computes it.
- **Knots.** A set of variables is a knot when the allowed states' projection on it excludes some assignment, while the projection
  on every set one smaller excludes none.
- **Decisive sets.** A set S of first-row cells is *decisive* when some assignment to S makes F_T constant. It is *minimally
  decisive* when no proper subset is decisive.

The results:

1. **Theorem 1.** The knots made of y and first-row cells are exactly S + {y} for the minimally decisive S with at least two
   cells. A decisive single cell gives a two-place tie, not a knot.
2. **Theorem 2.** A nonconstant Boolean function has no such knot exactly when it is a single conjunction or a single disjunction
   of literals.
3. **Theorem 3.** For a linear rule with update polynomial p over GF(2), F_T is the parity of the support of p^T. So there is
   exactly one knot of y with the first row: that support plus y. Its size is |supp p| + 1 at every lag T = 2^k (Frobenius). For
   rule 60, at a general lag it is 2^popcount(T) + 1 (Lucas).

## Nearest known result

- **Minimal certificates and prime implicants.** A decisive set's forcing assignment is an implicant of F or of ¬F. The minimal
  certificate is the subject of certificate complexity, and the decision-tree literature uses these words (Buhrman and de Wolf,
  2002).
- **Terms and clauses.** Theorem 2 is elementary.
- **Linear automata.** Rule 60's space-time diagram is Pascal's triangle mod 2 (Lucas's theorem). Ledrappier's shift is the
  space-time law of rule 102, which is rule 60 reflected, and its minimal relations are the Frobenius triangles
  (`LOGIC-AXIS-20261107-001B`).
- **Classification.** Known-with-delta. The pieces are classical. The delta is their reading under K1–K3:
  - a process's knots across time are the minimal decisive sets of its future values;
  - the processes whose memory is only pairwise are exactly the single ANDs and ORs;
  - linear processes bind a cell to its past at every power of two with a knot of fixed size.

## Setting

- **The space-time law.** For an elementary automaton (Wolfram's numbering: a cell's new value is bit 4a + 2b + c of the rule,
  where a, b, c are the left, own and right values), there is a variable x(t, i) for each time t ≥ 0 and cell i.
  - **Constraints.** x(t + 1, i) = f(x(t, i − 1), x(t, i), x(t, i + 1)).
  - **Allowed states.** The trajectories. The first row is free, and every other value is a function of it.
  - **Lags.** Cell 0's value y = x(T, 0) depends on the 2T + 1 cells −T..T of the first row through F_T.
- **The two-time law.** This is the projection of the space-time law on the first row and y. Projecting out the intermediate rows
  leaves the graph of F_T, so every knot of the two-time law is a knot of the space-time law.
- **The test.** K1–K3 is applied to allowed states, with erasure as forgetting. Knots are minimal constrained sets of at least
  three variables, which `GROWTH-LAW-20261107-001A`'s enumerator computes independently.

## Theorem 1 (knots across time are minimal decisive sets)

Let F be any Boolean function of inputs X, and R the graph relation {(u, F(u))} over X + {y}.

- A set of inputs alone is never constrained, since the inputs are free.
- A set S + {y} with S ⊆ X is constrained exactly when S is decisive. Its projection misses (a, b) exactly when every completion of
  a gives F = ¬b.
- S + {y} satisfies K2 exactly when S is minimally decisive.
  - Forgetting y leaves S free.
  - Forgetting s ∈ S leaves (S − s) + {y}, which is free exactly when S − s is not decisive.
  - Decisiveness is monotone, since a forcing assignment extends to any superset. So no set one smaller being decisive means no
    proper subset is decisive.
- K3 holds since R is nonempty.

So the knots of R are exactly S + {y} with S minimally decisive and |S| ≥ 2. For |S| = 1 the pair is a two-place tie. ∎

**Computed (check 1).** On all 88 elementary rules (up to reflection and complement) at T = 1 and 2, and on 300 random functions
of 5 and 6 inputs, the generic enumerator's knots equal the minimally decisive sets plus y: 476 maps, no mismatch. The control
counts every decisive set of size two or more, minimal or not, and it disagrees on rule 30 at T = 2.

## Theorem 2 (memory that is only pairwise)

A nonconstant F has no knot in its graph exactly when F is a single conjunction of literals (a term) or a single disjunction (a
clause).

*Proof.*
- **Terms and clauses have none.** For a term, setting any one of its literals false forces F = 0, so every variable is a
  decisive singleton and every decisive set contains one. A clause is the dual case.
- **Suppose every minimally decisive set is a single cell.**
  - **The forced value.** [n] is decisive, so some cell j is decisive alone.
  - **A literal.** If one cell forces both values, F is that literal.
  - **One forced value.** Otherwise each decisive cell j has one forcing value c_j and one forced value v_j. These are all equal,
    to v say: two cells forcing opposite values could be set together, a contradiction. Take v = 0; v = 1 is the dual case.
  - **A term.** Let C be the inputs where every decisive cell takes its non-forcing value. Outside C, F = 0. If F = 1 on all of C,
    then F is the term "every decisive cell non-forcing".
  - **Otherwise a contradiction.** F restricted to C is a function G of the other cells, and G is nonconstant, or F would be
    constant. Take any set S of other cells that fixes G to 0. It fixes F to 0 everywhere, so S is decisive for F. But S contains
    no decisive cell of F, so a minimally decisive subset of S has two or more cells, against the assumption. ∎

**Computed (check 2).** Every nonconstant function of 2, 3 and 4 inputs agrees with the theorem. Of them, 12 of 14, 46 of 254 and
152 of 65,534 are knot-free, and these are exactly the terms and clauses. All 484 terms and clauses of 5 inputs are knot-free, and
300 random 5-input functions agree.

## Theorem 3 (linear processes)

- **The law.** For a linear rule with update polynomial p, the space-time law is a linear code over GF(2). Its knots are the
  supports of its minimal dual words of size at least three.
- **The one two-time knot.** By induction x(T, ·) = p^T x(0, ·), so F_T is the parity of supp(p^T).
  - **Only the whole support decides.** A parity of a set S0 is fixed only when all of S0 is set. So S0 is the only minimally
    decisive set, and the two-time law has exactly one knot, S0 + {y}.
  - **Frobenius.** Over GF(2), p^(2^k)(X) = p(X^(2^k)). So at every lag 2^k the cell is knotted to |supp p| first-row cells,
    2^k apart: a knot of |supp p| + 1 places at every power of two.
  - **Lucas.** For rule 60 or 102, p = 1 + X and |supp (1 + X)^T| = 2^popcount(T).
- **Intermediate rows give smaller knots.** Ledrappier's law is rule 102's space-time law. Its minimal relations through a cell and
  its value T steps on have at most 2 + w(T) points, w the non-adjacent-form weight (`LOGIC-AXIS-20261107-001B`). This is less than
  the two-time 2^popcount(T) + 1 whenever T has two or more binary digits.
- **Affine rules.** Rules 105 and 195, the complements of 150 and 60, add a constant to each update, and their knots are the same.
  ∎

**Computed.**
- **Two-time knots (check 3).** For rules 60, 102, 90, 150, 105 and 195 at T = 1..6, there is exactly one two-time knot, the support
  of p^T plus y, with |supp p| + 1 places at T = 1, 2 and 4. Lucas's count holds for T ≤ 32.
- **Intermediate rows (check 4).** In rule 102's past light cone, the least knot through (0, 0) and (T, 0) has exactly 2 + w(T)
  places for T = 1..6.
- **The cone is too small at T = 7 (stress test).** There the cone's least knot has five places. The whole law has the four-place
  relation of `LOGIC-AXIS-20261107-001B`, {(0, 0), (0, 8), (7, 0), (7, 1)}, which leaves the cone sideways through a second cell
  at time 7. So the least knot across time is not confined to the light cone, and knots with two future cells can be smaller than
  any with one.

## Proposition 4 (Life's step)

In Conway's Life the knots joining a cell's next value to the present are exactly the 70 sets of four of its neighbours, with that
value. There are no ties, and the cell's own present value lies in no knot.

*Proof.* The rule is a function of nine cells, so the minimally decisive sets are found by checking every subset (check 5).
- **Four neighbours decide.** Four live neighbours force death by overcrowding, whatever the rest.
- **Three cells never decide.** Whichever three cells are set, the remaining neighbours can make the count three or not.
- **The cell itself is never needed.** A set that decides through the cell's own value must also pin the neighbour count. That
  takes four neighbours set alive, or all eight, and either contains a decisive set of four neighbours. ∎

**Computed (check 5).** Exactly 70 knots of five places; no ties; the centre is in none.

## Reading

**Interpretation, not a theorem.**
- **For question 4.** The static definition survives the change to processes. A process written as a law is a static law on its
  trajectories. Its knots across time are the minimal sets of past cells that, set suitably, decide a future cell, while no smaller
  set decides it.
- **Pairwise memory.** A future cell that is a single AND or OR of past cells knows its past only pairwise: only ties, no emergence
  under K1–K3. Every other future cell binds its past in a knot. This is the program's two/three boundary, read across time.
- **Linear memory.** A linear process keeps a fixed-size knot with its past at every power of two, so it never forgets: the
  Frobenius triangles of Ledrappier's law, read in time.
- **Life.** Its step binds a cell's future to four neighbours at a time, never to the cell's own present.

## Checks

`check.py`, with `time_knots_lib.py`, runs in about 15 s on the repository's `.venv` and reproduces `result.json`.

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream proofs Proved | pass |
| 1 | Theorem 1 on 476 maps against the generic enumerator; control | pass |
| 2 | Theorem 2 on every nonconstant function of ≤ 4 inputs, all terms and clauses of 5, 300 random of 5 | pass |
| 3 | Theorem 3 on six linear and affine rules, T ≤ 6; Lucas, T ≤ 32 | pass |
| 4 | Rule 102's light cone: least knot 2 + w(T), T ≤ 6 (at T = 7 the cone gives 5; see the stress test) | pass |
| 5 | Life's step: 70 knots of four neighbours | pass |

## Nonclaims

- **Two-time knots only.** Theorems 1 and 2 concern knots made of one future cell and first-row cells. Knots through several
  future cells, or through intermediate rows, are counted only for the linear rules.
- **No physics.** No physical time or dynamics is claimed.
