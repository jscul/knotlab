# Does the navigating agent's learned memory carry over to a meeting pattern it never trained on?: pre-registration

Epic `MEET-TRANSFER-20261117-001` (`SCALE-MEMORY-20261116-001#1`, coordinator's go-ahead 2026-11-17; goals G15, G16; the
prerequisite for sub-goal B191), 2026-11-17. **Frozen** before any new arm was trained or any comparator re-tuned; the commit
time of this file is the freeze. Before it, only the gate, calibration of the training families (Novelty+ and probSAT on 12
instances per cell) and a two-iteration smoke of the trainer ran. Code by the thread (Claude) in
`experiments/MEET-TRANSFER-20261117-001A/MEET-TRANSFER-20261117-001A-E001_meet_transfer/`, a copy of SCALE-MEMORY's engine with one
added flag and one added family. The canonical K1–K3 test is unchanged. The advisor reviewed a draft and found a negative result would be uninterpretable as
drafted; its changes are listed in the [advisor note](advisor_review.md) and folded in below.

## The question

`SCALE-MEMORY-20261116-001` found that the navigating agent, with memory reads that count no steps, stays at parity with the best
hand-written rule (Novelty+) across a sixteen-fold range of size on the `rand` meeting pattern. But every version lost 4.7 to 29
times on `local`, a pattern whose knots overlap only within a short run of distinctions and where each distinction is in about
12 knots instead of 6.3. There memory hurt. The owner's second stage (B191), a slow loop that changes knot structures, would put
the agent on patterns unlike its training ones. Can its memory carry over to a meeting pattern it never trained on, when its
reads are normalized by how many knots meet at a distinction and count no steps at all, and when it trains on a mixture of
meeting patterns?

## The objects

- **Training patterns** (all planted, the not-all-equal law):
  - `rand` at density 2.1 (each distinction in about 6.3 knots);
  - `rand` at density 4.0 (about 12), where Novelty+ (0.7, 0.05) stalls at 3,200 and probSAT does not;
  - `block` at density 2.5 (about 7.5): distinctions in consecutive blocks of 20; a knot binds three distinctions of one block with
    probability 3/4, otherwise three drawn from all.
- **Held out, primary:** `local` at density 4.0, window 10 (about 12 knots per distinction, every knot within a run of 21
  distinctions). It matches `rand` at 4.0 in degree but not in how knots meet. Two earlier studies' losses on it shaped this
  design, so it is a development pattern as much as a held-out one.
