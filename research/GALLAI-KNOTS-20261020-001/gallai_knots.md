# Colouring knots compose along Gallai trees

Epic `GALLAI-KNOTS-20261020-001`, closed 2026-10-20.

## How the question was chosen

The freezing epic ended with a recommendation: a bounded scan between two
candidates. The owner approved it.

- **(a) Space from native moves (open question 9).** Do a law's smallest
  finite moves build a low-dimensional complex?
  - For linear laws, the minimal finite moves either do not exist or are the
    cells of the substrate the law was written on. They do not exist for
    Ledrappier's law, or for any law on a tree. They are the cells for Tseitin's
    law and the gauge law on Z^d, whose minimal moves are the unit squares.
  - That met the stop condition set beforehand: the moves only reproduce the
    substrate's cell structure. A static law can remove space but not create
    it.
  - Not pursued.
- **(b) Composition of native knots (open question 3).** How do knots join
  through hidden witnesses into larger knots?
  - A quick probe found that witness triangles, 5-cycles and K₄ compose star
    knots into knots, while witness 4-cycles and 6-cycles impose nothing.
    That pattern is the Gallai-tree pattern of degree-list colouring.
  - Chosen.

## The evidence

- [The census](../../experiments/GALLAI-KNOTS-20261020-001A/GALLAI-KNOTS-20261020-001A-E001_witness_census/contract.json),
  with [result](../../artifacts/GALLAI-KNOTS-20261020-001A/GALLAI-KNOTS-20261020-001A-E001_witness_census/result.json).
  It covers every connected witness graph on at most 6 vertices, up to
  isomorphism, for q = 3 and 4.
- [The proof](../../proofs/GALLAI-KNOTS-20261020-001B/GALLAI-KNOTS-20261020-001B-P001_gallai_composition/proof.md).

## What was found

The setting is the proper q-colouring law. Hidden witnesses form a connected
graph W, and each witness carries q − deg(v) visible leaves, so that every
witness has exactly q neighbours.

- **A knot exactly on Gallai trees.**
  - The leaf relation passes K1–K3 exactly when every block of W is a complete
    graph or an odd cycle.
  - K2 and K3 hold for every W. Only K1 depends on W, and it reduces exactly to
    degree-choosability (Borodin; Erdős–Rubin–Taylor).
  - When W is not a Gallai tree, the hidden witnesses impose nothing at all.
  - The census agrees on all 83 networks within its caps: 27 knots, exactly
    the 27 Gallai trees.
- **Which witness cycles kill the knot.**
  - A block that is neither complete nor an odd cycle dissolves the knot. One
    example is a block that is an even cycle.
  - This is a statement about blocks, not cycles: K₄ contains 4-cycles and
    still gives a knot.
  - Read as frustration: an odd witness cycle with equal two-colour lists
    cannot be coloured, so it pins; an even one always can, so it leaks
    freedom.
- **A gluing law.**
  - Glue two witness networks at a vertex. The excluded leaf colourings of the
    composite are exactly the joins of the parts' excluded colourings, through
    a unique hidden split of the glued vertex's colours.
  - The excluded colourings are the block colour-set systems
    (Kostochka–Stiebitz–Wirth).
  - Their number is q! times a product of one mass per block. A tree witness
    network on k vertices excludes q!·((q − 1)!)^(k−1) colourings, whatever
    its shape.
  - So knots compose freely along Gallai trees. The star is the unit, and each
    bridge multiplies the count by (q − 1)!.
- **Fusion, not contact.**
  - Composition replaces the parts. The glued vertex's neighbours become hidden
    witnesses, and the composite knot lives on a new set of leaves.
  - Two knots that share a visible vertex form a common hub, not a knot: K2
    fails at every unshared variable.
  - Hiding that vertex alone leaves no constraint. Absorbing it into the
    witnesses gives one larger knot.
  - In general, it follows from Fact 2 of the knot intuition that, in one
    system, no knot's variables contain another knot's variables.
