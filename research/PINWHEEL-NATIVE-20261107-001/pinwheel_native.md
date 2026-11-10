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
- **Where the irrational angle went.** It is nowhere in the rule, but the law carries it at large scale. Kenyon and Stephenson prove
  that the combinatorics alone recover the triangles: drawn conformally, which fixes the picture up to similarity, clusters of tiles
  converge in shape to the 1:2:√5 triangles (see the literature section).
  - **Correction (2026-11-08).** A first version said the angle appears only if the grown law is drawn self-similarly in the plane.

## Literature and provenance

- **Ticket A.**
  - **Sources.** Collared tiles and Anderson–Putnam complexes give finite combinatorial descriptions of substitution tilings. For the
    pinwheel, which does not force its border: Barge, Diamond, Hunton and Sadun (2010); Frettlöh, Whitehead and Whittaker (2014),
    whose complex has 138 edges.
  - **Nearest known result (found after closure).** Kenyon and Stephenson, "Shape convergence for aggregate tiles in conformal
    tilings" (Proc. Amer. Math. Soc. 147, 2019; arXiv:1703.04371), take the pinwheel as their running example.
    - **The rule.** Each tile becomes a combinatorial polygon with four designated corners, the fourth at the midpoint of the long
      leg, and Conway's cut becomes a combinatorial subdivision rule with no coordinates.
    - **The geometry returns.** In the conformal tilings drawn from the subdivided combinatorics, aggregate tiles converge in shape
      to the Euclidean tiles. In their words, "the combinatorics of the pinwheel knows about √5".
  - **Folklore risk.** High for the rule and the census: a coordinate-free pinwheel rule with four-cornered tiles is published, and
    four corners per tile is the census's point that T-junctions sit only at long-leg midpoints. What remains is the rule's form on
    a parity law's knots and distinctions, the explicit eleven-label alphabet and its exact check.
    - **Correction (2026-11-08).** This replaces a first rating of moderate, made before this source was found.
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
- **The owner's continuing ratio is not in the counts.** The eight kinds recur in fixed rational proportions, per knot: a 3/11,
  b 5/22, c 16/55, d 3/55, e 6/55, f 1/5, g 17/55, h 27/110.
  - **What the table does carry.** The only irrational number it shows is its growth rate √5, the factor by which each
    distinction's pieces multiply per level: the length scale, not the angle.
  - **Where the angle shows.** Not in the table or the counts, but in the law's large-scale shape: by Kenyon and Stephenson's
    theorem, the combinatorics alone recover the 1:2:√5 triangles in the limit. So the owner's continuing ratio is in the law as a
    limit, as its round circle is, and in no finite part of it.
  - **Correction.** This bullet replaces a first version that placed the continuing ratio in these proportions; they are rational.
  - **Second correction (2026-11-08).** "Where the angle shows" first said that the angle appears only when the law is drawn. The
    conformal drawing that recovers it is fixed by the combinatorics up to similarity.

## Workspace assumption challenged

- **"Roundness needs something drawn."** The circles epic found exact roundness only with an isotropic drawn input, and the pinwheel
  epic used a geometric rule. This epic removes the geometry: a finite local rule on the law alone grows a round logical plane, on
  the tested patches.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families changed conclusions: A (proof) and B (exploratory experiment).
- **Administrative.** This note and the closure.

## Correction record (2026-11-08)

Written after closure, when a later prior-work check found Kenyon and Stephenson (2019).
- **What was claimed.**
  - The eleven-label rule and its census of T-junctions were not found in prior work (folklore risk moderate).
  - The pinwheel's irrational angle "appears only if the grown law is drawn".
- **What was wrong.** Kenyon and Stephenson (Proc. Amer. Math. Soc. 147, 2019; arXiv:1703.04371) take the pinwheel as the running
  example of a coordinate-free subdivision rule.
  - **Their tiles.** Each tile has four designated corners, the fourth at the long leg's midpoint, which is the census's main point.
  - **Their theorem.** The combinatorics alone give the geometry back: aggregate tiles of the conformal tilings converge in shape to
    the Euclidean triangles.
- **Why it was missed.**
  - **The search.** The prior-work check covered tiling spaces (collared tiles, Anderson–Putnam complexes, cohomology) and one general
    query on whether combinatorics determines geometry. It did not reach conformal tilings, where that question is asked directly.
  - **The reading.** From "the angle is in neither the table nor the counts" it concluded "the angle is only in a drawing". It did
    not ask whether the combinatorics fix a drawing of their own.
- **What it changes.**
  - **Novelty.** Ticket A's novelty narrows to the rule's form on a parity law's knots and distinctions, the explicit eleven-label
    alphabet and its exact check. Whether to qualify the discovery record is listed under "Pending the owner".
  - **The angle.** The reading of where it lives reverses: it is a limit property of the law, like the round circle.
- **What it does not change.**
  - **The results.** Every proved or measured result stands: exact regrowth at levels 0–7, the census, the Whitney step and the
    radius-2 reading. The radius-2 reading is still not found in prior work.
  - **The answer.** The pinwheel law can be grown with nothing drawn. The cited theorem supports this: the rule needs no geometry,
    and the geometry comes back from it.
- **Block or not.** Not a block. It corrects a novelty claim and an interpretation, not the theory under test. It favours question
  9's "derived, not put in": a finite combinatorial rule fixes the irrational angle in the limit.
- **Lesson.** For "does the combinatorics determine X?", search conformal tilings (Bowers and Stephenson; Kenyon and Stephenson) and
  finite subdivision rules (Cannon, Floyd and Parry), not only tiling-space topology. Before saying "only in a drawing", ask
  whether the combinatorics fix a canonical drawing.

