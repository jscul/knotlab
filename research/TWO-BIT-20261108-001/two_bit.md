# Two bits per tile: products of one-bit decorations

Epic `TWO-BIT-20261108-001` (program topology), 2026-11-08. Closed first as a preliminary record (46bc5afcd); the stop rule's
forcing test on 12 surviving products, run as the stress test TWO-BIT-B1, is folded in below.

## The question

- **Where it comes from.** Backlog B8 of the goals doc (G1, question 9; A35), started at the coordinator's go-ahead on 2026-11-08:
  one hidden bit per tile, placed by a decorated substitution, never forces the pinwheel (`CRYSTAL-UP-20261108-001`). Can two?
- **The family.** Products of two one-bit decorations: a tile carries a pair of bits, and each bit is passed to the children by its
  own one-bit decoration. A product is one kind of two-bit decoration; the others are not tested here.
- **Stop rule, frozen at the start.** If a crystal in hand gets through every product, no product forces the pinwheel and the line
  pauses. If some products let none through, one bounded forcing test runs on them, and the line pauses after it whatever it shows.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Most products let a crystal through.** Of the 139,656 product classes (all ordered pairs up to exchanging the factors and relabelling either), 136,415 admit a crystal in hand with a periodic two-bit labelling: first on a domino-torus plane for 88,961, on a mixed-orientation crystal of `CRYSTAL-UP-20261108-001A` for 47,454. Each such escape is a crystal at every radius. | exploratory experiment | A |
| 2 | **3,241 let none of the crystals in hand through.** For 646 of them the two factors admit no common crystal, so no listed crystal can carry both bits; for the other 2,595 the factors share crystals but no joint labelling obeys the product's law on them. 321 distinct one-bit decorations occur as factors; 69 survivors have the last one-bit decoration, 10101 / 00110, or its relabelling as a factor. | exploratory experiment | A |
| 3 | **The forcing route stalls at its first step on all 12 survivors sampled.** Their parents' labels are forced, but arc consistency on the product's level-one collars leaves off-law parents in every one: 177 to 996 pinwheel collars with labels the law does not list, and 0 to 270 non-pinwheel collars. Torus searches from up to 20 of them for three products found no crystal (on two no seed grew a patch to read periods from). One product, 01101/10001 x 10001/00010, keeps no non-pinwheel parent, only label defects. | exploratory experiment | B1 (`TWO-BIT-20261108-001B-E003`) |

## Answer

Two bits per tile, as products of one-bit decorations, let a known crystal through in 97.7% of the classes, and 3,241 classes are
left that no crystal in hand gets through. Whether any of them forces the pinwheel is open: on a sample of 12, parent labels are
forced but local consistency leaves off-law parents, as it did for one bit, and the bounded torus searches found no crystal.

## Reading

**Interpretation, not a theorem.**
- **A second bit can exclude every known crystal.** One bit never could: every one of the 1,024 one-bit decorations admits a
  crystal. A product excludes a crystal whenever its two bits cannot be laid on it together, and 3,241 classes exclude all 37
  crystals tried.
- **The survivors are candidates, not results.** The crystals tried are those found so far, at two levels and on small tori; the
  last one-bit decoration resisted every domino crystal and fell to a new kind of crystal found one level up.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| One bit per tile never forces the pinwheel (`CRYSTAL-UP-20261108-001`) | Two bits, as products, against the same crystals (A) | 3,241 product classes let no crystal tried through |
| No crystal in hand gets through the 3,241 | Forced parents, arc consistency and torus searches on 12 of them (B1) | Parents forced; off-law parents survive arc consistency in all 12; no crystal found |

## Literature and provenance

- **Sources.** Decorated substitutions and matching rules (Mozes 1989; Radin 1994; Goodman-Strauss 1998), which force the pinwheel
  with enough labels and give no lower bound.
- **Classification.** The product census was not found in prior work (no-overlap-found).

## Workspace assumptions

- **Relied on.** A35 (hidden information counted as labels a decorated substitution sets; a product carries two bits), A33, A25.
- **Taken by default.** None new: the family, the crystals, the levels and the tori are ticket A's declared scope.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families: the census (A) and the forcing test on a sample (B1).
- **Administrative.** This note, the closure, two long-running registrations and two runs lost to memory.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — two bits per tile as products | **Status:** Inconclusive | 3,241 classes shut out every crystal tried; the forcing route stalls on a sample |
| Local direction — decorated substitutions on the pinwheel | Paused by the frozen stop rule | Resumes only on a sharper target |
| Broader exploration — G1 lines | Known alternatives | Edge labels (A35); hub chains (A39); dimension three |
| Long-term goal — G1 Space from a law (question 9) | No demonstrated advance | The price of roundness stays above one bit; two is open |

