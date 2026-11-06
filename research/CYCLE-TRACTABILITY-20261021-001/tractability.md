# Does composing like cycles imply polynomial time?

Epic `CYCLE-TRACTABILITY-20261021-001`, closed 2026-10-21.

## The question

`CYCLE-UTILITY-20261021-001` proved a conditional tractability result. A law
that still composes like cycles with all constants added has a
polynomial-time constraint problem. It left open whether composing like
cycles alone suffices.

The owner set one bounded round, with no re-sharpening. The question counts
as settled if any one of these happens:
- the core of a law composing like cycles is proved to compose like cycles;
- that statement is refuted;
- a law composing like cycles is found with a non-Taylor core.

**The evidence:** [the proof](../../proofs/CYCLE-TRACTABILITY-20261021-001A/CYCLE-TRACTABILITY-20261021-001A-P001_hidden_hardness/proof.md),
with its [checks](../../proofs/CYCLE-TRACTABILITY-20261021-001A/CYCLE-TRACTABILITY-20261021-001A-P001_hidden_hardness/result.json).

## The answer: settled, negatively

The question is settled in two of the three permitted ways.
- **Refuted.** The lift of 3-colouring composes like cycles. Its core, K₃,
  does not.
- **Non-Taylor cores.** Laws composing like cycles can have the non-Taylor
  cores K₃ and not-all-equal. Their constraint problems are NP-complete.

**The construction is the equal-top lift.**
- **The lift.** Give every value a second coordinate in Z_q, and require
  every atom to share it.
- **The free sets.** In every system, the free sets are then the partial
  transversals of the components. That is a partition matroid, whatever the
  structure underneath.
- **The constraint problem.** The lift is homomorphically equivalent to the
  original structure. So every finite-template constraint problem is the
  problem of some law that composes like cycles.

**Being a core does not help.** The shifted lift adds a step relation on the
new coordinate. It still composes like cycles and keeps the constraint
problem, and it is a core whenever the original structure is.

| A law composing like cycles that is… | Its constraint problem | Source |
| --- | --- | --- |
| still composing like cycles with constants added | polynomial time | utility proof, Proposition 2 |
| a core with no nontrivial automorphism | polynomial time | Proposition 4 |
| a core whose only automorphisms are q translations, e.g. the shifted lift of one-in-three | can be NP-complete | Theorem 3 |
| not a core, but with a rigid core, e.g. the equal-top lift of one-in-three | can be NP-complete | Theorem 1 |
| arbitrary | every finite-template problem occurs | Theorem 1 |

**Without constants, composing like cycles does not imply polynomial time
unless P = NP, even for cores.** This is no claim about P versus NP. The
hardness is classical; the proof only places it inside laws that compose like
cycles.

## What the tops hide

- **The lifts have no knots.** Every circuit is a pair inside one component.
  The new coordinate supplies the top ("same first coordinate"), and the
  matroid sees only the components.
- **"Modulo the tops" carries the weight.**
  - The affine-tops theorem says that above the tops a law composing like
    cycles is affine geometry over finite fields.
  - This epic shows that the tops can hide any constraint problem below
    them.
- **Constants expose the hidden structure.** Pinning one element of the lift
  of K₃ turns 3-colouring into a tie that is not a bijection, and elimination
  fails. That is why the tractability theorem needs constants.
- **This matches the holes epic.** `HOLES-COHOMOLOGY-20261019-001` found that
  permutation holes cannot carry hardness. Here the hardness sits entirely in
  knot-free structure under the tops.

## A correction to the previous closure

The closed note [utility.md](../CYCLE-UTILITY-20261021-001/utility.md) says,
in its long-term goal row, that the program's NP-hard substrates "are exactly
where it fails". That is wrong.
- **The counterexample.** x ≤ y is tractable and also fails to compose like
  cycles.
- **The failing system.** In x ≤ e ∧ z ≤ e, the ties {x, e} and {z, e} are
  circuits, while {x, z} is free. Checked by direct computation.

The correct statement:

> cycle-like composition, with constants, certifies tractability; the
> program's NP-hard examples all lack it.

