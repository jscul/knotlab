# One formula for the growth of rings of knots

## Standard statement

For an odd cycle of n ≥ 5 even-parity constraints of arity 4 + s_i (one variable shared between consecutive constraints), with
j = Σ s_i extra variables, the least closure under the complete-round joining policy has, in the model of
`RING-GROWTH-20261118-001A` extended to j extra variables, c(t) = Σ_v C(m(v), t − h(v)) constraints in round t, which satisfies
c(t) = Σ_{i=0}^{j} C(j, i) c(t − n − i) for t ≥ n + j and grows like ρ^t with ρ the unique root above 1 of x^(n+j) = (1 + x)^j.
When every constraint has one extra variable, c(t) = n F(t + 2) for every t, F the Fibonacci numbers.

## Nearest known result

`RING-GROWTH-20261118-001A` (the case n = 5, j = 1, and the four-step identification of the growth with the model); Vandermonde's
identity; the diagonal sums of Pascal's triangle are the Fibonacci numbers. [Design](../../../research/RING-FORMULA-20261118-001/ring_formula.md).

## 1. The model for j spare distinctions

Ring knots R_0, …, R_{n−1} (n odd), R_i sharing one distinction with R_{i+1}; R_i has 4 + s_i places, two open plus s_i spare.
Without spares the growth is a cylinder of circumference n (cylinder is the literature's word; here it names only the pairs
(a, b) of integers taken modulo (n, −n)) (`RING-GROWTH-20261118-001A` §1, which used only that n is odd and at
least 5: two ring knots are candidates exactly when they are two apart, the "two apart" relation on ℤ_n is one cycle of length n
because 2 is invertible mod n, and for n ≥ 5 it has no three mutually candidate knots). In cylinder coordinates v = (a, b), height
h(v) = a + b, modulo (n, −n), ring knot R_i sits at a = i(n + 1)/2 mod n.

Each spare distinction of R_i at cylinder position a_0 has lifts p_k = (a_0 + nk, −a_0 − nk), k ∈ ℤ. A junction is (v, S), S a
finite set of lifts (of any spares) below v; its round is h(v) + |S|; parents and demands as in `RING-GROWTH-20261118-001A` §2, each
lift being one more direction on its cone. The identification of the grown pattern with this model is that study's Proposition 2,
whose four steps do not use j = 1: no surplus beyond the spares' offshoots (every demand is 2 + m(v) − |S| ≥ 2), candidates one
direction apart over a common lower element, groups the lower covers of one element (the referee's exact argument, now
`RING-GROWTH-20261118-001A` Proposition 2 step 3, which uses only that L is monotone and L(v ∧ v') = L(v) ∩ L(v'), true for any
spares), and no group wraps the ring (a group spans a few steps, a loop round the cylinder at least 2n ≥ 10). So the grown pattern
is the model, proved. A knot with q spares makes q one-parent offshoots in round 1, each of demand q + 1 and given exactly q + 1 by
the fewest rule; their combinations fill in later (the referee). The identification is checked by counts on 17 rings to round 13
(Verification) and by the referee's per-round histograms of (parents, fresh) on nine rings.

## 2. The count and the recurrence

**Proposition 1.** With m(v) the number of lifts below v, c(t) = Σ_{v: h(v) ≤ t} C(m(v), t − h(v)).

**Proposition 2.** For every t ≥ T_0 = n + j, c(t) = Σ_{i=0}^{j} C(j, i) c(t − n − i). Its
characteristic equation is x^(n+j) = (1 + x)^j, which has exactly one root ρ > 0, and ρ > 1 when j ≥ 1; c grows like ρ^t.

*Proof.* The shift (0, n) is a bijection from the positions of height h onto those of height h + n. For a spare at a_0, the number
of its lifts below (a, b) is ⌊(a − a_0)/n⌋ − ⌈(−b − a_0)/n⌉ + 1, which is nonnegative whenever h(v) ≥ 0; raising b by n raises it
by exactly one. So m(v + (0, n)) = m(v) + j at every position of height at least 0, and by Vandermonde's identity
C(m + j, s) = Σ_i C(j, i) C(m, s − i). Every position of height at least n is such a shift, so summing over them gives
Σ_i C(j, i) c(t − n − i). Below height n each spare has at most one lift below v (the admissible k lie in an interval of length
h(v)/n < 1), so m(v) ≤ j there, and those positions contribute C(m(v), t − h(v)) only for t ≤ h(v) + m(v) ≤ n − 1 + j. Hence the
recurrence holds from T_0 = n + j (the referee's sharpening of this study's "at most about 3n + j", and the first round at which it
can be stated).
For the root: f(x) = (n + j) log x − j log(1 + x) has derivative (n + j)/x − j/(1 + x) > 0 for x > 0, so f has one zero; f(1) =
−j log 2 < 0 for j ≥ 1. ∎

