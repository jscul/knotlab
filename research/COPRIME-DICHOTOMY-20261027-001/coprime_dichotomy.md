# The general coprime dichotomy: pairs collapse the action, triples decide

Epic `COPRIME-DICHOTOMY-20261027-001` (2026-10-27).

**The question.** The owner (via Codex) asked:
- to pursue the general coprime dichotomy, keeping the grading and class-at-most-4 assumptions;
- to test and prove or refute (P2) and (P3);
- to address the r > 2 base terms and recover the total count across sectors;
- to consolidate the corrected class-(K), beyond-class-2 and r = 2 arguments into a self-contained presentation for independent
  review.

## Outcome

**The criterion is proved in both directions, except for one precisely stated family.**

1. **Polynomial side, every r, every class, no grading** (`COPRIME-DICHOTOMY-20261027-001A-P001`, proved).
   - (P2_d) holds iff the C_d action collapses to an involution θ_d, which is then an automorphism of 𝔫.
   - Given (P2_d), (P3_d) says θ_d's Lie triple system is abelian.
   - Under the criterion, the count over a sector of order d is Π_{α≢0} |Z¹(π; F_p^{αψ})|^{dim 𝔤_α}, and every homomorphism lies
     in a class-2 subgroup. The criterion passes to divisors.
2. **Base terms and steering at characters of order d ≥ 3** (`COPRIME-DICHOTOMY-20261027-001B-E002`, supported under a frozen
   contract).
   - **No channels.** At slope d/p the counts on K # K are exactly the squares of the counts on K; at slope d/1 they are not
     (3 of 3 cases).
   - **Local forms.** Massey forms vanish on 66 amphichiral and 56 cable rows. Chiral knots obstruct.
   - **Steering.** The steering rule with κ_t = t⁻² − t⁻¹ holds exactly on 48 insertions and 10 gadgets, at d = 3, 4, 5, 6.
   - **Process.** The first run, E001, crashed on a construction error before any verdict and is kept as invalid.
3. **Hardness at every sector order** (`COPRIME-DICHOTOMY-20261027-001C-P001`, proved).
   - Under (P2_d), only near triples [[𝔤_a, 𝔤_{−a}], 𝔤_{±a}] can fail; far triples vanish by Jacobi.
   - If (P2_d) holds and (P3_d) fails, counting on S³_{d/p}(K) is #P-hard, for graded 𝔫 of class at most 4.
4. **The consolidated presentation** (`COPRIME-DICHOTOMY-20261027-001D-P001`, `presentation.md`).
   - **Proved.** Theorem A; hardness for class 2, for triples under pairs, and for the cross-layer pair.
   - **The dichotomy, Corollary C.** For graded algebras of class at most 4 and sector orders in a divisor-closed set:
     - polynomial iff the criterion holds at every occurring order, except for one family;
     - the exception is open: algebras of class 3 or 4 whose criterion fails, at every failing order, only through pair failures.
   - **Corrections.** The reversed Artin identity, the sector-count assumption, the per-group anchor lemma and the interpretation
     boundary.
   - **Organization.** Uniform proof obligations, classical ingredients, literature and finite validation are kept separate.

## Steps and what was new

- **Pairs collapse the action (A).**
  - (P2_d) is exactly the statement that θ_d is an automorphism, so the general case reduces to an involution.
  - Then (P3_d) is the r = 2 criterion for θ_d. Lemma 1 (iv) is the conceptual core.
- **Only near triples (C, Lemma 1).** Under (P2_d), Jacobi kills [[𝔤_α, 𝔤_{−α}], 𝔤_β] for β ≢ ±α. A failure is always a pair of
  inverse characters together with a third element of one of them.
- **Channels vanish at slope d/p.**
  - λ lies in the commutator subgroup, so ρ(λ)^p = 1. The surgery relator then only asks ρ(μ)^d = 1.
  - So the closed count is a positive sum, over sectors, of pinned knot-group counts. These are multiplicative over connected sums
    (meridian amalgams).
  - This removes the "channel term" obstacle recorded in the previous epics.
- **Local Massey forms, and two ways to remove them.**
  - For d ≥ 3 each summand carries classes at t₀ and t₀⁻¹ together, and their local Massey forms obstruct on twist knots.
  - **Odd orders.** Negative amphichiral summands kill them: the u-pairing is perfect at simple roots, which forces ε₊ε₋ = −1, and
    every obstruction monomial is (2,2)-balanced under (P2_d).
  - **Squares only.** Simple roots of strongly negative amphichiral knots are squares (Hartley–Kawauchi). On genus-one two-bridge
    knots b(4MN+1, 2N) the form vanishes exactly when M ≡ N, at square roots only.
  - **Even orders.** Every non-square has even order 2k, and there the (k,1)-cable of T(2, p) works in every class for every algebra.
    The companion's one-parameter homomorphism glues across the acyclic cable space.
