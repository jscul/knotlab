# A crystal one level up for the last one-bit decoration

Epic `CRYSTAL-UP-20261108-001` (program topology), 2026-11-08.

## The question

- **Where it comes from.** Direction 1 of `LAST-BIT-20261108-001`, started at the coordinator's go-ahead on 2026-11-08 as one bounded
  attempt (G1; A25, A35), with its direction 2, extension to distance 4, as a background stress test.
- **The decoration.** s(0) = 1 0 1 0 1, s(1) = 0 0 1 1 0, with its relabelling 11001 / 01010: the last of the 1,024 one-bit
  decorations of the pinwheel that no crystal tried had escaped. Its parent labels are forced, and 203 labelled parent collars
  outside its law survived every local test: 153 that are not pinwheel collars and 50 pinwheel collars with labels the law does not
  list.
- **The question.** Build a crystal from them: a periodic parent tiling whose labelled collars all lie among the survivors, one of
  them off-law. Its cut would be a periodic plane obeying the law that is not a pinwheel tiling.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Crystals one level up exist.** Growing tori from each off-law collar, on lattices spanned by periods seen in its own patches, 7 of the 153 non-pinwheel collars complete 26 periodic parent tilings, 8 to 40 tiles per period. In each, half the tiles are turned by arctan(4/3), twice the pinwheel angle, from the other half; each has collars that are not pinwheel collars, and cut once obeys the decoration's law. | exploratory experiment | A |
| 2 | **Every one-bit decoration admits a crystal.** Independent code checks a certificate for each of the sixteen decorations the exact census left open: these crystals for 10101 / 00110 and its relabelling, and one escape per class of `ONE-BIT-20261108-001B` for the other seven classes. With the census of 1,008 and the radius lemma, all 1,024 one-bit decorated substitutions of the pinwheel let a periodic plane through at every radius. | proved | B |
| 3 | **The forcing route needed every off-law parent to die** (a correction to `LAST-BIT-20261108-001`, not a block). A level-by-level proof repeats only on a plane of the labelled law, so the 50 off-law pinwheel collars had to die as well; they had never been tested by extension. The crystal settles the question the other way. | correction | — |

## Answer

**One hidden bit per tile, placed by a decorated substitution, never forces the pinwheel.** The last decoration falls to a new kind
of crystal. The smallest has 8 tiles per period: four with their legs along the axes and four turned by arctan(4/3), the angle of
the 3-4-5 triangle and twice the pinwheel's angle arctan(1/2). Four of its eight collars are not pinwheel collars, yet after one
cut, with the labels the decoration sets, every labelled collar is one of the decorated pinwheel's.

## Reading

**Interpretation, not a theorem.**
- **The price of roundness in the plane is more than one bit per tile**, counted as labels a decorated substitution sets (A35).
  On the sphere one hidden bit per incidence suffices; in the plane no single bit per tile does. Two bits per tile (backlog B8) is
  now the open count.
- **Where crystals hide their seams.** The earlier escapes hid them two to four cuts deep in domino tilings, all of whose tiles
  have their legs along the axes. These hide them in the meeting of two orientations, which one cut turns into pinwheel collars.
  A decoration that excludes every crystal of one orientation does not exclude crystals that mix two.
- **Why the forcing test could not have closed.** The crystals' non-pinwheel collars occur in a plane, so they survive extension
  at every distance; the stress test agrees at distance 3.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| 153 non-pinwheel parent collars survive extension to distance 2 (`LAST-BIT-20261108-001B`; 15 of 16 sampled at 3) | All 203 off-law collars, both kinds, at distance 3 to a fixed point (`crystal-up-s1`) | Two rounds remove 26, then 24; 109 non-pinwheel and 39 off-law pinwheel collars survive; every collar of the 26 crystals among them (`stress_crosscheck.py`). Distance 4 was stopped at its start, the crystals having settled the question |
| The crystal cut once obeys the law (B) | Cut twice: the 8-tile crystal and the six 20-tile ones | Every labelled collar in the law; holds |

## Literature and provenance

- **Sources.** Decorated matching rules for the pinwheel (Radin 1994) and for substitution tilings in general (Mozes 1989;
  Goodman-Strauss 1998), which show that enough labels force the pinwheel and give no lower bound; periodic tilings found by torus
  search (standard).
- **Classification.** The census for one bit per tile, its last crystal and the mixed-orientation crystals were not found in prior
  work (no-overlap-found).

## Workspace assumptions

- **Relied on.** A35 (the count of hidden information, under which the census is stated), A33 (laws up to congruence), A25.
- **Taken by default.** None new: the seeds, candidate periods, filters, lattice bound and budgets are ticket A's declared scope.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families (A, B) and one correction.
- **Administrative.** This note, the closure, two long-running registrations.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a crystal for the last one-bit decoration | **Status:** Successful | Crystals of 8 to 40 tiles; every one-bit decoration certified |
| Local direction — one-bit decorated laws | Practically exhausted | All 1,024 admit a crystal |
| Broader exploration — G1 lines | Known alternatives | Two bits (B8); edge labels (A35); bond versus chain distance (A12) |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | One hidden bit per tile is not enough for roundness in the plane |

