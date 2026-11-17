# Which knot laws on the weave give a ruler from their counts: pre-registration

Epic `WEAVE-LAWS-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead (the first direction of
`DISTANCE-DIM-20261117-001`). Goals G1 and G16; tests A97. Frozen before any read-out of ticket B. The canonical K1–K3 test is
unchanged.

## The question

On the six-regular weave, which three-place knot laws are:
- **disordered,** so the log of their counts grows linearly with distance at large scale (a ruler);
- **critical,** where it grows only like a logarithm;
- **frozen or ordered,** with no distance at all?

And for which laws is the law's information pairwise, carried by its pair counts? The owner's premise asks for one distance that
carries the information and also steps outward from a start without skipping. In those terms the question is which laws do both
on the weave.

**What a ruler here does and does not show.** The weave is one meeting pattern of knots. A ruler read from a law's counts on it
reads how the knots meet in that pattern: two-way on the weave, as the dimension test found for nearness levels
(`DISTANCE-DIM-20261117-001` and its referee). Nothing here shows a law adding or choosing a dimension. The question that follows,
which meeting patterns are typical or rare and whether knots alone build an order, is left for later.

## What is classical, by class

| Class | Law tested | The model in the literature | Known criticality |
| --- | --- | --- | --- |
| a complementary pair (not-all-equal) | NAE; signed NAE with consistent signs | the zero-temperature triangular Ising antiferromagnet (L2: gauge copies) | critical (Wannier 1950; Stephenson 1964, 1970; Blöte and Hilhorst 1982; Nienhuis, Hilhorst and Blöte 1984); conformal finite-size scaling with spin dimension x = 1/4 gives gap × width → π√3·x/ln 3 ≈ 1.238 |
| the same | signed NAE with inconsistent signs (place 1 odd; place 3 odd; NAE up with place 1 or 3 odd down) | not a gauge copy; I know of no study | unknown |
| three of one parity | not exactly two ones | hard hexagons at activity one, plus the all-ones state (L3; Baxter 1980) | disordered (critical activity ≈ 11.09); κ ≈ 1.39549 states per distinction |
| four (parity) | parity | linear algebra over two values | frozen: 4 states or 1 (L3) |
| one excluded state | OR (some 1 on every knot) | the "no empty triangle" gas; no solution known to me or the advisor | unknown |
| two at distance two | three place orientations of {000, 0xx}-type | none known | unknown |

Information (L1, proved): only the not-all-equal class is pairwise. The other classes have degree three, and whether their bases
collide on pair counts is decided by the census.

## Readings (ticket B)

- **Transfer spectrum.** For each law and each width 3 to 12: the row transfer matrix's λ₀, the multiplicity of its modulus, λ₁
  (the largest modulus below it), the gap log₃(λ₀/|λ₁|), gap × width, and λ₀^(1/width), states per distinction.
- **Classification by the trend over widths:**
  - *disordered:* the gap settles to a positive value, changing by less than 10% from width 9 to 12 and above 0.05 at width 12;
  - *critical:* the gap falls with width while gap × width changes by less than 15% from 6 to 12;
  - *frozen or ordered:* states per distinction tend to 1, or the gap falls faster than one over the width.
- **Direct correlation.** For each disordered law, the connected (Pearson) correlation of a distinction with the one r rows away,
  on the infinite cylinder of width 12. Its decay rate per row, from r = 6 to 12, is compared with the gap. This checks that λ₁
  couples to a single distinction.
- **Census.** For NAE, OR, not-exactly-two, parity, and the distance-two class (knots in any place order): every relation the law's
  knots allow on n = 4, 5 and 6 labelled distinctions (n = 6 if under two million relations), and the number of distinct (N, single
  counts, pair counts) keys. The bases are plain conjunctions of the law's knots, with no literals and no repeated triples.

## Predictions (frozen; checked with the advisor)

| # | Prediction | Fails when |
| --- | --- | --- |
| P1 | NAE (calibration; the gaps at 6, 9 and 12 were seen in `DISTANCE-DIM-20261117-001`): gap × width at widths 6, 9, 12 rises toward 1.238 and is within 0.03 of it at 12 | otherwise |
| P2 | Signed NAE with consistent signs (place 2 odd): critical, by the classification | otherwise |
| P3 | Not-exactly-two (hard hexagons): disordered; states per distinction within 0.001 of 1.39549 at width 12 | otherwise |
| P4 | OR: disordered | otherwise |
| P5 | Parity: frozen (states per distinction 1 at every width) | otherwise |
| P6 | Signed NAE with inconsistent signs, all four: frozen or ordered. *Disclosed: the proof check counted 64 states for each on the 6 × 6 torus before the freeze, which is what this prediction rests on.* | any is disordered or critical |
| P7 | For each disordered law, the direct correlation decays at the gap's rate within 10% | otherwise |
| P8 | Census: NAE has one key per relation at n = 4, 5, 6 (proved); parity collides at n = 4; OR has one key per relation at n = 4 and 5 and its first collision at n = 6 (the advisor's Pasch trade) | otherwise |

No prediction for:
- the three distance-two orientations on the weave;
- not-exactly-two's and the distance-two class's census.

**The headline, stated before running.**
- **If P2 and P6 hold:** among the uniform and two-kind laws tested on the weave, every law whose information is pairwise (the
  not-all-equal class) is critical or frozen. So none has a pair-count distance that both carries all its information and is a
  ruler on the weave's meeting pattern. The laws that do give a ruler (P3, P4 and any disordered distance-two orientation) need
  counts of three to carry their information.
- **If an inconsistent signed NAE law is disordered:** it is a law whose pair counts carry its information (L1) and also give a
  ruler on the weave. That is the premise's positive case on this meeting pattern.
- **The quantifiers.** "Carries the information" is about the family of all bases of a law. "Ruler" is about one base, the weave.

## Prior work in the program

`python3 -B scripts/track.py objects "knot laws on the weave transfer gap critical hard hexagons" --until 2026-11-17 --exclude WEAVE-LAWS-20261117-001`

`python3 -B scripts/track.py objects "three-place knot classes symmetric laws weave" --until 2026-11-17 --exclude WEAVE-LAWS-20261117-001`

- `DISTANCE-DIM-20261117-001` and its referee: the weave is critical under NAE; an off-critical chain grid gives a ruler.
- `DISTANCE-ORDER-20261117-001`: NAE information is pairwise (statement 3).
- `PINNING-20261031-001`: the 34 three-place knots in 5 classes.
- `KNOTS-ALONE-20261111-001`, `RULER-20261111-001`: NAE on weaves read through bond distance.
- `SEQUENTIAL-WALL-20261116-001`: a relative (the 34 three-place knot laws classified by the complexity of their forcing).

## Prior work outside the program

- **The triangular antiferromagnet and its conformal data:** Wannier; Stephenson; Blöte and Hilhorst; Nienhuis, Hilhorst and Blöte;
  Cardy for the finite-size scaling.
- **Hard hexagons:** Baxter 1980.
- **Frustration and gauge:** Mattis; Toulouse; Fradkin, Huberman and Shenker.
- **Fourier degree of Boolean functions:** O'Donnell's book.
- **The Pasch configuration.**

## Runs and stop rule

One script, `run.py`, one process, expected under twenty minutes. The study stops after its read-out, followed by A97 status, the
decision note, the referee hand-off and the report.

The advisor model was consulted before this freeze. It:
- corrected L2: the first draft claimed every not-all-equal-class weave is critical, and inconsistent assignments are not covered;
- gave the three-way classification and the direct-correlation check;
- gave the conformal value 1.238, the OR and parity census predictions, and the identification checks.
