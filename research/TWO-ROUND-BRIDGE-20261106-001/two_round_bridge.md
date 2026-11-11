# The two-round rule as a proof-complexity bridge

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a three-fold space is a three-regular contradiction; a knot space is a three-regular contradiction; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `TWO-ROUND-BRIDGE-20261106-001` (program complexity), 2026-11-06.

## The question

- **The request.** A new root epic: decide what `PENDANT-LINE-20261106-001A`'s two-round rule means in standard proof-complexity
  terms.
  1. Translate the elimination closure into a standard system and say what "depth two through a cut" bounds.
  2. Test whether it composes over the tight-cut (handle) tree into a global upper bound for three-regular contradictions.
  3. Compare with the late-October Tseitin results and the closest literature, with provenance and folklore risk.
- **Why it was open.** The rule was rated 2/3 as a bridge in several next-step tables and never pursued.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The knot closure is width-3 resolution.** Two knots sharing two variables resolve at width 3 exactly when their forbidden patterns relate the shared pair differently. At a gluing line, the closure's crossing knots are exactly the width-3 resolution consequences of the one-sided implicates on at most three variables. Each is derived in depth one or two, resolving only on the line's three variables, along a linear chain from one far knot. | proved (lemma by hand; local data exhaustive: 348,376,032 configurations, 52,308 crossing knots) | A |
| 2 | **Creation is width 4.** Every new crossing knot is still implied by those implicates, and is derived from them in width exactly 4 and depth 2. | proved (exhaustive local data) | A |
| 3 | The rule's literal pairs step is not a resolution step: in 1,645,912 of 1,685,232 local instances it is sign-incompatible at every line point. A near-knot route of depth two always works instead. | proved (exhaustive) | A |
| 4 | **Composition over the handle tree costs O(1) per Fano piece.** Davis–Putnam derives each piece's port relation in width at most 5 and at most 80 clauses. A three-regular contradiction costs its core plus O(pieces). | proved | B |
| 5 | **Three-regular contradictions are an Euler count.** On a plane Kasteleyn core, a satisfied line has exactly one agreeing corner and every face at least one, and faces exceed lines by two. Assignments modulo complement are exactly the parity solutions on the line–face graph. | proved (verified on six families) | B |
| 6 | **Sherali–Adams sees the count.** Level max(3, d) refutes every plane signed space whose faces carry at most d points: level 3 on the octahedral family. Constant level refutes their decorations into three-regular contradictions. | proved | B |
| 7 | Resolution: every three-regular contradiction has refutations of size n^{O(1)}·2^{O(√n)}, by treewidth. On the octahedral family (one brace for every k), solver costs grow by factors of 7 to 50 per step in k. A lower bound of 2^{Ω(√n)} is conjectured. | proved upper bound; measured; conjecture | B |

## Answer

- **(1) The standard system is resolution, at width 3.**
  - "Depth two through a cut" bounds the number of resolution layers across the interface, relative to the one-sided implicates: one
    for knots through a gluing-line point, two otherwise. It also bounds the width: 3 for the closure, exactly 4 for creation.
  - It bounds neither formula depth (everything is clauses, so Res(⊕) and bounded-depth Frege are not needed) nor the cost of the
    one-sided implicates.
  - The two-round rule is interpolation through a three-variable interface. The native closure is its width-3 part, and creation is
    the part that needs a fourth variable.
- **(2) It composes, but not into a global resolution bound.**
  - Cut-local derivations compose over the handle tree at constant cost per piece. Fano pieces are free.
  - The glue carries the whole contradiction, and the glue is a counting statement: the sphere's Euler characteristic. Width-3 or
    width-4 local reasoning cannot express it.
  - The octahedral family has a single brace for every k, and its resolution cost grows exponentially in √n as far as measured.
  - The global upper bound is a counting one (Sherali–Adams of level 3). Resolution gets only the treewidth bound.
- **(3) Three-regular contradictions are the integer counterpart of Tseitin.**

## Comparison with the late-October Tseitin results

| | Tseitin formulas on a graph G | Plane contradictions and three-regular contradictions |
| --- | --- | --- |
| The contradiction | Handshake lemma mod 2: odd total charge | Euler's formula over Z: faces = lines + 2, an even difference, invisible mod 2 |
| Solutions | Parity solutions | Parity solutions on the line–face graph, with degree exactly 1 at every line |
| Res(⊕) / Gaussian elimination | Polynomial (folklore) | Open |
| Nullstellensatz / polynomial calculus degree (char ≠ 2) | Toggle width (= cutwidth + 1 at degree ≤ 3); ⌈cvw/2⌉ to ⌊cvw/2⌋ + 1 (`PC-DEGREE-20261020-001`) | Open |
| Sherali–Adams / sum-of-squares degree | cvw to 3cvw/2 + 1 / cvw to cvw + 4 (`SOS-SIZE-20261020-001`) | 3 on bounded plane cores (this epic) |
| Resolution size | 2^Θ(tw) on cellular graphs (`CELL-SIZE-20261020-001`; grids: Dantchev–Riis) | ≤ 2^{O(√n)}; 2^{Ω(√n)} conjectured |
| Kind of principle | Parity | Counting (a mutilated chessboard of the sphere) |

