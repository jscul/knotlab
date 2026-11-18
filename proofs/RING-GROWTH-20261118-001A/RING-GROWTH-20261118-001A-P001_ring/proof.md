# The ring of five knots with one five-place knot

## Standard statement

The least closure of a five-cycle of even-parity constraints (four of arity four, one of arity five, consecutive constraints
sharing one variable) under the complete-round joining policy is, round by round, the product structure "cylinder position with a
set of lifts of the five-arity constraint below it"; the number of constraints formed in round t is
c(t) = Σ_v C(m(v), t − h(v)), and c(t) = c(t − 5) + c(t − 6), with growth rate the real root of x⁶ = x + 1.

## Nearest known result

`TOUCH-CENSUS-20261118-001` (the ring found growing faster than any power), `FIRST-KNOT-20261118-001A` and
`FRESH-COUNT-20261118-001A` (the policy, the fewest counts, the Birkhoff picture for one seed). The model below is the advisor's
(Fable 5.2, [answer](../../../research/RING-GROWTH-20261118-001/advisor/answer_1_fable.md)), checked here.

## 1. The growth without the five-place knot

Ring knots R_0, …, R_4, R_i sharing one distinction with R_{i+1} (indices mod 5), each of four places, so two open. In round 1, R_i
and R_{i+2} share the neighbour R_{i+1}, and no three ring knots are pairwise candidates, so the groups are the five pairs two apart
along the ring; each knot is in two of them and gives both open distinctions. The five new junctions again form a five-cycle of
candidates (two that share a parent are two apart), each in two pairs with two fresh distinctions. So every round has five junctions
of two parents and demand 2: a cylinder of circumference five, one-dimensional.

Coordinates: write a cylinder junction as v = (a, b) with height h(v) = a + b (its round), parents (a − 1, b) and (a, b − 1), and
(a, b) identified with (a + 5, b − 5). Round-0 positions (a, −a) are the five knots, the ring order being a ↦ a + 3 (two cylinder
steps are one ring step back).

## 2. The model with the five-place knot (the advisor's)

Let R_0 have five places (three open). Its lifts in the unrolled cylinder are p_k = (5k, −5k), k ∈ ℤ.
- **Junctions:** pairs (v, S) with S a finite set of lifts below v (p_k ≤ v in both coordinates), taken up to the shift; its round
  is h(v) + |S|.
- **Lifts below v:** m(v) = ⌊a/5⌋ + ⌊b/5⌋ + 1 when positive, else 0.
- **Parents of (v, S):** (v, S ∖ {k}) for each k ∈ S, and (v − e_a, S), (v − e_b, S) whenever S is still below the lower position.
- **Demand:** 2 + m(v) − |S|.

The round-1 offshoot of R_0's extra distinction is (p_0, {0}). In words: the offshoot is one more independent direction, available
on the cone above the five-place knot. Going round the ring once, that cone comes back over its own origin; the returning copy and
the first are not identified, so each lap adds one more independent direction there, and wherever k laps overlap the closure fills
in every combination.

## 3. What is proved

