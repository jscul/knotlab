# Does one hidden bit per tile force the pinwheel?

Epic `ONE-BIT-20261108-001` (program topology), 2026-11-08.

## The question

- **Where it comes from.** The selected next step of `ROUND-PRICE-20261108-001`, started at the coordinator's go-ahead on 2026-11-08
  (G1; A25, A35). The coordinator also asked for the outside-readers note at the end of this line, and sent two-bit decorations to
  the backlog.
- **The state.** Sixteen one-bit decorated substitutions of the pinwheel (eight up to exchanging the labels) excluded every crystal
  tried and forced every parent's label, but pairwise consistency left labelled parent collars outside their laws.
- **The question.** Settle them: a joint consistency test (if every off-law parent collar dies, the decoration forces the pinwheel),
  then a search for crystals that escape.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The joint test does not settle any.** A labelled parent collar passes when all its neighbours can be given surviving labelled collars that agree with it and with each other. The test is sound for forcing, but for each of the eight it leaves off-law survivors: 35 to 110 pinwheel collars with labellings the law does not produce, and 13 to 191 non-key collars. | proved (exact) | A |
| 2 | **Seven of the eight escape.** Of the 96,416 domino tilings of tori up to 4 × 4 with diagonals, 32 are collar-legal after one cut and 176 after two (11 distinct). A mixed tiling of the 4 × 4 torus with dominoes in both directions, legal after two cuts, admits six of the eight with a periodic labelling after two to four cuts, and a variant admits a seventh case. | exploratory experiment | B |
| 3 | **One bit per tile fails in 1,022 of 1,024 cases.** With `ROUND-PRICE-20261108-001`, every one-bit decorated substitution but one, up to relabelling, admits a periodic plane at every radius. The survivor is s(0) = 1 0 1 0 1, s(1) = 0 0 1 1 0. It excludes the rhombus lattice, two brick families and the eleven domino-torus crystals, its parent labels are forced, and local consistency leaves 50 off-law pinwheel collars and 191 non-key collars. | proved and exploratory | A, B |
| 4 | **A note for outside readers.** "The pinwheel tilings have no undecorated local rules", 5 pages, with an independent replay that rebuilds the collars by its own code and an angle-count completeness test. | result conversion | C |

## Answer

- **One bit per tile, placed by a decorated substitution, almost never forces the pinwheel.** 1,022 of the 1,024 ways let a crystal
  through, with a periodic labelling, at every radius.
- **One way remains open.** s(0) = 1 0 1 0 1, s(1) = 0 0 1 1 0 (and its relabelling) resists every crystal tried, and whether it
  forces the pinwheel is not known. If it does, one hidden bit per tile is the plane's price of roundness, beside the sphere's one
  bit per incidence.

## Reading

**Interpretation, not a theorem.**
- **Crystals get harder to find.** The rhombus lattice is legal after one cut; the escape for most survivors needed a mixed crystal
  legal only after two. A decoration that excludes the simple crystals pushes the escape to crystals whose seams are buried deeper.
- **What the survivor looks like.** Its children at the parent's corners, 0 and 4, and the middle child 2 carry 1 under a parent
  labelled 0; under a parent labelled 1 only children 2 and 3 do. Read as a bit, it marks the corner children under one parent
  label and not under the other.
- **Off-law parent collars.** Most of them are pinwheel collars with labels the decoration never produces. If they occur at all,
  they are pinwheel tilings carrying other labellings, which stop the induction without making a crystal.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Only the rhombus lattice and period-4 brick rows are legal after one cut, and brick rows after two (`COLLAR-PLANE-20261108-001C`, small tori at two cuts) | The 4 × 4 torus at two cuts, by the level-one filter (B) | 160 more planes legal after two cuts, including mixed tilings with dominoes in both directions; the one-cut list is unchanged |
| The sixteen exclude the three crystal families (`ROUND-PRICE-20261108-001`) | The 11 distinct domino-torus crystals (B) | Fails for 14 of the 16: they admit a crystal; holds for 2 |

The second row is not a correction: `ROUND-PRICE-20261108-001` claimed only what it tested.

## Literature and provenance

- **Sources.** Decorated matching rules (Radin 1994; Mozes 1989; Goodman-Strauss 1998); undecorated local rules (Levitov 1988;
  Socolar 1990); local consistency in constraint satisfaction (arc and path consistency, classical).
- **Classification.** The joint test is a standard method (known-with-delta). The escapes, the one surviving decoration and the
  note's conclusions: no-overlap-found, not a novelty claim.

## Workspace assumptions

- **Relied on.** A35 (hidden information counted as labels a decorated substitution sets), A33 (local laws read up to congruence),
  A25 (confirmed in the plane).
- **Taken by default.** None new. The crystal family (domino tilings of tori up to 4 × 4, two levels past the first legal cut, tori
  of index 1 or 2) is ticket B's declared scope.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families changed conclusions (A, B); the note (C) is a result conversion.
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
| This attempt — settle the sixteen | **Status:** Partially successful | 14 fail; 1 decoration (2 with relabelling) open |
| Local direction — one-bit decorated laws | Continue | A single, well-defined candidate remains |
| Broader exploration — G1 lines | Known alternatives | Two bits (backlog B8); edge labels; spheres |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | The plane's price of roundness is one bit per tile or more, as a decorated substitution |

**Corrections:** none. **Goals:** a G1 checkpoint (capability gained); backlog B8 added (two bits per tile, Payoff 1/3,
Concreteness 1/3); no goal change. **Assumptions:** none added; A35 relied on.

- **What is left open.** Whether s = 1 0 1 0 1 / 0 0 1 1 0 forces the pinwheel.
- **The missing bridge to G1.** A proof for that decoration, or a crystal that escapes it.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The last one-bit decoration (G1) | 2/3 — Substantial | 2/3 — Testable | Crystals legal after two or three cuts on larger tori and mixed shapes against it, then a forcing test on the undecorated geometry alone → a crystal that escapes, or a proof that it forces the pinwheel | Selected · awaiting go-ahead |
| 2 | Two bits per tile (backlog B8) | 1/3 — Incremental | 1/3 — Stated | Sampled two-bit decorations against the crystal families → a rate of survival | Alternative · deferred |
| 3 | Edge labels, as in Radin's rules (A35's challenge) | 1/3 — Incremental | 1/3 — Stated | One bit per edge against the rhombus crystal → a decoration the tile census missed, or none | Alternative · deferred |

1. **The last decoration.**
   - **Payoff 2.** A proof would set the plane's price of roundness at one bit per tile; a crystal would push it above one bit for
     decorated substitutions.
   - **Concreteness 2.** The decoration is fixed, its laws and tests exist, and the escape search is cheap per crystal; a forcing
     proof needs a test that follows the geometry rather than the labels.
   - **Uncertainty.** Whether a crystal exists that the families tried missed.
   - **Status.** Bound: one epic. Not started: the coordinator decides.
2. **Two bits.** The coordinator sent it to the backlog (B8 in `docs/RESEARCH_GOALS.md`).
3. **Edge labels.** It tests A35's measure, the way Radin's rules count.
