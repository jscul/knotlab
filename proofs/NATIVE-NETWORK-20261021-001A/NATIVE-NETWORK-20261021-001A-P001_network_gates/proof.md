# The native-network gate audit

Status: Proved

Ticket `NATIVE-NETWORK-20261021-001A`, 2026-10-21. It uses:
- the definitions of `KNOT-CIRCUITS-20261020-001B-P001`. A law composes like
  cycles when every system satisfies circuit elimination. Its free sets are
  then the independent sets of a matroid, and a pair of knots sharing only e
  is a hub exactly when it violates elimination at e.
- `CYCLE-TOPS-20261021-001B-P001`, Theorem 2 ("the top lemma"): every system
  has exactly the circuits of its top image.
- `THOMSEN-KNOTS-20261021-001A-P001`, Theorem 2: every circuit's top image is
  a Latin hypercube.
- `AFFINE-TOPS-20261021-001B-P001`, Theorem 1: tops are elementary abelian,
  and top images are cosets.
- `CYCLE-UTILITY-20261021-001A-P001` ("the utility proof"):
  - Proposition 2: a law that composes like cycles with constants has a
    polynomial-time constraint problem;
  - Proposition 4: constants break parity beside J and K₄.
- `CYCLE-TRACTABILITY-20261021-001A-P001`, Theorem 1 and Corollary 2: the
  equal-top lift of K₃ composes like cycles, and K₃ does not.
- `LOOP-HOMOLOGY-20261021-001A-P001`, Theorem 4: the 3-nets of Z₆ and S₃ do
  not compose like cycles.

The gates are those of `docs/COMMON_VERBIAGE.md` ("Contact network") and of
the canonical knot test in `docs/FOUNDATIONAL_THESIS.md`.

## The gates, read on allowed states

A **contact network** consists of complete contacts that:
- coexist in one declared native substrate;
- preserve compatible endpoint identities without collapse;
- compose by substrate-native laws, persistent under admitted restrictions,
  transports and recodings.

A larger common hub, an observer-drawn graph, or externally imposed
composition does not qualify. Under the canonical knot test, these gates
read as follows.

| Gate | Reading on allowed states |
| --- | --- |
| 1. Complete contacts | Each contact is a knot: K1–K3. This decides shared identity, two-sided essentiality, irreducible jointness, loss on erasure, and persistence under maps that preserve allowed states. Which structures count as native loops stays interpretive; each distinction is read as a loop's open distinction. |
| 2. One declared substrate | Both knots are knots of one system of one law. |
| 3. Endpoint identity without collapse | The shared distinction e is one variable, with the same range in both knots. Composition ties no two distinctions and loses none. |
| 4. Composition by a substrate-native law | The composite is obtained by forgetting e, which is the law's own projection. |
| 5. No larger common hub | After e is forgotten, the remaining distinctions are still constrained together. |
| 6. Not observer-drawn | Every verdict depends only on the allowed states, not on how the system is written. |
| 7. Not externally imposed | No rule beyond projection is used. |
| 8. Persistent under admitted restrictions | The composition rule (elimination) still holds after restrictions. Three are considered: erasure (forgetting distinctions), restriction by the law's own relations, and pinning (fixing values). |
| 9. Persistent under admitted transports | The same, after mapping the law to another. Four candidates are considered: isomorphism, pp-definable expansion or reduct, homomorphic equivalence, product. |
| 10. Persistent under recodings | Renaming variables or values, or changing the presentation of a system, changes nothing. |

## Standard statement

**Theorem 1 (the audit).** Let a law compose like cycles. Let K₁ on X ∪ {e}
and K₂ on Y ∪ {e} be knots of its systems, where:
- X, Y and {e} are nonempty and pairwise disjoint;
- e has the same range B in both.

Let P = K₁ ∧ K₂.
- **(a) Complete contacts.** In P, the projections onto X ∪ {e} and Y ∪ {e} are
  K₁ and K₂, and each passes K1–K3.
- **(b) Composition.** Forgetting e turns P into a single knot on X ∪ Y. With e
  kept, P has exactly three circuits: X ∪ {e}, Y ∪ {e} and X ∪ Y.
- **(c) No loss, no collapse, no hub.**
  - Every distinction of X ∪ Y lies in the composite.
  - No two distinctions are tied.
  - The pair is not a common hub.
- **(d) Native, not drawn, not imposed.** The composite is the projection of
  P's allowed states. Any presentation with the same allowed states gives the
  same composite.
