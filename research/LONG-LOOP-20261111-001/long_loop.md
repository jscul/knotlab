# The long-loop regime

Epic `LONG-LOOP-20261111-001` (NAE-SURFACE-20261111-001 direction 1, with KNOTS-ALONE-20261111-001 direction 2; G1, question 9;
program topology, group spacing), 2026-11-11, at the coordinator's go-ahead. Pre-registered in commit 706c950ae before any run.
Under challenge: A63, with the surface count given (A64). The canonical K1–K3 test is unchanged.

## The question

- **Where it comes from.** On worlds of three-place knots alone, the not-all-equal law (NAE) was faithful on every flat world in
  `KNOTS-ALONE-20261111-001`'s range whose short loops have length at least 5, and its bond distance was graph distance + 1 to
  distance 2; both readings came after that run, and its frozen predictions failed on thin worlds, so A63 stood.
  `NAE-SURFACE-20261111-001` then showed that the surface count is an input.
- **The question.** Frozen one size range up: is NAE faithful on every flat world of edge-width at least 5, and on tori of edge-width
  at least 6 is bond distance graph distance + 1 out to distance 3?

## The question in standard terms

For 6-regular triangulations of the torus (49 to 80 vertices) and of the Klein bottle (19 to 40) with no non-contractible cycle
shorter than 5, are the triangles exactly the minimal non-shattered triples of the set of proper 2-colourings (no monochromatic
triangle), with every pair shattered? On those of edge-width at least 6, is the least non-shattered set with shattered facets that
contains two vertices at graph distance δ ≤ 3 of size δ + 2?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **P1 holds: long loops are read faithfully.** NAE reads every one of the 449 flat worlds in range of edge-width at least 5 faithfully: 434 tori with 49 to 80 distinctions and 15 Klein bottles with 19 to 40. Every world of edge-width 4 in range is faithful too (76 tori, 29 Klein bottles; no prediction); at edge-width 3, 10 of 52 tori and 6 of 22 Klein bottles. | computed, exact, frozen | A |
| 2 | **P2 holds: NAE's knots space the world as a ruler to distance 3.** On every one of the 349 tori of edge-width at least 6 (all faithful), bond distance from a distinction is graph distance + 1 at every distinction within distance 3: at distance 3 no four-element bond contains the pair anywhere in the world, and a five-element bond contains it nearby. | computed, exact (the four-element search over the whole world; the five-element bonds found as witnesses) | A |
| 3 | **Distance 2 is a lemma.** On a surface world with every distinction in d ≥ 4 knots and no non-facial triangle that NAE reads faithfully, bond distance is 3 at graph distance 2: two disjoint edges of a hidden distinction's link, fixed to opposite equal values, force it both ways. The census found the bond on every torus it measured. | proved, refereed; checked on 349 tori | pre-registration, A |
| 4 | **The worlds are complete.** Tori are the lattice modulo a sublattice (Altshuler); Klein bottles the lattice modulo translations and a glide, which gave exactly the exhaustive SAT Klein bottles at 7 to 16 by isomorphism class (and to 18 by count). | classical; checked | A |

## Answer

