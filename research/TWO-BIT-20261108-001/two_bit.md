# Two bits per tile: products of one-bit decorations

Epic `TWO-BIT-20261108-001` (program topology), 2026-11-08. **Preliminary record: stress test pending** (the stop rule's forcing
test on 12 surviving products runs in the background as TWO-BIT-B1 and is folded in when it finishes).

## The question

- **Where it comes from.** Backlog B8 of the goals doc (G1, question 9; A35), started at the coordinator's go-ahead on 2026-11-08:
  one hidden bit per tile, placed by a decorated substitution, never forces the pinwheel (`CRYSTAL-UP-20261108-001`). Can two?
- **The family.** Products of two one-bit decorations: a tile carries a pair of bits, and each bit is passed to the children by its
  own one-bit decoration. A product is one kind of two-bit decoration; the others are not tested here.
- **Stop rule, frozen at the start.** If every product escapes a crystal in hand, no product forces the pinwheel and the line pauses.
  If some escape none, one bounded forcing test runs on them, and the line pauses after it whatever it shows.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Most products escape.** Of the 139,656 product classes (all ordered pairs up to exchanging the factors and relabelling either), 136,415 admit a crystal in hand with a periodic two-bit labelling: first on a domino-torus plane for 88,961, on a mixed-orientation crystal of `CRYSTAL-UP-20261108-001A` for 47,454. Each such escape is a crystal at every radius. | exploratory experiment | A |
| 2 | **3,241 escape none of the crystals in hand.** For 646 of them the two factors admit no common crystal, so no listed crystal can carry both bits; for the other 2,595 the factors share crystals but no joint labelling obeys the product's law on them. 321 distinct one-bit decorations occur as factors; 69 survivors have the last one-bit decoration, 10101 / 00110, or its relabelling as a factor. | exploratory experiment | A |
| 3 | **Stress test pending:** the stop rule's forcing test on 12 survivors drawn at random (forced parent labels, arc consistency on the product's level-one collars, torus searches from what is left). | exploratory experiment | B1, pending |

## Answer (preliminary)

Two bits per tile, as products of one-bit decorations, escape the known crystals in 97.7% of the classes, and 3,241 classes are
left that no crystal in hand admits. Whether any of them forces the pinwheel is open; the forcing test on a sample will say whether
local consistency removes their off-law parents or leaves them, as it did for one bit.

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
| One bit per tile never forces the pinwheel (`CRYSTAL-UP-20261108-001`) | Two bits, as products, against the same crystals (A) | 3,241 product classes escape every crystal tried |
| The 3,241 escape the crystals in hand | Forced parents, arc consistency and torus searches on 12 of them (B1) | Stress test pending |

## Literature and provenance

- **Sources.** Decorated substitutions and matching rules (Mozes 1989; Radin 1994; Goodman-Strauss 1998), which force the pinwheel
  with enough labels and give no lower bound.
- **Classification.** The product census was not found in prior work (no-overlap-found).

## Workspace assumptions

- **Relied on.** A35 (hidden information counted as labels a decorated substitution sets; a product carries two bits), A33, A25.
- **Taken by default.** None new: the family, the crystals, the levels and the tori are ticket A's declared scope.

## Ratio

Since the epic opened:
- **Substantive.** One evidence family (A); the forcing test pending.
- **Administrative.** This note, the closure and two long-running registrations.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — two bits per tile as products | **Status:** Inconclusive | 3,241 classes escape every crystal tried; forcing test pending |
| Local direction — decorated substitutions on the pinwheel | Paused by the frozen stop rule | Resumes only on the forcing test's say |
| Broader exploration — G1 lines | Known alternatives | Edge labels (A35); hub chains; dimension three |
| Long-term goal — G1 Space from a law (question 9) | No demonstrated advance | The price of roundness stays above one bit, and two is open |

**Corrections:** none. **Goals:** a G1 checkpoint (no demonstrated advance; preliminary); B8 taken. **Assumptions:** none added.

**Next step:** Research directions — No next action selected until the forcing test is folded in.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The survivors one level further (resume B8) | 2/3 — Substantial | 2/3 — Testable | The 3,241 at two more levels and on larger tori, then the forcing route on the rest → a product no crystal escapes and whose off-law parents die, or none | Alternative · deferred |
| 2 | Edge labels, as in Radin's rules (A35's challenge) | 2/3 — Substantial | 1/3 — Stated | An edge substitution with one bit per edge against the crystals in hand → one that excludes them all, or none | Alternative · deferred |
| 3 | Hub chains in two dimensions | 1/3 — Incremental | 2/3 — Testable | A plane of gated knots: chain balls' growth and circle shape → a hub shape, or the grid drawn in | Alternative · deferred |