**Corrections:** one, not a block (the summaries' direction of "escape", 716140ec5). **Goals:** a G1 checkpoint (no demonstrated
advance); B8's products part taken. **Assumptions:** none added.

- **What is left open.** Whether any of the 3,241 products forces the pinwheel.
- **The sharpest candidate.** 01101/10001 x 10001/00010: arc consistency removes all its non-pinwheel parents, leaving only 209
  pinwheel collars with labels the law does not list.

**Next step:** Research directions — No next action selected. The coordinator parked all three on 2026-11-08 (backlog B15 to B17):
the stop rule resumes this line only on a sharper target, and the thread cap was reached.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The forcing route on the label-only survivor | 2/3 — Substantial | 2/3 — Testable | 01101/10001 x 10001/00010: the joint test and exhaustive extension on its 209 off-law pinwheel collars → all die (the first step of a proof that two bits force the pinwheel) or some survive | Alternative · deferred (B15) |
| 2 | Edge labels, as in Radin's rules (A35's challenge) | 2/3 — Substantial | 1/3 — Stated | An edge substitution with one bit per edge against the crystals in hand → one that excludes them all, or none | Alternative · deferred (B16) |
| 3 | Hub chains in two dimensions (A39's challenge) | 1/3 — Incremental | 2/3 — Testable | A plane of gated knots: chain balls' growth and circle shape → a hub shape, or the grid drawn in | Alternative · deferred (B17) |

1. **The label-only survivor.**
   - **Payoff 2.** If its 209 off-law pinwheel collars die under the joint test and extension, the first step of a forcing proof holds
     for a two-bit decoration, and the plane's price of roundness would be two bits per tile as a decorated substitution.
   - **Concreteness 2.** The vectorized arc consistency, the joint test and the extension test exist; the joint test and extension
     need the four-label law, a small change.
   - **Uncertainty.** Label defects need not die: for one bit, the off-law pinwheel collars survived as long as the others did.
   - **Status.** Parked as B15 on 2026-11-08: the coordinator judged it not the sharper target the stop rule asks for.
2. **Edge labels.** Tests whether the count depends on where the bits sit; the edge substitution must be defined first.
3. **Hub chains.** A hub network has a natural count, but the grid it lives on is drawn, so the payoff is small.

## Final report as sent

Sent to the owner on 2026-11-08 at 17:03 UTC and copied here verbatim.

Two bits per tile is closed and published (318f38a99). The line now pauses under its frozen stop rule.

- **Census:** a known crystal gets through 136,415 of the 139,656 product classes, so those fail. No crystal we tried gets through the other 3,241.
- **Forcing test on 12 of the 3,241:** every parent's labels are forced, but local consistency leaves off-law parents in all 12, and the bounded torus searches found no crystal. One product, 01101/10001 × 10001/00010, has only label defects left; no geometric defects survive.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: two bits as products | **Status:** Inconclusive | 3,241 classes shut out every crystal tried; forcing stalls on a sample |
| Local direction: pinwheel decorations | Paused (stop rule) | resumes only on a sharper target |
| Broader: G1 lines | Known alternatives | edge labels, hub chains |
| G1 Space from a law | No demonstrated advance | the price of roundness stays above one bit; two is open |

**Corrections:** one, not a block (the summaries used "escape" backwards, 716140ec5). **Goals:** G1 checkpoint added. **Assumptions:** none added.

**Next step:** Research directions, selected #1

| # | Direction | Payoff | Concreteness | Status |
| --- | --- | --- | --- | --- |
| 1 | Forcing route on the label-only survivor (joint test and extension on its 209 off-law collars) | 2/3 | 2/3 | Selected · awaiting go-ahead |
| 2 | Edge labels, as in Radin's rules (A35) | 2/3 | 1/3 | Deferred |
| 3 | Hub chains in two dimensions (A39) | 1/3 | 2/3 | Deferred |

Operational note: the first forcing-test runs used about 59 GB and were killed by the out-of-memory killer, probably causing the earlier session restart. Heavy jobs now run under a 16 GB cap, and the final run stayed under 1 GB.
