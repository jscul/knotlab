# The pinwheel's own law: what it forces and what it grows

Epic `PINWHEEL-ATLAS-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner said "Then both yes" to the recommendation after `PINWHEEL-NATIVE-20261107-001`: qualify that epic's
  record, and start the round-plane epic with the radius-2 pattern set first. The owner also gave a standing mandate to follow
  promising leads, and later asked to wrap up the current lines rather than widen them.
- **The shared question** with the sphere line (`SPHERE-GROWTH-20261107-001`, `GROW-COIN-20261107-001`): how much hidden information
  does roundness cost, and can growth replace it?
- **For the plane.**
  - **The law.** What is the pinwheel's own local law, exactly?
  - **Forcing.** Does that law force a round plane, or does a periodic plane, whose circles are polygons, satisfy it too?
  - **Regrowth.** Can the regrowth rule drop its labels, with the growing patch's shape as its only memory?
- **Question served.** Question 9 (space from a law), goal G1.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The pinwheel's law is finite and reads its own labels.** The collared tiles of all pinwheel patches form 193 keys closed under the cut (108 complete, in 54 mirror pairs). Four cuts of each complete collar contain every radius-2 neighbourhood of its centre. So in every pinwheel tiling the radius-2 neighbourhoods of darts take exactly 1,168 forms, each with one oriented label: every edge's label is a function of the unlabelled planar map within radius 2. At radius 1 there are 198 forms, 9 with two labels. The level-7 patch already shows every form. | proved (finite closure, exact computation) | A |
| 2 | **No tested periodic plane obeys the law, even at radius 1.** None of 96,474 periodic configurations passes: rectangle grids and brick rows with every diagonal pattern of period up to 2 × 2, every domino tiling of the 2×2 to 4×4 tori with every diagonal choice, and the six two-tile shapes tiled by half-turns. The frame-consistent cut, which is neither periodic nor round, fails too. The pinwheel passes and the tetrakis triangulation fails. | exploratory experiment | B |
| 3 | **Regrowth needs no labels.** In the bare growing patch T_k (levels 4–7, up to 267,766 darts), every dart's label, boundary included, is a function of its unlabelled radius-2 code, pooled over all levels: 3,227 codes, no conflict. Marking the outer face is not even needed. | exploratory experiment | D |
| — | **Outward growth one tile at a time** was not run. It is held as backlog at the owner's request. | retired | C |

## Answer

- **The law is finite, and it carries its own labels.** The pinwheel's radius-2 law is a finite list of 1,168 local forms (theorem).
  - **Every label is read.** Each form fixes the label of its edge.
  - **Regrowth reads only the map.** The eleven-label regrowth rule can run on the bare map: read each label within radius 2, then
    cut. At the boundary this is measured on levels 4–7; inside it is proved.
- **The law is selective.** No tested periodic plane comes close.
  - **Every dart fails.** Each tested plane fails at radius 1. For the half-turn tilings and the frame-consistent cut, every tested
    dart lies outside the law.
  - **Unlike the sphere.** On the sphere, a law without hidden states cannot tell a round sphere from a tube, because the tube's
    balls all occur in the sphere. In the plane, the pinwheel's own law rejects every tested non-round plane outright.
- **For the shared question.** For regrowth, roundness costs no hidden information beyond the patch's own shape at radius 2. Whether
  the law forces roundness outright is open: no periodic plane passed, but none built from the pinwheel's own vertex stars was
  searched.

## Literature and provenance

- **Ticket A.**
  - **Sources.**
    - **Collared tiles.** Collared tiles closed under a substitution (Anderson and Putnam, 1998). For the pinwheel: Barge, Diamond,
      Hunton and Sadun (2010); Frettlöh, Whitehead and Whittaker (2014).
    - **The combinatorial rule.** Kenyon and Stephenson (Proc. Amer. Math. Soc. 147, 2019). Their tiles' four corners are given; here
      the labels are read from the bare map.
    - **Recognizability.** Classical in the geometric setting (Solomyak, 1998).
  - **Classification.** The method is known. The 1,168-form atlas and the theorem that labels are read within radius 2 were not
    found. Folklore risk is moderate.
- **Ticket B.**
  - **Undecorated local rules.** These are Levitov's local rules (Commun. Math. Phys. 119, 1988). Strong ones exist for undecorated
    rhombus tilings only in a few symmetries, and Socolar's weak rules (1990) cover more.
  - **Decorated matching rules.** These exist for substitution tilings generally: Mozes (1989); Goodman-Strauss (Annals of
    Mathematics, 1998); for the pinwheel, Radin (Annals of Mathematics, 1994); and Fernique and Ollinger (2010) on combinatorial
    substitutions and sofic tilings.
  - **Not found.** An undecorated local law for the pinwheel, or any test of periodic planes against it.
- **Ticket D.** Not found: the boundary readability of the growing patch.
- **For the retired growth ticket C.**
  - **Growth rules with dead surfaces.** Onoda, Steinhardt, DiVincenzo and Socolar (1988); the review by Grimm and Joseph.
  - **Local-rule assembly.** Berger and Shor's local rules for virus capsids.
  - **Self-assembly.** The self-assembly literature.

## Reading

**Interpretation, not a theorem.**
- **What the pinwheel's law is made of.** Mostly T-junctions at long-leg midpoints. Degree-3 vertices, where two right angles meet on
  a straight side, are its commonest vertices. No crystalline arrangement of the same triangle that was tested makes them in the
  combinations the law allows.
- **A plane is not a sphere here.** The sphere line found that roundness needs a hidden bit per incidence (the seam law), and that
  label-free growth does not remove that need (`GROW-COIN-20261107-001`). The pinwheel's plane may need no hidden bit at all: its
  regrowth reads everything from the map, and its local law rejects every tested non-round plane. Whether it rejects all of them is
  the open question.

## Workspace assumption challenged

- **"A local law without hidden states cannot force roundness."** This held for the closed spheres (`SPHERE-GROWTH-20261107-001`).
  For the plane it is untested rather than false: every tested non-round plane fails the pinwheel's radius-1 law outright.

## Ratio

Since the epic opened:
- **Substantive.** Three evidence families changed conclusions: A (proof), B and D (exploratory experiments).
- **Administrative.** This note and the closure.

## Pending the owner

- **Carried from `LOGIC-AXIS-20261107-001`.** Whether a native knot must also be natively bound
  (`research/LOGIC-AXIS-20261107-001/canonical_correction_request.md`).
- **Carried from earlier epics.**
  - The PHASE-HALO and FACE-CLAIM qualifications.
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the pinwheel's own law | **Status:** Successful | Law finite and self-reading; periodic planes rejected |
| Local direction: the combinatorial pinwheel law | Continue later | Forcing still open |
| Broader exploration: question 9 lines | Known alternatives | Spheres need a hidden bit; the plane may not |
| Long-term goal: G1 Space from a law | Capability gained | Regrowth needs no hidden information |

- **Corrections:** none in this epic. The two corrections made the same day concern `PINWHEEL-NATIVE-20261107-001` and are logged.
- **Goals:** a G1 checkpoint (capability gained); no goal change.
- **The local direction.** It stays open on one question: whether any plane other than a pinwheel tiling obeys the radius-2 law.
  Ticket B rejected every tested periodic plane, but its families were rectangle-based.

**Next step:** Continue — No next action selected. The lines are held, at the owner's request, to wrap up current work rather than
widen it.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does the undecorated law force aperiodicity? | 2/3 — Substantial | 2/3 — Testable | SAT search for torus maps from the law's own vertex stars → one found, or none up to a declared size | Alternative · deferred |
| 2 | Grow the plane one tile at a time, every growth order | 2/3 — Substantial | 1/3 — Stated | Forced moves from one tile under the radius-2 law → radius 30 or an unavoidable dead end | Alternative · deferred |
| 3 | Prove radius 2 at the boundary for every level | 1/3 — Incremental | 3/3 — Ready | Rerun A's collar closure on the 85 partial collars → theorem or a conflict | Alternative · deferred |

- **#1.** It would settle whether roundness costs any hidden information in the plane: an undecorated law forcing aperiodicity would
  be Levitov-type local rules for the pinwheel, not found in the literature. The method is clear (a SAT encoding over the 198
  radius-1 forms), but the search may be large. A negative answer still needs a proof.
- **#2.** It would show whether outward growth can replace the hierarchy. The design is open: dead surfaces are classical
  (Onoda–Steinhardt–DiVincenzo–Socolar), and the sphere line found that label-free growth keeps the roundness witness. A result
  belongs to the law only if it holds in every growth order.
- **#3.** It converts ticket D into a theorem with the method already in hand. The partial collars are the 85 incomplete keys of
  ticket A's closure. It changes little on its own.
