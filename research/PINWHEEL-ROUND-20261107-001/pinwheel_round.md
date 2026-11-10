# Round without coins: the pinwheel law

Epic `PINWHEEL-ROUND-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner said "Yes, let's continue." to `LOGIC-CIRCLE-20261107-001`'s recommendation. That epic found round
  circles only where chance with no preferred direction is put in. Can a law with no coins have a round circle?
- **The candidate.** Conway and Radin's pinwheel tiling. One rule cuts the right triangle with legs 1:2 into five copies of
  itself, and its tiles turn through the irrational angle arctan(1/2).
- **The two doubts flagged before starting.**
  - Whether a rule with a built-in irrational angle counts as nothing drawn.
  - Whether this is already known.
- **Question served.** Question 9 (space from a law).

## What was already known

- **Radin and Sadun** (Comm. Math. Phys. 177, 1996) proved that in a pinwheel tiling the shortest path along tile edges between
  points R apart has Euclidean length R + o(R). The pinwheel's length-weighted edge metric is large-scale Euclidean, with no rate.
- **Radin** (1993, 1994) proved that the pinwheel system is uniquely ergodic under translations, has complete rotational symmetry,
  and is forced by local matching rules.
- **What that leaves open.** "Round without coins" was known for lengths. Open were the program's own distance, bond distance,
  which counts distinctions and uses no lengths, and what in the rule produces the roundness.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **An isotropy principle.** Suppose a space of plane tilings with finite local complexity is rotation-invariant and uniquely ergodic under translations. Then every rigid-motion-covariant bond distance with linear bounds has, for almost every tiling, one limit per unit distance in all directions: its circle is round. | proved (standard ergodic argument) | A |
| 2 | **The pinwheel's laws are round.** Both parity laws on the pinwheel (knots at tile corners; knots on tiles) have exactly round circles. The distance counts distinctions and uses no lengths. | proved, citing Radin | A |
| 3 | **Roundness needs both ingredients.** Two cuts of the same family keep polygonal or non-round circles, so roundness needs an irrational angle (arctan(1/2), by Niven) and tiles of both handednesses. | proved; consistent cut measured | A, B |
| | — The 1:1 triangle's substitution has a rational angle (π/4). It is the periodic tetrakis triangulation, with an octagon (π = 10/3) and a square (π = 4). | | |
| | — The same 1:2 triangle cut frame-consistently into the same five copies keeps one frame and four orientations. Its measured circle keeps a growing four-fold component. | | |
| 4 | **Roundness is a large-scale trend.** A disc of radius R meets O(log R) orientations (28 at R = 128), so at every finite scale the pinwheel is like a polygon with logarithmically many sides. | proved; measured | A, B |
| 5 | **Measured.** The pinwheel corner law's anisotropy falls from 1.106 to 1.030 between R = 8 and 128, and its four-fold harmonic almost vanishes. The tile law falls from 1.33 to 1.08. The 1:1 laws sit on their exact polygons. | exploratory experiment | B |

## Answer

- **Yes: a law with no coins can have a round circle.** The parity law on the pinwheel tiling is one. It needs no chance and no
  Poisson points, only one rule applied at every scale.
- **Its roundness comes from two things together.**
  - **A ratio that continues.** The angle arctan(1/2) is not a rational part of a turn.
  - **Turning against each other.** Sibling tiles come in mirror pairs, so their descendants turn opposite ways and the
    orientations multiply.
  - **Either alone fails.** The 1:1 triangle mirrors but turns by a rational angle: it closes into a periodic polygon world. The
    frame-consistent 1:2 cut turns by the irrational angle but all tiles turn together: one frame, no roundness.
- **The circle is round only as a trend.** At radius R the law has met about log R directions. Exact roundness is a limit, never a
  finite state.

## Literature and provenance

- **Ticket A.**
  - **Sources.** Radin and Sadun (1996); Radin (1993, 1994); unique ergodicity reproved for compact-alphabet substitutions
    (arXiv:2204.07516); Sadun's generalized pinwheels (1998); slack isometry (Benjamini); rates for related constructions (Cai and
    Chen, arXiv:2507.23105); isotropy arguments (Vahidi-Asl and Wierman).
  - **Folklore risk.** High for the isotropy principle. Low to moderate for bond distance on the pinwheel and the
    two-ingredient contrast.
- **Ticket B.**
  - **What it measures.** The rate at accessible radii and the contrast, with exact bond distances.
  - **The solver.** A faster exact least-cycle solver replaced the original one after validation; a 32-bit overflow it had on
    large graphs was caught and fixed before the reported run (see the interpretation).
- **Where the ideas came from.** The candidate came from the previous epic's recommendation. The frame-consistent control turned
  up by accident: the first implementation of the pinwheel cut was frame-consistent and gave only four orientations.

## Reading

**Interpretation, not a theorem.**
- **Harmony and continuing ratio, in one rule.** "Cut a right triangle into copies of itself" makes a harmony or a continuing
  ratio depending only on the triangle.
  - **Legs 1:1.** The angle is a rational part of a turn, and the world closes into a periodic pattern whose circle is a polygon
    with rational π.
  - **Legs 1:2.** The angle continues forever, and the circle becomes round.
- **The circle as a trend.** This matches the owner's earlier view that perfect circles are trends, not things: the pinwheel's
  circle is round only in the limit, gaining directions logarithmically.
- **The intrinsic reading.** Bond distance depends only on the law: which distinctions share knots. The theorem says the law's own
  metric is large-scale Euclidean in every direction. The drawing is used to prove it, not to state it.
- **The remaining doubt.** Whether the pinwheel's rule itself can be stated with nothing drawn. The rule cuts triangles, which are
  geometric objects.

## Workspace assumption challenged

- **"Roundness needs chance or a drawn isotropic input."** The previous epic found roundness only with isotropic randomness. A
  deterministic substitution rule also makes it, as a trend.
- **"An irrational angle suffices."** It does not: the frame-consistent cut has one and stays non-round.

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
| Current attempt — round without coins | **Status:** Successful | The pinwheel's parity laws have exactly round circles (proved, citing Radin). Roundness needs an irrational angle and mirror pairs, and appears as a logarithmic trend (proved; measured). Unresolved: a rate, and whether the rule can be stated with nothing drawn. |
| Local direction — substitution tilings | Practically exhausted for this question | Both ingredients and both failures are identified. Further tilings would change constants, not the mechanism. |
| Broader exploration — question 9 | Line, plane, circles and a coin-free round circle mapped | Line grown natively, plane as a product, circles polygonal for periodic laws, round with isotropic chance or with the pinwheel's turning. Unmapped: a law that grows the pinwheel with no coordinates. |
| Long-term goal — space from logic | Capability gained | A deterministic rule yields a law whose own distance is large-scale Euclidean. The bridge still missing is a coordinate-free statement of the rule. |
| Next recommendation — the pinwheel grown with nothing drawn | **Next step:** Continue, as a fresh epic. Write the pinwheel substitution as a rule on knots and their shared distinctions, with labels but no coordinates: each three-place tile knot splits into five, and each boundary segment carries how it is subdivided. Check that it regrows the pinwheel's law exactly, up to isomorphism, at levels 1 to 7. Then the round circle is derived from a logical rule. | It settles this epic's remaining doubt. Bond distance depends only on the law's graph, so a coordinate-free rule would make the Euclidean large-scale geometry intrinsic. It moves question 9 and the owner's "ratio that continues". |
| Interest — that recommendation | **Payoff 2/3 — Substantial · Concreteness 2/3 — Testable** | **Payoff.** It would remove the last drawn ingredient from a round logical space. **Concreteness.** The question is precise, the first discriminator is an isomorphism check against the geometric construction already built, and matching-rule constructions for substitution tilings suggest such rules exist. **Main uncertainty.** The non-edge-to-edge bookkeeping, and whether the rule can read only the law's allowed states rather than labels. |
| Execution — that action | Deferred to the owner | **Not started.** **Stop when** the combinatorial rule reproduces the level-7 law up to isomorphism, or when a level is found that no labelling of a bounded alphabet regrows (an obstruction). **Alternatives:** the spectrum of rational π among periodic laws (Payoff 1/3 — Incremental · Concreteness 3/3 — Ready); a proved rate for the pinwheel's rounding (Payoff 1/3 — Incremental · Concreteness 1/3 — Stated). |

## Final report as sent

Sent to the owner on 2026-11-08 at 01:11 UTC and copied here verbatim.

I've finished and published the pinwheel epic. A law with no coins can have a round circle, but most of that answer was already known, so here is what's new on top of it.

**What was already known.** You flagged that this might be. Radin and Sadun proved in 1996 that on Conway and Radin's pinwheel tiling, the shortest path along tile edges between points R apart has length R + o(R). That is roundness for a distance that adds up Euclidean edge lengths. So I narrowed the epic to what remained open.

**What's new:**
- **The program's own distance is round** (proved, relying on Radin's published facts about the pinwheel). Bond distance counts distinctions and uses no lengths, so their result doesn't cover it. The proof is a general principle: if a family of tilings looks the same in every rotation and its translations are uniquely ergodic, then any distance defined the same way everywhere is round. It holds with knots at tile corners and with knots on tiles.
- **Roundness needs two things together:**

| Same rule: cut a right triangle into copies of itself | Angle | Tiles turn against each other? | Circle |
| --- | --- | --- | --- |
| Legs 1:1 | π/4, a whole fraction of a turn | yes | periodic tiling; polygons with π = 10/3 and 4 (proved) |
| Legs 1:2, cut so all tiles keep one frame | arctan(½), irrational | no | not round: 4 directions forever, and the measured 4-fold component grows |
| Legs 1:2, the pinwheel cut | arctan(½) | yes: mirror-image sibling tiles turn opposite ways | round (proved) |

- **It is round only as a trend** (proved and measured). A disc of radius R contains about log R tile directions, 28 at R = 128. The corner law's lopsidedness falls slowly, from 1.106 to 1.030 between R = 8 and 128.

**Against your intuition** (a reading, not a proof): one rule gives a harmony or a ratio that continues depending only on the triangle. With legs 1:1 it closes into a periodic world with polygon circles. With legs 1:2 it continues, and the circle becomes round only in the limit, which fits your view that perfect circles are trends rather than things.

**What remains drawn.** Bond distance depends only on which distinctions share knots, so the roundness is a property of the law's own distance. But the pinwheel rule itself cuts geometric triangles.

**Measurements** (exact bond distances, 188 s):
- The 1:1 controls sit on their exact polygons.
- The pinwheel tile law falls from 1.33 to 1.08, which is still above the threshold I froze in advance, so it's formally unresolved.
- The frame-consistent cut fails the "rounding" test, though by its fixed rule it is unresolved rather than shown to stall.
- The first fast solver had an integer overflow on large graphs. I caught and fixed it before the reported run, and the solver matches the original one exactly.

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: round without coins | **Successful** | The pinwheel laws are round; the two ingredients and the slow trend are identified. Still open: a rate, and a coordinate-free rule. |
| Local direction: substitution tilings | Practically exhausted for this question | More tilings would change constants, not the mechanism. |
| Long-term goal: space from logic | Capability gained | A deterministic rule yields a law whose own distance is round at large scale. |
| Next recommendation | **Continue**, as a fresh epic: the pinwheel grown with nothing drawn | Write the pinwheel cut as a rule on knots and their shared distinctions, with labels but no coordinates, and check that it regrows the same law exactly at levels 1–7. |
| Interest | **Payoff 2/3 — Substantial · Concreteness 2/3 — Testable** | It would remove the last drawn ingredient from a round logical space. Main uncertainty: tiles here don't meet edge to edge, which complicates the bookkeeping, and the rule may need labels rather than allowed states alone. |
| Execution | Waiting for your go-ahead | Alternatives: which fractions periodic laws realize as π (Payoff 1/3 · Concreteness 3/3); a proved rate for the rounding (Payoff 1/3 · Concreteness 1/3). |

**Still waiting on you, carried from earlier epics:**
- whether a native knot must also be natively bound;
- the PHASE-HALO and FACE-CLAIM qualifications;
- the SELECTION-NOTE erratum;
- superseding KNOT-COMPOSE D001;
- counted length as a native magnitude.

The epic added two discovery records, so the generated discoveries index needs a maintenance rebuild. knotlab's tests and the jscul.dev sync both passed.
- [Decision note](https://github.com/jscul/knotlab/blob/main/research/PINWHEEL-ROUND-20261107-001/pinwheel_round.md)
- [Proof](https://github.com/jscul/knotlab/tree/main/proofs/PINWHEEL-ROUND-20261107-001A/PINWHEEL-ROUND-20261107-001A-P001_isotropy_makes_circles_round)
- [Measurements](https://github.com/jscul/knotlab/blob/main/artifacts/PINWHEEL-ROUND-20261107-001B/PINWHEEL-ROUND-20261107-001B-E001_measured_substitution_circles/run/interpretation.md)
- [jscul.dev/proofs](https://jscul.dev/proofs)

Sources:
- **Radin & Sadun 1996** (edge paths have length R + o(R)): [preprint listing](https://web.ma.utexas.edu/mp_arc-bin/mpa?yn=95-37), [record](https://portal.mardi4nfdi.de/wiki/Publication:1918096)
- **Radin 1993** (unique ergodicity, rotational symmetry): [arXiv math/9310234](https://arxiv.org/abs/math/9310234)
- **Unique ergodicity reproved:** [arXiv 2204.07516](https://arxiv.org/pdf/2204.07516)
- **The pinwheel tiling:** [Wikipedia](https://en.wikipedia.org/wiki/Pinwheel_tiling), [Tilings Encyclopedia](https://tilings.math.uni-bielefeld.de/substitution/pinwheel/)
- **Sadun's generalized pinwheels:** [arXiv math/9712263](https://arxiv.org/abs/math/9712263)
- **Benjamini on graph versus Euclidean metrics:** [note](https://www.wisdom.weizmann.ac.il/~itai/erd100.pdf)
- **Rates for related constructions:** [The Squishy Grid Problem](https://arxiv.org/abs/2507.23105)