- **(e) Recodings** carry all of this along.
- **(f) Restrictions.**
  - **Erasure and the law's own relations.** Restricting by them gives systems
    of the same law, so elimination persists. Erasing a distinction of a knot
    dissolves that knot and every composite containing it, by K2. That is loss
    on erasure, not a failure of composition.
  - **Pinning.** Elimination persists under pinning exactly when the law with
    all constants added still composes like cycles.
    - Affine laws over finite fields do.
    - Such laws have polynomial-time constraint problems (the utility proof).
    - Parity beside J and K₄ do not.
- **(g) Transports.**
  - **Preserving.** Isomorphisms, and pp-definable expansions and reducts,
    preserve every gate.
  - **Not preserving.** Homomorphic equivalence does not: the equal-top lift of
    K₃ composes like cycles, and K₃ does not. Products do not either: Z₂ and Z₃
    compose like cycles, and their product Z₆ does not.

**Corollary 2 (a native-network candidate).** In a law that composes like
cycles, every pair of knots sharing one distinction with a common range passes
the contact-network gate, under these admitted maps:
- recodings;
- erasure, and restriction by the law's own relations;
- isomorphisms and pp-definitions as transports.

**If pinning is admitted,** exactly the laws that still compose like cycles
with constants pass, and their constraint problems are solvable in polynomial
time. **Homomorphic equivalence and products** cannot be admitted transports.

**The pair test alone does not certify a law.**
- **Pairs pass where the law fails.** In the 3-net law of S₃, every pair
  composes into one knot, yet Thomsen's configuration, doubled, violates
  elimination. So the law fails gate 8 under restriction by its own relations.
- **Hubs.** Two not-all-three knots sharing a distinction form a hub, and fail
  gate 5.

## Nearest known results

- **Circuit elimination and composition** are matroid theory (Whitney 1935).
  The audit applies the program's characterization of laws whose systems are
  matroidal.
- **The program's own earlier contact chains,** Proofs 0011–0021, formed
  composed topology under the earlier contact gate:
  - two complete contacts sharing a recurrence;
  - a native successor between them;
  - restriction and recoding laws.

  The foundation triage files them under the earlier gate. This audit is
  their counterpart under the canonical knot test. Composition here is
  forgetting the shared distinction, not a successor phase.

**Classification: new to the program; elementary given the composition
series.**
- Theorem 1 combines the top lemma, the Latin and affine structure of tops,
  and the earlier counterexamples.
- The new content is the reading: which gates the pair passes, under which
  admitted maps.

## Theorem 1

*Proof of (a).*
- **The projections.** Every value of e in B extends, in K₂, to some values of
  Y. So the projection of P onto X ∪ {e} is K₁, and likewise for K₂.
- **K1–K3.** A knot's relation is constrained (K1), every proper subset of its
  variables is free (K2), and it is nonempty (K3).
- **What K1–K3 decides.** It decides the contact conditions (the canonical knot
  test). ∎

*Proof of (b).*
1. **Modulo the tops.** Write Ā_v for the top of v's range.
   - By the 3-net proof's Theorem 2 and the affine-tops proof's Theorem 1,
     K₁'s top image is ē = Σ_{x∈X} α_x x̄ + c₁. Each α_x : Ā_x → Ā_e is a group
     isomorphism, since the image is Latin at x.
   - Likewise K₂'s top image is ē = Σ_{y∈Y} β_y ȳ + c₂.
2. **Blurring commutes with P.** The top image of P is the set of solutions of
   the two blurred knots.
   - Take blurred values satisfying both, and choose elements of X in their
     classes.
   - K₂ for K₁ (X is free) gives e. Its class is forced, since the image is
     Latin at e.
   - Choose all but one element of Y in their classes. K₂ for K₂ (Y minus one,
     with e, is free) gives the last, and its class is forced.
3. **The circuits of the blurred P.** A set Z of its variables is free unless
   it contains X ∪ {e}, Y ∪ {e} or X ∪ Y.
   - **If Z misses some x₀ ∈ X and some y₀ ∈ Y,** assign Z freely. Pick e if it
     is not in Z. Then x₀ and y₀ are solved for, since α_{x₀} and β_{y₀} are
     isomorphisms.
   - **If Z misses e and some x₀,** assign Z freely. Y ∩ Z, with free choices
     for Y − Z, gives e through K₂, and x₀ follows from K₁. The case of y₀ is
     symmetric.
   - **Each of the three sets is constrained.** Each lies in a coset of index
     |Ā_e| ≥ 2: X ∪ {e} and Y ∪ {e} by their knots, and X ∪ Y by
     Σ α_x x̄ + c₁ = Σ β_y ȳ + c₂.
   - **Each is minimal.** Each proper subset misses a variable whose
     coefficient is an isomorphism, so it is free.
