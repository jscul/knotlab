# Does a slow loop that changes the knot pattern at the knots a fast search attends to most cut the charged work of solving unseen patterns?: pre-registration

Epic `SLOW-LOOP-20261117-001` (sub-goal B191, the owner's second stage, coordinator's go-ahead 2026-11-17; goals G15, G16).
**Frozen** before any slow-loop policy was tuned, any comparator re-tuned or any test instance run. The commit time of this file
is the only authority for the freeze. Before it, only the gates and a calibration ran (below, disclosed). Code by the thread
(Claude) in `experiments/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop/`: a new engine for signed knots whose fast
loop reproduces SCALE-MEMORY's engine run for run (gate G6), and the slow loop. The canonical K1–K3 test is unchanged. The advisor
reviewed a draft, said "freeze with changes", and the changes are in ([advisor note](advisor_review.md)).

## The question

The owner's picture (2026-11-16): a fast activity searches on the knot structure, and a slower loop reshapes the structure, "a kind
of metacognition", with braids and untangles as ways of creating structure. The first stage (WHERE-NEXT, SCALE-MEMORY, both
refereed) tested the fast half: a learned agent reaches parity with Novelty+ on one meeting pattern, at about 5 times the CPU per
flip, and loses on another. This study tests the slow half with Novelty+ as the fast loop. Between epochs of the search, the slow
loop reads which knots the search attended to most (its **attention counts**) and changes the pattern at those knots. It uses two
moves that keep the allowed states:

- **Tie merge.** A bounded refutation shows that two distinctions are tied: equal, or unequal, in every allowed state (the
  glossary's tie class). The two are merged into one, and the merged pattern's allowed states correspond one for one with the
  original's. A knot whose members fall into two classes either always holds, and is dropped, or forces a further tie, which is
  merged in turn.
- **Shadow knot.** A bounded refutation shows that some joint state of three distinctions, and its complement, hold in no allowed
  state, while the other three pairs are not refuted. The signed not-all-equal knot that excludes exactly that pair then holds in
  every allowed state. It is the pattern's shadow on those three distinctions, it passes K1–K3, and it is added. The allowed states
  are unchanged.

These are the owner's untangle and braid only as analogies. The record already uses "braid" for carrying open distinctions together
and for a classical crossing, so the moves keep the plain names above. The advisor preferred "shadow knot" to "implied knot",
because every knot of a pattern is implied by it.

This reading of the owner's picture is assumption A90 (the coordinator's, open to challenge). The study asks three questions:
- Are the changed patterns solved with less charged work than the originals, with every probe and rebuild charged?
- Do the attention counts pick better targets than random knots, and is the result better than probing every knot first, which is
  the known preprocessing?
- Does a slow-loop policy tuned on two meeting patterns carry over to three it never saw?

## In standard terms

The patterns are planted 3-uniform hypergraph 2-colourings (unsigned not-all-equal 3-SAT), solved by stochastic local search with
**inprocessing** between search epochs:
- failed-assumption probing by unit propagation, giving equivalent-literal substitution (tie merge);
- learned implied clauses of the not-all-equal kind (shadow knot).

The inprocessing is scheduled by the search's own clause visit counts. The comparators are:
- the same search alone (re-tuned Novelty+ and probSAT);
- the same probing applied to every clause first, as tuned preprocessing;
- the same probing on randomly drawn clauses;
- CDCL (CaDiCaL 1.9.5), with its own preprocessing and inprocessing.

The `local` patterns have bounded bandwidth along a declared order, and propagation and dynamic programming are known to solve such
patterns.

## Prior work in the program

Objects index, searched 2026-11-17:

`python3 -B scripts/track.py objects "slow loop mutating knot structure during local search" --until 2026-11-18 --exclude SLOW-LOOP-20261117-001`
`python3 -B scripts/track.py objects "propagation refutation probe finds tie classes on not-all-equal patterns" --until 2026-11-18 --exclude SLOW-LOOP-20261117-001`
`python3 -B scripts/track.py objects "preprocessing before local search charged cost" --until 2026-11-18 --exclude SLOW-LOOP-20261117-001`

