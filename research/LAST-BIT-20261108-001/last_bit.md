# The last one-bit decoration of the pinwheel

Epic `LAST-BIT-20261108-001` (program topology), 2026-11-08.

## The question

- **Where it comes from.** The selected next step of `ONE-BIT-20261108-001`, started at the coordinator's go-ahead on 2026-11-08
  (G1; A25, A35): deeper crystals first, then a forcing test on geometry alone.
- **The decoration.** s(0) = 1 0 1 0 1, s(1) = 0 0 1 1 0, with its relabelling: the only one of the 1,024 one-bit decorated
  substitutions of the pinwheel that no crystal tried has escaped. Its parent labels are forced.
- **The question.** Does it force the pinwheel? A yes would make one hidden bit per tile the plane's price of roundness.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **No deeper domino crystals exist.** Of the 5,376 collar types of the 96,416 domino tilings of tori up to 4 × 4, 82 are in the level-one law, 54 cut into it, and none needs exactly three cuts. So the family has no crystal legal only after three cuts, and the crystal search for this decoration is exhausted in it. | exploratory experiment | A |
| 2 | **The forcing proof stalls at its first step.** Parent labels are forced, but 153 labelled parent collars that are not pinwheel collars survive the joint consistency test and exhaustive extension to tile distance 2, and 15 of 16 sampled survive distance 3. | proved (exact) | B |

## Answer

The decoration is still open. No crystal in the domino-torus family escapes it at any number of cuts, and no local argument tried so
far shows that it forces the pinwheel: non-pinwheel parent collars sit inside consistent labelled patches reaching about seven
tiles out at the level of the plane.

## Reading

**Interpretation, not a theorem.**
- **Two ways it can end.** Either some plane obeys the law while its parents break the collar law somewhere, and the decoration fails
  (most likely through a crystal outside the domino family, whose seams survive one cut more), or the off-pinwheel parents die at a
  distance larger than three, and a longer version of this argument proves that one bit per tile forces the pinwheel.
- **The domino family is closed.** Its crystals are legal after one or two cuts or never, so a new escape needs another family:
  larger tori, or tilings not built from 1 × 2 rectangles.

## Stress test

The epic's tests are themselves one size past `ONE-BIT-20261108-001`: one more cut (A) and one more radius of consistency (B).

| Claim | One size past | Result |
| --- | --- | --- |
| The decoration escapes the domino crystals legal within two cuts (`ONE-BIT-20261108-001B`) | Three cuts (A) | No crystal of the family is legal only after three cuts; holds |
| Joint consistency leaves non-pinwheel parent collars (`ONE-BIT-20261108-001A`) | Extension to distance 2, and 3 on a sample (B) | 153 still survive at 2, 15 of 16 at 3; holds |

## Literature and provenance

- **Sources.** Decorated matching rules (Radin 1994; Mozes 1989; Goodman-Strauss 1998); deceptions and exhaustive extension in
  tiling searches (Dworkin and Shieh 1995).
- **Classification.** The methods are known (known-with-delta); the decoration and its open status were not found in prior work.

## Workspace assumptions

- **Relied on.** A35, A33, A25.
- **Taken by default.** None new: the family, the depths and the budgets are the tickets' declared scopes.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families (A, B).
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
| This attempt — settle the last decoration | **Status:** Inconclusive | No crystal found; the forcing proof stalls |
| Local direction — one-bit decorated laws | Unresolved | One open case; both tools reached their limits |
| Broader exploration — G1 lines | Known alternatives | Two bits (B8); edge labels; spheres; growth |
| Long-term goal — G1 Space from a law (question 9) | No demonstrated advance | The open case stays open |

**Corrections:** none. **Goals:** a G1 checkpoint (no demonstrated advance); the open case is recorded under G1; no goal change.
**Assumptions:** none added.

- **What is left open.** Whether s = 10101 / 00110 forces the pinwheel.
- **The local direction.** Both tools reached a limit, not a verdict. The next step that could change it is a search for a crystal
  among tilings built from the surviving parent collars themselves.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A crystal built from the survivors (G1) | 2/3 — Substantial | 2/3 — Testable | Periodic parent tilings on tori whose labelled collars all lie among the 153 + 360 survivors, at least one off-pinwheel → an escape for the last decoration, or none up to a declared torus size | Selected · awaiting go-ahead |
| 2 | Extension to distance 4 on all survivors | 1/3 — Incremental | 3/3 — Ready | The same test one distance further, in the background → all off-pinwheel parents die (the first step of a proof), or some survive | Alternative · deferred |
| 3 | Pause the one-bit line; return to G1's other lines | 1/3 — Incremental | 3/3 — Ready | Record the open case; take up two bits (B8) or edge labels only on demand | Alternative · deferred |

1. **A crystal built from the survivors.**
   - **Payoff 2.** An escape would close the one-bit question (one bit per tile never forces the pinwheel as a decorated
     substitution); none, at a declared size, would make the forcing proof the remaining route.
   - **Concreteness 2.** The surviving labelled collars and their compatibilities are computed; a torus search over them at the
     parent level is the same SAT problem as before, one level up.
   - **Uncertainty.** The torus sizes needed.
   - **Status.** Bound: one epic. Not started: the coordinator decides.
2. **Distance 4.** It would show whether the defects die; it is ready but slow (hours in the background).
3. **Pause.** The program's G1 question has its main answer from this line already: roundness in the plane costs non-local hidden
   information, and one bit per tile almost never suffices.
