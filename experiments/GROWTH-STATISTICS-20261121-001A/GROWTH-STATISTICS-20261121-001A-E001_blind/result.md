# Blind recognition at held-back meeting scales

The reader correctly called 6 of 12 roots and abstained on six. It identified the polygonal-limit control and bounded-bond source at all three roots each. It abstained on the cubic construction and round-limit source at all three roots each. The frozen whole-roster gate required at least two correct calls in each family and failed. The separate meeting-dimension read was correct at nine roots, wrong at one and inconclusive at two. The source crosswalk was opened after the calls were locked. [Scoring rule](../../../research/GROWTH-STATISTICS-20261121-001/blind_scoring.md) · [Locked calls](../../../research/GROWTH-STATISTICS-20261121-001/blind_calls.json) · [Scored rows](../../../research/GROWTH-STATISTICS-20261121-001/blind_score.json)

## Every call

The fitting range is 8–26 meeting steps. The local column gives matching knots over knots containing the root. An empty shape entry marks a main row outside the matched two-dimensional shape panel. The separate shape identifiers join to main identifiers through the released crosswalk.

| Source | Main ID | Exponent | Dimension call | Local match | Main call | Bond shape call | Meeting shape call | Combined |
| --- | --- | ---: | --- | ---: | --- | --- | --- | --- |
| Cubic | `f85ca18aaf3cca56` | 2.237 | 2, wrong | 2/2 | Abstained | — | — | Abstained |
| Cubic | `de62055b185ab2d1` | 2.349 | Abstained | 0/2 | Abstained | — | — | Abstained |
| Cubic | `95c4aba99506aec4` | 2.574 | Abstained | 0/2 | Abstained | — | — | Abstained |
| Pinwheel | `65f7e6a4e4d0fdae` | 2.140 | 2, correct | 0/2 | Abstained | Abstained | Abstained | Abstained |
| Pinwheel | `498a74c599ae1a1e` | 2.056 | 2, correct | 0/2 | Abstained | Abstained | Round-limit candidate | Abstained |
| Pinwheel | `0d2a158a0e2e1e54` | 2.054 | 2, correct | 0/2 | Abstained | Abstained | Round-limit candidate | Abstained |
| Periodic control | `16e43a57145fe3d8` | 1.927 | 2, correct | 0/2 | Abstained | Polygonal-limit candidate | Abstained | Correct |
| Periodic control | `4f1a0f7a5b813704` | 1.927 | 2, correct | 0/2 | Abstained | Polygonal-limit candidate | Abstained | Correct |
| Periodic control | `e645185ba97125b2` | 1.938 | 2, correct | 0/2 | Abstained | Polygonal-limit candidate | Abstained | Correct |
| Bounded-bond | `2156c3aa62396914` | 1.952 | 2, correct | 0/6 | Bounded-bond candidate | — | — | Correct |
| Bounded-bond | `53af764ec93ed825` | 1.952 | 2, correct | 0/6 | Bounded-bond candidate | — | — | Correct |
| Bounded-bond | `2166c293949d47c7` | 1.952 | 2, correct | 0/6 | Bounded-bond candidate | — | — | Correct |

| Shape ID | Source | Bond shape | Meeting shape | Largest late bond Ptolemy residual | Late relative bond fit error |
| --- | --- | --- | --- | ---: | ---: |
| `56a907b9aa7c7b0c` | Pinwheel | Abstained | Abstained | 0.000 | 0.063 |
| `fad08087825f1066` | Pinwheel | Abstained | Round-limit candidate | 0.020 | 0.076 |
| `01bc1fbaa2c75e31` | Pinwheel | Abstained | Round-limit candidate | 0.046 | 0.067 |
| `ea3f819a777880dc` | Periodic control | Polygonal-limit candidate | Abstained | 0.347 | 0.097 |
| `c8cd9fdab67001f7` | Periodic control | Polygonal-limit candidate | Abstained | 0.328 | 0.103 |
| `b1275e608f1fab47` | Periodic control | Polygonal-limit candidate | Abstained | 0.369 | 0.116 |