- `WHERE-NEXT-20261116-001` and `SCALE-MEMORY-20261116-001`: the fast half of the same picture, on the same planted patterns. This
  study reuses their engine run for run (G6) and their families, through MEET-TRANSFER's generator. It also keeps their lesson:
  five runs per instance against a widely re-tuned Novelty+, walk probability 0 included.
- `COMMON-FOLD-20261112-001`: a relative. It measured how much of a grown base a conditioned pair forces, split by ties,
  propagation and search, on uniform growth. Its finding that most forcing is the final tie class is the phenomenon the tie merge
  uses, on a different population.
- `SUBST-NEST-20261112-001`, `RANDOM-FATES-20261112-001` and `NEST-READ-20261112-001`: relatives on not-all-equal patterns (what
  substitution pins, how growth ends). None measures search cost.
- `SEARCH-AUDIT-20261112-001`: a relative in method. It scored learned target-finding against blind search, and this study keeps
  its lesson of charging every check against a tuned search alone. Its object (finding a count) is unrelated.
- `SHIFT-COUNT-20261112-001`, `FIVE-PRODUCT-TOTAL-WORK-20261115-001` and `STEER-LEARN-20261112-001`: unrelated objects, matched on
  "search", "structure" and "charged".
- `MEET-TRANSFER-20261117-001`, the meeting-pattern transfer study, runs at the same time on the same families. It tests the
  learned fast loop, not structure changes, and this study shares no runs or files with it.

## Prior work outside the program

All of the parts are known:
- **Probing and equivalence reasoning:** failed-literal probing (Freeman 1995; Le Berre 2001), equivalency reasoning in DPLL (Li
  2000), Stålmarck's method with its dilemma rule and equivalence classes (Sheeran and Stålmarck 1998), and equivalent-literal
  substitution and inprocessing in CDCL solvers (Järvisalo, Heule and Biere 2012; CaDiCaL).
- **Structure for local search:** resolution preprocessing for local search (Anbulagan, Pham, Slaney and Sattar 2005,
  R+AdaptNovelty+), dependency structure built into local search (Pham, Thornton and Sattar 2007), and hybrids that call clause
  learning around local minima (Audemard, Lagniez, Mazure and Saïs 2009–10).
- **Reshaping the search's landscape:** clause weighting (Morris 1993; SAPS, Hutter et al. 2002; PAWS, Thornton et al. 2004),
  whose weights rise on clauses the search keeps violated. It also follows where the search stays, and it is not run here (below).
- **The patterns:** planted not-all-equal patterns are quietly planted below condensation (Krzakala and Zdeborová 2009).

Not found: a comparison at charged work of the same probing targeted by a local search's visit counts, applied to random clauses,
and applied everywhere first, with the moves stated as changes that keep the allowed states and the scheduling policy tuned on some
meeting patterns and tested on others. What the knot framing adds is the statement of the moves (tie classes, and shadows that pass
K1–K3) and the question of whether the fast loop's attention is a useful signal for where the structure should change. It adds no
new inference rule.

## Settled by construction (stated, not tested)

- **Soundness.** Every move keeps the allowed states (tie merges up to the one-for-one map), because propagation refutes only
  states that no allowed state extends. Gates G1 and G7 check this by brute force and against the planted state, and G4 checks that
  a wrong move would be caught.
- **No budget, no change.** With no slow budget, the slow-loop driver is the fast loop alone, run for run (G3). Until its first
  move, a slow arm's fast loop makes exactly the fast loop's flips. So on a pattern where nothing is found, its extra work is its
  probes and nothing else.
- **Random patterns.** On a random meeting pattern a probe almost never refutes anything, because two assumed distinctions rarely
  share a second knot and propagation stops after one step (calibration below). The slow loop can only lose there, by its overhead.
- **`local` window 10 is solved by probing.** Static probing to its fixpoint collapses it to a few hundred classes (calibration).
  A win there re-derives preprocessing; it does not test the owner's idea. The cells that can test the attention signal are the
  sparse-structure ones: `local` window 40 and the embedded pattern.

## Calibration before the freeze (disclosed)

