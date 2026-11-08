# A periodic plane obeys the pinwheel's undecorated local laws

Epic `COLLAR-PLANE-20261108-001` (program topology), 2026-11-08.

## The question

- **Where it comes from.** Direction 2 of `GROWTH-LAW-20261107-001`'s closure report, "the collar law off the pinwheel" (G1, A25),
  rated Payoff 2/3 and Concreteness 2/3. The coordinator started it on 2026-11-08, after the owner asked whether every direction
  rated 2/3 on both scales should be run, beside direction 1 (knots across time).
- **The question.** Outward growth by the pinwheel's own collar law left the pinwheel: four forced-first runs grew 500 to 1,005 tiles
  of collar-legal patches that are not pinwheel patches. Is there a periodic plane that obeys the collar law (every tile's collar
  one of the 108 complete pinwheel collars of `PINWHEEL-ATLAS-20261107-001A`)? Stop at one, or at none to a declared size.
- **Why it matters.** `PINWHEEL-ATLAS-20261107-001` left open whether the pinwheel's undecorated law forces aperiodicity, and with it
  roundness. If it did, the plane would need no hidden information where the sphere needs a bit per incidence. A25 of
  `docs/ASSUMPTIONS.md` (a law without hidden states cannot force roundness) was under challenge on exactly this point.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **A periodic plane obeys the collar law.** Four tiles around a common right angle make a rhombus with diagonals 2 and 4. The rhombi tile the plane by translations, and cut once by Conway's cut they give a periodic tiling, 20 tiles per period, in which every tile's collar is a complete pinwheel collar. It uses 10 of the 108. | proved (exact witness) | A |
| 2 | **And every radius.** The cut keeps collar-legality. After k cuts, every patch of tile radius r of a collar-legal plane lies in the cut of one pinwheel collar once (r + 1)√5 · 5^(−k/2) is below the least collar width, 0.447 for legs 1 and 2. So for every r a periodic plane obeys the pinwheel's undecorated radius-r law. The twice-cut lattice, 100 tiles per period, obeys the 1,168-form radius-2 atlas; the three-times-cut one obeys the radius-3 atlas (stress test). No undecorated local law of the pinwheel forces aperiodicity. | proved; radius 2 and 3 computed | A, stress test |
| 3 | **The collar law forces one level of composition.** Each collar names its tile's parent, and in a collar-legal plane touching siblings name the same one. Of 956 compatible sibling pairs, 888 agree, and each of the other 68 leaves a tile with no consistent completion. So every collar-legal plane is the cut of a plane of √5-larger triangles whose collars lie in a level-one law L1: 1,264 collars per handedness, 54 of them pinwheel keys. Only 156 (54 keys, 102 others) survive arc consistency. The rhombus lattice's collar is one of the 102, so composition stops there. | proved (exact computation) | B |
| 4 | **The patches that left the pinwheel.** Growth's four off-pinwheel patches compose once with no conflicting parent. Their defect sits one level up, in 45 non-key collars of L1. They show no period of their own: away from the defect they look like the pinwheel. | proved (B); measured | B |
| 5 | **The census.** Of the periodic planes `PINWHEEL-ATLAS-20261107-001B` rejected uncut, cut one to three times: after one cut only the rhombus lattice obeys the collar law, in four presentations (checkerboard grids, the two isosceles shapes tiled by half-turns, eight domino tilings of the 2 × 4 and 4 × 2 tori). After two cuts six brick-row planes and 16 more domino tilings join. The plain rectangle lattice, the kite and both parallelograms fail at every cut tried. The larger tori after one cut are pending. | exploratory experiment | C |

## Answer

- **Yes: a periodic plane passes the collar law.** The rhombus lattice cut once is an explicit one, with 20 tiles per period.
- **Larger radii do not help.** Its further cuts obey every larger radius. No list of undecorated pinwheel patches, of any radius,
  forces a plane to be a pinwheel tiling or even non-periodic. Forcing it takes decorations, as in Radin's matching rules (1994):
  hidden information.
- **The local structure is real but shallow.** The collar law forces one level of the hierarchy, and only one. The periodic plane is
  the cut of a crystal whose collars pass at the next level down but are not pinwheel collars.

## Reading

**Interpretation, not a theorem.**
- **The plane is like the sphere after all.** On spheres a law without hidden states cannot tell a round sphere from a capped tube
  (`SPHERE-GROWTH-20261107-001`). In the plane the pinwheel's own law, at any radius and without decorations, cannot tell the round
  pinwheel from a crystal. A crystal's circles are polygons with rational π (`LOGIC-CIRCLE-20261107-001`). So roundness costs hidden
  information in the plane too, and A25 holds here: confirmed for the pinwheel at every radius.