- **Squier duality and the corrected Artin identity.**
  - J_t, lower unitriangular with (J_t)_{qq′} = (t − 1)t^{q−q′−1}, makes Burau unitary between t and t⁻¹. At t = −1 it is the
    earlier J.
  - The coboundary vector comes from the reversed identity Π_{j desc} P_j R_j P_j⁻¹ = 1. Codex's correction is incorporated and
    replayed.
- **Steering at t.** Bundles of d strands (products in N), leaves Σ_i t^{d−1−i} c_i, and the constant κ_t = t⁻² − t⁻¹ (= 2 at
  t = −1).
- **Exact difference leaves.** In the gadget, d − 2 unknot blocks copying u's colour sit next to u's reading strand. Because the
  bundle coefficients sum to zero, the vertex leaf reads exactly X_v − X_u at every character.

## Challenged assumptions

- **"Channel terms are an intrinsic obstacle at r > 2."** No. They depend on the slope, and slope d/p removes them.
- **"Local terms are unavoidable and need vertex weights."** Scoping showed that vertex weights fail in general (Gauss sums can be
  negative or complex). Summand choice removes local terms instead.
- **"Amphichiral summands suffice for every root."** No: only for squares. Cables cover the even orders, which include every
  non-square.
- **"Far triples are a separate case."** No. Under (P2_d) they vanish identically.
- **"The r = 2 machinery is special to t = −1."** No. J_t and κ_t generalize it; only the base needed new ideas.
- **Bugs caught by checks.**
  - Two-bridge presentations with even β gave wrong groups; Schubert's normal form needs odd β.
  - A trivial-character assertion fired on samples already obstructed lower down.
  - Gadget leaves were first read at the wrong positions.
  - E001's insertion did not fit its base.
  All were caught before any claim depended on them.

## Literature

- **Samperton–Weiss (arXiv:2602.02885).** Class 2, bounded H².
- **Galindo (arXiv:2605.06984).** Unbounded homology.
- **Kuperberg–Samperton; Rowell.** Solvable targets open.
- **Moussard (2017).** The closest precursor for the class-(K) steering.
- **Squier.** Burau unitarity; verified directly here.
- **Schubert.** Two-bridge classification.
- **Hartley–Kawauchi.** Amphichiral Alexander polynomials.
- **Bulatov–Grohe via Cai–Chen–Lu.** Theorem 2.1 and Corollary 2.1.
- **The search.** No new external search was run this epic. The comparisons are those of the predecessor epics, and novelty
  remains a candidate claim.

## Gaps

1. **Pair failures in classes 3 and 4** (the residual family).
   - Without (P2_d) there is no parity. Steering side effects and in-bundle brackets can reach root characters, so the edge weight
     need not depend only on σ_v − σ_u.
   - Known: the cross-layer pair (`BEYOND-CLASS2-20261027-001A`).
   - Plausible partial result: when the higher layers have no components at the class-(K) gadget's characters, the count reduces to
     the class-2 quotient. This is not written.
2. **Class at least 5.** Amphichiral summands do not kill (3,3)-balanced terms. Cables survive in every class.
3. Non-graded algebras; p = 2 and p = 3; p-torsion in H₁; unbounded sectors.
4. Knot exteriors beyond class (K). The pinned framework suggests the way, but nothing is written.
5. No external review of A at every r, or of C for d ≥ 3.

## End-of-epic assessment

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: the general coprime dichotomy (graded, class ≤ 4) | **Status:** Partially successful | **Proved:** the polynomial side for every r and class, and hardness at every sector order whenever pairs hold and a triple fails. Class 2 and the cross-layer pair are inherited. **Open:** pair failures in classes 3 and 4. The consolidated, corrected presentation is complete. |
| Local direction: coprime p-group-by-cyclic counting with bounded H₁ | Continue | The machinery now works at every character order: pinning, two summand constructions, Squier duality and κ_t. One residual family remains, with a clear technical obstacle (no parity). |
| Broader exploration: complexity of 3-manifold invariants | Known alternatives | Samperton–Weiss (bounded H²) and Galindo (unbounded homology) cover other regimes. The coprime, bounded-H₁ regime is this program's. |
| Long-term goal: the complexity side of "two versus three" | Capability gained | At every sector order, pairs that bracket into the fixed part are rigid, and a surviving triple decides hardness. The parity of θ_d makes "two is easy, three decides" exact once pairs are clean. Not an emergence result; r counts action characters. |
| Next recommendation: pair failures in classes 3 and 4 | **Next step:** Continue, with a fresh epic | First discriminator: write the inert reduction, where higher layers avoid the gadget characters, and test non-inert examples. One example is free class 3 on (a, a) at d = 4 or 5, where [[y₁, y₂], y₁] reaches a root character. Measure whether its edge weight stays non-rank-one. Alternative: class at least 5, where cable summands already work. |
| Interest: that recommendation | **2/3 (Promising)** | It would complete the coprime dichotomy for graded class ≤ 4. Main uncertainty: without parity the edge weight is a general exponential sum and need not be real or depend only on differences. A new argument (or a counterexample) is needed. |
| Execution: that next action | Deferred to the owner | No successor created. Stop condition: a proof covering pair failures, or an algebra with a pair failure whose counting is provably polynomial. |