**Proposition 1 (the model's count).** In the model, c(t) = Σ over cylinder positions v with h(v) ≤ t of C(m(v), t − h(v)), and
c(t) = c(t − 5) + c(t − 6) for t ≥ 6, so c grows like ρ^t with ρ ≈ 1.1347 the real root of x⁶ = x + 1.

*Proof.* The first formula counts the sets S of size t − h(v) among the m(v) lifts below v. Shifting a position by five steps in b
raises m by exactly one, so Pascal's rule C(m + 1, s) = C(m, s) + C(m, s − 1) splits the positions of height h into those of height
h − 5 (the term without the new lift) and those of height h − 5 counted one round later with the new lift (the term with it): a lap
costs five rounds without the new direction and six with it. Summing over positions gives the recurrence once every position of
height at most 5 has its first lift (t ≥ 6). ∎

**Proposition 2 (the growth is the model).** For every t, the junctions of rounds 0 to t of the fewest growth of the ring, with
their parents, rounds and fresh counts, are the model's (v, S) of round at most t.

*Proof (the advisor's four steps; step 3 is the substantial one).*
1. *No surplus after round 1.* In the model every demand 2 + m(v) − |S| is at least 2 (|S| ≤ m(v)), so no junction is implied
   and none closes; every junction but the offshoot has at least two parents, so p + d ≥ 4 and the fewest rule gives exactly the
   demand, k = d. The offshoot (p_0, {0}) has one parent and demand 2 and gets max(2, 3 − 1, 1) = 2, again its demand.
2. *Candidates.* Two round-t junctions are candidates exactly when they are u + x and u + y for one round-(t − 1) junction u and two
   different directions x, y among e_a, e_b and the lifts e_k available at u.
3. *Groups* (the referee's exact argument, R1 §2, replacing this study's sketch). The model's junctions form the set
   M = {(v, S): h(v) ≥ 0, S ⊆ L(v)}, with L(v) the lifts below v, inside the lattice ℤ² × (finite sets of lifts), ordered by both
   coordinates and by inclusion. That lattice is distributive and its rank h(v) + |S| is modular.
   - *M is closed under joins:* S ⊆ L(v) and S' ⊆ L(v') give S ∪ S' ⊆ L(v ∨ v'), since L is monotone.
   - *Candidates meet in M:* if x ≠ y of rank t share a lower cover u in M, then u = x ∧ y, since u ≤ x ∧ y < x.
   - *Sunflower or co-star:* let x₁, x₂, x₃ of rank t meet pairwise at rank t − 1. If x₁ ∧ x₂ ≠ x₁ ∧ x₃, then
     (x₁ ∧ x₂) ∨ (x₁ ∧ x₃) = x₁, so x₁ ≤ x₂ ∨ x₃; every pairwise join has rank t + 1 by modularity, so the three joins are one
     element w of M, and the three have no common neighbour (it would be a common lower cover of rank t − 1 below x₁ ∧ x₂ ∧ x₃,
     which has rank t − 2). Otherwise the three meets are one lower cover: a sunflower, which is invalid.
   - *Lower covers meet:* two lower covers of a w = (v, S) in M share a lower cover in M, except when w is a round-1 position
     junction. The meets are (v − e_a − e_b, S) when h(v) ≥ 2, using L(v − e_a − e_b) = L(v − e_a) ∩ L(v − e_b); (v − e_a, S ∖ k);
     and (v, S ∖ {k, k'}).

   So the maximal valid sets are exactly the lower-cover sets of the elements with three or more lower covers, and the remaining
   candidate pairs are the lower-cover pairs of the elements with exactly two. At round 1 the ring knots are candidates through the
   ring adjacency, not a lower cover; §1 handles that (n odd and at least 5: pairs two apart, no triple). The argument uses only that
   L is monotone and L(v ∧ v') = L(v) ∩ L(v'), so it holds for any set of spares.
4. *Descent to the ring.* A valid set, or a candidate pair, spans a loop of at most six junction steps, while a loop around the ring
   in the cylinder takes at least ten, so every group lifts to the unrolled cylinder and is counted once.

All four steps are exact. Step 3 is the referee's; this study's first version sketched it through the predecessor's lemma "in a
product of the quadrant order with a cube over each position", but M is a join-closed subset, not a product (the cube's dimension
m(v) changes with v, and positions stop at height 0).

**Checked.** The grown pattern (parents, rounds, fresh counts, the five-place knot marked) is isomorphic to the model as a directed
graph at rounds 8, 12, 16 and 20 (526 junctions); the per-round counts agree with Proposition 1 at every round computed (to 40 here,
to 57 by the TOUCH-CENSUS referee's independent code); the parent-and-demand histograms agree at every round to 22, including the advisor's two
forecasts (the first six-parent junction at round 21, the first demand 7 at round 20). The referee (R1): equal counts and equal
joint histograms of (parents, fresh) in every round 1 to 53 (41,501 junctions).

## 4. Other rings (the advisor's predictions, checked by ticket B)

With j extra open distinctions on a clean ring of odd period n ≥ 5 (any positions; a six-place knot counts two), every lap raises the number
of independent directions by j, and after a transient c(t) = Σ_i C(j, i) c(t − n − i): growth rate the root of x^(n + j) = (1 + x)^j
(about 1.135 for n = 5, j = 1; 1.263 for j = 2; 1.385 for j = 3). A ring of eight splits into two interleaved cylinders, one of which
stays inert; the other follows the formula with n/2 = 4 (rate 1.1673), not with n = 8. The formula is proved for every odd
n ≥ 5 in `RING-FORMULA-20261118-001A`. Rings of four and six are degenerate (two common neighbours, or a group wrapping the ring).

## 5. What the ring does that a chain cannot

On a chain the offshoot's extra direction lives on one cone above the five-place knot; it never meets itself, so the growth stays
at most two-dimensional. On a ring the cone winds around and comes back over its own start once every lap; the closure does not
identify the returning copy with the first, it adds it as a new independent direction, so the number of directions grows by one per
lap, and the junctions per round grow exponentially. In the owner's words this is folded, overlapping structure, literally: one
cone wound over the ring, overlapping itself once per lap. It is not a fractal in the sense of self-similarity at every scale; its
counts are diagonal sums of Pascal's triangle wound around the ring (the advisor's caution).
