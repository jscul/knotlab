# Where the loop shields the twist

Epic `LOOP-SHIELD-20261023-001`, closed 2026-10-23.

## The question

**What the previous epic left.** It proved the odd-loop identity on every torus:
- the two twists that make a class c odd give the same probability that the only contradiction is a lone loop along c;
- the proof slides the second twist's seam onto the loop's own boundary (the "wall"), and no directed cycle changes.

**What the mechanism predicts.** A wall next to the loop can only carry the twist dual to the loop: the twist that counts crossings with c.
- **On a torus** that is the only other twist odd on c, so every pair is covered.
- **On a surface of genus 2,** eight twists are odd on c. Only the dual pairs should agree.
- **In three dimensions** a loop cannot separate space, so no twist should be shielded.

**Approval.** The owner approved the test with "Yes, let's continue."

**The language of the thesis.** The twisted double cover is the implication digraph of a two-literal formula (`NAE-INVARIANT-20261022-001A-P001`, after Aspvall, Plass and Tarjan). The twist flips clause polarities across a seam, and an odd loop is a contradiction cycle x ⇝ ¬x ⇝ x that winds around the surface.

**The evidence:**
- [Genus-2 surfaces](../../experiments/LOOP-SHIELD-20261023-001A/LOOP-SHIELD-20261023-001A-E001_genus_two/contract.json) (A, exhaustive; [result](../../artifacts/LOOP-SHIELD-20261023-001A/LOOP-SHIELD-20261023-001A-E001_genus_two/result.json));
- [Thin and cubic 3-tori](../../experiments/LOOP-SHIELD-20261023-001B/LOOP-SHIELD-20261023-001B-E001_three_tori/contract.json) (B, Monte Carlo; [result](../../artifacts/LOOP-SHIELD-20261023-001B/LOOP-SHIELD-20261023-001B-E001_three_tori/result.json));
- [The wall on closed surfaces, and which twists a seam can carry](../../proofs/LOOP-SHIELD-20261023-001C/LOOP-SHIELD-20261023-001C-P001_surface_wall/proof.md) (C, proof);
- **Scoping (scratch, not evidence):** the same counter on smaller surfaces and 3-tori, and a multi-loop count on L(2, 2, 2, 2).

## Outcome in one paragraph

**Proved (C).**
- **The theorem.** On every closed orientable surface, a lone odd loop along c is blind to exactly one change of twist: adding the twist dual to c. The wall involution pairs the two events and keeps every directed cycle.
- **Which twists a seam can carry.** By Lefschetz duality, a seam next to a set of vertices carries exactly the duals of the classes of curves in the set's open star, minus the set's own graph. Next to a lone loop (with no square touching it at two opposite corners) that leaves only 0 and the dual twist.
- **In three dimensions** the same duality involves closed surfaces, so a loop confined to a tube carries no seam at all.

**Exact on genus 2 (A).**
- **The dual pairs agree.** On eight genus-2 square-tiled surfaces (16 to 32 edges, every orientation counted), every one of 15 classes with lone odd loops has exactly equal counts for each dual pair.
- **Nothing else agrees.** In every class the four pair values are not all equal: the other twists odd on c are not shielded.

**Three dimensions (B).** No twist is shielded.
- **On thin 3-tori,** every comparison between twists odd on a class that no symmetry relates differs by more than 5 standard errors (28 of 28).
- **On the cubic 3 × 3 × 3 torus** the same holds (15 of 15), where lone loops are rare but resolvable at 1.5·10⁹ samples.

## Genus 2 (A): only the dual twist is shielded

