# One distance for parity and not-all-equal knots: pre-registration

Epic `CUMULANT-DIST-20261118-001` (sub-goal B200; G1 and G16; tests A97), 18 November 2026. Frozen before the run. Code by the
thread (Claude), run by the thread; no Codex. The canonical K1–K3 test is unchanged.

**Why B200 and not the ladder on not-all-equal bases.** The coordinator's go-ahead (18 November 2026, 07:08 UTC) was
`ROW-ARRANGE-20261118-001`'s direction 3, with the instruction to take B200 itself if a concrete handle appeared while designing
it. One did: the cumulant distance below, which on chains of three knots gives steps apart exactly under parity, under
not-all-equal and under every mixture. This study takes B200.

## The question

Each distance the program reads from the states is blank where the other works: bond distance (the least knot holding both)
reads parity systems but is two for every pair of a betweenness grid; the disagreement count reads not-all-equal bases but is flat
on every parity base. Is there one distance, read from the allowed states alone, that reads both? The candidate:

δ(x, y) = min over sets S of distinctions containing x and y of (|S| − 2) + τ(κ_S),  τ(k) = max(0, −log₃ |k|),

where κ_S is the joint cumulant of the spins s = (−1)^value of the distinctions in S under the uniform weighting (sets with
κ_S = 0 are skipped). It is invariant under renaming distinctions and under flipping a distinction's values. Read in the program's
words: a set of distinctions counts as close when it is bound together beyond what its parts explain (its cumulant), and each
distinction it needs costs one step; one knot is one step, under either law.

## In standard terms

