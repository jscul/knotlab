# Space from knot matroids

Epic `KNOT-SPACE-20261020-001`, closed 2026-10-20.

## The question

`KNOT-CIRCUITS-20261020-001` showed that the knots of a difference law form a
matroid computed from allowed states alone, provided its distinctions do not
split. This epic asked what that matroid says about space:
- Can a law's allowed states carry a graph, a surface, or ends?
- Is that space made by the law or only found in it?

This is open question 9 of `docs/KNOT_INTUITION.md`. The owner asked for it
together with the converse question ("Do both").

**The evidence.**
- [The census](../../experiments/KNOT-SPACE-20261020-001A/KNOT-SPACE-20261020-001A-E001_space_census/contract.json),
  with [result](../../artifacts/KNOT-SPACE-20261020-001A/KNOT-SPACE-20261020-001A-E001_space_census/result.json).
- [Its continuation](../../experiments/KNOT-SPACE-20261020-001C/KNOT-SPACE-20261020-001C-E001_embeddings_and_local_laws/contract.json),
  with [result](../../artifacts/KNOT-SPACE-20261020-001C/KNOT-SPACE-20261020-001C-E001_embeddings_and_local_laws/result.json).
- [The proof](../../proofs/KNOT-SPACE-20261020-001B/KNOT-SPACE-20261020-001B-P001_recognized_space/proof.md).

## What was found

- **A law carries a graph exactly when its knot matroid is graphic.** Its
  allowed states then determine the graph.
  - A gauge law over any group, commutative or not, has the cycles of its
    graph as knots and ties. A Tseitin law has the bonds. The two are dual.
  - In a 3-connected graph, the vertex stars are exactly the cocircuits whose
    deletion leaves the matroid connected. So the allowed states return the
    graph, under any presentation.
  - Below 3-connectivity, the graph is determined only up to Whitney twists. A
    twist writes a different graph with identical allowed states.
- **A sphere when the graph is planar.** The dual reading returns the faces.
  - Vertices, edges and faces then form the 2-sphere.
  - Euler's formula is the dimension count of the two codes.
- **Recognized, not created.**
  - The reading uses only the allowed states.
  - A law carries a graph exactly when it can be rewritten so that every
    variable joins exactly two sites: either two witnesses, as in a gauge law,
    or two constraints, as in a Tseitin law.
  - Whether it can is a property of the matroid, decided by Tutte's excluded
    minors. The way the law was written does not decide it:
    - A local law of 8 random constraints on 16 variables, written on no
      graph, carries a sphere with 9 vertices, 16 edges and 9 faces. Only 5
      of its constraints are faces.
    - Most laws carry none. Almost every balanced random code is neither
      graphic nor cographic. Among 240 random local laws, 13 had 3-connected
      knot matroids, and 1 of those carried a graph.
- **In the program's terms.** This is a reading of Theorem 5, not a new
  theorem.
  - The read vertices are a law's minimal moves between allowed states, kept
    when deleting one leaves the matroid connected ("non-separating").
  - The read faces are its knots and ties, kept on the same condition.
  - A law carries a graph when every variable lies in exactly two such moves.
    It carries a sphere when, in addition, every variable lies in exactly two
    such knots.
- **Ends.** On infinite graphs, the Tseitin law's knot matroid depends on the
  reading. This is cited, not checked.
  - Over all solutions, its circuits are the minimal finite cuts with a finite
    side. A finite bond between two ends is open.
  - Within one class of finitely different solutions, its circuits are the
    finite bonds. By Bruhn and Diestel, the dual matroid then has the circles
    through the ends as circuits.

  The epic's objective named only the second reading.
- **The census predictions.**
  - Census A:
    - S1, S2 and S4 held.
    - S3 failed through a labelling error: six planar random cubic graphs were
      labelled non-planar.
    - S5 was vacuous.
  - Continuation C:
    - T1 held: the dual reading succeeds exactly on planar graphs, across 40
      graphs.
    - T2 was refuted with 1 graph-carrying law among 13. That is a
      small-sample event, since a 5 percent rate gives at least one hit with
      probability about 0.49. It therefore does not meet the stop rule's
      condition of "well above chance".

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Gauge laws over any group have the cycles as circuits | The forest and telescoping argument | Classical, elementary |
| Exact recovery of 3-connected graphs; twists are invisible | Whitney (1933); the cocircuit form of Tutte (1963) | Classical |
| Faces and the sphere | Whitney's unique embedding and dual | Classical |
| Graph present exactly when the matroid is graphic; Tutte's minors | Tutte (1958, 1959); unique binary representation | Classical |
| Space read from allowed states; the two-site rewriting; moves and knots | The knot-matroid perspective | The reading is new to the program; the mathematics is immediate |
| A randomly written local law carrying a sphere | Continuation C | Observation |
| Two readings at infinity | `HOLES-AT-INFINITY-20261020-001B-P001`; Bruhn and Diestel | Cited; the split into readings is the program's |

**Did the perspective do real work?** It chose the question. It also produced
two readings: moves and knots as vertices and faces, and the two readings at
infinity. Every theorem is classical, and the folklore risk is high: all of it
is standard matroid theory.

**Ratio since the last checkpoint.**
- 3 artifacts are substantive: the census, the continuation and the proof.
- 2 are administrative: this note and the ledger.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — space from knot matroids | **Successful** | The question is answered, by classical mathematics. A law's allowed states carry a graph exactly when its knot matroid is graphic, and a sphere when it is also cographic. The graph is recovered exactly at 3-connectivity and up to twists below. Unresolved: only laws that have a knot matroid are covered. |
| Local direction — reading space from one law's knot matroid | Practically exhausted | The answer is Whitney's and Tutte's. One gauge or Tseitin law cannot see a surface of higher genus, because a 3-connected graph can have many embeddings and its matroid does not choose one. Theorems 3–5 and the moves-and-knots reading are retained. |
| Broader exploration — the source-aware foundation | Known alternatives | Three are known: (1) the diagonal lemma (`MALTSEV-CONVERSE-20261020-001`), which decides which laws have a knot matroid at all; (2) native moves in frozen worlds, which is deferred; (3) surfaces of higher genus, which need two laws on shared variables, a vertex law and a face law, whose mismatch is first cohomology (classical). |
| Long-term goal — intrinsic structure from logic | Obstruction learned | Space in this sense is recognized, not created. It is present only when every variable joins exactly two sites, up to presentation, and generic laws carry none. The missing bridge is a native mechanism by which two-site structure would arise rather than be written. |
| Next recommendation — the diagonal lemma, as a fresh epic after `MALTSEV-CONVERSE-20261020-001` | **Next step:** Full pivot. Leave the matroid reading of single laws and take up the diagonal lemma. It decides which laws have a knot matroid to read, so it is the precondition for any space reading beyond group cosets. | It is the one concrete open statement the two epics leave. The alternative is surfaces of higher genus from a vertex law and a face law on shared variables, rated 1/3 because it is very likely classical. Reopen space readings if a native mechanism is found that makes two-site structure generic. |
| Interest — the diagonal lemma | **2/3 — Promising** | Unchanged from the converse epic. Every one of the 146 knots tested satisfies it, and the statement is concrete. The risk is that larger domains need more than one derivation. |
| Execution — the diagonal lemma | Deferred | Not started, because "Do both" covered these two epics. Stop if a counterexample appears on 5 values. The next step is the owner's decision. |