These runs used instance seeds 9,000,000 and up, disjoint from every seed below. Their outputs are in the thread's scratch notes and
are not evidence.
- **One pass of three tie probes per knot at n = 800** (4,000 per probe) found ties at:
  - no knot of `rand` 2.1 and of a heavy-tailed pattern;
  - 12–14% of knots on `block` 2.5, leaving about 700 classes;
  - 57% on `local` window 10, leaving about 200 classes;
  - 0.5–0.8% on `local` window 40.
- **Shadow-knot probes** on triples from a knot and one overlapping knot excluded exactly one pair in:
  - 0% of triples on `rand`;
  - 13% on `block`;
  - 32% on `local` window 10;
  - 6% on `local` window 40.
- **Eight instances, two runs each, with an untuned default policy** (epochs of n flips, slow budget 0.3 of the epoch's fast work,
  backoff). Charged work against Novelty+ (0.7, 0.01):
  - guided: about 1.1 on `rand`; 1.2–1.3 on `block`, but 0.95–0.98 without shadow knots; 0.13–0.21 on `local` window 10 at 3,200;
    0.8–1.1 on `local` window 40 at 3,200;
  - static probing, untuned: 1.6–2.3 on `rand`, 0.9–2.3 on `block`, 0.2 on `local` window 10 and 0.4 on `local` window 40 at
    3,200.
- **What the calibration already suggests.** In the one sparse-tie cell, `local` window 40, static probing (0.4) did better than
  guided (0.8–1.1). That points to reading 2 below.
- **The embedded pattern.** A first version (a `local` sub-pattern on 10–25% of the distinctions under a uniform pattern over all
  of them) was easy for Novelty+, and every slow arm lost there (1.6–3.5 guided, 15–40 static). The uniform knots across the
  sub-pattern remove what makes it hard. The version used below couples the two sub-patterns weakly.
  - With an untuned policy at 3,200 it gave guided 0.52, random 0.86 and static 1.8.
  - In every embedded variant tried, random targets found more ties per unit of probe work than the attention counts did (roughly
    1.3 to 3 times as many).
- **Many shadow knots slow the search.** With a very large slow budget on `block` 3,200, about 13,000 added shadow knots kept
  Novelty+ unsolved within 2·10^6 flips, where it alone solved in 263,000. Without shadow knots, the same run solved in 31,000.

These shaped the design below. They enter no verdict.

## Families and cells

All planted, unsigned not-all-equal patterns. MEET-TRANSFER-20261117-001A's generator is used unchanged for:
- `rand` at density 2.1 (each distinction in about 6.3 knots);
- `block` at density 2.5, blocks of 20;
- `local` at density 4.0, windows 10 and 40.

**`embed`**, this study's own generator, has one hidden state shared by three parts, with the knots in a uniformly shuffled order:
- a `local` sub-pattern (density 4.0, window 10) on the first quarter of the distinctions;
- a uniform pattern at density 2.1 on the other three quarters;
- 0.02·n coupling knots drawn from all distinctions.

| Cell | Role | Instances | Flip cap |
| --- | --- | --- | --- |
| `local` w10, n = 3,200 | **primary**: held-out pattern, 4 times the tuning size (solved by probing; see above) | 50 | 2·10^8 |
| `local` w40, n = 3,200 | held-out; sparse ties, where attention can matter | 50 | 2·10^8 |
| `embed`, n = 3,200 | held-out; local structure on a quarter of the pattern, where attention can matter | 50 | 2·10^8 |
| `rand` 2.1, `block` 2.5, n = 3,200 | tuning patterns at 4 times the tuning size | 50 each | 2·10^8 |
| the same five patterns, n = 800 | at the tuning size | 50 each | 2·10^7 |

Seeds:
- policy and static tuning: 7,000,000 and up, 8 instances per pattern;
- oracle policy tuning: 7,600,000 and up;
- comparator re-tuning: 7,500,000 and up, 8 instances per cell;
- test: 7,100,000 and up;
- stress: 7,200,000 and up.

The generators' streams depend on the pattern, its size and the seed, so equal seeds in different cells give different instances.
Every arm runs from the same five initial states per instance, given by `run_seed("test", cell, seed, rep)`.

## Arms

All local-search arms run five times per instance.