## Pending the owner

- **From this epic (2026-11-08).** Whether to qualify `PINWHEEL-NATIVE-20261107-001-D001` (significance `first_construction`):
  its rule is known in substance from Kenyon and Stephenson (2019); its form on knots and distinctions is not.
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

## Final report as sent

Sent to the owner on 2026-11-08 at 01:41 UTC and copied here verbatim.

I've finished and published the "pinwheel grown with nothing drawn" epic. The pinwheel law can be grown by a small symbolic rule with no coordinates, lengths or angles. On every patch I tested, that rule can read everything it needs from the law itself.

**The rule** (proved). Label each distinction by:
- the two knots' side types;
- where it sits along them;
- whether the two sides run the same way.

Only 11 labels ever occur: 8 inside the patch and 3 on its boundary. Each step:
- **Knots.** Every knot splits into five, whose handedness flips in a fixed pattern.
- **Distinctions.** Each splits by a letter table: a → g e d e g, b → h c c, c → b b, d → a, e → b, f → b, g → a, h → b.
- **Inside each knot**, five new distinctions appear, labelled f, g, c, a, h.

This regrows the law exactly at every level. It matches the geometric construction at levels 0–7, including all 133,883 distinctions at level 7. The pinwheel's distinctions therefore come in only eight kinds, and its only T-junctions sit at the midpoints of long legs.

**On the doubt you flagged** (measured, not proved). You asked whether the rule needs labels supplied from outside. On every tested patch it doesn't:
- **The law fixes its map.** Its graph is 3-connected, so by Whitney's theorem its allowed states determine its planar map up to a mirror image.
- **The map fixes the labels.** Every distinction's label is determined by its unlabelled neighbourhood of radius 2. There was no conflict among up to 235,394 cases at levels 5–7. Shuffled and non-local labellings conflict almost everywhere, so the test can fail.

So the step "split every knot, read each distinction's kind nearby, split it by the table" reads only the law, and it grows the law whose circle is round. This is shown on patches up to level 7, not proved for every pinwheel tiling.

**A correction to my own reading.** I first wrote that your "ratio that continues" lives in how often the eight kinds recur. I then computed those frequencies, and they are rational: per knot, a 3/11, b 5/22, c 16/55, d 3/55, e 6/55, f 1/5, g 17/55, h 27/110. The only irrational number in the table is its growth rate √5, which is the length scale, not the angle. The irrational angle appears only when the law is drawn; what the law itself shows of it is its round circle. I corrected the decision note and the intuition entry and republished.

**Prior work.** Finite combinatorial descriptions of the pinwheel substitution already exist in substance, via collared tiles and Anderson–Putnam complexes. What I didn't find: an explicit rule on knots and distinctions, the eight-kind census, or the radius-2 reading.

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: pinwheel grown with nothing drawn | **Successful** | Exact regrowth proved; labels readable from the law at radius 2 on tested patches. Open: radius 2 for every pinwheel tiling. |
| Broader: space from a law | A round plane grown by local subdivision | Still unmapped: growing a round plane outward from one knot, the way the number line grew. |
| Next recommendation | **Continue**, as a fresh epic: a round plane grown at its open ends. Start with "atlas growth": from one knot, add knots only where every nearby distinction keeps a radius-2 neighbourhood that the pinwheel law actually contains. Then see whether growth hits dead ends. | Your growth-at-open-ends epic found that no local rule grew a plane. A rule that grows the pinwheel plane outward would overturn that, and the plane would be round. |
| Interest | **Payoff 3/3 — Barrier · Concreteness 2/3 — Testable** | A precedent exists: Onoda and colleagues grew perfect Penrose tilings by forced local moves in 1988. Main doubt: whether forced moves exist at every step for the pinwheel. |
| Execution | Waiting for your go-ahead | Alternatives: prove radius 2 for every pinwheel tiling (Payoff 1/3 · Concreteness 3/3); which fractions periodic laws realize as π (Payoff 1/3 · Concreteness 3/3). |

**Still waiting on you, carried from earlier epics:**
- whether a native knot must also be natively bound;
- the PHASE-HALO and FACE-CLAIM qualifications;
- the SELECTION-NOTE erratum;
- superseding KNOT-COMPOSE D001;
- counted length as a native magnitude.

One new discovery record means the generated discoveries index needs a rebuild. knotlab's tests and the jscul.dev sync both passed.
- [Decision note](https://github.com/jscul/knotlab/blob/main/research/PINWHEEL-NATIVE-20261107-001/pinwheel_native.md)
- [Proof, with `rule_table.json`](https://github.com/jscul/knotlab/tree/main/proofs/PINWHEEL-NATIVE-20261107-001A/PINWHEEL-NATIVE-20261107-001A-P001_a_finite_rule_regrows_the_pinwheel)
- [Readability measurements](https://github.com/jscul/knotlab/blob/main/artifacts/PINWHEEL-NATIVE-20261107-001B/PINWHEEL-NATIVE-20261107-001B-E001_reading_labels_from_the_law/run/interpretation.md)
- [jscul.dev/proofs](https://jscul.dev/proofs)

Sources:
- **Collared tiles for the pinwheel:** [Barge, Diamond, Hunton, Sadun](https://arxiv.org/pdf/0811.2507)
- **The pinwheel's Anderson–Putnam complex:** [Frettlöh, Whitehead, Whittaker](https://arxiv.org/abs/1212.4401)
- **Combinatorial versions of geometric substitutions:** [topological substitution for the Rauzy fractal](https://arxiv.org/pdf/1603.02790)
- **Background:** [Substitution tiling](https://en.wikipedia.org/wiki/Substitution_tiling)
