# Frozen worlds: native loops by law and by world

Epic `FROZEN-WORLDS-20261020-001`, closed 2026-10-20.

## The question

The open decision, in
[canonical_correction_request.md](../HOLES-AT-INFINITY-20261020-001/canonical_correction_request.md),
is whether open distinctions supplied by a system's ends count as native loops.
The owner asked which reading gives more interesting results.

This epic answers by working out the source-aware reading. A distinction is
native at a world (a solution) when some change of finitely many variables
flips it. The question is what that makes visible that the source-blind
reading cannot see.

The proofs are:
- [B: a linear law is frozen everywhere or nowhere](../../proofs/FROZEN-WORLDS-20261020-001B/FROZEN-WORLDS-20261020-001B-P001_linear_laws/proof.md)
- [C: colourings have frozen and flexible worlds](../../proofs/FROZEN-WORLDS-20261020-001C/FROZEN-WORLDS-20261020-001C-P001_frozen_and_flexible_worlds/proof.md)

## What was found

- **Linear laws are all or nothing** (B).
  - Whether a finite change can flip a parity does not depend on the world. So
    a linear law either has the same finite moves at every world or is frozen
    at every world.
  - Its K1–K3 knots are exactly its minimal fixed parities. They are native
    exactly when they lie inside the supports of finite moves.
  - On Z^d, a law has finite moves exactly when its matrix has a rank deficit,
    which happens exactly when its solution space has positive entropy.
  - On the square grid:
    - Tseitin's law and the gauge (plaquette) law have native knots.
    - Ledrappier's law, and Tseitin's and the gauge law imposed together, are
      frozen. They have knots, but no native one.
  - So two laws that each have native loops can combine into one that has
    none.
- **Colourings depend on the world** (C).
  - Proper 3-colourings of the grid and of the 3-regular tree have frozen
    worlds: every finite region is determined by the rest of the world, so all
    of its distinctions are supplied at infinity.
  - They also have flexible worlds, which form a dense open set.
  - Three neighbours of a vertex carry the knot "not all three colours
    distinct". It is native in flexible worlds and in no frozen world.
- **Native loops are necessary but not sufficient** (C). The hard-core law
  (independent sets) is flexible at every world but has no knot at all.

## Which reading gives more interesting results

| Law | Knots, source-blind | Native knots, source-aware |
| --- | --- | --- |
| Tseitin or gauge on the grid | yes | yes, at every world |
| Ledrappier on the grid | yes | none: frozen everywhere |
| Tseitin and gauge together | yes | none: frozen everywhere |
| 3-regular tree, Tseitin | yes | none: openness only from ends |
| 3-colourings of grid or tree | yes, at every world | only in flexible worlds |
| Hard-core law | none | none, although every world is flexible |

The source-blind reading gives the first column. Every law with constrained
but free relations has knots at every world. The source-aware reading
separates:
- laws with emergence from frozen laws, with a criterion: rank deficit, or
  positive entropy;
- worlds with emergence from frozen worlds of the same law.

All of these are new statements about emergence. They hold only under the
source-aware reading.

The two readings agree on every finite system. All earlier finite results
stand either way. The decision remains the owner's, and the request stays
open.

**Recommendation:** adopt the source-aware reading. If you prefer not to
commit yet, keep K1–K3 unchanged and require a source label on every knot
claim about infinite systems. That gives the same results.

## How this meets the owner's intuitions

This section is interpretation, kept separate from the proofs.

- **Base realities and worlds.** One law can have worlds with emergence and
  worlds without: frozen worlds, fully determined by their surroundings. That
  is branch-relative emergence inside one base.
  - It is not a global selector. Every world is a solution of the same law.
  - It is not evidence for co-reality either.
- **"Requirement versus choice."** A frozen world is all requirement. Every
  local value is forced by the rest. Native loops are where choice survives
  locally.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Linear nativity is world-independent | source-aware reading applied to linear laws | Elementary |
| Native loops ⟺ rank deficit ⟺ positive entropy on Z^d | homoclinic points of algebraic actions | Classical in substance (Schmidt; Lind–Schmidt–Ward) |
| Linear knots = minimal fixed parities | coding theory | Standard |
| Two flexible laws freeze together | computed, then proved (H¹ of the plane) | Elementary; not found stated in these terms |
| Frozen and flexible colouring worlds | classical colourings | Classical (Peled–Spinka; freezing in random colourings) |
| Star knot "not all distinct", world-relative nativity | knot reading of the above | Elementary; the reading is the program's |
| Hard-core: native everywhere, no knots | majority closure | Classical ingredients |

**Ratio since the last checkpoint:**
- 2 artifacts changed a conclusion: proofs B and C.
- 2 are administrative: this note and the closure ledger.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — native loops by law and by world | **Successful** | Linear laws are all or nothing, with an entropy criterion. Colourings are world-relative. The hard-core law shows native loops are not enough. Together these answer which reading gives more: the source-aware one. |
| Local direction — the source-aware reading on canonical laws | Practically settled | Linear laws are classified. The two canonical non-linear examples are done. |
| Broader exploration — emergence and freezing | One named lead | Frozen worlds lack native knots. In random colourings, typical solutions freeze above a known threshold, where local algorithms are proved or conjectured to fail (Achlioptas–Coja-Oghlan; Molloy). Not yet tested here. |
| Long-term goal — where emergence lives | Capability gained | Emergence, read as native knots, is now a property of the law (entropy) and of the world (not frozen). Before, it was a property of relations alone. |
| Next recommendation — native knots at the freezing threshold | **Next step:** Continue, as a fresh epic. On random regular graphs, with exhaustive or solver-based enumeration at small n, measure how many star knots are native, meaning their three vertices can be recoloured by bounded-size changes, in typical colourings. Compare that fraction with the known rigidity and freezing thresholds. | Would tie the foundation's notion of emergence to the computational phase transition. Bounded and experimental. |
| Interest — that lead | **2/3 — Promising** | The frozen-variable literature is rich and its thresholds are known. The question is whether native knots add anything beyond frozen variables, which is uncertain. |
| Execution — that action | Deferred to the owner | Not started. Stop if native-knot density merely restates frozen-variable density. |
