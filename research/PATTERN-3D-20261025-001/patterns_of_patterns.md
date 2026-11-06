# Patterns of patterns in three dimensions

Epic `PATTERN-3D-20261025-001`, closed 2026-10-25.

## The question

The owner approved the recommendation made at the close of `TWIST-3D-20261025-001`.
- **What was known.** With one bit per edge, counting laws on ordered triangulations see a closed three-manifold only through
  |H¹(M; Z/2)|. This holds with symmetric rules (`HUB-DIMENSION-20261024-001A`) and with twisted, ordered or orientation-dependent
  rules and positive weights (`TWIST-3D-20261025-001`).
- **The question.** What do larger distinctions see, made of patterns of bits? Which counting laws with three or more labels per edge
  survive the moves that relate triangulations of one manifold?
- **Prediction under test.** Only groups survive, so the counts are homomorphism counts of the fundamental group.
- **Intuitions this epic targets.**
  - Patterns of patterns: what composite distinctions can do.
  - Space comes from logic, in three dimensions.
  - The complexity side.

**The evidence:**
- [The moves force a groupoid](../../proofs/PATTERN-3D-20261025-001A/PATTERN-3D-20261025-001A-P001_the_moves_force_a_groupoid/proof.md)
  (A, proof for every label set, with exhaustive checks);
- [Complete censuses on three and four labels](../../experiments/PATTERN-3D-20261025-001B/PATTERN-3D-20261025-001B-E001_complete_censuses/contract.json)
  (B, experiment; [result](../../artifacts/PATTERN-3D-20261025-001B/PATTERN-3D-20261025-001B-E001_complete_censuses/result.json));
- [bounded scan](scan.md);
- **scoping (scratch, not evidence):**
  - C censuses of all tables on three and four labels and all relations on three labels;
  - a merged-label construction, which looked like a counterexample and failed;
  - the proof idea it suggested.

## Outcome in one paragraph

**The moves force a group, and counting sees space only through its loops' finite symmetries.**
- **Functions (A).** Let the long edge of every triangle be a function of its two short edges, on any finite set of labels, total or
  partial.
  - The law survives the ordered 2–3 and 1–4 moves exactly when its working triangles are the compositions of a finite groupoid whose
    components are all alike: the same number of objects times group order. The working triangles are those lying in an allowed
    tetrahedron.
  - The objects are invisible. The proof recovers them as the labels that compose with themselves to themselves.
  - The 2–3 move asks for associativity and the 1–4 move for division.
- **Everything on three labels (B).** Every one of the 2²⁷ triangle relations on three labels was tested, functions or not.
  - Every survivor is a groupoid law, possibly with free decorations: one, two or three constants, Z₂, Z₃, or the free laws on two and
    three labels.
  - On four labels, every surviving multiplication table hides a groupoid: Z₄, Z₂ × Z₂, the pair groupoid, or one or two constants.
- **What they see.** The count is a sum of |Hom(π₁(M), G)|/|G| over the groupoid's vertex groups G.
  - Taken together, these counts see exactly the finite quotients of π₁.
  - So no count separates lens spaces of equal order, such as L(5,1) and L(5,2), nor the pairs of Funar and Hempel.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Census of all 3⁹ tables on three labels | Only the three labelled copies of Z₃ | Scratch, then proved (A) |
| Census of all 4¹⁶ tables on four labels, in C | Z₄, Z₂ × Z₂, and groupoids hidden among junk labels: a pair groupoid inside 12 non-associative Latin squares, one or two constants inside other tables | Scratch, then supported (B) |
| Census of all 2²⁷ relations on three labels, in C | Seven laws: constants, Z₂, Z₃, free laws | Scratch, then supported (B) |
| Merge two arrows of different components into one label | Fails the 1–4 identity: mixed tetrahedra appear | Scratch; it pointed to the proof |
| Blocks and units | Units of different blocks always form an allowed tetrahedron, so every label has one block; the groupoid follows | Proved (A) |

## What was proved and supported

| Result | Content |
| --- | --- |
| A, Theorem 1 | Triangles in no allowed tetrahedron never enter a move identity, for any triangle rule. |
| A, Theorem 2 | A law whose long edge is a function of the short edges survives exactly when its working triangles form a finite groupoid with equal component values; λ = 1 and μ = objects × group order. |
| A, Corollaries 3 and 4 | The invariant is Σᵢ \|Hom(π₁(M), Gᵢ)\|/\|Gᵢ\|. Cited group theory then gives the finite quotients of π₁; lens spaces of equal order and the pairs of Funar and Hempel are never separated. |
| B | Relations on three labels: seven laws, all groupoid pullbacks. Tables on four labels: groupoids only, as A predicts. |

## What this changes

- **What counting sees of three dimensions.**
  - Bits see the mod-2 first cohomology.
  - Composite distinctions see more: every finite quotient of π₁. Abelian groups see only homology. Non-abelian groups can see beyond
    it, and S₃, with six labels, is the smallest. For example, it separates S³/Q₈ from RP³ # RP³, which have the same homology.
  - That is still all they see. Linking forms need phases, as in twisted Dijkgraaf–Witten theory.