- **Held out, untouched** (chosen at this freeze, never run by a learned arm before): `local` at windows 40 and 160 (density 4.0),
  a sweep from the primary pattern toward `rand`; and `heavy` at density 3.0, each knot's distinctions drawn by weight
  (i + 10)^(-1/2), so a few distinctions meet many knots (up to about 80) and most meet few, a degree spread no training pattern
  has (the literature's Chung–Lu model).
- **Degree-normalized reads** (flag 32, with the scale-free flag 16): break and make are read as fractions of the distinction's own
  knots, for the attended knot's distinctions, the where-candidates and the recurrent input, and the 50-step recent counts are not
  read. With flag 16 the long-horizon reads are relative ages (each distinction's age over the oldest of the knot's three, each
  candidate's visit age over the oldest candidate's), their ranks and the last-flipped flag. No read counts steps or knots.

## Arms

| Arm | Reads | Memory | Training patterns | Validation |
| --- | --- | --- | --- | --- |
| D | degree-normalized, scale-free | yes | `rand` 2.1, `rand` 4.0, `block` 2.5 | 24 instances of each at n = 800 |
| Dr | as D | yes | `rand` 2.1 only | 24 instances of `rand` 2.1 at n = 800 |
| Dn | degree-normalized | none | as D | as D |
| Dl (oracle) | as D | yes | as D, plus `local` window 10 | as D, plus 24 of `local` window 10 |
| L3sm (SCALE-MEMORY, both seeds) | scale-free, not degree-normalized | yes | `rand` 2.1 | — (reused weights) |

**Seeds.** D and Dl get four seeds each, Dr and Dn two. Dl answers whether these reads and this network can do the primary
pattern at all when trained on it: if Dl also loses there, the obstacle is the representation, not transfer.

Schedule for D, Dr and Dn: 120 iterations at n = 200 (6 instances per training pattern, cap 60,000), 100 at n = 400 (6, cap
300,000), 40 at n = 800 (10, cap 1,500,000). Each member is scored on every training pattern of its arm. Fitness is the mean, over
the patterns, of the members' centred ranks within each. In the last stage the mean weights are scored every 10 iterations, and at
the end, on the validation instances; the best are kept. OpenAI-ES settings and charging are as before. Two seeds per arm, both
tested.

## Comparators: tuned in two stages, five runs

In every test cell the hand-written rules are tuned in two stages.
- **Stage 1 (screen).** 8 tuning instances, three runs each, scored by the median over instances of the mean log flips (an
  unsolved run scores log of the cap plus log of one plus the least violated count), over:
  - Novelty+: noise 0.5, 0.6, 0.65, 0.7, 0.75, 0.8 × walk probability 0, 0.005, 0.01, 0.02, 0.05 (30 settings);
  - probSAT: poly cb 1.0 to 3.0 (8 settings) and exp cb 1.5 to 4.0 (6);
  - WalkSAT: noise 0.3 to 0.8 (6), a rule that does not stall.
- **Stage 2 (confirm).** The top three Novelty+ settings, the top probSAT and the top WalkSAT are rerun on 20 fresh tuning
  instances, five runs each, and ranked by the test metric.
- **Test.** All five run on the test instances. The comparator is the best of them in each bootstrap resample, and the spread of
  the three Novelty+ settings is reported as a sensitivity check. The comparators' censoring is reported too.

The tuning caps are 2·10^7, or 10^8 at `local` 3,200. Walk probability 0 can stall, as the previous referee found; it stays in the
grid and the cap scores it.

## Test cells

Unseen instances, **five runs per instance for every arm**, the same five initial states per instance for every arm, flip caps
identical across arms in a cell:

| Cell | Role | Instances | Cap |
| --- | --- | --- | --- |
| `local` window 10, n = 3,200 | **primary**: held-out pattern, 4 times the training size | 50 | 4·10^8 |
| `local` window 10, n = 800 | held-out pattern at the training size | 100 | 2·10^7 |
| `local` windows 40 and 160, n = 800 | untouched held-out patterns, at the training size | 100 each | 2·10^7 |
| `heavy` 3.0, n = 800 and 3,200 | untouched held-out degree spread | 100, 50 | 2·10^7, 2·10^8 |
| `rand` 2.1, `rand` 4.0, `block` 2.5 at n = 3,200 | training patterns at 4 times the training size | 50 each | 2·10^8 |

## Measures

- **Per-instance figure.** The geometric mean of an arm's five run lengths, a censored run counted at the cap. Where more than 5%
  of an arm's runs are censored, its figure and R are lower bounds, so its R is reported as "at least".
- **Per-seed figure.** The median of the per-instance figures. The arm figure is the geometric mean of its two seeds' figures.
- **R.** The arm figure over the best re-tuned rule's figure. The interval is a 99% paired bootstrap over instances (10,000
  resamples), with the best rule re-chosen in each.
- **Ratios between arms**, the same way:
  - X = D / Dr: mixed-pattern training, structure and degree together, since Dr never sees a degree above about 6.3;
  - Y = D / L3sm: the new package (degree-normalized reads, no counts, mixed training) against the previous agent;
  - Z = Dr / L3sm: the new reads and dropped counts together, with Dr's schedule;
  - K = D / Dn: memory;
  - O = D / Dl: the cost of not having trained on the pattern.
- **Usable as an inner loop** (the bar for B191): R at most 2 with the upper end below 2.5, a solved fraction no lower than the
  best rule's, and a 95th-percentile ratio at most 3 (the slow loop pays for slow runs as well as typical ones). CPU per instance
  is reported beside it; no CPU win is expected.
- **Cost.** Median CPU and incidences per instance, and break-even N*.
- **Seed agreement for every verdict and ratio.** A claim holds only when the arm-level interval satisfies it and every seed's own
  value lies on the same side of the threshold (the lesson of SCALE-MEMORY's L3m). A split is read as learner variance, not as a
  verdict on transfer.

## Gates

| # | Gate | Fails when |
| --- | --- | --- |
| G | The engine checks G0–G5 extended to flag 32 and the block family, and G6: this engine reproduces SCALE-MEMORY's run for run (8 rules, L3 and L3sm on 12 instances). | any fails |
| G-learn | On **every** training pattern of the arm, its median on that pattern's validation instances at n = 800 is at most 1.15 times the better of Novelty+ (0.7, 0.01) and probSAT (cb 1.8) on the same instances (for the memoryless Dn, probSAT's). | above 1.15 on some pattern: that arm is read "learner failure" |