| Surface (edges) | Class | The four dual-pair values |
| --- | --- | --- |
| L(2,2,2,2) (24) | h2 | 3264, 3168, 4544, 4416 |
| L(2,2,2,2) (24) | v2 | 3264, 4544, 3168, 4416 |
| L(2,1,2,3) (24) | h2 | 0, 12864, 0, 22272 |
| L(2,1,3,2) (26) | (−1, 1, 0, 0) | 28512, 36288, 28824, 36672 |
| L(2,1,3,2) (26) | h1 | 5148, 0, 7696, 0 |
| L(3,1,2,2) (28) | v1 | 0, 8320, 0, 9600 |
| L(2,2,3,1) (28) | h1 | 0, 0, 8320, 9600 |
| L(2,3,2,2) (28) | h2 | 34784, 34368, 72064, 71296 |
| L(2,3,2,2) (28) | v2 | 402816, 726080, 439680, 844864 |
| L(3,2,2,2) (32) | h2 | 32136, 31824, 44720, 44304 |
| L(3,2,2,2) (32) | v1 − v2 | 263952, 266832, 357264, 361008 |
| L(3,2,2,2) (32) | v2 | 3139776, 3496128, 2957952, 3295744 |
| L(3,2,2,2) (32) | v1 | 63360, 94720, 122880, 178560 |
| L(2,2,2,4) (32) | h2 | 14828576, 16731552, 28669504, 34589248 |
| L(2,2,2,4) (32) | v2 | 288512, 988800, 286944, 984704 |

**How to read it.**
- Each value is the common count of a dual pair {a, a + c}, the two members being exactly equal.
- The rows of a class run over the four dual pairs among the eight twists odd on it.
- Classes are in core-curve coordinates (h1, h2, v1, v2).
- Several pairs are close but never equal, for example 288512 and 286944 on L(2,2,2,4).

**How the run was checked.**
- The checker:
  - built the smallest surface with its own code and matched all 16 twists;
  - reproduced the 3 × 3 torus row;
  - confirmed the diagonal reflection of the symmetric surface exactly;
  - replayed a 28-edge surface by other code.
- The halved enumeration matched the full one.
- The run took 3152 s against a 5400 s budget.

**Scoping beyond the contract.** With two disjoint loops on L(2,2,2,2) (one odd, along h2 or v2, and one even), the odd loop still shields its own dual twist exactly: 2560 = 2560 and 2496 = 2496 on both classes, while the unshielded twists differ (2560 against 2496). No orientation of that surface has two odd loops of different classes at once.

## Three dimensions (B)

**Cubic 3-tori have few lone loops.**
- Fair orientations of the cubic lattice almost always have cycles winding in every direction.
- Lone odd loops do not occur at all on 2 × 2 × 2 (every orientation counted).
- At 3 × 3 × 3 there are about 3.5 per million per class (secondary row, below).

**Thin 3-tori, two layers thick, carry lone loops along the short side.** Loops along the vertical class occur at about 10⁻⁴ to 2·10⁻⁵. The four twists odd on that class give:

| Torus (samples) | 001 | 011 | 101 | 111 | Smallest unrelated \|z\| |
| --- | --- | --- | --- | --- | --- |
| 3 × 2 × 2 (10⁹) | 41493 | 77432 | 49165 | 91283 | 28.0 |
| 3 × 3 × 2 (5·10⁸) | 49630 | 61276 | 61038 | 74996 | 37.6 |
| 4 × 3 × 2 (5·10⁸) | 19887 | 27547 | 21256 | 29351 | 7.6 |
| 4 × 4 × 2 (5·10⁸) | 8563 | 9640 | 9566 | 10539 | 6.9 |

**The comparisons.**
- **Every unrelated pair differs.** All 28 comparisons between twists not related by a symmetry of the box differ by more than 5 standard errors (smallest 6.9). These cover the vertical class on all four tori and also the second short class on 3 × 2 × 2. No twist is shielded.
- **The controls hold.**
  - The pairs that a symmetry forces equal agree: 011 and 101 on the square tori, z = 0.69 and 0.54.
  - Every comparison between classes exchanged by a symmetry agrees within 4 standard errors.

