# Findings

These eleven findings are the ones we packaged for outside readers. Each comes
with Lean proofs, a self-contained note or exhaustive checks that run from this
repository. Every other result is in [RESULTS.md](RESULTS.md), dated and linked
to its proofs as recorded.

Each finding is something we proved and checked ourselves. It is one of three
kinds:

- a **new result**: as far as our searches found, it was not known before;
- a **new proof**: a known fact reached by a different route;
- a **new reading**: a known fact asked in the program's language, where the
  question is ours and the answer may be classical.

Status says how the claim is supported. "No human review" means no human
expert has checked it. AI-assisted reviews are recorded where they happened.
Record labels name the entries in our private research log that these items
come from, so that later corrections can be traced.

| # | Finding | Kind | Status | Where |
| --- | --- | --- | --- | --- |
| 1 | The knot test K1–K3; no 2-CNF defines a knot; width 3 binds any number of loops | New reading | Proved (Lean); checked exhaustively | [INTUITIONS §2–3](INTUITIONS.md#2-the-knot-test), [`lean/ForgettingKernel.lean`](lean/ForgettingKernel.lean), [`lean/KnotKernel.lean`](lean/KnotKernel.lean) |
| 2 | Two loops and a contact have 34 knots in 5 shapes; a knot hides at most one bit, and only parity hides a full bit | New reading | Proved (short proof); checked exhaustively | [INTUITIONS §4](INTUITIONS.md#4-what-a-knot-hides), [`tests/`](tests/test_knotlab.py) |
| 3 | Pairwise rules make holes but never knots; every simplicial complex is the shape of some system | New reading | Checked; the construction is proved in Lean | [INTUITIONS §5](INTUITIONS.md#5-holes-and-knots), [`lean/LoopNerve.lean`](lean/LoopNerve.lean) |
| 4 | Requirement and choice are one knot read two ways (16 of the 34 two-loop knots) | New reading | Checked exhaustively | [INTUITIONS §6](INTUITIONS.md#6-requirement-and-choice) |
| 5 | Competing pairs make exactly the four not-all-equal knots on three variables, none on four or more, and every knot with hidden variables | New reading (three variables: an instance of a known criterion); new result (four or more: not found stated) | Proved (Lean) | [INTUITIONS §7](INTUITIONS.md#7-knots-from-competing-pairs), [`lean/CompetitionKernel.lean`](lean/CompetitionKernel.lean) |
| 6 | The ring theorem: a ring of knots excludes exactly the odd loops, and only parity carries a loop at full strength | New reading (elementary; known overlap likely) | Proved (Lean) | [INTUITIONS §8](INTUITIONS.md#8-which-knots-remember-a-loop), [`lean/RingKernel.lean`](lean/RingKernel.lean) |
| 7 | Loop nerves: free contact binds nothing; knots among loops are atoms; a knot among k loops needs k + 1 witness values | New reading (elementary; parts not found stated) | Proved (Lean) | [INTUITIONS §8](INTUITIONS.md#8-which-knots-remember-a-loop), [`lean/LoopNerve.lean`](lean/LoopNerve.lean) |
| 8 | The Nullstellensatz degree of Tseitin formulas is the toggle width: cutwidth + 1 on graphs of maximum degree three, exactly cutwidth in the ±1 encoding | New result (not found stated; standard methods) | Proved (7-page note); `replay.py` checks every certificate on ten graphs; no human review | [`notes/tseitin-nullstellensatz-degree`](notes/tseitin-nullstellensatz-degree/) |
| 9 | Counting 2-colourings of 3-regular 3-uniform hypergraphs with Pfaffian incidence graphs: polynomial after removing one edge from a non-2-colourable one; #P-hard under branching twists, without signs, and on braces | New result (as far as found; folklore risk stated per theorem) | Proved (10-page note); `independent.py` recomputes the headline numbers; no human review | [`notes/pfaffian-hypergraph-colourings`](notes/pfaffian-hypergraph-colourings/) |
| 10 | Counting homomorphisms from knot groups to solvable groups can be #P-hard: Rowell's Conjecture 3.2(b) fails on links for S₃ and on knots for S₄, unless FP = #P | New result (no earlier refutation found) | Proved (14-page note); link checks included; knot results checked in our workspace and by two AI-assisted reviews; no human review | [`notes/knot-group-counting`](notes/knot-group-counting/) |
| 11 | A counterexample to Conjecture 1.4/4.2 of ECCC TR26-007 (unions of affine subspaces, used for Res(⊕) lower bounds) | New result | Proved (short proof); `verify.py` | [jscul/affine-sunflower-counterexample](https://github.com/jscul/affine-sunflower-counterexample) |

## Sources and record labels

| # | Record labels in our research log |
| --- | --- |
| 1 | `KNOT-FOUNDATION-20261019-001A`, `KNOT-FOUNDATION-20261019-001E` |
| 2 | `KNOT-FOUNDATION-20261019-001E` |
| 3 | `KNOT-FOUNDATION-20261019-001D`, `HOLES-COHOMOLOGY-20261019-001B` |
| 4 | `KNOT-FOUNDATION-20261019-001C` |
| 5 | `KNOT-COMPETITION-20261019-001A` |
| 6 | `KNOT-LOOPS-20261019-001B` |
| 7 | `HOLES-COHOMOLOGY-20261019-001B` |
| 8 | `TSEITIN-NS-DEGREE-NOTE-20261020-001`, `DEEP-HOLES-20261020-001B`, `CUTWIDTH-DEPTH-20261020-001B` |
| 9 | `COUNT-NOTE-20261031-001` and the records listed in the note's evidence section |
| 10 | `ROWELL-NOTE-20261026-001` and the records listed in the note's evidence section |
| 11 | `AFFINE-SUBSPACE-EROSION-001` |

## What counts as packaged here

A finding enters this list only when all of these hold:

1. It has a complete proof, in Lean, in a note, or on the intuition page.
2. Its numbers can be rechecked by a script in this repository.
3. We looked for prior statements, and the finding states what we found.

The other results in [RESULTS.md](RESULTS.md) have proofs and checks in the
full record, written in the program's own language. They include our degree
and size bounds for Tseitin formulas in other proof systems, and the spaces the
not-all-equal knot builds. Corrections are listed in [HISTORY.md](HISTORY.md).