## Predictions (frozen)

| # | Prediction | Probability | Fails when |
| --- | --- | --- | --- |
| P1 | D is usable as an inner loop on held-out `local` 3,200 (the bar above). | 30% | otherwise |
| P1o | The oracle Dl is usable there. | 50% | otherwise |
| P2 | Mixed-pattern training helps the held-out pattern: X = D / Dr at `local` 3,200 at most 0.5, upper end below 1. | 50% | otherwise |
| P3 | D beats the previous agent there: Y = D / L3sm at most 0.5, upper end below 1. | 55% | otherwise |
| P5 | D keeps parity on its training patterns at 3,200: R ≤ 1.1 on all three. | 45% | above 1.1 on some |
| P6 | Memory helps on the held-out pattern: K = D / Dn at `local` 3,200 at most 0.9, upper end below 1. | 35% | otherwise |
| P7 | No CPU win in any cell. | 92% | some arm's median CPU per instance is below the best rule's |
| P8 | The new reads alone help on `local`: Z = Dr / L3sm at `local` 3,200 at most 0.7, upper end below 1. | 40% | otherwise |
| P9 | D is usable on both untouched windows (40, 160) at n = 800. | 35% | otherwise |
| P10 | D comes within 1.5 times the best rule on `heavy` at n = 800 and 3,200. | 50% | otherwise |

**Decision rule.** The main reading is the inner-loop bar for B191, applied to D on the primary cell, `local` 3,200, and on the
untouched held-out cells:
- usable on the primary and on the untouched cells: B191 may use the learned fast loop;
- usable on the primary only: the transfer is to the development pattern, and B191 does not use the learned fast loop;
- not usable on the primary: B191 starts with Novelty+ as its fast loop.

Dl reads which: if Dl is usable and D is not, the obstacle is transfer; if neither is, the obstacle is the representation. The
WHERE-NEXT tiers (real win, mechanism win, clean loss, inconclusive; 99% intervals, seed agreement) are reported beside it for
continuity.

**Publication hold.** As before: planted instances and local search cannot give a general SAT method; if an arm's flips grow
with n at a clearly smaller rate than every rule's, the thread tells the owner before committing.

## Not done, with the reason

- *A covariate-shift table* (each read's distribution on every pattern): the engine does not log its reads, and the oracle Dl
  answers the more useful question, whether the reads can do the pattern at all.
- *An arm trained on `rand` 2.1 and 4.0 only*: X is labelled as structure and degree together instead.
- *The recurrent state* still decays at a fixed rate per step, so it counts steps implicitly; this is stated as a limitation.

## Runs and stop rule

The re-tuning (5 cells × 38 settings × 8 instances × 3 runs) and the six trainings are registered long runs; the test cells
follow. The study stops at the decision rule. The 51,200 cell of SCALE-MEMORY keeps running in the background and is folded into
that study, not this one.

## Prior work in the program

Objects index, searched 2026-11-17:

`python3 -B scripts/track.py objects "learned memory that carries over to another meeting pattern" --until 2026-11-18 --exclude MEET-TRANSFER-20261117-001`
`python3 -B scripts/track.py objects "learned local search policy transfer to a held-out instance family" --until 2026-11-18 --exclude MEET-TRANSFER-20261117-001`

- `SCALE-MEMORY-20261116-001` and `WHERE-NEXT-20261116-001`: the same agent and the same held-out `local` pattern; this study
  continues them and reuses SCALE-MEMORY's L3sm and engine (gate G6).
- `SEARCH-AUDIT-20261112-001`: a relative; its lesson (score against tuned search) is kept.
- `FORGET-RULE-20261114-001`: unrelated object (syntactic forgetting rules on nested families, with a held-out split); matched on
  "held-out" and "family".

## Prior work outside the program

As in WHERE-NEXT and SCALE-MEMORY. Transfer of learned SAT heuristics across instance families was tested by Yolcu and Póczos
(2019, trained per family) and Graph-Q-SAT (Kurin et al. 2020, some cross-family transfer for branching); no study found compares
a learned clause-and-variable choice with memory across meeting patterns at charged cost against widely tuned rules.
