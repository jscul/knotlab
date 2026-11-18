# Ball outlines under the disagreement count: pre-registration

Epic `COUNT-BALLS-20261118-001` (backlog B195; G1 and G16; tests A97 and A39), 18 November 2026. Frozen before the run. Code by
the thread (Claude), run by the thread; no Codex. The canonical K1–K3 test is unchanged.

## The question

Take a base and one of its distinctions, and collect every distinction within a given disagreement count of it. How does that
collection, the count's ball, grow as the count allowed grows, what does its outline (the members with a nearest partner outside)
look like, and does the growth read how many orders the base has, without names or history? The coordinator's words were "take a
state and collect all states within r disagreements of it"; the tracked direction B195 and the glossary's "ball" are about
distinctions, so the distinction side is the main reading and the state side (states within r disagreements of a state) is a
second arm.

Why it matters. Under bond distance every periodic law has a polygonal ball with rational Gołąb π, and no periodic law has a
round one (`LOGIC-CIRCLE-20261107-001`, proved); roundness was found to need aperiodicity, isotropic randomness or non-local hidden
information (`PINWHEEL-ROUND-20261107-001`, `ROUND-PRICE-20261108-001`). The disagreement count is the reading that carries every
not-all-equal base (`DISTANCE-ORDER-20261117-001`), so the same question asked of it tests whether the polygon verdict belongs to
periodic laws or to bond distance. On grown split bases the count is twice the L1 distance (`GRID-GROW-20261117-001`), on parity
bases it is blank (`DISTANCE-ORDER-20261117-001`, statement 4), and on the weave and the chain grid it gives no order but levels
that grow as the meeting pattern does (`DISTANCE-DIM-20261117-001`).

## In standard terms