Values: ρ = 1.1347 (n = 5, j = 1), 1.2628 (j = 2), 1.3854 (j = 3), 1.5036 (j = 4), and for n = 7, j = 1, 1.0970.

## 3. Every knot with one spare: the Fibonacci numbers in every round

**Proposition 3.** If every ring knot has exactly one spare distinction (j = n), then m(v) = h(v) + 1 for every position, and
c(t) = n F(t + 2) for every t ≥ 0 (F(1) = F(2) = 1). For the ring of five five-place knots: 5, 10, 15, 25, 40, 65, 105, …

*Proof.* The ring knots occupy every cylinder position, so the lifts are all (a', −a'), a' ∈ ℤ, one per integer. Those below
(a, b) are the a' with −b ≤ a' ≤ a: a + b + 1 of them. There are n positions of each height h, so
c(t) = n Σ_{h=0}^{t} C(h + 1, t − h) = n Σ_k C(t + 1 − k, k) = n F(t + 2), the diagonal sums of Pascal's triangle. ∎

The rate is the golden ratio for every n, as x^(2n) = (1 + x)^n reduces to x² = x + 1.

**Proposition 4 (q spares at every knot; the referee's addition).** If every ring knot has q spare distinctions (j = qn), then
m(v) = q(h(v) + 1), c(t) = n Σ_h C(q(h + 1), t − h), with generating function n(1 + x)^q / (1 − x(1 + x)^q), and the rate is the
root of x^(q+1) = (1 + x)^q.

*Proof.* As Proposition 3, with q lifts at every integer; summing x^h (1 + x)^(q(h+1)) over h gives the generating function, whose
dominant singularity is the root x_0 of x(1 + x)^q = 1, and ρ = 1/x_0 satisfies ρ^(q+1) = (1 + ρ)^q. ∎

This agrees with Proposition 2, since x^(q+1) − (1 + x)^q divides x^(n(q+1)) − (1 + x)^(nq). For q = 2 (five six-place knots) the
referee's grown counts are 15, 30, 65, 140, 300, 645, 1,385, 2,975, 6,390, 13,725 in rounds 1 to 10, with
c(t) = c(t − 1) + 2c(t − 2) + c(t − 3) and rate 2.1479 (computed; R1 §7).

## 4. Why rings of three, four and six are different, and even rings in general

- **Three knots.** Every two ring knots are neighbours and also share the third as a common neighbour; the three are mutually
  candidates with no common neighbour, so round 1 joins all three in one group. With four places each, that group takes one open
  distinction from each and the other open ones become offshoots of demand 1 (the crossed start: `FIRST-KNOT-20261118-001A`
  Proposition 4 with m = 3, three-dimensional); not a cylinder.
- **Four knots.** R_0 and R_2 share two common neighbours (R_1 and R_3), and so do R_1 and R_3: the round-1 groups are the two pairs
  {R_0, R_2} and {R_1, R_3}, each knot in one group, not two; each knot's other open distinction becomes an offshoot. Not a
  cylinder: computed, one more junction each round.
- **Six knots.** The "two apart" relation splits ℤ_6 into two cycles of length three, {R_0, R_2, R_4} and {R_1, R_3, R_5}, each three
  mutually candidate with no common neighbour: two groups of three, each knot in one, and a surplus offshoot each. Not a cylinder:
  computed, per-round counts quadratic.
- **Even n ≥ 8.** The relation splits into two cycles of length n/2 ≥ 4 with no three mutually candidate, so the growth is two
  interleaved cylinders of circumference n/2, each with its own spares: the formula holds per cylinder with n/2 in place of n (the
  ring of eight with one spare: g = c − 4 with g(t) = g(t − 4) + g(t − 5), `RING-GROWTH-20261118-001`, predicted and computed). Not
  proved here.

## Verification

Ticket B compares the model's counts with the grown rings for 17 rings of lengths 5, 7 and 9 with knots of four to six places, to
round 13, and checks the recurrence and the rate on the model to round 80. The referee (R1, Part 2) compared the full per-round
histograms of (parents, fresh) with the model on nine rings through 10 to 88 rounds, two of them past this study (a seven-place
knot; two spares at every knot), and found the recurrence exact from its first possible round on five odd rings this study did not
grow (n = 11, j = 1; n = 9, j = 3; n = 7, j = 4; n = 5, j = 4; n = 9, j = 9, which gives 9 F(t + 2) in every round) and on all 13
census rings.