- **Only the knot part sees.**
  - A groupoid's triangle relation is a knot in the sense of K1–K3 only when it has one object, that is, when it is a group. With more
    objects, composability constrains pairs of edges.
  - The objects cancel from the invariant. So the pairwise bookkeeping sees nothing, and the group knot does all the seeing.
  - On three labels, the surviving laws whose triangle relation is a knot are exactly Z₂ (parity) and Z₃.
- **Patterns of patterns.** The composite distinctions that live natively in three dimensions are symmetries. What they carry is how
  the loops of space map into a finite symmetry.
- **The complexity side** (cited).
  - Counting homomorphisms into an abelian group is linear algebra.
  - For class-2 nilpotent targets it is polynomial on triangulations (Samperton and Weiß, 2026).
  - For non-abelian simple groups it is #P-complete (Kuperberg and Samperton, 2018).
  - The boundary in between, starting with S₃, is open. The same split as in two dimensions, affine easy and the rest hard, has an
    unknown edge in three.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| A non-group structure might survive with composite labels and see something new | The recommendation behind this epic | **False for functions:** only groupoids survive, and they see no more than their groups. **False for all relations on three labels:** only groupoid laws with free decorations. |
| Seeing more of three dimensions needs signs | `TWIST-3D-20261025-001`, already refined there | **Refined again.** Composite labels see every finite quotient of π₁ without signs. Phases are still needed for linking forms. |
| Patterns of patterns grow what can be seen without bound | The program's intuition | **Bounded.** All counts together see exactly the finite quotients of π₁. Distinct manifolds remain invisible. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A, Theorem 2 (the converse) | The program's question with objects invisible; blocks and units | `candidate-local-delta`; folklore risk medium (nearest: Duskin–Glenn) |
| A, Corollaries | Untwisted Dijkgraaf–Witten for groups and groupoids; profinite facts cited | Classical |
| B | Exhaustive censuses | `no-overlap-in-bounded-search` for the relations; low depth. The table part is an independent check of A. |
| Knot reading (only the group part sees) | The program's K1–K3 test applied to A | Local reading of a classical cancellation |

**Did the perspective do real work?** Partly.
- **What it supplied.**
  - The question of what native distinctions can see, posed with unlabelled vertices, which led to the converse.
  - The knot reading: pairwise structure is invisible to the invariant.
- **What is classical.** The invariants themselves.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: patterns of patterns in three dimensions | **Status:** Successful (prediction confirmed, sharpened to groupoids) | Functions: proved for every label set. Relations: complete on three labels. |
| Local direction: counting laws with composite labels | Practically exhausted for what counts can see | For functions every count is a homomorphism count (proved); on three labels the same holds for all relations (supported). Only phases or labels on higher simplices could see more, and those are known theories. |
| Broader exploration: space from logic | Known alternatives | Phases (twisted Dijkgraaf–Witten, Turaev–Viro); labels on triangles (Yetter's 2-groups). Both are classical. |
| Long-term goal: space comes from logic, with its complexity side | Capability gained | Three-dimensional space is seen by native counting exactly through π₁'s finite quotients. The open question has moved to the complexity of those counts. |
| Next recommendation: where counting in three dimensions becomes hard | **Next step:** Continue, with a fresh epic | See below. |
| Interest: that recommendation | **2/3: promising** | It ties the complexity side to three-dimensional space. Abelian and class-2 nilpotent groups are easy, simple groups are #P-complete, and the middle (S₃, A₄, nilpotent class 3) is open in the literature. Main uncertainty: the question may be hard enough that one epic only maps it. |
| Execution | Deferred to the owner | Bound: one epic. Stop if neither a hardness reduction nor an algorithm for S₃ emerges; then record the open boundary. |

**The next step in more detail.**
- **The question.** For which finite groups G is counting homomorphisms from π₁ of a triangulated 3-manifold into G polynomial, and
  for which is it #P-hard?
- **The first discriminator: S₃**, the smallest non-nilpotent group.
  - Its count is a sum over H¹(M; Z/2) of the sizes of twisted Z/3 cohomology groups.
  - Either that sum has the quadratic structure that makes class 2 easy, or it encodes a #P-hard sum.
- **The reading.** In two dimensions the program found that the affine knots (parity) are easy and the rest are hard. Does the same
  line, abelian or nilpotent against the rest, divide easy from hard among the three-dimensional knots?

**Alternatives:**
- **Prove the classification for relations (1/3).** Every pure counting law would be a groupoid law with free decorations. This would
  complete the picture with low surprise.
- **Phases and linking forms (1/3).** Which signed or phased laws exist with small labels, and when do they see the linking form?
  Classical in outline.
- **A short note on the converse (1/3).** Moderate magnitude and medium folklore risk.
