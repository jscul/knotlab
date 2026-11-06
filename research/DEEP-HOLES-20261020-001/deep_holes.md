# Deep holes: how far local reasoning must look to see a network's charge

Epic `DEEP-HOLES-20261020-001`, 2026-10-20. This is the decision note.
`HOLES-COHOMOLOGY-20261019-001` found that the holes of permutation
networks are shallow, and recommended testing whether the program's hole
criterion predicts how deep local reasoning must look on networks that are
hard. This epic does that.

## The setting

Put a knot at every vertex of a cubic graph, with the graph's edges as its
distinctions, so that every distinction is shared by two knots.
- **Parity knots.** Each vertex asks its three edges to sum to its charge
  mod 2. This is a Tseitin formula.
- **Sum-mod-3 knots.** Each vertex asks out-flow minus in-flow to equal its
  charge mod 3.
- **Impossibility.** Such a **charge network** is impossible exactly when the
  total charge is nonzero, a class in the reduced homology H̃₀ of the graph.
- **The dual of the previous epic.** There, witnesses at the vertices with
  contact on the edges made loop holes, classes in H¹.

**Depth** means the least number of distinctions that linear local reasoning
must hold at once to refute the network: the least level at which the affine
relaxation over a coefficient ring has no solution.

## What was found

### The program's plain hole criterion cannot see depth (B, prose with checks; A, census)

The criterion certifies a level whenever every small set of distinctions is
free of holes. But **every knot that excludes two or more states is already a
hole at its own scope.**
- For a Boolean knot with excluded set E, the hole has rank |E| − 1 over every
  field, so only atoms are free of it.
- The sum-mod-3 knot's hole has rank 10.

So on parity, sum-mod-3 and not-all-equal networks the criterion certifies
only level 2. That is trivial: bags of two edges hold no knot. The census
confirms this on every network (P3). Not-all-equal networks on the roster are
all possible anyway (P6).

### Depth depends on the coefficients, and then on a cut width (B, prose with verified certificates; A, census)

- **Rings that compute in the charge group see the hole at once.** F₂ and Z
  refute every impossible parity network at level 3, and F₃ and Z every
  sum-mod-3 network. Summing every vertex's flow counts each edge twice with
  opposite signs, leaving 0 = total charge.
- **Every other field must sweep the charge across a cut.**
  - **The theorem.** Over any field in which the group's order is
    invertible, the depth is exactly the **toggle width** of the graph,
    whatever the charges. That is the least k such that some sequence of
    vertex sets from ∅ to all vertices, toggling one vertex at a time, keeps
    every step's current cut plus the toggled vertex's star within k edges.
    This covers Q, F₃ and F₅ for parity, and Q, F₂ and F₅ for sum mod 3.
  - **The refutation** at that level is a sweep: it carries the flux across
    the current cut one vertex at a time. Its coefficients are ±1, so it
    refutes over every ring.
  - **The solution** one level below has a closed form: a Fourier sum over the
    cuts that fit in the bag, weighted by a sign or root of unity that records
    which side of each cut the excess charge is on.
- **On cubic graphs the toggle width is cutwidth + 1.**
  - Proved for the monotone version, where vertices are only added.
  - Observed for the full version on all 27 connected cubic graphs with 4 to
    10 vertices.
- **Signed reasoning can need one level more than nonnegative reasoning.**
  - The network's own variable graph is the line graph, where edges are
    adjacent when they share a knot.
  - On one 10-vertex cubic graph it has treewidth 4 while the cutwidth is 5.
    The depth there is 6: the level-5 solution is verified on every equation.
  - Sherali–Adams with nonnegativity refutes by treewidth + 1 = 5, by the
    standard tree-decomposition argument (not computed here).
- **The census agrees on every case.** Thirty networks on all 8 connected
  cubic graphs with at most 8 vertices, under 2–3 charge placements each,
  over F₂, F₃, F₅, Q and Z (P1, P2, P5). The independent check verified every
  certificate by substitution.
- **Depth is not a function of treewidth.**
  - Seven roster graphs have treewidth 3. K₄, the prism and two 8-vertex
    graphs have depth 5; K₃,₃, the cube and the third 8-vertex graph have
    depth 6.
  - The Wagner graph has treewidth 4 and depth 6 (P4).

### The census (A, exploratory; all six frozen predictions hold)

`DEEP-HOLES-20261020-001A-E001` covers:
- **graphs:** all 8 connected cubic graphs on 4, 6 and 8 vertices;
- **networks:** parity under three placements, and sum mod 3 on K₄, K₃,₃ and
  the prism under two;
