# Does a faithful reading supply the surface?

Epic `NAE-SURFACE-20261111-001` (sub-goal B145, G1, question 9; program topology, group spacing), 2026-11-11, at the coordinator's
go-ahead after `KNOTS-ALONE-20261111-001`. Pre-registered in commit e2b80c46e before any run. Under challenge: A64 (counting how
knots meet at a distinction names no face). The canonical K1–K3 test is unchanged.

## The question

- **Where it comes from.** On worlds of three-place knots alone, the not-all-equal law (NAE) reads almost every flat surface
  faithfully: its three-place bonds are exactly the world's knots, with no ties and nothing frozen (`KNOTS-ALONE-20261111-001`). The
  surface condition (every co-knotted pair in two knots, every link one cycle) was given with the law, and that epic's small sample
  found faithful non-surface worlds only at d = 3.
- **The question.** For d = 4 to 7, is any connected simple d-regular world that is not a surface read faithfully by NAE? If none
  is, faithfulness supplies the surface count; one such world shows the count is an input.

## The question in standard terms

For a 3-uniform d-regular hypergraph H, let S be its set of proper 2-colourings (no monochromatic edge). If the minimal triples not
shattered by S are exactly the edges of H, no pair is unshattered and no vertex is constant, must H be a triangulated closed surface?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **No: a faithful reading does not supply the surface.** 160 of the 822 swap worlds (6-regular, 24 to 48 distinctions, flat tori of edge-width at least 5 with one, two or four degree-preserving knot swaps) are read faithfully though none is a surface. Each has pairs in one knot, and 22 also have pairs in three or more knots. The smallest has 25 distinctions and 50 knots, 8 pairs in one knot, and 2,044 states. | computed, exact, frozen; the smallest checked independently (brute force and knotlab) | A |
| 2 | **Defects cost faithfulness.** One swap keeps 69 of 274 worlds faithful, two swaps 61, four swaps 30; the others gain three-place bonds that are not knots (660) or lose nativeness (2). | computed, exact | A |
| 3 | **Random regular worlds are never read faithfully in range.** Of 1,440 sampled worlds (d = 4 to 7, 13 to 30 distinctions), none is: they gain extra three-place bonds or lose nativeness, and at d = 7 almost none is native (1 of 240). | computed, exact per world; a biased sample | A |
| 4 | **Nothing on six distinctions is faithful.** Of the 21 non-surface worlds on 6 distinctions at d = 4 to 7 (all of them), none is read faithfully. | computed, exact, exhaustive | A |

## Answer

B145 is answered no. NAE's faithful reading recovers a world's knots exactly, but it recovers non-surfaces too: a flat torus with
two of its knots swapped for two long-range ones is read faithfully although eight of its pairs now lie in one knot. So the surface count is an
input to the law, not a consequence of reading the knots natively. P1 and P3 held; P2 failed (no faithful random world at any d).

## Reading

**Interpretation, not a theorem.**
- **Faithfulness is slack, not shape.** NAE recovers a knot when nothing else in the world pins its three distinctions together. A
  flat torus with long loops has that slack everywhere, and a few defects leave most of it, so the knots are still recovered. The
  law reads which knots there are, not how they meet.
- **But it prefers near-surfaces.** Every faithful non-surface world found is a surface with a few defects, and faithfulness falls
  as defects are added; random regular worlds, defects everywhere, were never faithful. A surface is where NAE's reading is easiest,
  not where it is forced.
- **For the named face (A63, A64).** The knot is the face, but how knots meet, two to a pair and once around each distinction, is
  put in. Whether that count is naming (A61's finer reading) or merely counting (A64's default) is a choice about words; this epic
  shows it is an input either way.
- **What this leaves for G1.** Within the surface count, NAE reads flat local geometry natively where loops are long
  (`KNOTS-ALONE-20261111-001`). The count itself would have to come from elsewhere, for instance from growth, which supplied
  connectedness in `GROW-FACE-20261110-001`.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Exact.** Every reading. F0 is exhaustive on 6 distinctions; F1 is a biased sample; F2 is complete over the frozen tori, swaps
  and seeds.
- **Census-only.** That defects cost faithfulness, and that random regular worlds are not faithful, hold in the samples only.

## Stress test

