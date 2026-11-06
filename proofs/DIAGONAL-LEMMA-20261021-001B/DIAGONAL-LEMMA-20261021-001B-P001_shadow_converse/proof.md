# Shadows refute the local converse

Status: Proved

Ticket `DIAGONAL-LEMMA-20261021-001B`, 2026-10-21. It uses:
- the definitions of `KNOT-CIRCUITS-20261020-001B-P001` ("the circuits
  proof");
- the results of `MALTSEV-CONVERSE-20261020-001B-P001` ("the converse proof");
- the census `DIAGONAL-LEMMA-20261021-001A-E001` ("A").

## Standard statement

**Definitions.** They are those of the circuits proof.
- A system is a conjunction of copies of a law's relations. Any variables may
  be identified, and witnesses are quantified away.
- A set of variables is constrained when its projection is smaller than the
  product of its variables' ranges. Circuits are the minimal constrained sets;
  ties have two variables, and knots three or more.
- A law composes (knots) like cycles when, in every system, two circuits
  (knots) sharing a variable e leave their union without e constrained.
- A knot is rectangular at e when its fibres over e are pairwise equal or
  disjoint.

**The question.** The converse proof reduced the converse of the difference-law
theorem to a local converse:
- **Local converse.** In a law whose knots compose like cycles, every knot is
  rectangular.
- **Diagonal lemma.** Every non-rectangular 3-variable knot with no direct case
  has a diagonal derivation ∃h K(x₀, x₀, h) ∧ K(x₁, x₂, h) that has one.

  A direct case is a variable whose fibres pairwise meet, or a selector.

**This proof shows the following.**
1. **Shadows** (Theorem 1). Let M be a law whose systems all have full ranges,
   and let h be a surjection with h(M) ⊆ K. Then in every system the product
   M × K has exactly M's constrained sets. Fibres can be decorated without
   changing which sets are constrained.
2. **Lifts** (Theorem 2). Let M contain every constant tuple, and suppose each
   identification of its positions that leaves two or more distinct variables
   is constrained. Double one value a and delete the single tuple (a, …, a).
   Then every system keeps M's constrained sets.
3. **Counterexamples** (Corollary 3). Each of the following has a law that
   composes all circuits like cycles, yet is a non-rectangular knot with no
   direct case:
   - a 3-variable knot on 4 values:

     K₄ = {(x, y, z) ∈ {0,1,2,3}³ : x̄ + ȳ + z̄ ≡ 0 (mod 3)} − {(2, 2, 2)},

     where x̄ reads 3 as 2;
   - a product knot on 6 values;
   - a 4-variable knot on 4 values.

   No derivation of these knots, diagonal or otherwise, has a direct case. So
   both the local converse and the diagonal lemma are false.
4. **Fibre distance** (Theorem 4). Suppose a knot's fibres at a variable are
   connected through shared values, and two of them are at distance 2 or more
   (or at distance 1 with some value at distance 2 from a fibre). Then
   composing with the fibre-sharing relation gives a knot whose fibres
   pairwise meet, so the law fails. In a law whose knots compose like cycles,
   each fibre graph is therefore disconnected or dense. The counterexamples
   hide their non-rectangularity inside a component.
5. **What survives.**
   - Every knot of such a law has no direct case and disconnected or dense
     fibre graphs.
   - On two values every knot is a parity (the converse proof).
   - Laws with rectangular knots are characterized by the converse proof's
     Theorem 4.

   Beyond that, cycle-like composition is a property of which sets are
   constrained, not of fibres.

## Nearest known results

- **The circuits proof.** A difference law composes like cycles exactly when no
  subalgebra splits. Linear codes over a field compose like cycles, because
  their circuits are those of a matroid.
- **The converse proof.**
  - The naive converse fails.
  - Direct cases form hubs.
  - On two values every knot is a parity.
  - Rectangular knots reduce the question to partitions.
- **Rectangularity.** A finite algebra has a Mal'tsev term exactly when all its
  compatible relations are rectangular, by the classical free-algebra argument
  (see Bulatov and Dalmau, SIAM J. Comput. 2006). The local converse asked for
  less: rectangularity of knots only, from composition only.

**Classification: new to the program; elementary.**
- The product and lift constructions are short, and so is the fibre-distance
  construction.
- I found no source that asks this question, because constrained sets relative
  to ranges are the program's own notion.
- No literature search was made beyond the sources of the circuits proof.

## Theorem 1 (shadows)

Let M ⊆ A^k and K ⊆ B^k, and let h: A → B be a surjection with h(M) ⊆ K,
applied position by position. Let M × K ⊆ (A × B)^k pair the positions:
((a₁, b₁), …, (a_k, b_k)) ∈ M × K exactly when (aᵢ) ∈ M and (bᵢ) ∈ K. Suppose
every system over M has full ranges, as happens when M contains every constant
tuple.

Then for every system φ, with φ(R) its allowed states over relation R:
1. φ(M × K) = φ(M) × φ(K), pairing variable by variable;
2. every variable ranges over all of A × B;
3. a set Y is constrained in φ(M × K) exactly when it is constrained in φ(M).

So the law of M × K has, system by system, exactly the circuits of the law of
M. If M's law composes (knots) like cycles, so does M × K's.

*Proof.*
1. **Products.** An assignment of pairs satisfies a copy of M × K exactly when
   its first components satisfy the copy of M and its second components the
   copy of K. Identifications and projections act on each component
   separately.
2. **Ranges.** Applying h to each variable maps solutions of φ(M) to solutions
   of φ(K), since h(M) ⊆ K. φ(M) has range A at every variable, so φ(K) has
   range h(A) = B.
3. **Constrained sets.** |π_Y(φ(M × K))| = |π_Y(φ(M))| · |π_Y(φ(K))|, against
   |A|^{|Y|} · |B|^{|Y|}. So Y is constrained exactly when π_Y(φ(M)) ≠ A^Y or
   π_Y(φ(K)) ≠ B^Y. If π_Y(φ(M)) = A^Y, then
   π_Y(φ(K)) ⊇ h(A^Y) = B^Y. So Y is constrained exactly when
   π_Y(φ(M)) ≠ A^Y. ∎

The B-component can carry any fibre pattern that h(M) ⊆ K allows. The circuits
never see it.

## Theorem 2 (lifts)

Let M ⊆ A^k satisfy two conditions:
- **Constants.** M contains every constant tuple.
- **No free identifications.** For every pattern of identifications of its
  positions that leaves at least two distinct variables, the resulting
  relation on those variables is not the full product.

Fix a ∈ A, add a new value a′, and let g map a′ to a and fix A. Let

  L = g⁻¹(M) − {(a, a, …, a)}.

Call a variable x of a system **pinned** when some constraint has x in every
position. Then for every system φ:
1. a pinned variable ranges over D − {a}, and any other over D = A ∪ {a′};
2. a set Y is constrained in φ(L) exactly when it is constrained in φ(M).

So L's law has, system by system, exactly the circuits of M's law.

*Proof.* Constant tuples of M solve every φ(M). Applying g to each variable maps
φ(L) into φ(M).
1. **Ranges.**
   - **Values other than a.** For b ∈ A − {a}, the constant assignment b solves
     φ(L). So does the constant a′, because no constraint then reads
     (a, …, a).
   - **The value a, unpinned.** Put a on x and a′ on every other variable. The
     only constraint reading (a, …, a) would be one with x in every position,
     so this works exactly when x is unpinned.
   - **The value a, pinned.** A pinned x never takes a.
2. **Constrained in M implies constrained in L.**
   1. Take α ∈ A^Y missing from π_Y(φ(M)).
   2. Lift each α(y) to a value of y's range that g maps to α(y). This is
      possible because every range contains D − {a}, which g maps onto A.
   3. The lift is missing from π_Y(φ(L)), because g maps φ(L) into φ(M).
3. **Unconstrained in M implies unconstrained in L.**
   1. Suppose π_Y(φ(M)) = A^Y. Take any p with p(y) in y's range for each
      y ∈ Y.
   2. Choose σ ∈ φ(M) with σ = g(p) on Y.
   3. Put s = p on Y. Outside Y, put s = σ, but replace each value a by a′.
      Then g(s) = σ.
   4. Suppose a constraint read (a, …, a) under s. Its variables would all lie
      in Y with p = a.
      - If they are at least two distinct variables, then by no free
        identifications they form a constrained set inside Y. That contradicts
        π_Y(φ(M)) = A^Y.
      - If there is only one, it is pinned, so p ≠ a there. Again a
        contradiction.
   5. So s ∈ φ(L) and s = p on Y. ∎

## Corollary 3 (counterexamples)

**K₄ (3 variables, 4 values).**
- **The hypotheses.** Take M = {x + y + z ≡ 0 (mod 3)} on Z₃ and a = 2, and
  check Theorem 2's conditions:
  - M contains the constants, since 3t ≡ 0.
  - Identifying two positions gives 2x + y ≡ 0, that is y ≡ x, which is
    constrained.
  - Linear systems over GF(3) have the circuits of a matroid, so M's law
    composes like cycles.

  So K₄ = L composes all circuits like cycles.
- **Non-rectangular.** The fibre of (2, 2) at the third variable is {3}, and
  the fibre of (2, 3) is {2, 3}.
- **A knot.** Every pair of values extends to a triple. K₄ keeps 21 of the
  64 triples: the 22 lifts of the 9 solutions of M, less (2, 2, 2). So it is
  constrained, and it is a knot.
- **In words.** Read 3 as 2; the readings sum to zero mod 3; and the triple
  (2, 2, 2) itself is excluded.

**K₆ (3 variables, 6 values).** Take M = {x + y + z ≡ 0} over Z₃, B = {0, 1},
and h(0) = h(1) = 0, h(2) = 1. Then h(M) is "not exactly two ones", and K₆ is
the product of M with "not exactly two ones":
- the Z₃ parts sum to zero;
- the bits are not exactly two ones.

**K₄ₓ₄ (4 variables, 4 values).** Take M = {x + y + z + w ≡ 0} over Z₂ and h
the identity. K₄ₓ₄ is the product of M with M ∪ {1000}.

**Consequences.**
- Each is a non-rectangular knot in a law that composes all circuits like
  cycles, so the local converse is false.
- None has a direct case, and no knot derived from them has one: either would
  give a failure. In particular, the diagonal derivation of K₄ or K₆ never has
  a direct case, so the diagonal lemma is false.

**How small.**
- On two values there is no counterexample: by the converse proof, every knot
  of such a law is a parity.
- K₄ shows four values suffice for 3-variable knots.
- Three values remain open. Every random 3-variable knot on three values in A
  was resolved, and the 3-value candidate from A was resolved too.

## Theorem 4 (fibre distance)

Let K be a knot on y ∪ {e} with e-fibres E(a). Join two values of e's range
when some fibre contains both, and call this graph G_e. Suppose:
- G_e is connected;
- D, the largest distance in G_e between two fibres, satisfies D ≥ 2, or D = 1
  and some value lies at distance 2 or more from some fibre.

Set k = ⌈D/2⌉ and

  K_k(y, e) = ∃h₀ … h_k: K(y, h₀) ∧ R(h₀, h₁) ∧ … ∧ R(h_{k−1}, h_k = e),

where R(h, h′) = ∃y′: K(y′, h) ∧ K(y′, h′) is the fibre-sharing relation. Then
K_k is a knot whose e-fibres pairwise meet. So two copies of K_k sharing only e
fail elimination at e. The construction identifies no variables across
positions.

*Proof.*
1. **The fibres.** R is reflexive, so the e-fibres of K_k are the
   k-neighbourhoods N_k(E(a)), which contain E(a).
2. **Proper projections are full.**
   - Fibres are nonempty, so the projection onto y is full.
   - For each i, the projection onto (y − yᵢ) ∪ {e} contains K's, which is
     full.
3. **K_k is constrained.**
   - If D ≥ 2, take fibres E(a) and E(b) at distance D. The values of E(b) lie
     at distance at least D > k from E(a).
   - If D = 1, then k = 1, and the hypothesis gives a value at distance at
     least 2 from some fibre.

   Either way some k-neighbourhood misses a value.
4. **The fibres pairwise meet.** Two fibres at distance at most D ≤ 2k have
   overlapping k-neighbourhoods: the midpoint of a shortest path lies in both.
5. **The failure.** Two copies sharing only e are still circuits, since e's
   range is full. Their union without e is unconstrained, because the fibres
   pairwise meet. ∎

**Corollary.** In a law whose knots compose like cycles, at every variable of
every knot, G_e is disconnected, or every two fibres are at distance at most 1
and every value lies within distance 1 of every fibre.

All three counterexamples hide inside components. In K₄ the fibres at the third
variable are {0}, {1}, {2, 3} and {3}. The components are {0}, {1} and {2, 3},
and the non-rectangular pair {3}, {2, 3} sits inside the last one.

## Remark 5 (the full-range hypothesis)

Take parity P and the Boolean neither-knot N = {000, 010, 011, 101, 110}. Then
P ⊆ N, so h is the identity.

- **Single-sorted, it fails.** The product P × N on 4 values has a failure
  between knots. Parity systems can force constants, for example
  K(x, x, z) forces z = 0, and then Theorem 1's step 3 breaks. The witness is
  the system (1,1,4), (1,0,5), (1,3,2), (2,5,0) on six variables.
- **Positional, it holds.** In positional systems no variable is used in two
  positions, so parity forces no constants.
  - Suppose a sum of constraints had x alone as its odd support. Counting
    occurrences in x's position shows the number of constraints is odd;
    counting in another position shows it is even.
  - So Theorem 1 applies. The positions given disjoint ranges then compose
    like cycles.

## Remark 6 (the identification hypothesis)

Lift 4-variable parity by doubling 1 and deleting (1, 1, 1, 1). The
identification (x, x, y, y) is free in M but forbids x = y = 1 in L. Ties then
fail elimination, for example in the system (1,0,0,1), (0,1,1,2), (2,0,2,2), so
Theorem 2 needs its hypothesis.

No failure between knots appeared in 1,500 sampled systems. Whether this
4-variable knot on 3 values composes knots like cycles is open.

## The census candidates

A's predictions L4, L5 and L6 failed on candidates. These are now resolved.

- **L6, lifted knots.** Every knot on 4 values lifted from x + y + z ≡ 0 is
  g⁻¹(M) with the (2,2,2)-block replaced by a Boolean relation R with full pair
  projections.
  - When R is "all but 000", the knot is K₄, covered by Theorem 2.
  - For the other blocks tried (odd parity, the neither-knot, NAE, even
    parity), failures between knots exist. They need 6 variables and full
    identifications such as K(x, x, x), which A's random search (at most 5
    variables) missed. The checks verify one witness for each.
