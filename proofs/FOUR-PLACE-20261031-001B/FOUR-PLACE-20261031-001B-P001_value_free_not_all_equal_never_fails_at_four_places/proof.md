# Value-free not-all-equal never fails on k-regular systems for k ≥ 4

Status: Proved

Ticket `FOUR-PLACE-20261031-001B`, 2026-10-31.

## Statement

**Theorem.** Let k ≥ 4. Take a k-regular k-uniform system (every line has k distinct points, every point lies on k lines) with any
signs on its incidences. Then some colouring makes every line not-all-equal in its literals.

**At k = 3** the same law fails, exactly on the knot's spaces: the systems whose signed incidence matrix is sign-nonsingular
(Pfaffian).

## Dependencies

- **`FOUR-PLACE-20261031-001A`.** The library and the census: k = 4, n ≤ 7, every signing satisfiable.
- **`PINNING-20261031-001C`.** The cubic instance of Lemma 1: on all 1,380,864 signings of cubic systems with n ≤ 6, failure ⟺
  sign-nonsingular.
- **External, not replayed.**
  - Thomassen (1992), "The even cycle problem for directed graphs", J. AMS 5: a strongly connected digraph with minimum in- and
    out-degree at least 3 is even, i.e. it has a directed cycle of even weight under every 0/1 arc weighting.
  - Seymour (1974), on the two-colouring of hypergraphs.
  - The correspondence between sign-nonsingular patterns and even digraphs (Bassett–Maybee–Quirk; Klee–Ladner–Manber).

## Lemma 1 (signed Seymour lemma)

**Statement.** Let a signed system be not-all-equal-unsatisfiable and minimal (dropping any line makes it satisfiable). Let V be the set
of points its lines cover. Then:
- it has at least |V| lines;
- with exactly |V| lines, every real matrix with its signed incidence pattern is nonsingular. Here the pattern has entry sign s_{ℓ,v} at
  each incidence and 0 elsewhere.

**Proof.**
1. **The setup.** Suppose some real matrix B with the pattern has a nonzero kernel vector x. This always happens with fewer lines than
   points, and with equally many whenever B is singular. Let P be the set of points with x_v ≠ 0.
2. **Lines meeting P.** For such a line, Σ_v B_{ℓ,v} x_v = 0 has nonzero terms of both signs.
3. **Colour P by sign.** Set c_v = [x_v > 0]. A literal's value is c_v ⊕ [s_{ℓ,v} < 0] = [B_{ℓ,v} x_v > 0]. So every line meeting P
   shows both literal values, whatever the other colours are.
4. **The rest.** The lines missing P form a proper subset, since some line meets P. By minimality they are satisfiable. They touch only
   points outside P, so their colouring combines with c on P.
5. **Conclusion.** The whole system is satisfiable, a contradiction. So no such B and x exist. ∎

## Lemma 2 (failing regular systems are square)

**Statement.** In a k-regular k-uniform signed system, every minimal unsatisfiable set of lines E′ covers exactly |E′| points. It also
contains every line through those points, so it is a union of components.

**Proof.** By Lemma 1, |E′| ≥ |V′|. Counting incidences, k|E′| = Σ_{v ∈ V′} deg_{E′}(v) ≤ k|V′|. So equality holds throughout, and each
v ∈ V′ has all k of its lines in E′. ∎

## Lemma 3 (no sign-nonsingular k-regular pattern, k ≥ 4)

**Statement.** The incidence pattern of a k-regular k-uniform system with k ≥ 4 is not sign-nonsingular.

**Proof.**
1. **The digraph.** By Hall's theorem the incidence graph has a perfect matching. Put it on the diagonal. The digraph D has an arc from
   the point matched to line ℓ to each other point of ℓ. Every in- and out-degree of D is k − 1 ≥ 3.
2. **Strong components.** In a regular digraph every weak component is strongly connected.
3. **The correspondence.** A pattern with a nonzero diagonal is sign-nonsingular iff, after normalising the diagonal, every cycle of D
   has the sign that the determinant expansion requires. Equivalently, there is a 0/1 weighting of D under which every cycle has odd
   weight.
4. **Thomassen.** D is even (Thomassen 1992), so no such weighting exists. ∎

## Proof of the theorem

1. A failing system would contain a minimal unsatisfiable subsystem.
2. By Lemma 2 that subsystem is a square k-regular k-uniform system.
3. By Lemma 1 its pattern is sign-nonsingular, which Lemma 3 rules out. ∎

**Why three is different.** At k = 3, D has degree 2. Such digraphs need not be even, and the systems whose digraph is not even (the
Pfaffian ones) are exactly where not-all-equal fails: the knot's spaces. Thomassen's degree threshold, 3, is exactly the step from
three-place to four-place lines.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; ticket A and PINNING C Proved. | pass |
| 1 | Lemma 1 on 150 random unsatisfiable signed systems (lines of 2 to 4 points): every minimal unsatisfiable set of lines has at least as many lines as points, and with equality |det| = #PM. | 150/150 |
| 1b | The cubic instance (PINNING C): failure ⟺ sign-nonsingular on 1,380,864 signings. | pass |
| 2 | No incidence graph of the 20 systems with n ≤ 7 has a sign-nonsingular signing (all signings up to row and column sign changes). Their digraphs have in- and out-degree 3 and strong weak components. Control: the Fano plane (cubic) has one. | pass |
| 3 | k = 4: every signing of every system with n ≤ 7 is satisfiable (ticket A). k = 5: every signing of K5,5 (16⁵) and of K6,6 minus a perfect matching (16⁶) is satisfiable. | pass |
| 4 | Rigidity, observed: every not-all-equal piece with three to five internal points accepts not-all-equal (14 states) or everything. | pass |

## What this does not establish

- **Counting.** The theorem says nothing about counting solutions.
- **Rigidity at every size.** Observed only up to five internal points.

## Novelty

- **The plain case.** Thomassen (1992); Alon–Bregman for k ≥ 8.
- **The signed case.** It follows from Thomassen's even-digraph theorem through Seymour's linear-algebra argument. No explicit statement
  was found in the sources checked, so folklore risk is moderate.
- **The reading.** "The knot's law fails only at three places because Thomassen's threshold is three" is ours.
