# Knots separated by one port are 2-sums

Status: Proved (for any near side and any removal; checked on plane and non-planar splices)

Ticket `PLANAR-THEOREM-20261102-001B`, 2026-11-02.

## Question

- **The premise to prove.** Every new knot at an opened cut is a pinned-and-separated three-point knot through the hub.
- **This ticket's step.** It takes the simplest way a crossing knot can carry its constraint across the cut: through a single port.
  Are such knots always built from one-sided knots?

## Dependencies

- **`PLANAR-THEOREM-20261102-001A`.** The epic's first step (not used in the proof; bound for lineage).
- **`HANDLE-EMERGENCE-20261102-001B`, Lemma 1 (the join).** For a near set U and a far set V, the pattern (u, v) occurs iff
  T(u) ∩ T(v) ≠ ∅. Here T(u) is the set of port patterns compatible with U = u, and likewise T(v).
- **`SPLICE-TREE-20261102-001C`.** Circuits, tie classes, and the closure by class-level eliminations (`elim_lib.py`).

## Setting

- **The glued space.** Two knot spaces are glued along a simple 3-edge cut with ports X. Any line on the near side is removed.
  - The solution set is closed under complement, since signed NAE is.
  - So every point takes both values.
- **The knot.** K is a crossing knot (a circuit of three or more points) with near part U (on the near side, ports allowed) and far
  part V. It meets both near non-port points and far points.
- **Separated by one port.** An excluded pattern (u, v) of K is separated by the port y when every pattern in T(u) has y = β and
  every pattern in T(v) has y = β̄.

## The lemma

**If an excluded pattern of K is separated by the port y, then:**
- **(a)** y is not in K;
- **(b)** U + y and V + y are circuits;
- **(c)** K is their elimination through y: K = (U + y) ∪ (V + y) − y.
- **(d) Two cases.**
  - **Degenerate.** If y is tied to a point of K, that point is alone on its side, and the circuit on that side is the tie. K is then
    tie-equivalent to the other circuit, which is one-sided.
  - **Otherwise,** both circuits are one-sided knots, and K arises from them by one class-level elimination of the closure.
- **Either way,** K is generated: it is never new.

*Proof.*

**Both parts are nonempty, and proper subsets occur in full.** K is a circuit, so every proper subset is unconstrained and every
pattern on it occurs. In particular T(u) and T(v) are nonempty.

**(a) y is not in K.**
- Ports lie on the near side, so y is not in V.
- Suppose y ∈ U. Then every pattern in T(u) has y = u_y, so β = u_y.
  - **If U = {y}.** Then K = {y} ∪ V lies on the far side with the ports, so K is not crossing.
  - **Otherwise.** V + y is a proper subset of K, so (v, y = β) occurs, so T(v) contains a pattern with y = β. This contradicts the
    separation.

**(b), first half: U + y and V + y are constrained.**
- A solution with U = u has its port pattern in T(u), so it has y = β. Hence (u, y = β̄) never occurs.
- Likewise, (v, y = β) never occurs.

**(b), second half: they are minimal.**
- Suppose W ⊊ U + y is constrained.
  - W must contain y, since subsets of U are proper subsets of K. So W = U′ + y with U′ ⊊ U.
  - U′ is nonempty, since every point takes both values.
- **What W excludes.** W excludes some pattern (u′, β′). By complement symmetry it also excludes (ū′, β̄′). So:
  - every pattern in T(u′) has y = β̄′;
  - every pattern in T(ū′) has y = β′.
- **What K's minimality gives.** U′ ∪ V is a proper subset of K, so (u′, v) and (ū′, v) both occur. By the join lemma, T(v) meets
  both T(u′) and T(ū′). So T(v) contains patterns with y = β̄′ and with y = β′.
- **The contradiction.** T(v) has y = β̄ throughout.
- **The other half.** The same argument with the sides exchanged shows that V + y is minimal. ∎(b)

**(c)** This follows from (a).

**(d) The tie classes.**
- **A knot holds no tie.** A knot of three or more points never contains two tied points, since the tie would be a smaller
  constrained subset.
- **The degenerate case.** Suppose y is tied to k ∈ U.
  - Then {k, y} ⊆ U + y is constrained. Since U + y is a circuit, U + y = {k, y}, so U = {k}.
  - Replacing k by its tie partner y turns K into V + y. So K is tie-equivalent to a circuit on the far side with the ports.
  - The case k ∈ V is symmetric.
  - y cannot be tied to points on both sides, since then K would have two points.
- **The non-degenerate case.** Suppose y's tie class misses K.
  - Then |U| ≥ 2: if U = {u}, the circuit U + y = {u, y} would be a tie.
  - Likewise |V| ≥ 2.
  - So both circuits are knots, of sizes |U| + 1 and |V| + 1, each on one side with the ports.
  - In tie classes, A = [U + y] and B = [V + y] pass through y's class h, which is outside [K], and A ∪ B = [K] + h.
  - This is exactly one step of the closure (`elim_lib.closure`). ∎

## Checks

`check.py` (`result.json`, about a minute).
- **The splices.** Near sides: census 6, 14, 38 and 45 (plane), census 21 and 58 (non-planar), and two 10-point plane spaces. Far
  sides: K4^(3), census 6, the Fano plane and census 58. Gluing lines 0 and 1, every near removal.
- **The test.** For every crossing knot with a single-port-separated excluded pattern, and every separating port: the port is outside
  the knot, and the knot is the stated 2-sum or the stated degenerate case.

| Near sides | Removals | Separated crossing knots | Class-level 2-sum | Only degenerate |
| --- | --- | --- | --- | --- |
| Plane | four-pattern | 15,076 | 8,247 | 6,829 |
| Plane | six-pattern | 11,538 | 9,548 | 1,990 |
| Non-planar | four-pattern | 1,362 | 794 | 568 |
| Non-planar | six-pattern | 5,580 | 4,556 | 1,024 |
| **Total** | | **33,556** | **23,145** | **10,411** |

All 33,556 are as stated.

## What this does not establish

- **The remaining crossing knots.** A crossing knot may have no excluded pattern separated by one port. Its constraint then crosses
  through two or three ports jointly. Ticket C classifies these.

## Novelty

- **New here.** The lemma.
- **Classical analogue.** It is the non-linear analogue of the 2-sum of matroid circuits across a 2-separation. The proof uses only
  complement symmetry and minimality.
