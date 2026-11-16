# Carrying distinctions together

Epic `CARRY-STRANDS-20261116-001`, 16 November 2026, by Claude; takes `SEQUENTIAL-WALL-20261116-001#1`, the owner's braid made exact
for forcing. Goal G3. Referee pending. Pre-registration: [preregistration.md](preregistration.md), frozen in commit `4df1a101e`
(22:39 UTC) before the run (22:43 to 22:46 UTC). Proof: [Theorems 1–3](../../proofs/CARRY-STRANDS-20261116-001B/CARRY-STRANDS-20261116-001B-P001_carry_laws/proof.md).
Experiment: [code and contract](../../experiments/CARRY-STRANDS-20261116-001A/CARRY-STRANDS-20261116-001A-E001_carried/),
[summary](../../artifacts/CARRY-STRANDS-20261116-001A/CARRY-STRANDS-20261116-001A-E001_carried/summary.json).

## The answer

In the owner's picture, carrying several open distinctions at once is holding several strands, and keeping one after a use is
letting a strand split into two that later rejoin. Made exact for forcing, the picture is the classical one of registers and
pebbles, and it explains nothing the classical statement does not. It does isolate one distinction cleanly, and the measurements
say how the program's random families fall on each side of it:

- **Holding strands without splitting them cannot remove the nesting.** With w carried distinctions and every use spending what
  it uses, the phases fall exactly to ⌈σ/w⌉ (σ the Strahler number, the forcing law's phase count). The doubling rounds never fall
  below σ (proved). In practice two carried distinctions cut the rounds by 22 to 32% on random atom patterns at the jump, the
  saving growing with n (T₂/T₁ = 0.78 at n = 64, 0.69 at 4096). That is more than predicted, and still far above the floor (23.5
  rounds against σ = 8.5 at n = 4096).
- **Letting a strand split pays exactly where strands rejoin.** A ladder of any length takes one phase with two carried
  distinctions, and its rounds fall from 2k to about log₂(4k) (from 256 to 9 at k = 128). A layered circuit of width W takes one
  phase with 2W at any depth (proved, and checked on every narrow circuit).
- **The program's random families have little rejoining.** On random atom patterns at the jump, keeping saves no phase for any
  distinction forced before the narrowest phase, and saves a phase for 6 to 12% of those forced after it (n ≥ 128; 28% at n = 64). Keeping changes the phase
  count of 70 to 95% of samples not at all. On layered random circuits of width 16 and 32, the median gain is mostly zero. Their open
  uses are nested ties of different strands, the kind no amount of carrying removes without paying for it in rounds.
- **Pyramids** need ⌈h/w⌉ phases whether or not strands may split, and exactly h = σ rounds for every w, so the Strahler floor is
  reached there and keeping buys nothing (the advisor's derivation, confirmed).

What the braid picture explained, plainly: nothing beyond the classical register and pebbling statements (Ershov; Sethi and
Ullman; Cook). What it did was name the line between nesting and rejoining in the owner's terms. What is new is measured: how
little rejoining random atom patterns and random circuits contain, and how much spend-only carrying shortens the rounds. The atom is
not a reversible crossing, so the braid studies' joint-record effect (separate strand records losing what the joint record keeps)
has no counterpart in forcing: there the forced set is one state, and a joint record holds nothing that separate ones do not.

## The law and the measure

The **w-carry law** carries at most w open distinctions in a phase. It may begin (carry what an atom over two forced demanders
demands), follow a rule (an atom with one forced demander), take an open use while carrying both demanders, and release. The
**spend-only law** spends what each step uses; the **keep law** may keep it. w = 1 is the forcing law. The measure is w, the number
of distinctions carried at once: for forcing, a carried record holds only which distinctions are carried, so a phase searches about
n^w carried sets, and w is the pebble count of the classical games (assumption A87).

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | gates; every law ends in the closure | held | 305 of 305 cases; capped only at subdivided tree d = 4, ℓ = 16, w = 3 |
| Q1 | keeping rarely saves a phase: P₂(keep) = ⌈P₁/2⌉ in ≥ 75% of samples at each n ≥ 256 | **failed** | 0.90, 0.80, 0.90, 0.80 at 256 … 2048, but 0.70 at 4096 |
| Q1b | per distinction at most 10% gain, more after the narrowest phase than before | **failed**, narrowly | after > before held everywhere (before: 0 at every n); the median gain is 0.104 at 512 and 0.101 at 2048, just above 0.10 |
| Q2 | T₂(spend) ≤ T₁ in ≥ 90%, median ratio in [0.8, 0.95] at n ≥ 1024 | **failed**, by saving more | T₂ ≤ T₁ in every sample; ratio 0.73, 0.70, 0.685 at 1024, 2048, 4096 |
| Q3 | keeping gains more on narrower layered circuits (depth 32) | **failed** | median relative gain 0 (width 4), 0.25 (16), 0 (32); mostly zero; at width 4 depth 64, 0.32 |
| Q3b | narrow circuits take one phase with 2W carried | held | 30 of 30 samples (some with no true gate) |
| Q4 | pyramids: P_w = ⌈h/w⌉ both laws, equal rounds | held | every h = 4 … 12, w ≤ 4; T_w = h for every w |
| Q5 | subdivided trees: carrying cuts rounds | held where evaluable | ℓ = 16: T₂ = 13 against T₁ = 21 (d = 4), 19 against 31 (d = 6); T₃ at d = 4 not evaluable (state cap) |

3 held, 4 failed. The read-out script needed one fix after the run, disclosed: it crashed on the capped case, and now reports that
part of Q5 as not evaluable.

### Random atom patterns at the jump (medians)

| n | σ | R | T₁ | T₂ spend | T₂ keep | P₂ keep | gain after the narrowest phase |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 64 | 3 | 12 | 9 | 7 | 7 | 2 | 0.28 |
| 256 | 5 | 22.5 | 16 | 12.5 | 12 | 3 | 0.079 |
| 1024 | 6 | 32.5 | 22 | 15 | 15 | 3 | 0.065 |
| 4096 | 8.5 | 60 | 35 | 23.5 | 23 | 4 | 0.089 |

### Structured families

| Family | σ | T₁ | T₂ spend | T₂ keep (phases) |
| --- | --- | --- | --- | --- |
| ladder k = 8, 32, 128 | 9, 33, 129 | 16, 64, 256 | 13, 49, 193 | 5, 7, 9 (1 phase) |
| pyramid h = 4 … 12 | h | h | h | h (⌈h/2⌉ phases) |
| subdivided tree d = 4, 6, ℓ = 16 | 5, 7 | 21, 31 | 13, 19 | 13, 19 |

## Limitations

- Sizes are small: n ≤ 4096 for two carried distinctions, n ≤ 256 for three, because a phase searches about n^w carried sets.
- Q1–Q3 failures are against frozen thresholds that were guesses; the readings themselves are the result.
- Layered circuits at width 4 mostly die out to constants, so their gains are often trivially zero.
- No claim about P versus NC; the laws are particular parallel laws, not all algorithms.

## Reproduce

```sh
.venv/bin/python -B experiments/CARRY-STRANDS-20261116-001A/CARRY-STRANDS-20261116-001A-E001_carried/gates.py
.venv/bin/python -B scripts/longrun.py launch experiments/CARRY-STRANDS-20261116-001A/CARRY-STRANDS-20261116-001A-E001_carried/job.py --out RUN --workers 2 --case-mem 3G
.venv/bin/python -B experiments/CARRY-STRANDS-20261116-001A/CARRY-STRANDS-20261116-001A-E001_carried/summarize.py RUN
```

The registered run is `artifacts/CARRY-STRANDS-20261116-001A/CARRY-STRANDS-20261116-001A-E001_carried/run` (long-running row
CARRY-STRANDS-L1).

## Advisor

Consulted once before the freeze (see the pre-registration). It replaced copying by keeping (a copying law is off from pebbling
with sliding by up to two), derived the pyramid's ⌈h/w⌉ (confirmed), proposed the subdivided-tree example (confirmed where
evaluable), sharpened Q1 to Q3 (Q1 failed only at the largest size, Q2 failed by saving more than it expected, Q3 was a coin flip
and failed), and gave the one-line verdict this note confirms: the strands are pebbles, and the picture isolates the dichotomy of
rejoining against nesting.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — carrying distinctions together | **Status:** Successful (referee pending) | The braid picture made exact for forcing; 3 of 7 frozen predictions held, the 4 failures read; proved that spend-only carrying cannot go below the Strahler number |
| Local direction — carrying laws for forcing | Practically exhausted | The theory is classical (registers, pebbling); the only open quantity, rejoining in random families, is measured small |
| Broader exploration — the braid picture | Known alternatives | The joint-record effect needs relations with many states (counting or satisfiability), not forcing |
| Long-term goal — G3 Hardness at three places | Obstruction learned | Carrying strands cannot remove nested open uses; what makes order in these families is genuine nesting, not rejoining |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The braid's joint record where it can matter: carrying open knots in counting or satisfiability of not-all-equal patterns, where a joint record holds more than separate ones | 3/3 — the one place the braid picture could explain something classical statements do not emphasize | 1/3 — needs a law and a measure first; risk of re-deriving treewidth dynamic programming | Define a w-carry law that carries joint relations of w distinctions in not-all-equal propagation and count phases on small weaves → stop when it reduces to known width-based dynamic programming or shows a gap | Selected · not started |
| 2 | Why layered random circuits need about d^0.4 phases (carried over from `SEQUENTIAL-WALL-20261116-001#2`) | 2/3 | 3/3 | Write and solve the rank-distribution recursion → matches within one, or fails | Alternative · deferred |
| 3 | Rounds saved by spend-only carrying at large n | 1/3 — a constant-factor effect | 3/3 | Fit T₂/T₁ against log n to n = 2^14 with a faster search → stop at a clear limit | Alternative · deferred |

**Corrections:** none for this epic. The predecessor `SEQUENTIAL-WALL-20261116-001` got four after its referee (two Narrowing, two Not
a block), folded in at `a4860475a` and signed off.

**Goals:** G3 checkpoint (obstruction learned); no goal changed.

**Assumptions:** A87 added (measure: the record carried in forcing is how many distinctions are carried); A86's scope reused at small
sizes.

**Basket:** the holes-and-proofs line's basket was read; its untaken directions are about proof size, not this question.