Both frozen predictions held. Within the surface count, the not-all-equal knot reads every long-loop flat world in range from its
allowed states alone (the world's knots are exactly its minimal constrained triples) and spaces it as graph distance + 1 out to
three steps. By the frozen rule, A63 is overturned in the knots-alone setting: a face named only by a knot gives native flat local
geometry. What is still put in is the count of how knots meet (A64, `NAE-SURFACE-20261111-001`). The evidence is computed in range;
distance 2 is proved given faithfulness.

## Reading

**Interpretation, not a theorem.**
- **For the owner's question.** The board line ended with "the plane needs a named face". Here the face is the knot, nothing else
  is named, and the plane's local geometry is read natively wherever the world's loops are long. So the face was never the
  obstacle; the obstacle is how faces meet, a count the law has to be given.
- **Where it breaks is topology, and only there.** Thin worlds, with non-contractible loops of length 3, are where faithfulness
  fails and bonds shortcut. The law reads the world's short loops, as it should: they are part of the world.
- **Composition is the ruler.** Bond distance grows by one per step because each step adds one hidden distinction whose link is
  forced both ways; the knots compose through hidden distinctions, which is what A39 asks of space.
- **A local ruler.** Out to three steps on tori of edge-width at least 6 the reading is graph distance + 1. On faithful tori of
  edge-width 4 and 5 a bond can shortcut at three steps, so the ruler looks local, holding to about half the edge-width (post hoc,
  from the referee's examples and `KNOTS-ALONE-20261111-001`); whether it holds at every distance below that is the next question.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Exact and complete in range.** Every torus with 49 to 80 distinctions and every Klein bottle with 19 to 40; every reading exact.
- **Census-only.** P1 and P2 hold in range and are not proved; distance 2 is proved given faithfulness.

## Stress test

One size past, the frozen code unchanged (`stress_test.py`, output in `stress/`): every torus with 81 to 96 distinctions and Klein
bottle with 41 to 48 (424 worlds; the glide control again exact at 7 to 16).

| Claim | One size past | Result |
| --- | --- | --- |
| P1 (faithful at edge-width ≥ 5) | 339 worlds (tori 81 to 96, Klein bottles 41 to 48) | pass: every one faithful |
| P2 (graph distance + 1 to distance 3 at edge-width ≥ 6) | 286 tori | pass: every one |

Below edge-width 5, again with no prediction: every edge-width-4 world faithful (38 tori, 10 Klein bottles); at edge-width 3, 6 of 28
tori and 4 of 9 Klein bottles. Folded in on 2026-11-11 (LONG-LOOP-S1).

## Review

An independent referee, a fresh agent that did not see the results, checked the lemma, the world construction and the census
code with its own brute force. No step of the lemma fails and no bug can flip P1 or P2. Its findings:
1. **The lemma is correct**, checked by brute force on the octahedron, the icosahedron, every faithful torus and Klein bottle to 21
   distinctions and seven random spheres of mixed degree. Its hypotheses are stronger than needed: uniform degree is never used,
   d ≥ 4 is automatic, and only "no knot among three link vertices of the hidden distinction" is used, not edge-width 4. Faithful
   edge-width-3 worlds have β = 3 at distance 2 as well.
2. **The Klein bottle construction is correct and complete;** the referee's independent replication gives the same 66 classes.
3. **Edge-width labels (error, latent, no effect).** The search boxes in `flat_worlds.py` can only overestimate. Four tori labelled
   10 have edge-width 9 ((1,16,70), (1,18,78), (1,18,80), (1,36,80)), and some raw Klein quotients are overestimated, none of them a
   class representative. The counts at the thresholds are exact (434 tori and 15 Klein bottles of at least 5, 349 tori of at least
   6), so no world was wrongly in or out. A successor should use an exact orbit search.
4. **The census does what the pre-registration says;** its distance-2 and distance-3 answers match brute force on all 16 faithful
   tori with 19 to 24 distinctions.
5. **Edge-width 6 is load-bearing (overclaim risk).** The faithful edge-width-5 tori (1,9,21) and (1,5,22) have four-element bonds
   at distance 3. Every summary keeps "to distance 3, on edge-width at least 6".
6. **The 4-colourability citation guarantees nothing at these widths** (an unspecified constant, orientable surfaces only); the
   census checks states directly, so nothing rests on it.

## Literature and provenance

- **Known.** Altshuler (1973) for the tori; the Klein bottles as quotients of the triangular lattice (Negami, Thomassen); Eulerian
  triangulations of orientable surfaces of edge-width above an unspecified constant are 4-colourable (Hutchinson, Richter and
  Seymour), so NAE has states on large enough tori; this guarantees nothing at the widths here.
- **Classification.** Faithfulness and the bond distances: no overlap found in a bounded search (also those of `KNOTS-ALONE` and
  `NAE-SURFACE`), not a novelty claim.

## Workspace assumptions

- **Relied on.** A64 (the surface count names no face), A39, A40.
- **Changed.** A63 overturned in the knots-alone setting with the surface count given, on computed evidence in range.

## Ratio

- **Substantive.** The world list, the frozen census, the lemma, one referee pass, the stress test (passed).
- **Administrative.** The pre-registration, this note, the closure and one correction entry.

## Corrections

One, Not a block (`docs/CORRECTIONS.md`, 2026-11-11): the board line's reading that what a law must say is "what a face is" holds
only where places are given; on worlds of knots alone the face is the knot, and what must be said is how knots meet.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the long-loop regime, frozen | **Status:** Successful | P1 and P2 hold on 449 and 349 worlds |
| Local direction — NAE on worlds of knots alone | Continue | The ruler beyond distance 3 and as a theorem is open |
| Broader exploration — G1 space from a law | Known alternatives | The count from growth; the ruler; defects |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | Flat local geometry read natively from knots alone, the surface count given |

**Corrections:** one, Not a block (above). **Goals:** a G1 checkpoint (capability gained), no goal change; the taken directions
recorded. **Assumptions:** A63 overturned in the knots-alone setting with the surface count given.
**Basket:** `KNOTS-ALONE-20261111-001#3` (the ruler, 2/3, 2/3), `NAE-SURFACE-20261111-001#3` (the count from growth, 2/3, 1/3),
`GROW-FACE-20261110-001#1` (2/3, 1/3); taken: none yet; direction 1 below is the first.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | NAE's ruler as a theorem (was `KNOTS-ALONE-20261111-001#3`) | 2/3 — Substantial | 2/3 — Testable | Prove bond distance = graph distance + 1 at every distance on faithful flat worlds of large edge-width: hidden-path bonds for the upper bound, a lower bound from faithfulness and locality → a proof, or the distance where it fails | Selected · awaiting go-ahead |
| 2 | The count from growth (was `NAE-SURFACE-20261111-001#3`) | 2/3 — Substantial | 1/3 — Stated | A growth rule adding one NAE knot at a time while the reading stays faithful → closes into a surface, or not | Alternative · deferred |
| 3 | Bond balls read dimension 2 | 2/3 — Substantial | 2/3 — Testable | Bond-ball sizes from one distinction out to distance 6 on the largest tori, by local search → quadratic growth, or where the search stops being exact | Alternative · deferred |
| 4 | Which defects NAE tolerates (was `NAE-SURFACE-20261111-001#4`) | 1/3 — Modest | 3/3 — Ready | As recorded | Alternative · deferred |

1. **The ruler as a theorem.** Payoff 2: a native metric from knots alone, graph distance + 1, proved rather than computed.
   Concreteness 2: the distance-2 lemma shows the shape of the argument; at larger distances the upper bound needs the bond around a
   hidden path to have free facets, and the lower bound needs a reason no smaller set is constrained.
2. **The count from growth.** Payoff 2: the count is the one input left; growth supplied connectedness before. Concreteness 1: no rule
   is in hand.
3. **Bond balls.** Payoff 2: dimension read natively, question 9's measure. Concreteness 2: direction 1 would give it outright; the
   search grows fast with distance.
4. **Defects.** Payoff 1, concreteness 3, as recorded.

**Recommendation.** Research directions, #1, awaiting the coordinator's go-ahead.

## Final report as sent

Sent to the owner on 2026-11-11 at 06:27 UTC and copied here verbatim.

**Long-loop regime: both frozen predictions held, so A63 is overturned for worlds made of knots alone.** The face can be the knot. What still has to be given is the count of how knots meet.

- **P1.** Not-all-equal reads every flat world in range whose shortest loop has length 5 or more faithfully: 434 tori (49–80 distinctions) and 15 Klein bottles (19–40).
- **P2.** On all 349 tori with loops of length 6 or more, bond distance is graph distance + 1 at every distinction within three steps. Two steps is a short proof, which the referee checked; three steps is computed.
- **Scope.** This is computed in range, to distance 3 and edge-width 6. The referee found faithful edge-width-5 tori where a bond shortcuts at three steps, so the ruler looks local. A stress test one size past (tori 81–96) is still running.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the long-loop regime, frozen | **Status:** Successful | P1 and P2 hold on 449 and 349 worlds |
| Local direction — NAE on worlds of knots alone | Continue | The ruler beyond distance 3 and as a theorem is open |
| Broader exploration — G1 space from a law | Known alternatives | The count from growth; the ruler; defects |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | Flat local geometry read natively from knots alone, the surface count given |

**Corrections:** one, Not a block. The board line read "the rules have to say what a face is" as the obstacle. That holds where places are given; with knots alone the face is the knot, and the obstacle is how knots meet.
**Goals:** a G1 checkpoint (capability gained), no goal change.
**Assumptions:** A63 overturned in this setting, with the surface count given.
**Basket:** the ruler (2/3, 2/3), the count from growth (2/3, 1/3), GROW-FACE#1 (2/3, 1/3); none taken yet. Direction 1 is the first.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | NAE's ruler as a theorem | 2/3 — Substantial | 2/3 — Testable | Hidden-path bonds up, faithfulness and locality down → a proof, or the distance where it fails | Selected · awaiting go-ahead |
| 2 | The count from growth | 2/3 — Substantial | 1/3 — Stated | A growth rule adding NAE knots while the reading stays faithful → closes into a surface, or not | Alternative · deferred |
| 3 | Bond balls read dimension 2 | 2/3 — Substantial | 2/3 — Testable | Ball sizes to distance 6 on the largest tori → quadratic growth, or where exact search stops | Alternative · deferred |
| 4 | Which defects NAE tolerates | 1/3 — Modest | 3/3 — Ready | Classify faithful swaps by distance → a rule, or none | Alternative · deferred |

It's committed and published ([decision note](https://github.com/jscul/knotlab/blob/main/research/LONG-LOOP-20261111-001/long_loop.md)). I'm holding for a go-ahead and will fold in the stress test when it finishes.
