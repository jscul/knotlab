# What do laws that compose like cycles carry on their tops?

Epic `CYCLE-TOPS-20261021-001`, closed 2026-10-21.

## The question

`MALTSEV-CONDITIONS-20261021-001` showed that composing like cycles is not a
classical Mal'tsev condition. Every known example instead had a polymorphism
that is Mal'tsev modulo the tops: the unique maximal proper pp-definable
equivalence on each range. It conjectured that this is forced (Conjecture 6).
The owner approved a fresh epic with two parts:
- a census of the closest laws outside the proved families: the removals from
  the lift's (2,2,2)-block, and the lifts of K₆;
- a proof attempt through rectangularity modulo the tops.

**The evidence.**
- [The census](../../experiments/CYCLE-TOPS-20261021-001A/CYCLE-TOPS-20261021-001A-E001_tops_census/contract.json),
  with [result](../../artifacts/CYCLE-TOPS-20261021-001A/CYCLE-TOPS-20261021-001A-E001_tops_census/result.json).
- [The proof](../../proofs/CYCLE-TOPS-20261021-001B/CYCLE-TOPS-20261021-001B-P001_decided_on_tops/proof.md).

## What was found

- **The top lemma holds for every law that composes like cycles.**
  - Every system has exactly the circuits of its image modulo the tops. So no
    circuit hides below the tops, and a system's matroid is its top image's
    matroid.
  - **The proof.** Put each variable and a copy blurred by its top into one
    system. They form a two-element circuit, so they are parallel elements of
    that system's matroid. Exchanging each variable for its copy carries every
    circuit to a circuit of the blur.
  - It needs only circuit elimination. The previous epic had shown that the
    matroid proof's route through modularity and Fleischer's lemma cannot be
    extended, so this is the route that works.
  - It proves the top-lemma form of the matroid proof's Conjecture 5.
- **Reflexive relations lie below the top.** Every reflexive pp-definable
  relation on a range is total or lies inside the top. This strengthens the
  matroid proof's Proposition 6 from equivalences to reflexive relations.
- **Ties are bijections of tops.** The top image of every tie is the graph of
  a bijection, which is an isomorphism of the induced structure.
- **Knots are functional or overlapping.** At each variable of a knot, the top
  image either determines that variable's top from the others, or lets every
  two of its top classes share a fibre. Only the functional case was seen.
- **Conjecture 6 was false as stated.** Parity beside the isolated-value
  relation J composes like cycles. That law is Proposition 1 of
  `MALTSEV-CONVERSE-20261020-001B-P001`, already in the repository when the
  conjecture was made.
  - Nothing links its two parts, so the top of its whole domain is equality.
    A Mal'tsev operation would then be needed on J, which has none.
  - K₄ beside the Z₃ law fails the same way.
- **The repair.** Restricted to the ranges of variables that lie in knots, the
  condition passes to disjoint unions (Conjecture 7). Census A found it in
  every surviving law.
- **The census** (signal true: H1–H6 and all four controls).
  - **Block removals.** Of the 46 classes of removals from the lift's
    (2,2,2)-block, exactly five have no failure in 6000 systems:
    - nothing removed;
    - (2,2,2);
    - (2,2,3);
    - {223, 232};
    - the whole one-3 class {223, 232, 322}.

    All five are dressed: every sampled system has the Z₃ law's constrained
    sets. The last two are new survivors.
  - **The other laws.** Both lifts of K₆ and both disjoint unions have no
    failure.
  - **What every surviving law showed** (37,242 systems over eleven laws,
    including the controls parity and Z₃).
    - No hidden circuit.
    - Every tie image is a bijection (103,302 ties).
    - Every knot image is functional (32,506 knots).
    - Some polymorphism is Mal'tsev modulo the tops on the knot ranges.
  - **The independent check** replicated these on 400 fresh systems per law.
- **Scoping for the next step (not evidence).** Two natural candidates for an
  overlapping knot image were tried.
  - **Evaluation of GF(2)² functionals.** The full relation is not a knot:
    the zero vector pins a tie.
  - **The equality indicator**, y = [a ≠ b] on three values. It is a knot that
    overlaps everywhere, but it fails elimination at once.
  - In both, the failure runs through an implication-like tie between Boolean
    variables.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Top lemma for every law that composes like cycles | Asking which circuits survive a blur, then putting the system and its blur in one system | New to the program; textbook matroid exchange, so an expert would find it quickly once asked |
| Reflexive relations lie below the top | Prop 6's tie chaining applied to ρ ∘ ρᵀ | Elementary strengthening |
| Ties are bijections of tops | Lemma 1 applied to the fibre-sharing of a blurred tie | New to the program |
| Knots functional or overlapping | Lemma 1 at each variable of a blurred knot | New to the program |
| Conjecture 6 refuted | Rereading the converse proof's Proposition 1 | Correction of the previous epic |
| Repair for disjoint unions | Components of systems | Elementary |
| Two new dressed survivors | Census A | Observation |

**Did the perspective do real work?** It did.
- **The question is the program's own.** It is the range-relative free set,
  and which circuits survive passing to the tops.
- **The decisive move is matroid-theoretic.** A variable and its blurred copy
  are parallel.
- **The universal-algebra tools of the previous epic were not needed.** No
  modularity and no Fleischer's lemma.

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the census and the proof.
- 2 are administrative: this note and the ledger.

The recommendation is therefore substantive work.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — tops of laws that compose like cycles | **Successful** | The top lemma is proved for every such law, ties are bijections of tops, and the old conjecture is refuted and repaired. Open: Conjecture 7 (Mal'tsev on knot tops) and whether knot images can overlap. |
| Local direction — composition through tops | Continue | Everything now happens on the tops. The matroid-level converse reduces to the shape of knot top images. |
| Broader exploration — composition (open question 3) | Known alternatives | (1) Knot top images, this line. (2) The three-value diagonal question (1/3). (3) The deferred space directions. (4) A write-up of the composition series once the converse is settled. |
| Long-term goal — intrinsic structure from logic | Capability gained | The circuits of every such law are read off simple tops, and ties there are isomorphisms. If knot images are functional and group-like, composing like cycles would be exactly linear algebra on the tops. |
| Next recommendation — knot top images, as a fresh epic | **Next step:** Continue. Try to prove that knot top images are functional, so that each is a Latin hypercube of its tops. The two failed candidates suggest the route: an overlapping variable yields an implication-like tie, which Corollary 3 forbids. Then test whether elimination forces the Reidemeister closure condition, which makes a Latin square isotopic to a group. That would give a Mal'tsev operation on knot tops (Conjecture 7). Start with a census of overlapping and non-group Latin knots on small tops. | If both hold, the matroid-level converse reduces to classical commutator theory for simple Mal'tsev algebras. A surviving non-group Latin knot would make cycle-like composition genuinely wider than linear algebra. |
| Interest — that next step | **2/3 — Promising** | Every census knot is functional, both overlapping candidates failed through a forbidden tie, and the payoff is a full characterization. The main uncertainty is whether elimination alone forces group-likeness, especially for non-abelian tops. |
| Execution — that next step | Deferred | Not started: the owner's request covered this epic. Stop if a census law composing like cycles has an overlapping or non-group Latin knot image, which would become the subject, or if the functional proof stalls after one epic. The next step is the owner's decision. |
