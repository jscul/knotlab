# The not-all-equal ruler

Epic `RULER-20261111-001` (LONG-LOOP-20261111-001 direction 1; G1, question 9; program topology, group spacing), 2026-11-11, at the
coordinator's go-ahead. Statement frozen in commit 6fd9a2c6b before the proof was written. The canonical K1–K3 test is unchanged.

## The question

- **Where it comes from.** On flat worlds of knots alone, the not-all-equal law (NAE) set bond distance equal to graph distance + 1
  out to distance 3 on every torus of edge-width at least 6 in range (`LONG-LOOP-20261111-001`, computed), with distance 2 proved
  given faithfulness. Is it a theorem at every distance?
- **The question.** On the triangular lattice under NAE: is every pair free with the triangles as the only three-site bonds (R1), is
  β(u, v) = δ(u, v) + 1 for every two sites (R2), and is every bond native (R3)?

## The question in standard terms

For the ground states of the triangular Ising antiferromagnet (2-colourings of the triangular lattice with no monochromatic
triangle), what are the minimal non-shattered vertex sets, and how large is the smallest one containing two given vertices?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The plane is read faithfully (R1).** Every pair of sites takes all four value pairs, and the non-free triples are exactly the triangles. | proved; checked in a box | A |
| 2 | **Bond distance is graph distance + 1 (R2).** For any two sites at graph distance d, the least bond containing both has exactly d + 2 sites: one whole side of a triangle of side d together with its opposite corner, the side equal and the corner equal to it exactly when d is odd. No smaller set works, because every bond spans at most its size minus two. | proved; checked to d = 8 in every direction | A |
| 3 | **Every bond is native (R3).** At the flat three-class state every site is flipped by a change inside a disc of radius 4. | proved; checked by SAT | A |
| 4 | **The tool.** A pattern extends to a ground state exactly when a weighted digraph on its sites, built from the known height function, has no negative cycle; checked against SAT on a disc for 71,002 patterns. | proved (from the known height mapping); checked | A |

## Answer

Yes, in the plane: under NAE the triangular lattice is read faithfully, and its knots compose into an exact ruler: bond distance is
graph distance + 1 at every distance, with explicit bonds and a matching lower bound. On flat tori and Klein bottles the equality
stays computed: faithfulness on tori and Klein bottles of edge-width at least 5, the equality to distance 3 on tori of edge-width
at least 6, where short non-contractible loops make it fail on thinner tori. A corollary in the plane: bond balls are graph-distance
balls, so they grow quadratically and the law reads dimension 2 natively (proved, from R2).

## Reading

**Interpretation, not a theorem.**
- **Why the ruler is exact.** A ground state is a height function that rises by at most one per forward step. A pattern is forbidden
  when it asks the height to rise faster than that around a closed route, and each site of the pattern can supply at most half a
  unit of the needed excess. So covering a distance d costs d + 2 sites: a rigid side of equal values, which forces the height to
  climb, and a far corner that cannot meet it.
- **For question 9.** With nothing drawn and nothing named but the knot and how knots meet, the not-all-equal knot measures its own
  plane, and what it measures is the plane's graph distance. That is a native magnitude (A40) with the triangular lattice's
  hexagonal unit ball, not a round metric: the law reads the lattice's own geometry, as the doubling law read its board's.
- **What stays open.** Tori and Klein bottles, where the height function can wind.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Proved.** R1, R2 and R3 for the infinite triangular lattice.
- **Census-only.** None in the plane; the flat-world statements are `LONG-LOOP-20261111-001`'s (the equality on tori only).

## Stress test

The theorem covers every distance; `check.py` checks it to distance 8. The claim it extends, LONG-LOOP's distance-3 equality on
tori, has its own stress test (LONG-LOOP-S1).

## Review

An independent referee, a fresh agent given the proof and the code, checked every lemma and theorem with its own oracles (SAT on a
disc of radius 11 for non-extension, SAT on the 24 × 24 torus for extension, neither using the height criterion) and found R1 to R3
fully proved, with no error or gap in the mathematics. Its independent tests: the criterion matched on 55,756 random patterns; the
side-and-apex sets are bonds in all 6d directions for d ≤ 6, and the stated pattern is the only failing one (with its complement) for
d ≤ 4; no smaller bond in boxes to d = 4 (398,504 sets at d = 4); R3's flip needs radius 0 (classes 0 and 2) or 1 (class 1). Its
findings, folded in:
1. **Lemma 1's constant** (presentational): the normalization σ = h mod 2 is now stated, and Lemma 4 uses it.
2. **Why disc SAT speaks for the plane** (a gap in the checks): every state of a hex disc extends to the plane, now said in the proof;
   C3 uses the criterion on a stated box.