- **What hides the crystal.** A cut is self-similar. Cutting a crystal k times buries its seams under k levels of pinwheel-like
  structure, so any fixed window sees only pinwheel forms once k is large enough. The rhombus lattice is special only in being
  legal after a single cut.
- **Why growth still got stuck.** The collar law is not an aperiodic set, so Dworkin and Shieh's theorem on deceptions does not
  explain the dead ends of outward growth. Those dead ends are measured facts about coin growth, not consequences of aperiodicity
  (correction below).
- **The atlas's reading is withdrawn.** `PINWHEEL-ATLAS-20261107-001` read its periodic-plane test as "the plane may need no hidden
  bit at all". Its measurement stands: none of the 96,474 planes it tested obeys the law uncut. But one of them, cut twice, obeys
  the same law (correction below).

## Stress test

One size past each computed claim (`stress_test_radius3.py` here, with its output).

| Claim | One size past | Result |
| --- | --- | --- |
| The twice-cut rhombus lattice R_2 obeys the radius-2 dart atlas (A; 4,048 darts) | The radius-3 atlas, computed as the atlas proof computed radius 2 (five cuts of each complete collar, no dart near the edge: 3,530 codes, each with one label); R_2, R_3 and R_4 against it | pass: R_3 (30,288 darts) and R_4 (58,396) obey it; R_2 does not (1,200 of 8,908 darts), as expected one radius past; the rectangle lattice cut three times fails (6,828 of 12,498) |
| Only the rhombus lattice passes after one cut (C; small tori) | The 2 × 6, 6 × 2 and 4 × 4 tori after one cut (95,232 planes) | **pending**: running in the background (`collar-plane-c1`, `docs/LONG_RUNNING.md`); folded in by a follow-up commit |

The radius-3 atlas also gives one size past for `PINWHEEL-ATLAS-20261107-001A`: at radius 3, too, every code carries one label.

## Literature and provenance

- **Sources.**
  - **Matching rules.** Radin (Annals of Mathematics 139, 1994) forced the pinwheel with decorated tiles; Mozes (1989) and
    Goodman-Strauss (Annals 147, 1998) did so for substitution tilings in general.
  - **Undecorated local rules.** Levitov (Commun. Math. Phys. 119, 1988) asked which tilings an atlas of undecorated patches
    forces; Socolar (1990) gave weak rules.
  - **Collared tiles.** Anderson and Putnam (1998); for the pinwheel Barge, Diamond, Hunton and Sadun (2010).
  - **Recognizability.** Solomyak (1998).
  - **Deceptions.** Dworkin and Shieh (Comm. Math. Phys. 168, 1995).
- **Searched (2026-11-08, bounded).** Web searches on undecorated local rules, atlases and matching rules for the pinwheel, and a
  2012 survey of aperiodicity notions for Delone sets that discusses the pinwheel. No statement that the pinwheel lacks
  undecorated local rules was found, and no periodic plane obeying its local laws.
- **Classification.** The method is known: cutting a periodic tiling that obeys a small-radius law to defeat every radius is the
  standard way local rules fail for substitution tilings. The witness and the pinwheel conclusion, the forced first level and the
  level-one law: no-overlap-found, not a novelty claim. Folklore risk is moderate.
- **Where the ideas came from.** The question is `GROWTH-LAW-20261107-001`'s direction 2. The witness turned up in a census of the
  atlas epic's own periodic families after cutting, run to test the composition idea. The composition lemma came from asking why
  growth's off-pinwheel patches had no conflicting parents.

## Workspace assumptions

- **Relied on.**
  - **A23.** The atlas's rooted codes, for the radius-2 and radius-3 checks.
  - **A24.** The pinwheel law fixes its map.
- **Challenged.**
  - **A25, a law without hidden states cannot force roundness.** Confirmed in the plane for the pinwheel, at every radius: its
    undecorated local laws all admit a periodic plane.
  - **A28, outward growth is judged by its law's local consistency.** Bears on it: the law that growth was judged by admits
    periodic planes, so its dead ends say nothing about aperiodicity.
- **Taken by default.**
  - **Congruence.** A local law is read up to congruence: rotations and reflections are free, as in the program's laws, which carry
    no frame.
  - **The census.** It used the atlas epic's own families of periodic planes. Both are recorded in the register as A31.