- **rings:** F₂, F₃, F₅, Q and Z;
- **controls:** even-charge networks were never refuted, the homology code
  gave the known values, and the predictions shifted by one in either
  direction failed.

## What it means

- **Network holes come in two kinds, and the contact decides which.**
  - **Loop holes** (H¹) arise where contact acts on witnesses at the vertices.
    They are shallow: three witnesses at a time see them, over any ring.
  - **Charge holes** (H̃₀) arise where knots meet in distinctions on the
    edges. They are shallow for reasoning that can compute in the charge's
    group, and otherwise as deep as the graph's best sweep.
- **Depth is about carrying.** A charge can only be seen by carrying its
  partial sums across a separating boundary. So the depth is the widest
  boundary the best sweep must hold, plus one vertex. Local holes (the shape
  of each knot) do not measure it; the cut structure of the whole network
  does.
- **It locates the classical hardness, small-scale.** For expanders the
  cutwidth grows linearly. That is consistent with the classical result that
  Tseitin formulas need large degree outside characteristic 2. Here the cause
  is visible on small graphs: the coefficients cannot compute in the charge
  group, so the charge has to be carried, and carrying costs the layout's cut
  width.
- **Depth is a width, not a distance.** The toggle width measures how wide a
  boundary the best sweep must hold. It is not a distance, a path length or a
  native metric, and the layouts were made by hand.

## Nearest known results

- **Tseitin formulas.** Easy in characteristic 2 (Gaussian elimination).
  Linear Nullstellensatz and polynomial-calculus degree in other
  characteristics on expanders (Grigoriev 2001; Buss, Grigoriev, Impagliazzo
  and Pitassi 2001). Averaging over symmetries and using characters is the
  standard method there.
- **Exact game characterizations.** Galesi, Talebanfard and Torán (SAT 2018;
  ACM TOCT 2020) characterize resolution width, depth and variable space of
  Tseitin formulas by a cops-and-robber game related to treewidth.
- **Treewidth and counting logics.** CFI graphs, which are Tseitin on a graph,
  and the treewidth bound for Weisfeiler–Leman (Dawar and Richerby 2007).
  Sherali–Adams and counting logics (Atserias and Maneva 2013).

**Novelty: known-overlap-likely** for the method and the matched-ring
statements. We did not find stated:
- the exact level of the affine relaxation for charge networks over a field
  of the other characteristic, as the toggle width;
- its coincidence with cutwidth + 1 on small cubic graphs.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: deep holes (does the hole criterion predict depth; what does) | **Status:** Successful | The plain hole criterion is stuck at level 2 (proved). Depth is 3 over matched rings and exactly the toggle width over every other field, whatever the charges (proved with verified certificates). All six frozen census predictions hold. |
| Local direction: the program's plain (worst-case) hole criterion | Retired as a depth measure | Every non-atom knot is a hole at its own scope, so the criterion cannot rise above the trivial level on charge networks. The accepted results (`HOLE-CRITERION-COLOURING-20261019-001`) stand where the criterion is informative: injective constraints with many values. |
| Broader exploration: knots, holes and local reasoning | Known alternatives | Loop holes (H¹) are shallow over every ring. Charge holes (H̃₀) are shallow for matched rings and as deep as the layout's cut width otherwise. Not assessed: OR-combinations of charge networks (Lichter and Pago), Nullstellensatz degree, and Sherali–Adams with nonnegativity beyond the remark above. |
| Long-term goal: native structure from knots (questions 3 and 9) | Capability gained; obstruction learned | Gained: an exact invariant of a whole network, depth = toggle width, which measures the network's extent as a width. Learned: local hole structure, the shape of each knot, says nothing about it. Still missing: a law that makes the network. |
| Next recommendation: close the cutwidth gap | **Next step:** Continue in a fresh epic. Test whether the toggle width ever drops below its monotone version on the 85 connected cubic graphs with 12 vertices, then prove monotonicity or record the counterexample. With this epic's theorems, a proof gives "the depth of a charge hole over a field that cannot compute in its group is cutwidth + 1 on every connected cubic graph". | It turns an observation on 27 graphs into a theorem in a classical parameter, or finds where non-monotone reasoning helps. Alternative: write the result up as a short self-contained note for proof-complexity readers (1/3: the novelty search was brief and the method is standard). |
| Interest | **2/3 — Promising** | A sharp, falsifiable question with a cheap discriminator. Main uncertainty: monotonicity results for width parameters are often true but technical, and the theorem's interest for the program is indirect. |
| Execution | Not started | Needs the owner's go-ahead. Stop if a counterexample is found on 12 vertices (record it and characterize depth by the toggle width only), or if no proof emerges within one epic. |
