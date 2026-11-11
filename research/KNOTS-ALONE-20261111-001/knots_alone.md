# Knots alone

Epic `KNOTS-ALONE-20261111-001` (backlog B144, G1, question 9; program topology, group spacing), 2026-11-11, at the owner's
go-ahead. Pre-registered in commit 91584bf92 before any law was run on any world of the family. Under challenge: A62 (a law gives a
shape only by forcing it) and A63 (a named face is put in, not native). The canonical K1–K3 test is unchanged.

## The question

- **Where it comes from.** The board line parked with "a uniform local law chooses the plane only by naming a face"
  (`GROW-FACE-20261110-001`). A review of the parked lines found that `UNIFORM-SPHERES-20261107-001` had read the same fact the other
  way: with faces declared as co-lines, a uniform law builds its own surface. In the knot's own terms a face can be a knot. A62 and
  A63 recorded the two default readings, and B144 proposed a census of worlds made of knots alone.
- **The question.** A world is a finite set of distinctions and a set of three-element subsets, its knots: no board, no names, no
  declared faces. A uniform law puts one symmetric three-place knot on every knot (PAR, NAE, OR or NOL, up to complement), with every
  distinction in d knots, with or without the surface condition (each co-knotted pair in exactly two knots, each link one cycle).
  Read from the allowed states alone: which worlds does each law allow and keep native, which does it read faithfully (its
  three-place bonds exactly the world's knots, no ties), what does it fix in every world it allows, and how far apart does it set
  two distinctions (bond distance)?

## The question in standard terms

For closed triangulated surfaces with every vertex of degree d, and for d-regular 3-uniform hypergraphs, consider the Boolean CSP
with one symmetric constraint (parity, not-all-equal, the 3-clause, not-exactly-one) on every triangle. When is the solution set
free of frozen variables, when are its minimal non-shattered triples exactly the triangles (the shatter complex recovers the
surface), what is the least non-shattered set with shattered facets containing two vertices, and which surfaces have no solution?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Three laws are settled by short arguments.** OR (the clause) reads every world faithfully and spaces nothing: its bonds are exactly the knots, bond distance 2 between co-knotted distinctions and none otherwise. PAR (parity) collapses a surface world to a proper 3-colouring: 4 states, ties inside each colour class, every rainbow triple a bond; native exactly on the 3-colourable surfaces, never faithful. NOL (not exactly one 1) is the hard-core law plus an all-zero hub state: native on every surface, its 3-bonds all triples containing a co-knotted pair, bond distance 2 between every two distinctions. Curvature is double counting (χ = V(6 − d)/6), and allowed and native states lift to covers. | proved (D1–D6; refereed; D1, D3 classical); the census reproduces every one on every world read | pre-registration, A |
| 2 | **P1 holds: at positive curvature NAE fixes the icosahedron.** NAE is faithful on the tetrahedron, octahedron and icosahedron and allows no state on the hemi-icosahedron. With the surface condition, d = 3 and d = 4 each leave one world and d = 5 two; NAE removes the projective plane, so the NAE law at d = 5 allows exactly the icosahedron. | computed, exact; complete by D1 | A |
| 3 | **P2 fails narrowly: NAE recovers almost every flat world.** It is faithful on 227 of the 229 flat worlds in range without a non-facial triangle; the two exceptions are the thin tori Z²/⟨(1,4),(0,16)⟩ and Z²/⟨(1,4),(0,17)⟩, of edge-width 4. K7 has no state. After the run: faithful on every one of the 142 flat worlds in range of edge-width at least 5, on 85 of 87 of edge-width 4, and on 16 of 77 of edge-width 3. | computed, exact, frozen; the edge-width reading exploratory | A |
| 4 | **P4 holds: NAE does not fix orientability.** It allows states on all 11 Klein bottles and on 294 of the 295 tori in range (all but K7), and on all 4 Klein bottles with 18 distinctions (stress test). PAR is native on 47 tori and 1 Klein bottle, the 3-colourable ones. | computed, exact | A |
| 5 | **P5 fails at distance 3: NAE's knots compose, as a ruler only to distance 2.** On every one of the 38 faithful lattice tori with 12 to 24 distinctions, bond distance is 2 at graph distance 1 and 3 at graph distance 2. At distance 3 it is 4 on some tori and 3 on others (19 rows on tori of 18 to 24), and the same in the stress test to 30; on the three tori of edge-width 6 it is 4 throughout. After the run: the shorter bonds depend on the torus, through its short loops, not on the local configuration. | computed, exact within bonds of size 6; the loop reading exploratory | A |
| 6 | **P3 fails as registered: no witness found at d ≥ 4.** Every law is native on non-surface worlds at d = 3, and NAE faithful on 34 of 420. At d = 4 to 7 the sample has no NAE-faithful non-surface world, no NAE-native one at d = 7, and no PAR-native one at d ≥ 4; OR and NOL are native on all. A biased sample at V ≤ 12 cannot show an absence. The two registered cells the frozen code omitted, (6, 6) and (7, 6), give the same. | computed, exact per world; the sample biased | A, supplement |
| 7 | **Negative curvature, a sample.** Of 34 seven-regular surfaces on 12 distinctions, NAE allows 33 and reads none faithfully; all have non-facial triangles. | computed, exact per world; a 600-second sample | A |

## Answer

On worlds of knots alone, only the not-all-equal knot both recovers its world from its allowed states and spaces it. OR recovers
the knots but relates nothing beyond touching; parity folds the plane to coordinates mod 3; not-exactly-one ties everything to one
hub state. NAE reads almost every flat world faithfully, every one in range whose short loops have length at least 5, and its
bond distance is graph distance plus one out to distance 2. The frozen predictions P2 and P5 failed, narrowly: two thin tori are
not read faithfully, and at distance 3 short loops can shorten a bond. By the frozen rule A63 stands for NAE on flat worlds. At
positive curvature a uniform law does fix global shape and size, mostly through the surface condition, with NAE removing the
projective plane at d = 5; at d ≥ 6 no law fixes size, and NAE does not fix orientability. A62 is narrowed accordingly.

## Reading

**Interpretation, not a theorem.**
- **Four readings of one drawn surface.**
  - **OR** is a photograph without distances. Its bonds are exactly the faces, and a shared distinction of two OR knots is a gate (its
    value 1 satisfies both), a common hub under A39.
  - **PAR** folds the flat world into one knot copied everywhere: three classes, the coordinates mod 3 that the square-closing law of
    `GROW-FACE-20261110-001` carried as its values.
  - **NOL** ties every pair to the all-zero state, a hub, so every two distinctions are at bond distance 2.
  - **NAE** keeps the surface. Its composite bonds sit around hidden distinctions: fixing two edges of a hidden distinction's link
    to opposite equal values forces it both ways, and the four fixed distinctions form a bond. That is why bond distance steps from
    2 to 3 between graph distances 1 and 2.
- **What breaks the reading is topology.** The worlds NAE does not read faithfully, and the bonds that come out shorter than graph
  distance plus one, sit on worlds with short non-contractible loops. NAE's allowed states see the world's short loops: local
  geometry and loop structure are both native, and they part only where the loops are short.
- **For the named face.** Here the face is the knot, and nothing else names it. What is still put in is the surface count: d, and
  that knots meet in pairs around each distinction, recorded as A64. Whether NAE's faithful reading supplies that count by itself is
  what P3 left open: the sample found faithful non-surface worlds only at d = 3, where the only surface is the tetrahedron.
- **For forcing.** Positive curvature leaves a world no cover, so a local law can fix it outright; that is where forcing works.
  Flat and hyperbolic worlds always have covers, so there a law can fix only what every allowed world shares, the co-real reading of
  A62.
- **Bond distance is a counted size** (A40), the size of the least knot through two distinctions; it is not drawn and not read from
  the complex.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Exact and complete within range.** Surface worlds at d ≤ 5 for every V, all 6-regular surfaces with 7 to 16 distinctions (SAT,
  refereed), all lattice tori with 17 to 48 (Altshuler; the referee's orbit count agrees at every V). Every law reading is exact.
- **Census-only.** The edge-width reading of P2, and bond distance 2 and 3 at graph distances 1 and 2, hold in range and are not
  proved. The negative-curvature figures come from a time-limited sample, and P3's from a biased one.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| P5 (bond distance) | every lattice torus with 25 to 30 distinctions (41, 33 faithful) | distance 1 → 2 and 2 → 3 on all; distance 3 → 4 or 3, 16 rows with 3; edge-width 6 → 4 only |
| P2 and P4 | every 6-regular surface with 17 and 18 distinctions | the edge-width-4 torus at 17 again not faithful; all 4 Klein bottles at 18 allowed, 3 faithful |

Scripts: `stress_test.py` (output `stress_test.json`), `edge_width.py` (the post-run edge-width readings) and `omitted_cells.py`
(the two omitted cells, `omitted_cells.json`), all beside this note.

## Review

An independent referee, a fresh agent that did not see the results, checked the lemmas and the code with its own brute force, SAT
encoding and isomorphism test on 174 surface worlds and 60 non-surface systems. No lemma is broken and no code bug changes a
verdict. Its findings, all folded in:
1. **D2** holds, with one step added: a cover of a simplicial surface is simplicial, so covers are worlds. Only allowed and native
   lift; faithfulness need not.
2. **D3 overclaim.** "At d ≥ 7 there are worlds of every higher genus" fails for the non-orientable surface with χ = −1. Nothing
   rests on it (corrected).
3. **D5** holds, with the missing step written out: the A-coloured vertices of a non-A vertex's link are all equal, so the
   equality classes are the colour classes.
4. **P4 wording.** "PAR allows exactly the 3-colourable flat worlds" is wrong: the all-ones state is allowed everywhere. The code
   counts "native", which is right (corrected).
5. **The A62 rule overstates the law's part.** At d ≤ 5 the surface condition and d do most of the fixing; NAE only excludes the
   projective plane, and only among surface worlds (folded into the Answer).
6. **The non-surface family was narrower than registered.** An unregistered filter dropped the cells (6, 6) and (7, 6); they were
   run afterwards with the frozen generator and seed rule, and P3 is unchanged (corrected).
7. **Minor.** P1's dictionary could hide a duplicate key (no effect, by D3); the knotlab cross-check compares the number of
   3-bonds, not the sets (the referee's own comparison covers the sets); the d = 7 sample depends on the machine's speed.
8. **Checked fine.** The SAT symmetry breaking is sound, and the referee's labelled counts match its classes at 7 to 13; flag codes
   neither merge nor split classes; the lattice tori match an independent orbit count at every V to 48; the four reading functions
   and the bond-distance search match the referee's brute force on every field.

## Literature and provenance

- **Classical background.** Euler's formula and the regular triangulations; Altshuler (1973) for the 6-regular tori T(r, s, t);
  Negami and Thomassen for the Klein bottles; Heawood's 3-colouring criterion for parity.
- **NAE on triangulations** is the weak (polychromatic) 2-colouring of a triangulation. K7 on the torus has none; Kündgen and
  Ramamurthi showed that every surface other than the sphere has triangulations that need three colours; Hutchinson, Richter and
  Seymour showed that Eulerian triangulations of high width on orientable surfaces are 4-colourable. Collins and Hutchinson, Yeh and
  Zhu, and Sankarnarayanan (2022) classify the 4-colourable T(r, s, t). These bear on whether NAE allows a state, not on
  faithfulness or bond distance.
- **Shatter complexes.** Free sets form the shatter complex of the solution set, and bonds are its minimal non-faces
  (Moran–Rashtchian; Yang). No result recovering a triangulation from a CSP's shatter complex was found.
- **Classification.** D1, D3 and D4 elementary or classical; D5 and D6 elementary, as readings new; the NAE census (faithfulness,
  bond distance, the exclusion of the hemi-icosahedron) no overlap found in a bounded search, which is not a novelty claim.

## Workspace assumptions

- **Relied on.** A15 (co-reality, behind A62's alternative reading), A39 (gates are hubs), A40 (counted length is native), A61
  (closing a cycle names a face), A62 and A63 (the readings under challenge).
- **Added.** A64, counting how knots meet at a distinction names no face: the surface condition was read as an incidence count,
  like d.
- **Changed.** A62 and A63 gain history lines; their statuses stay Assumed.

## Ratio

Since the epic opened:
- **Substantive.** The six lemmas, the frozen census and its independent paths, the stress test, the edge-width readings, the two
  omitted cells, one referee pass.
- **Administrative.** Two correction entries, the pre-registration, this note and the closure.

## Corrections

Two, neither a block (`docs/CORRECTIONS.md`, 2026-11-11):
- **Narrowing.** "A law fixes local geometry and never global shape or size" (A62's challenge, B144's P2, the review's reply)
  holds only where every world has proper covers.
- **Not a block.** Slips in the pre-registration found by the referee: D3's "every higher genus" at d ≥ 7, P4's "allows" for
  "is native on", the A62 rule's credit to the law, and two registered cells dropped by the frozen code.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the knots-alone census (B144) | **Status:** Partially successful | P1, P4 hold; P2, P3, P5 fail narrowly; three laws settled by proof |
| Local direction — NAE on worlds of knots alone | Continue | Faithful wherever loops are long; whether faithfulness supplies the surface is open |
| Broader exploration — G1 space from a law | Known alternatives | The board line's routes are closed; this setting is the open one |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | One knot law reads flat local geometry natively with nothing named but the knot and the surface count |

Under the table: the attempt leaves A63 standing by its frozen rule, while NAE's reading comes close to overturning it on flat
worlds of long loops; the missing bridge is whether the surface count must be put in.

**Corrections:** two, neither a block (above). **Goals:** a G1 checkpoint (capability gained), no goal change; B144 taken;
sub-goal B145 recorded. **Assumptions:** A64 added (Assumed); A62 and A63 gain history lines, statuses unchanged.
**Basket:** `GROW-FACE-20261110-001#1` (a face that emerges, 2/3, 1/3), B16 (2/3, 1/3); none taken: direction 1 below asks the
same question with a test in hand.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does NAE's faithful reading supply the surface? (B145) | 3/3 — Major | 2/3 — Testable | NAE readings of d-regular non-surface worlds with 13 to 30 distinctions, d = 4 to 7, exhaustive small cases first, frozen → a faithful non-surface world (the count must be put in), or none and a local lemma for why | Selected · awaiting go-ahead |
| 2 | The edge-width reading, frozen | 2/3 — Substantial | 3/3 — Ready | NAE on lattice tori 49 to 80 and Klein bottles past 18, predicting faithful at edge-width ≥ 5 → confirmed, or the first failure | Alternative · deferred |
| 3 | NAE's ruler as a theorem | 2/3 — Substantial | 2/3 — Testable | Prove bond distance = graph distance + 1 on flat worlds of large edge-width (the hidden-path bonds for the upper bound, a splitting argument as in `LOGIC-AXIS-20261107-001` for the lower) → a proof, or the distance where it fails | Alternative · deferred |
| 4 | A face that emerges (was `GROW-FACE-20261110-001#1`) | 2/3 — Substantial | 1/3 — Stated | As recorded | Alternative · deferred |

1. **Faithfulness and the surface.** Payoff 3: if no non-surface world is read faithfully at d ≥ 4, the surface count is not an
   input but a consequence of reading the knots natively, and the last caveat on A63 goes. Concreteness 2: the code runs as is; the
   sample here was small and biased, and a lemma would have to explain why a pair in one or three knots, or a pinched link, makes an
   extra bond or a tie. The main uncertainty is that the absence may be a small-size effect, as faithfulness itself is on flat worlds
   below V = 12. It bears on G1 through A63 and A64; bounded to one epic.
2. **The edge-width reading.** Payoff 2: it would make "faithful wherever loops are long" a frozen result. Concreteness 3: the
   frozen code needs only the new range. Deferred: it confirms a pattern rather than deciding a caveat.
3. **The ruler.** Payoff 2: a native metric equal to graph distance plus one, the board's own distance read from knots alone.
   Concreteness 2: the upper bound has a construction; the lower bound route is not yet checked on this law.
4. **A face that emerges.** Payoff 2, concreteness 1, as recorded; direction 1 asks the same question with a test in hand.

**Recommendation.** Research directions, #1, awaiting the coordinator's go-ahead.

## Final report as sent

Sent to the owner on 2026-11-11 at 04:59 UTC and copied here verbatim.

**Knots alone: only the not-all-equal knot both recovers a world made of knots and spaces it. It came close to overturning A63 but didn't.**

- **The other three laws are settled by proof.** The clause recovers exactly the knots but relates nothing beyond touching. Parity folds a flat world into a 3-colouring. Not-exactly-one ties everything to one all-zero hub state.
- **Not-all-equal recovers the world.** It reads 227 of 229 flat worlds (those without a non-facial triangle) faithfully, and every one whose short loops have length 5 or more. Its bond distance is graph distance + 1 out to distance 2.
- **At positive curvature a law fixes the whole world.** With five knots per distinction, not-all-equal allows only the icosahedron. Flat worlds always have covers, so no law fixes their size, and not-all-equal allows every Klein bottle in range.
- **Why A63 stands.** P2, P3 and P5 failed narrowly (two thin tori, a biased sample, and short loops shortening bonds at distance 3), so by the frozen rule A63 stands.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the knots-alone census (B144) | **Status:** Partially successful | P1, P4 hold; P2, P3, P5 fail narrowly; three laws settled by proof |
| Local direction — NAE on worlds of knots alone | Continue | Faithful wherever loops are long; whether faithfulness supplies the surface is open |
| Broader exploration — G1 space from a law | Known alternatives | The board line's routes are closed; this setting is the open one |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | One knot law reads flat local geometry natively with nothing named but the knot and the surface count |

**Corrections:** two, neither a block.
1. *Narrowing*, reported earlier: "a law never fixes global shape or size" holds only where worlds have covers.
2. *Not a block*: the referee found four slips in the pre-registration (a genus aside, "allows" written for "is native on", the A62 rule crediting the law, and two registered cells the code dropped; I ran those afterwards and nothing changed).

**Goals:** a G1 checkpoint (capability gained), no goal change; B144 taken; sub-goal B145 recorded.
**Assumptions:** A64 added ("counting how knots meet names no face"); A62 and A63 gain history lines, statuses unchanged.
**Basket:** GROW-FACE#1 (a face that emerges, 2/3, 1/3), B16 (2/3, 1/3); none taken, because direction 1 asks the same question with a test in hand.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does NAE's faithful reading supply the surface? (B145) | 3/3 — Major | 2/3 — Testable | NAE on non-surface regular worlds, 13–30 distinctions, d = 4–7, frozen → a faithful one, or none and a local lemma | Selected · awaiting go-ahead |
| 2 | The edge-width reading, frozen | 2/3 — Substantial | 3/3 — Ready | Tori 49–80, Klein bottles past 18 → confirmed or first failure | Alternative · deferred |
| 3 | NAE's ruler as a theorem | 2/3 — Substantial | 2/3 — Testable | Hidden-path bonds up, a splitting argument down → a proof or where it fails | Alternative · deferred |
| 4 | A face that emerges (was GROW-FACE#1) | 2/3 — Substantial | 1/3 — Stated | As recorded | Alternative · deferred |

Everything is committed and published ([decision note](https://github.com/jscul/knotlab/blob/main/research/KNOTS-ALONE-20261111-001/knots_alone.md)). I'm holding before a second epic until the coordinator gives the go-ahead.