- **L5, the inner factor.** The inner factor x + y + z ≡ 0 plus {001, 010} has
  a failure through Theorem 4.
- **L4, the dihedral action.** When its two point positions share variables,
  the action of the square's symmetry group on its corners has a failure
  between knots. A searched positional systems only.

## What this does not show

- **Three values.** Whether a counterexample exists on three values is open.
- **The matroid-level converse.** Is every law whose knots compose like cycles
  equal, system by system, to a difference law in its constrained sets? This
  is not decided. Shadows, lifts and the converse proof's disjoint unions all
  are.
- **Remark 6's knot.** Whether the lifted 4-variable parity composes knots
  like cycles is open.
- **No protected structure.** No native recurrence, composed topology in the
  protected sense, path or distance is claimed.

## Checks

`check.py` runs in about 20 seconds and writes `result.json`. All checks pass,
and all controls are rejected.

- **Theorem 1.**
  - On K₆ and K₄ₓ₄ (400 random systems each), the product's constrained sets
    equal M's and no two circuits fail.
  - The same holds for 9 random shadows over Z₃, GF(4) and 4-variable Z₂ (900
    systems).
- **Theorem 2.** For K₄, and for the lift of z = ωx + ω²y over GF(4) on 5
  values (500 systems each):
  - the constrained sets equal M's;
  - ranges lose the doubled value exactly at pinned variables;
  - no two circuits fail.
