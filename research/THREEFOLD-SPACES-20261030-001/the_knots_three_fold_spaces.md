# The knot's three-fold spaces

Epic `THREEFOLD-SPACES-20261030-001`, 2026-10-30.

## The question

- **The owner's request (2026-10-30).** "Yes, let's continue with this," on the recommendation of `SPACE-SELECTION-20261030-001`.
  - Prove or cite that the Fano plane is the only connected 3-regular triple system that is not 2-colourable. Then the Fano gadgets would be
    the knot's only three-fold spaces.
  - Then classify the mixed gluings of two-fold phase locks and three-fold phase knots, up to six triangles.
- **What changed before activation.**
  - The premise is false. Splicing one Fano plane into another gives a 13-point counterexample, and the matching 13-triangle gluings are
    exact for the knot.
  - The random probe behind the recommendation had simply missed these rare systems.
  - The more interesting reading, adopted under the owner's standing rule: is every three-fold space of the knot built from Fano planes?
- **Setting.**
  - A three-fold gluing's contacts each join three triangles with an odd number of base corners. By `SPACE-SELECTION-20261030-001C`, at the
    knot angle such a gluing is the unsigned not-all-equal problem on its dual triple system.
  - So the knot's three-fold spaces are the connected 3-regular triple systems that are not 2-colourable, read as gluings.