**Two refinements from this epic.**
- **"All lack it" holds only for the laws as given.**
  - One-in-three, not-all-equal and 3-colouring each fail elimination.
  - Their equal-top lifts compose like cycles. They are different laws with
    the same constraint problems.
  - So, without constants, neither failing nor passing is a complexity
    signature.
- **A superseded Interest row.** The previous Interest row said that "every
  known law composing like cycles is tractable". The lifts are now known laws
  that compose like cycles and have NP-complete constraint problems.

The closed note is not edited. This section is the correction.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Equal-top lifts compose like cycles | The constants failure in the utility epic: tops carry structure that only pinning exposes. Taken to the extreme, a free shared label is the top, and an arbitrary structure sits underneath. | New to the program. Elementary: a product with a trivial structure. |
| The core question refuted; non-Taylor cores | The lift is homomorphically equivalent to the original structure | New to the program. Classical hardness. |
| Shifted lifts are cores | The equal-top lift is never a core, since it retracts onto a fibre; a step relation removes the retraction | New to the program. Elementary: a product with a directed cycle. |
| Rigid cores are tractable | The canonical system of a core, a classical step, with the utility proof's Proposition 2 | Short application |
| x ≤ y fails | The owner's correction, checked | — |

**Did the perspective do real work?** Partly.
- **The question** came from the program's own characterization: tops, ties
  and elimination.
- **The answer** is a classical-style product, read through the program's
  matroid of free sets. The hardness is classical.
- **Folklore risk.**
  - The lifts as constructions: high. They are standard products.
  - The statement that they compose like cycles: low to medium. The notion
    is the program's own.

**Ratio since the last checkpoint.**
- 1 artifact is substantive: the proof, with three theorems and a
  proposition.
- 2 are administrative: this note and the ledger.

So the recommendation is substantive work.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — does composing like cycles imply polynomial time? | **Successful** | Settled negatively in two permitted ways: refuted (K₃), and non-Taylor cores found (K₃, not-all-equal). It holds even for cores (shifted lifts). The positive remainder is rigid cores and constants. |
| Local direction — composition and tractability | Practically complete; retired under the owner's stop rule | Without constants, composing like cycles carries no complexity information. With constants or rigidity, it certifies polynomial time. Laws with knots were not treated, and the stop rule leaves that unasked. |
| Broader exploration — the contact-first program | Known alternatives | (1) The holes connection, the owner's chosen next epic. (2) Contact, network and distance questions, queued. (3) Banking the composition series, through an expert check or a write-up. (4) Urquhart's conjecture. |
| Long-term goal — intrinsic structure from logic | Obstruction learned | Composing like cycles fixes what lies above the tops, finite-field affine geometry, but not what the tops hide. Hardness can sit entirely below the tops, in knot-free structure. |
| Next recommendation — the holes connection (fresh epic) | **Next step:** Continue. State and test the unified claim: group-like knots are exactly those that both remember loops and compose like cycles, so holes behave like homology over finite fields modulo the tops. Tie it to `KNOT-LOOPS-20261019-001` (only group-like knots remember a loop) and to `HOLES-COHOMOLOGY-20261019-001` (one H¹ class per loop). Then say what it implies for contact networks. | The first discriminator compares, on the census laws, three properties of each knot: it remembers a loop, it is group-like, and it lies in a law composing like cycles. A knot with two of them but not the third refutes or sharpens the claim. This epic adds the qualifier "modulo the tops": below them, anything can hide. |
| Interest — that next step | **2/3 — Promising** | Each half is proved separately: group-like knots and loops for single knots, and affine geometry modulo the tops for laws. The main uncertainty is a mismatch of level. Remembering a loop is a property of one knot, while composing like cycles is a property of a whole law. |
| Execution — that next step | Started, under the owner's instruction to study both directions in this order | One bounded epic: a precise statement, a proof or counterexample on the census laws, and the consequence for contact networks. Stop if the per-knot and per-law notions cannot be aligned within the epic, and close with the exact mismatch. The contact, network and distance questions stay in the queue. |