4. **The top lemma** gives P exactly these circuits. Forgetting e leaves the
   circuits of P that avoid e: just X ∪ Y. ∎

*Proof of (c).* By (b), X ∪ Y is a circuit: it contains every distinction, and
no circuit has two elements. Since X ∪ Y is constrained, the pair is not a hub
(the circuits proof's hub criterion). ∎

*Proof of (d) and (e).*
- **(d).** Free sets, circuits and projections are defined from allowed
  states. Projection is the law's own operation on systems.
- **(e).** A bijection of values maps allowed states to allowed states and
  preserves which projections are full products. Renaming variables relabels
  everything consistently. ∎

*Proof of (f).*
- **Erasure and restriction by the law's own relations.** Erasure forgets
  variables; restriction adds atoms of the law. Either way the result is again
  a system of the law, so it satisfies elimination. By K2, erasing a
  distinction of a knot frees the rest of it.
- **Pinning.**
  - **The criterion.** The systems obtained by pinning are exactly the systems
    of the law with constants added. So persistence under pinning is the
    statement that this law composes like cycles.
  - **Affine laws over finite fields.** Every relation, constants included, is
    an affine subspace, so every solution set is one too.
    - Its free sets are the sets onto which the direction space projects
      surjectively, ignoring variables with a single value.
    - These are the independent sets of a matroid: a linear matroid in which
      single-valued variables act as coloops.
    - Polynomial time is the utility proof's Proposition 2.
  - **The failures** are the utility proof's pinned systems, rechecked below. ∎

*Proof of (g).*
- **Isomorphisms** rename everything.
- **pp-definitions.** A system over pp-definable relations unfolds into a
  system of the original law, with the same allowed states on the visible
  variables.
- **The failures.**
  - **The lift.** It composes like cycles (the tractability proof's
    Theorem 1). K₃, to which it is homomorphically equivalent, violates
    elimination in x ≠ e ∧ e ≠ z.
  - **Z₆.** In c = a + m mod 6, the ties x ≡ e (mod 2) and e ≡ y (mod 3) leave
    {x, y} free (the loop-homology proof's Theorem 4). Yet Z₂ and Z₃, its
    factors, compose like cycles. ∎

## What this does not show

- **No paths, separation or distance.** Those are ticket B.
- **Native loops.** Whether the distinctions belong to native loops is
  interpretive, as in the canonical test.
- **The verdict depends on the admitted maps.** They are declared here.
  Admitting pinning or homomorphisms changes the verdict, as (f) and (g) show.
- **No physical claim.**

## Checks

`check.py` writes `result.json` in about a second. All checks pass, and all
six controls are rejected.

- **Pairs.** The eleven census laws composing like cycles were each tested in
  all nine placements of e: 99 pairs in all. Each law's main knot passes
  K1–K3. In every pair:
  - with e kept, the circuits are exactly the two knots and X ∪ Y;
  - with e forgotten, X ∪ Y is the only circuit;
  - there is no tie and no hub.

  A random relabelling of each law's values gives the same circuits in all 99.
- **Restrictions.**
  - **The law's own relations.** Random systems of the eleven laws, with hidden
    variables, satisfy elimination: 607 nonempty systems out of 660.
  - **Pinning, affine laws.** Random systems of x + y + z = 0 over F₂, F₃ and
    F₅, with constants pinned, satisfy elimination: 60, 73 and 64 nonempty
    systems out of 80 each.
  - **Pinning, the failures.** Parity beside J (with 3 pinned) and K₄ (with 2
    pinned) each violate elimination in an explicit system.
- **Transports.**
  - **A pp-definition.** x + y + z + w = 0 is pp-definable in parity, and 80
    random systems of the expanded law satisfy elimination.
  - **Homomorphic equivalence.** 80 random systems of the equal-top lift of K₃
    satisfy elimination (32 nonempty), while K₃ fails.
  - **A product.** The Z₆ system fails.
- **Remarks.**
  - **S₃.** All nine of its pairs compose into one knot, yet Thomsen's
    configuration, doubled, fails at two variables.
  - **Not-all-three.** Its pair has circuits {x₁, x₂, e} and {y₁, y₂, e}, and
    nothing remains after forgetting e: a hub.
- **Controls,** each rejected:
  - "a pair in a law composing like cycles can be a hub";
  - "pinning preserves composing like cycles in every such law";
  - "homomorphic equivalence transports it";
  - "products transport it";
  - "a law whose pairs all pass composes like cycles";
  - "every pair passes the hub test".
