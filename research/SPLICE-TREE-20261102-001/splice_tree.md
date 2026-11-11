# Emergence along the tree of cuts

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a three-regular contradiction; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `SPLICE-TREE-20261102-001` (program topology), 2026-11-02.

## The question

- **The approval.** The owner said "Yes, let's continue" to HUB-GLUE-20261102-001's recommendation.
- **The question it approved.** A contradiction glued from several pieces has a tree of cuts. After one line is removed, are the kept knots
  iterated 2-sums at the held cuts, with new emergence only at the cuts opened on the way to the removed line?
- **The test.** Chains and trees of three and four pieces.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Orientation.** A removal holds every cut that points toward it (its ports stay tied) and opens every cut that points away. Beyond a held cut nothing depends on the removal. Beyond an opened cut the removal acts only through the interface. | proof (from HUB-GLUE A–C); 6 assemblies, 107 held and 69 opened cuts | A |
| 2 | **Iterated 2-sums.** The knots that cross only held cuts are exactly the iterated 2-sums, through held hubs, of knots that cross no cut. So new emergence lives only across opened cuts. | proof (induction on HUB-GLUE B, using that the cuts form a tree); 510 circuits, 162 across two held cuts | B |
| 3 | **Opened cuts interact.** New knots of one opened cut are carried across others, and two or three opened cuts create knots jointly. Three hub-level rules each fail: touching hubs, a port shared by two opened cuts on the removed line, and passage through the removed line's hub. | computation; 96 chains, 642 removals, 1126 joint knots | C |
| 4 | **Regularities.** Every joint knot has three or four points, and chains of K4^(3) pieces create nothing new. | computation; 96 chains | C |
| 5 | **Method.** A derivation by eliminations never uses a knot larger than its result, so closures computed with a size bound are exact within it. Elimination over tie classes reproduces HUB-GLUE C's count, which was computed with representatives. | proof (elementary); check | C |

## Answer

- **Yes for the held cuts.** They compose exactly, cut by cut, as iterated 2-sums, and beyond a held cut nothing depends on the removal.
- **Yes, new emergence lives only across opened cuts, but not cut by cut.** The opened cuts act as one zone:
  - new knots arise at single opened cuts;
  - they are carried across the other opened cuts;
  - knots also arise jointly across two or three opened cuts at once.
- **Hubs don't localize the zone.** No hub-level feature decides where knots arise inside it.
- **So the kept knots after a removal have two parts.** On the held side, a tree of exact compositions. On the opened side, a zone of
  new emergence that does not decompose by hubs.

## Reading

- **The removal orients the tree.**
  - **Held.** Cuts pointing toward the removed line hold, and their glue composes.
  - **Opened.** Cuts pointing away open, and their glue creates.
- **Hubs do not localize creation.** Touching hubs were the natural candidate, since they are the places where two cuts share a point.
  They decide nothing.
  - K4 > Fano > K4 with disjoint hubs carries new knots across its second cut.
  - K4 > K4 > K4 with touching hubs creates nothing.
  - Fano > K4 > K4 with disjoint hubs creates 36 joint knots.
- **What looks decisive (scouting for the next step, not a claim): handles.** The scout took single splices of every ordered pair of
  census contradictions, with every removal on the point side (720 removals):

  | Removed line's side | Interface | Removals | With new knots |
  | --- | --- | --- | --- |
  | Planar | 4 patterns | 464 | 0 |
  | Planar | 6 patterns | 96 | 0 |
  | Non-planar (Fano, census 58) | 4 patterns | 48 | 0 |
  | Non-planar (Fano, census 58) | 6 patterns | 160 | 100 |

  - **The pattern.** New knots appeared only when the opened hub had become a knot on its ports (six patterns) and the removed line's
    side was non-planar.
  - **Consistent with the chains.** The chains of K4^(3) pieces (planar) create nothing.
  - **Why it matters.** By THREEFOLD-SURFACES each Fano piece is a handle. So the knot's emergence after a removal may be created only in
    handles, with planar glue only composing.
- **Doctrine.**
  - Hubs remain equality fan-out, not contact.
  - What composes and what is created here is emergence (knots), never a native path or a distance.

## Literature

- **Ours.**
  - HUB-GLUE A–C.
  - THREEFOLD-GRAMMAR (Fano pieces, planar glue).
  - THREEFOLD-SURFACES (genus = number of Fano pieces).
  - NATIVE-PATHS A (the 3-edge-cut theorem).
  - MUTUAL-SELECTION C's census.
- **Classical.**
  - Matroid 2-sums along a tree decomposition and circuit elimination (Tutte; Cunningham–Edmonds).
  - Tight cuts and Pfaffian planar graphs (Lovász; Kasteleyn; Little).
- **New here.**
  - The orientation reading.
  - The iterated 2-sum in this relational setting. Its matroid analogue is standard, so folklore risk is moderate.
  - The classification of how opened cuts interact.

## Pending the owner

Still open from earlier epics:
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — are the kept knots iterated 2-sums at held cuts, with new emergence only at opened cuts? | **Status:** Successful | **Both parts proved.** Ticket A gives the orientation; ticket B gives the iterated 2-sums, so new emergence lives only across opened cuts. **Unresolved.** The opened cuts form one zone, and its emergence does not decompose by hubs (ticket C). |
| Local direction — decomposing emergence along the splice tree by hubs | Practically exhausted | **Held side settled.** **Opened side.** Three hub-level rules are refuted on 96 chains. What remains is a property of the pieces, not of the hubs. |
| Broader exploration — where the knot's emergence is created after selection | Open, with a lead | **The lead.** In the census scout, new knots appear only when the hub becomes a knot and the removed line's side is non-planar (100 of 160 such removals, 0 of 560 with a planar side). |
| Long-term goal — composed structure from native emergence | Capability gained; obstruction learned | **Gained.** A global composition law on the held side. **Obstruction.** The opened side does not decompose by hubs. **The limit.** Hubs are equality fan-out, so emergence composes and is created, but no native path or distance is claimed. |
| Next recommendation — emergence needs a handle | **Next step:** Continue. **The conjecture.** At an opened cut, new emergence needs both a knot on the hub (six patterns) and a non-planar removed side, so planar glue only composes. **First test.** Planar contradictions beyond the census as removed sides with six-pattern interfaces (planar splices of census spaces, up to 19 points); one new knot refutes it. **Then.** Prove the planar case, then measure the non-planar side. | **If yes.** The knot's emergence after selection is created only in handles (Fano pieces, the genus), tying logical emergence to the topology of its space. **If no.** The census split was a small-piece effect, and the zone needs another invariant. **Alternatives.** Classify the joint knots of three and four points (1/3). Explain why four-pattern interfaces never create (1/3; likely a lemma inside the main line). |
| Interest — that recommendation | **3/3 — Hot** | **Evidence.** A clean split over all 64 ordered census pairs (0 of 560 planar against 100 of 160 non-planar six-pattern removals), consistent with every chain in ticket C. **Payoff.** It would locate creation in the handles. **Main uncertainty.** The pieces are small (at most 8 points), the only non-planar ones contain a Fano, and no proof route is visible yet. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened; the scout only calibrated this recommendation. **Bound.** Census pieces and planar splices up to 19 points, all circuits. **Stop when** a planar removed side with a six-pattern interface creates a new knot (refuted), or the planar statement is proved. |