**Partial shielding is visible.**
- **The pattern.** The smallest differences are between twists that differ across the box's smaller vertical slice: the x-twist on 4 × 3 × 2 (7.6 and 8.4 standard errors, against 29 to 43 for the others) and on 3 × 2 × 2.
- **Why.** On a thin torus the loop's open star can occasionally contain a whole small slice. By Lemma F, a seam can then carry that slice's dual twist for that orientation.
- **Why the identity still fails.** No choice of seam is canonical across the event.

**The cubic 3 × 3 × 3 torus (secondary, 1.5·10⁹ samples).**

| Class | Twists odd on it (counts) | Unrelated pairs |
| --- | --- | --- |
| (0, 0, 1) | 001: 886, 011: 1207, 101: 1280, 111: 1920 | all differ, \|z\| 7.4 to 19.6 |
| (0, 1, 0) | 010: 847, 011: 1218, 110: 1242, 111: 1853 | all differ, \|z\| 8.5 to 19.4 |
| (1, 0, 0) | 100: 883, 101: 1216, 110: 1289, 111: 1860 | all differ, \|z\| 7.7 to 18.7 |

- **The symmetric pairs agree:** 011 and 101 for the class (0, 0, 1), within 1.5 standard errors.
- **What this shows.** The original 3-torus prediction holds directly, not only on thin tori: a loop that cannot separate shields nothing.

**How the run was checked.**
- The independent checker reproduced the 3 × 3 torus row and the 3 × 2 × 2 slice by its own classification.
- The run took 3475 s against a 5400 s budget.

## The proof (C) in plain terms

**Why the wall works on any surface.**
- The odd loop's neighbourhood is a planar strip whose edge includes a curve of class ±c. Cutting the surface along that curve builds the cover in which the loop separates the two ends.
- The torus argument then goes through unchanged.
- The wall's class is the twist that counts crossings with c.

**Why nothing else can be shielded.**
- A seam made of edges that touch the loop is, by Lefschetz duality, dual to a curve that runs in the loop's open star but avoids the loop's own graph.
- Near a lone loop such curves run alongside the loop, so they have class 0 or ±c.

**A correction made during the proof.**
- **The first version was wrong.** It used the loop's graph instead of its open star.
- **How it was caught.** The check found it false on 117 of 300 random vertex sets.
- **The cause.** A square with two opposite corners in the set joins them through its interior.
- **The fix.** The corrected lemma states the condition explicitly. On all 425 line configurations examined, the seams next to the loop carried only 0 and the dual twist.

**In three dimensions.** The dual objects are closed surfaces. A loop's open star is a thickened curve, a solid torus, which contains no essential closed surface. So no seam next to a loop carries a twist, and no wall exists.

## Interpretation (not theorem)

- **A contradiction shields exactly what is dual to it.**
  - In a fair two-literal world on a surface, a lone contradiction cycle along c makes one background choice invisible: the polarity twist dual to c.
  - Every other twist that also makes c odd remains visible in the statistics.
- **Codimension one is what matters.** On a surface, a loop has codimension one and can act as a wall. In three dimensions a loop has codimension two, and its open star carries no surface.
- **The relational reading.** What an emergent structure screens is fixed by duality with its own shape, not by the geometry of the lattice.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| The odd-loop identity is a fact about tori | `ODD-LOOP-20261023-001` | **Sharper.** It is a fact about duality: on every closed orientable surface the dual pair agrees exactly. |
| All twists that make c odd are alike for a loop along c | The natural extension of the torus statement | **False on genus 2.** Only the dual twist is shielded; the other pair values differ on every tested class. |
| A seam next to the loop can carry only classes the loop's graph carries | The first draft of C's Lemma E | **False**, caught by its own check: the open star (diagonal squares) is what counts. |
| The identity should extend to 3-tori | The epic's motivating question | **No.** No wall exists around a loop in three dimensions (proved), and the twists odd on a class differ on thin and cubic 3-tori (B). |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| The wall theorem on closed orientable surfaces | Generalizing `ODD-LOOP-20261023-001B-P001` | New to the program. The ingredients are classical (cyclic covers, separating curves); moderate folklore risk for the technique, low for the statement. |
| Seams carry the duals of the open star's classes (surfaces and 3-manifolds) | Lefschetz duality applied to seams | Standard topology; the application to shielding is new to the program. |
| Only the dual twist is shielded on genus 2 | A, exhaustive counts on eight surfaces | A recorded computation |
| The failure of the graph-only seam lemma | C's own check | A recorded correction |
| No shielding on thin and cubic 3-tori; partial shielding where a loop can fill a slice | B, Monte Carlo | A recorded computation |

