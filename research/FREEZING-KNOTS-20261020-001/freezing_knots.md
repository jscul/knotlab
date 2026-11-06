# Native knots at the freezing threshold of random colourings

Epic `FREEZING-KNOTS-20261020-001`, closed 2026-10-20.

## The question

Under the source-aware reading, adopted on 2026-10-20 and reopenable, a knot is
native at a solution when each of its variables can be flipped by a change of
finitely many variables. A star knot on q neighbours of a vertex is the
relation "not all q colours used". The owner approved the question: do star
knots stop being native at the freezing threshold of random colourings?

The evidence is:
- [the experiment](../../experiments/FREEZING-KNOTS-20261020-001A/FREEZING-KNOTS-20261020-001A-E001_freezing_census/contract.json),
  with [result](../../artifacts/FREEZING-KNOTS-20261020-001A/FREEZING-KNOTS-20261020-001A-E001_freezing_census/result.json);
- [the proof](../../proofs/FREEZING-KNOTS-20261020-001B/FREEZING-KNOTS-20261020-001B-P001_tree_freezing/proof.md).

## What was found

- **Yes, exactly at the threshold, and abruptly.**
  - Take the d-regular tree with the broadcast colouring, which is the local
    limit of planted colourings of random d-regular graphs.
  - The star knot exists at every degree.
  - It is native with probability 1 below the freezing threshold: d = 6, 10
    and 15 for q = 3, 4 and 5, certified exactly.
  - At the threshold the probability that a branch freezes jumps from 0 to
    about 0.9. Nativity drops from 1 to below 0.0011, 0.00046 and 0.00003.
- **Finite graphs follow the tree.** At planted colourings of random regular
  graphs, the fractions of vertices frozen at radius L, and of star knots
  native at radius L, match the tree's exact values within about 0.01. This
  holds at every measured radius (q = 3, d = 3..7, L ≤ 3; q = 4, d = 9..11,
  L = 1). Every finite measurement was independently re-checked.
- **The two readings see different things.**
  - On the tree, the source-blind knot is present at every degree, while
    nativity has a sharp threshold.
  - In small planted graphs (n ≤ 36), the source-blind relation over all
    colourings is the knot at degrees 3 and 4. It collapses from degree 5,
    because those graphs have only 6 to 102 colourings.
  - So in finite systems, the source-blind verdict tracks the global count of
    solutions. The source-aware verdict is local and tracks freezing.
- **Native-knot density restates freezing.** Star nativity is a function of
  branch freezing, approximately vertex nativity to the power q, and its
  threshold is the freezing threshold. This was the stop condition set
  beforehand.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Frozen-branch recursion and the thresholds | cavity method (hard fields, naive reconstruction) | Classical; thresholds not compared with a published table |
| The source-blind star knot exists at every degree | knot test on the star | Elementary; the reading is the program's |
| Nativity formula and its jump | source-aware reading applied to freezing | Not found stated; a short consequence of the recursion |
| Finite planted graphs match the tree | calibration of local convergence | Expected (exploratory evidence) |
| The source-blind knot collapses with the count of solutions in small graphs | experiment | An observation at small n; not evidence of an asymptotic effect |

**Ratio since the last checkpoint:**
- 2 artifacts changed a conclusion: the experiment and the proof.
- 3 are administrative: this note, the closure ledger, and the owner-requested
  adoption of the source-aware reading.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — native star knots at the freezing threshold | **Successful** | Answered exactly on the tree and calibrated on finite planted graphs. As a threshold, the answer restates freezing. |
| Local direction — native knots in random constraint problems | Retire | Stop condition met. Larger q or other random problems would restate the classical freezing picture. Results kept. |
| Broader exploration — the source-aware foundation | Three results in place | Ends as a second source of openness (`HOLES-AT-INFINITY-20261020-001`); emergence relative to law and world (`FROZEN-WORLDS-20261020-001`); freezing (here). Not yet assessed: whether native moves build space-like structure (question 9), and how native knots compose (question 3). |
| Long-term goal — intrinsic structure from logic | Capability gained | Under the adopted reading, emergence lives exactly where a law's solutions admit finite moves. In random colourings it ends at the freezing threshold. |
| Next recommendation — space from native moves | **Next step:** Research directions. Run a bounded scan of two candidates and pick by the cheapest discriminator. (a) Do a law's minimal finite moves, and the relations among them, form a low-dimensional complex, and which laws give one (question 9)? First test: compute these complexes for Tseitin on Z² and Z³, the gauge law, a random regular graph and Ledrappier, and ask whether their dimension belongs to the law. (b) How do native knots compose into networks (question 3)? | (a) would make native loops a candidate mechanism for space from a law. |
| Interest — that scan | **2/3 — Promising** | It speaks directly to the program's aim. The main risk is that, for linear laws, it reduces to classical cellular resolutions (Koszul complexes). |
| Execution — that scan | Deferred to the owner | Not started. Stop if candidate (a) only reproduces the cell structure of the graph the law was written on. |
