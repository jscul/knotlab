# What the caps allow

Status: Proved

Ticket `KNOT-CAP-20261117-001A`, 17 November 2026, by Claude. Epic `KNOT-CAP-20261117-001`. The moves are A99's: one new
distinction p with an irredundant set of one to three betweenness knots, each on p and two old distinctions; every old state
extends, and p is constrained and not a copy. The rule takes the fewest states.
- **Degree cap c.** After a move, every distinction lies in at most c knots.
- **Pair cap m.** After a move, every pair of distinctions lies together in at most m knots.

Ticket B's frozen computation checks every statement on its cases.

## Statements

- **T1. From one knot, a cap of three knots per distinction stops at the 2 × 2 pattern.** The first step gives the 2 × 2 pattern
  with certainty. After it no move is allowed, so the growth ends there.
- **T2. From one knot, a cap of two knots per pair also stops at the 2 × 2 pattern.** The first step is the same. After it every
  pair of the four distinctions lies in exactly two knots, so no move is allowed.
- **T3. The fill bound.** Under a degree cap c, a base of K knots on n distinctions has 3K ≤ c·n. Growth from one knot that takes
  f three-knot steps has K ≥ n − 2 + 2f, so f ≤ (c·n − 3n + 6)/6. For c = 4, 5 and 6 at n = 16 that is at most 3, 6 and 9.
- **T4. Erasure cannot increase the difference.** Let two starts give distributions P and Q over classes of states at n₀. Continue
  both with the same rule that reads only the states. Their total variation distance at every later n is at most its value at n₀.

## Proofs

**T1.** The line of three has 6 states. By `STATE-RULES-20261117-001A`, S4, its only zero-cost extension with at most three knots
is the fill F(a, c, b) = {B(a, p, b), B(c, a, p), B(c, b, p)}, which gives the 2 × 2 pattern.
- **It is allowed.** a, b and c each take two new knots, reaching 1 + 2 = 3, and p takes 3.
- **It is cheapest.** Every other move costs at least N + 2 by S1.

Afterwards all four distinctions lie in three knots. Every new knot holds two old distinctions, and each of them would reach four.
So no move is allowed. ∎

**T2.** The first step is T1's fill. In the result the four knots are B(a, c, b), B(a, p, b), B(c, a, p) and B(c, b, p), and every
one of the six pairs lies in exactly two of them. A new knot holds the new distinction and an old pair, which would then lie in
three knots. So no move is allowed. ∎

**T3.**
- Each knot holds three distinctions, so the sum of the degrees is 3K, and it is at most c·n.
- From one knot at n = 3, each later step adds at least one knot, and a three-knot step adds two more. So K ≥ 1 + (n − 3) + 2f.
- Combining: 3(n − 2 + 2f) ≤ c·n. ∎

**T4.** A rule that reads only the states sends each class of states at n to a distribution over classes at n + 1, the same for
both starts: a Markov kernel M. Total variation does not increase under a Markov kernel: ‖PM − QM‖ ≤ ‖P − Q‖ (data processing).
Induct on n. ∎

## Provenance

- **Classical.** Data processing for total variation.
- **Local.**
  - The two stops are new as far as I know, and so is the reading in the program's terms.
  - T3's bound is elementary.
- **The advisor** gave T3's bound and the pair cap as a parameter-free law. It noted that the pair cap saturates exactly on the
  2 × 2 pattern; T2 makes that a stop.