The uniform weighting of the allowed states; the correlation C(x, y) = 1 − 2d/N of two distinctions (d their disagreement
count, N the number of states); τ = −log₃ |C|. Bases:
- **the endless six-regular weave under not-all-equal**: the literature's triangular Ising antiferromagnet at zero temperature,
  read on the plane (maximal-entropy measure), exact through honeycomb dimers (Kenyon's local statistics);
- **chain grids**: every co-knotted pair of the literature's square grid replaced by a chain of l not-all-equal knots, each with
  its own loose distinction; summing them out leaves the square-lattice Ising model at tanh K = (−1/3)^l, high temperature for
  every l; exact correlations by the Kac–Ward resolvent on the plane;
- **grown split bases**: states = splits of the distinctions (with complements and the two all-equal states), from betweenness
  knots; orders k = least colours of the splits' crossing graph, λ = Eppstein's lattice dimension;
- **parity bases**: states a linear code.

## Prior work in the program

Searches (`--until 2026-11-18 --exclude COUNT-BALLS-20261118-001`):

`python3 -B scripts/track.py objects "ball outline under the disagreement count round polygon" --until 2026-11-18 --exclude COUNT-BALLS-20261118-001`
`python3 -B scripts/track.py objects "correlation length anisotropy Wulff shape Ising triangular antiferromagnet correlation amplitude" --until 2026-11-18 --exclude COUNT-BALLS-20261118-001`
`python3 -B scripts/track.py objects "six-regular weave chain grid grown split bases orders lattice dimension ball growth" --until 2026-11-18 --exclude COUNT-BALLS-20261118-001`

- `MEET-TWIST-20261118-001` — unrelated (a coupling of KF3 presentations; matched on words).
- `DISTANCE-ORDER-20261117-001` — same object (the disagreement count) on the same weave: no betweenness; the weave's raw count puts
  the start's own class nearest. Taken: the count, statement 4 (parity blank) and 3(a) (the table determines these bases).
- `MEET-DIST-20261118-001` — a relative: how much of a grown base's nesting its unnamed counts carry; not outlines.
- `BOND-BALLS-20261111-001` — a relative: bond balls, not count balls.
- `DISTANCE-DIM-20261117-001` — same population (weave, chain grid): nearness levels grow quadratically; transfer gaps (chain grid
  to Onsager's 0.3691, weave critical). It measured no outline (its Limitations name B195). Taken: the bases and the gap numbers.
- `RULER-20261111-001` — same population: on the weave bond distance is steps apart plus one, so bond balls are the hexagon of steps
  apart. This study compares against that hexagon (the 0.931 alternative below).
- `WEAVE-LAWS-20261117-001` — same population: other knot laws on the weave; B195 queued there for OR and hard hexagons (not run here).
- `STATE-RULES-20261117-001` — same population for the census (its growth engine is used unchanged; k and λ as there).
- `LOGIC-CIRCLE-20261107-001` (found by its ticket) — the outline verdict under bond distance, which this study tests under the count.

## Prior work outside the program

- Weave: Stephenson (J. Math. Phys. 5, 1009 (1964); 11, 413 and 420 (1970)): C(r) ~ a r^(−1/2) cos(Q·r) at zero temperature, with
  an exact amplitude; Blöte and Hilhorst (1982), Nienhuis, Hilhorst and Blöte (1984): the height mapping and Coulomb gas, spin
  exponent η = 1/2; Kenyon (1997) for the honeycomb local statistics. Isotropy of a follows from an isotropic stiffness (three-fold
  symmetry); I found no published ray-by-ray check, so W1 is a check of known physics.
- Chain grid: Onsager (axis rate); Cheng and Wu (Phys. Rev. 164, 719 (1967)) for the asymptotics in every direction; the decay rate
  in every direction as the support function of the curve cosh q₁ + cosh q₂ = cosh² 2K / sinh 2K, dual to the 2D Ising crystal's
  Wulff shape (Rottman and Wortis 1981; Avron, van Beijeren, Schulman and Zia 1982; Zia and Avron 1982; Holzer 1990; Akutsu and
  Akutsu 1990); Campanino, Ioffe and Velenik (2003): Ornstein–Zernike decay above Tc with an analytic, strictly convex rate.
- Growth against dimension: lattice dimension (Eppstein 2005), trees (ceil(leaves/2), Ovchinnikov), isoperimetric dimension.
- Known, so the contribution is the reading: that the program's count, which carries the information, has smooth outlines on
  periodic laws, against bond distance's polygons, and what its growth does and does not see of the orders.

## Settled by construction (stated, not tested)

- Box split bases of sides n₁ × … × n_d: the count is twice the L1 distance; the ball is the literature's cross-polytope clipped to
  the box (in two orders the taxicab diamond, Gołąb π 4); from an inner start the outline at count 2j has 4j members in two orders
  and 4j² + 2 in three; the growth exponent is d = k = λ. Q_d: binom(d, j) at count 2j. Checked on 7 × 7, 5 × 5 × 5, Q_4.
- The 2 × m ladder (k = λ = 2) and the comb with m spine distinctions (a tree: k = 1, λ = ceil(leaves/2), 5 at m = 10) have outlines
  of 4 members at every count from 4 up to twice the steps to the nearer end, from a middle spine distinction (checked at
  m = 10): the growth is the same, the orders differ.
- Parity bases: the count is N/2 on every pair, so every ball is the start alone or everything.
- On a base with λ = 2 (NN's grids, `NEVER-NEST-20261118-001`), by the definition of λ the count is twice the L1 distance in the
  two orders: a two-way ruler, its balls taxicab diamonds clipped to the grown shape (`NEVER-NEST-20261118-001#4`).
- Chain grid closed form (computed from the formula, not a measurement): axis 0.369070 and diagonal 0.523719 per step in τ at
  l = 1; largest to smallest rate per unit of the literature's drawing 1.003400, 1.068608, 1.141877 at l = 1, 2, 3, tending to √2;
  Gołąb π 3.141701, 3.182439, 3.297932, 3.418830 (l = 4), 3.589379 (l = 6), tending to 4. Strictly convex and analytic for every l
  (a sublevel set of a strictly convex analytic function; its polar has the same property).
- Parity bases on the state side: every state's profile is the code's weight enumerator.

## Exploration disclosed

Before the freeze, building and gating the code, I saw: weave correlations at (1,1), (3,0), (2,2), (2,0), (−2,5), (4,−7), (−3,−3),
(5,2), (9,0) (amplitudes √r·C between 0.621 and 0.638 at r ≤ 9) and finite tori L = 6, 9, 12 at four targets; chain-grid
correlations at a few short separations (agreement of two formulas, Onsager's nearest value); the restricted census's class counts
and (k, λ) counts by n (P-one-split: 4, 12, 101, 1,656, 59,675 classes at n = 4 to 8; cheapest: 1 to 14 classes) but no reading
of any profile. The advisor (below) computed the row exactly to r = 482 and gave its corrections; W1b, W1c and W3b are taken from
its analysis.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates (`checks.py`, all pass before the run): weave kernel 1/3 on a knot's pairs, exact = quadrature, nearest −1/3, path independence, row by dimers = the independent row Toeplitz formula, float = mp, a wrong pair map detected, finite weaves L = 6, 9 approach the endless values; chain-grid reduction literal = reduced (2 × 2 at l = 1, 2, 3; 3 × 3 open and wrapped at l = 1), two classes on the open 3 × 3, the loose identity C(x, c) = −[C(x, a) + C(x, b)]/2, wrong weights detected, Kac–Ward = brute force on a 4 × 4 patch, Onsager's nearest value, path independence; Gołąb π of the circle, taxicab and hexagon; lattice dimension = brute force; the box, ladder and comb layers | any fails |
| W1 | Weave, own class: A = √r·C along the repeats (4,1), (5,2) and (1,1) at their largest separations (r ≈ 56–61) equals the row's A (fit a∞(1 + c/r²) on r ≥ 30) within 1e-3, and is not within 0.05 of 0.931 times it (the steps-apart hexagon) | either |
| W1b | The deviation from the row shrinks from the middle separation to the largest on each repeat | any repeat grows |
| W1c | (advisor's symmetry argument, exploratory) dev·r² at the largest separation is positive and ordered (4,1) < (5,2) < (1,1) | not |
| W2 | The row's own-class log-slope between r = 57 and 60 is −1/2 within 0.005 | otherwise |
| W3 | Other classes along the row: the mean of √r·C at r = 58 and 59, over a∞, is −1/2 within 2e-3 | otherwise |
| W3b | Their relative difference is 1/(4·58) + 1/(4·59) within 20% | otherwise |
| W4 | a∞ (row) equals the literature's 0.6322260804 within 1e-3 relative | otherwise |
| W5a | Every scanned own-class distinction (r ≤ 22) has C > 0 and every other one C < 0, so the raw count's balls below N/2 hold only the start's class | any exception |
| W5b | The raw-count ball {C ≥ u} at u = 0.17 and 0.15 has 2π/(3√3)·a⁴·u^(−4) members within 5% | otherwise |
| W6 | Outline (ball members with one of their six count-nearest outside the ball) against ball, log-log slope over u = 0.30 … 0.15: in [0.40, 0.60] ((d − 1)/d with d = 2) | outside |
| W6b | Ball against 1/u, log-log slope in [3.5, 4.5] (d/η = 4) | outside |
| C1 | Chain grids l = 1, 2, 3: the Richardson rate estimate along (1,0), (1,1), (2,1), (3,1), on the separations where the two Kac–Ward formulas agree within 1e-8 (at most r = 40), equals the closed form within 1e-3 relative (rays with fewer than 6 such points not scored) | any scored ray off |
| C1b | The plain successive-ratio estimate at the largest stable separation within 3e-3 | any off |
| C1c | At l = 1 the measured rate ratio (1,1)/(1,0) equals the closed form's 1.003400 × √2 within 1e-3 relative (nearly round, not round) | otherwise |
| C4 | Chain grid l = 1, grid distinctions within 22: outline (members with one of their four τ-nearest outside) against τ-ball, log-log slope over τ = 2 … 7 in [0.40, 0.60] | outside |
| C4b | τ-ball against τ, log-log slope in [1.6, 2.4] (polynomial, quadratic: unlike the weave, where it is exponential in τ) | outside |
| C4c | Raw count at l = 1: C > 0 exactly at even steps apart (two classes) | any exception |
| G1 | Reading (a), the multiset of sorted count rows, determines k and λ on the cheapest population at every n ≤ 12 and on the one-split population at every n ≤ 7 | a group with two values |
| G2 | Reading (c), the multiset of sorted state rows, fails to determine k on the one-split population at n = 4 or 5 (XOR-translating every state by one state keeps all state distances) | no failure |
| G3 | One size past: reading (a) determines k and λ on the one-split population at n = 8 | a group with two values |

## Runs and stop rule

`run.py --part` for weave_rays (exact, 40 digits), weave_scan (floats, every distinction within 22 of the start), chain_rays,
chain_scan, outline_cf, census (cheapest to n = 12, one-split to n = 8) and state_side (descriptive: a finite weave of 6 × 6 and
the boxes 7 × 7, 4 × 4 × 4); then `run.py --score`. Expected well under an hour in all on this machine; the census at n = 8 is
the longest part and registers a LONG_RUNNING row if it passes ten minutes. One run; no change to cases, readings, predictions or
decision rules after seeing results; any later look is post hoc and labelled. Stop at the read-out, then proofs of the settled
parts, the referee hand-off and the report.

Advisor. `claude -p --model claude-fable-5-2` was asked before the freeze (question and answers in the epic's `advisor/`). The first
call, without `--tools ""`, fell back to another model, which ran its own scripts and gave the row's exact Toeplitz form, the
amplitude, the corrections, a census of partial cubes and the critique of the state side; the second call was answered by
claude-fable-5-2 (checked in `modelUsage`). Both agreed on the closed form and the amplitude. Changes from my draft: W1 tightened
from 1% to 1e-3 with W1b and W1c added; W3 restated from "equal r" (impossible: own and other classes never share a separation) to
the mean of r = 58, 59 with W3b; W4 and W5a added; W6 and W6b added on Fable's suggestion that the outline's exponent against the
ball's separates the dimension d from the law's exponent η; G1 and G2 reversed from my draft (I had expected (a) to fail and (c)
to succeed; both advisors expected the opposite: (a) loses only the order of rows, (c) is blind to translating every state by one
state); C1 given Richardson extrapolation and a stable range, after the two formulas were seen to part at small t. The fallback
model's second suggestion, a reading of "two neighbours agree" variables, was not taken: those are XOR values, and the guardrails
forbid deriving a distance from them.
