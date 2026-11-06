# Space from a law

Epic `SURFACE-GLUING-20261024-001`, closed 2026-10-24.

## The question

The owner asked for "space from a law" after `READING-COST-20261024-001`, when the torus branch had drifted from the core intuitions.
- **Question 9** of the knot intuition asks which law, not written on a space in advance, gives a shape that looks like a space of
  low dimension.
- **Re-posed under the no-selection framing:** what does the native gluing of knots build, and which laws see only that?
- **Intuitions this epic targets:**
  - space from logic without a drawn space;
  - the two/three boundary;
  - what's real is the binding between loops;
  - everything relational.

**The evidence:**
- [Native gluing builds surfaces, and four knots see only the surface](../../proofs/SURFACE-GLUING-20261024-001A/SURFACE-GLUING-20261024-001A-P001_surface_gluing/proof.md)
  (A, proof);
- [Hub-free gadgets cannot create parity](../../proofs/SURFACE-GLUING-20261024-001B/SURFACE-GLUING-20261024-001B-P001_no_parity_without_hubs/proof.md)
  (B, proof);
- [bounded scan](scan.md) (2D topological field theories, Frobenius objects in relations, emergent-space programs);
- **scoping (scratch, not evidence):**
  - the first gluing probe (path against star);
  - the census by gluing shape;
  - the parity-gadget search;
  - the hub-free closures before the theorem;
  - a provenance check at closure, which matched the no-lone counts with the Verlinde dimensions of the Fibonacci theory for genus 1
    to 6.

## Outcome in one paragraph

**Gluing three-place knots natively builds two-dimensional space; gluing two-place relations builds only one-dimensional space; and
the knots that see only that space are exactly the fusion rules of the two smallest topological theories.**
- **Surfaces (A).**
  - A hub-free network, where every shared distinction joins exactly two knots, is a pants decomposition of a compact orientable
    surface. Each knot is a pair of pants; each open distinction is a boundary circle; the genus is the number of independent cycles.
  - A hub is the one place where the surface fails to be a surface: three sheets meet along a circle.
  - Two-place relations glue only into lines and loops.
  - So the two/three boundary is the boundary between dimension one and dimension two of what native gluing builds.
- **Which laws see only the surface (A).** A symmetric relation glues topologically exactly when two glued copies already give a
  result symmetric in its four legs. Among the knots, four pass:
  - **The two parity knots.** Their result fixes the boundary's total, and every handle doubles the hidden witnesses, one hidden bit
    per handle. Emergence counts the genus.
  - **The two "no lone value" knots.** They remember the boundary only on spheres; one handle frees everything. Their witnesses count
    handles through a matrix whose eigenvalues are (5 ± √5)/2: integer counts 2, 5, 15, 50, … built from two incommensurable rates.
  - **The rest.** The two frozen knots forget once two copies meet. Not-all-equal and the 27 asymmetric knots depend on the
    arrangement, not only on the surface.
- **What the four are (provenance check at closure).**
  - The "no lone one" knot is the fusion rule of the Fibonacci anyon: a trivalent vertex may not carry exactly one τ. Its counts are
    the Verlinde dimensions of the Fibonacci theory, and (5 + √5)/2 is that theory's global dimension 1 + φ².
  - Parity is the fusion rule of the theory with two abelian anyons.
  - Each comes in two versions, according to which value plays the vacuum. These are the two fusion rings of rank two without
    multiplicities.
- **Memory cannot be created without hubs (B).** The knots and everything glued from them without hubs keep their excluded tuples
  pairwise non-adjacent. Gluing multiplies excluded fractions as a₀b₁ + a₁b₀. So no hub-free gadget of non-parity knots ever produces
  parity, even with several knot types combined. With hubs, not-all-equal and pins define parity.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Read each knot as a pair of pants and glue | Hub-free networks are surfaces; genus = cycle rank; two places give lines and loops | Proved (A, Theorem 1) |
| Probe two gluings of one surface | Parity agrees; not-all-equal and one-in-three differ | Scoping |
| Census all symmetric relations up to six copies | Topological with counts: parity, no-lone value, all-equal, constants, trivial; frozen relations only as relations | Proved (A, Theorems 2 and 3); 220 shapes checked |
| Expect only parity (groupoid prediction) | Wrong: the no-lone knots also glue topologically, at genus 0 in their relations and at every genus in their counts | The prediction was corrected by the census |
| Ask which knots build parity without hubs | Only parity, by an exact density identity; all 32 non-parity knots together have a closure of 279 relations with no parity face | Proved (B) |
| Provenance check at closure | The no-lone counts are the Fibonacci Verlinde dimensions; the four topological knots are the rank-two fusion rules | Classical identification; the novelty label of A's Theorem 3 is corrected below |

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1 | Hub-free networks of three-place relations are pants decompositions of compact orientable surfaces (Euler characteristic minus the number of copies); two-place relations give paths and cycles; a hub is a non-surface point. |
| A, Theorem 2 | A symmetric three-place relation glues topologically, as a relation or with counts, exactly when two glued copies give a result symmetric in its four legs. |
| A, Theorem 3 and Corollary 4 | Exactly four knots glue topologically with counts: the parity knots (leg total fixed, 2^g witnesses) and the no-lone-value knots (sphere: no lone value on the legs; handle: everything; closed counts tr H^(g−1), H = [[3,1],[1,2]]). |
| B, Theorem 5 and Corollary 6 | Hub-free gluing, self-gluing and pinning never create a parity face of dimension three or more; only the parity knots build parity without hubs. |