- **Nativity.**
  - On the d-regular tree, every finite subtree with chosen leaves carries
    such a knot.
  - Where branches do not freeze (p* = 0), all of them are native at almost
    every broadcast world. This holds at d = q for every q ≥ 3, where the
    branch polynomial is the monomial (q − 1)!/(q − 1)^{q−1}·p^{q−1}, and
    below the freezing thresholds.
  - The rainbow colouring at d = q freezes every vertex, so there no such knot
    is native. The source-aware reading separates these two worlds, while the
    K1–K3 verdict is the same in both.
- **Outside the hypothesis.** A found 9 knots for q = 3 and 1 for q = 4 on
  witness networks with a vertex of degree q + 1. These are not classified.

**For the open questions.**
- **Question 3, composition.** In the colouring law, knots compose by
  enlarging the hidden witness network. The result is one knot, which exists
  exactly along Gallai trees and has multiplicative mass. They never compose
  into two knots joined by a contact: sharing a visible variable gives a hub.
- **Question 2, witnesses.** A hidden witness can take part in a further
  binding while its degree stays within q. The binding survives exactly when
  every block stays complete or an odd cycle.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Knot ⟺ Gallai tree | Census of witness networks; the knot test on leaf relations | Classical core (Borodin 1977; Erdős–Rubin–Taylor 1979). The reading, with K2 and K3 automatic, is the program's. |
| Block colour-set systems | Gluing law, induction over blocks | Classical (Kostochka–Stiebitz–Wirth 1996) |
| Gluing law as knot composition | The program's question 3 | Elementary; the composition reading is the program's |
| Multiplicative excluded mass | Counting through the gluing law | Not found stated; immediate from the decomposition |
| Nativity on regular trees; the rainbow world | The source-aware reading, with the freezing proof | Short consequences of the freezing recursion |
| Shared visible vertex is a hub | The program's hub rule | Elementary |

**Ratio since the last checkpoint:**
- 2 artifacts are substantive: the census and the proof.
- 2 are administrative: this note and the closure ledger.

That is half administrative, so the next step must be substantive work,
conversion or stopping, not another administrative artifact.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — composition of colouring knots | **Successful** | Characterized exactly: knots exist along Gallai trees, the gluing law holds, and the mass is multiplicative. The mathematical core is classical degree-choosability. |
| Local direction — composing knots in colouring laws | Retire | Answered. Witnesses above degree q, lattices and other colouring laws would restate list-colouring theory. Results kept. |
| Broader exploration — the source-aware foundation | First answers to questions 3 and 9 | Question 9: a static law reproduces or removes the substrate's cells (scan). Question 3: fusion along Gallai trees in colouring laws; earlier, rings and networks of loops. Questions 2, 4 and 7 are partly or not assessed. Each concrete question so far has reduced to a classical theorem read as a knot theorem. |
| Long-term goal — intrinsic structure from logic | Obstruction learned | In this law, knots never form a network of distinct knots joined by contacts. They fuse into one knot over a larger hidden witness network, or share a hub. A native network would need a law whose knots compose without fusing. |
| Next recommendation — knots as circuits | **Next step:** Research directions. For a linear law, a variable set is constrained exactly when it supports a constraint. So its knots are the minimal supports, the circuits of a matroid: bonds for Tseitin's law, cycles for the plaquette (gauge) law on the grid. They compose like cycles: two knots sharing a variable leave a knot inside their union without it. Colouring knots do not; they fuse over new variables (Theorem 1). Ask whether composition like cycles marks exactly the group-like, or almost affine, laws. First step: a prior-art check (Simonis–Ashikhmin's almost affine codes, 1998; matroid ports in secret sharing), then a census of small relations. | It would tell the program where topology-like composition lives, joining this epic to the result that only group-like knots remember a loop. The alternative already on the table is to convert the Tseitin results into one note (2/3, from `URQUHART-TSEITIN-20261020-001`). |
| Interest — knots as circuits | **1/3 — Exploratory poking** | The split between linear and colouring laws is real in every example. The main uncertainty is that almost-affine code theory probably covers the positive direction already. The converse fails for laws with a single knot, so the right statement is not yet clear. |
| Execution — that check | Deferred to the owner | Not started. Stop if the census only re-derives almost affinity, or finds no law between the linear and the colouring cases. |
