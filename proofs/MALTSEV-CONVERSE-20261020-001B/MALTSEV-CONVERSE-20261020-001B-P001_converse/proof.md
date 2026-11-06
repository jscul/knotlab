# What composing knots like cycles forces

Status: Proved

Ticket `MALTSEV-CONVERSE-20261020-001B`, 2026-10-20. It uses
`KNOT-CIRCUITS-20261020-001B-P001` ("the circuits proof" below) and the census
`MALTSEV-CONVERSE-20261020-001A-E001` ("A" below).

## Standard statement

The definitions are those of the circuits proof:
- **Circuits** are minimal constrained sets, relative to each variable's
  range.
- **Knots** are circuits of at least three variables.
- A law **composes knots like cycles** when, in every system, two knots
  sharing a variable e leave their union without e constrained.
- A knot is **rectangular at e** when its fibres over e (the sets of e-values
  allowed by each assignment of its other variables) are pairwise equal or
  disjoint.

The circuits proof showed that a law with a Mal'tsev polymorphism composes
like cycles exactly when no subalgebra splits. It left the converse open. This
proof shows:

1. **The naive converse is false.** A parity law on {0, 1} placed beside an
   unrelated law has knots that compose like cycles but no Mal'tsev
   polymorphism.
   - Beside x ≤ y on {2, 3}, ties still fail.
   - Beside an isolated-value relation on {2, 3, 4}, nothing fails at all.
2. **Direct hubs** (Lemma 2). A knot forms a hub with a copy of itself if:
   - at some variable all its fibres pairwise meet; or
   - it has a selector: a variable s such that, for each value of s, the
     fibres over another variable e pairwise meet.
3. **Two values** (Theorem 3). In a law that composes knots like cycles,
   every knot whose variables share one two-element range is a parity knot.
4. **Rectangular knots suffice** (Theorem 4). Suppose every knot of a law is
   rectangular. Then the law composes knots like cycles exactly when no two
   knots meeting at a variable split its range: their fibre partitions never
   compose to the total relation. No difference operation is needed.
5. **The open step** is the local converse. Must every knot be rectangular
   once knots compose like cycles?
   - Every knot found in A, and every 3-variable knot tested on 2, 3 and 4
     values, gives a hub either directly or through one derivation, the
     diagonal (Observation 6).
   - The general statement is a conjecture.

## Nearest known results

- **The circuits proof.** Theorem 1 (difference laws), Theorem 2 (Boolean
  laws) and the fibre criterion.
- **Mal'tsev conditions.** Rectangularity characterizes Mal'tsev
  polymorphisms through the free relation (the classical argument; see
  Bulatov and Dalmau, SIAM J. Comput. 2006). The local converse asks for
  rectangularity of knots only, not of all relations.

**Classification: new to the program; elementary from the circuits proof.**
The counterexamples, the direct-hub lemma and Theorem 4 are short. Theorem 3
is a corollary of the circuits proof's Theorem 2. Observation 6 is
computational evidence.

## Proposition 1 (the naive converse fails)

Let Γ_A = {parity on {0,1}^3, x ≤ y on {2,3}^2} over D = {0, 1, 2, 3}. Let
Γ_B = {parity, J} over D = {0, 1, 2, 3, 4}, where
J = {(2,2), (3,3), (3,4), (4,3)} gives the value 2 to itself only.

1. **Systems split.** Every tuple of parity lies in {0,1}, and every tuple of
   the other relation lies in its own part. So a variable used by both kinds
   of copy has an empty range. A nonempty system is therefore a product: a
   parity system, a system of the other relation, and free variables.
2. **Circuits lie in factors.** In a product, a set is constrained exactly
   when its part in some factor is. So circuits lie inside factors, and
   elimination holds exactly when it holds in each factor.
3. **The factors.**
   - Parity systems are affine, so they compose like cycles (the circuits
     proof).
   - Systems of x ≤ y are bijunctive, so they have no knots. Their ties fail,
     for example (x ≤ e) ∧ (z ≤ e).
   - Systems of J tie every linked pair (the circuits proof, Readings), so
     every circuit is a tie and elimination holds.
4. **No Mal'tsev polymorphism.** A Mal'tsev operation on D that preserves the
   second relation restricts to one on that relation's range, after the
   unused entries are reassigned. No Mal'tsev operation on {2,3} preserves
   x ≤ y, and none on {2,3,4} preserves J; exhaustive search confirms both.
5. **Conclusion.**
   - Γ_A composes knots like cycles, but not ties.
   - Γ_B composes all circuits like cycles.
   - Neither has a Mal'tsev polymorphism, and both have knots. ∎

## Lemma 2 (direct hubs)

Let K be a knot with full ranges.
- **Meeting fibres.** If its fibres over e pairwise meet, then K(a, e) ∧ K(b, e)
  fails elimination at e. This is the fibre criterion of the circuits proof.
- **Selector.** Suppose s is a selector for e. Then K(a, s, e) ∧ K(b, s, e) has
  circuits vars(K) and its copy, because a knot's projection onto two of its
  variables is full. Fix any (a, b, s). The fibres E(a, s) and E(b, s) meet,
  so some e satisfies both. Hence (C₁ ∪ C₂) − e is unconstrained. ∎