## What this changes

- **Question 9 gets a base-level answer at the level of topology.**
  - Native gluing of three-place knots builds a surface, determined by the network's own sharing pattern rather than drawn.
  - A topological law makes every network logically equivalent to that surface: parity, or the Fibonacci rule.
  - The law still selects no surface, and no geometry (metric, flatness) appears.
- **The two/three boundary acquires a dimensional reading.** Two places: dimension one. Three places: dimension two.
- **Emergence counts handles.** "Emergence counts loops" (`EMERGENCE-BITS-20261021-001`) becomes "emergence counts handles": exactly,
  for parity, one hidden bit per handle; asymptotically, for the Fibonacci rule, log₂((5 + √5)/2) ≈ 1.86 bits of witness count per
  handle.
- **The relational intuition has a classical instance.** Two incommensurable rates, (5 ± √5)/2, cancel into integer counts. This is
  the Fibonacci theory's Verlinde formula, reached here from Boolean knots.
- **See also `NATIVE-HARDNESS-20261024-001`, closed alongside.** It shows that every native contradiction is a parity system inside
  the blocks of the network. The law that counts handles is also the only native source of contradiction beyond forced values.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Space is recognized, never created, by a law | `KNOT-SPACE-20261020-001` (two-site structure must be written) | **Refined.** Two-site structure arises natively: hub-free gluing is pairwise by the hub guardrail itself, and it builds surfaces. What is not created is any particular surface, or geometry. |
| Only group-like (groupoid) relations glue topologically | This epic's own prediction from the Frobenius classification | **False for counts.** The no-lone knots glue topologically with witness counts through the Fibonacci fusion ring, which is not a groupoid. As relations, they are topological only on spheres, as the groupoid classification requires. |
| A law with memory can build it in any network | Implicit in "memory ⟺ the law defines parity" (`BASE-THREE-20261021-001`), whose definitions use hubs | **Refined.** Without hubs, memory is never created; it must be present from the start. |
| The golden-ratio handle is new | A's proof.md (novelty `candidate-local-delta` for Theorem 3) | **Corrected.** It is the Verlinde formula of the Fibonacci theory (see below). |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A, Theorem 1 | Pants decompositions and dual cubic graphs | Classical |
| A, Theorem 2 | Generalized associativity and closing handles | The elementary half of the classical correspondence between 2D topological field theories and commutative Frobenius algebras |
| A, Theorem 3 and Corollary 4 | Census and induction | **Known overlap, corrected at closure.** The four knots are the fusion rules of the two multiplicity-free fusion rings of rank two, the abelian one and the Fibonacci one, each with either value as vacuum, and their counts are Verlinde dimensions (Verlinde 1988; rank-two classification, Ostrik 2003). The program's contribution is the route: among Boolean knots glued natively, these are exactly the laws that see only the surface. |
| B | Hypercube independent sets and an exact gluing count | New to the program; `candidate-local-delta` |

**Did the perspective do real work?** Partly.
- **What it did.** The pants reading and the density identity came from the program's own vocabulary: a knot binds loops, and a shared
  distinction is pairwise by the hub guardrail. They made the census and the no-parity theorem computable.
- **What it rediscovered.** The topological knots are classical objects: fusion rules. Theorem 3 is an independent rediscovery of a
  known classification, with high folklore risk.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: space from a law | **Status:** Successful | Native gluing builds surfaces exactly (A); the laws that see only the surface are the rank-two fusion rules (A, with the classical identification); memory cannot be created without hubs (B). No geometry appears. |
| Local direction: native gluing of three-place knots | Practically exhausted at the level of topology | Dimension two is the most that pairwise sharing builds; the Boolean topological laws are classified. |
| Broader exploration: topology program | Known alternatives | Hubs (three sheets on a circle) are the only native-looking route beyond surfaces; geometry remains unconstructed. |
| Long-term goal: space from logic (question 9) | Capability gained | Two-dimensional topology from native gluing, with the law counting handles; the bridges to dimension three and to geometry are missing. |
| Next recommendation: dimension three through hubs | **Next step:** Continue, with a fresh epic | In 2D the Fibonacci rule counts surfaces exactly. Its 3D theory (Turaev–Viro) lives on triangulations whose edge labels are shared by many tetrahedra, which is hubs. Do hubs let a Boolean knot see a 3-manifold? First discriminator: count Fibonacci-admissible edge labellings of triangulations related by 2–3 moves. If the counts change, 3D topology needs weights (6j symbols involving φ); then test whether such weights can be native. |
| Interest: that recommendation | **2/3 — Promising** | It directly continues the space intuition, and it ties space to complexity: hubs carry NP-hardness (`NATIVE-HARDNESS-20261024-001A`), and evaluating the Fibonacci 3D invariants is hard. Main uncertainty: the machinery is classical, and Boolean counts are probably not invariant in 3D. |
| Execution | Deferred to the owner | Bound: one epic; stop if Boolean counts are not invariant and no native weighting is found. |

**Alternatives:**
- the growth of emergent information per handle for the arrangement-dependent knots (1/3);
- a note on native gluing and the fusion rules (1/3: mostly classical).