Joint cumulants (Ursell functions) of ±1 variables; the moment–cumulant relation over set partitions. On linear codes (parity
bases), moments are ±1 on dual codewords and 0 elsewhere; circuits of the dual matroid are the minimal dual codewords. On
trees of three-place constraints, −log|correlation| is additive (the phylogenetic log-det or information distance). Switching
(flipping a variable's values) is the gauge of Seidel's two-graphs.

## Prior work in the program

`python3 -B scripts/track.py objects "one distance read from the states for parity and not-all-equal bases, cumulant" --until 2026-11-18 --exclude CUMULANT-DIST-20261118-001`
`python3 -B scripts/track.py objects "joint cumulant connected correlation Ursell function information distance tree metric switching two-graph" --until 2026-11-18 --exclude CUMULANT-DIST-20261118-001`
`python3 -B scripts/track.py objects "knot trees parity not-all-equal mixed chains rings chain grid weave patch split line" --until 2026-11-18 --exclude CUMULANT-DIST-20261118-001`

- `DISTANCE-ORDER-20261117-001` — same object family (pair counts): τ equals steps apart on not-all-equal knot trees (proved);
  parity is invisible to pairs. This study extends both to the cumulant distance.
- `DISTANCE-INFO-20261117-001` — a relative: bond-distance tables do not determine not-all-equal bases; not a cumulant reading.
- `RANDOM-FATES-20261112-001` — unrelated (growth of not-all-equal knots; matched on words).
- `DISTANCE-DIM-20261117-001` — same population for the chain grid and the weave (nearness levels, transfer gaps).
- `COUNT-BALLS-20261118-001` — same population: the count's outlines on the weave and chain grids; reused code for the chain grid.
- `WEAVE-MIX-20261117-001` — unrelated (arrangements on the weave).
- `CUBIC-FROM-A-KNOT-20261117-001`, `BOND-NEXT-JOIN-20261117-001` (found by their records) — bond distance on parity systems,
  which this distance must reproduce there.

## Prior work outside the program

Ursell functions and cumulant inequalities (Lebowitz; Aizenman's tree bound; Sylvester); connected information and irreducible
correlations (Schneidman, Still, Berry and Bialek 2003; Linden, Popescu and Wootters), whose canonical example is parity; tree
metrics from correlations (Cavender–Farris–Neyman, log-det distances, Steel; information distances in latent-tree learning,
Choi, Tan, Anandkumar and Willsky; Chow and Liu); matroid circuits and connectivity (Tutte); two-graphs and switching (Seidel;
Harary and Zaslavsky's signed graphs; Toulouse's frustration); the cut cone and circular split systems (Deza and Laurent; Bandelt
and Dress). Not found: this functional, and the statements below for knot bases.

## Settled by construction (stated, not tested; proofs in ticket A, several from the advisor)

- **Parity bases** (advisor): moments are 1 on dual codewords and 0 elsewhere. κ_S ≠ 0 forces the restricted matroid on S to be
  connected, and in a connected matroid any two elements lie on a common circuit inside S; a circuit has κ = ±1. So
  δ(x, y) = (least circuit through x and y) − 2, which is bond distance minus one (a circuit is exactly a set whose states form a
  parity knot; gate 4 checks it).
- **Parity knot trees** (advisor): the sum of the k path knots' checks has support x, y and one pendant per path knot, size k + 2,
  with no proper sub-codeword, so δ = k = steps apart.
- **Mixed chains, upper bound** (advisor): with b parity and a not-all-equal knots on the path, κ({x, y} ∪ parity pendants) =
  (−1/3)^a exactly, so δ ≤ b + a = steps apart.
- **Not-all-equal trees, no four-set shortcut** (advisor): a distinction separating {x, u} from {y, v} makes E[xuyv] = E[xu]E[yv],
  so κ₄ = −2·3^(−(d(x,u) + d(y,v))) for the separated pairing.
- **The clamp is needed**: |κ_S| can exceed 1 ({0000, 1111} gives κ₄ = −2).
- **Switching obstruction** (advisor): flipping a distinction's values multiplies κ_S by −1 when it is in S, so δ cannot see
  values. A split line of m points is, up to switching, a ring: the map i → i + 1 with the last point's values flipped carries its
  states to themselves, so no reading invariant under switching sees the line's ends, and |C| and every |κ_S| fold its L1. On it δ
  saturates at 2 + log₃ 2 (a four-set with κ₄ = −1/2 where C = 0).

## Exploration disclosed

Before the freeze: δ on chains of three knots under P, N, PNP and NPN (all steps apart), on a star of four knots under P and N
(steps apart), on a ring of three knots (parity: a new three-set; not-all-equal: graded, δ = τ on the four pairs printed), and on
the 3 × 3 split grid and one switched copy (δ folds: the far corner at 0.465, as the neighbours). The gates use random bases of up to
seven distinctions and a not-all-equal chain of five knots.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates (`checks.py`): cumulant recursion = partition formula; pruned search = full search; invariance under renaming and under switching values; circuits = sets whose states form a parity knot; one knot is distance one under P, N and betweenness; a mutant with moments in place of cumulants shortcuts on a not-all-equal chain (4 against 5) | any fails |
| P1 | On 300 random parity bases of 6 to 9 distinctions, δ = least circuit through the pair − 2 on every pair (∞ when none) | any pair differs |
| P2 | On every knot tree with up to five knots under every assignment of P and N to its knots, and up to six knots under pure P or pure N, δ = steps apart on every pair | any pair differs |
| P3 | On every chain of up to five knots under every law assignment, κ({ends} ∪ parity pendants) = (−1/3)^(number of N knots) | any differs |
| P4 | On not-all-equal chains of three to five knots, every four-set separated by a shared distinction has κ₄ = −2·3^(−(d₁ + d₂)) | any differs |
| P5 | Rings of three to six knots: under parity some pair has δ below steps apart (the ring's own circuit); under not-all-equal δ = τ on every pair | either fails |
| P6 | Chain grid (one knot per pair) on a 4 × 4 patch, read on its grid distinctions: no set of up to six grid distinctions shortcuts τ (δ = τ on every pair); and the endless chain grid's Σ_z C(0, z)² ≤ 4.5 | either fails |
| P7 | A weave patch of radius two (19 distinctions, not-all-equal on every knot inside): δ = τ on every pair (sets up to six) | any pair with δ < τ |
| P8 | The split line of eight: the switching rotation maps its states to themselves; every \|κ_S\| (\|S\| ≤ 4) is invariant under it; the largest δ is exactly 2 + log₃ 2 | any fails |
| P9 | Split grids 3 × 3, 3 × 4 and 4 × 4: a switching equivalence fixes a corner and takes its neighbour to the far corner (so in two orders as well, switching hides L1) | absent for any (exploratory; the advisor did not know) |

## Runs and stop rule

`run.py --part` for trees, mixed_identity, nae_separated, linear, rings, chain_patch, bubble, weave_patch, split_line and
split_grid, then `run.py --score`. Each part is single-process; expected minutes, so no shared-runner row unless a part passes ten
minutes. One run; no change after seeing results; later looks labelled post hoc. Stop at the read-out, the proofs, the referee
hand-off and the report.

Advisor. `claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), asked before the freeze. It recommended this study over the ladder, gave the parity-base
theorem, the parity-tree and mixed-chain identities, the separated four-set formula, the clamp counterexample, the switching
obstruction and its consequence on the split line, and predictions P1 to P8 (P9 is its open question).
