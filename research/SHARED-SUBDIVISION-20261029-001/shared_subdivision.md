# Shared-boundary self-reproduction on the triangular lattice

Epic `SHARED-SUBDIVISION-20261029-001`, closed 2026-10-29.

## The question

- **The owner's decision.** On 2026-10-29 the owner approved the recommended continuation of `EXACT-TOWERS-20261029-001` ("Yes,
  let's continue").
- **Why this question.** Exact self-reproduction with private hidden variables builds only finitely ramified, tree-like spaces. So:
  can a law reproduce itself exactly on a genuinely two-dimensional space, where neighbouring copies share their subdivided
  boundary?
- **The family tested.**
  - Copies of one knot class on the triangular lattice: on up triangles (S2), or on all triangles with one placement per orientation
    (S1). That makes 122 rules.
  - Each triangle is cut into k² with shared new vertices, at scale k = 2 and 3.
- **Intuitions targeted:**
  - space from logic without a drawn space;
  - the two/three boundary;
  - universally influential cycles;
  - everything relational.

**The evidence:**
- [Which knots reproduce themselves under shared subdivision](../../proofs/SHARED-SUBDIVISION-20261029-001A/SHARED-SUBDIVISION-20261029-001A-P001_which_knots_reproduce_themselves_under_shared_subdivision/proof.md)
  (A, proof by exact computation);
- [The exact two-dimensional laws](../../proofs/SHARED-SUBDIVISION-20261029-001B/SHARED-SUBDIVISION-20261029-001B-P001_the_exact_two_dimensional_laws/proof.md)
  (B, proof);
- **scoping (scratch, not evidence):**
  - the first runs on the 6- and 8-tori;
  - the symmetry orbits;
  - the patch tests;
  - an aborted slow run at scale 3.

## Outcome in one paragraph

