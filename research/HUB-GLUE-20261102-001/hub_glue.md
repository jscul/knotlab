# What selection leaves, and how pieces glue

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a three-regular contradiction; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `HUB-GLUE-20261102-001` (program topology), 2026-11-02.

## The question

- **The approval.** The owner said "Yes, continue" to TOP-LAYER-20261102-001's recommendation.
- **The question it approved.** When a contradiction loses a line, the line's three points become a hub. The knot's contradictions are glued
  along exactly such lines. Does gluing selected spaces along these leftover hubs build the knot's contradictions natively, and does the
  emergence each piece keeps survive across the glue?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The leftover is a hub.** In every contradiction, removing a line ties its three points (the two all-equal patterns). So selection leaves exactly the point side of a 3-edge cut. | proof; 56 removals in the census spaces | A |
| 2 | **Gluing.** Splicing a contradiction at a line into another at a point gives a contradiction for exactly one switching class of the new signs. Every simple 3-edge cut is such a splice. With THREEFOLD-GRAMMAR, every contradiction is assembled this way from Fano pieces and planar glue (4-sums for non-planar glue). | proof; 1216 splices, 10 simple cuts | A |
| 3 | **A held hub composes as a 2-sum.** After removing a line off the point side, the hub stays held (one bit). The crossing knots are then exactly the 2-sums of one circuit through the hub on each side, ties included. The reason is the knot's symmetry under complementing every value, and an OR control fails without it. | proof; 200 removals, 2300 crossing circuits, exact | B |
| 4 | **An opened hub.** After removing a line on the point side, the interface is what the closed piece allows on its closing line. It has one of three types: one pair (re-tied; the 2-sum holds), two pairs (one port released), or three (the hub becomes a knot on its three points). | proof; 1120 removals (16, 716, 388) | C |
| 5 | **Opened hubs create emergence.** With two or three pairs, composition fails. In the 13-point Fano splice, 72 crossing knots of opened hubs come from no chain of eliminations, while all 384 through held hubs do. | computation | C |

## Answer

- **Yes, gluing along leftover hubs builds the knot's contradictions.** This is the splice grammar the earlier epics found, now read as
  selection's own interface.
- **Yes, emergence survives across the glue,** in two ways depending on where selection falls.
  - **Off the hub's side.** The hub holds and the pieces' knots compose across it exactly like cycles, as a 2-sum.
  - **On the hub's side.** The hub opens (it releases a point or becomes a knot), and new crossing emergence appears that no
    composition explains.
- **So composition through hubs does come from selection itself.** It is cycle-like exactly at held hubs, and it is not composition
  at opened ones.

## Reading

- **Where the two earlier findings meet.**
  - **The exclusion.** SELECT-COUNT showed that selection and cycle-like composition exclude each other as properties of a whole
    two-valued law.
  - **The meeting point.** Inside the knot's own selected spaces they meet: at a held hub, circuit elimination holds exactly.
- **The reason is the knot's own symmetry.** Complementing every value maps solutions to solutions, so the two halves of every
  projection across a one-bit hub have equal size.
- **Hubs stay hubs.** A tied triple is equality fan-out (a hub in the program's sense), not a contact.
  - **The new part.** This hub is not declared: selection makes it.
  - **What composes through it.** Emergence (knots), never a native path or a distance. Doctrine is unchanged.
- **Selection decides composition.** One removal both selects a space and decides, cut by cut, whether the glue composes (held) or
  creates (opened). In a space with many pieces, the cuts that point at the removed line are opened and all the others held.

## Literature

- **Ours.**
  - THREEFOLD-SPACES (dictionary, block lemma, splices).
  - THREEFOLD-GRAMMAR (Fano pieces, planar glue).
  - NATIVE-PATHS A (the 3-edge-cut theorem).
  - SELECT-COUNT A.
  - TOP-LAYER.
  - MUTUAL-SELECTION C's census.
- **Classical.**
  - Tight cuts of Pfaffian bipartite graphs (Little; Vazirani–Yannakakis; Robertson–Seymour–Thomas).
  - Sign-nonsingularity.
  - The 2-sum of matroids and circuit elimination.
- **New here.**
  - The selection reading of the interface.
  - The relational 2-sum through a complement-symmetric hub.
  - The classification of opened hubs and their non-compositional emergence.

  These are elementary, with moderate folklore risk.

## Pending the owner

Still open from earlier epics:
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — do selection's hubs glue the knot's contradictions and keep emergence across? | **Status:** Successful | **Yes on both counts.** The splice grammar is selection's interface, and emergence crosses the glue, as a 2-sum at held hubs. **Open hubs create** crossing knots that are not compositions. **Open questions:** where a two-pair interface releases its port when the removed line holds fewer than two ports, and what the new knots are. |
| Local direction — a single cut | Practically exhausted | Held and opened hubs are characterized. What is left is classifying the opened hubs' new knots. |
| Broader exploration — how emergence is organized in a whole contradiction | Open, with a lead | **Not yet tested.** A space with several pieces has a tree of cuts. One removal opens the cuts that point at it and holds all the others. |
| Long-term goal — composed structure from native emergence | Capability gained | **What is gained.** A native composition law for the knot's emergence: 2-sums at the hubs selection leaves. **The limit.** The hubs are equality fan-out, so this composes emergence, not contacts: no native path or distance is claimed. |
| Next recommendation — emergence along the splice tree | **Next step:** Continue. **The decomposition to test.** After any removal in a space of several pieces, the kept knots are iterated 2-sums along the held cuts, with new emergence only at the opened cuts on the way to the removed line. **First test.** Chains and trees of three and four pieces (Fano pieces and planar glue, up to 25 points). Predict by the 2-sum and verify on the joins. | **If yes.** The whole space's emergence after selection is a tree of compositions with a computable shape, the first global description of what the knot keeps. **If no.** Cuts interact, and the held-hub theorem is only local. **Alternatives.** Classify the opened hubs' new knots (1/3). Prove the released-port rule (1/3). Count kept knots along the tree with counted length (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** Both local theorems are exact. The tree structure is the natural global test, and the prediction can be computed. **Main uncertainty.** Opened cuts along the path may interact, and the 2^25 state spaces need structured joins rather than brute force. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** Chains and trees of up to four pieces. **Stop when** the tree decomposition is proved or refuted on these. |