All shape matrices passed their no-exit certificates and all 18 scales per channel were available. The pinwheel met both Ptolemy ceilings on both final scales at all three roots. Its relative two-dimensional bond fit errors exceeded 0.055 at both scales, which explains the three abstentions. The periodic control, the literature's tetrakis triangulation with the tile parity law, retained four-distinction violations at all three roots. Swapping meeting steps into the same shape rule produced two correct calls and four abstentions. The primary bond shape rule produced three correct calls and three abstentions. Each channel gives finite evidence about the known reference. [Anonymous packet](../../../artifacts/GROWTH-STATISTICS-20261121-001A/GROWTH-STATISTICS-20261121-001A-E001_blind/run/packet.json) · [Matrix observations](../../../artifacts/GROWTH-STATISTICS-20261121-001A/GROWTH-STATISTICS-20261121-001A-E001_blind/run/summary.json)

## Fixed bond size across meeting steps

Each entry gives verified witnesses over all distinctions in that meeting shell. Each queried pair's allowed support used the endpoints and up to two of their one-step meeting neighbors. A zero means zero verified witnesses under that search. The bounded-bond roots had 34, 34, 30 and 62 unresolved queries at successive radii per root. The other sources' declared candidate searches resolved without missing queries. The ten repeated bounded-bond witnesses are finite checks across the held-back scales. The archived proof establishes these witnesses for arbitrarily many meeting steps. [Crosswalk and attempts](../../../artifacts/GROWTH-STATISTICS-20261121-001A/GROWTH-STATISTICS-20261121-001A-E001_blind/run/custody/measurements.json) · [Every-step proof](../../../proofs/FOLD-20261112-001A/FOLD-20261112-001A-P001_folded_direction/proof.md)

| Main ID | 8 steps | 12 steps | 18 steps | 26 steps |
| --- | ---: | ---: | ---: | ---: |
| `f85ca18aaf3cca56` | 0/621 | 0/998 | 0/1552 | 0/2500 |
| `de62055b185ab2d1` | 0/307 | 0/529 | 0/952 | 0/1684 |
| `95c4aba99506aec4` | 0/354 | 0/694 | 0/1382 | 0/2438 |
| `65f7e6a4e4d0fdae` | 0/43 | 0/73 | 0/108 | 0/192 |
| `498a74c599ae1a1e` | 0/52 | 0/80 | 0/134 | 0/188 |
| `0d2a158a0e2e1e54` | 0/49 | 0/86 | 0/131 | 0/190 |
| `16e43a57145fe3d8` | 0/32 | 0/46 | 0/70 | 0/104 |
| `4f1a0f7a5b813704` | 0/32 | 0/46 | 0/70 | 0/104 |
| `e645185ba97125b2` | 0/29 | 0/47 | 0/73 | 0/103 |
| `2156c3aa62396914` | 10/110 | 10/166 | 10/250 | 10/362 |
| `53af764ec93ed825` | 10/110 | 10/166 | 10/250 | 10/362 |
| `2166c293949d47c7` | 10/110 | 10/166 | 10/250 | 10/362 |

## Limits and checks

The three roots in each source are correlated. The bounded-bond source's roots are translates in its infinite law, and the finite query ledger reused translation-equivalent support checks. The 495 four-distinction sets from each twelve-distinction sample share distinctions. The exact results describe this roster under equal family and root weight.

For the cubic construction, a post-lock reconstruction measured steps to its three genuine one-sided boundaries. They were `[7,6,3]`, `[4,0,3]` and `[3,17,0]` in table order. The unfinished-assembly boundaries were 34, 43 and 30 steps away. All measured meeting balls were complete. Even the root that matched the local arrangement at both knots reached all three genuine boundaries by the first radius. Boundary distances make the finite slope sensitive to root choice. The source theorem establishes cubic bond-ball growth, which the finite meeting-volume fit addresses only indirectly. [Source theorem](../../../proofs/CUBIC-FROM-A-KNOT-20261117-001/CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth/proof.md)

