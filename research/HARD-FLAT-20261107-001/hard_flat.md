# Hardness needs a flat disc, not roundness

Epic `HARD-FLAT-20261107-001` (program complexity), 2026-11-07.

## The question

- **The approval.** This is `GROW-COIN-20261107-001`'s selected next step, under the owner's standing mandate. It was then run as the
  last check of the sphere line, after the owner asked on 2026-11-08 to wrap up open lines before widening them.
- **The question.** The round knot spheres need a witness, checked or grown. Does the knot's hard contradiction need roundness, or
  only corners that are far apart?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Flat states on every two-kind sphere.** The frames are flat at three-point faces and have label holonomy −1 at each of the six digons, so a flat state cut along disjoint paths to the digons violates exactly one line, at its vortex. | proved (`FLAT-STATES-20261107-001A`'s argument is local); computed on 16 spheres | A |
| 2 | **The Sperner reduction needs only a flat disc.** `FLAT-STATES-20261107-001B`'s reduction of one-sided Sperner_m uses only a corner-free lattice triangle of side 2m and cut paths from its boundary to the digons. So on every such sphere the knot needs resolution width at least c·m. | known-with-delta; proved | A |
| 3 | **Hardness follows the flat radius.** The width is at least c′ times the flat radius, when that disc's rim reaches the digons, and at most O(√n). Spheres with flat radius of order √n are hard, round or not. | proved | A |
| 4 | **Grown lopsided spheres are fat in the sample.** Their flat radius is 0.14 to 0.35 √n, against 0.25 √n on the octahedral spheres; elimination width 1.2 to 1.9 √n. On thin tubes the largest disc reaches around the band. | computed (8 grown spheres up to 252 points) | A |

## Answer

The knot's hard contradiction does not need roundness. It needs a large flat disc, and the round spheres have one, as do the lopsided
spheres that local growth closes in the sample. Roundness costs a witness, but hardness, as far as resolution width shows, does not.

## Reading

**Interpretation, not a theorem.** For G3, hardness at three places: the hard part of the knot's contradiction lives in a flat region
far from every corner, where Sperner's lemma sits. A law needs to tell places apart only enough to keep its six corners away from one
large disc. It need not lay them out exactly.

## Literature and provenance

- **Sources.** `FLAT-STATES-20261107-001A` and `001B`, and `SPHERE-WIDTH-20261107-001B`, proved for the octahedral sphere.
- **Classical inputs.** Sperner's lemma as a search problem: Papadimitriou 1994; Crescenzi–Silvestri 1998; Itsykson, Malova, Oparin
  and Sokolov 2014.
- **The new part.** The reduction needs only a flat disc, so hardness follows the largest corner-free disc.

## Ratio

Since the epic opened:
- **Substantive.** One proof family.
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
| This attempt — does hardness need roundness? | **Status:** Successful | No: a large flat disc suffices for width Θ(√n) |
| Local direction — the sphere line (SPHERE-GROWTH, GROW-COIN, this) | Paused | Wrapped up at the owner's request |
| Broader exploration — G1 and G3 | Known alternatives | The plane (pinwheel atlas); counting and proof systems |
| Long-term goal — G3 Hardness at three places | Capability gained | Hardness lives in a flat disc; roundness and its witness are not needed |

**Corrections:** none. **Goals:** G3 checkpoint, capability gained; G1 unchanged since `GROW-COIN-20261107-001`.

The sphere line is paused, not exhausted. It leaves open whether random accretion stays fat as it grows, whether resolution size also
follows the flat radius, and a theorem for every accretion law.

**Next step:** Research directions — No next action selected

The owner asked on 2026-11-08 to wrap up open lines and return to them if they look interesting. These are the candidates for when the
line reopens.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Do grown spheres stay fat? | 2/3 — Substantial | 2/3 — Testable | Flat radius of random accretion up to 10⁴ points → a constant fraction of √n, or decay | Alternative · deferred |
| 2 | Size follows the flat radius | 2/3 — Substantial | 2/3 — Testable | Carry `SPHERE-SIZE-20261107-001`'s islands into a flat disc → 2^Ω(r), or a gap | Alternative · deferred |
| 3 | Every accretion law (G1) | 2/3 — Substantial | 2/3 — Testable | An order that splits the equator, then a completion → a theorem, or a law that escapes | Alternative · deferred |
| 4 | A note on the sphere line | 1/3 — Incremental | 3/3 — Ready | Write up seams, coins and flat discs with a replay → a reviewed note | Alternative · deferred |

1. **Fat growth.** If random accretion keeps a flat disc of order √n, a witness-free local law grows hard contradictions with positive
   probability (G3). The question is precise, and the sample's 0.14 to 0.35 √n is the evidence. It is uncertain because growth that
   rarely closes may favour small or thin outputs.
2. **Size.** This would carry the size bound 2^Θ(√n), not only the width, to every fat sphere. The island packing lives in a flat
   region, which suggests it carries over; that is not checked.
3. **Every accretion law.** This is carried from `GROW-COIN-20261107-001`.
4. **A note.** This would make the line reviewable without new results.