## Corrections

Two earlier readings are corrected; both are logged in `docs/CORRECTIONS.md`.
- **The deceptions reading of `GROWTH-LAW-20261107-001`** (Narrowing). It said the collar law's dead ends are consistent with
  Dworkin and Shieh, and that the local direction is "exhausted in the sense of Dworkin and Shieh". Neither the collar law nor the
  radius-2 law is an aperiodic set, so the theorem does not apply to them. The measured dead ends stand.
- **The atlas reading of `PINWHEEL-ATLAS-20261107-001`** (Narrowing). It said no tested periodic plane comes close, and that the
  plane may need no hidden bit at all. One of its tested planes obeys the law after two cuts, and no undecorated local law of the
  pinwheel forces roundness. The finite law and the label theorem stand.

## Ratio

Since the epic opened:
- **Substantive.** Three evidence families changed conclusions: A and B (proofs) and C (exploratory experiment). The radius-3 stress
  test is substantive too.
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a periodic plane for the collar law | **Status:** Successful | Found one; no radius forces the pinwheel |
| Local direction — undecorated laws of the pinwheel | Practically exhausted | Every radius admits a crystal |
| Broader exploration — G1 lines | Known alternatives | Decorated laws; spheres; growth |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | Roundness costs hidden information in the plane too |

**Corrections:** two narrowings (the deceptions reading of `GROWTH-LAW-20261107-001`; the atlas reading of
`PINWHEEL-ATLAS-20261107-001`), logged in `docs/CORRECTIONS.md`. **Goals:** a G1 checkpoint (obstruction learned); no goal
change. **Assumptions:** A25 Confirmed in the plane for the pinwheel; history lines for A28 and the atlas entries; A31 added (local
laws read up to congruence, the census's families).

- **What is left open.** How much hidden information forces roundness in the plane: Radin's decorations suffice, none is too little.
  Whether a collar-legal plane has fewer than 20 tiles per period, and which non-periodic planes besides the pinwheel obey the
  collar law.
- **The local direction.** It is exhausted for a reason that is a theorem: no undecorated pinwheel law, at any radius, forces
  aperiodicity. Its accepted results are the witness, the radius bound, the forced first level and the level-one law.
- **The missing bridge to G1.** A law with hidden states that forces a round plane, with its hidden information counted, so the
  plane's price of roundness can be set beside the sphere's one bit per incidence.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The price of roundness in the plane (G1, A25) | 2/3 — Substantial | 1/3 — Stated | Label each tile with its child index (5 labels) and test whether the labelled collar law forces composition at two levels → a count of hidden bits that forces it, or the first escape | Selected · awaiting go-ahead |
| 2 | A note: the pinwheel has no undecorated local rules | 1/3 — Incremental | 3/3 — Ready | The witness, the radius bound and the checks written for outside readers, with a prior-work search in the tiling literature's words → a note that passes review, or prior work found | Alternative · deferred |
| 3 | Which planes obey the collar law (G1) | 1/3 — Incremental | 2/3 — Testable | Grow from each of the 102 non-key core collars of L1 with backtracking → a non-periodic non-pinwheel plane (a fault line), or none | Alternative · deferred |
| 4 | The least period | 1/3 — Incremental | 2/3 — Testable | Periodic planes with 2 or 3 tiles per period against L1's core → a collar-legal plane with 10 or 15 tiles per period, or 20 is least | Alternative · deferred |

1. **The price of roundness in the plane.**
   - **Payoff 2.** It would answer G1's open question, how much hidden information roundness costs, for the plane.
   - **Concreteness 1.** Radin's decorated rules give an upper bound, and ticket B shows the undecorated collars already force one
     level. But no count of hidden bits is in hand, and the right labelling is not fixed.
   - **Uncertainty.** Whether a small fixed alphabet forces every level.
   - **Status.** Bound: one epic. Not started: the coordinator decides whether this thread or a new one takes it, so it does not
     overlap a running line.
2. **A note.**
   - **Payoff 1.** It makes the result checkable by outside readers. The tiling community may already know it.
   - **Concreteness 3.** The witness and all checks exist.
3. **Which planes obey the collar law.**
   - **Payoff 1.** It would map the collar law's planes beyond the pinwheel and the crystals.
   - **Concreteness 2.** The core and the growth engine exist.
4. **The least period.**
   - **Payoff 1.** It would sharpen the witness.
   - **Concreteness 2.** Ticket B reduces it to small periodic planes against a finite law.