- **Corollary 3.** K₆, K₄ and K₄ₓ₄ are non-rectangular knots with no direct
  case and no fibre-distance case. No diagonal derivation of K₆ or K₄ has a
  direct case.
- **Theorem 4.** On 30 random sparse knots on 5 and 6 values:
  - the composed relation is a knot whose fibres pairwise meet;
  - two copies fail.

  The construction does not apply to the Boolean neither-knot.
- **Remark 5.**
  - The single-sorted failure verifies.
  - In 300 positional systems, parity has no constant variable, the product has
    parity's constrained sets, and nothing fails.
- **Remark 6.** The tie failure verifies, and no failure between knots appeared
  in 1,500 systems.
- **The census candidates.** Failures verify for the four other lifted blocks,
  for the inner factor through Theorem 4, and for the dihedral action with
  shared point variables. The "all but 000" block equals K₄.
- **Census agreement.** A's L1–L3 hold. Every shadow had M's constrained sets
  and no failure in all sampled systems.
- **Controls:**
  - "composing knots like cycles forces rectangular knots" (K₄);
  - "the diagonal derivation resolves every knot with no direct case" (K₄);
  - "the full-range hypothesis can be dropped" (single-sorted P × N);
  - "the identification hypothesis can be dropped" (lifted 4-variable
    parity);
  - "a shadow composes like cycles because its inner factor does" ("not
    exactly two ones" fails on its own).