| Arm | What it is |
| --- | --- |
| NOV | Novelty+ re-tuned per cell: noise 0.5, 0.6, 0.65, 0.7, 0.75, 0.8 × walk probability 0, 0.005, 0.01, 0.02, 0.05 (30 settings) |
| PS | probSAT (poly, eps 1) re-tuned per cell: cb 1.0, 1.4, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0 |
| F | the fast loop alone: the better of NOV and PS by the cell figure, re-chosen in every bootstrap resample |
| G | the slow loop with the policy **tuned on `rand` 2.1 and `block` 2.5 at n = 800**; fast loop the cell's NOV setting |
| Gx | G with the shadow-knot share switched (0.5 if G's is 0, else 0): what the shadow knots do |
| RND | G's policy with uniformly drawn unprobed targets: what the attention counts do |
| ST | static probing with its own setting **tuned on `rand` 2.1 and `block` 2.5 at n = 800** (below), then the cell's NOV setting alone: the preprocessing precedent |
| GO | the slow loop with the policy **tuned on `local` w10 at n = 800** (the oracle for transfer); fast loop as G |
| CDCL | CaDiCaL 1.9.5 (pysat) on the CNF encoding (two clauses per knot, one unit fixing the complement), 60 s, one run on each of the 50 instances of the `local` and `embed` cells and the first 20 of `rand` and `block`; CPU and propagations |

**The slow loop.**
- **Epochs.** The fast loop runs in epochs of e·n′ flips, n′ being the current number of tie classes, at least 100.
- **Targets.** After each epoch, the knots attended to in that epoch, most attended first, skipping knots already probed with an
  unchanged signature. RND draws uniformly among unprobed knots.
- **Probes.** Each target gets three tie probes, one for each of its three allowed patterns up to complement. With probability β it
  also gets shadow-knot probes: J = 2 overlapping knots sharing one distinction with it, the four triples of the other four
  distinctions, and four joint states each.
- **Budget.** Each probe is bounded by 4,000 charged incidences. The epoch's slow budget is ρ times the epoch's fast work. With
  backoff, an epoch that finds nothing halves the next budget, down to ρ/64, and a find restores it.
- **Rebuild.** After an epoch with a find:
  - the tie classes are merged, with the cascade of forced ties;
  - every knot is mapped through the classes, dropped when it always holds, its signs normalized, and duplicates dropped;
  - a merged class takes the value most of its members hold (its root's on a tie) and its root's age;
  - the search continues on the rebuilt pattern.
- **The answer.** A state of the rebuilt pattern is mapped back to the original distinctions and checked on every original knot.

**Static probing (ST).**
- **Passes.** Tie probes on every knot in index order, each followed by shadow-knot probes with probability β_s. Passes repeat on
  the knots whose signature changed, while a pass finds a move, up to P passes.
- **Abort.** A pass that has probed a·m knots without a find stops.
- **Grid** (8 settings): P ∈ {1, 8}, β_s ∈ {0, 0.5}, a ∈ {0, 0.05}.

**Policy grid** (48 settings): e ∈ {1, 4, 16}; ρ ∈ {0.03, 0.1, 0.3, 1}; β ∈ {0, 0.5}; backoff ∈ {on, off}. J = 2 and the probe
budget of 4,000 are fixed.

**Tuning scores.**
- **G and ST.** On each tuning pattern, the mean over 8 instances × 3 runs of log(the setting's charged work) − log(NOV's charged
  work from the same initial state). The fast loop is that pattern's re-tuned NOV setting at n = 800. G's and ST's settings each
  minimize the mean of the two patterns' scores.
- **GO.** The same on `local` w10 alone.
- **Unsolved runs.** A run unsolved at the cap scores log of its work at the cap plus log(1 + least violated count).
- **Declared before tuning.** The advisor expects G's score to pick the floor of the grid (ρ = 0.03, β = 0, backoff on), since the
  slow loop cannot pay on `rand`. If it does, T = G/GO reads a lazy policy against an eager one, not transfer as such.

**Re-tuning of NOV and PS.** On 8 tuning instances per cell, 3 runs each, by mean log charged work, unsolved runs scored as above.
Tuning caps: 2·10^7 flips at both sizes.

## Measures

- **Charged work W** (primary; the measure is assumption A91): incidences touched (one knot-distinction pair read) by both loops. It counts:
  - the fast loop's reads and flips;
  - three per knot read in a probe;
  - the rebuild: the cascade's reads, 3 per knot mapped, n per class map, and 3 per knot of the new pattern's counts.

  It does not depend on the machine.
- **CPU:** thread CPU of the whole run, Python included, split into fast loop, probes and rebuild. The rebuild runs partly in
  Python, so the total overstates what a C rebuild would cost. The verdicts use the total.
- **Flips:** the fast loop's.
- **Per-instance figure:** the geometric mean of an arm's five runs. A censored run counts at its value at the cap. Where more than
  5% of an arm's runs are censored, R is a lower bound ("at least"). Where more than 5% of F's are, R is an upper bound ("at most").
  Where both are, R is undetermined.
- **Cell figure:** the median of the per-instance figures.
- **R(X)** = the cell figure of X over F's, for W and for CPU. The interval is a 99% paired bootstrap over instances (10,000
  resamples), with F's rule re-chosen in each. R against NOV alone is reported beside it, since NOV is the slow arms' fast loop.
- **Ratios between arms**, computed the same way:
  - G/ST: attention-scheduled against tuned static;
  - G/RND: the attention counts at the same policy. Realized slow work is reported, since backoff gives the arm that finds less a
    smaller budget;
  - G/Gx: the shadow knots;
  - T = G/GO: the cost of not having tuned on the pattern.
- **Finds per unit of probe work** (frozen measure of the attention signal): ties plus shadow knots found per 10^6 probe
  incidences, per instance over its five runs, G against RND.
- **Diagnostics:** classes left, ties and shadow knots found, the slow share of W, rebuilds, targets.

## Verdict for each arm in each cell (frozen)

- **Charged win:** R_W ≤ 0.8 with its upper end below 0.9, and R_CPU's upper end below 1.
- **Work win:** the W condition holds, the CPU condition does not.
- **Loss:** R_W's lower end above 1.1.
- **Parity or inconclusive:** otherwise.

## Decision rule (frozen)

The held-out cells at 3,200 are `local` w10, `local` w40 and `embed`. The tuning cells at 3,200 are `rand` and `block`.

1. **Attention pays.** G has a charged win on a held-out cell, no loss on the tuning cells, and in the same winning cell both G/ST
   below 1 (upper end) and G/RND ≤ 0.9 (upper end below 1). Scheduling the moves by attention counts pays, carries over, and beats
   both static probing and random targets. This confirms scheduling by visit counts, not "metacognition" in general.
2. **Pays, attention not shown.** As 1, but G/RND is not below 0.9 where G wins. The slow loop pays and beats static probing, and
   the attention counts are not shown to matter.
3. **Static is as good.** G wins only where ST wins by as much or more (G/ST ≥ 1 in every win cell). Structure change pays where
   the pattern has local structure, and the known preprocessing gets it as cheaply. B191's next step would need a move static
   probing cannot make.
4. **No win.** G has no charged win anywhere. These moves, scheduled this way, do not pay at charged cost. This does not refute the
   owner's idea, only this reading of it (A90).
5. **Default.** G wins somewhere, but none of the above holds as frozen. Read cell by cell.

A charged win here does not say that structure change beats clause weighting, the cheaper precedent that also follows where the
search stays; it was not run.

## Gates (run before the freeze)

| # | Gate | Fails when |
| --- | --- | --- |
| G0 | The knot law and a signed knot pass K1–K3 (`knotlab check`) | either fails |
| G1 | 240 small instances (n = 8–14, three patterns), guided with a large budget and static: every tie and shadow knot holds in every allowed state (brute force); the changed pattern's states, mapped back, are exactly the original's; every solution checks | any fails |
| G2 | Incremental counts on randomly signed patterns equal recomputation after random runs of flips (300 recounts) | any differs |
| G3 | With ρ = 0 the slow driver reproduces the fast loop run for run (60 runs) | any differs |
| G4 | A mutant that applies every tie with the wrong parity is caught (its changed pattern's states differ from the original's) on every small instance where it made a tie, at least 20 | any not caught |
| G5 | CaDiCaL agrees with brute force and its models check | any fails |
| G6 | This engine reproduces SCALE-MEMORY's engine run for run (Novelty+ at three settings and probSAT at two, on 12 instances of `rand` and `local`), and the generator reproduces MEET-TRANSFER's on `block` | any differs |
| G7 | At n = 800 and 3,200 on four patterns, with a very large slow budget, every tie and shadow knot found holds in the planted state, and every reported solution checks (a run may stop unsolved: see the calibration) | any fails |

## Predictions (frozen)

| # | Prediction | Probability | Fails when |
| --- | --- | --- | --- |
| P1 | G charged win on the primary cell (`local` w10, 3,200) | 80% | otherwise |
| P2 | G costs at most 15% on `rand` 3,200: R_W ≤ 1.15 and upper end ≤ 1.25 | 85% | otherwise |
| P3 | No win for G on `block` 3,200 (R_W > 0.8) | 90% | R_W ≤ 0.8 |
| P4 | G work win or better on `local` w40, 3,200 | 25% | otherwise |
| P5 | ST at least as good as G on the primary cell: G/ST ≥ 0.9 | 75% | G/ST < 0.9 |
| P6 | The attention counts pay somewhere at 3,200: G/RND ≤ 0.9 with upper end below 1 | 15% | nowhere |
| P7 | Transfer: T = G/GO on the primary cell within [0.8, 1.25] | 35% | outside |
| P8 | Shadow knots change G by less than 10% in every cell: G/Gx within [0.9, 1.11] | 25% | outside somewhere |
| P9 | CDCL solves all 50 primary-cell instances within 60 s, at a median CPU below G's | 90% | otherwise |
| P10 | CDCL solves fewer than half of the `rand` 3,200 instances within 60 s | 90% | half or more |
| P11 | Soundness: no contradiction, and every reported solution checks on the original knots, in every run | 99% | any |
| P12 | On `embed` 3,200, G finds at least as many moves per unit of probe work as RND (medians) | 25% | fewer |
| P13 | G work win or better on `embed` 3,200 | 25% | otherwise |

**Publication hold.** Planted patterns, local search and probing by propagation cannot give a general method for SAT. If a slow
arm's work grows with n on `rand` at a clearly smaller rate than F's, the thread tells the owner before committing.

## Runs and stop rule

All on the shared runner (`scripts/longrun.py`), MemoryMax 16G, 8 workers, each a registered long run:
1. **S1:** comparator re-tuning, 10 cells × 38 settings × 8 instances × 3 runs.
2. **S2:** tuning of the policies (48 settings on `rand` 800, `block` 800 and `local` w10 800) and of ST (8 settings on `rand` 800
   and `block` 800), 8 instances × 3 runs.
3. **S3:** the test, 10 cells × 50 instances × 7 arms × 5 runs, and CDCL.
4. **S4, a stress cell** one size up, registered and run in the background: `local` w10 and `rand` at n = 12,800, 20 instances,
   five runs, NOV, PS, G, ST and GO at the 3,200 settings. It does not block the close.

Estimates: S1 20–40 min, S2 under 15 min, S3 about an hour, S4 about 30 min. Estimates here have run about twice too low. The study
stops at the decision rule. No arm, cell or setting is added after the test results are seen, except S4.

## Not done, with the reason

- **The learned agent as the fast loop.** Its engine reads unsigned knots only, and after a tie merge the knots carry signs.
  Novelty+ matches it on `rand` and beats it on `local`.
- **Re-tuning the fast loop on the changed pattern.** The slow arms keep the cell's NOV setting, tuned on the original pattern. This
  can only understate them. A loss is therefore read as a loss of this pairing.
- **A clause-weighting comparator** (PAWS or SAPS). It is the advisor's third addition, and the closest precedent that also follows
  where the search stays. It needs a new search family in the engine and its own tuning. It is recorded as a direction, and the
  decision rule says what its absence leaves open.
- **The rebuild in C.** The CPU is split into fast loop, probes and rebuild instead.
- **A trained network for the slow loop's choices.** The slow loop's policy is four tuned parameters, and the question of carrying
  over is put to that small policy first.
