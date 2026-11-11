# The count from growth

Epic `GROW-COUNT-20261111-001` (RULER-20261111-001 direction 2; G1, question 9; the challenge of A64), 2026-11-11, at the owner's
go-ahead ("Yes, let's continue it"). Pre-registered in commit 34610c9ff before any registered run. The canonical K1–K3 test is
unchanged.

## The question

- **Where it comes from.** The not-all-equal law (NAE) reads long-loop flat worlds of knots alone faithfully and measures them
  exactly (`LONG-LOOP-20261111-001`, `RULER-20261111-001`), but the count of how knots meet, two knots per co-knotted pair, one link
  per distinction, six knots per distinction, is put in, and a static faithful reading does not supply it (`NAE-SURFACE-20261111-001`).
- **The question.** Can growth supply it? A world grows from one knot; a knot proposed on a co-knotted pair is kept only while NAE
  still reads the world faithfully. Three rules name nothing (free), two per pair (open), or that and one link (disc); none names a
  degree. The clause law (OR), which accepts every legal move, runs beside it, so what OR grows is the growth order's part and what NAE
  changes is the law's.

## The question in standard terms

Grow a 3-uniform hypergraph one edge at a time, attaching each new edge along an existing pair, and keep an edge only while the
minimal non-shattered triples of the hypergraph's proper 2-colourings are exactly its edges with every pair shattered. Does the grown
hypergraph become a triangulated surface of degree 6?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Not two per pair (free).** In every run that grew past a tetrahedron (26 of 30) NAE accepted pairs in three or more knots, and pinched links. The other four closed into a tetrahedron within four knots and grew no further. | computed, exact per move, frozen | A |
| 2 | **Not one link (open).** With two per pair named, 17 of 30 runs grew pinched links; 13 closed into a tetrahedron and stopped. | computed, frozen | A |
| 3 | **Not the degree (disc).** With both named, closed distinctions took every degree from 3 to 14; no run had degree 6 at 90% or more, and no run closed into a flat surface. | computed, frozen | A |
| 4 | **The law's only part: no degree 3 inside a larger world.** NAE refused all 89 closings at degree 3 inside a world larger than a tetrahedron (its 24 accepted ones closed whole tetrahedra), 14 of 76 at degree 4, 5 of 37 at 5, 3 of 25 at 6, none of 24 at 7 or more. Compared with OR it moves closings from degree 3 to 4 and above: it disfavours sharp positive curvature, not non-flatness. | computed, frozen | A |
| 5 | **Why: adjacent apices.** No faithfully read world has a pair {p, q} in two knots {p, q, a}, {p, q, c} whose other corners are knotted together, {a, c, z} with z outside {p, q}: p = q = 0 forces a = c = 1 and so z = 0, which makes {p, q, z} a non-knot constraint, and if it were a knot p = q could not occur at all, a tie. A degree-3 closing in a connected world of more than four distinctions with every link a single path or cycle (the disc rule) always creates the configuration through a rim knot, so it fails; and every knot added on a pair of a tetrahedron does, so under growth the tetrahedron is a dead end. | proved after the run; refereed (exhaustive to 6 distinctions) | A |

## Answer

No. Faithful growth does not supply the count of how knots meet: wherever the world grows, NAE accepts pairs in three knots and
pinched links, and with both counts named it closes links at every degree from 3 to 14. Its one local preference, refusing degree 3
inside a larger world, comes from a short lemma (with the disc rule's single links), and it makes the tetrahedron a dead end
for growth, not the plane a target. The count must be
put in, as A64 reads it. P2, P3 and P4 held; P1 and P5 failed as worded, both only on worlds that closed into a tetrahedron. By the
stop rule the growth route for the count closes here.

## Reading

**Interpretation, not a theorem.**
- **What growth adds and what it does not.** In the board line growth from a seed supplied connectedness and the absence of a
  quotient (`GROW-FACE-20261110-001`). Here it supplies nothing about how knots meet: the law accepts almost every local shape the
  proposals offer.
- **The law forbids one local shape.** Two knots on a pair whose other corners are knotted together: a sharp cone. That is curvature
  at one point, not the count; flatness is never chosen, only the sharpest positive curvature refused, and only where links are
  single and the world connected.
- **For A64 and A63.** The count is an input under growth too. A63's conditional overturning (on A64) stands as it was: the face is
  the knot, and how faces meet is given.

## Lag cutoffs and census-only claims

- **No lag cutoff;** growth is read world by world, not as dynamics in time.
- **Exact.** Every faithfulness verdict (SAT, exact). **Census-only.** Conclusions 1 to 4 hold in the 180 frozen runs (80 knots at
  most); conclusion 5 is proved.

## Stress test

The decisive claims are existences (fins, pinches, degrees other than 6), so the check is an independent re-reading of witnesses
(`witness_check.py`, code apart from the frozen library): a free NAE world with pairs in three knots (37 distinctions, 80 knots) and an
open NAE world with a pinched link (40, 80) are read faithfully by a separate SAT encoding, and the tetrahedron lemma holds by brute
force for all six pairs. A corrected re-run of the whole design (`supplement.py`, below) gives the same verdicts and the same closing
tables.

## Review

An independent referee, a fresh agent, checked the two lemmas with its own exhaustive search (every world to 6 distinctions; 8,809
faithful knot sets at 6) and its own growth simulation (60 seeds per rule). No errors. Its findings, folded in:
1. **Lemma A is stronger than first stated:** the adjacent-apices configuration is never faithful at all (if {p, q, z} were a knot, p =
   q could not occur, a tie), with no cap on knots per pair needed. Conclusion 5 now says so.
2. **The tetrahedron is a dead end for growth, not for every added knot** (overclaim): knots {i, new, new} keep it faithful; every
   knot on a pair of it breaks the reading. Reworded.
3. **The degree-3 explanation needs the disc rule's single links and connectivity** (gap): with a pinched link ({012, 013, 123,
   045}) or a disconnected world a triangle link can be faithful. In connected disc-legal worlds of more than four distinctions none
   is (5,460 checked at six), and all 254 such closings in its simulation were rejected, each containing the configuration.