**On genuinely two-dimensional space, a law reproduces itself exactly only by being parity, behaving as parity, or dissolving
into pairwise lines.**
- **Census (A).** Of 122 rules (copies of one knot class on up triangles or on all triangles), shared subdivision by 2 leaves 22
  exact rules, and subdivision by 3 leaves 6.
  - Every exact rule has an affine solution set and zero entropy density.
  - Every other rule has a non-affine solution set.
  - Not-all-equal (Wannier's antiferromagnet) is never exact.
- **The families (B).**
  - Parity on up triangles is the Newman–Moore model. It is exact at scale 2 with N(2m) = N(m)², because (1 + S)² = 1 + S² over the
    two-element field.
  - Parity on all triangles has the Baxter–Wu ground states. It is exact at scale 2 because 2 permutes the colour classes mod 3.
  - Twelve three-excluded rules have exactly the Baxter–Wu solutions on every torus tested.
  - Twisted not-all-equal is exact at every scale, but only because walls persist and its solutions collapse to lines of constant
    value. No triangle then carries a knot.
- **Rigidity.** The parity families are rigid on the plane, so under the canonical source-aware reading no knot is native at their
  solutions. Exactness keeps a knot only through parity.

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1 | Exact census, 122 rules. Scale 2 (6- and 8-tori): 22 exact (parity on up triangles; parity, twelve three-excluded pairs and six twisted pairs on all triangles). Scale 3 (9-torus): the six twisted pairs. Set-level and counted exactness coincide. |
| A, Theorem 2 | Every exact rule has affine solution sets (tori of side 3 to 6) and at most 2^L solutions (L = 2..11). Every other rule is non-affine somewhere. No rule above 0.1 bit per site is exact. |
| B, Theorem 1 | Newman–Moore: rows of x ↦ (1 + S)x + b. At scale 2 the restriction is onto with N(m) extensions, and N(2m) = N(m)². Not exact at scale 3. Rigid on the plane. |
| B, Theorem 2 | Baxter–Wu: opposite vertices equal, so the solutions are colour-class patterns. Exact at scale 2, not at 3. Rigid. |
| B, Theorem 3 | Line collapse: walls persist, so the solutions are the 2^L line-constant configurations. Exact at every scale. No triangle projection is a knot. Not rigid (half-lines). |
| B, Proposition 4 | The twelve three-excluded rules equal Baxter–Wu on tori of side 2 to 11. No patch of radius ≤ 3 explains it. |
| B, Corollary 5 | Every exact rule falls in one of the three families. A triangle carries a knot only in the parity families, and only when their solution set has more than one element. |

## What this changes for the core intuitions

- **Space from logic.**
  - Private substitution (`EXACT-TOWERS-20261029-001`) lets non-linear knots reproduce themselves, but only on tree-like spaces.
  - On genuinely two-dimensional space, every exact law is frozen or line-like and affine.
  - So, within this family, exact self-reproduction of non-linear emergence needs hierarchy, while genuine extended space admits only
    linear (parity) or pairwise structure.
- **The two/three boundary.** Exactness on genuine space sorts laws exactly along the program's thesis:
  - three-place structure survives only as parity, which is linear;
  - twisted not-all-equal survives only by dissolving into equalities, which are pairwise;
  - every knot outside these, including not-all-equal, fails.
- **Universally influential cycles.**
  - The parity families keep a three-place correlation at every scale. Newman–Moore's solutions are the same Pascal-triangle pattern
    at every scale, by Frobenius.
  - But those families are rigid. No finite change moves between solutions, so under the source-aware reading nothing native lives
    there.
- **Arithmetic rather than geometry.** Parity's two-dimensional exactness holds at scale 2 and fails at scale 3. It is a property of
  the two-element field and of the three colour classes, not of the space.
- **Everything relational.**
  - The exact laws are the ones whose global relation is a linear code, or a product of equalities.
  - A non-linear relation cannot be its own coarse-graining here.
  - Its relation survives only as a relation, not as an exact counted law.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Sharing boundaries would let non-linear knots reproduce themselves on genuine space | Recommendation of `EXACT-TOWERS-20261029-001` | **False in this family.** Only parity, rules that behave as parity on tori, and a knot that collapses into equality lines are exact. |
| Parity's exact self-similarity is geometric | The towers' growth exponents | **Refined.** On the lattice it is arithmetic: exact at scale 2, not at scale 3, through the two-element field and the colour classes mod 3. |
| A rebuilt knot keeps its three-place structure | `HUB-SURVIVORS-20261029-001`, `EXACT-TOWERS-20261029-001` | **Not on genuine space.** Twisted not-all-equal reproduces itself exactly only by dissolving into pairwise equality along lines. |

## Scoping and corrections

- **A slow first run at scale 3.** It used non-BLAS integer products, and was stopped and replaced by the engine of ticket A:
  floats for the support, residues modulo four primes below 2^18 for equality.
- **Rigidity was overclaimed in scoping.** An early reading said every exact family is rigid. Twisted not-all-equal is not rigid on
  the plane: half-lines can end anywhere. Ticket B claims rigidity only for the parity families.
- **A local proof for the three-excluded rules was tried and failed.** The extra tuple extends to patches of radius 1 to 3, so their
  coincidence with Baxter–Wu is recorded as computed on tori of side 2 to 11, and left open.
- **Enumeration was too slow for line collapse.** Ticket B therefore certifies each family's solution set by inclusion and counting
  (all predicted configurations satisfy the rule, and the transfer-matrix count matches).

## Literature (bounded)

- **Newman and Moore (1999).** The triangular plaquette model, parity on up triangles: a linear cellular automaton whose
  self-similarity under rescaling by 2 is classical (Willson; Allouche, von Haeseler, Peitgen and Skordev). Its degeneracy as a
  function of the torus size was studied in arXiv 2301.02826.
- **Baxter and Wu (1973).** Parity on all triangles: four ground states on tori whose side is divisible by 3.
- **Wannier (1950).** Not-all-equal on all triangles, with positive entropy.
- **Exact real-space renormalization** of two-dimensional lattices is rare.
- **Not found.** A census of which hard laws are exact under shared subdivision.

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A | Exact census of 122 rules, two scales | Candidate local delta |
| B, Theorems 1 and 2 | Linear cellular automata; colour classes | Classical in substance |
| B, Theorem 3 | Wall persistence | Elementary, not found as such |
| B, Proposition 4 | Certified computation | Candidate local delta; open for all tori |

**Did the perspective do real work?** Partly.
- **The question came from the program's arc.** It asked which laws reproduce themselves, first natively, then with hubs, then on
  genuine space.
- **The exact families are classical.** The census and the "parity or pairwise" reading are new here.
- **The source-aware reading made rigidity relevant.** The parity families are rigid, so no knot is native there.

## Gaps

1. **Exact and affine.** That they coincide is observed in this census, not proved. Other subdivisions, lattices, three dimensions,
   and relations beyond the knots are untested.
2. **The three-excluded rules.** Their equality with Baxter–Wu on every torus is open, with no local explanation up to radius 3.
3. **Nativeness for line collapse.** Whether a knot is native at some non-periodic solution on the plane is open.
4. **Criticality.** Laws that are not exact, such as not-all-equal, may still be scale-invariant asymptotically (Wannier's
   antiferromagnet is critical). That was not studied here.
5. **Review.** No human or external review.

## Work ratio

- **Artifacts that changed a conclusion (2):** A, B.
- **Administrative:** the closure ledger, the discovery record and its disposition.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: shared-boundary self-reproduction on the triangular lattice | **Status:** Successful | Census of 122 rules at two scales. The three exact families are proved, with rigidity for the parity ones. The knot survives exactness only through parity. |
| Local direction: exact self-reproduction | Practically exhausted for non-linear emergence | Private substitution gives non-linear exact laws only on tree-like spaces. Shared substitution gives only affine, zero-entropy laws. |
| Broader exploration: space from logic (question 9) | Obstruction learned | Exact self-similarity cannot build genuine extended space carrying non-linear emergence, in the families tested. The open alternatives are asymptotic, critical scale invariance, or a general theorem. |
| Long-term goal: the two/three boundary as emergence | Capability gained | Exactness on genuine space sorts laws into linear three-place (parity), pairwise (lines), or excluded. This is the program's thesis appearing in a new setting. |
| Next recommendation: is exact self-reproduction on genuine space always affine? | **Next step:** Continue, with a fresh epic | First discriminator: all 256 relations on three bits on up triangles, at scales 2 and 3, together with an attempt at a local criterion: the two-step row relation, read on even sites, equals the rule. That would make the up-triangle case a theorem. |
| Interest: that recommendation | **2/3 (Promising)** | A proof would join four parity-only results (native gluing, Pachner moves, memory = affine, shared subdivision) in one statement. A non-affine exact relation would be the first non-linear law to reproduce itself on genuine space. Main uncertainty: the up-triangle case may reduce to known facts about linear cellular automata. |
| Execution: that next action | Deferred to the owner | No successor created. Alternative (1/3): the critical counterpart, how fast not-all-equal's three-corner correlation decays across scales (Wannier criticality, largely classical). Stop the affine route if the 256-relation census finds no new exact family and the local criterion is classical. |
