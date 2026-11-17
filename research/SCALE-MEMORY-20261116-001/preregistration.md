# Does the navigating agent's learned memory carry over when it reads no step counts, or when it trains larger?: pre-registration

Epic `SCALE-MEMORY-20261116-001` (`WHERE-NEXT-20261116-001#1`, coordinator's go-ahead 2026-11-16; goals G15, G16), 2026-11-16.
**Frozen** before any of the new arms was trained; the commit time of this file is the freeze. Before it, only the gate,
two-iteration smokes of the trainer and the start of the n = 51200 re-tuning of two hand-written rules ran, none of which
reads a new arm. Code by the thread (Claude) in `experiments/SCALE-MEMORY-20261116-001A/SCALE-MEMORY-20261116-001A-E001_scale_memory/`,
a copy of WHERE-NEXT's engine and scripts with one added flag. The canonical K1–K3 test is unchanged. The advisor model
reviewed a first draft and asked for changes before freezing; they are listed in the [advisor note](advisor_review.md) and
folded in below.

## The question

`WHERE-NEXT-20261116-001` trained an agent that attends to a violated not-all-equal knot, flips one of its distinctions and
chooses the next knot, with memory of its earlier steps. At its training sizes it took 0.45 and 0.60 times the flips of the best
re-tuned hand-written rule (Novelty+). At 4 times its largest training size it tied (R = 1.07); at 16 times it lost 2.4 times;
on an unseen local meeting pattern it lost 3 to 55 times. Its long-horizon memory reads count steps: log ages clipped at 1,000
steps. Novelty+ reads only which of the knot's distinctions was flipped most recently, which counts nothing. Is the failure to
carry over in the reads, in the sizes it trained on, in both, or in neither? The study crosses the reads with the training sizes,
with a memoryless arm and a schedule control.

## Prior work in the program

Objects index, searched 2026-11-16:

`python3 -B scripts/track.py objects "learned memory that carries over to larger sizes" --until 2026-11-17 --exclude SCALE-MEMORY-20261116-001`
`python3 -B scripts/track.py objects "learned local search policy transfer to larger instances" --until 2026-11-17 --exclude SCALE-MEMORY-20261116-001`
`python3 -B scripts/track.py objects "navigating agent with memory" --until 2026-11-17 --exclude SCALE-MEMORY-20261116-001`

- `WHERE-NEXT-20261116-001` (rows 1 and 2): the same object and population; this study continues it, reuses its instances, runs
  and trained L3, and keeps its rules and win rule.
- `SEARCH-AUDIT-20261112-001`: a relative (learned cases against blind search); its lesson is kept by scoring against tuned rules.
- `SHIFT-COUNT-20261112-001`, `ROUTE-FRONTIER-MEMORY-20261115-001`, `UNSIGNED-ROUTE-JOINS-20261115-001`: unrelated objects
  (matched on "memory" and "carries").

## Prior work outside the program

WHERE-NEXT's prior-work section applies. Transfer of learned SAT heuristics to larger instances was the
weak point of Yolcu and Póczos (2019) and the tested strength of Graph-Q-SAT (Kurin et al. 2020, trained on 50 variables and run
on up to 250); neither isolated the role of size-dependent features.

## Arms

| Arm | Where and what | Memory | Long-horizon reads | Schedule (all `rand`) | Validation |
| --- | --- | --- | --- | --- | --- |
| L3 (WHERE-NEXT, both seeds) | learned | yes | step-counted | 200, 400, 800 | n = 800 |
| L3s | learned | yes | scale-free | as L3 | n = 800 |
| L3m | learned | yes | step-counted | 200, 800, then 800 and 3200 mixed | n = 3200 |
| L3sm | learned | yes | scale-free | as L3m | n = 3200 |
| L2m | learned | none | — | as L3m | n = 3200 |
| L3c (control) | learned | yes | step-counted | as L3m, but its last stage at 800 only | n = 3200 |

**Scale-free reads** (flag 16 with flags 2 and 4). The clipped log age of each distinction of the attended knot is replaced by
its age over the oldest of the knot's three; the clipped log visit age of each candidate knot by its visit age over the oldest
candidate's. A distinction never flipped, or a knot never visited, has age t + 1, the steps so far, so it reads 1, the oldest.
Kept as in L3: the ranks by age, the last-flipped flag, and the recent flip and visit counts, which decay over 50 steps, a
horizon that does not grow with n (Novelty+'s tuned noise stayed at 0.6 to 0.7 at every size). In the recurrent input the
flipped distinction's age is read the same relative way, and the violated count is read as 10 × violated / knots, clipped at 1,
instead of log(1 + violated) / log(1 + knots), which falls with n at a fixed count.

**Schedules.** The mixed schedule: 100 iterations at n = 200 (16 instances, cap 60,000), 80 at n = 800 (16, cap 1,500,000), then
40 in which every member is scored on 8 instances at n = 800 and 8 at n = 3200 (caps 1,500,000 and 10,000,000, about 40 times
the re-tuned probSAT median at each size). Its fitness is the mean, over the two sizes, of the members' centred ranks within
each size, so neither size's spread dominates. The control L3c runs the same schedule with its last stage at 800 only (16
instances), and the same selection at 3200. In the last stage the mean weights are scored every 10 iterations, and at the end,
on 64 validation instances at the arm's validation size; the best are kept. ES settings and charging are as in WHERE-NEXT. Two
seeds per arm, and **both seeds are tested**.

Not added, with the reason: a hand-wired Novelty+ inside the network. Every read Novelty+ uses (break, make, rank by age, last
flipped) is among the network's reads, and Novelty+ itself runs in the same engine.

## Test cells

The same instances and run seeds as WHERE-NEXT, so the same instances and initial states. One run per instance per arm and
seed, with flip caps identical across arms in a cell:
- `rand` n = 800: 100 instances, cap 10^7;
- `rand` n = 3200: 100 instances, cap 2·10^8;
- `local` n = 3200: 100 instances, cap 4·10^8;
- `rand` n = 12800: **100** instances, cap 2·10^9;
- `rand` n = **51200**: 100 instances, cap 2·10^9.

**Reused runs.** WHERE-NEXT's runs of the hand-written rules and of L3 seed 1 are reused where they exist: at 800, 3200,
`local` 3200, and instances 0–49 of 12800. Gate G6 checks that this engine reproduces WHERE-NEXT's run for run on every rule and
on L3.

**New runs of the rules.** At 12800 (instances 50–99) and at 51200, Novelty+ and sticky (the two best at 3200) run
training-tuned and re-tuned. At 12800 they keep WHERE-NEXT's re-tuned values; at 51200 they are re-tuned on 16 tuning
instances, five neighbouring grid values each.

## Measures

- **Per-arm flips.** The geometric mean of the two seeds' median flips.
- **R.** That flips figure over the best re-tuned rule's median, with a paired bootstrap that resamples instances, recomputes
  both seeds' medians and re-chooses the best rule each time.
- **Seed agreement.** Each seed's own R is reported too. A claim holds only when the arm-level interval satisfies it and both
  seeds' point values lie on the same side of its threshold.
- **Seed noise floor.** L3 seed 0 over L3 seed 1, per cell.
- **Ratios between arms.** The same way: S = L3s / L3, T = L3m / L3, C = L3m / L3c (size against schedule), I = L3sm / L3m and
  L3sm / L3s (interaction), and K = L3m / L2m (memory under the mixed schedule).
- **Cost.** Median CPU and incidences per instance, and break-even N*, as in WHERE-NEXT.
- **Censoring.** Where more than half of an arm's runs hit the cap, its median is a lower bound and R is reported as a bound.

**Primary cell of each new arm**: `rand` at 4 times its largest training size (L3s: n = 3200; L3m, L3sm, L2m, L3c: n = 12800).
Its 16-times cell (L3s: 12800; the others: 51200) is its transfer cell. Five arms are judged, so intervals are 99% (Bonferroni
over five).

## Gates

| # | Gate | Fails when |
| --- | --- | --- |
| G | WHERE-NEXT's six engine checks, extended to the scale-free flag, and G6: this engine reproduces WHERE-NEXT's run for run (8 rules and L3 on 12 instances). | any fails |
| G-learn | Each new arm's validation median, at its validation size, is at most 1.15 times training-tuned Novelty+'s on the same instances. | above 1.15: that arm is read "learner failure", never "loss" |
| G-train | For the arms with a mixed last stage (L3m, L3sm, L2m), the best validation in the last stage is at least 5% below the validation at that stage's start, in median flips. | not met: that arm is read "undertrained at 3200", and P3 and C are not read |

## Predictions (frozen)

| # | Prediction | Probability | Fails when |
| --- | --- | --- | --- |
| P1 | Scale-free reads keep the training-size gain: L3s / L3 at `rand` 800 at most 1.1. | 60% | above 1.1 |
| P2 | Scale-free reads help transfer: S = L3s / L3 at `rand` 12800 at most 0.7, the interval's upper end below 1. | 40% | otherwise |
| P3 | Training at 3200 helps transfer: T = L3m / L3 at `rand` 12800 at most 0.7, upper end below 1. | 55% | otherwise |
| P3c | It is the size, not the longer schedule: C = L3m / L3c at `rand` 12800 at most 0.8, upper end below 1. | 50% | otherwise |
| P4 | L3sm wins in flips on its primary cell: R at `rand` 12800 at most 0.8, upper end below 0.9. | 30% | otherwise |
| P5 | L3sm carries over to its transfer cell: R at `rand` 51200 at most 1.0. | 25% | above 1.0 |
| P6 | Memory still pays under the mixed schedule: K = L3m / L2m at `rand` 12800 at most 0.8. | 50% | above 0.8 |
| P7 | Every new arm still loses on `local` 3200 (R > 1). | 80% | some arm has R ≤ 1 |
| P8 | No real win: no new arm's median CPU per instance is below the re-tuned best rule's on its primary cell. | 90% | some arm's is |

**Decision rule.** The WHERE-NEXT rule, per arm on its primary cell, with 99% intervals and seed agreement:
- *real win*: R ≤ 0.8 with the upper end below 0.9, and median CPU and incidences per instance both below the best rule's, with
  N* stated;
- *mechanism win*: the flips condition only;
- *clean loss*: the lower end above 0.9, with G-learn and G-train passed;
- *inconclusive*: otherwise.

**Diagnosis.**
- *The reads are an obstacle* if P2 holds.
- *Training size is an obstacle* if P3 and P3c hold.
- *Both are needed* if neither holds but L3sm's R at 12800 is below both L3s's and L3m's, by I with upper ends below 1.
- *Neither change helps* if no arm's R at its transfer cell is below L3's at the same cell.

A holding P2 says only that the reads are *an* obstacle, unless L3s also wins on its primary cell.

**Publication hold.** As in WHERE-NEXT: planted instances and local search cannot give a general SAT method. If a new arm's
slope of log median flips against log n over `rand` 800 to 51200 is smaller than every rule's by at least 0.5, the thread tells
the owner before committing that result.

## For the second stage

The owner's second stage (sub-goal B191) is a slow loop that changes the knot structures the fast loop works on. That is a
shift in meeting pattern, not in size, so the relevant evidence is `local`, where WHERE-NEXT's agent lost and its memory hurt.
The report says what this study implies for B191. A fast loop that carries over in size but still loses on `local` is not a
safe inner loop: a slow loop would select structures that suit its quirks. The plan states this now, before the results.

## Runs and stop rule

The ten trainings form one registered long run (shared runner, MemoryMax 16G). The n = 51200 re-tuning (registered
`SCALE-MEMORY-R1`, started before this freeze) and the test cells are further long runs. The study stops at the decision rule.