So in a law that composes knots like cycles, every knot has, at every variable,
two disjoint fibres, and has no selector.

**Example.** The three-variable NAE on {0, 1} has no variable with pairwise
meeting fibres, but its second variable is a selector for its first. So two
copies sharing two variables form a hub.

## Theorem 3 (two values)

Suppose a law composes knots like cycles, and K is a knot all of whose
variables have the same two-element range B. Then K is a single parity knot.

*Proof.*
1. Identify B with {0, 1}. Systems built from copies of K stay inside B and
   are systems of the law, so the Boolean law ⟨K⟩ composes knots like cycles.
2. By Theorem 2 of the circuits proof, ⟨K⟩ is affine or bijunctive.
3. K is a knot, so ⟨K⟩ is not bijunctive. Hence it is affine.
4. An affine relation all of whose proper projections are full is a single
   equation over all its variables, x₁ ⊕ … ⊕ x_n = c. ∎

So if the distinctions are bits and knots compose like cycles, every knot is a
parity.

## Theorem 4 (rectangular knots suffice)

Suppose every knot of every system over Γ is rectangular at each of its
variables. Then Γ composes knots like cycles exactly when there are no two
knots K₁ on (a, e) and K₂ on (b, e), with equal ranges at e, whose fibre
partitions γ₁ and γ₂ of D_e satisfy γ₁ ∘ γ₂ = D_e².

*Proof.*
- **If such knots exist, a failure follows.** Join K₁ and K₂ on fresh
  variables at e alone. Their vars remain circuits. For any (a, b), the class
  E₁(a) meets the class E₂(b), because γ₁ ∘ γ₂ is total. So the union without
  e is unconstrained.
- **If a failure exists, such knots exist.** Suppose knots C₁ and C₂ fail at
  e in a system. Repeat the "if" part of the circuits proof's Theorem 1,
  using the rectangularity of π_{C₁}(S) and π_{C₂}(S) in place of the
  Mal'tsev operation.
  - Each knot fixes e modulo a pp-definable equivalence γ_i, with every class
    reached for each value of the shared variables.
  - The failure forces γ₁ ∘ γ₂ = D_e². ∎

The circuits proof's Theorem 1 is the special case where the Mal'tsev
operation makes every relation rectangular. With Theorem 4, the only thing
standing between "knots compose like cycles" and a complete description is
whether such laws force their knots to be rectangular.

## The open step: the local converse

**Conjecture.** In a law that composes knots like cycles, every knot is
rectangular at each of its variables.

**Evidence.**
- **Census A.** Among 1,026 laws over three elements, the 34 laws found to
  have knots (30 binary relations and 4 semilattice-generated ones) all have
  hubs between knots. All 142 of their knots are non-rectangular and have a
  variable with pairwise meeting fibres. No sampled law without such a
  failure had a knot, so this half of the evidence is vacuous.
- **Theorem 3** proves the conjecture on two values.
- **Observation 6** (computational). Some knots have neither direct case. The
  Boolean knot {000, 010, 011, 101, 110} is one.
  - For every such random 3-variable knot tested (on 2, 3 and 4 values), the
    diagonal derivation K′(x₀, x₁, x₂) = ∃h: K(x₀, x₀, h) ∧ K(x₁, x₂, h),
    for some ordering of K's variables, is a knot with a direct case. It
    therefore gives a hub.
  - Together with Lemma 2, this covers every non-rectangular 3-variable knot
    tested.
  - I do not have a proof that the diagonal derivation always works.

## What this does not show

- The local converse is not proved beyond two values.
- Knots on four or more variables were not tested for the diagonal
  derivation.
- No claim is made about which laws without knots compose ties like cycles.
- No contact network, composed topology in the protected sense, path or
  distance is claimed.

## Checks

`check.py` runs in about 15 seconds and writes `result.json`. All checks pass,
and all controls are rejected.

- **Proposition 1** on random mixed systems, 462 for Γ_A and 448 for Γ_B:
  - every system splits;
  - Γ_A has knots in 58, no failure between knots, and 14 between ties;
  - Γ_B has knots in 46 and no failure at all;
  - exhaustive search finds no Mal'tsev operation on the second relation's
    range.
- **Lemma 2** on 959 knots over two and three values: all 583 knots with a
  meeting variable, and all 245 with only a selector, form hubs.
- **Theorem 3.** The only affine Boolean knots on 3 and 4 variables are the
  4 single parities. All 32 other Boolean knots on 3 variables have a hub
  between knots in their own law.
- **Theorem 4** on random cosets over Z2×Z2, Z3, Z4 and Z6:
  - every knot is rectangular;
  - every failure comes with a pair of knots whose partitions compose to the
    total relation;
  - every such pair fails when joined alone;
  - the knot-level two-congruence construction on Z2×Z2 fails.
- **Remark** (NAE's selector) and **Observation 6:** 20, 20 and 12 knots with
  neither direct case, on 2, 3 and 4 values, are all resolved by the diagonal
  derivation.
- **Census agreement:** 34 laws with knots, none without a failure between
  knots.
- **Controls:**
  - "no failure implies Mal'tsev" (Γ_B);
  - "every knot is rectangular" (OR₃);
  - "the direct cases cover every non-rectangular knot" (the Boolean knot
    above).
