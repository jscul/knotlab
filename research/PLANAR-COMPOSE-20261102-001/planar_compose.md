# Planar glue only composes

Epic `PLANAR-COMPOSE-20261102-001` (program topology), 2026-11-02.

## The question

- **The approval.** The owner said "Yes, continue." to HANDLE-EMERGENCE-20261102-001's recommendation.
- **The proof goal.** Prove from the matching picture that a plane removed side never creates. Start with a single-port lemma, and
  check it on plane spaces first.
- **The handle test.** Test on Fano splices whether creation disappears when the handle is cut open along non-contractible cycles.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The hub's tie class on a plane side.** It contains every point on the removed line's three faces. The solutions are perfect matchings of lines to faces, two of which differ by alternating cycles. Each cycle flips exactly the points it encloses and never enters the removed line's faces. | proof; 325 removals | A |
| 2 | **The route lemma.** Suppose the hub and a near point pin the gluing pattern, and either (i) the hub is tied to a port other than the pattern's odd port, or (ii) it forms a near knot with the two other ports whose excluded pattern is one step from the pinned one. Then every pinned-and-separated three-point knot is generated, whatever the far side, because the needed far knot is automatic. | proof (any near side) | A |
| 3 | **The access lemma splits plane from non-planar.** All 4560 pinnings on 30 plane spaces are of type (i) or (ii). All 336 pinnings of the Fano plane and census 58 are of neither type. | computation | A |
| 4 | **Consequence.** On those 30 plane near sides, no pinned-and-separated three-point knot is ever new at a six-pattern removal, for any far side. The routes are confirmed knot by knot (2142). | proof from 2 and 3 | A |
| 5 | **The premise extends.** All 1884 further new knots (non-planar near sides glued to census and 10-point plane far sides) are pinned-and-separated three-point knots through the hub. | computation | A |
| 6 | **Cutting a handle open is not canonical.** Uniting the near solutions over the four homology sectors removes all creation for some embeddings and cut positions and not for others, even within one homology class (on Fano > Fano, 25 cut positions against 55). Dropping one parity removes about nine tenths of the new knots, and local point flips remove none. | computation | B |

**Scouting after ticket A (not a claim; `access_lemma_scout.py`).** The access lemma also holds on 12 grown plane spaces of 16, 18 and
20 points, both readings: 4460 more pinnings (2130 of type (i), 2330 of type (ii)), none failing.

## Answer

- **The planar statement is reduced to one combinatorial lemma.**
  - **The lemma.** On every plane space, the hub reaches the ports: tied to a non-odd port, or in a well-placed two-port near knot.
  - **What it gives.** The route lemma (proved) turns it into non-creation of every pinned-and-separated three-point knot, whatever is
    glued on the far side.
- **The lemma is not proved.** It holds on 8020 plane pinnings across 42 spaces and fails on every non-planar pinning tested.
- **Also unproved.** The premise that every new knot has this form (it does in all 2820 found).
- **The homology reading needs a canonical form.** As tested, "a handle creates exactly what its homology parities add" fails:
  cutting a handle open helps or not depending on where the cut runs. The homology parities still carry most of the creation (one
  dropped parity removes about nine tenths), and local relaxations remove none.

## Reading

- **Why a plane side composes.** A plane side's removed line leaves a hub that always reaches the gluing ports.
  - **How it reaches them.** Directly, by a tie through the faces the removed line leaves (item 1). Or through one well-placed knot
    with two ports.
  - **What that makes possible.** Every joint use of the ports can be taken apart one port at a time.
- **Where a handle differs.**
  - **The Fano plane.** The hub sits on the very port it pins as odd.
  - **Census 58.** Its two-port knot points the wrong way.
  - **Either way,** no single port can carry the constraint across, and a new knot appears.
- **Doctrine.** Hubs remain equality fan-out, and no native path or distance is claimed.

## Literature

- **Ours.** HANDLE-EMERGENCE A–C (planar tests, pin and separate, the skip model), SPLICE-TREE C, THREEFOLD-SPIN.
- **Classical.**
  - Kasteleyn's face condition, and plane bipartite perfect matchings with their alternating-cycle structure.
  - Spin structures, the genus-1 sectors (Kasteleyn's four Pfaffians).
- **New here.**
  - The tie-class lemma.
  - The route lemma.
  - The access lemma and its plane/non-plane split.
  - The handle-cut measurements.

## Pending the owner

Still open from earlier epics:
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — prove planar non-creation from the matching picture | **Status:** Partially successful | **Proved.** The tie-class and route lemmas. **Reduced.** The three-point case now rests on one lemma, which splits plane from non-planar on every space tested (8020 plane pinnings). **Not proved.** The lemma itself, and the premise that every new knot is a pinned three-point knot. **The handle-cut reading fails as stated.** |
| Local direction — the planar theorem | Continue, narrowly | **What is left.** Two precise lemmas, with strong evidence and a structural foothold: in the height picture, a hub-tied port makes the gluing line's states a chain with that port's pair in the middle. |
| Broader exploration — where selection creates | Known, with a refined lead | **Handles create.** Their homology parities carry most of the creation, but not canonically in point values. A formulation in odd-point choices is the natural fix. |
| Long-term goal — topology from native emergence | Capability gained; obstruction learned | **Gained.** A sharp mechanism for why planar glue composes: the hub reaches the ports. **Learned.** The topological reading of creation is not a simple homology statement. |
| Next recommendation — finish the planar theorem | **Next step:** Continue. **First,** prove the access lemma from the height picture. Show that a near point's parity can never single out the middle state, and that otherwise the two-port knot points one step from the pinned pattern. **Then,** attack the premise with the skip model: show that every crossing knot reduces to three-point knots through the hub. | **If yes.** A theorem: on a plane side, selection creates no new knot at a six-pattern removal, for any far side. **If no.** The obstruction would show exactly where the matching picture fails. **Alternatives.** Selection as a dimer model on large plane spaces: line–face matchings are lozenge-like tilings, so ask how far a selection's influence reaches (2/3). State the homology reading in odd-point choices (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The lemma splits plane from non-planar exactly, holds up to 20 points, and has a structural foothold in the height picture. **Main uncertainty.** The premise has no proof route yet, so proving the access lemma alone leaves the theorem conditional. The dimer alternative may carry more discovery value. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** Plane spaces up to 20 points for checks. **Stop when** both lemmas are proved or one fails on a plane space; reassess against the dimer direction after the first lemma. |