**Did the perspective do real work?** Yes.
- **What the topology supplied.** The prediction came from the mechanism, not from data: the wall's dual class names exactly which twist is shielded, and duality says no other can be. The genus-2 counts were a test of that prediction, and it held on every class.
- **What was standard.** The lattice and the gauge bookkeeping.

## Recommendation

**Where the line of work stands.** The twisted model's exact relations have reached a natural end:
- the cone and its duality;
- the harmonic structure under shear;
- the odd-loop identity;
- now the shielding principle with its mechanism and its topological reach.

What remains in this branch are refinements. For example, two disjoint odd loops of different classes on genus ≥ 2 should shield both duals, which follows from the same lemmas. No orientation of the smallest surface has such a pair.

**The thesis question it raises.** All of this lives on the two-literal side: the double cover is a two-literal implication digraph, and its contradictions are cycles. The open question is what plays the role of the shielding loop for a contradiction that is not an implication cycle.

| Option | What it would do | Interest |
| --- | --- | --- |
| **1. Full pivot: the three-literal side** (recommended) | A bounded direction search for a fair three-literal lattice world where twisted sectors make sense and contradictions are not implication cycles. Then one exhaustive small-torus test of whether any exact twist identity survives beyond symmetries. Read first: the census and base-three results. Stop if no such world gives events comparable to lone loops. | 1/3 |
| 2. The complete map of exact twist relations | Classify every cyclic-structure event on genus-2 surfaces by the topology of its odd components, and test exhaustively whether lattice symmetry, planar duality and walls explain every exact equality between twists | 1/3 |
| 3. A self-contained note on shielding | The surface theorem, the seam duality and the exact counts, with replays, for readers in percolation and random two-literal formulas; sharing is the owner's call | 1/3 |

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — where the loop shields the twist | **Successful** | Both predictions of the mechanism hold. On genus 2, exactly the dual pairs agree and the other twists differ on all 15 classes (exact counts). In three dimensions no wall exists (proved), and no twist is shielded on thin or cubic 3-tori (Monte Carlo: 43 of 43 unrelated pairs differ by more than 5 standard errors). The surface theorem and the seam duality are proved. |
| Local direction — exact relations of the twisted model | Practically complete; retire | Duality, harmonics, the odd-loop identity and shielding are proved, with their scope mapped. What remains are refinements of the same lemmas. |
| Broader exploration — critical emergence of single fair contacts | Practically complete, with a structural principle | A fair two-literal contradiction on a surface screens exactly the twist dual to it; codimension one is needed. Open: the lower bound and the scaling-limit relations. |
| Long-term goal — emergence from logic (the two-literal/three-literal boundary) | Capability gained | An exact relational principle for two-literal contradictions. The missing bridge is the three-literal side, where contradictions are not cycles. |
| Next recommendation — the three-literal side | **Next step:** Full pivot. A bounded direction search for a three-literal counterpart of shielding, then one exhaustive small-torus test. Retained: every result of this branch. Reopen it if a three-literal world shows an exact twist identity, or if option 2 finds an equality that walls do not explain. | The question tests whether a "harmony" of this kind marks the two-literal side of the boundary. |
| Interest — that next step | **1/3 — Exploratory poking** | The lead is plausible, but no candidate three-literal world with comparable events is identified yet. With fair independent polarities a twist is invisible by symmetry, so the world needs correlated polarities, as orientations give in the two-literal case. |
| Execution — that next step | Deferred to the owner | Bound: one epic, mostly reading and small exhaustive counts. Stop if no world with lone-contradiction events is found. |
