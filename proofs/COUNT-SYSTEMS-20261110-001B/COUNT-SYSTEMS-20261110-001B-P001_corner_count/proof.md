# The count is a linear count of corner parities

Status: Proved by hand; the finite claims are checked on K_2 to K_8 in `check.py`.

Words (2026-11-11). The statements use the literature's words for the knot sphere's triple system: a line {a, b, c} is a
knot and a point a distinction (Intuitions guide, Glossary); the lines of a cutting-planes refutation are lines of the proof.

Ticket `COUNT-SYSTEMS-20261110-001B`, 2026-11-10.

## Standard statement

- **The count.** NAE(K_k) as in `COUNT-NOTE-20261107-001B`: points with variables x_p, lines {a, b, c} with literals y_p = x_p ⊕ s_{l,p}
  and the two clauses (y_a ∨ y_b ∨ y_c), (¬y_a ∨ ¬y_b ∨ ¬y_c). The plane incidence graph is cubic, with L lines, n = L points and
  F = L + 2 faces; a **corner** of a line on a face is the pair of the line's points consecutive along the face, and every corner lies on
  one line and one face.
- **Corner atoms.** For a corner c = (l; a, b), e_c is the agreement of its two literals, e_c ↔ (y_a ≡ y_b): over F2, e_c = 1 + y_a + y_b,
  a 2-XOR of the points. Def is the four clauses defining every e_c.

**Theorem 1 (linear over corner atoms).** NAE(K_k) ∧ Def has a cutting-planes refutation with O(n) lines. Every line yields
Σ_{c∈l} e_c ≤ 1, every face Σ_{c∈f} e_c ≥ 1, and their sums contradict, since both sums are the same linear form and F − L = 2.

**Theorem 2 (every corner parity holds).** Under every assignment of the points, every line has 1 or 3 agreeing corners (1 exactly when
it is satisfied) and every face an odd number. So every corner parity the count states holds under every assignment. Its contradiction
is that a satisfied line has one agreeing corner and not three, which no count modulo 2 sees.

**Remark (the plain relaxations).** Over the points alone the linear relaxation is feasible at x ≡ 1/2, so any cutting-planes refutation
of NAE(K_k) itself must round. Over the corner atoms, with each line's and face's local inequality derived, the linear program is already
infeasible.

## Nearest known result

- **The degree-3 identity.** `COUNT-NOTE-20261107-001B`'s Sherali–Adams refutation is the same count with each corner agreement written
  as the quadratic 1 − y_a − y_b + 2y_ay_b. Theorem 1 is its linear form once those quadratics are named.
- **Classification.** Known-with-delta: elementary once the Euler count of `TWO-ROUND-BRIDGE-20261106-001B` is in hand. The delta is to
  separate the two ingredients, the corner atoms and the integer count, which cutting planes and Res(⊕) each have only one of.

## Proof of Theorem 1

**Lines.** On a line's six variables (three points, three corner atoms), Def and the line's two clauses imply e_1 + e_2 + e_3 ≤ 1: a
satisfied line has exactly one agreeing corner. An implication among a fixed number of 0/1 variables has a cutting-planes derivation of
size bounded by a constant (cutting planes is complete, and the Chvátal rank of a polytope in [0, 1]^6 is bounded). Check 2 confirms the
implication under all 8 assignments of every line's points on K_2 to K_8.

**Faces.** On a face, Def alone implies Σ e ≥ 1, because Kasteleyn's signs make the number of agreeing corners odd under every assignment
(`TWO-ROUND-BRIDGE-20261106-001B`, theorem 2). A face has at most three points, so this too has a constant-size derivation.

**The count.** Every corner lies on exactly one line and one face, so Σ_lines Σ_{c∈l} e_c and Σ_faces Σ_{c∈f} e_c are the same linear
form. Adding the line inequalities and subtracting the face inequalities gives 0 ≤ L − F = −2. Check 3 confirms, on K_2 to K_8, that
the two sums cancel coefficient by coefficient with constant 2 left over, and that the linear program over e ∈ [0, 1]^corners with the
derived inequalities is infeasible on K_2 to K_6. ∎

## Proof of Theorem 2

A line's three literals agree pairwise on 1 corner when they are not all equal and on 3 when they are. A face's number of agreeing corners
is odd by Kasteleyn's condition. Check 2 confirms both under every local assignment of every line and face on K_2 to K_8. Every parity is
odd, the only values are 1 and 3, and the contradiction needs "exactly one", so the count is invisible modulo 2. ∎

## Reading

**Interpretation, not a theorem.**
- **What each open system has.** Cutting planes adds and rounds, so it has the integer count, but the corner agreements are quadratic in
  the points, and it is open whether it can count them without naming them. Res(⊕) names every corner agreement as a linear form over F2,
  but every parity among them holds, so its linear algebra finds nothing and it would have to count within clauses of parities.
- **Against Tseitin and the pigeonhole principle.** Tseitin's contradiction is a parity, easy for Res(⊕); the pigeonhole principle's is a
  count of variables, easy for cutting planes. The sphere's count is a count of parities, and neither ingredient alone suffices.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Every corner on one line and one face, three per line, F − L = 2 (K_2 to K_8) | pass |
| 2 | Under every local assignment: 1 agreeing corner on a satisfied line, 3 on a violated one, an odd number on every face (K_2 to K_8) | pass |
| 3 | The line and face inequalities sum to 0 ≤ −2 coefficient by coefficient; the corner LP is infeasible (K_2 to K_6); x ≡ 1/2 satisfies the point LP | pass |

## Nonclaims

- **No lower bound for cutting planes or Res(⊕)** is claimed; the reading says what each system would have to do.
- **The constant-size local derivations are by completeness**, not written out.
