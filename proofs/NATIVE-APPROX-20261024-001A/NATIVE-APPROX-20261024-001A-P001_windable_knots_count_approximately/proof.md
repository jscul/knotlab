# Windable knots count approximately

Status: Proved

Ticket `NATIVE-APPROX-20261024-001A`, 2026-10-24.

**What it uses:**
- from `NATIVE-COUNTING-20261024-001` (closed): native counting with pins is a Holant problem with the knot and the two pins; exact
  counting is polynomial for the four topological knots and #P-hard for the other 30, given Backens's dichotomy;
- the knot axiom K2: no two excluded tuples of a knot are adjacent;
- an external theorem, cited as a hypothesis and not admitted as local evidence:
  - **(M)** McQuillan, *Approximating Holant problems by winding* (arXiv:1301.2880), Theorem 4. The strictly terraced windable
    functions are closed under connected circuits, and for every finite set of them the Holant problem has a fully polynomial
    randomized approximation scheme (FPRAS).

## Standard statement

**Setting.**
- **Native counting.** For a knot R, native counting with pins and free legs is the Holant problem for the knot R, the pins [1, 0]
  and [0, 1], and the free unary function [1, 1].
- **Strictly terraced** (McQuillan, Definition 3). A non-negative function F is strictly terraced if F(x) = 0 implies that all
  neighbours x + eᵢ take one common value.
- **Windable** (McQuillan, Definition 2). F is windable if there are B(x, y, M) ≥ 0 with Σ_M B(x, y, M) = F(x)F(y), invariant under
  flipping any block of M. Here M ranges over the partitions into pairs and singletons of the set where x and y differ.
- **The three-place criterion.** For three-place functions, McQuillan's Theorem 6 makes windability equivalent to an inequality for
  every x:
  F(x)F(x̄) ≤ F(x₁x₂x̄₃)F(x̄₁x̄₂x₃) + F(x₁x̄₂x₃)F(x̄₁x₂x̄₃) + F(x₁x̄₂x̄₃)F(x̄₁x₂x₃).
  The three products on the right are the *split pairs* of x.

**Lemma 1 (K2 is terraced).** Every knot, and every relation whose excluded tuples are pairwise non-adjacent, is strictly terraced.
So are the pins and the free unary function.

**Theorem 2 (the census).** A knot is windable exactly when it excludes at most two tuples or is a parity knot. So 26 of the 34 knots
are windable:
- the two parity knots;
- the four knots excluding an antipodal pair (not-all-equal and its relabellings);
- the eight single clauses;
- the twelve knots excluding a pair at distance two.

The eight knots excluding three tuples, a parity class minus one tuple, are not windable. Two of them are symmetric: the topological
no-lone-value knots.

**Corollary 3 (approximate counting, given M).** For each of the 26 windable knots, counting its native networks with pins and free
legs has an FPRAS.

**Corollary 4 (where efficient counting stands).**
- **Covered.** Every knot except six has an efficient counting algorithm for its native networks:
  - exact for the four topological knots;
  - randomized approximate for the other 24 windable knots.
- **Open.** The six exceptions are the non-symmetric knots excluding three tuples.

**Reading.**
- **K2 a third time.** The knot axiom K2, flip repair, is now the hypothesis of a third complexity result. It gave the
  resolution width bound (`NATIVE-HARDNESS-20261024-001B`) and the half rule (`NATIVE-HARDNESS-20261024-001C`). Here it gives
  approximate counting, through McQuillan's terraced condition, which bounds the weight of near-assignments.
- **Hard exactly, easy approximately.** For 24 knots, emergence is hard to count exactly and easy to approximate.

## Nearest known result

- **The algorithms are classical theorems applied.**
  - McQuillan (2013): FPRAS for windable strictly terraced Holant problems, including parity and not-all-equal constraints, which
    generalizes sink-free orientations.
  - Bubley and Dyer (1997): formulas with every variable at most twice, which covers the single-clause knots.
  - Lin, Liu and Lu (2014): edge covers, which covers the three-place clause.
- **The local contribution** is the census, the elementary proof of it from the split pairs, the observation that K2 implies the
  terraced condition, and the identification of the six knots left open. Novelty: `candidate-local-delta`; folklore risk medium.

## Proof

### Lemma 1

- **Knots.** If x is excluded, K2 says no neighbour of x is excluded, so every neighbour takes the value 1.
- **Unary functions.** A unary function with a zero has a single neighbour of that zero.
- **The free function** has no zero. ∎

### Theorem 2

For x with x and x̄ both allowed, the six tuples in the three split pairs of x are all the tuples other than x and x̄.
- **At most two excluded tuples.** Two excluded tuples spoil at most two of the three split pairs, so one pair is fully allowed and the
  inequality holds.
- **Parity knots.** x and x̄ have different parities, so they are never both allowed, and the left side is 0.
- **Three excluded tuples.** The excluded set is P \ {t} for a parity class P and a tuple t ∈ P.
  - The allowed set is the other class Q together with t, and t̄ ∈ Q is allowed.
  - Each split pair of t consists of a tuple at distance one from t, which lies in Q, and its complement, which lies at distance two
    from t. That complement is in P but is not t, so it is excluded.
  - So every split product is 0 while F(t)F(t̄) = 1, and the inequality fails at t.
- **Independently of McQuillan's Theorem 6.** The check decides Definition 2 directly, by exact linear feasibility over fractions on
  the 45 orbit variables of the conditions. This agrees with the inequality on all 34 knots. ∎

### Corollary 3

- **The functions involved.** The knot is strictly terraced (Lemma 1) and windable (Theorem 2).
- **The unary functions are windable.** For x ≠ y the only partition of one differing place is a singleton, and invariance asks
  F(0)F(1) = F(1)F(0). So the pins and the free function are windable and strictly terraced.
- **Apply (M)** to the finite set {R, [1, 0], [0, 1], [1, 1]}. Its Holant problem, on multigraphs with loops allowed, is native
  counting with pins and free legs. ∎

### Corollary 4

By Corollary 3, and by the exact formulas for the four topological knots (`NATIVE-COUNTING-20261024-001A`). The two parity knots are
windable and topological; the two no-lone-value knots are topological and not windable. ∎

## Checks

`check.py` uses the standard library only. It confirms:
- **Lemma 1** for the 34 knots, for all 35 co-independent relations on three bits, and for the unary functions;
- **Theorem 2**:
  - McQuillan's inequality and exact phase-one simplex feasibility of Definition 2 agree on every knot;
  - 26 knots are windable;
  - the 8 that are not are exactly those excluding three tuples, two of them symmetric.

**Controls.**
- **The tests reproduce published verdicts.** McQuillan's example relation {000, 100, 010, 101, 011} is windable under both tests, as
  his paper states, and not-all-equal is windable.
- **The tests can reject.** The soft equality with weights 2 on 000 and 111 and 1 elsewhere is rejected by both tests.
- **The terraced test can reject.** The perfect-matching relation (exactly one 1) is not strictly terraced.

## What this does not show

- **A local proof of (M).** The approximation schemes are cited.
- **The six knots left open.** They are examined in the next ticket of this epic.
- **Deterministic schemes.** Deterministic approximation (FPTAS) and the running-time exponents are not addressed.
