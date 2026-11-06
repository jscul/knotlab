# Knots as circuits: which laws compose knots like cycles

Epic `KNOT-CIRCUITS-20261020-001`, closed 2026-10-20.

## The question

`GALLAI-KNOTS-20261020-001` found two things about the colouring law:
- its knots compose only by fusing over a larger hidden witness network;
- two knots that share a visible variable form a common hub.

Its decision note recommended asking when knots compose *like cycles*. The
owner approved continuing ("Let's continue exploring").

**The definitions.**
- A system's **circuits** are its minimal constrained sets of variables. A set
  is constrained when not every combination of its variables' possible values
  occurs.
- **Knots** are circuits of at least three variables (Fact 2).
- Two circuits sharing a distinction e **compose like cycles** when their union
  without e is still constrained. This is the circuit-elimination axiom of
  matroids, the axiom that cycles in a graph satisfy.

**The evidence.**
- [The census](../../experiments/KNOT-CIRCUITS-20261020-001A/KNOT-CIRCUITS-20261020-001A-E001_elimination_census/contract.json),
  with [result](../../artifacts/KNOT-CIRCUITS-20261020-001A/KNOT-CIRCUITS-20261020-001A-E001_elimination_census/result.json).
- [The proof](../../proofs/KNOT-CIRCUITS-20261020-001B/KNOT-CIRCUITS-20261020-001B-P001_circuit_composition/proof.md).

## What was found

- **Difference laws compose like cycles exactly when no distinction splits.**
  Suppose a law has a Mal'tsev polymorphism, a "difference" operation m with
  m(x, x, y) = m(y, x, x) = y, as groups have through x y⁻¹ z.
  - Such a law composes like cycles exactly when every subalgebra of its
    polymorphism algebra has a unique maximal congruence.
  - The proof is short:
    - a difference law's relations are rectangular;
    - so a circuit fixes its shared variable modulo a congruence;
    - so a failure needs two congruences whose composition is total.
  - **Reading:** a hub appears exactly when some variable's values can be
    coarse-grained in two independent ways that together pin it. Such a
    variable carries two distinctions, not one.
- **Fields and groups.**
  - Affine laws over finite fields compose like cycles.
  - A group's coset law composes like cycles exactly when every subgroup has a
    unique maximal normal subgroup:
    - yes: Z_{p^k}, S3 and the dihedral groups D_p for odd primes p;
    - no: Z6, Z2×Z2, A4 (through its Klein subgroup), D4, Q8, Dic3 and Z12.
  - On four elements, the GF(4)-linear law passes while the Z2×Z2 coset law
    fails. The polymorphisms decide, not the domain.
- **Boolean laws.**
  - A Boolean law composes like cycles exactly when it is affine (parity).
  - It composes its *knots* like cycles exactly when it is affine or
    bijunctive. Bijunctive laws have no knots at all.
  - Every other Boolean law with knots has knot hubs: Horn, dual Horn, OR₃ and
    NAND₃ clauses, or twisted clauses for complement-closed laws such as NAE.
    The proof uses Post's lattice.
- **Hubs.** Two knots that share only e form a hub exactly when every e-fibre
  of one meets every e-fibre of the other.
  - Colouring stars, Horn clauses and OR₃ are hubs.
  - Parity knots never are.
- **Readings.**
  - Tseitin's knots are the bonds of its graph, and the gauge law's knots are
    its cycles.
  - In both, knots compose like cycles.
- **Open.** Does every law that has knots and composes them like cycles have a
  Mal'tsev polymorphism?
  - Proved for Boolean laws.
  - True for every binary relation on three elements. The only non-Mal'tsev
    exceptions there have an isolated reflexive value, which ties every linked
    pair and leaves no knots.
- **The census's shortfall, kept on record.**
  - A's predictions P1, P3 and P4 hold, but its frozen signal is false.
  - Its bounded search found no knot at all for the eight negation-twists of
    1-in-3, so P2 was short by eight relations.
  - The ticket is recorded as obstructed. The proof supplies explicit
    four-copy definitions of knot hubs for all eight.

**For the open questions.**
- **Question 3 (composition) has its sharpest answer yet.** Knots compose
  like cycles exactly in difference laws whose distinctions do not split.
  Elsewhere they fuse, as in colouring, or meet at hubs, as in Horn laws.
- **This joins the earlier loop results.** The knot-loops epic found that only
  group-like knots remember a loop. Here, only difference laws compose knots
  into matroids, the structure of a cycle space.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Knots and ties are a system's minimal constrained sets, a matroid under elimination | Fact 2 read as a clutter; the composition question | Elementary |
| Mal'tsev laws compose like cycles ⟺ every subalgebra has a unique maximal congruence | The census (groups) and a direct proof from rectangularity | Not found stated; short from classical parts (rectangularity, Fleischer's lemma), so folklore risk is moderate |
| Group criterion: every subgroup has a unique maximal normal subgroup | Corollary | Not found stated |
| Boolean: cycles ⟺ affine; knots ⟺ affine or bijunctive | Census, then Post's lattice and explicit hubs | Affine ⇒ matroid classical; converse and knot level not found stated |
| Hub criterion by fibres | Gallai epic's shared-vertex remark | Elementary |
| Tseitin knots are bonds, gauge knots are cycles | Matroid duality | Classical |

**Ratio since the last checkpoint.**
- 2 artifacts changed a conclusion: the census and the proof.
- 2 are administrative: this note and the closure ledger.

So the next step must be substantive work, conversion or stopping.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — when knots compose like cycles | **Successful** | Characterized for difference (Mal'tsev) laws and for all Boolean laws. The census's search shortfall was resolved by explicit construction. The non-Mal'tsev case beyond Boolean is open. |
| Local direction — composition of knots (question 3) | Continue only through a new question | The colouring answer (fusion along Gallai trees) and this one (cycle-like exactly in difference laws with indecomposable distinctions) together map composition. Further laws would refine the conjecture rather than change the picture. |
| Broader exploration — the source-aware foundation | Questions 3 and 9 now meet | Composition like cycles means a law's knots form a matroid. A matroid can carry a graph intrinsically: a 3-connected graph is determined by its cycle matroid (Whitney), with vertices recoverable as non-separating cocircuits (Tutte). Not yet assessed: whether this gives "space from a law" (question 9). |
| Long-term goal — intrinsic structure from logic | Capability gained | The class of laws whose knots compose into cycle-space structure is now characterized for difference laws: exactly those whose distinctions do not split. That structure depends only on allowed states, not on how the law is written. |
| Next recommendation — space from knot matroids | **Next step:** Research directions. Test whether a difference law's knot matroid recovers a space from allowed states alone. First discriminators: (1) on gauge and Tseitin laws presented by scrambled constraints, recover the graph, or for planar Tseitin its dual, from the knot matroid; (2) check whether local difference laws written on no graph have graphic or cographic knot matroids more often than chance, and what dimension any recovered complex has. Alternative: prove or refute the conjecture that cycle-like composition with knots forces a Mal'tsev polymorphism (interest 1/3). | It would give question 9 a precise, presentation-invariant meaning: the space a law defines is the complex whose cycle or bond matroid is its knot matroid. |
| Interest — space from knot matroids | **2/3 — Promising** | Recovering a graph from its matroid is classical, so (1) is a calibration. The uncertainty is (2): it may only reproduce the graph the law was written on (the stop condition of the earlier space scan), or graphic knot matroids may be rare outside graph-based laws. |
| Execution — that scan | Deferred to the owner | Not started. Stop if no law outside graph-based presentations yields a graphic or cographic knot matroid beyond chance. |