- **Intuitions targeted:** space from logic without a drawn space (a gluing made only of the knot's own contacts); the two/three boundary.

**The evidence:**
- [The knot's three-fold spaces are built from the Fano plane](../../proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane/proof.md)
  (A, proof). Its Theorem 4 is corrected by C.
- [Exhaustive classification of small three-fold spaces](../../proofs/THREEFOLD-SPACES-20261030-001B/THREEFOLD-SPACES-20261030-001B-P001_exhaustive_classification_of_small_three_fold_spaces/proof.md)
  (B, proof, SAT to 13 points).
- [Odd cycles of Fano planes](../../proofs/THREEFOLD-SPACES-20261030-001C/THREEFOLD-SPACES-20261030-001C-P001_odd_cycles_of_fano_planes/proof.md)
  (C, proof, with the erratum).
- Scoping (scratch, not evidence):
  - **Literature.** Robertson–Seymour–Thomas (Annals 1999) and McCuaig ("Even dicycles", 2000). The full text of the RST paper was read.
  - **SAT at 14 and 15 points.**
    - Untwisted 14: no solution, in 20 minutes.
    - Twisted 14: a solution. It was verified and became Theorem 2 of C.
    - Untwisted 15: still running when the epic closed, with no result recorded.
  - **The earlier probe** of 25,000 random systems.

## Outcome in one paragraph

**The knot's three-fold space is built from the two classical obstructions to 2-colouring: the Fano plane and the odd cycle.**
- **The dictionary (A).** A connected 3-regular triple system resists 2-colouring exactly when its incidence matrix is sign-nonsingular, and
  exactly when its 2-in 2-out digraph has no even directed cycle. That is the classical even-cycle problem. Its one exceptional
  indecomposable object is F7, the Fano plane (McCuaig).
- **The splice calculus (A).** Splicing along 3-edge cuts factorizes matching signs up to one twist. Fano planes compose without limit, so the
  knot has three-fold spaces with 7 + 6k triangles for every k.
- **The census (B).** Up to 13 points the only examples are the Fano plane and the Fano splice.
- **Odd cycles (C).** Beyond 13 points the family is not just Fano compositions.
  - A Fano block forces its three ports to one colour, so lines meeting a block twice are "not-equal" constraints.
  - Cycles of an odd number of Fano blocks (21, 35, … points) resist 2-colouring.
  - One twist makes even cycles odd: a twisted 14-point system, found by SAT, gives a 27-point space.
  - The knot is exact on all of their gluings.
- **Mixed gluings (A).** Gluings of phase locks and phase knots alone do not exist: counting base corners forbids every lock. So the planned
  "mixed" classification is empty.
- **An error caught.** A's first reduction claimed Fano compositions were everything, which was wrong. C corrects it.

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1 | Not 2-colourable = minimally so = sign-nonsingular = nice cycles 2 mod 4 = no even dicycle (connected 3-regular triple systems). |
| A, Theorem 2 | 3-edge tight cuts: matching signs factorize; pieces agree up to one common twist; an untwisted non-colourable piece acts as a point or a line. |
| A, Theorem 3 | Fano compositions are not 2-colourable. The knot has three-fold spaces with 7 + 6k triangles (λ(0) = 5^(k+1) where checked). |
| A, Lemma 5; Corollary 6; Proposition 7 | One twist never makes the Heawood graph or a planar cubic brace sign-nonsingular. The "only Fano" premise fails at 13. Lock-and-knot gluings have no locks. |
| A, Theorem 4 | **Superseded by C.** The claimed reduction to Fano compositions fails: contractions can repeat a point on a line. |
| B | Exhaustive, n ≤ 13: only the Fano plane (7) and the Fano splice (13), unique; no twisted system. The knot's three-fold spaces with ≤ 13 triangles are their duals. Phase-pure gadgets to six triangles have no locks and none is exact. |
| C | Block lemma. Cycles of k Fano blocks resist 2-colouring iff k is odd, and twisted cycles iff k is even. The twisted 2-cycle is the smallest twisted system (14). A 27-point splice. Knot spaces with 21, 27, 35, … triangles. Conjecture 5 (structure). |

## Reading

- **Space made only of the knot's own contacts.**
  - At the knot angle a three-fold contact is itself a not-all-equal knot on its triangles' phases. A gluing made only of such contacts is a
    space for the knot exactly when its dual configuration cannot be 2-coloured, but can once the corner line is removed.
  - The structures that cannot be 2-coloured are built from two atoms. The Fano plane is the smallest arrangement of triples with no
    2-colouring. The odd cycle is the smallest arrangement of "not equal" constraints with none.
  - Inside the gluing, "not equal" constraints appear where a line meets a Fano block twice.
- **The two/three boundary, again.** The three-place atom (Fano) and the two-place atom (odd cycle) are both needed, and a sign (a twist)
  turns an even cycle into an odd one. This is the program's boundary showing up as the grammar of the knot's own space.
- **Nothing is drawn but the gadget.** The gluing is still chosen, but the law decides which gluings work. For three-fold gluings the answer is
  now a classical, structured family, not a list.
- **Method lesson.** Two errors were caught by computation inside the epic: the false premise, and the overreaching reduction. Rare
  objects (13-point splices, 14-point twisted systems) are invisible to random sampling and visible to exhaustive SAT.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the knot's three-fold spaces | **Status:** Partially successful | The premise was refuted. The dictionary, splice calculus, closure and exhaustive census to 13 are proved. The family is shown to contain odd cycles of Fano planes beyond Fano compositions. The full classification is a stated conjecture (C, 5). |
| Local direction — three-fold gluings | Continue | The structure conjecture is concrete, and the classical theory (Pfaffian braces, Kasteleyn) points at a proof. |
| Broader exploration — space from a law (question 9) | Known alternatives | Gluings mixing locks, knots and free contacts are weighted phase models, not yet classified. Self-dual spaces are another alternative (the Fano plane reads the same with triangles and contacts swapped). |
| Long-term goal — space from logic without a drawn space | Capability gained | The law's own three-fold spaces are generated by the two obstructions to 2-colouring. Space here is assembled from the knot's contacts by a grammar the law dictates. |
| Next recommendation — the grammar of three-fold spaces | **Next step:** Continue, as a fresh epic. Prove Conjecture 5: every non-colourable 3-regular triple system is assembled from Fano blocks by splices and odd cycles. Route: tight-cut decomposition with doubled incidences allowed; Robertson–Seymour–Thomas for the braces; Kasteleyn's face parity for the planar pieces. Extend the SAT census with doubled incidences as a check. | It would complete the description of the space the knot builds from its own contacts, with two named atoms. |
| Interest — that recommendation | **2/3 — Promising** | The examples, the census and the classical structure theory all point the same way. Main uncertainty: 4-sums of planar braces may allow further pieces, and the result may be implicit in the Pfaffian literature, leaving the knot reading as the new part. |
| Execution — that next action | Deferred to the owner (fresh epic) | Done so far: dictionary, splice calculus, census to 13, odd cycles, erratum. Stop when the decomposition theorem is proved, or a counterexample piece is found and classified. |

**Recommendation.** **Continue**, as a fresh epic: the grammar of three-fold spaces (2/3). Three alternatives were considered.
- **Weighted mixed gluings (1/3).** Locks force free contacts, so mixed gluings are weighted phase models. A census at six triangles is
  completion-like.
- **Self-dual knot spaces (1/3).** Which three-fold spaces have duals that are also knot spaces, as the Fano plane does? Speculative.
- **A write-up of the standing wave and the spaces it builds (1/3).** It would cover the gasket epics, the gadget criterion and the
  three-fold spaces. Deferred until the classification settles.