- **Complementary profiles.**
  - Tseitin is easy for linear algebra over F2 and hard for every LP or SDP hierarchy below its carving width.
  - The knot's contradictions are easy for the LP hierarchy at level 3, and their count is invisible to parity.
  - In both, resolution is expected to pay exponentially in the width of a planar structure.
- **Where the perspective did the work.**
  - The program supplied the objects and the invariant: the native closure, the handle tree, the skip model and the genus picture of
    the Fano pieces.
  - The proof techniques are standard: interpolation, Davis–Putnam, local distributions, treewidth.

## Literature and provenance

| Result | Closest known | Folklore risk |
| --- | --- | --- |
| Elimination lemma (1) | Resolution of two not-all-equal constraints sharing two variables | High: elementary |
| Closure = width-3 resolution; creation = width 4 (1, 2) | Craig interpolation; Davis–Putnam; Atserias–Dalmau (width = pebble game) | Low for the exact statement; the framing is classical |
| Composition over tight cuts (4) | Composition of refutations along small separators; treewidth dynamic programming | High: standard technique |
| Euler count (5) | `HANDLE-EMERGENCE-20261102-001C`'s skip model; Kasteleyn 1963; planar T-joins (Hadlock 1975) | Moderate: classical ingredients, new reading |
| Sherali–Adams level 3 (6) | Planar max-cut is solved by cycle inequalities (Barahona–Mahjoub 1986); planar not-all-equal 3-SAT is in P (Moret 1988) | High: essentially planar max-cut duality |
| 2^{O(√n)} and the conjecture (7) | Robertson–Seymour–Thomas 1999 structure; Lipton–Tarjan; mutilated chessboard (Dantchev–Riis 2001, Alekhnovich 2004); perfect matching vs Tseitin (Austrin–Risse 2022) | Upper bound: high. Conjecture: no statement for these formulas found |

- **Searches.** Bounded web searches found no proof-complexity treatment of non-2-colourable cubic hypergraphs, sign-nonsingular
  matrices or Pfaffian orientations.
- **Planar perfect matching.** Mutilated-chessboard lower bounds are grid-specific; no general planar theorem was found.

## Ratio

Since the epic opened:
- **Substantive.** Two proof families (A, B) changed conclusions.
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics; nothing new here:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the two-round rule as a proof-complexity bridge | **Status:** Successful | **(1) Translation.** Closure = width-3 resolution; creation = width 4, proved exhaustively. **(2) Composition.** Proved at O(1) per piece, but no global resolution bound beyond 2^{O(√n)}: the glue is an Euler count. Sherali–Adams level 3 refutes it; a resolution lower bound is conjectured, with solver evidence. **(3) Comparison.** Done. |
| Local direction — native creation as resolution at a cut | Practically complete | The dictionary is exact at widths 3 and 4. Nothing local remains. |
| Broader exploration — proof complexity of the knot's contradictions | Mapped in part | **Easy.** Sherali–Adams at level 3. **Upper bound.** Resolution 2^{O(√n)}. **Open.** Lower bounds in every system: resolution, Res(⊕), polynomial calculus, cutting planes, bounded-depth Frege. |
| Long-term goal — complexity and native emergence | Capability gained | **Gained.** Native creation is a standard measure: the step from width 3 to width 4 at a cut. The knot's contradictions are an integer counting principle complementary to Tseitin's parity. **Missing bridge.** Lower bounds. |
| Next recommendation — is the sphere's Euler count hard for resolution? | **Next step:** Continue. A fresh epic on the octahedral three-regular contradictions. First prove resolution width Ω(√n), from a mobility lemma for the violated line: a height-function statement for the dimer model on the line–face graph, or a finite check in the bulk. Then attempt size 2^{Ω(√n)}, adapting the mutilated-chessboard lower bounds (Dantchev–Riis, Alekhnovich) or the program's cell and tangle restrictions (`CELL-SIZE-20261020-001`). | **If yes.** A natural family decided in polynomial time (Kasteleyn), refuted by Sherali–Adams at level 3, yet exponential for resolution: the knot's own spaces as a counting barrier. **If no.** A short resolution proof of the sphere's count, which would be new for planar counting principles. **Alternative.** Polynomial calculus over F2 or Res(⊕) on these spaces, where the count is invisible to parity (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** Solver costs grow 7 to 50 times per step in k, and the violated line moved freely in 148 of 148 tests. **Main uncertainty.** Planar counting lower bounds are known only on square grids. The octahedral lattice is triangular, and separations of this kind already exist (pigeonhole, mutilated chessboard), so the payoff is mainly for the program. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Stop when** width Ω(√n) is proved or a frozen-boundary obstruction to mobility is found. Reassess before attempting size. |