As a retrospective control, a breadth-first count on the two-sided three-order meeting pattern gave 2,433, 7,777, 25,273 and 74,361 distinctions at the same four scales, an exponent of 2.901. The fractions retained by the observed roots fell from 88% to 40%, 47% to 25%, and 51% to 35%. Those decreases account for the departures from the control slope over this range. The control did not enter the blind score.

The sealed run took 275.84 seconds wall time and 275.78 seconds CPU, with maximum RSS of 827,164 KiB and exit status zero. Held-back counting began after the R1 review. The draw's seed matches the published SHA-256 commitment. The full-packet SHA-256 is `149a39cb3a4f34bf6c827b6572cc4888cce1cbd5a7158f4285b6460b8927dbde`. The independent reader's calls were locked at `5a1e7ae14e1e4780478b8fb37273dabc1b2a43c88e4a521821615a16f9cfc0b9`. [Run receipt](../../../artifacts/GROWTH-STATISTICS-20261121-001A/GROWTH-STATISTICS-20261121-001A-E001_blind/sealed.time) · [Seed commitment](../../../artifacts/GROWTH-STATISTICS-20261121-001A/GROWTH-STATISTICS-20261121-001A-E001_blind/draw/commitment.json) · [Run review](../../../research/GROWTH-STATISTICS-20261121-001/R1/A/red_team_report.json)

After call lock, the same producer and seed recreated the anonymous packet and summary byte for byte. All twelve rooted crosswalk and certificate records also matched after removing measurements of run time. The replay took 283.15 seconds wall time and 283.09 seconds CPU, with maximum RSS of 827,240 KiB. Scoring again from the locked calls and released crosswalk reproduced the original scored ledger byte for byte. [Replay receipt](../../../artifacts/GROWTH-STATISTICS-20261121-001A/GROWTH-STATISTICS-20261121-001A-E001_blind/replay_receipt.json)

The separate review re-derived every main and shape call and the 120 positive certificate records. It cleared the finite mixed outcome for reporting, including the failed whole-roster criterion. [Independent review](../../../research/GROWTH-STATISTICS-20261121-001/R2/A/red_team_report.json)

## Position and directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — four-source blind recognition | **Status:** Partially successful | Two of four families met the frozen criterion |
| Local direction — finite rooted readings | Unresolved | Cubic slopes and round bond fits abstained |
| Broader exploration — intrinsic shape tests | Known alternatives | Meeting steps and bond distance gave different calls |
| Long-term goal — G1 Space from a law | Capability gained | Two intrinsic signatures had correct blind calls |

**Next step:** Research directions — No next action selected

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Compare root choices in cubic growth | 2/3 — Substantial | 2/3 — Testable | Read counts at several genuine boundary depths → isolate their slope effect | Alternative · deferred |
| 2 | Compare intrinsic finite shape readings | 2/3 — Substantial | 2/3 — Testable | Apply the same pair selection rule at larger certified scales → compare the two fit errors | Alternative · deferred |

Different positions relative to a genuine boundary are the cheapest way to check what drove the cubic slope. The discrepancy between meeting and bond fit errors suggests a direct same-root comparison at larger fixed radii. Its main uncertainty is the size needed for a decision.

**STOP** at the registered roster. The checks cover the four selected source laws and the stated radii. A follow-on would need a separately frozen root or scale design.

**Corrections:** None to earlier research claims.

**Goals:** G1, finite intrinsic recognition from held-back measurements.

**Assumptions:** The readings depend on the declared scales, root weighting and finite tolerances.

**Scaffolds:** Finite source windows, randomized root draws and fixed scale thresholds.
