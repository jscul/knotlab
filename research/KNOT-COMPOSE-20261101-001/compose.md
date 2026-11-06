# Composition of the knot's spaces: decision at closure

Epic `KNOT-COMPOSE-20261101-001`, closed 2026-11-01. Program: topology.

## The request

Option (c) of the three recommendations the owner approved ("Can we do all 3?"): do the knot's selected spaces compose into native
networks?

## What was found

| # | Result | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Every 3-edge cut of a cubic incidence graph is balanced: a point side with three ports, a line side with three slots. | proved | A, Lemma 1 |
| 2 | Across every nontrivial 3-edge cut of a knot's space the line side is exactly the knot (not-all-equal) and the point side exactly a hub (equality). | proved (point lemma); checked on all 5 cuts of four spaces | A, Theorem 4 |
| 3 | Two sides that both accept knots fail together only as complementary parity cosets (an independent half of the cube is a colour class). | proved | A, Lemma 3 |
| 4 | Double cuts of knot's spaces accept twelve-class knots or no knot, and two twelve-class sides never fail together. | checked (468 double cuts, 200 joins) | A |
| 5 | Parity does fail hub-free (control). | checked | A |
| 6 | The transpose maps knot's spaces to knot's spaces and exchanges knot sides with hub sides. | proved | A |
| 7 | Against the native-network gate: the composition passes on substrate, native law, endpoint identity and persistence, and fails on the no-common-hub item. So it is a native network of knots with network hubs (in scope by the owner's decision). | documentation | B |

## Answer

- **Yes, natively, but always through hubs.** The parts of a knot's space meet as a knot against an equality fan-out.
- **Hub-free composition is parity's.** A failing composition that joins knot to knot is a parity composition. This echoes the earlier
  results in which only parity survives hub-free composition.

## Reading

- **Everything is relational.** Knots relate through shared points. A direct knot-to-knot relation with nothing between them exists only
  for parity, the law that hides one full bit.
- **Duality.** The transpose shows that knot and hub are the two sides of one incidence structure.

## Literature

- **From the earlier epics.** Tight cuts and the splice calculus (THREEFOLD-SPACES, on Lovász–Plummer and Robertson–Seymour–Thomas), and
  the point lemma and factorization (THREEFOLD-AMPLITUDE).
- **Elementary.** The complementarity lemma (independent halves of the cube).
- **New reading.** That the knot's spaces meet only through hubs was found in no source checked.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — composition of the knot's spaces | **Status:** Successful | Every small interface is classified: knot against hub across 3-edge cuts; knot against knot fails only for parity. |
| Local direction — composition | Continue later, with scope stated | Open: cuts of four or more edges with a hub side (trisum glue), and native paths and separation through network hubs. |
| Broader exploration — composed topology | Known alternatives | Paths through network hubs (2/3); the five weak four-place classes (1/3). |
| Long-term goal — emergence then composed topology | Obstruction learned | The knot's composition needs hubs, and hub-free composition is linear (parity). The missing bridge is native paths through admitted network hubs. |
| Next recommendation — option (a), the note | **Next step:** Continue, as approved: the note on native selection, gathering the coupling dichotomy, uniqueness, the parity correction, four places and composition. | It converts a completed arc into one reviewable piece. Completion check: a self-contained note with a replay of every cited number. |
| Interest — that recommendation | **2/3 — Promising** | The arc is complete and coherent. The main uncertainty is novelty against the Holant and hypergraph-colouring literature. |
| Execution — that action | Started (approved) | The note epic opens now. |