The claim that decides the epic is an existence, so the stress test is an independent check of the witness rather than a size past
it: `witness_check.py` (code apart from the frozen library) enumerates all 2^25 states of the smallest faithful world
(`witness.json`), and confirms with knotlab's canonical projections that every pair is free, every knot is a bond and every other
triple is free (`witness_check.json`). The same check rejects a non-faithful 12-distinction torus.

## Review

The witness was checked by independent code and the canonical checker (above). No lemma is claimed, so no proof was refereed. The
frozen code's coverage check confirmed that every registered cell of F0 and F1 ran, and the library hash matched KNOTS-ALONE's
contract.

## Literature and provenance

- **Searched (bounded).** Reconstruction of hypergraphs from their colourings appears in a quantum-contextuality setting (arXiv
  2105.08520); weak 2-colourings of pseudomanifolds and polychromatic colourings of triangulations (SWAT 2026) concern existence and
  balance.
- **Classification.** No overlap found for whether the shatter structure of a hypergraph's proper 2-colourings determines that it is
  a surface; not a novelty claim.

## Workspace assumptions

- **Relied on.** A64 (the reading under challenge), A63, A15.
- **Changed.** A64 gains a history line: the count is an input; status unchanged (Assumed), since whether counting is naming is
  untouched. A63 gains one: the surface count must be put in.

## Ratio

- **Substantive.** The frozen census (three families), the independent witness check.
- **Administrative.** The pre-registration, this note and the closure.

## Corrections

None.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — does a faithful reading supply the surface (B145) | **Status:** Successful | 160 faithful non-surface worlds; the count is an input |
| Local direction — the surface count from the knot law | Practically exhausted | Faithfulness tolerates defects; nothing in the reading enforces the count |
| Broader exploration — G1 on worlds of knots alone | Known alternatives | The long-loop regime and the ruler, from `KNOTS-ALONE-20261111-001` |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | The knot law reads local geometry, not the count of how knots meet |

**Corrections:** none. **Goals:** a G1 checkpoint (obstruction learned), no goal change; B145 taken. **Assumptions:** A64 and A63
gain history lines, statuses unchanged.
**Basket:** `KNOTS-ALONE-20261111-001#2` (the edge-width reading, 2/3, 3/3), `KNOTS-ALONE-20261111-001#3` (the ruler, 2/3, 2/3),
`GROW-FACE-20261110-001#1` (2/3, 1/3); none taken yet: direction 1 below joins the first two, awaiting the go-ahead.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The long-loop regime, frozen (was `KNOTS-ALONE-20261111-001#2`) | 2/3 — Substantial | 3/3 — Ready | NAE on lattice tori 49 to 80 and Klein bottles past 18, predicting faithful at edge-width ≥ 5 and bond distance = graph distance + 1 to distance 3 at edge-width ≥ 6 → both confirmed (A63 overturned within the surface count), or the first failure | Selected · awaiting go-ahead |
| 2 | NAE's ruler as a theorem (was `KNOTS-ALONE-20261111-001#3`) | 2/3 — Substantial | 2/3 — Testable | Hidden-path bonds for the upper bound, a splitting argument for the lower → a proof, or the distance where it fails | Alternative · deferred |
| 3 | The count from growth | 2/3 — Substantial | 1/3 — Stated | Does a growth rule that adds one NAE knot at a time, keeping the reading faithful, close into a surface? → a rule that does, or worlds it grows that are not surfaces | Alternative · deferred |
| 4 | Which defects NAE tolerates | 1/3 — Modest | 3/3 — Ready | Classify the swaps that keep faithfulness by the distance between the swapped knots → a rule, or none | Alternative · deferred |

1. **The long-loop regime.** Payoff 2: it would settle A63's challenge where loops are long, the regime the knots-alone census
   pointed to, with the surface count as given. Concreteness 3: the frozen code needs only the range. Bounded to one epic.
2. **The ruler.** Payoff 2: a native metric equal to graph distance plus one. Concreteness 2: the upper bound has a construction;
   the lower bound route is unchecked.
3. **The count from growth.** Payoff 2: the count is an input to a static law, but growth might supply it, as it supplied
   connectedness for the board line. Concreteness 1: no rule is in hand.
4. **Defects.** Payoff 1: it would describe how far from a surface the reading survives. Concreteness 3: the data exist.

**Recommendation.** Research directions, #1, awaiting the coordinator's go-ahead.
