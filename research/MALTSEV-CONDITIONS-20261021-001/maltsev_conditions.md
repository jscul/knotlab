# Which Mal'tsev conditions do laws that compose like cycles satisfy?

Epic `MALTSEV-CONDITIONS-20261021-001`, closed 2026-10-21.

## The question

`MATROID-CONVERSE-20261021-001` proved a top lemma for difference laws. Its
proof uses modularity for one half and permutability only for Fleischer's
lemma. Laws such as the lift K₄ compose like cycles without any difference
operation. The epic asked:
- Do laws that compose like cycles satisfy the classical conditions:
  congruence n-permutability (Hagemann–Mitschke terms) or congruence
  modularity (Day or Gumm terms)?
- If they are modular, half of the top lemma carries over unchanged.

**The evidence.**
- [The census](../../experiments/MALTSEV-CONDITIONS-20261021-001A/MALTSEV-CONDITIONS-20261021-001A-E001_conditions_census/contract.json),
  with [result](../../artifacts/MALTSEV-CONDITIONS-20261021-001A/MALTSEV-CONDITIONS-20261021-001A-E001_conditions_census/result.json).
- [The proof](../../proofs/MALTSEV-CONDITIONS-20261021-001B/MALTSEV-CONDITIONS-20261021-001B-P001_tops_not_modularity/proof.md).
- The term characterizations are classical. The proof uses the forms stated
  in [On the number of terms witnessing congruence
  modularity](https://arxiv.org/abs/1709.06023) (Gumm terms, Theorem 4.1) and
  [n-permutability and linear Datalog implies symmetric
  Datalog](https://arxiv.org/abs/1508.05766) (Hagemann–Mitschke terms).

## What was found

- **K₄ is 3-permutable and congruence modular.**
  - Explicit Hagemann–Mitschke terms (n = 3) and Gumm terms (n = 1) exist.
    Each is a lifted linear form over Z₃ that copies a 2 only where an
    identity forces it.
  - K₄ still has no Mal'tsev polymorphism, because it is not rectangular.
- **K₆ composes like cycles but is neither modular nor n-permutable.**
  - K₆ = (x + y + z ≡ 0 over Z₃) × (not exactly two ones). It composes like
    cycles by the shadow theorem.
  - **A restriction lemma.** Linear identities among a shadow's polymorphisms
    pass, fibre by fibre, to the clone of its dominated factor.
  - That clone is tiny: the polymorphisms of "not exactly two ones" are only
    the conjunctions and the constants. Monotonicity kills every
    Hagemann–Mitschke chain, and the shape of the Day identities kills every
    Day chain.
- **So composing like cycles is not a classical Mal'tsev condition.**
  - It is incomparable with permutability, n-permutability and modularity.
    Z₆ has a Mal'tsev operation and fails elimination; K₆ composes like cycles
    with neither condition; K₄ composes like cycles with both.
  - The top lemma for all such laws therefore cannot go through modularity.
- **What the examples share: they are Mal'tsev on their tops.**
  - Some polymorphism F satisfies F(x,y,y) ≡ x and F(x,x,y) ≡ y modulo each
    range's unique maximal pp-definable equivalence.
  - Proved for difference laws, for their lifts, and for their shadows in
    which equality of first components is pp-definable. K₄, K₆, K₄ₓ₄ and the
    GF(4) lift are covered.
  - The census found such operations by search for L₂₂₃ and L₂₃₃ as well.
  - The shadow hypothesis is needed for the operation used. For the Z₃ law
    paired with itself, that operation fails, although the law is a
    difference law.
- **Dressings.** Each of the eight Boolean relations containing "not exactly
  two ones" gives a shadow of the Z₃ law. Only the full relation keeps a
  Hagemann–Mitschke or Day chain. For these shadows, any real decoration below
  the tops costs n-permutability and modularity, yet composition does not
  notice.
- **Conjecture 6.** Every law that composes like cycles is Mal'tsev on its
  tops. Below the tops it can carry clones far from Mal'tsev.

**A correction.** Census A's control text said that x ⊕ y ⊕ z = 0 over
Z₂ × Z₂ does not compose like cycles. Alone, it does: it is binary parity on
both bits at once, so its systems have parity's free sets.
- The census tested only its Mal'tsev operation, so the census's results
  stand.
- The proof uses the Z₂ × Z₂ law with two line congruences added instead.
  That law fails elimination.

**The narrowing from the plan.** The ticket planned Theorem 5 for every
shadow and disjoint union. The shadow case needed the hypothesis above, and
disjoint unions were dropped: the operation on mixed triples needs a separate
argument, and no example needed it.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| K₄ is 3-permutable and modular | Census search; the terms were then read off as lifted linear forms | New to the program; elementary |
| Restriction lemma | Fibres of shadows | Routine |
| K₆ neither modular nor n-permutable | The shadow construction plus the two-element clone of "not exactly two ones" | New to the program; standard characterizations |
| Incomparability with the classical conditions | Combining K₄, K₆ and Z₆ | New to the program |
| Mal'tsev on the tops for difference laws, lifts and some shadows | The tops of `MATROID-CONVERSE-20261021-001B-P001`, Proposition 6 | New to the program. It resembles a difference term, which is Mal'tsev modulo a commutator (see [Characterizing the commutator in varieties with a difference term](https://arxiv.org/abs/2112.00715)); that literature was not searched for this notion |
| The Z₂ × Z₂ correction | Checking the proof's control | Correction |

**Did the perspective do real work?** Partly.
- **The tools are standard universal algebra.** Term conditions, clones and
  congruences.
- **The program's own reading supplied two things.**
  - **The question.** It asks which conditions composition sees.
  - **The answer's shape.** Composition reads only the tops, so the classical
    conditions, which hold or fail across the whole variety, cannot express
    it.
- **The decisive example K₆** came from the program's shadow construction.

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the census and the proof.
- 2 are administrative: this note and the ledger.

The recommendation is therefore substantive work.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — classical Mal'tsev conditions of laws that compose like cycles | **Successful** (negative answer) | Composing like cycles is incomparable with permutability, n-permutability and modularity. The planned route to the top lemma through modularity is closed. Mal'tsev on the tops is proved for the known families. Open: Conjecture 6. |
| Local direction — algebraic conditions for composition | Continue, narrowed to the tops | The global classical conditions are the wrong level. Every example is Mal'tsev on its tops, and the tops exist in every such law. |
| Broader exploration — composition (open question 3) | Known alternatives | (1) Conjecture 6 together with a top lemma for all such laws. (2) The three-value diagonal question (1/3). (3) The deferred space directions. Converting the composition series into a note is premature while Conjecture 6 is open. |
| Long-term goal — intrinsic structure from logic | Obstruction learned | Cycle-like composition is invisible to the classical global conditions, and whatever algebra it forces lives on the tops. If Conjecture 6 and the top lemma both hold, every such law is linear algebra on its tops, with arbitrary decoration below. |
| Next recommendation — tops of laws that compose like cycles, as a fresh epic | **Next step:** Continue. Test Conjecture 6 and the hidden-circuit question (is every circuit of a system visible modulo the tops?) on the closest laws outside Theorem 5: all 256 subsets removed from the lift's (2,2,2)-block, and lifts of the shadow K₆. Then attempt a proof through rectangularity modulo the tops. | A counterexample would refute Conjecture 6 and become the subject. Confirmation would make a full characterization the target: composing like cycles exactly when the law is linear algebra on its tops. |
| Interest — that next step | **2/3 — Promising** | Every known law that composes like cycles fits, tops always exist, and the census is cheap. The main uncertainty is whether rectangularity modulo the tops yields one operation that works for nested ranges at once. |
| Execution — that next step | Deferred | Not started: the owner's request covered this epic. Stop and reassess if the census finds a counterexample, or if the proof attempt stalls after one epic. The next step is the owner's decision. |
