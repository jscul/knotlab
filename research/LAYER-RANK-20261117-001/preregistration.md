# Why layered circuits need about d^0.4 phases: pre-registration

Epic `LAYER-RANK-20261117-001` (takes B184; goal G3), 17 November 2026. Frozen before any read-out. The code (`layer_rank.py`,
`gates.py`, `job.py`, `summarize.py` in `experiments/LAYER-RANK-20261117-001A/LAYER-RANK-20261117-001A-E001_layer_rank/`) was
written first and run only on its gates and timing smoke tests; no registered reading was taken. Code and run by this thread.

## The question

`SEQUENTIAL-WALL-20261116-001` measured that layered random monotone circuits (each gate AND or OR with chance 1/2, reading two
gates of the layer below) need about d^0.41 untangling phases at depth d, while unlayered random circuits need at most 4. What law
is behind it, and what does layering, an order designed into the meeting pattern, do to the nesting of open uses?

## Settled by construction (proved here)

In the limit of infinite width the inputs of a gate are independent, and the cumulative distribution
Q_L(r) = P(a gate of layer L is true with rank ≤ r) obeys, for L ≥ 2, **Q_{L+1}(r) = Q_L(r) − ½ q_L(r)²**, q_L(r) its mass at r.
Proof: an OR gate has rank ≤ r exactly when some input is true with rank ≤ r, with chance 2Q − Q²; an AND gate exactly when both
are, except when both have rank exactly r (an open use of equal standing, which gives r + 1), with chance Q² − q²; averaging the
two, the max and the min cancel. So **taking an alternative (OR) and joining (AND) cancel exactly, and only open uses of equal
standing move the ranks.** (`job.py` asserts the identity against the full recursion at every layer.) The true fraction stays 1/2
in this limit. At finite width w the one-layer update is exact given the layer's histogram; the deviation is sampling noise, and the
true fraction drifts like a Wright–Fisher martingale and fixes at 0 or 1 after about 1.4w layers.

## Derived (heuristic; advisor), to be tested

The continuum limit of the identity is ∂_L F = −¼ (∂_r F)², inviscid Burgers for the rank density among true gates. From a point
mass it gives a triangular density π(r) ≈ 2r/L on [0, √L]: mean (2/3)√L, sd √L/√18, largest/mean 3/2, P(tie) ≈ 4/(3√L). At fixed
rank, L·F_L(r) → β_r with β_1 = 4 and β_r − β_(r−1) = 2√β_r (β_2 = 6 + 2√5 ≈ 10.47), so μ_L ≈ (2/3)√L − ¼ ln L + O(1). The
measured d^0.41 is this logarithmic correction plus an offset, not a different exponent. Unlayered circuits obey the same equation
with L replaced by about ln n, hence √(ln n) + O(1), 2.6 to 3.7 for n = 10³ to 10⁶. At finite width, for L ≫ w, the advisor expects
linear growth with slope c/√w, c of order 0.5 to 1.

## Prior work in the program

`python3 -B scripts/track.py objects "layered random circuits Strahler number rank distribution depth" --until 2026-11-17 --exclude LAYER-RANK-20261117-001`

`python3 -B scripts/track.py objects "random monotone circuit untangling phases layered unlayered" --until 2026-11-17 --exclude LAYER-RANK-20261117-001`

`python3 -B scripts/track.py objects "Horton-Strahler random trees min max recursion" --until 2026-11-17 --exclude LAYER-RANK-20261117-001`

The searches return `SEQUENTIAL-WALL-20261116-001` (the measured d^0.41, this study's source), `CARRY-STRANDS-20261116-001`
(carrying distinctions on the same circuits; keeping gains little), `SPACE-ORDER-20261117-001` (phases on weaves) and unrelated
rows; they are discussed in the decision note.

## Prior work outside the program

Strahler numbers of random trees grow logarithmically (Flajolet, Raoult and Vuillemin 1979; Kemp; Meir, Moon and Pounder;
Devroye and Kruszewski; Brandenberger, Devroye and Reddad), for a fixed tree, not a least number over derivations. Layered growth
of random formulas (Savický; Brodsky and Pippenger; Valiant's amplification) has the same "two independent copies of the layer
below" structure. Max-type recursive distributional equations (Aldous and Bandyopadhyay). Not found: this recursion or its √L law.

## Predictions (frozen)

| # | Prediction (advisor's values) | Fails when |
| --- | --- | --- |
| G | gates pass; the cumulative identity holds at every layer of the recursion; every case runs | any fails |
| M1 | exponent of the mean rank over L = 10³ to 10⁵ in [0.505, 0.53] (tending to 1/2 from above) | outside |
| M2 | mean/√L in [0.60, 0.63] at L = 10³ and in [0.65, 0.662] at L = 10⁵ | either outside |
| M3 | exponent of the sd in [0.49, 0.52] | outside |
| M4 | L·F_L(1) in [3.95, 4.05] and L·F_L(2) in [10.3, 10.6] at L = 10⁵ (limits 4 and 6 + 2√5) | either outside |
| M5 | mean × P(tie) in [0.85, 0.93] at L = 10⁵ (limit 8/9) | outside |
| M6 | profile π(r)·L/(2r) at r = √L/2 in [0.9, 1.1] at L = 10⁵ | outside |
| M7 | slope of mean + ¼ ln L against √L between 10³ and 10⁵ in [0.64, 0.69] (limit 2/3) | outside |
| S1 | exact simulation at w = 2^17 and 2^20 agrees with the recursion within 5% (median of 3 samples) at depths d ≤ w/128 | any above |
| S2 | w = 1024: median largest rank over samples with some true gate in [31, 44] at d = 1024 and [75, 130] at d = 4096; all-false share in [0.10, 0.35] at d = 1024 and [0.35, 0.65] at d = 4096 | any outside |
| S3 | finite-width linear regime: on samples whose true fraction fixed at 1, c = √w × slope of the mean rank over L = 40w … 100w lies in [0.3, 1.5] for each w = 64 … 1024, and the largest c is at most 1.5 times the smallest | any fails |

## Runs and stop rule

One shared-runner job, 257 cases (the recursion to 10⁵; validation at 2^17 and 2^20; 50 samples at w = 1024 to d = 4096; 40 samples
for each w = 64 … 1024 to d = 100w), three workers; expected a few minutes. The study stops after this run and its read-out.

The advisor model (`claude -p --model claude-fable-5-2`) was consulted before this freeze. It reduced the recursion to the
cumulative identity, derived the Burgers limit and the β_r recursion, corrected my picture (layering does not spread standings
like a random walk: alternatives and joins cancel exactly, and only ties move the ranks), corrected my finite-width reasoning (the
breakdown is drift of the true fraction, not overlapping cones), and gave every numeric prediction above.
