# Why a Fano atom acts as one

Epic `ATOM-ONE-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner said "Yes continue." to FAR-READ's recommendation: prove that a Fano atom acts as one from outside.
- **The property.** FAR-READ A computed it on 1,065 atoms: every line of another Fano atom receives the same creation, far side by far
  side, whichever of the atom's lines is removed. FAR-READ B's reading rule rests on it.
- **The aim.** Find the mechanism, prove what holds in every knot space, and test what remains on fresh spaces.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Every Fano atom, with its closed sides, is the Fano plane.** A closed side acts as its lost element up to signs (KNOT-COMPOSE A, as corrected by NATIVE-PATHS A). Of the 256 signed Fano planes, only the plain one is a knot. | proved: exhaustive over sign classes | A |
| 2 | **A Fano atom with a line removed is transparent.** With any one of its lines removed, it sends the free relation through every one of its cuts, the same whichever line is removed. | proved: 91 of 91 freeness cases | A |
| 3 | **The knot is needed.** With arbitrary relations on the other cuts, the relation sent is the same whichever line is removed for every atom with at most one line-type cut, but for only 209 of 1,609 (configuration, cut) pairs with more. | proved: exhaustive over 253 configurations | A |
| 4 | **Deep points of a removal's side never decide creation at a Fano atom's line.** This holds even paired with deep points behind the atom's other elements. They add far sides only at a receiving atom's cut lines whose port relation has six patterns. | proved: 5,880 of 5,880 cases; 504 exception cases | B |
| 5 | **A free relation passes through a closed Fano atom unchanged.** | proved: 182 of 182 | B |
| 6 | **A Fano atom acts as one.** For creation this holds in every knot space. Far side by far side it holds except at that one place. On Fano trees, and wherever only atoms lie between, it holds without exception. | proved (corollary of 1, 2, 4 and 5) | B |
| 7 | **Bounding cannot show more.** Deep points behind a receiving atom's own other elements could add creation at its intact lines (56 of 980 abstract cases). They do not depend on the removed line. | proved: exhaustive | B |
| 8 | **Real spaces never use that room.** On 191 saved and 86 fresh spaces, every Fano atom's line receives exactly its closed verdict for its facing cut's port relation, at 154,165 of 154,165 pairs. The exception occurs at 1,325 receiving cuts and adds nothing. | computed; predictions written before the run | C |

## Answer

- **Yes for creation, in every knot space.** Whether a removal in a Fano atom creates at a line of another Fano atom does not depend on
  which of the atom's lines was removed.
- **Far side by far side, yes except at one finite place.** That place is a receiving atom's cut lines with a six-pattern port relation.
  - **On Fano trees.** It holds without exception.
  - **In every computed space.** It holds everywhere, the exception included: 277 spaces, 2,625 exception lines with room to add.
- **The mechanism is transparency.**
  - An atom missing a line constrains nothing through its cuts.
  - So the rest of the space sees the same port relation whichever line went.
  - A Fano atom's lines see nothing but that relation, apart from the exception.

## Reading

- **A handle is all or nothing from outside.**
  - **Present.** With all its lines, a Fano atom constrains each of its cuts exactly as one lost element would.
  - **Absent.** With any one line gone, it constrains nothing any cut can see.
  - **No partial state.** None shows through a cut. This is the precise sense of FAR-READ's reading, that atoms act as one.
- **In the intuition's terms.**
  - **The knot is one bound unit.** Removing any one of its lines unties all of it as far as the outside can tell.
  - **The source of it.** The unit property comes from the knot itself: the plain Fano plane is the only signed Fano knot, and in it any
    missing line frees every other element.
  - **The control.** It fails without the knot (conclusion 3).
- **Atoms are blind to depth, made precise.**
  - GLUE-READ's reading was that atoms are blind to depth and plane glue is not.
  - **Proved.** For creation in every knot space, and for far sides outside one finite place.
  - **Computed.** Everywhere in 277 spaces.
  - **The gap is narrow.** Bounding alone cannot close it (conclusion 7), yet no real side ever uses the room it leaves.
- **What this gives the reading rule.** FAR-READ B's split rests on atoms acting as one. That premise is now a theorem on Fano trees and,
  outside the exception, in every knot space.
- **Doctrine.**
  - **No space is assumed.** Cuts, channels and relations are relations among lines and points.
  - **The far sides.** They are the creation map's four census far sides, unchanged.

## Literature

- **Classical.**
  - The Fano plane is the smallest non-2-colourable 3-uniform hypergraph, and it is critical (property B).
  - The tight-cut decomposition of matching-covered graphs into bricks and braces (Lovász; Edmonds, Lovász and Pulleyblank).
  - Robertson, Seymour and Thomas: Pfaffian braces are built from planar braces and the Heawood graph.
- **Ours.**
  - The cut theorem (KNOT-COMPOSE A, NATIVE-PATHS A).
  - Minimality of knot spaces (THREEFOLD-SPACES A).
  - The receiving-cut law and its bound (GLUE-READ A).
  - Free ports along chains (CHAIN-TRANSFER A), which transparency extends to every knot space.
  - The two-round rule (PENDANT-LINE A).
  - Acts-as-one, computed (FAR-READ A).
- **New here.**
  - The classification of signed Fano knots.
  - Transparency.
  - The control.
  - The extended bound with mixed pairs, and pass-through.
  - The acts-as-one corollary.
  - The measurement of the exception.
- **Provenance.** No statement of the signed classification, of transparency, or of the corollary was found. The bounding method is
  GLUE-READ A's.

## Predictions for ticket C

These were written at 2026-11-07T16:54Z, before ticket C's code ran on any space:
- **P1 (fresh).** The exact far-side vector equals the real side of B with the removal's side replaced by its port relation.
- **P2 (saved and fresh).** It equals B's own closed verdict.
- **P3 (saved and fresh).** At every exception line, the real removal's side adds no far side.

All three held.

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.
  - Whether to publish the recent epics to knotlab and jscul.dev.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — acts-as-one proved | **Status:** Successful, with one finite exception left to computation | **Proved.** Transparency, and acts-as-one for creation in every knot space; far side by far side outside one place, and fully on Fano trees. **Computed.** The exception is empty on 277 spaces (2,625 lines with room to add). |
| Local direction — the reading rule as a theorem | Open | **Now proved.** The premise of FAR-READ B's split. **Not proved.** That no atom splits into smaller parts acting as one; the twin steps; reattachment; the exception. |
| Broader exploration — handles that are not Fano atoms | Known alternatives | **Untouched.** Non-Fano handles, such as census 58 and the glue's junctions, where HANDLE-COUNT found counting hardness lives. **The tool.** Transparency rests on the Fano plane being the only signed Fano knot; whether other handles are transparent is open. |
| Long-term goal — topology from native emergence | Capability gained | **Gained.** A handle is provably a unit of native creation, all or nothing from outside. **Missing.** A full proof that creation reads the genus, and handles that are not Fano atoms. |
| Next recommendation — the genus reading on Fano trees | **Next step:** Continue. Prove that FAR-READ B's rule returns exactly the Fano atoms of every Fano tree, where acts-as-one is now fully proved. **Two lemmas remain.** No atom splits into two parts of three or more lines acting as one, decided from creation inside an atom, whose closed sides are exact elements. The twin steps pick out the atoms, as CHAIN-TRANSFER C proved for trees with at most four cuts per atom. Then add plane glue. | **If proved.** Native creation reads the genus of every Fano tree by a theorem, and the glue case reduces to the exception. **If it fails.** A splitting atom shows what the reading must add. **Alternatives.** Whether junction handles act as one, tested on spaces with trisum glue (2/3); a proof of the exception from the structure of planar sides (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** Inside an atom everything is finite once closed sides are exact elements, and the twin steps are proved for trees with at most four cuts per atom. **Main uncertainty.** Internal creation may still feel deep points behind the atom's cuts, which bounding cannot control (conclusion 7). |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** Fano trees first, then the saved and fresh glue spaces. **Stop when** the rule is proved on Fano trees and its status with glue is stated, or a splitting atom is found. |