**Corrections:** one, not a block (the forcing route of `LAST-BIT-20261108-001`). **Goals:** a G1 checkpoint (obstruction learned:
one bit per tile never forces the pinwheel); no goal change. **Assumptions:** none added; A35 gains a history line (the census
completed under it).

- **What is left open.** How many labels per tile a decorated substitution needs to force the pinwheel, and whether bits on edges
  change the count.
- **The missing bridge to G1.** A count of hidden information that does force roundness, or a reason none of a given size can.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Is bond distance the only native spacing? (challenge A12, backlog B4) | 2/3 — Substantial | 3/3 — Ready | Prove that on parity laws a chain counted in knots collapses to one step and a chain counted in distinctions equals bond distance; then compute both on the non-matroidal laws in hand → A12 confirmed for them, or the first law where a dimension or circle changes | Selected · started |
| 2 | Two bits per tile (backlog B8) | 2/3 — Substantial | 1/3 — Stated | Products of two one-bit decorations against the crystal list, rhombus to mixed-orientation → a two-bit decoration that excludes them all, or none | Alternative · deferred |
| 3 | Edge labels, as in Radin's rules (A35's challenge) | 2/3 — Substantial | 1/3 — Stated | A decorated substitution on edges, one bit each, against the same crystals → one that excludes them all, or none | Alternative · deferred |
| 4 | Dimension three on crystallizations (G2) | 1/3 — Incremental | 1/3 — Stated | Laws beyond one bit per edge on gems of lens spaces → an invariant past mod-2 cohomology, where Dijkgraaf–Witten answers are expected | Alternative · deferred |

1. **Bond versus chain distance.**
   - **Payoff 2.** Every space-from-a-law result since 2026-11-07 measures with bond distance (A12, never challenged). A theorem that
     the natural chain measures either collapse or coincide on parity laws would confirm question 9's measure where it has been used;
     a non-matroidal law where they differ would split it.
   - **Concreteness 3.** The matroid argument is short (two distinctions of a connected part lie on a common knot, and a union of
     overlapping knots is connected), and the laws and their code exist (`LOGIC-AXIS-20261107-001`, `LOGIC-CIRCLE-20261107-001`,
     `MATROID-CONVERSE-20261021-001`).
   - **Uncertainty.** Whether any non-matroidal law in hand has a spacing worth comparing.
   - **Status.** Bound: one epic. Started after this closure, as the coordinator's plan for this line asked.
2. **Two bits.** Now the open count, but 4^20 decorations; products of two one-bit decorations are one structured family, and no
   other is chosen yet.
3. **Edge labels.** Tests whether the count depends on where the bits sit; the edge substitution must be defined first.
4. **Dimension three.** One-bit laws on triangulations are classified (counting and one twist); beyond them classical answers are
   expected.

## Final report as sent

Sent to the owner on 2026-11-08 at 13:09 UTC and copied here verbatim.

The crystal held up, so the one-bit question is settled: **one hidden bit per tile never forces the pinwheel.** All 1,024 one-bit decorations admit a crystal at every radius.

The last decoration (10101 / 00110) falls to 26 periodic parent tilings built from its surviving parent collars. The smallest has 8 tiles per period, half of them turned by twice the pinwheel angle from the other half. A separate check on the note's standalone replay code confirms every crystal and the 14 earlier escapes. The epic is committed and published (5511f9673, 3ca271028).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a crystal for the last decoration | **Status:** Successful | 26 crystals, 8 to 40 tiles |
| Local direction: one-bit decorations | Practically exhausted | all 1,024 fail |
| Broader: G1 lines | Known alternatives | two bits, edge labels, A12 |
| G1 Space from a law | Obstruction learned | one bit per tile is not enough for roundness |

**Corrections:** one, not a block. The last epic's forcing route also needed the 50 off-law pinwheel collars to die. **Goals:** G1 checkpoint added, and backlog B8 (two bits) is re-rated to Payoff 2/3. **Assumptions:** A35 has a new history line, and A12 is now under challenge.

**Next step:** Research directions, selected #1

| # | Direction | Payoff | Concreteness | Status |
| --- | --- | --- | --- | --- |
| 1 | Is bond distance the only native spacing? (A12, backlog B4) | 2/3 | 3/3 | Selected · starting now |
| 2 | Two bits per tile (B8) | 2/3 | 1/3 | Deferred |
| 3 | Edge labels, as in Radin's rules (A35) | 2/3 | 1/3 | Deferred |
| 4 | Dimension three on crystallizations (G2) | 1/3 | 1/3 | Deferred |

I'm starting #1 as `BOND-CHAIN-20261108-001`. Its first step is a short matroid argument on parity laws, then the non-matroidal laws we already have.
