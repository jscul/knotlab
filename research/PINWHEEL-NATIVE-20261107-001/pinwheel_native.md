# The pinwheel grown with nothing drawn

Epic `PINWHEEL-NATIVE-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner said "Yes, let's continue." to `PINWHEEL-ROUND-20261107-001`'s recommendation. That epic left one
  doubt: the pinwheel's rule cuts triangles, which are drawn.
- **The task.** Write the cut as a rule on knots and their shared distinctions, with labels but no coordinates. Check that it
  regrows the same law exactly.
- **The doubt flagged at the start.** Whether the rule needs labels from outside, or can read them from the law's allowed states.
- **Question served.** Question 9 (space from a law).

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **An eleven-label table regrows the pinwheel law exactly.** Label each distinction by its two knots' side types, where it sits along them, and whether they run the same way. Only eleven labels ever occur, eight inside the patch and three on its boundary. The table: every knot splits into five; every distinction splits as a → g e d e g, b → h c c, c → b b, d → a, e → b, f → b, g → a, h → b; five new distinctions f, g, c, a, h appear inside each knot. It regrows the tile law at every level. | proved (locality and induction; identical to the geometry at levels 0–7) | A |
| 2 | **The pinwheel's distinctions come in eight kinds.** Whole hypotenuse against whole hypotenuse (either way round); long leg against long leg; short leg against short leg; half a long leg against a short leg or against another half. Its only T-junctions are at midpoints of long legs. | proved | A |
| 3 | **The law determines its map.** The pinwheel law's graph is 3-connected at levels 2–5. By Whitney, the law's allowed states determine its planar map up to mirror image. | measured; Whitney cited | B |
| 4 | **The map determines the labels within radius 2.** At levels 5, 6 and 7, with up to 235,394 tested darts and 1,168 neighbourhood types, every distinction's label is a function of its unlabelled neighbourhood of radius 2. Shuffled and non-local labellings conflict on nearly every type. | exploratory experiment | B |

## Answer

- **The pinwheel law can be grown with nothing drawn.** One rule suffices: split every knot into five, read each distinction's kind
  from its neighbourhood of radius 2 in the law, and split it as an eleven-letter table says.
  - **No geometry.** The rule contains no coordinate, no length and no angle.
  - **What it grows.** It regrows the pinwheel law exactly, whose circle is round (`PINWHEEL-ROUND-20261107-001`).
- **On the doubt.**
  - **The labels are not extra.** On every tested patch they are written in the law itself, readable within radius 2.
  - **Proved and measured.** The regrowth is proved; the readability is measured on patches to level 7.
- **Where the irrational angle went.** It is nowhere in the rule. It appears only if the grown law is drawn self-similarly in the
  plane.

## Literature and provenance

- **Ticket A.**
  - **Sources.** Collared tiles and Anderson–Putnam complexes give finite combinatorial descriptions of substitution tilings. For the
    pinwheel, which does not force its border: Barge, Diamond, Hunton and Sadun (2010); Frettlöh, Whitehead and Whittaker (2014),
    whose complex has 138 edges.
  - **Folklore risk.** Moderate for the eleven-label rule and the census: they say what is known in substance, in the program's
    terms.
- **Ticket B.**
  - **Sources.** Whitney's theorems (a 3-connected graph is determined by its cycle matroid and has a unique planar embedding). Local
    recognizability of substitution tilings is classical in the geometric setting.
  - **Not found.** A combinatorial readability radius for the pinwheel.
  - **What the controls show.** That the test can fail.

## Reading

**Interpretation, not a theorem.**
- **What it does.** The rule reads only which distinctions share knots, nearby, and splits them. What it grows is a law whose own
  distance is round at large scale.
- **The two kinds of picture.** The drawing becomes one possible picture of the law, not an ingredient.
- **The owner's continuing ratio.** It lives in the law's combinatorics, in how often each of the eight kinds of distinction recurs
  as the rule repeats, not in a drawn angle.

## Workspace assumption challenged

- **"Roundness needs something drawn."** The circles epic found exact roundness only with an isotropic drawn input, and the pinwheel
  epic used a geometric rule. This epic removes the geometry: a finite local rule on the law alone grows a round logical plane, on
  the tested patches.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families changed conclusions: A (proof) and B (exploratory experiment).
- **Administrative.** This note and the closure.

## Pending the owner

- **Carried from `LOGIC-AXIS-20261107-001`.** Whether a native knot must also be natively bound
  (`research/LOGIC-AXIS-20261107-001/canonical_correction_request.md`).
- **Carried from earlier epics.**
  - Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Counted length as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the pinwheel grown with nothing drawn | **Status:** Successful | An eleven-label table regrows the law exactly (proved), and the law determines its own labels within radius 2 on patches to level 7 (measured). Unresolved: radius 2 for every pinwheel tiling. |
| Local direction — symbolic substitution of the pinwheel | Practically exhausted | The rule is minimal in form and verified. What remains is converting the readability evidence into a theorem, a bounded task. |
| Broader exploration — question 9 | A round plane grown by a local rule, by subdivision | The number line grows at open ends; the plane is a product; round circles come from isotropic chance or from the pinwheel's turning, now grown symbolically. Unmapped: growing a round plane outward from one knot, at open ends, as the line grew. |
| Long-term goal — space from logic | Capability gained | A finite local rule on the law alone produces a law with a round large-scale distance. The missing bridge is growth from a seed, rather than subdivision of a given triangle. |
| Next recommendation — a round plane grown at its open ends | **Next step:** Continue, as a fresh epic, starting with a scoping test. Atlas growth: from one knot, add knots one at a time where the law shows an open end. Allow a placement only if every distinction near it keeps a radius-2 neighbourhood that occurs in the pinwheel law's atlas (the 1,168 types of ticket B). Prefer placements that are forced. Does growth ever reach a dead end, and do the grown patches stay pinwheel patches? | `OPEN-END-GROWTH-20261107-001` found no local rule that grows a plane. A rule that grows the pinwheel plane outward would break that, with a round distance. A clean dead end is also informative. |
| Interest — that recommendation | **Payoff 3/3 — Barrier · Concreteness 2/3 — Testable** | **Payoff.** It would answer question 9's open part, a plane grown natively from one knot, and the plane would be round. **Concreteness.** The question is precise, the atlas exists, and Onoda, Steinhardt, DiVincenzo and Socolar (1988) grew perfect Penrose tilings by local forced-move rules from a seed. **Main uncertainty.** Whether forced moves exist at every step for the pinwheel, which has infinitely many orientations. |
| Execution — that action | Deferred to the owner | **Not started.** **Stop when** atlas growth either grows a patch of radius 30 without a dead end (then test that it is a pinwheel patch) or reaches a dead end that no radius up to 4 avoids. **Alternatives:** prove radius 2 for every pinwheel tiling (Payoff 1/3 — Incremental · Concreteness 3/3 — Ready); the spectrum of rational π among periodic laws (Payoff 1/3 — Incremental · Concreteness 3/3 — Ready). |