## Slips in the frozen run (said plainly)

- **P5 was not evaluated by the frozen code.** Its verdict is computed from the closing tables the code recorded.
- **Phantom distinctions.** After a rejected move with a new distinction, the frozen code kept the raised distinction count, so later
  "existing" proposals could pick an isolated distinction, and its surface and Euler readings counted isolated distinctions. A
  corrected re-run (`supplement.py`, labelled as a supplement, not the frozen test) gives identical verdicts and closing tables: the
  phantoms arose only after a world had stalled. Surfaces are read here on the distinctions in knots.
- **P1's and P5's failure lines did not anticipate a world closing into a tetrahedron before it could grow.** By the letter of the
  decision rules, P1's failure would say the law supplies "two per pair"; in fact the four failing worlds are closed tetrahedra that
  NAE will not extend. Logged in `docs/CORRECTIONS.md` (Not a block).

## Literature and provenance

- **Known.** Random growth of triangulations and Eden-type growth of surfaces; weak 2-colourings of hypergraphs (property B).
- **Classification.** The adjacent-apices lemma is elementary; the census's reading of growth through faithfulness: no overlap found
  (bounded search), not a novelty claim.

## Workspace assumptions

- **Relied on.** A64 (the reading under challenge), A39, A40.
- **Changed.** A64 gains a history line: growth by faithfulness does not supply the count either; status unchanged.

## Ratio

- **Substantive.** The frozen census (180 runs), the adjacent-apices lemma, the witness checks, the corrected supplement, one referee
  pass.
- **Administrative.** The pre-registration, this note, the closure and one correction entry.

## Corrections

One, Not a block (`docs/CORRECTIONS.md`, 2026-11-11): the pre-registration's decision rules for P1 and P5 would read a closed
tetrahedron as the law supplying the count; and the frozen code did not evaluate P5 and left phantom distinctions (verdicts
unchanged by the corrected re-run).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the count from growth | **Status:** Successful | The count is not supplied; the law's one local part found and proved |
| Local direction — growth by faithfulness | Practically exhausted | Closed by the stop rule; nothing in the reading chooses the count |
| Broader exploration — G1 on worlds of knots alone | Known alternatives | The ruler on tori and Klein bottles; the local list of what NAE forbids |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | How knots meet stays an input, static or grown |

**Corrections:** one, Not a block (above). **Goals:** a G1 checkpoint (obstruction learned), no goal change. **Assumptions:** A64
gains a history line, status unchanged.
**Basket:** `RULER-20261111-001#1` (the ruler on tori and Klein bottles, 2/3, 2/3), `GROW-FACE-20261110-001#1` (2/3, 1/3), B16
(2/3, 1/3); taken: none yet, direction 1 below is the first.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The ruler on tori and Klein bottles (was `RULER-20261111-001#1`) | 2/3 — Substantial | 2/3 — Testable | Extend the criterion to quasi-periodic heights; bound the tilt a short pattern sees by edge-width → β = δ + 1 below a proved function of edge-width, or the first counterexample | Selected · awaiting go-ahead |
| 2 | The local list of what NAE forbids | 2/3 — Substantial | 2/3 — Testable | Is "no adjacent apices plus long loops" exactly NAE-faithfulness on surface worlds? Test the lemma's converse on the frozen flat worlds of `LONG-LOOP-20261111-001` and on small spheres → a characterization, or a faithful failure it misses | Alternative · deferred |
| 3 | Write the knots-alone line up as a note | 1/3 — Modest | 3/3 — Ready | Five epics into one self-contained note → a note an expert can check | Alternative · deferred |
| 4 | A face that emerges (was `GROW-FACE-20261110-001#1`) | 2/3 — Substantial | 1/3 — Stated | As recorded | Alternative · deferred |

1. **Tori and Klein bottles.** Payoff 2: it proves what LONG-LOOP computed and explains its shortcuts. Concreteness 2: the torus
   states are quasi-periodic heights; the open step is the tilt bound.
2. **The local list.** Payoff 2: a local characterization of the faithful reading would say exactly which worlds of knots the law can
   read. Concreteness 2: the lemma gives one direction; the edge-width data suggest the rest.
3. **A note.** Payoff 1, concreteness 3: result conversion.
4. **A face that emerges.** As recorded.

**Recommendation.** Research directions, #1, the fallback the coordinator named, awaiting the go-ahead.
