# Why layered circuits need about d^0.4 phases

Epic `LAYER-RANK-20261117-001`, 17 November 2026, by Claude; takes B184. Goal G3. Referee pending. Pre-registration:
[preregistration.md](preregistration.md), frozen in commit `7bf1d9c59` at 17:25:52 UTC before the run (17:26 to 17:29 UTC).
Experiment: [code and contract](../../experiments/LAYER-RANK-20261117-001A/LAYER-RANK-20261117-001A-E001_layer_rank/),
[summary](../../artifacts/LAYER-RANK-20261117-001A/LAYER-RANK-20261117-001A-E001_layer_rank/summary.json).

## The answer

Layered random circuits need about (2/3)√d untangling phases, and the d^0.41 measured earlier was this law's slowly vanishing
logarithmic correction, not a different exponent. The mechanism is one exact identity.

In a gate's derivation, taking the better of two alternatives (OR) and joining two strands (AND) cancel exactly. Only an open use of
two strands of equal standing (an AND of two inputs of the same rank, which costs a phase) moves the ranks. With infinite width the
cumulative rank distribution obeys **Q_{L+1}(r) = Q_L(r) − ½ q_L(r)²** (proved, below). Each tie raises a strand and spreads the
standings, which makes the next tie rarer: nesting limits itself.

The continuum limit is inviscid Burgers. Its solution, confirmed by the frozen numerics to depth 10⁵, has these properties:

- a triangular standing profile reaching √d;
- mean (2/3)√d − ¼ ln d + O(1) (at 10⁵: mean/√d = 0.658, and the slope of mean + ¼ ln d against √d is 0.666);
- exactly 4/d of true gates at standing 1, and 10.47/d at standing ≤ 2, the predicted limits 4 and 6 + 2√5.

The largest standing among 1,024 gates by the recursion is 4, 5, 6, 9, 12, 16 at d = 8 … 256, against 4, 5, 7, 9, 11, 17 measured in
`SEQUENTIAL-WALL-20261116-001`: within one everywhere. Unlayered circuits obey the same equation with depth about ln n, hence
√(ln n), which is why they stayed at 2 to 4. At finite width the true fraction drifts and fixes. Once all gates are true, the
standings grow linearly, about c·d/√w with c from 0.70 (w = 64) to 1.01 (w = 1,024).

**What the knot picture explained.** The cancellation is the explanation, and it is stated in the program's words: alternatives and
joins balance, so only equal-standing open uses build nesting, and they build it at a rate that falls as the standing spreads.
Layering matters because every gate then draws its two strands from the same standing distribution, an order designed into the
meeting pattern. My first picture ("layering spreads standings like a random walk") was wrong, as the advisor pointed out:
layering spreads nothing, and the ties make the spread. As mathematics this is a max/min recursion reducing to Burgers. I found no
statement of it in the Strahler literature, which treats fixed trees and gets logarithms.

## The identity (proved)

For L ≥ 2 (when every true gate has rank at least 1), with inputs independent:

- an OR gate has rank ≤ r exactly when some input is true with rank ≤ r: chance 2Q − Q²;
- an AND gate has rank ≤ r exactly when both inputs are true with rank ≤ r, except when both have rank exactly r (then r + 1):
  chance Q² − q².

Each gate is one or the other with chance ½, so Q_{L+1}(r) = ½(2Q − Q²) + ½(Q² − q²) = Q − ½q². `job.py` asserted it against the full
recursion at every one of 10⁵ layers. The true fraction p = Q(∞) stays ½. At finite width the one-layer update is exact given the
layer's histogram; deviations are sampling noise.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | gates; identity at every layer; all cases | held | 257 of 257; identity at every layer |
| M1 | mean exponent 10³–10⁵ in [0.505, 0.53] | held | 0.513 |
| M2 | mean/√L 0.60–0.63 at 10³, 0.65–0.662 at 10⁵ | held | 0.619, 0.658 |
| M3 | sd exponent 0.49–0.52 | held | 0.504 |
| M4 | L·F(1) → 4, L·F(2) → 6 + 2√5 | held | 3.9995, 10.4707 |
| M5 | mean × tie → 8/9 | held | 0.875 at 10⁵ (0.853 at 10⁴, rising) |
| M6 | triangular profile | held | 1.020 at half the front |
| M7 | slope of mean + ¼ ln L against √L → 2/3 | held | 0.666 |
| S1 | simulation at w = 2^17, 2^20 within 5% at d ≤ w/128 | held | at most 3.0% |
| S2 | w = 1024: largest rank 31–44 at d = 1024, 75–130 at 4096; all-false shares | **failed** at d = 4096 | 40 at 1024 (held); 142.5 at 4096, above 130; all-false 0.12 and 0.60 (held) |
| S3 | finite-width linear regime, c in [0.3, 1.5], spread ≤ 1.5 | held | c = 0.70, 0.76, 0.84, 0.95, 1.01 for w = 64 … 1024 (ratio 1.44, rising with w) |

