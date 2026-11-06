# The diagonal lemma, and why composition cannot see fibres

Epic `DIAGONAL-LEMMA-20261021-001`, closed 2026-10-21.

## The question

`MALTSEV-CONVERSE-20261020-001` reduced the converse of the difference-law
theorem to a local converse: in a law whose knots compose like cycles, must
every knot be rectangular? It recommended the diagonal lemma, which would
complete that converse for 3-variable knots. The owner asked to continue with
it.

**The evidence.**
- [The census](../../experiments/DIAGONAL-LEMMA-20261021-001A/DIAGONAL-LEMMA-20261021-001A-E001_diagonal_census/contract.json),
  with [result](../../artifacts/DIAGONAL-LEMMA-20261021-001A/DIAGONAL-LEMMA-20261021-001A-E001_diagonal_census/result.json).
- [The proof](../../proofs/DIAGONAL-LEMMA-20261021-001B/DIAGONAL-LEMMA-20261021-001B-P001_shadow_converse/proof.md).

## What was found

- **The diagonal lemma and the local converse are false.** The smallest
  counterexample found is a 3-variable knot on four values:

  K₄ = {(x, y, z) ∈ {0,1,2,3}³ : x̄ + ȳ + z̄ ≡ 0 (mod 3)} − {(2, 2, 2)}

  Here x̄ reads 3 as 2.
  - K₄ is a non-rectangular knot, and its law composes every circuit like
    cycles.
  - The reason: in every system, K₄ has exactly the constrained sets of
    x + y + z ≡ 0 over Z₃. A system can force the excluded triple only by
    pinning a variable with K(x, x, x), and that merely removes the value 2
    from its range.
- **Why: composition only sees which sets are constrained.** Two general
  constructions show this.
  - **Shadows.** Pair a difference law with any relation it dominates, through
    a surjection. The product has the difference law's constrained sets in
    every system, whatever its fibres look like. Example: the Z₃ parts sum to
    zero, and the bits are not exactly two ones.
  - **Lifts.** Double one value of such a law and remove its constant tuple.
    This is K₄.
- **What composition still forces.**
  - **Fibre distance** (new). If a knot's fibre graph is connected and two
    fibres are two steps apart, composing with fibre sharing gives a knot
    whose fibres all meet, and so a failure. A law whose knots compose like
    cycles therefore has fibre graphs that are disconnected or dense. The
    counterexamples hide their non-rectangularity inside a component.
  - On two values every knot is still a parity (the converse proof).
  - Three values are open.
- **The lemma holds generically.**
  - Every random non-rectangular knot in the census was resolved:
    - 3-variable knots on 3–6 values: 160 with no direct case. All were
      resolved without cross-position identification, and 154 also by the
      diagonal derivation.
    - 4-variable knots on 2–3 values: 50.
  - The census predictions that failed (L4–L6) were candidates. The proof
    resolved all of them except K₄, which it proved to be a counterexample.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Shadow theorem | Scoping showed failures are cheap to find, so a counterexample had to hide its fibres behind a dominating law | New to the program; elementary |
| Lift theorem and K₄ | The census's lifted knots on four values (L6) | New to the program; elementary |
| Fibre-distance construction | Asking why the diagonal derivation works | New to the program; elementary |
| Generic truth of the lemma | Census A | Observation |

**Did the perspective do real work?** It did. Reading knots as circuits
relative to ranges is what makes a shadow invisible: a dominated factor adds no
constrained set. The mathematics is elementary.

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the census and the proof.
- 2 are administrative: this note and the ledger.

The recommendation is therefore substantive work.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the diagonal lemma and the local converse | **Successful** | Both are refuted. The counterexample K₄ is a 3-variable knot on four values, proved by the lift theorem. The lemma still holds for every random knot tested, and two values admit no counterexample. Three values are open. |
| Local direction — explaining cycle-like composition through fibres or polymorphisms | Practically exhausted | The naive converse and the local converse both fail. Beyond the direct cases and the fibre-distance construction, no fibre property is forced. Keep Theorems 1, 2 and 4. |
| Broader exploration — composition (open question 3) | Known alternatives | (1) The matroid-level converse: are the constrained sets of every such law, system by system, those of a difference law? (2) The three-value question (1/3, narrow). (3) The deferred space directions: higher genus (1/3) and native moves. |
| Long-term goal — intrinsic structure from logic | Obstruction learned | Cycle-like composition, the matroid structure of knots, is coarser than any fibre-level algebra. A law can carry hidden fibre patterns without changing how its knots compose. What remains is which matroids logic can carry this way. |
| Next recommendation — the matroid-level converse, as a fresh epic after this one | **Next step:** Continue. Ask whether every law whose knots compose like cycles has, system by system, the constrained sets of a difference law. First, scan what is known about representing matroids by the free sets of relations (partition representations, secret sharing). Then test the cheapest discriminator: can one relation's constrained sets form a non-representable matroid such as Vámos, in a law whose knots compose like cycles? | Every known example satisfies it: shadows, lifts and disjoint unions. A yes would say cycle-like composition is algebraic at the level of matroids. A no would say logic can carry topologies that no difference law carries. |
| Interest — the matroid-level converse | **2/3 — Promising** | The statement is concrete, every known example satisfies it, and either answer is informative. The risk is that it meets open problems on matroid representability and stays undecided. |
| Execution — the matroid-level converse | Deferred | Not started, because the owner's request covered this epic. Stop if a general construction realizes every matroid inside a law whose knots compose like cycles, which would refute it, or if the literature already settles weak representations. The next step is the owner's decision. |