3. **The scope note** (overclaim): the flat-world equality to distance 3 was computed on tori only, not on Klein bottles, which got
   faithfulness only. Corrected in the proof and here; the pre-registration's wording is corrected by a note (`docs/CORRECTIONS.md`).

## Literature and provenance

- **Known.** The triangular Ising antiferromagnet's ground states (Wannier 1950) and their height mapping (Blöte and Hilhorst 1982;
  Nienhuis, Hilhorst and Blöte 1984); extension of height functions by difference constraints (Thurston 1990 for tilings); weak
  2-colourings of triangulations for existence.
- **Classification.** Known-with-delta: the tools are known; R1 to R3 as statements about the ground-state space's minimal
  non-shattered sets were not found in a bounded search. Folklore risk moderate.

## Workspace assumptions

- **Relied on.** A40 (counted length is native), A64 (the surface count names no face), through A63's conditional overturning.
- **Changed.** None.

## Ratio

- **Substantive.** The proof (six lemmas, three theorems), its finite checks, one referee pass.
- **Administrative.** The pre-registration, this note, the closure and one correction entry.

## Corrections

One, Not a block (`docs/CORRECTIONS.md`, 2026-11-11): the pre-registration said the flat-world result stays computed on tori
and Klein bottles to distance 3; the equality was computed on tori only.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — NAE's ruler as a theorem | **Status:** Successful | R1 to R3 proved in the plane |
| Local direction — NAE on worlds of knots alone | Continue | Flat worlds (winding heights) and bond balls remain |
| Broader exploration — G1 space from a law | Known alternatives | The count from growth; the ruler on tori |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A knot law measures its own plane exactly, nothing drawn |

**Corrections:** one, Not a block (above). **Goals:** a G1 checkpoint (capability gained), no goal change. **Assumptions:** none changed.
**Basket:** `LONG-LOOP-20261111-001#2` (the count from growth, 2/3, 1/3), `LONG-LOOP-20261111-001#3` (bond balls, 2/3, 2/3),
`GROW-FACE-20261110-001#1` (2/3, 1/3); none taken: the owner has paused new work.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The ruler on tori and Klein bottles | 2/3 — Substantial | 2/3 — Testable | Extend the criterion to quasi-periodic heights with a tilt; bound which tilts a short pattern can use in terms of edge-width → β = δ + 1 for δ below a function of edge-width, proved, or the first counterexample | Selected · awaiting go-ahead |
| 2 | The count from growth (was `LONG-LOOP-20261111-001#2`) | 2/3 — Substantial | 1/3 — Stated | A growth rule adding NAE knots while the reading stays faithful → closes into a surface, or not | Alternative · deferred |
| 3 | Other uniform knot laws on other surfaces | 2/3 — Substantial | 2/3 — Testable | The criterion for NAE on the 4-, 5- and 7-regular worlds, where heights do not exist as here → which have a ruler | Alternative · deferred |
| 4 | Write the knots-alone line up as a note | 1/3 — Modest | 3/3 — Ready | Four epics into one self-contained note (faithful reading, the count as input, the ruler) → a note an expert can check | Alternative · deferred |

1. **Tori and Klein bottles.** Payoff 2: it would prove the flat-world equality LONG-LOOP computed and explain its shortcuts.
   Concreteness 2: the torus states are the quasi-periodic height functions; the open step is bounding the tilt a short pattern sees.
2. **The count from growth.** As recorded.
3. **Other laws and surfaces.** Payoff 2: whether rulers belong to flatness. Concreteness 2: the criterion needs the height function,
   which only flat worlds of degree 6 have in this form.
4. **A note.** Payoff 1: result conversion. Concreteness 3.

**Recommendation.** Research directions, #1, awaiting the go-ahead; the owner has paused new work until tomorrow.