10 of 11 held. S2 failed because the finite-width growth after fixation is faster than the advisor's guessed slope. S3's c rising
with w (not flat) says the collapse is imperfect at these widths.

### The recursion

| L | mean | mean/√L | sd | L·F(1) | L·F(2) | mean × tie |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | 2.11 | 0.666 | 0.86 | 2.78 | 6.65 | 0.656 |
| 100 | 5.92 | 0.592 | 2.34 | 3.76 | 9.83 | 0.705 |
| 1,000 | 19.58 | 0.619 | 7.29 | 3.97 | 10.38 | 0.802 |
| 10,000 | 64.51 | 0.645 | 23.36 | 3.996 | 10.46 | 0.853 |
| 100,000 | 208.06 | 0.658 | 74.31 | 3.9995 | 10.471 | 0.875 |

## Prior work in the program

`SEQUENTIAL-WALL-20261116-001` (the measured d^0.41 and the unlayered 2 to 4, both now explained); `CARRY-STRANDS-20261116-001`
(carrying distinctions on the same circuits: keeping gains little, consistent with ties being between independent strands);
`SPACE-ORDER-20261117-001` (order from steps apart on weaves; here order comes from layering).

## Limitations

The identity needs independent inputs, which holds exactly in the infinite-width limit; the asymptotics are a continuum argument
confirmed numerically, not proved. Only one circuit model (AND and OR with chance ½, true inputs with chance ½); a different OR
share changes the true fraction and the rate.

## Reproduce

```sh
.venv/bin/python -B experiments/LAYER-RANK-20261117-001A/LAYER-RANK-20261117-001A-E001_layer_rank/gates.py
.venv/bin/python -B scripts/longrun.py launch experiments/LAYER-RANK-20261117-001A/LAYER-RANK-20261117-001A-E001_layer_rank/job.py --out RUN --workers 3 --case-mem 2G
.venv/bin/python -B experiments/LAYER-RANK-20261117-001A/LAYER-RANK-20261117-001A-E001_layer_rank/summarize.py RUN
```

## Advisor

Consulted before the freeze. It reduced the recursion to the cumulative identity, derived the Burgers limit, the β_r values and
every numeric prediction, and corrected two of my pictures:

- random-walk spreading: in fact the ties create the spread;
- overlapping cones at finite width: in fact the drift of the true fraction.

Its only miss was the slope after fixation at w = 1,024 (S2).

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: why layered circuits need about d^0.4 phases | **Status:** Successful (referee pending) | An exact identity and its √d law, confirmed to depth 10⁵; the old measurements reproduced within one; 10 of 11 held |
| Local direction: phases of random circuits | Practically exhausted | The law is known now, layered and unlayered |
| Broader exploration: Strahler-type recursions | Known alternatives | Max-type recursive distributional equations (Aldous and Bandyopadhyay) |
| Long-term goal: G3 | Capability gained | A mechanism for how designed order forces nesting: only equal-standing open uses build it, and they slow themselves |

**Next step:** Research directions. Selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A97's test: do equal bond-distance tables force equal relations? (the owner's "distance is the only form of information") | 3/3, would test the owner's reading of information directly | 3/3, a census of small not-all-equal patterns grouped by bond-distance table | Enumerate small patterns, group by bond-distance table, compare their allowed-state relations → stop at a counterexample or at the largest size checked | Selected · not started |
| 2 | Parity knots on weaves (rules that reach past the rim): does the one-step light cone hold? | 2/3 | 2/3 | Phases of elimination against steps apart on parity weaves → a clear scaling | Alternative · deferred |

**Corrections:** none. **Goals:** G3 checkpoint (capability gained); no goal changed. **Assumptions:** none new. **Basket:** read;
B184 taken by this epic.
